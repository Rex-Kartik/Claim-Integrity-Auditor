"""
Gemini key rotation, model probing, and LLM call wrapper.
Keys come from GEMINI_API_KEYS env var (comma-separated).
Never logs or returns the key value — only position ("key 1", "key 2").
"""
import json
import logging
import os
import time
from typing import Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Key management
# ---------------------------------------------------------------------------

_raw_keys = os.environ.get("GEMINI_API_KEYS", "")
_keys: list[str] = [k.strip() for k in _raw_keys.split(",") if k.strip()]
COOLDOWN_SECONDS = int(os.environ.get("GEMINI_KEY_COOLDOWN_SECONDS", "300"))

# cooldown_until[i] = epoch time after which key i is usable again
_cooldown_until: list[float] = [0.0] * len(_keys)

# ---------------------------------------------------------------------------
# Active model state
# ---------------------------------------------------------------------------

_active_model: Optional[str] = None
MODEL_CANDIDATES_ENV = os.environ.get("GEMINI_MODEL_CANDIDATES", "")
_GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"


def _available_keys() -> list[tuple[int, str]]:
    """Return (index, key) pairs for keys not on cooldown."""
    now = time.time()
    return [(i, k) for i, k in enumerate(_keys) if now >= _cooldown_until[i]]


def key_status() -> list[dict]:
    """Return key status for /health endpoint (no key values)."""
    now = time.time()
    return [
        {
            "position": f"key {i + 1}",
            "available": now >= _cooldown_until[i],
            "cooldown_remaining": max(0, _cooldown_until[i] - now),
        }
        for i in range(len(_keys))
    ]


def has_keys() -> bool:
    return len(_keys) > 0


# ---------------------------------------------------------------------------
# Model probing
# ---------------------------------------------------------------------------

def _list_models(api_key: str) -> list[str]:
    """Call the Gemini model-listing endpoint and return models supporting generateContent."""
    url = f"{_GEMINI_BASE}/models?pageSize=100"
    try:
        resp = httpx.get(url, headers={"x-goog-api-key": api_key}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        models = []
        for m in data.get("models", []):
            if "generateContent" in m.get("supportedGenerationMethods", []):
                models.append(m["name"])
        return models
    except Exception as e:
        logger.warning("Failed to list Gemini models: %s", e)
        return []


def _probe_model(model_name: str, api_key: str) -> bool:
    """Send a probe prompt; return True if response contains 'OK'."""
    # model_name may be "models/gemini-1.5-flash" — use as-is
    short = model_name.lstrip("models/")
    url = f"{_GEMINI_BASE}/{model_name}:generateContent"
    payload = {
        "contents": [{"parts": [{"text": "Reply with exactly: OK"}]}]
    }
    try:
        resp = httpx.post(url, headers={"x-goog-api-key": api_key}, json=payload, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return "OK" in text
    except Exception as e:
        logger.debug("Probe failed for %s: %s", short, e)
    return False


def probe_and_select_model() -> Optional[str]:
    """Discover and probe models; set _active_model to first passing one."""
    global _active_model
    avail = _available_keys()
    if not avail:
        logger.error("No Gemini API keys configured.")
        return None

    # Use any available key just to list models
    _, probe_key = avail[0]

    if MODEL_CANDIDATES_ENV:
        candidates = [c.strip() for c in MODEL_CANDIDATES_ENV.split(",") if c.strip()]
    else:
        # Fallback to known fast models, prioritizing 1.5-flash for better JSON and verbatim adherence
        candidates = ["gemini-1.5-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-flash-latest"]

    for model in candidates:
        # Normalise to full path
        if not model.startswith("models/"):
            model = f"models/{model}"
        if _probe_model(model, probe_key):
            _active_model = model
            logger.info("Active Gemini model: %s", model)
            return model

    logger.error("No Gemini model passed probe.")
    return None


def get_active_model() -> Optional[str]:
    return _active_model


# ---------------------------------------------------------------------------
# LLM call with rotation
# ---------------------------------------------------------------------------

def call_llm(prompt: str, cached_result=None, require_json: bool = False) -> Optional[str]:
    """
    Call the active Gemini model with key rotation on 429.
    Returns response text, or None if all keys fail.
    cached_result is returned if all keys fail and it is not None.
    """
    global _active_model

    if not _active_model:
        probe_and_select_model()
    if not _active_model:
        return cached_result

    avail = _available_keys()
    if not avail:
        logger.warning("All Gemini keys on cooldown.")
        return cached_result

    for idx, key in avail:
        url = f"{_GEMINI_BASE}/{_active_model}:generateContent"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        if require_json:
            payload["generationConfig"] = {"responseMimeType": "application/json"}
        try:
            resp = httpx.post(url, headers={"x-goog-api-key": key}, json=payload, timeout=60)
            if resp.status_code == 429:
                logger.warning("Rate limit on key %d; putting on cooldown.", idx + 1)
                _cooldown_until[idx] = time.time() + COOLDOWN_SECONDS
                continue
            if resp.status_code in (404, 400):
                # Model may not be available; re-probe
                logger.warning("Model error %d; re-probing.", resp.status_code)
                _active_model = None
                probe_and_select_model()
                if not _active_model:
                    return cached_result
                url = f"{_GEMINI_BASE}/{_active_model}:generateContent"
                resp = httpx.post(url, headers={"x-goog-api-key": key}, json=payload, timeout=60)

            resp.raise_for_status()
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return text
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                _cooldown_until[idx] = time.time() + COOLDOWN_SECONDS
                continue
            logger.error("HTTP error calling Gemini with key %d: %s", idx + 1, e)
        except Exception as e:
            logger.error("Error calling Gemini with key %d: %s", idx + 1, e)

    # All keys failed
    if cached_result is not None:
        logger.warning("All keys failed; using cached result.")
        return cached_result
    return None

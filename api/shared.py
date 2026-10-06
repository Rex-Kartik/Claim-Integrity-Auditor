"""
Shared utilities: disk cache, JSON result writer, run-directory helper.
"""
import hashlib
import json
import os
import time
from pathlib import Path

CACHE_DIR = Path(__file__).parent.parent / "cache"
RUNS_DIR = Path(__file__).parent.parent / "runs"

CACHE_DIR.mkdir(parents=True, exist_ok=True)
RUNS_DIR.mkdir(parents=True, exist_ok=True)


def _cache_key(namespace: str, data: str) -> str:
    digest = hashlib.sha256(f"{namespace}:{data}".encode()).hexdigest()
    return digest


def cache_get(namespace: str, key_data: str):
    """Return cached value or None."""
    path = CACHE_DIR / f"{_cache_key(namespace, key_data)}.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def cache_set(namespace: str, key_data: str, value) -> None:
    """Store value in disk cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{_cache_key(namespace, key_data)}.json"
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def run_dir(audit_id: str) -> Path:
    """Return (and create) the run directory for an audit."""
    d = RUNS_DIR / audit_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def write_stage_result(audit_id: str, stage: str, payload: dict) -> Path:
    """Write stage result JSON and return path."""
    path = run_dir(audit_id) / f"{stage}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def read_stage_result(audit_id: str, stage: str):
    """Read existing stage result or return None."""
    path = run_dir(audit_id) / f"{stage}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None

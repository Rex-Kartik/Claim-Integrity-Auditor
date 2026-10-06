"""
Stage 2: Claim extraction via Gemini.
Returns at most 15 claims, each with claim, quote (verbatim from text), page.
Also extracts: paper DOI, cited DOIs, code/data URLs, APA statistic strings.
Rejects any claim whose quote is not found verbatim in the extracted text.
"""
import json
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

CLAIM_PROMPT = """You are a scientific claim extraction assistant. Analyse the following research paper text and return a JSON object with exactly these fields:

{{
  "claims": [
    {{
      "claim": "A single declarative sentence stating a factual claim made in the paper.",
      "quote": "The VERBATIM text from the paper that contains or directly supports this claim. Must be copied character-for-character from the paper text.",
      "page": 1
    }}
  ],
  "paper_doi": "DOI of this paper if mentioned, else null",
  "cited_dois": ["list of DOIs cited in the paper"],
  "code_data_urls": ["list of URLs to code repositories or datasets mentioned"],
  "apa_statistics": ["list of APA-style statistic strings like t(42)=3.14, p=.001 or F(2,87)=5.23, p<.05"]
}}

Rules:
- Return at most 15 claims. Choose the most empirically verifiable ones.
- The quote field must be VERBATIM text from the paper. Do not paraphrase.
- The page field must be the page number where the quote appears.
- Return ONLY valid JSON, no markdown fences, no commentary.

Paper text (page numbers indicated with [PAGE N]):
{text}"""


def _build_text_with_pages(raw_pages: list[dict]) -> str:
    parts = []
    for p in raw_pages:
        parts.append(f"[PAGE {p['page']}]\n{p['text']}")
    return "\n\n".join(parts)


def run(audit_id: str, raw_pages: list[dict]) -> dict:
    """Run claim extraction and write stage result."""
    from shared import write_stage_result, cache_get, cache_set
    from llm import call_llm

    full_text_with_pages = _build_text_with_pages(raw_pages)
    # Trim to ~60k chars to avoid context overflow
    trimmed = full_text_with_pages[:60000]
    full_plain = "\n".join(p["text"] for p in raw_pages)

    prompt = CLAIM_PROMPT.format(text=trimmed)

    cache_key = trimmed[:200]  # cache by first 200 chars of text
    cached = cache_get("claims", cache_key)

    raw_response = call_llm(prompt, cached_result=json.dumps(cached) if cached else None, require_json=True)

    if raw_response is None:
        payload = {
            "stage": "claims",
            "inputs": {"page_count": len(raw_pages)},
            "outputs": {"claims": [], "paper_doi": None, "cited_dois": [], "code_data_urls": [], "apa_statistics": []},
            "error": "LLM quota exhausted",
            "not_checkable_reason": "LLM quota exhausted",
        }
        write_stage_result(audit_id, "claims", payload)
        return payload

    # Parse JSON from response
    try:
        # Strip markdown fences if present
        text = raw_response.strip()
        if text.startswith("```"):
            text = re.sub(r"^```[a-z]*\n?", "", text)
            text = re.sub(r"\n?```$", "", text)
        data = json.loads(text)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse claims JSON: %s", e)
        data = {
            "claims": [], "paper_doi": None, "cited_dois": [],
            "code_data_urls": [], "apa_statistics": []
        }

    # Validate: reject claims whose quote is not verbatim in the text (allowing for spacing differences)
    valid_claims = []
    rejected_claims = []
    import re
    full_plain_normalized = re.sub(r"\s+", "", full_plain)
    
    for c in data.get("claims", [])[:15]:
        quote = c.get("quote", "")
        quote_normalized = re.sub(r"\s+", "", quote)
        
        if quote_normalized and quote_normalized in full_plain_normalized:
            valid_claims.append(c)
        else:
            rejected_claims.append({"claim": c.get("claim"), "reason": "quote not found verbatim in text"})

    data["claims"] = valid_claims

    # Cache successful extraction
    cache_set("claims", cache_key, data)

    payload = {
        "stage": "claims",
        "inputs": {"page_count": len(raw_pages)},
        "outputs": data,
        "rejected_claims": rejected_claims,
        "raw_response_length": len(raw_response),
    }
    write_stage_result(audit_id, "claims", payload)
    return payload

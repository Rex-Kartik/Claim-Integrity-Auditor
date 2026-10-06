"""
Stage 5: Citation check using Gemini.
For at most 3 claims per paper that cite a DOI, fetches the cited abstract
from Crossref or OpenAlex and asks Gemini whether it supports the claim.
Returns "supports", "not supported", or "not checkable".
"""
import logging
from langfuse import observe, propagate_attributes
import json
import re
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

CROSSREF_BASE = "https://api.crossref.org/v1"
OPENALEX_BASE = "https://api.openalex.org"
MAILTO = "research-audit-demo@example.com"

CITATION_PROMPT = """You are a scientific citation verifier. Determine whether the abstract of the cited paper supports the claim made in the paper under review.

Claim: {claim}

Cited paper abstract (or excerpt):
{abstract}

Instructions:
- Reply with exactly one of: "supports", "not supported", or "not checkable"
- Reply "supports" only if the abstract directly supports the claim.
- Reply "not supported" if the abstract contradicts or does not support the claim.
- Reply "not checkable" only if the abstract is absent or too short to judge.
- After the verdict, add a colon and a one-sentence justification.
- Do not use the words: fraud, fabricated, misconduct, cheat, fake, dishonest, guilty.

Format: <verdict>: <one sentence justification>"""


def _fetch_abstract_crossref(doi: str) -> Optional[str]:
    from shared import cache_get, cache_set

    cached = cache_get("abstract_crossref", doi)
    if cached is not None:
        return cached

    try:
        resp = httpx.get(
            f"{CROSSREF_BASE}/works/{doi}",
            params={"mailto": MAILTO},
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            abstract = data.get("message", {}).get("abstract", None)
            if abstract:
                # Crossref abstracts may contain JATS XML tags
                abstract = re.sub(r"<[^>]+>", " ", abstract).strip()
                cache_set("abstract_crossref", doi, abstract)
                return abstract
            else:
                cache_set("abstract_crossref", doi, "")
                return ""
    except Exception as e:
        logger.debug("Crossref abstract fetch failed for %s: %s", doi, e)
    return None


def _fetch_abstract_openalex(doi: str) -> Optional[str]:
    from shared import cache_get, cache_set

    cached = cache_get("abstract_openalex", doi)
    if cached is not None:
        return cached

    try:
        resp = httpx.get(
            f"{OPENALEX_BASE}/works/doi:{doi}",
            params={"mailto": MAILTO},
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            # OpenAlex stores abstract as inverted index
            inv_index = data.get("abstract_inverted_index")
            if inv_index:
                # Reconstruct from inverted index
                word_positions = []
                for word, positions in inv_index.items():
                    for pos in positions:
                        word_positions.append((pos, word))
                word_positions.sort()
                abstract = " ".join(w for _, w in word_positions)
                cache_set("abstract_openalex", doi, abstract)
                return abstract
    except Exception as e:
        logger.debug("OpenAlex abstract fetch failed for %s: %s", doi, e)
    cache_set("abstract_openalex", doi, None)
    return None


def _fetch_abstract(doi: str) -> Optional[str]:
    """Try Crossref first, then OpenAlex."""
    abstract = _fetch_abstract_crossref(doi)
    if abstract:
        return abstract
    return _fetch_abstract_openalex(doi)


def _parse_verdict(response: str) -> tuple[str, str]:
    """Parse verdict and justification from LLM response."""
    response = response.strip()
    for verdict in ("supports", "not supported", "not checkable"):
        if response.lower().startswith(verdict):
            rest = response[len(verdict):].lstrip(":").strip()
            return verdict, rest
    return "not checkable", response


def check_claim(claim: dict, cited_dois: list[str]) -> dict:
    """Check a single claim against its cited DOIs."""
    from shared import cache_get, cache_set
    from llm import call_llm

    claim_text = claim.get("claim", "")
    quote = claim.get("quote", "")
    page = claim.get("page")

    if not cited_dois:
        return {
            "claim": claim_text,
            "quote": quote,
            "page": page,
            "verdict": "not checkable",
            "reason": "no cited DOI for this claim",
            "evidence_label": "abstract only",
        }

    # Try the first cited DOI that has an abstract
    for doi in cited_dois[:2]:
        abstract = _fetch_abstract(doi)
        if not abstract:
            continue

        cache_key = f"{claim_text[:100]}:{doi}"
        cached = cache_get("citation_check", cache_key)

        prompt = CITATION_PROMPT.format(claim=claim_text, abstract=abstract[:3000])
        response = call_llm(prompt, cached_result=cached)

        if response:
            cache_set("citation_check", cache_key, response)
            verdict, justification = _parse_verdict(response)
            return {
                "claim": claim_text,
                "quote": quote,
                "page": page,
                "cited_doi": doi,
                "verdict": verdict,
                "justification": justification,
                "retrieved_passage": abstract[:500],
                "evidence_label": "abstract only",
            }

    return {
        "claim": claim_text,
        "quote": quote,
        "page": page,
        "verdict": "not checkable",
        "reason": "no abstract available for cited DOIs",
        "evidence_label": "abstract only",
    }


@observe(name="citations_run")
def run(audit_id: str, claims: list[dict], cited_dois: list[str]) -> dict:
    """Run citation check on at most 3 claims and write stage result."""
    from shared import write_stage_result

    # Check at most 3 claims
    claims_to_check = claims[:3]
    results = []
    for claim in claims_to_check:
        result = check_claim(claim, cited_dois)
        results.append(result)

    payload = {
        "stage": "citations",
        "inputs": {
            "claims_checked": len(claims_to_check),
            "total_claims": len(claims),
            "cited_doi_count": len(cited_dois),
        },
        "outputs": {"results": results},
    }
    write_stage_result(audit_id, "citations", payload)
    return payload

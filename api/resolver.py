"""
Metadata resolver: given a DOI or URL, resolves paper metadata via
Crossref and OpenAlex, and finds an open-access PDF URL.
OpenAlex field confirmed: best_oa_location.pdf_url
"""
import logging
import re
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

CROSSREF_BASE = "https://api.crossref.org/v1"
OPENALEX_BASE = "https://api.openalex.org"
MAILTO = "research-audit-demo@example.com"


def _extract_doi(text: str) -> Optional[str]:
    """Extract a DOI from a string (URL or bare DOI)."""
    # Standard DOI pattern
    m = re.search(r"10\.\d{4,9}/[^\s\"'<>]+", text)
    if m:
        return m.group(0).rstrip(".,;)")
    return None


def resolve_doi(doi_or_url: str) -> dict:
    """
    Given a DOI or URL, return metadata dict with:
      doi, title, abstract, pdf_url, open_access, crossref_data, openalex_data
    pdf_url is from OpenAlex best_oa_location.pdf_url (confirmed field name).
    """
    from shared import cache_get, cache_set

    doi = _extract_doi(doi_or_url)
    if not doi:
        return {"error": "Could not extract DOI from input", "doi": None, "pdf_url": None}

    cached = cache_get("metadata", doi)
    if cached:
        return cached

    result = {"doi": doi, "title": None, "abstract": None, "pdf_url": None, "open_access": False}

    # Crossref
    try:
        resp = httpx.get(f"{CROSSREF_BASE}/works/{doi}", params={"mailto": MAILTO}, timeout=15)
        if resp.status_code == 200:
            cr = resp.json().get("message", {})
            result["crossref_data"] = {
                "title": " ".join(cr.get("title", [])),
                "type": cr.get("type"),
                "published": cr.get("published", {}).get("date-parts", [[]])[0],
                "journal": " ".join(cr.get("container-title", [])),
            }
            result["title"] = result["crossref_data"]["title"]
    except Exception as e:
        logger.warning("Crossref metadata error for %s: %s", doi, e)

    # OpenAlex — confirmed field: best_oa_location.pdf_url
    try:
        resp = httpx.get(
            f"{OPENALEX_BASE}/works/doi:{doi}",
            params={"mailto": MAILTO},
            timeout=15,
        )
        if resp.status_code == 200:
            oa = resp.json()
            best_oa = oa.get("best_oa_location") or {}
            pdf_url = best_oa.get("pdf_url")
            result["pdf_url"] = pdf_url
            result["open_access"] = oa.get("open_access", {}).get("is_oa", False)
            # Abstract from inverted index
            inv_index = oa.get("abstract_inverted_index")
            if inv_index:
                word_positions = []
                for word, positions in inv_index.items():
                    for pos in positions:
                        word_positions.append((pos, word))
                word_positions.sort()
                result["abstract"] = " ".join(w for _, w in word_positions)
            if not result["title"]:
                result["title"] = oa.get("display_name")
            result["openalex_data"] = {
                "id": oa.get("id"),
                "open_access": oa.get("open_access"),
                "best_oa_location": best_oa,
            }
    except Exception as e:
        logger.warning("OpenAlex metadata error for %s: %s", doi, e)

    cache_set("metadata", doi, result)
    return result


def download_pdf(pdf_url: str) -> Optional[bytes]:
    """Download a PDF and return its bytes, or None on failure."""
    try:
        resp = httpx.get(
            pdf_url,
            timeout=60,
            follow_redirects=True,
            headers={"User-Agent": "ResearchAuditBot/1.0"},
        )
        if resp.status_code == 200 and "pdf" in resp.headers.get("content-type", "").lower():
            return resp.content
        # Sometimes content-type is wrong but content is PDF
        if resp.status_code == 200 and resp.content[:4] == b"%PDF":
            return resp.content
    except Exception as e:
        logger.warning("PDF download failed from %s: %s", pdf_url, e)
    return None

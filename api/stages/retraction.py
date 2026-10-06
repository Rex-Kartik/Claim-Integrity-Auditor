"""
Stage 3: Retraction check.
Queries Crossref REST API and local Retraction Watch CSV for the paper DOI
and each cited DOI.
Returns per DOI: "retraction record found", "none found", or "not checkable".
A failed lookup is NEVER reported as "none found".
"""
import csv
import logging
from langfuse import observe, propagate_attributes
import os
from pathlib import Path
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

CROSSREF_BASE = "https://api.crossref.org/v1"
MAILTO = "research-audit-demo@example.com"

# Path to the cloned Retraction Watch CSV
_RW_CSV_CANDIDATES = [
    Path(__file__).parent.parent.parent / "data" / "retraction-watch-data" / "retracted_papers.csv",
    Path(__file__).parent.parent.parent / "data" / "retraction-watch-data" / "retraction_watch.csv",
    Path(__file__).parent.parent.parent / "data" / "retraction-watch-data" / "retractions.csv",
]


def _find_rw_csv() -> Optional[Path]:
    """Find the Retraction Watch CSV file."""
    # Check any CSV in the data directory
    data_dir = Path(__file__).parent.parent.parent / "data" / "retraction-watch-data"
    if data_dir.exists():
        for csv_file in data_dir.glob("*.csv"):
            return csv_file
    return None


def _load_rw_dois() -> set[str]:
    """Load all DOIs from the Retraction Watch CSV into a set."""
    csv_path = _find_rw_csv()
    if not csv_path or not csv_path.exists():
        logger.warning("Retraction Watch CSV not found at expected paths.")
        return set()

    dois = set()
    try:
        with open(csv_path, encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Try multiple possible column names
                doi = (
                    row.get("OriginalPaperDOI", "")
                    or row.get("doi", "")
                    or row.get("DOI", "")
                    or row.get("paper_doi", "")
                ).strip()
                if doi:
                    dois.add(doi.lower())
    except Exception as e:
        logger.error("Error reading Retraction Watch CSV: %s", e)
    logger.info("Loaded %d DOIs from Retraction Watch CSV", len(dois))
    return dois


def _get_rw_record(doi: str, csv_path: Optional[Path]) -> Optional[dict]:
    """Return the full CSV row for a DOI if found, else None."""
    if not csv_path or not csv_path.exists():
        return None
    try:
        with open(csv_path, encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_doi = (
                    row.get("OriginalPaperDOI", "")
                    or row.get("doi", "")
                    or row.get("DOI", "")
                    or row.get("paper_doi", "")
                ).strip().lower()
                if row_doi == doi.lower():
                    return dict(row)
    except Exception as e:
        logger.error("Error reading RW record for %s: %s", doi, e)
    return None


def _check_crossref(doi: str) -> dict:
    """Query Crossref for a DOI. Returns verdict and raw record or error."""
    from shared import cache_get, cache_set

    cached = cache_get("crossref_doi", doi)
    if cached:
        return cached

    url = f"{CROSSREF_BASE}/works/{doi}"
    try:
        resp = httpx.get(url, params={"mailto": MAILTO}, timeout=15)
        if resp.status_code == 404:
            result = {"verdict": "none found", "source": "crossref", "doi": doi, "record": None}
            cache_set("crossref_doi", doi, result)
            return result
        resp.raise_for_status()
        data = resp.json()
        work = data.get("message", {})
        # Check if it is a retraction notice
        work_type = work.get("type", "")
        title = " ".join(work.get("title", []))
        is_retraction = False
        # Check explicit update-to array
        for update in work.get("update-to", []):
            if update.get("type") == "retraction":
                is_retraction = True
                break
        
        # Check relations (is-retracted-by)
        relations = work.get("relation", {})
        if "is-retracted-by" in relations:
            is_retraction = True
        if is_retraction:
            result = {
                "verdict": "retraction record found",
                "source": "crossref",
                "doi": doi,
                "record": {"type": work_type, "title": title},
            }
        else:
            result = {"verdict": "none found", "source": "crossref", "doi": doi, "record": None}
        cache_set("crossref_doi", doi, result)
        return result
    except httpx.HTTPStatusError as e:
        logger.warning("Crossref HTTP error for %s: %s", doi, e)
        return {"verdict": "not checkable", "source": "crossref", "doi": doi, "error": str(e)}
    except Exception as e:
        logger.warning("Crossref error for %s: %s", doi, e)
        return {"verdict": "not checkable", "source": "crossref", "doi": doi, "error": str(e)}


def check_doi(doi: str, rw_dois: set, csv_path: Optional[Path]) -> dict:
    """
    Check a single DOI against both Crossref and Retraction Watch CSV.
    Returns {"doi": ..., "verdict": ..., "evidence": ...}.
    """
    if not doi or not doi.strip():
        return {"doi": doi, "verdict": "not checkable", "reason": "empty DOI"}

    doi = doi.strip()
    evidence = []

    # Check Retraction Watch CSV first (local, fast)
    rw_hit = doi.lower() in rw_dois
    rw_record = None
    if rw_hit:
        rw_record = _get_rw_record(doi, csv_path)
        evidence.append({"source": "retraction_watch_csv", "record": rw_record})

    # Check Crossref
    crossref_result = _check_crossref(doi)
    evidence.append(crossref_result)

    # Also check if there's a retraction notice linked (Crossref retract field)
    from shared import cache_get, cache_set
    cached_related = cache_get("crossref_related", doi)
    if cached_related is None:
        try:
            url = f"{CROSSREF_BASE}/works"
            resp = httpx.get(
                url,
                params={"filter": f"relation.type:is-retraction-of,relation.object:{doi}", "mailto": MAILTO},
                timeout=15,
            )
            if resp.status_code == 200:
                related = resp.json().get("message", {}).get("items", [])
                cached_related = related
                cache_set("crossref_related", doi, related)
            else:
                cached_related = []
        except Exception:
            cached_related = []

    has_retraction_notice = len(cached_related) > 0

    # Determine final verdict
    if rw_hit or crossref_result["verdict"] == "retraction record found" or has_retraction_notice:
        verdict = "retraction record found"
    elif crossref_result["verdict"] == "not checkable":
        verdict = "not checkable"
    else:
        verdict = "none found"

    return {
        "doi": doi,
        "verdict": verdict,
        "evidence": evidence,
        "retraction_watch_hit": rw_hit,
        "crossref_retraction_notice": has_retraction_notice,
    }


@observe(name="retraction_run")
def run(audit_id: str, paper_doi: Optional[str], cited_dois: list[str]) -> dict:
    """Run retraction check on paper DOI and cited DOIs, write stage result."""
    from shared import write_stage_result

    rw_dois = _load_rw_dois()
    csv_path = _find_rw_csv()

    all_dois = []
    seen = set()
    if paper_doi:
        all_dois.append(paper_doi)
        seen.add(paper_doi.lower())
    for doi in cited_dois[:30]:  # cap at 30 cited DOIs
        if doi.lower() not in seen:
            all_dois.append(doi)
            seen.add(doi.lower())

    results = []
    for doi in all_dois:
        r = check_doi(doi, rw_dois, csv_path)
        results.append(r)

    # Paper-level verdict
    paper_result = None
    if paper_doi:
        paper_result = next((r for r in results if r["doi"] == paper_doi), None)

    paper_verdict = paper_result["verdict"] if paper_result else "not checkable"

    payload = {
        "stage": "retraction",
        "inputs": {"paper_doi": paper_doi, "cited_doi_count": len(cited_dois)},
        "outputs": {
            "paper_verdict": paper_verdict,
            "paper_doi": paper_doi,
            "doi_results": results,
        },
        "rw_csv_loaded": len(rw_dois) > 0,
        "rw_doi_count": len(rw_dois),
    }
    write_stage_result(audit_id, "retraction", payload)
    return payload

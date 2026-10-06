"""
Stage 6: Code and data URL link check.
Sends HTTP HEAD (then GET if refused) with 10-second timeout.
Returns "loads", "fails" (with status code), or "absent".
Never clones or executes anything.
"""
import logging
import re
from langfuse import observe, propagate_attributes
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

TIMEOUT = 10.0
USER_AGENT = "ResearchAuditBot/1.0 (demo; +https://github.com/example/research-audit)"
GITHUB_API_BASE = "https://api.github.com/repos"

def check_github_repo(owner: str, repo: str, url: str) -> dict:
    """Check if a GitHub repo exists using the GitHub REST API."""
    from shared import cache_get, cache_set
    
    api_url = f"{GITHUB_API_BASE}/{owner}/{repo}"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github.v3+json"}
    
    try:
        resp = httpx.get(api_url, headers=headers, timeout=TIMEOUT)
        if resp.status_code == 200:
            return {"url": url, "verdict": "loads", "status_code": 200, "method": "GITHUB_API"}
        else:
            return {"url": url, "verdict": "fails", "status_code": resp.status_code, "method": "GITHUB_API"}
    except Exception as e:
        return {"url": url, "verdict": "fails", "error": str(e), "method": "GITHUB_API"}


def check_url(url: str) -> dict:
    """Check a single URL. Returns verdict dict."""
    from shared import cache_get, cache_set

    if not url or not url.strip():
        return {"url": url, "verdict": "absent", "reason": "empty URL"}

    url = url.strip()
    cached = cache_get("url_check", url)
    if cached:
        return cached

    # Check if it's a GitHub URL
    github_match = re.match(r'https?://(?:www\.)?github\.com/([^/]+)/([^/]+)/?', url)
    if github_match:
        owner, repo = github_match.groups()
        # strip query params or fragments if any
        repo = repo.split('?')[0].split('#')[0]
        result = check_github_repo(owner, repo, url)
        cache_set("url_check", url, result)
        return result

    headers = {"User-Agent": USER_AGENT}

    # Try HEAD first
    try:
        resp = httpx.head(url, headers=headers, timeout=TIMEOUT, follow_redirects=True)
        if resp.status_code < 400:
            result = {"url": url, "verdict": "loads", "status_code": resp.status_code, "method": "HEAD"}
            cache_set("url_check", url, result)
            return result
        if resp.status_code == 405:
            # HEAD not allowed, try GET
            raise httpx.HTTPStatusError("HEAD refused", request=resp.request, response=resp)
        result = {"url": url, "verdict": "fails", "status_code": resp.status_code, "method": "HEAD"}
        cache_set("url_check", url, result)
        return result
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 405:
            pass  # fall through to GET
        else:
            result = {"url": url, "verdict": "fails", "error": str(e), "method": "HEAD"}
            cache_set("url_check", url, result)
            return result
    except Exception:
        pass  # fall through to GET

    # Try GET
    try:
        resp = httpx.get(url, headers=headers, timeout=TIMEOUT, follow_redirects=True)
        if resp.status_code < 400:
            result = {"url": url, "verdict": "loads", "status_code": resp.status_code, "method": "GET"}
        else:
            result = {"url": url, "verdict": "fails", "status_code": resp.status_code, "method": "GET"}
        cache_set("url_check", url, result)
        return result
    except Exception as e:
        result = {"url": url, "verdict": "fails", "error": str(e), "method": "GET"}
        cache_set("url_check", url, result)
        return result


@observe(name="code_data_run")
def run(audit_id: str, code_data_urls: list[str]) -> dict:
    """Run link checks and write stage result."""
    from shared import write_stage_result

    if not code_data_urls:
        payload = {
            "stage": "code_data",
            "inputs": {"url_count": 0},
            "outputs": {"results": [], "overall_verdict": "absent"},
        }
        write_stage_result(audit_id, "code_data", payload)
        return payload

    results = [check_url(url) for url in code_data_urls]

    # Overall verdict: if any loads -> "loads"; if all fail -> "fails"; if absent -> "absent"
    verdicts = [r["verdict"] for r in results]
    if "loads" in verdicts:
        overall = "loads"
    elif "fails" in verdicts:
        overall = "fails"
    else:
        overall = "absent"

    payload = {
        "stage": "code_data",
        "inputs": {"url_count": len(code_data_urls)},
        "outputs": {"results": results, "overall_verdict": overall},
    }
    write_stage_result(audit_id, "code_data", payload)
    return payload

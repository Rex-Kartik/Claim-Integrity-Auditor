"""
Stage 7: Grader — plain code, no LLM.
Evaluates D -> C -> B -> A in order.
"grade withheld" if more than half of claims are uncheckable.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Allowed verdict words (must match the spec)
ALLOWED_VERDICTS = {"not supported", "not reproduced", "retraction record found", "not checkable"}
FORBIDDEN_WORDS = {"fraud", "fabricated", "misconduct", "cheat", "fake", "dishonest", "guilty"}


def grade(
    retraction_verdict: str,
    citation_results: list[dict],
    stats_results: list[dict],
    code_data_verdict: str,
    total_claims: int,
) -> dict:
    """
    Apply the rubric and return grade info.

    Checks:
      S: source supports claim
      R: statistic reproduces
      N: no retraction found
      C: code/data loads
    """
    # Count uncheckable claims (from citation check)
    citation_uncheckable = [r for r in citation_results if r.get("verdict") == "not checkable"]
    citation_checkable = [r for r in citation_results if r.get("verdict") != "not checkable"]

    stats_uncheckable = [r for r in stats_results if r.get("verdict") == "not checkable"]
    stats_checkable = [r for r in stats_results if r.get("verdict") != "not checkable"]

    # Determine if more than half of claims are uncheckable
    # "claims" here = citation checks + stats checks combined view
    total_checked = len(citation_results) + len(stats_results)
    total_uncheckable = len(citation_uncheckable) + len(stats_uncheckable)

    # If more than half of all claims are uncheckable, withhold grade
    # Use total_claims from claims stage for the denominator
    if total_claims > 0 and total_uncheckable > total_claims / 2:
        return {
            "grade": "grade withheld",
            "rule": "More than half of the claims could not be checked.",
            "uncheckable_items": _collect_uncheckable(citation_uncheckable, stats_uncheckable),
        }

    # Check N: retraction
    N_pass = retraction_verdict in ("none found", "not checkable")  # "not checkable" doesn't fail N
    N_retracted = retraction_verdict == "retraction record found"

    # Check S: all checkable citation results pass (support)
    S_pass = all(r["verdict"] == "supports" for r in citation_checkable)
    S_fail = any(r["verdict"] == "not supported" for r in citation_checkable)

    # Check R: all checkable stats reproduce
    R_pass = all(r["verdict"] == "reproduced" for r in stats_checkable)
    R_fail = any(r["verdict"] == "not reproduced" for r in stats_checkable)

    # Check C: code/data loads
    C_pass = code_data_verdict == "loads"
    C_absent_or_fail = code_data_verdict in ("fails", "absent")

    # Grade D: retraction record found, OR some claim fails both S and R
    any_claim_fails_both_S_and_R = False
    if citation_results and stats_results:
        # Conservative: any "not supported" claim AND any "not reproduced" stat
        any_claim_fails_both_S_and_R = S_fail and R_fail

    if N_retracted or any_claim_fails_both_S_and_R:
        if N_retracted:
            rule = "Retraction record found for this paper."
        else:
            rule = "At least one claim is not supported by its source and at least one statistic is not reproduced."
        return {
            "grade": "D",
            "rule": rule,
            "uncheckable_items": _collect_uncheckable(citation_uncheckable, stats_uncheckable),
        }

    # Grade C: no D, but some claim "not supported" or some stat "not reproduced"
    if S_fail or R_fail:
        if S_fail and R_fail:
            rule = "At least one claim is not supported by its cited source, and at least one statistic is not reproduced."
        elif S_fail:
            rule = "At least one claim is not supported by its cited source."
        else:
            rule = "At least one statistic is not reproduced."
        return {
            "grade": "C",
            "rule": rule,
            "uncheckable_items": _collect_uncheckable(citation_uncheckable, stats_uncheckable),
        }

    # Grade B: N passes, S and R pass on all checkable, C fails or absent
    if N_pass and S_pass and R_pass and C_absent_or_fail:
        if code_data_verdict == "absent":
            rule = "No retraction record found, all checkable claims and statistics pass, but no code or data link is provided."
        else:
            rule = "No retraction record found, all checkable claims and statistics pass, but the code or data link does not load."
        return {
            "grade": "B",
            "rule": rule,
            "uncheckable_items": _collect_uncheckable(citation_uncheckable, stats_uncheckable),
        }

    # Grade A: N, S, R and C all pass
    if N_pass and S_pass and R_pass and C_pass:
        return {
            "grade": "A",
            "rule": "No retraction record found, all checkable claims and statistics pass, and code or data loads.",
            "uncheckable_items": _collect_uncheckable(citation_uncheckable, stats_uncheckable),
        }

    # Fallback: if some items are all uncheckable
    return {
        "grade": "grade withheld",
        "rule": "Insufficient checkable evidence to assign a grade.",
        "uncheckable_items": _collect_uncheckable(citation_uncheckable, stats_uncheckable),
    }


def _collect_uncheckable(citation_uncheckable: list, stats_uncheckable: list) -> list:
    items = []
    for r in citation_uncheckable:
        items.append({
            "type": "citation",
            "claim": r.get("claim"),
            "reason": r.get("reason", "not checkable"),
        })
    for r in stats_uncheckable:
        items.append({
            "type": "statistic",
            "raw_string": r.get("raw_string"),
            "reason": r.get("reason", "not checkable"),
        })
    return items


def run(audit_id: str, retraction_payload: dict, stats_payload: dict,
        citation_payload: dict, code_data_payload: dict, claims_payload: dict) -> dict:
    """Run the grader and write stage result."""
    from shared import write_stage_result

    retraction_verdict = retraction_payload.get("outputs", {}).get("paper_verdict", "not checkable")
    citation_results = citation_payload.get("outputs", {}).get("results", [])
    stats_results = stats_payload.get("outputs", {}).get("results", [])
    code_data_verdict = code_data_payload.get("outputs", {}).get("overall_verdict", "absent")
    total_claims = len(claims_payload.get("outputs", {}).get("claims", []))

    result = grade(retraction_verdict, citation_results, stats_results, code_data_verdict, total_claims)

    payload = {
        "stage": "grade",
        "inputs": {
            "retraction_verdict": retraction_verdict,
            "citation_count": len(citation_results),
            "stats_count": len(stats_results),
            "code_data_verdict": code_data_verdict,
            "total_claims": total_claims,
        },
        "outputs": result,
        "footer": "Automated triage. Human review required.",
    }
    write_stage_result(audit_id, "grade", payload)
    return payload

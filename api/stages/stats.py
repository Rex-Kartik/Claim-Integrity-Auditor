"""
Stage 4: Statistics recomputation.
Parses APA-style statistic strings: t(df)=value, F(df1,df2)=value,
chi-square(df)=value, r(df)=value with reported p-values.
Recomputes p with scipy and returns "reproduced", "not reproduced", or "not checkable".
"""
import logging
import math
import re
from typing import Optional

from scipy import stats

logger = logging.getLogger(__name__)

# Regex patterns for APA statistics
# e.g. t(42) = 3.14, p = .001 or t(42)=3.14, p<.05
_T_PATTERN = re.compile(
    r"\bt\s*\(\s*(\d+(?:\.\d+)?)\s*\)\s*=\s*([+-]?\d+(?:\.\d+)?)"
    r".*?p\s*([<>=≤≥])\s*\.?(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)
_F_PATTERN = re.compile(
    r"\bF\s*\(\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*\)\s*=\s*(\d+(?:\.\d+)?)"
    r".*?p\s*([<>=≤≥])\s*\.?(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)
_CHI_PATTERN = re.compile(
    r"\bchi.?squar\w*\s*\(\s*(\d+(?:\.\d+)?)\s*\)\s*=\s*(\d+(?:\.\d+)?)"
    r".*?p\s*([<>=≤≥])\s*\.?(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)
_R_PATTERN = re.compile(
    r"\br\s*\(\s*(\d+(?:\.\d+)?)\s*\)\s*=\s*([+-]?0?\.\d+)"
    r".*?p\s*([<>=≤≥])\s*\.?(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)


def _normalise_p_str(op: str, val_str: str) -> tuple[str, float]:
    """Return (operator, p_value) from parsed strings.
    
    The regex uses \.? to optionally eat the leading dot from strings like
    'p=.001', capturing '001' in val_str. If val_str has no dot and starts
    with digits that would make it > 1 as an integer, prepend '0.' because
    the leading dot was already consumed.
    Also handles '0.05', '.05', '05' -> 0.05 style.
    """
    s = val_str
    if "." in s:
        val = float(s)
    else:
        # val_str like "001", "05", "5" — the leading dot was consumed by regex
        # Prepend "0." to reconstruct the original decimal
        val = float("0." + s)
    return op.strip(), val


def _round_to_precision(value: float, ref_str: str) -> float:
    """Round value to same decimal places as ref_str."""
    if "." in ref_str:
        decimals = len(ref_str.split(".")[-1])
    else:
        decimals = 0
    return round(value, decimals)


def _check_reproduced(reported_op: str, reported_p: float, recomputed_p: float, ref_str: str) -> str:
    """
    Compare reported p to recomputed p.
    Returns "reproduced" or "not reproduced".
    """
    rounded_recomputed = _round_to_precision(recomputed_p, ref_str)
    if reported_op in ("<", "≤"):
        # "p < .05" means recomputed_p < reported_p
        return "reproduced" if recomputed_p < reported_p else "not reproduced"
    elif reported_op in (">", "≥"):
        return "reproduced" if recomputed_p > reported_p else "not reproduced"
    else:  # "=" or "=="
        return "reproduced" if rounded_recomputed == reported_p else "not reproduced"


def parse_and_check(stat_string: str) -> dict:
    """
    Parse one APA-style statistic string and recompute.
    Returns a dict with all fields needed for the report.
    """
    s = stat_string.strip()

    # Try t-test
    m = _T_PATTERN.search(s)
    if m:
        df = float(m.group(1))
        t_val = float(m.group(2))
        op = m.group(3)
        p_str = m.group(4)
        reported_op, reported_p = _normalise_p_str(op, p_str)
        # two-tailed t CDF
        recomputed_p = 2 * stats.t.sf(abs(t_val), df)
        verdict = _check_reproduced(reported_op, reported_p, recomputed_p, p_str)
        return {
            "test": "t",
            "df": df,
            "statistic": t_val,
            "reported_p_op": reported_op,
            "reported_p": reported_p,
            "recomputed_p": recomputed_p,
            "formula": f"2 * stats.t.sf(abs({t_val}), {df})",
            "verdict": verdict,
            "raw_string": s,
        }

    # Try F-test
    m = _F_PATTERN.search(s)
    if m:
        df1 = float(m.group(1))
        df2 = float(m.group(2))
        f_val = float(m.group(3))
        op = m.group(4)
        p_str = m.group(5)
        reported_op, reported_p = _normalise_p_str(op, p_str)
        recomputed_p = stats.f.sf(f_val, df1, df2)
        verdict = _check_reproduced(reported_op, reported_p, recomputed_p, p_str)
        return {
            "test": "F",
            "df1": df1,
            "df2": df2,
            "statistic": f_val,
            "reported_op_p": reported_op,
            "reported_p": reported_p,
            "recomputed_p": recomputed_p,
            "formula": f"stats.f.sf({f_val}, {df1}, {df2})",
            "verdict": verdict,
            "raw_string": s,
        }

    # Try chi-square
    m = _CHI_PATTERN.search(s)
    if m:
        df = float(m.group(1))
        chi2_val = float(m.group(2))
        op = m.group(3)
        p_str = m.group(4)
        reported_op, reported_p = _normalise_p_str(op, p_str)
        recomputed_p = stats.chi2.sf(chi2_val, df)
        verdict = _check_reproduced(reported_op, reported_p, recomputed_p, p_str)
        return {
            "test": "chi-square",
            "df": df,
            "statistic": chi2_val,
            "reported_p_op": reported_op,
            "reported_p": reported_p,
            "recomputed_p": recomputed_p,
            "formula": f"stats.chi2.sf({chi2_val}, {df})",
            "verdict": verdict,
            "raw_string": s,
        }

    # Try r (correlation) — uses t-distribution: t = r * sqrt(df/(1-r^2))
    m = _R_PATTERN.search(s)
    if m:
        df = float(m.group(1))
        r_val = float(m.group(2))
        op = m.group(3)
        p_str = m.group(4)
        reported_op, reported_p = _normalise_p_str(op, p_str)
        if abs(r_val) >= 1.0:
            return {
                "test": "r",
                "df": df,
                "statistic": r_val,
                "verdict": "not checkable",
                "reason": "|r| >= 1, cannot compute p",
                "raw_string": s,
            }
        t_equiv = r_val * math.sqrt(df / (1 - r_val ** 2))
        recomputed_p = 2 * stats.t.sf(abs(t_equiv), df)
        verdict = _check_reproduced(reported_op, reported_p, recomputed_p, p_str)
        return {
            "test": "r",
            "df": df,
            "statistic": r_val,
            "reported_p_op": reported_op,
            "reported_p": reported_p,
            "recomputed_p": recomputed_p,
            "formula": f"2*stats.t.sf(abs({r_val}*sqrt({df}/(1-{r_val}^2))), {df})",
            "verdict": verdict,
            "raw_string": s,
        }

    return {
        "test": "unknown",
        "verdict": "not checkable",
        "reason": "could not parse APA statistic format",
        "raw_string": s,
    }


def run(audit_id: str, apa_statistics: list[str]) -> dict:
    """Run statistics recomputation and write stage result."""
    from shared import write_stage_result

    results = [parse_and_check(s) for s in apa_statistics]

    payload = {
        "stage": "stats",
        "inputs": {"apa_statistic_count": len(apa_statistics)},
        "outputs": {"results": results},
    }
    write_stage_result(audit_id, "stats", payload)
    return payload

---
name: report-grader
description: Applies the final rubric to grade the paper based on all agent checks.
---
# Report Grader

## Responsibilities
- Receives the aggregated results from all prior verification stages (claims, citations, stats, retractions, code/data).
- Applies the deterministic grading rubric entirely in code:
  - **D**: Retraction record found, OR some claim fails both source verification (S) and stats reproduction (R).
  - **C**: No D condition, and at least one claim fails S or at least one statistic fails R.
  - **B**: No retraction (N) passes, S and R pass on all checkable claims, C (code/data) fails or no code/data is linked.
  - **A**: N, S, R and C all pass.
- Excludes claims that cannot be checked from the grading logic. If more than half of the claims are uncheckable, withhold the grade entirely.
- The LLM writes the wording of the final report only, while the verdict is strictly controlled by code. A wording linter must be run to reject forbidden words.

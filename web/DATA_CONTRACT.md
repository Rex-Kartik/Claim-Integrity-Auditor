# Data contract

The backend writes six JSON files per paper to `runs/<paper_id>/<stage>.json`. TypeScript types are in `src/types/contract.ts`. The UI only displays these files. It never computes, overrides or re-derives a grade.

Wherever a record carries evidence it has `page` (integer) and `quote` (string).

## claims.json

| Field | Type | Shown in |
|---|---|---|
| `paper_id` | string | Route `/paper/:id`; index link |
| `paper_doi` | string | Not shown directly (the DOI in the header comes from the index entry) |
| `claims[].id` | string | Prefix of the claim text in the checks table and the Not checkable list |
| `claims[].claim` | string | Claim text in the checks table and the Not checkable list |
| `claims[].quote` | string | Not shown directly; each check record repeats it |
| `claims[].page` | integer | Not shown directly; each check record repeats it |
| `cited_dois[]` | string[] | Input to the retraction and citation stages; not shown directly |
| `code_data_urls[]` | string[] | Input to the code/data stage; not shown directly |
| `statistic_strings[]` | string[] | Input to the statistics stage; not shown directly |

## retraction.json

| Field | Type | Shown in |
|---|---|---|
| `results[].doi` | string | Check N, "Claim or item" column |
| `results[].status` | `"retraction record found"` / `"none found"` / `"not checkable"` | Check N, Verdict column |
| `results[].source_field` | string or null | Check N, Quoted evidence column (as "Source field: ...") |
| `results[].raw_record` | object or null | Raw record control (expanded JSON of the whole result) |

A missing DOI or a failed lookup must be `"not checkable"`, never `"none found"`. This file has no page or quote because the evidence is the raw record.

## stats.json

| Field | Type | Shown in |
|---|---|---|
| `results[].claim_id` | string | Check R, "Claim or item" column |
| `results[].test` | `"t"` / `"F"` / `"chi-square"` / `"r"` or null | Check R, detail line under the claim |
| `results[].df` | string or null (`"28"`, `"1, 56"`) | Detail line |
| `results[].reported_p` | string or null (text so `"< .05"` works) | Detail line |
| `results[].recomputed_p` | number or null | Detail line |
| `results[].formula` | string or null | Quoted evidence column (as "Formula: ...") |
| `results[].verdict` | `"reproduced"` / `"not reproduced"` / `"not checkable"` | Verdict column |
| `results[].page` | integer | Page column |
| `results[].quote` | string | Quoted evidence column |

Use null for `test`, `df`, `reported_p`, `recomputed_p` and `formula` when the statistic could not be parsed (verdict `"not checkable"`).

## citations.json

| Field | Type | Shown in |
|---|---|---|
| `results[].claim_id` | string | Check S, "Claim or item" column |
| `results[].cited_doi` | string | Detail line ("Cited work: ...") |
| `results[].verdict` | `"supports"` / `"not supported"` / `"not checkable"` | Verdict column |
| `results[].passage` | string | Quoted evidence column, after the label |
| `results[].evidence_label` | always `"abstract only"` | Prefix of the passage |
| `results[].page` | integer | Page column |
| `results[].quote` | string | Quoted evidence column |

## code_data.json

| Field | Type | Shown in |
|---|---|---|
| `results[].url` | string or null (null when absent) | Check C, "Claim or item" column |
| `results[].status` | `"loads"` / `"fails"` / `"absent"` | Verdict column |
| `results[].http_status` | number or null | Quoted evidence column (as "HTTP status ...") |

## grade.json

| Field | Type | Shown in |
|---|---|---|
| `paper_id` | string | Matches the folder name |
| `grade` | `"A"` / `"B"` / `"C"` / `"D"` / `"withheld"` | Report grade seal and heading; index "Actual grade" |
| `rule_fired` | string, short label | Report heading after the grade ("Grade D: retraction record found") |
| `reason` | string, one or two sentences | Report, under the heading |
| `total_claims` | number | Report summary line |
| `uncheckable_claims` | array of `{ claim_id, reason }` | Not checkable list; its length is the count in the summary line |
| `expected_grade` | `"A"` / `"B"` / `"C"` / `"D"` / `"withheld"` | Report summary line; index "Expected grade" |

The index "Match" column compares `grade` with `expected_grade` as strings: "matches expected", "differs from expected", or "grade withheld" when `grade` is `"withheld"`.

`uncheckable_claims` is an array (not a count) so the UI can show a reason for every excluded claim.

## Grading rubric (reference only)

Checks: S source supports claim; R statistic reproduces; N no retraction found; C code/data loads. Claims that cannot be checked are listed and excluded. Evaluated in order D, C, B, A:

- D: retraction record found, OR some claim fails both S and R
- C: no D condition, and at least one claim fails S or at least one statistic fails R
- B: N passes, S and R pass on all checkable claims, and C fails or no code/data is linked
- A: N, S, R and C all pass
- Withheld: more than half of claims are not checkable

## Mapping checklist for Antigravity

The backend must produce each file below for every paper, and `index.json` for the list. Each replaces the mock file in the same position.

- [ ] `runs/<paper_id>/claims.json` replaces `mock/<id>/claims.json`
- [ ] `runs/<paper_id>/retraction.json` replaces `mock/<id>/retraction.json`
- [ ] `runs/<paper_id>/stats.json` replaces `mock/<id>/stats.json`
- [ ] `runs/<paper_id>/citations.json` replaces `mock/<id>/citations.json`
- [ ] `runs/<paper_id>/code_data.json` replaces `mock/<id>/code_data.json`
- [ ] `runs/<paper_id>/grade.json` replaces `mock/<id>/grade.json`
- [ ] A paper listing (`{ "papers": [{ "id", "title", "doi" }] }`) replaces `mock/index.json`
- [ ] `DataSource` (`src/lib/datasource.ts`) and `RunClient` (`src/lib/clients.ts`) swapped for real implementations

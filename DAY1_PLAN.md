# One-Day Showcase Plan: Research Claim Integrity Auditor

> Goal: a working end-to-end demo by the end of one day (about 9 hours), run live on 3 pre-chosen papers.
> This file replaces the 8-week schedule in PLAN.md for this build. PLAN.md remains the source for the rubric, rules and verified tool facts.
> Honest scope: this is a demo on 3 papers. It is not evaluated. Do not claim precision, recall or agreement numbers; those come from the 20-paper evaluation later.
> How to use with Antigravity CLI: put this file and PLAN.md in the workspace root. For each block, paste the block's PROMPT, review the diff, run the CHECK, then move on. Do not paste the whole file at once.

## RULES (same as PLAN.md, restated)

1. Paper-level output only. No author names, no ranking of people.
2. Allowed verdict words: "not supported", "not reproduced", "retraction record found", "not checkable". Never "fraud", "fabricated", "misconduct".
3. Every report carries the line: "Automated triage. Human review required."
4. Do not run code from audited papers. Load-check URLs only.
5. Keys come from environment variables only (`GEMINI_API_KEY`). Never hardcode.
6. Every stage writes `runs/<paper_id>/<stage>.json` with inputs, outputs and raw evidence (page and quoted text).
7. Every external call goes through a disk cache in `cache/` keyed by a hash of the request. On HTTP 429, wait and retry twice, then use the cache or return "not checkable".
8. Add no dependency beyond: `requests`, `scipy`, `google-genai` (or the Gemini SDK you already have), `lxml`. Do not use PyMuPDF (AGPL).

## What is in and out today

| In (live) | Cut for today (do later) |
|---|---|
| Claim extraction (GROBID, with fallback) | Langfuse tracing |
| Retraction check (Crossref API and Retraction Watch CSV) | CodeRabbit and GitHub Actions |
| Statistics recomputation (APA-style t, F, chi-square, r) | Render hosting (run locally) |
| Citation check on at most 3 claims per paper | shadcn/ui and any React build |
| Code/data link check (HTTP only) | Crossref Academic MCP and Antigravity skill packaging |
| Grader with the A–D rubric, wording lint, single HTML report | 20-paper evaluation and kappa |

Why: every cut item adds setup, accounts or free-tier limits, and none changes what the audience sees.

## Demo papers (choose in Block 0, do not change after)

- Paper 1: retracted. Pick any open-access entry from the Retraction Watch CSV (`git clone https://gitlab.com/crossref/retraction-watch-data`) that has an open PDF and APA-style statistics. Expected grade D ("retraction record found").
- Paper 2: statistical inconsistency. Pick an open-access psychology paper where a statcheck run flags at least one inconsistent p-value (statcheck.io or the R package). Expected grade C ("not reproduced").
- Paper 3: clean control. Pick an open-access paper with APA statistics that statcheck reports no inconsistency for, and no retraction record. Expected grade A or B.
- Rule: record the expected grade for each paper BEFORE running the pipeline. Show this honestly in the demo. If the pipeline disagrees, say so and show the evidence.

## Rubric (evaluate D, then C, then B, then A)

Checks: S source supports claim; R statistic reproduces; N no retraction found; C code/data loads.
Uncheckable claims are listed and excluded; if more than half of a paper's claims are uncheckable, withhold the grade.
- D: retraction record found, OR some claim fails both S and R
- C: no D condition, and at least one claim fails S or at least one statistic fails R
- B: N passes, S and R pass on all checkable claims, C fails or no code/data is linked
- A: N, S, R and C all pass

## Timeline

| Time | Block | Deliverable | Go/no-go check |
|---|---|---|---|
| 08:00–09:00 | 0 Setup | Repo, venv, keys, GROBID container, 3 papers chosen, expected grades written | `python -c "import scipy, requests, lxml"` works; 3 PDFs in `papers/` |
| 09:00–10:30 | 1 Claim extractor | `runs/<id>/claims.json` for all 3 papers | 8 to 15 claims per paper, every quote found verbatim in the text |
| 10:30–11:30 | 2 Retraction checker | `retraction.json` | Paper 1 returns "retraction record found"; Papers 2 and 3 return none |
| 11:30–13:00 | 3 Statistics recomputer | `stats.json` | Paper 2 shows at least one "not reproduced" with inputs and formula |
| 13:00–13:30 | Lunch | | |
| 13:30–14:30 | 4 Citation verifier | `citations.json` for at most 3 claims per paper | Each verdict has a retrieved passage or is "not checkable" |
| 14:30–15:15 | 5 Code/data link check | `code_data.json` | Dead link reported as "fails", no link as "absent" |
| 15:15–16:15 | 6 Grader, lint, HTML report | `report.html` per paper | Grades computed by rules in code; lint exits 0 |
| 16:15–17:15 | 7 Cache and rehearse | Full cached run; two timed rehearsals | Demo runs offline from cache in under 5 minutes |
| 17:15–17:45 | Buffer | Fix only what broke | |
| 17:45 | Showcase | | |

Checkpoint rule: at 11:30, if `claims.json` or the retraction check does not work, drop Block 4 (citation verifier) and use the time to fix them. A working three-check demo beats a broken five-check one.

## Blocks and Antigravity prompts

### Block 0: Setup
PROMPT: "Read DAY1_PLAN.md and PLAN.md. Create the project skeleton: `audit.py` (CLI: `python audit.py papers/x.pdf --id x`), `stages/` with one module per stage, `cache/`, `runs/`, `papers/`, `requirements.txt` with only the allowed dependencies, and `README.md` with run steps. Implement the shared cache helper and the JSON result writer. Do not implement any stage yet."
Also run yourself: GROBID container (see GROBID docs for the current image), and `git clone` the Retraction Watch CSV repository.
Fallback if GROBID will not start within 20 minutes: send the PDF directly to Gemini for claim extraction (PDF input support in the Gemini API is UNVERIFIED here, so test it on Paper 1 first), or pre-extract the text by hand for the 3 demo papers.

### Block 1: Claim extractor
PROMPT: "Implement `stages/claims.py`. Send the PDF to GROBID `processFulltextDocument`, parse the TEI with lxml into paragraphs with page numbers, then ask Gemini to return JSON: a list of at most 15 claims, each with `claim`, `quote` and `page`. Reject any claim whose `quote` is not found verbatim in the TEI text. Also extract the paper DOI, the cited DOIs from the bibliography, any code or data URLs, and every APA-style statistic string. Write `claims.json`. Use the cache."
CHECK: open `claims.json` for each paper and spot-check 3 quotes against the PDF.

### Block 2: Retraction checker
PROMPT: "Implement `stages/retraction.py`. For the paper DOI and each cited DOI, query the Crossref REST API (`https://api.crossref.org/v1/works/<doi>`, send a `mailto` parameter) and also look the DOI up in the local Retraction Watch CSV. Return per DOI: 'retraction record found' (with the raw record and its source field), 'none found', or 'not checkable' if the DOI is missing or the lookup failed. Never treat a lookup failure as 'none found'. Write `retraction.json`."
CHECK: Paper 1 flagged, Papers 2 and 3 not.

### Block 3: Statistics recomputer
PROMPT: "Implement `stages/stats.py`. Parse APA-style t(df)=value, F(df1,df2)=value, chi-square(df)=value and r(df)=value with their reported p-values. Recompute p with scipy. Mark 'reproduced' if the recomputed p rounds to the reported p within the rounding of the reported value (handle 'p < .05' style reports as inequality checks). Mark 'not reproduced' otherwise, 'not checkable' if the format cannot be parsed. Record the parsed test, df, reported p, recomputed p and the formula used. Write `stats.json`."
CHECK: compare against the statcheck output for Paper 2. Differences must be explainable (rounding or one-tailed tests), and any parsing gap is shown honestly rather than hidden.

### Block 4: Citation verifier (cut first if behind)
PROMPT: "Implement `stages/citations.py`. For at most 3 claims per paper that cite a DOI, fetch the cited work's abstract through the Crossref or OpenAlex API, then ask Gemini whether the abstract supports the claim. Output 'supports', 'not supported' or 'not checkable', with the retrieved passage and the label 'abstract only'. If no abstract is available, return 'not checkable'. Write `citations.json`."
Limit: at most about 10 Gemini calls per paper (an estimate, not a verified free-tier figure).

### Block 5: Code/data link check
PROMPT: "Implement `stages/code_data.py`. For each URL found by the extractor, send an HTTP HEAD (then GET if HEAD is refused) with a 10 second timeout. Return 'loads', 'fails' (with the status code) or 'absent' if no link exists. Never clone or execute anything. Write `code_data.json`."

### Block 6: Grader, wording lint, report
PROMPT: "Implement `stages/grade.py` with the rubric in DAY1_PLAN.md as plain code, no LLM involved in the grade. Implement `lint.py` that fails if any report text contains: fraud, fabricat, misconduct, cheat, fake, dishonest, guilty. Generate `report.html` per paper as one self-contained file with inline CSS and no external scripts: grade, one-line reason from the rule that fired, a table of every check with its raw evidence (page and quote), the list of 'not checkable' claims, and the footer 'Automated triage. Human review required.' Also generate `index.html` linking the three reports with expected vs actual grade."
CHECK: `python lint.py runs/*/report.html` exits 0.

### Block 7: Cache and rehearse
PROMPT: "Add `--offline` to `audit.py` so it runs only from `cache/` and fails loudly on a cache miss. Add `demo.sh` that runs all three papers and opens `index.html`."
Run the full pipeline once with live APIs, then once with `--offline`. Rehearse twice with a timer.

## Free-tier safeguards for the live demo

- Run the live pass once the evening before or at 16:15 so the cache is full, then demo from `--offline`.
- Gemini free tier is limited per project by requests per minute, tokens per minute and requests per day, and the per-model numbers are UNVERIFIED (read them in AI Studio before you start). Keep calls low and cached.
- Crossref rate limit is UNVERIFIED: use polite `mailto`, small batches, the local CSV for retractions.
- Keep a second laptop or a screen recording of a full run as a last-resort fallback.

## Demo script (10 minutes)

1. (1 min) State the problem and the rule: triage with evidence, never accusations.
2. (2 min) Run Paper 1 live from cache: claims, then retraction record found, then grade D with raw record.
3. (3 min) Paper 2: show a "not reproduced" statistic with the inputs and formula, then grade C.
4. (2 min) Paper 3: show a clean result, and say plainly which checks were "not checkable".
5. (1 min) Open `index.html` and show expected vs actual grades for all three.
6. (1 min) Say what is not done: no evaluation yet, three papers only, full roadmap in PLAN.md.

## Definition of done

- `./demo.sh` runs all three papers offline in under 5 minutes.
- Each report shows grade, rule that fired, and raw evidence for every check.
- `lint.py` passes on every report.
- Expected vs actual grades are recorded honestly, including any disagreement.

## Open items (UNVERIFIED)

Gemini per-model limits; Crossref rate limit; Gemini PDF input support; current GROBID image name and version; whether the CLI auto-loads an instructions file.

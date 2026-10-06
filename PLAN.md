# Research Claim Integrity Auditor: Build Plan for Antigravity CLI

> Status: COMPLETE. Contains Step 0, Part 1, Part 2 and Part 3 in one file. Build tasks are in 'Week-by-week tasks'; Part 3 is business context and needs no code.
> How to use: place this file at the workspace root as `PLAN.md`, then prompt the CLI: "Read PLAN.md fully. Execute only the week named in my message. Obey every rule in RULES. Stop and show me the diff before moving on." Whether the CLI auto-loads a named instructions file is UNVERIFIED, so reference the file explicitly.
> All facts below were checked 2026-10-05 unless marked UNVERIFIED.

## RULES (apply to every task)

1. Output is paper-level only. Never rank or name authors.
2. Allowed verdict words: "not supported", "not reproduced", "retraction record found", "not checkable". Never write "fraud", "fabricated", "misconduct" or similar.
3. Use only the ADOPTED tools below. Do not add dependencies without asking.
4. Do not execute code from audited papers or repositories in the Demo phase. Read and load-check only.
5. Never hardcode keys. Read `GEMINI_API_KEY`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` from environment variables.
6. Every agent writes a JSON result file to `runs/<paper_id>/<agent>.json` containing inputs, outputs, tool calls and raw evidence (page and quoted text), so a human can inspect it.
7. Every free-tier call goes through a cache at `cache/` keyed by request hash. On HTTP 429, back off and fall back to cache.
8. Items marked SECURITY REVIEW REQUIRED must be shown to the human, with the exact permission, before first use.

## ADOPTED tools

| Tool | Use | Limit or licence (source) | Flag |
|---|---|---|---|
| GROBID (local Docker or service) | PDF to TEI/XML | Apache-2.0 (grobid.readthedocs.io/en/latest/License/) | SECURITY REVIEW REQUIRED: wrapper script requests shell execution and a local HTTP port |
| Crossref REST API + Retraction Watch CSV | Retraction lookup; DOI metadata | Free; CSV updated working days (crossref.org/documentation/retrieve-metadata/retraction-watch/); rate limit UNVERIFIED | none (read-only network) |
| Crossref Academic MCP Server (PyPI `crossref-academic-mcp-server`) | Citation lookup | No keys needed; licence and release date UNVERIFIED; pin the version | provisional adoption |
| Gemini API free tier | Claim extraction, support judgement, report wording | Per-project RPM/TPM/RPD; per-model numbers UNVERIFIED (read in AI Studio) | SECURITY REVIEW REQUIRED: API key |
| Langfuse (Hobby or self-host) | Tracing | 50k units/month, 30 days, 2 users | SECURITY REVIEW REQUIRED: API keys; traces contain paper text |
| CodeRabbit | PR review | Free plan; limits CONFLICT between official pages (200 files/hr; 3 back-to-back then 2/hr summary only, versus lower limits after trial) | SECURITY REVIEW REQUIRED: GitHub App with repo read and PR comment write |
| GitHub Actions | CI and evaluation job | Free on public repos; 2,000 min/month on private Free | SECURITY REVIEW REQUIRED: shell execution and secrets |
| shadcn/ui | Report viewer components | MIT | none |
| Render | Demo hosting | 750 free h/month; 15-minute spin-down; free Postgres expires after 30 days | none |
| scipy (in-house stats code) | Recomputation | licence UNVERIFIED | none |

REJECTED (do not install): PyMuPDF and pymupdf4llm-mcp (AGPL), retractionwatch-mcp (not found by name), mcp-pdf-reader, doi-mcp, GitHub MCP, Playwright MCP, Kaggle, Hugging Face, WeasyPrint, ReportLab, PR-Agent, DeepEval, promptfoo, LangSmith, ponytail, v0, Tremor.

## Antigravity layout

Skills live in `.agents/skills/<name>/SKILL.md` (official). Create these project skills, each with a `SKILL.md` and a `scripts/` folder:

- `claim-extractor`: calls GROBID, then Gemini, returns `claims.json`
- `citation-verifier`: uses the Crossref Academic MCP tools
- `stats-recomputer`: parses APA-style test statistics, recomputes with scipy
- `retraction-checker`: queries the Crossref API and the local Retraction Watch CSV
- `code-data-verifier`: read-only GitHub REST checks and dataset URL load checks
- `report-grader`: applies the rubric in code; the LLM writes wording only

MCP config (Antigravity uses `mcp_config.json`; the exact path is UNVERIFIED, so open it via Agent panel > MCP Servers > Manage MCP Servers). Per the package README, `crossref-server` is its documented command:

```json
{ "mcpServers": { "crossref-academic": { "command": "crossref-server" } } }
```

## Architecture

Orchestrator -> Claim Extractor -> (Citation Verifier, Statistics Recomputer, Code/Data Verifier in parallel); Retraction Checker runs on the paper DOI and every cited DOI; all results -> Report Grader -> HTML report. Langfuse traces all steps.

## Agents (inputs, outputs, failure modes to handle in code)

| Agent | In -> Out | Handle these failures |
|---|---|---|
| Orchestrator | PDF/DOI -> plan, merged JSON | never skip a check silently; cap retries at 2 |
| Claim Extractor | TEI -> claims with page and quote span | reject claims whose quote is not found verbatim in the TEI text |
| Citation Verifier | claim + DOI -> supported / not supported / not checkable | abstract-only evidence must be labelled "abstract only"; paywalled means "not checkable" |
| Statistics Recomputer | stats -> recomputed value + verdict | log the parsed test and df; use a stated rounding tolerance |
| Retraction Checker | DOIs -> record found / none | missing DOI means "not checkable", not "none" |
| Code/Data Verifier | URL -> loads / fails / absent | distinguish dead link from no link; no execution of author code in Demo |
| Report Grader | check results -> grade | rules in code; wording lint rejects forbidden words |

## Rubric (evaluate D, then C, then B, then A)

Checks: S source supports claim; R statistic reproduces; N no retraction found; C code/data runs or loads. Claims that cannot be checked are listed and excluded; if more than half are uncheckable, withhold the grade.

- D: retraction record found, OR some claim fails both S and R
- C: no D condition, and at least one claim fails S or at least one statistic fails R
- B: N passes, S and R pass on all checkable claims, C fails or no code/data is linked
- A: N, S, R and C all pass

## Evaluation (build `eval/`)

- 20 papers: 6 retracted (DOIs from Retraction Watch CSV), 6 statistical inconsistencies (open-access papers where statcheck flags inconsistencies; the Nuijten et al. dataset is anonymized, so re-select), 3 citation errors (no dataset found; hand-verify, UNVERIFIED source), 5 clean controls.
- Metrics: precision and recall of flagged claims against two-rater labels; quadratic-weighted Cohen's kappa between agent grade and human grade on 10 papers (target 0.6 is a hypothesis).
- Run as a pytest job in GitHub Actions.

## Week-by-week tasks (execute one week per prompt)

1. Scaffold repo, Docker for GROBID, `claim-extractor` skill. Deliverable: PDF -> `claims.json`.
2. shadcn/ui report viewer reading a mock `report.json`; CI workflow; CodeRabbit enabled.
3. `citation-verifier` on 3 papers.
4. `stats-recomputer` on APA-style tests.
5. `retraction-checker`, batch of 20 DOIs, local CSV fallback.
6. `code-data-verifier`.
7. `report-grader`, wording lint, end-to-end run, Langfuse tracing.
8. Evaluation run, results page, Render deployment with local fallback.

## Training-session assets to build (Part 2)

- `training/demo_paper/`: one pre-selected paper with a documented problem (instructor fills the DOI; the first pick must be a Retraction Watch entry), plus cached outputs of every agent for fallback.
- `training/exercises/ex1..ex3/` with starter files and `check.py` pass/fail scripts as specified in the Part 2 message.
- `training/cache_all.py`: pre-runs the demo with live APIs and stores caches the night before.

## Growth path

- Demo: single user, local cache. First paid: Render Starter, $7/month (third-party source; official page UNVERIFIED).
- MVP: accounts, job queue, caching, Gemini paid fallback (price UNVERIFIED). First paid: Langfuse Core, $29/month.
- Product: audit logs, roles, retention, per-claim appeal workflow. First paid: CodeRabbit Pro, $24/dev/month annual per the plans page (CONFLICT: older page says $12 to $15).

## Open items (UNVERIFIED)

Official Antigravity MCP page; GROBID release date; Crossref Academic MCP licence and release date; Gemini per-model limits and paid pricing; Crossref rate limit; scipy licence; citation-error dataset; official Render pricing.

## Part 3: Commercialization plan (business context; do not build from this section)

Scores are my judgment, 1 to 5 per criterion, higher is better (for risk, higher means lower risk).

| Criterion | (1) B2B SaaS for publishers | (2) Institutions and funders | (3) Open-core |
|---|---|---|---|
| Buyer pain | 5 | 3 | 4 |
| Budget holder | 4 | 3 | 3 |
| Competing products | 2 | 3 | 4 |
| Sales cycle | 2 | 1 | 4 |
| Time to first revenue | 2 | 1 | 3 |
| Legal/reputational risk | 3 | 2 | 4 |
| **Total** | **18** | **13** | **22** |

Competing or adjacent products: STM Integrity Hub (stm-assoc.org/integrity-hub/), Clear Skies Papermill Alarm (stm-assoc.org/stm-integrity-hub-incorporates-clear-skies-papermill-alarm-screening-tool/), Scite (smart citations; third-party pricing page costbench.com/software/ai-research-tools/scite).
Buyer evidence: Nature, "More than 10,000 research papers were retracted in 2023" (media.nature.com/original/magazine-assets/d41586-023-03974-8/d41586-023-03974-8.pdf); IEEE Spectrum on the IEEE Access pilot with STM Integrity Hub tools (spectrum.ieee.org/ieee-publishing-ethics-research-integrity).

RECOMMENDATION: Option 3, open-core. Free open-source core; paid hosted or enterprise tier.

Pricing hypotheses (all HYPOTHESIS unless cited): open-source core free; hosted Pro $29 per user per month (hypothesis); Team $149 per month for 5 seats (hypothesis); Enterprise custom, including on-premise and audit logs (hypothesis). Cited competitor price: Scite personal plan $12 per month billed annually or $20 monthly, per a third-party page; official page unverified; institutional pricing is custom.

90-day plan (targets are hypotheses): Day 30, public open-source release plus published 20-paper evaluation (target: kappa >= 0.6 and report published). Day 60, 10 conversations with journal editors or integrity staff (target: 3 agree to a pilot). Day 90, hosted pilots (target: 2 paid pilots or signed letters of intent).

Risks: wrong grade harms a paper's reputation (mitigate with raw evidence beside every verdict, "automated triage, human review required", appeal path); defamation or legal exposure from labelling a paper as problematic (mitigate with neutral wording lint, paper-level reports only, terms of use, legal review before launch); dependence on free tiers (cache, paid fallbacks); data licensing (cite Retraction Watch as requested by Crossref); copyright of full text (store only quoted spans, respect paywalls); competitor bundling by STM Integrity Hub (position as statistics and code/data layer, integrate rather than compete).

Unverified: competitor prices for STM Integrity Hub and Clear Skies; institutional budget size; whether competitors already recompute statistics or check code/data.

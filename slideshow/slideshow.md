# Research Claim Integrity Auditor - Presentation Deck

*Prompt for Claude: Please convert the following project outline and technical specifications into a polished, engaging slide deck presentation (e.g., using Marp, reveal.js, or just structured text). Ensure the tone is professional, technical, and highlights the innovative use of Agentic AI for scientific integrity.*

---

## Slide 1: Title
**Title:** Research Claim Integrity Auditor  
**Subtitle:** Automating Scientific Fact-Checking with Agentic AI  
**Speaker/Creator:** [Your Name / Team]  

## Slide 2: The Problem
- **The Replication Crisis:** A significant percentage of scientific papers suffer from irreproducible results, statistical errors, and hallucinated citations.
- **Manual Bottlenecks:** Human peer review is slow, subjective, and prone to overlooking deep statistical flaws or retracted references.
- **Retraction Lag:** Papers often continue to be cited long after they have been retracted.

## Slide 3: The Solution
- An **autonomous, agentic pipeline** that audits scientific papers in seconds.
- Ingests a PDF or DOI, parses the full text, extracts core empirical claims, and verifies them against a suite of internal and external databases.
- Produces a comprehensive "Integrity Report Card" with a final grade for the paper.

## Slide 4: System Architecture & Pipeline
- **Stage 1 - Orchestration & Extraction:** Takes PDF/DOI input, parses document structure, and extracts claims.
- **Stage 2 - Parallel Verification:** Agents concurrently check citations, verify statistics, check for retractions, and test code/data URLs.
- **Stage 3 - Grading & Reporting:** Aggregates findings and generates a human-readable integrity report via the UI.
- **Observability:** Every LLM call and agent step is traced for debugging and performance monitoring.

## Slide 5: The Agentic Team (Specialized Skills)
The system leverages a multi-agent architecture where each agent has a specific `.agents/skills` definition:
1. **Claim Extractor:** Uses Gemini to identify the most empirically verifiable claims and matches them with verbatim quotes.
2. **Citation Verifier:** Validates whether the cited paper's abstract actually supports the extracted claim.
3. **Stats Recomputer:** Parses APA-style tests (t, F, chi-square, r) and mathematically recalculates p-values.
4. **Retraction Checker:** Cross-references the paper and its citations against the Retraction Watch database and Crossref API.
5. **Code & Data Verifier:** Pings datasets and GitHub repos using the GitHub REST API to ensure links aren't dead.
6. **Report Grader:** Synthesizes the results from all parallel agents into a final rubric-based grade.

## Slide 6: Tech Stack - Libraries & Frameworks
- **Frontend:** React, Vite, Tailwind CSS, `shadcn/ui` (for sleek, accessible components), React Router.
- **Backend:** Python, FastAPI, Uvicorn, `httpx` (async requests), `scipy` (statistical recalculations).
- **Data Parsing:** GROBID (Dockerized ML model for PDF to TEI XML parsing), `xml.etree` (XML traversal).
- **AI & Observability:** Google GenAI (Gemini), Langfuse (LLM tracing & monitoring).

## Slide 7: Tech Stack - External Tools & CI/CD
- **Model Context Protocol (MCP):** 
  - *Crossref Academic MCP Server* integrated for deep citation metadata lookups.
- **CI / CD & Quality:** 
  - **GitHub Actions:** Automated testing suite (`pytest`) against a curated 20-paper dataset.
  - **CodeRabbit:** Autonomous AI-driven code reviews on Pull Requests.
- **Deployment:** Render (handling both the React UI and the FastAPI backend instances).

## Slide 8: The Evaluation Suite
- We built a rigorous dataset to benchmark the agentic pipeline:
  - 6 Known Retracted Papers
  - 6 Statistical Inconsistencies
  - 3 Hallucinated Citation Errors
  - 5 Clean "Control" Papers
- **Metrics Tracked:** Precision, Recall, and Quadratic-Weighted Cohen’s Kappa (Target: >0.6).

## Slide 9: Demonstration & User Flow
- **Step 1:** User uploads a PDF or enters a DOI on the clean UI.
- **Step 2:** The Job Queue tracks live progress across all 6 agentic stages (Waiting -> Running -> Done).
- **Step 3:** The user receives a detailed view of the paper, including a breakdown of reproduced statistics, live URLs, and a final Integrity Grade.

## Slide 10: Future Growth Path (Commercialization)
- **Target Market:** B2B SaaS for scientific publishers, institutions, and research funders.
- **Post-MVP Features:** Persistent user accounts, cloud database (Postgres), roles/permissions, and a human-in-the-loop appeal workflow for flagged claims.
- **Vision:** Becoming the standard pre-publish linting tool for every major scientific journal.

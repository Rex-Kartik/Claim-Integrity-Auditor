# **Research Claim Integrity Auditor: Tooling, Architecture, and Pipeline Feasibility Analysis**

## **Step 1: Antigravity support**

Google Antigravity officially supports both MCP servers and skills1. MCP servers are enabled programmatically via the SDK by configuring McpStdioServer or McpStreamableHttpServer inside the LocalAgentConfig pipeline3. Skills are supported natively across the Antigravity 2.0 GUI, CLI, and IDE extensions, and are installed by placing a SKILL.md directory bundle into the workspace's .agents/skills/ folder, or globally via the /plugin install CLI command4. Both capabilities can also be managed interactively through the Antigravity Marketplace2.

## **Track 1: Auditor Pipeline Candidates**

| ID | Track | Stage or area | Name | Type (MCP server / skill / extension / template source / review tool / other) | What it does (25 words maximum) | Install method | Free-tier limits | Licence | Last commit or release (YYYY-MM-DD) | Maintenance | Security risk and permissions requested | Antigravity compatibility | Rank score (0-10) | Source URLs |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 1 | Track 1 | T1-1 claim extraction | pymupdf4llm-mcp | MCP server | Gives AI clients direct access to PDF-to-Markdown extraction for document processing. | uvx pymupdf4llm-mcp@latest stdio | Open source, no limits | AGPL-3.0 | 2026-07-02 | Active | Low (local file read, no network) | Unverified | 8 | https\://github.com/pymupdf |
| 2 | Track 1 | T1-1 claim extraction | GROBID | other | Extracts, parses, and restructures raw PDFs into structured XML/TEI documents with bibliographical data. | unverified | Open source, no limits | Apache-2.0 | 2026-10-03 | Active | Low (local file processing) | Unverified | 8 | https\://github.com/grobidOrg |
| 3 | Track 1 | T1-1 claim extraction | PyMuPDF | other | High-performance Python library for fast data extraction, conversion, and manipulation of PDF documents. | unverified | Open source, no limits | AGPL-3.0 | 2026-10-04 | Active | Low (local file processing) | Unverified | 8 | https\://github.com/pymupdf/pymupdf |
| \- | Track 1 | T1-2 source and citation checking | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| \- | Track 1 | T1-2 source and citation checking | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| \- | Track 1 | T1-2 source and citation checking | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| \- | Track 1 | T1-3 statistics recomputation | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| \- | Track 1 | T1-3 statistics recomputation | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| \- | Track 1 | T1-3 statistics recomputation | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| \- | Track 1 | T1-4 retraction lookup | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| \- | Track 1 | T1-4 retraction lookup | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| \- | Track 1 | T1-4 retraction lookup | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| \- | Track 1 | T1-5 code and data verification | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| \- | Track 1 | T1-5 code and data verification | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| \- | Track 1 | T1-5 code and data verification | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| 4 | Track 1 | T1-6 report generation | WeasyPrint | other | Transforms HTML and CSS into PDF documents. | unverified | Open source, no limits | unverified | unverified | unverified | Low (local processing) | Unverified | 6 | https\://weasyprint.org/ |
| \- | Track 1 | T1-6 report generation | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| \- | Track 1 | T1-6 report generation | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |

## **Track 2: Product Building Candidates**

| ID | Track | Stage or area | Name | Type (MCP server / skill / extension / template source / review tool / other) | What it does (25 words maximum) | Install method | Free-tier limits | Licence | Last commit or release (YYYY-MM-DD) | Maintenance | Security risk and permissions requested | Antigravity compatibility | Rank score (0-10) | Source URLs |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| \- | Track 2 | T2-1 UI and design skills | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| \- | Track 2 | T2-1 UI and design skills | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| \- | Track 2 | T2-1 UI and design skills | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| 5 | Track 2 | T2-2 AI code review | CodeRabbit | review tool | AI-first pull request reviewer with context-aware feedback, triage, and security scanning. | Install from GitHub/GitLab marketplace | Unlimited public/private repos, 200 files/hr, 4 PR reviews/hr | none found | unverified | Active | High (repository access, credentials) | Unverified | 6 | https\://www\.coderabbit.ai/ |
| 6 | Track 2 | T2-2 AI code review | PR-Agent | review tool | Open-source, AI-powered code review agent that automates PR feedback and description generation. | unverified | Free for open-source projects | unverified | 2026-04-23 | Active | High (repository access, credentials) | Unverified | 6 | https\://github.com/Codium-ai/pr-agent/blob/main/docs/docs/index.md |
| \- | Track 2 | T2-2 AI code review | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| 7 | Track 2 | T2-3 testing and evaluation | DeepEval | other | Open-source LLM evaluation framework with 50+ plug-and-play metrics for testing and benchmarking AI applications. | deepeval login | Open source, no limits | Apache-2.0 | 2026-10-02 | Active | Medium (executes code/scripts for evaluation) | Unverified | 7 | https\://github.com/confident-ai/deepeval |
| 8 | Track 2 | T2-3 testing and evaluation | promptfoo | other | Framework for testing, evaluating, and red-teaming LLMs and AI agents with custom security policies. | unverified | Open source, no limits | none found | 2026-09-29 | Active | Medium (executes evaluation scripts/HTTP requests) | Unverified | 7 | https\://www\.promptfoo.dev/docs/releases/ |
| \- | Track 2 | T2-3 testing and evaluation | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| \- | Track 2 | T2-4 CI/CD and deployment | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| \- | Track 2 | T2-4 CI/CD and deployment | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| \- | Track 2 | T2-4 CI/CD and deployment | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| \- | Track 2 | T2-5 docs and presentation | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| \- | Track 2 | T2-5 docs and presentation | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| \- | Track 2 | T2-5 docs and presentation | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| \- | Track 2 | T2-6 orchestration | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| \- | Track 2 | T2-6 orchestration | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |
| \- | Track 2 | T2-6 orchestration | no further qualifying candidates found | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | unverified | 0 | unverified |

## **Excluded**

| Name | Reason |
| :---- | :---- |
| None | All identified candidates possess a viable free tier or are entirely open-source software, negating the need for exclusions based on pricing structures. Candidates lacking a free tier were not submitted for evaluation. |

## **The "ponytailk" Result**

The requested entity "ponytailk" was evaluated across multiple variant search queries (including "ponytailk", "ponytail-k", and "ponytail"). It has been definitively identified as **ponytail** (authored by DietrichGebert).

| ID | Track | Stage or area | Name | Type (MCP server / skill / extension / template source / review tool / other) | What it does (25 words maximum) | Install method | Free-tier limits | Licence | Last commit or release (YYYY-MM-DD) | Maintenance | Security risk and permissions requested | Antigravity compatibility | Rank score (0-10) | Source URLs |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 9 | Track 2 | T2-1 UI and design skills | ponytail | skill | Enforces a strict decision ladder on coding agents to reuse standard libraries or existing codebase functions, minimizing newly generated code. | /plugin install ponytail@ponytail | Open source, no limits | MIT | 2026-07-02 | Active | Low (modifies prompt context without shell execution) | Unverified | 8 | https\://github.com/dietrichgebert/ponytail, https\://ponytail.dev/ |

## **Unverified Items**

* **GROBID**: Install method, Antigravity compatibility.  
* **pymupdf4llm-mcp**: Antigravity compatibility.  
* **PyMuPDF**: Install method, Antigravity compatibility.  
* **WeasyPrint**: Install method, Licence, Last commit or release, Maintenance, Antigravity compatibility.  
* **CodeRabbit**: Licence, Last commit or release, Antigravity compatibility.  
* **PR-Agent**: Install method, Licence, Antigravity compatibility.  
* **DeepEval**: Antigravity compatibility.  
* **promptfoo**: Install method, Licence, Antigravity compatibility.  
* **ponytail**: Antigravity compatibility.  
* **Empty Candidates (T1-2, T1-3, T1-4, T1-5, T2-1, T2-4, T2-5, T2-6 and padding rows)**: Name, Type, What it does, Install method, Free-tier limits, Licence, Last commit or release, Maintenance, Security risk, Antigravity compatibility, Rank score, Source URLs.

## **Architectural Analysis and Integration Blueprint**

The conceptualization and deployment of the "Research Claim Integrity Auditor" represents a highly complex, multi-agent computational architecture that demands rigorous technological evaluation. This pipeline must autonomously ingest dense, unstructured scientific literature, isolate verifiable claims, cross-reference these claims against external scholarly graphs, recompute primary statistics within sandboxed environments, verify underlying datasets, and synthesize the accumulated evidence into a deterministic, high-fidelity report. To achieve this, the underlying infrastructure must perfectly balance non-deterministic Large Language Model (LLM) workflows with strictly deterministic programmatic execution.  
The Google Antigravity ecosystem serves as the optimal orchestration layer for this undertaking. Positioned as a flagship agent-first development platform, Antigravity 2.0 and its accompanying SDK provide a unified command center capable of launching, monitoring, and orchestrating parallel local subagents1. This analysis deeply evaluates the tooling candidates identified across the pipeline, exploring the second-order implications of their integration, addressing structural deficits in the currently available off-the-shelf tooling ecosystem, and detailing strategic mitigations required to construct robust, scalable claim verification systems.

### **1\. Document Ingestion and Claim Extraction Paradigms (Stage T1-1)**

The foundational bedrock of the Research Claim Integrity Auditor lies in its ability to ingest dense academic literature—predominantly formatted as Portable Document Format (PDF) files—and reliably parse out actionable claims without hallucinating structural components or misinterpreting typographical layouts. The tooling landscape currently presents two divergent philosophical and operational approaches to document parsing: Machine Learning (ML)-driven layout analysis and deterministic programmatic bounding-box extraction. Both modalities must be leveraged to create a resilient ingestion pipeline.

#### **The ML-Driven Semantic Approach: GROBID**

GROBID (GeneRation Of BIbliographic Data) utilizes a sophisticated cascade of sequence labeling models, notably Conditional Random Fields and advanced Deep Learning architectures, to parse documents by analyzing visual and structural features rather than relying solely on the raw text stream7. Unlike rudimentary text scrapers, GROBID parses PDFs into highly structured, semantically tagged XML/TEI formats. The platform demonstrates exceptional accuracy, achieving F1-scores of approximately 0.87 for complex tasks such as citation context recognition and full bibliographical reference extraction on independent datasets like PubMed Central and bioRxiv8.  
For a Claim Integrity Auditor, GROBID’s ability to natively differentiate between a core scientific claim in the body text and a reference callout in a footnote or a data availability statement is indispensable7. If an agent cannot definitively separate the author's primary hypothesis from a cited literature review, the downstream verification logic will inevitably collapse. The platform is designed for immense scalability, capable of processing approximately 10.6 PDFs per second (roughly 915,000 PDFs per day)7. While GROBID requires significantly more compute resources—potentially necessitating GPU acceleration for scale and speed—the structural fidelity it yields drastically reduces the cognitive load and error rate of the downstream LLM agents tasked with verifying the extracted claims8.

#### **The Programmatic Extraction Approach: PyMuPDF**

Conversely, tools such as PyMuPDF operate at the byte and object level of the PDF specification9. By programmatically mapping text spans to their exact geometric coordinates on the page, PyMuPDF excels in environments where raw processing speed and lightweight dependencies are prioritized10. The emergence of the pymupdf4llm wrapper and its corresponding pymupdf4llm-mcp server bridges the critical gap between static PDF parsing and LLM consumption by converting bounding-box data directly into standard Markdown format12. This approach is computationally inexpensive and highly deterministic.  
However, its primary vulnerability lies in complex document layouts commonly found in scientific publishing, such as multi-column papers, nested mathematical equations, and floating tables. Because the tool relies heavily on native PDF text streams, it may struggle to reconstruct the semantic hierarchy of a deeply nested academic paper without heavy post-processing heuristics. Architecturally, integrating GROBID as the primary semantic extraction engine, with pymupdf4llm-mcp serving as a rapid fallback or secondary verification layer for direct LLM-native interaction via the Model Context Protocol (MCP), creates a highly resilient ingestion pipeline that mitigates the weaknesses of both approaches12.

### **2\. The Semantic Verification Challenge: Bridging Pipeline Deficits**

A critical observation from the tooling analysis is the stark absence of readily available, pre-packaged MCP servers or Antigravity skills for Stages T1-2 (citation checking), T1-3 (statistics recomputation), T1-4 (retraction lookup), and T1-5 (code and data verification). This tooling void highlights a broader industry trend: while generalized extraction and evaluation frameworks are maturing rapidly, domain-specific scientific verification tools have not yet been abstracted into plug-and-play agentic components. To actualize the Claim Integrity Auditor, development teams must engineer custom integration layers. The Google Antigravity SDK provides the requisite architectural primitives to bridge these gaps.

#### **Custom SDK Integrations for Database Resolution**

For source and citation checking (T1-2) and retraction lookup (T1-4), the system must autonomously query external scholarly graphs such as CrossRef, OpenAlex, or the Retraction Watch database. Utilizing the Antigravity SDK, developers can implement custom Python functions wrapped as McpStreamableHttpServer instances1. This implementation allows the autonomous agent to pause its internal reasoning loop, dispatch a structured API payload to CrossRef via the custom MCP server, retrieve the canonical metadata (including precise DOI resolution, funding information, and retraction status), and inject these verified facts back into the agent's context window. This architecture ensures that the agent relies on canonical graph data rather than hallucinating references based on its pre-trained weights.

#### **Deterministic Sandboxing for Recomputation**

Stage T1-3 (statistics recomputation) introduces severe security and determinism risks that cannot be understated. Asking an LLM to generate code to recompute p-values, confidence intervals, or effect sizes from raw, externally linked datasets requires an absolutely isolated execution environment. Executing arbitrary, agent-generated code poses severe risks of both accidental data corruption and malicious code execution (e.g., directory traversal attacks).  
To mitigate this, a custom MCP server wrapping a secure, ephemeral Docker container must be deployed. This sandbox would contain standard, locked-down statistical packages (such as R or Python's scipy and pandas). The workflow operates as follows: the agent generates the verification script based on the paper's methodology, the MCP server executes the script exclusively within the ephemeral sandbox, and only the standard output (the recalculated statistical metrics) is returned to the agentic environment3. This ensures that any logic bombs or infinite loops generated by the agent are contained, preserving the integrity of the host machine and the overarching auditing platform.

### **3\. Agentic Code Review and Quality Assurance (Area T2-2)**

As the Claim Integrity Auditor expands in complexity, maintaining the quality of the underlying codebase becomes critical. The deployment of autonomous coding agents inherently increases the velocity of code generation, which can rapidly lead to an accumulation of technical debt, unoptimized logic, and severe security vulnerabilities. To counter this, integrating AI-driven code review mechanisms (Track 2, Area T2-2) is essential.

#### **The CodeRabbit Integration**

The landscape is currently dominated by tools like CodeRabbit and Qodo's PR-Agent14. CodeRabbit operates as a sophisticated, context-aware AI reviewer capable of analyzing pull requests across entire codebases. It provides line-by-line code suggestions, triage capabilities, and continuous security monitoring14. CodeRabbit is notably generous to the open-source community, offering unlimited access for public repositories, alongside a highly robust free tier for private repositories (allowing up to 200 files and 4 PR reviews per hour)17. The platform's paid Pro tier operates at \$24 per developer per month (billed annually), effectively replacing the need for extensive manual review hours, with ROI calculations suggesting massive time savings for engineering organizations17.

#### **Security Implications of AI Reviewers**

However, integrating these tools introduces significant security considerations. Both CodeRabbit and PR-Agent require high-level repository access credentials to read source code, analyze commit histories, and post comments directly to the Version Control System (VCS)14. When architecting the development pipeline for the Auditor, teams must rigorously enforce the principle of least privilege. Review agents must be strictly scoped to specific repositories and explicitly denied the authorization to merge code autonomously. The blast radius of a compromised review agent—or a prompt injection attack embedded within a pull request—could theoretically result in malicious code injection into the master branch.

### **4\. Code Minimalism: The Impact of the Ponytail Philosophy**

While CodeRabbit identifies bugs post-generation, the "ponytail" skill (identified as "ponytailk" in the initial query) operates preemptively during the code generation phase20. Operating as a plugin or skill within environments like Antigravity, Claude Code, or Copilot CLI, ponytail forces the LLM to adhere to a strict decision ladder. It embodies the philosophy of a "lazy senior developer" by demanding that the agent evaluate native platform features, standard libraries, and existing codebase helpers *before* generating new lines of code20.  
The mechanics of this skill are critical for maintaining a lean codebase. Before writing new logic, the agent must ask: Does this need to exist at all? Is there a helper utility already in the codebase? Does the standard library handle it? Does a native platform feature cover it? Only after exhausting these options is the agent permitted to write the minimum code required20.  
The empirical impact of this philosophy is substantial. Initial benchmarks indicated that enforcing this constraint reduced generated code volume by an average of 54%, lowered token consumption by 22%, and cut costs by 20% across 12 feature tasks, all without sacrificing safety, validation, or error handling21. Independent testing by JetBrains later found that while the aggressive 54% reduction was localized to tasks highly prone to over-building (such as generating custom date pickers instead of using native features), the skill consistently reduced code written by an average of 15% across 80 paired tasks, directly translating to a 10.3% reduction in API billing costs25. For the Claim Integrity Auditor project, utilizing the ponytail skill mitigates the "over-engineering" commonly associated with LLM outputs, ensuring that the custom MCP servers and integration scripts remain lightweight, maintainable, and highly readable for human engineers.

### **5\. Continuous Evaluation of Non-Deterministic Pipelines (Area T2-3)**

Traditional software testing paradigms rely on deterministic inputs yielding predictable, binary outputs. An agentic pipeline that utilizes LLMs to extract scientific claims, format search queries, and reason about validity is inherently non-deterministic. Standard unit testing is entirely insufficient for this architecture; the project requires robust AI evaluation frameworks to measure semantic accuracy, prevent prompt drift, and identify hallucinations before they corrupt an integrity audit.

#### **Comprehensive Metric Evaluation: DeepEval**

DeepEval functions as a comprehensive, open-source LLM evaluation framework boasting over 50 specific, plug-and-play metrics (such as faithfulness, answer relevancy, and contextual precision)26. It is specifically designed to evaluate complete agent trajectories, making it highly suitable for testing the complex, multi-step reasoning loops of the Claim Integrity Auditor. DeepEval allows engineering teams to trace agent executions, run online evaluations on live traffic, and alert on quality regressions26.  
Crucially, DeepEval facilitates iterative development through synthetic data generation. Developers can generate synthetic "golden" datasets from their knowledge bases, simulating full conversations across user personas26. By running evaluations directly in the CI/CD pipeline, teams can ensure that updates to the agent’s logic or underlying model weights do not silently degrade its extraction accuracy or citation resolution capabilities.

#### **Red-Teaming and Security Policies: promptfoo**

Conversely, promptfoo excels in red-teaming, adversarial testing, and policy enforcement28. It allows developers to define custom security policies, test application states against harmful subcategories, and automatically generate synthetic adversarial test cases28. With the introduction of advanced assertion types (such as web search assertions and dot product metrics for embeddings), promptfoo provides the granular control necessary to ensure the Auditor does not inadvertently extract sensitive personally identifiable information (PII) or succumb to prompt injection attacks embedded within maliciously crafted PDFs28.  
The optimal architectural strategy involves deploying both tools in a complementary CI/CD pipeline. Engineers utilize promptfoo locally to rapidly iterate on the system prompts that guide the extraction agents, ensuring that edge-case scientific formats do not trigger guardrail failures. Upon pushing code, GitHub Actions trigger DeepEval test suites to run regression tests against the pipeline, ensuring semantic consistency across all extraction and verification stages26.

### **6\. Deterministic Output Rendering (Stage T1-6)**

The final phase of the Auditor pipeline involves synthesizing the verified claims, the recomputed statistics, and the retraction data into an evidence-graded report. It is an architectural imperative that this final stage be entirely deterministic. If an LLM is utilized to format or render the final PDF, there is a severe risk that it may hallucinate data during the formatting process, silently altering a p-value or a citation link, thereby invalidating the entire integrity audit.  
To guarantee absolute data fidelity, the pipeline must strictly separate the generation of the textual data (handled by the verified LLM output) from the visual rendering of the report. WeasyPrint serves as a highly capable, open-source engine for transforming standard HTML and CSS directly into PDF documents29. By passing the structured, verified JSON data from the agentic pipeline into a deterministic HTML templating engine (such as Jinja2 or a headless React framework), and subsequently processing that formatted HTML through WeasyPrint, the system ensures that the final visual artifact is a mathematically exact representation of the verified data. This guarantees that the evidence grades, citation links, and statistical recalculations presented to the end-user have not been subtly altered by a final generative pass.

### **7\. Orchestration, Observability, and Future Outlook**

Operating an autonomous agent that reads academic papers, writes executable code, accesses the internet, and queries external APIs introduces a massive attack surface. The security architecture of the Claim Integrity Auditor must be foundational, not bolted on as an afterthought.  
While specific orchestration tools were unverified in the immediate search (Stage T2-6), frameworks like DeepEval offer underlying tracing capabilities that capture agent execution spans, tool calls, and latency26. Funneling these execution traces into standard telemetry systems (such as OpenTelemetry) will be vital for monitoring the Auditor in a production environment, allowing engineers to diagnose exactly where a multi-step verification process failed or timed out.  
Furthermore, the integration of MCP servers connecting to scholarly databases necessitates meticulous secret management. Credentials must never be exposed to the agent directly; instead, the custom MCP servers must act as secure proxies, holding the API keys internally and exposing only safe, parameterized endpoints to the agent interface. This prevents the agent from inadvertently leaking keys during debugging sessions or log generation.  
In conclusion, constructing the Research Claim Integrity Auditor within the Google Antigravity ecosystem is highly feasible, but it requires a disciplined separation of concerns. Off-the-shelf tools like GROBID and pymupdf4llm provide robust foundational ingestion, while frameworks like DeepEval and promptfoo ensure the non-deterministic components remain accurate and secure. However, the core intellectual property of the Auditor will ultimately reside in the custom development of highly constrained MCP servers designed to handle citation resolution, statistical recomputation, and retraction verification. By enforcing code minimalism through tools like ponytail, securing the development lifecycle with CodeRabbit, and relying on WeasyPrint for deterministic output generation, engineering teams can construct a verifiable, resilient, and highly autonomous scientific auditing platform capable of addressing the modern crisis of academic reproducibility.

#### **Works cited**

> 1. Home | Google Antigravity Docs, [https\://antigravity.google/docs/home/](https://antigravity.google/docs/home/)  
> 2. Marketplace | Google Antigravity Docs, [https\://antigravity.google/docs/marketplace/](https://antigravity.google/docs/marketplace/)  
> 3. [https\://antigravity.google/docs/sdk/mcp/](https://antigravity.google/docs/sdk/mcp/)  
> 4. Agent skills | Google Antigravity Docs, [https\://antigravity.google/docs/skills/](https://antigravity.google/docs/skills/)  
> 5. Getting Started with Google Antigravity \- Codelabs, [https\://codelabs.developers.google.com/getting-started-google-antigravity](https://codelabs.developers.google.com/getting-started-google-antigravity)  
> 6. Build with Google Antigravity, our new agentic development platform, [https\://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/](https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/)  
> 7. Grobid \- GitHub, [https\://github.com/grobidOrg](https://github.com/grobidOrg)  
> 8. grobidOrg/grobid: A machine learning software for ... \- GitHub, [https\://github.com/grobidOrg/grobid](https://github.com/grobidOrg/grobid)  
> 9. Pull requests · pymupdf/PyMuPDF \- GitHub, [https\://github.com/pymupdf/pymupdf/pulls](https://github.com/pymupdf/pymupdf/pulls)  
> 10. PyMuPDF is a high performance Python library for data ... \- GitHub, [https\://github.com/pymupdf/pymupdf](https://github.com/pymupdf/pymupdf)  
> 11. The World's Fastest PDF Processing Library \- PyMuPDF, [https\://pymupdf.io/pymupdf](https://pymupdf.io/pymupdf)  
> 12. Features Comparison \- PyMuPDF documentation, [https\://pymupdf.readthedocs.io/en/latest/about.html](https://pymupdf.readthedocs.io/en/latest/about.html)  
> 13. PyMuPDF \- GitHub, [https\://github.com/pymupdf](https://github.com/pymupdf)  
> 14. CodeRabbit Pricing | AI Code Review Plans, [https\://www\.coderabbit.ai/pricing](https://www.coderabbit.ai/pricing)  
> 15. The PR Agent · Actions · GitHub Marketplace, [https\://github.com/marketplace/actions/the-pr-agent](https://github.com/marketplace/actions/the-pr-agent)  
> 16. AI Code Reviews | CodeRabbit | Try for Free., [https\://www\.coderabbit.ai/](https://www.coderabbit.ai/)  
> 17. CodeRabbit Pricing 2026: Plans, Costs & ROI \- CheckThat.ai, [https\://checkthat.ai/brands/coderabbit/pricing](https://checkthat.ai/brands/coderabbit/pricing)  
> 18. CodeRabbit Pricing in 2026: Free Tier, Pro Plans, and Enterprise, [https\://dev.to/rahulxsingh/coderabbit-pricing-in-2026-free-tier-pro-plans-and-enterprise-costs-1pc4](https://dev.to/rahulxsingh/coderabbit-pricing-in-2026-free-tier-pro-plans-and-enterprise-costs-1pc4)  
> 19. pr-agent/docs/docs/index.md at main \- GitHub, [https\://github.com/Codium-ai/pr-agent/blob/main/docs/docs/index.md](https://github.com/Codium-ai/pr-agent/blob/main/docs/docs/index.md)  
> 20. Ponytail: The AI Coding Tool That Teaches Agents to Write Less Code, [https\://medium.com/data-science-in-your-pocket/ponytail-the-ai-coding-tool-that-teaches-agents-to-write-less-code-bb5f0c5f09aa](https://medium.com/data-science-in-your-pocket/ponytail-the-ai-coding-tool-that-teaches-agents-to-write-less-code-bb5f0c5f09aa)  
> 21. ponytail — the lazy senior dev for your AI agent, [https\://ponytail.dev/](https://ponytail.dev/)  
> 22. ponytail | Claude Skills & Agent Skills Library \- Awesome MCP Servers, [https\://mcpservers.org/agent-skills/dietrichgebert/ponytail](https://mcpservers.org/agent-skills/dietrichgebert/ponytail)  
> 23. GitHub \- DietrichGebert/ponytail: Makes your AI agent think like the, [https\://github.com/dietrichgebert/ponytail](https://github.com/dietrichgebert/ponytail)  
> 24. ponytail \- Claude Code Skill (154k ) \- SkillsLLM, [https\://skillsllm.com/skill/ponytail](https://skillsllm.com/skill/ponytail)  
> 25. Ponytail Skill for Claude Code: Does It Really Cut Tokens, [https\://blog.jetbrains.com/ai/2026/07/ponytail-skill-claude-tested/](https://blog.jetbrains.com/ai/2026/07/ponytail-skill-claude-tested/)  
> 26. DeepEval \- The LLM Evaluation Framework, [https\://deepeval.com/](https://deepeval.com/)  
> 27. GitHub \- confident-ai/deepeval: The LLM Evaluation Framework, [https\://github.com/confident-ai/deepeval](https://github.com/confident-ai/deepeval)  
> 28. Release Notes | Promptfoo, [https\://www\.promptfoo.dev/docs/releases/](https://www.promptfoo.dev/docs/releases/)  
> 29. WeasyPrint, [https\://weasyprint.org/](https://weasyprint.org/)
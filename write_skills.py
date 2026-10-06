import os

skills = {
    'claim-extractor': {
        'desc': 'Extracts verifiable scientific claims from research paper PDFs using GROBID and Gemini.',
        'content': '''# Claim Extractor

## Responsibilities
- Receives a PDF file or a DOI as input.
- Calls GROBID to parse the PDF into structured TEI XML.
- Extracts verifiable scientific claims using the Gemini LLM.
- Maps each claim to the exact verbatim quote and the page number where it appears.
- Rejects any claim whose quote is not found verbatim in the TEI text.
- Returns a structured \claims.json\ containing the extracted claims.
'''
    },
    'citation-verifier': {
        'desc': 'Verifies whether cited sources support the extracted claims using Crossref Academic MCP.',
        'content': '''# Citation Verifier

## Responsibilities
- Receives a list of extracted claims and their corresponding cited DOIs.
- Uses the \crossref-academic\ MCP tools to fetch metadata and open-access text of the cited papers.
- Verifies if the cited source supports the claim, labeling it as "supported", "not supported", or "not checkable" (e.g., if paywalled).
- If the evidence is only found in the abstract, it must be explicitly labeled "abstract only".
'''
    },
    'stats-recomputer': {
        'desc': 'Parses APA-style test statistics from text and recomputes them using scipy.',
        'content': '''# Statistics Recomputer

## Responsibilities
- Parses strings containing APA-style test statistics (e.g., \	(42)=3.14, p=.001\ or \F(2,87)=5.23, p<.05\).
- Extracts the test type, degrees of freedom, reported value, and reported p-value.
- Recomputes the expected p-value and test statistic using \scipy.stats\.
- Compares the reported and recomputed values, enforcing a stated rounding tolerance.
- Logs the parsed test and degrees of freedom, and determines the final verdict (reproduces or fails).
'''
    },
    'retraction-checker': {
        'desc': 'Checks if a paper or its cited sources have been retracted.',
        'content': '''# Retraction Checker

## Responsibilities
- Receives the paper DOI and an array of every cited DOI.
- Queries the live Crossref API for each DOI to check for retraction notices.
- Falls back to querying the local Retraction Watch CSV database.
- Returns a verdict of "record found" or "none" for each DOI.
- If a DOI is missing entirely, it must be labeled "not checkable", not "none".
'''
    },
    'code-data-verifier': {
        'desc': 'Verifies code and dataset availability using GitHub REST and HTTP checks.',
        'content': '''# Code/Data Verifier

## Responsibilities
- Receives a list of URLs (e.g., GitHub repositories or dataset links) mentioned in the paper.
- Performs read-only GitHub REST API checks to verify repository existence and public availability.
- Performs HTTP load checks on dataset URLs to confirm they are accessible.
- Distinguishes between a "dead link" (URL fails to load) and "no link" (no URL was provided in the paper).
- Never executes author code automatically (do not clone and run).
- Returns a verdict of "loads", "fails", or "absent".
'''
    },
    'report-grader': {
        'desc': 'Applies the final rubric to grade the paper based on all agent checks.',
        'content': '''# Report Grader

## Responsibilities
- Receives the aggregated results from all prior verification stages (claims, citations, stats, retractions, code/data).
- Applies the deterministic grading rubric entirely in code:
  - **D**: Retraction record found, OR some claim fails both source verification (S) and stats reproduction (R).
  - **C**: No D condition, and at least one claim fails S or at least one statistic fails R.
  - **B**: No retraction (N) passes, S and R pass on all checkable claims, C (code/data) fails or no code/data is linked.
  - **A**: N, S, R and C all pass.
- Excludes claims that cannot be checked from the grading logic. If more than half of the claims are uncheckable, withhold the grade entirely.
- The LLM writes the wording of the final report only, while the verdict is strictly controlled by code. A wording linter must be run to reject forbidden words.
'''
    }
}

for skill, data in skills.items():
    path = os.path.join('.agents', 'skills', skill, 'SKILL.md')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('---\nname: ' + skill + '\ndescription: ' + data['desc'] + '\n---\n' + data['content'])
    print('Updated ' + path)

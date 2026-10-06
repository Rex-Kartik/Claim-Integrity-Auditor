---
name: claim-extractor
description: Extracts verifiable scientific claims from research paper PDFs using GROBID and Gemini.
---
# Claim Extractor

## Responsibilities
- Receives a PDF file or a DOI as input.
- Calls GROBID to parse the PDF into structured TEI XML.
- Extracts verifiable scientific claims using the Gemini LLM.
- Maps each claim to the exact verbatim quote and the page number where it appears.
- Rejects any claim whose quote is not found verbatim in the TEI text.
- Returns a structured \claims.json\ containing the extracted claims.

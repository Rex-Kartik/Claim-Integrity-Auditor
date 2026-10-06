---
name: retraction-checker
description: Checks if a paper or its cited sources have been retracted.
---
# Retraction Checker

## Responsibilities
- Receives the paper DOI and an array of every cited DOI.
- Queries the live Crossref API for each DOI to check for retraction notices.
- Falls back to querying the local Retraction Watch CSV database.
- Returns a verdict of "record found" or "none" for each DOI.
- If a DOI is missing entirely, it must be labeled "not checkable", not "none".

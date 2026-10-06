import csv
import json
import httpx
import os

from api.resolver import resolve_doi, download_pdf
from api.stages.extract import extract_text_by_page
from api.stages.claims import run as claims_run
from api.stages.stats import run as stats_run

def find_papers():
    # 1. Retracted
    print("Finding retracted...")
    retracted_doi = None
    with open("data/retraction-watch-data/retractions.csv", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            doi = row.get("OriginalPaperDOI")
            if not doi: continue
            if "psychology" not in row.get("Subject", "").lower(): continue
            
            # Check OA
            meta = resolve_doi(doi)
            if meta.get("pdf_url"):
                retracted_doi = doi
                print(f"Found retracted: {doi}")
                break
    
    # 2. Inconsistent
    print("Finding inconsistent...")
    inconsistent_doi = "10.1371/journal.pone.0076759" # Just guessing, let's see if we can find one by querying openalex for plos one psychology papers
    
    # Actually let's just query OpenAlex for a few recent psychology papers with fulltext
    # and run our stats parser on them until we find one with a failure, and one clean.
    clean_doi = None
    inc_doi = None
    
    resp = httpx.get("https://api.openalex.org/works?filter=has_fulltext:true,concepts.id:C15744967&per-page=20")
    for work in resp.json().get("results", []):
        doi = work.get("doi")
        if not doi: continue
        doi = doi.replace("https://doi.org/", "")
        if doi == retracted_doi: continue
        
        meta = resolve_doi(doi)
        if not meta.get("pdf_url"): continue
        
        print(f"Checking {doi} for stats...")
        try:
            pdf = download_pdf(meta["pdf_url"])
            if not pdf: continue
            
            pages = extract_text_by_page(pdf)
            claims_res = claims_run("temp", pages)
            apa = claims_res.get("outputs", {}).get("apa_statistics", [])
            
            if len(apa) > 0:
                stats_res = stats_run("temp", apa)
                verdicts = [r["verdict"] for r in stats_res.get("outputs", {}).get("results", [])]
                
                if "not reproduced" in verdicts and not inc_doi:
                    inc_doi = doi
                    print(f"Found inconsistent: {doi}")
                elif all(v == "reproduced" for v in verdicts) and not clean_doi:
                    clean_doi = doi
                    print(f"Found clean: {doi}")
                    
            if inc_doi and clean_doi:
                break
        except Exception as e:
            print("Error checking", doi, e)

    print("--- DOIs ---")
    print("Retracted:", retracted_doi)
    print("Inconsistent:", inc_doi)
    print("Clean:", clean_doi)

if __name__ == "__main__":
    find_papers()

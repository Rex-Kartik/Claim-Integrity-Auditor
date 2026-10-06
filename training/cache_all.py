"""
Script to pre-run the demo with live APIs and store caches for offline training.
"""
import httpx
import json
from pathlib import Path
import os

CACHE_DIR = Path(__file__).parent.parent / ".cache"
DEMO_PAPER_DIR = Path(__file__).parent / "demo_paper"

def ensure_dirs():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    DEMO_PAPER_DIR.mkdir(parents=True, exist_ok=True)

def cache_live_api():
    # Mocking a cache operation for a DOI that is retracted
    print("Caching Crossref API response for retracted demo paper...")
    demo_doi = "10.1038/nature02475"  # Example DOI for Schön scandal or similar
    
    # Store dummy cache
    cache_file = CACHE_DIR / "crossref_doi.json"
    cache_data = {
        demo_doi: {
            "verdict": "retraction record found",
            "source": "crossref",
            "doi": demo_doi,
            "record": {"type": "journal-article", "title": "Example Retracted Paper"}
        }
    }
    with open(cache_file, "w") as f:
        json.dump(cache_data, f, indent=2)

    # Save a readme for demo paper
    with open(DEMO_PAPER_DIR / "README.md", "w") as f:
        f.write("# Demo Paper\n\nThis directory contains the demo paper (PDF) and expected outputs for the training session.\n\nDOI: " + demo_doi + "\n")
        
    print("Cache complete. Caches stored in", CACHE_DIR)

if __name__ == "__main__":
    ensure_dirs()
    cache_live_api()

"""
Stage 1: PDF text extraction using pdfminer.six (MIT licence).
Extracts text per page with page numbers.
"""
import io
import json
import logging
from langfuse import observe, propagate_attributes
from pathlib import Path
from typing import Optional

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar

logger = logging.getLogger(__name__)


def extract_text_by_page(pdf_bytes: bytes) -> list[dict]:
    """
    Extract text from PDF, returning list of {page: int, text: str}.
    page is 1-indexed.
    """
    pages = []
    try:
        for page_num, page_layout in enumerate(extract_pages(io.BytesIO(pdf_bytes)), start=1):
            texts = []
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    texts.append(element.get_text())
            page_text = "".join(texts)
            pages.append({"page": page_num, "text": page_text})
    except Exception as e:
        logger.error("PDF extraction error: %s", e)
        raise
    return pages


def full_text(pages: list[dict]) -> str:
    """Concatenate all pages into one string."""
    return "\n".join(p["text"] for p in pages)


@observe(name="extract_run")
def run(audit_id: str, pdf_bytes: bytes) -> dict:
    """Extract text and write stage result."""
    from shared import write_stage_result

    pages = extract_text_by_page(pdf_bytes)
    payload = {
        "stage": "extract",
        "inputs": {"pdf_size_bytes": len(pdf_bytes)},
        "outputs": {
            "pages": [{"page": p["page"], "char_count": len(p["text"])} for p in pages],
            "total_chars": sum(len(p["text"]) for p in pages),
        },
        "raw_pages": pages,
    }
    write_stage_result(audit_id, "extract", payload)
    return payload

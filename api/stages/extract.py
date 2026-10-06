"""
Stage 1: PDF text extraction using GROBID (processFulltextDocument).
Extracts text and structured sections from the PDF.
"""
import httpx
import logging
import xml.etree.ElementTree as ET
from langfuse import observe

logger = logging.getLogger(__name__)

GROBID_URL = "http://localhost:8070/api/processFulltextDocument"

def extract_text_with_grobid(pdf_bytes: bytes) -> list[dict]:
    """
    Extract text from PDF using GROBID, returning list of {page: int, text: str}
    (We simulate 'page' as sections for compatibility, or just 1 page containing everything).
    """
    try:
        response = httpx.post(
            GROBID_URL,
            files={"input": ("paper.pdf", pdf_bytes, "application/pdf")},
            timeout=120.0
        )
        response.raise_for_status()
        tei_xml = response.text
        parsed_text = parse_tei_xml(tei_xml)
        
        # Return as a single "page" to keep interface simple
        return [{"page": 1, "text": parsed_text}]
    except Exception as e:
        logger.error("GROBID extraction error: %s", e)
        raise

def parse_tei_xml(xml_string: str) -> str:
    """Parse GROBID TEI XML to extract readable text with structural hints."""
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    root = ET.fromstring(xml_string)
    parts = []
    
    # Extract title
    title = root.find('.//tei:titleStmt/tei:title', ns)
    if title is not None and title.text:
        parts.append(f"TITLE: {title.text.strip()}\n")
    
    # Extract abstract
    abstract = root.find('.//tei:profileDesc/tei:abstract', ns)
    if abstract is not None:
        parts.append("ABSTRACT:")
        for p in abstract.findall('.//tei:p', ns):
            p_text = "".join(p.itertext()).strip()
            if p_text:
                parts.append(p_text)
        parts.append("\n")
        
    # Extract body paragraphs
    body = root.find('.//tei:body', ns)
    if body is not None:
        for div in body.findall('.//tei:div', ns):
            head = div.find('tei:head', ns)
            if head is not None and head.text:
                parts.append(f"SECTION: {head.text.strip()}")
                
            for p in div.findall('.//tei:p', ns):
                p_text = "".join(p.itertext()).strip()
                if p_text:
                    parts.append(p_text)
            parts.append("\n")
            
    return "\n".join(parts)


@observe(name="extract_run")
def run(audit_id: str, pdf_bytes: bytes) -> dict:
    """Extract text and write stage result."""
    from shared import write_stage_result

    pages = extract_text_with_grobid(pdf_bytes)
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

"""
Main FastAPI application for the Research Claim Integrity Auditor.
"""
import asyncio
import json
import logging
from langfuse import observe, propagate_attributes
import os
import sys
import uuid
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Research Claim Integrity Auditor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory audit state (demo; not persistent across restarts)
_audits: dict[str, dict] = {}

# Stage event queues per audit_id
_event_queues: dict[str, asyncio.Queue] = {}


def _get_or_create_queue(audit_id: str) -> asyncio.Queue:
    if audit_id not in _event_queues:
        _event_queues[audit_id] = asyncio.Queue()
    return _event_queues[audit_id]


async def _push_event(audit_id: str, event: dict):
    q = _get_or_create_queue(audit_id)
    await q.put(event)


def _push_event_sync(audit_id: str, event: dict):
    """Push event from sync context using the running loop."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(_push_event(audit_id, event), loop)
        else:
            q = _get_or_create_queue(audit_id)
            q.put_nowait(event)
    except Exception as e:
        logger.debug("Event push error: %s", e)


@observe(name="audit_pipeline")
async def _run_audit_pipeline(audit_id: str, pdf_bytes: Optional[bytes], doi_or_link: Optional[str]):
    """Run the full audit pipeline, emitting SSE events."""
    from langfuse import get_client
    get_client().update_current_span(metadata={"audit_id": audit_id})
    audit = _audits[audit_id]

    async def emit(stage: str, status: str, data: dict = None):
        event = {"stage": stage, "status": status, "data": data or {}}
        await _push_event(audit_id, event)
        audit["stages"][stage] = {"status": status, "data": data or {}}

    try:
        # --- Resolve metadata if DOI/link provided ---
        pdf_url = None
        if doi_or_link and not pdf_bytes:
            await emit("resolve", "running")
            from resolver import resolve_doi, download_pdf
            meta = resolve_doi(doi_or_link)
            audit["metadata"] = meta
            pdf_url = meta.get("pdf_url")

            if pdf_url:
                await emit("resolve", "running", {"message": "Downloading open-access PDF..."})
                pdf_bytes = download_pdf(pdf_url)
                if pdf_bytes:
                    await emit("resolve", "done", {"pdf_url": pdf_url, "pdf_size": len(pdf_bytes)})
                else:
                    await emit("resolve", "done", {
                        "pdf_url": pdf_url,
                        "message": "PDF download failed; metadata-only audit."
                    })
            else:
                await emit("resolve", "done", {
                    "message": "No open-access PDF found. Running metadata-only audit.",
                    "needs_pdf_upload": True,
                })
                audit["needs_pdf_upload"] = True

        # --- Stage 1: Extract ---
        if pdf_bytes:
            await emit("extract", "running")
            from stages.extract import run as extract_run
            extract_result = extract_run(audit_id, pdf_bytes)
            raw_pages = extract_result.get("raw_pages", [])
            await emit("extract", "done", {"page_count": len(raw_pages)})
        else:
            raw_pages = []
            await emit("extract", "not checkable", {"reason": "No PDF available"})

        # --- Stage 2: Claims ---
        if raw_pages:
            await emit("claims", "running")
            from stages.claims import run as claims_run
            claims_result = claims_run(audit_id, raw_pages)
            claims = claims_result.get("outputs", {}).get("claims", [])
            paper_doi = claims_result.get("outputs", {}).get("paper_doi")
            cited_dois = claims_result.get("outputs", {}).get("cited_dois", [])
            code_data_urls = claims_result.get("outputs", {}).get("code_data_urls", [])
            apa_stats = claims_result.get("outputs", {}).get("apa_statistics", [])
            await emit("claims", "done", {"claim_count": len(claims)})
        else:
            claims, paper_doi, cited_dois, code_data_urls, apa_stats = [], None, [], [], []
            claims_result = {
                "stage": "claims", "outputs": {
                    "claims": [], "paper_doi": None,
                    "cited_dois": [], "code_data_urls": [], "apa_statistics": []
                }
            }
            await emit("claims", "not checkable", {"reason": "No PDF available"})

        # Override paper_doi from metadata if claims didn't find one
        if not paper_doi and audit.get("metadata", {}).get("doi"):
            paper_doi = audit["metadata"]["doi"]
            cited_dois = cited_dois or []

        # --- Stage 3: Retraction ---
        await emit("retraction", "running")
        from stages.retraction import run as retraction_run
        retraction_result = retraction_run(audit_id, paper_doi, cited_dois)
        await emit("retraction", "done", {
            "paper_verdict": retraction_result.get("outputs", {}).get("paper_verdict")
        })

        # --- Stage 4: Stats ---
        if apa_stats:
            await emit("stats", "running")
            from stages.stats import run as stats_run
            stats_result = stats_run(audit_id, apa_stats)
            await emit("stats", "done", {
                "stat_count": len(stats_result.get("outputs", {}).get("results", []))
            })
        else:
            stats_result = {"stage": "stats", "outputs": {"results": []}}
            await emit("stats", "not checkable", {"reason": "No APA statistics found"})
            from shared import write_stage_result
            write_stage_result(audit_id, "stats", stats_result)

        # --- Stage 5: Citations ---
        if claims:
            await emit("citations", "running")
            from stages.citations import run as citations_run
            citations_result = citations_run(audit_id, claims, cited_dois)
            await emit("citations", "done", {
                "checked": len(citations_result.get("outputs", {}).get("results", []))
            })
        else:
            citations_result = {"stage": "citations", "outputs": {"results": []}}
            await emit("citations", "not checkable", {"reason": "No claims extracted"})
            from shared import write_stage_result
            write_stage_result(audit_id, "citations", citations_result)

        # --- Stage 6: Code/data ---
        await emit("code_data", "running")
        from stages.code_data import run as code_data_run
        code_data_result = code_data_run(audit_id, code_data_urls)
        await emit("code_data", "done", {
            "verdict": code_data_result.get("outputs", {}).get("overall_verdict")
        })

        # --- Stage 7: Grade ---
        await emit("grade", "running")
        from stages.grade import run as grade_run
        grade_result = grade_run(
            audit_id,
            retraction_result,
            stats_result,
            citations_result,
            code_data_result,
            claims_result,
        )
        grade_val = grade_result.get("outputs", {}).get("grade")
        await emit("grade", "done", {"grade": grade_val})

        # Store full result
        audit["result"] = {
            "audit_id": audit_id,
            "metadata": audit.get("metadata", {}),
            "stages": {
                "extract": extract_result if raw_pages else {"not_checkable": True},
                "claims": claims_result,
                "retraction": retraction_result,
                "stats": stats_result,
                "citations": citations_result,
                "code_data": code_data_result,
                "grade": grade_result,
            },
            "grade": grade_val,
            "rule": grade_result.get("outputs", {}).get("rule"),
            "uncheckable_items": grade_result.get("outputs", {}).get("uncheckable_items", []),
            "footer": "Automated triage. Human review required.",
        }
        audit["status"] = "done"
        await _push_event(audit_id, {"stage": "done", "status": "done"})

        # Automatically generate HTML report for this run
        try:
            import subprocess
            subprocess.run([sys.executable, str(Path(__file__).parent / "report_generator.py")], check=True)
        except Exception as e:
            logger.error("Failed to generate HTML report: %s", e)

    except Exception as e:
        logger.exception("Audit pipeline error for %s", audit_id)
        audit["status"] = "error"
        audit["error"] = str(e)
        await _push_event(audit_id, {"stage": "error", "status": "error", "data": {"message": str(e)}})


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """Probe Gemini models at startup."""
    from llm import probe_and_select_model, has_keys
    if has_keys():
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, probe_and_select_model)
    else:
        logger.warning("No GEMINI_API_KEYS configured. LLM stages will return 'not checkable'.")


@app.post("/api/audit")
async def start_audit(
    doi_or_link: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    """Start a new audit. Accepts a DOI/URL or a PDF upload."""
    if not doi_or_link and not file:
        raise HTTPException(status_code=400, detail="Provide doi_or_link or upload a file.")

    audit_id = str(uuid.uuid4())
    pdf_bytes = None
    if file:
        pdf_bytes = await file.read()

    _audits[audit_id] = {
        "audit_id": audit_id,
        "status": "running",
        "doi_or_link": doi_or_link,
        "stages": {},
        "result": None,
        "needs_pdf_upload": False,
    }
    _get_or_create_queue(audit_id)

    asyncio.create_task(_run_audit_pipeline(audit_id, pdf_bytes, doi_or_link))
    return {"audit_id": audit_id}


@app.get("/api/audit/{audit_id}/events")
async def stream_events(audit_id: str):
    """Stream pipeline progress as Server-Sent Events."""
    if audit_id not in _audits:
        raise HTTPException(status_code=404, detail="Audit not found")

    q = _get_or_create_queue(audit_id)

    async def event_generator():
        while True:
            try:
                event = await asyncio.wait_for(q.get(), timeout=30.0)
                data = json.dumps(event)
                yield f"data: {data}\n\n"
                if event.get("stage") in ("done", "error"):
                    break
            except asyncio.TimeoutError:
                yield ": keepalive\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/audit/{audit_id}")
async def get_audit(audit_id: str):
    """Return the full audit result."""
    if audit_id not in _audits:
        raise HTTPException(status_code=404, detail="Audit not found")
    audit = _audits[audit_id]
    if audit["status"] == "running":
        return {"audit_id": audit_id, "status": "running"}
    return audit.get("result", {"audit_id": audit_id, "status": audit["status"]})


@app.post("/api/audit/{audit_id}/pdf")
async def upload_followup_pdf(audit_id: str, file: UploadFile = File(...)):
    """Accept a follow-up PDF upload when no OA PDF was found initially."""
    if audit_id not in _audits:
        raise HTTPException(status_code=404, detail="Audit not found")
    audit = _audits[audit_id]
    if not audit.get("needs_pdf_upload"):
        raise HTTPException(status_code=400, detail="This audit does not need a PDF upload.")

    pdf_bytes = await file.read()
    audit["needs_pdf_upload"] = False
    audit["status"] = "running"
    _get_or_create_queue(audit_id)

    doi_or_link = audit.get("doi_or_link")
    asyncio.create_task(_run_audit_pipeline(audit_id, pdf_bytes, doi_or_link))
    return {"audit_id": audit_id, "status": "running"}


@app.get("/api/health/llm")
async def health_llm():
    """Return LLM status — active model and key positions, never key values."""
    from llm import get_active_model, key_status, has_keys
    return {
        "active_model": get_active_model(),
        "keys_configured": has_keys(),
        "key_status": key_status(),
    }

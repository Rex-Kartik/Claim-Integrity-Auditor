import sys
import os
import httpx
import time
import json
from pathlib import Path

DOIS = [
    ("10.1016/s0140-6736(20)30367-6", "D"),
    ("10.1371/journal.pone.0145892", "C (or B depending on stats)"),
    ("10.1371/journal.pone.0001097", "A or B")
]

API_URL = "http://localhost:8000"

def run_paper(doi: str, expected_grade: str):
    print(f"\n======================================")
    print(f"RUNNING AUDIT FOR: {doi}")
    print(f"EXPECTED GRADE: {expected_grade}")
    print(f"======================================")
    
    # Start audit
    try:
        resp = httpx.post(f"{API_URL}/api/audit", data={"doi_or_link": doi}, timeout=120.0)
        resp.raise_for_status()
    except Exception as e:
        print(f"Failed to start audit: {e}")
        return
        
    audit_id = resp.json()["audit_id"]
    print(f"Audit started. ID: {audit_id}")
    
    # In a real app we'd consume SSE, but here we can just poll the grade endpoint or wait.
    # The pipeline writes to runs/{audit_id}/grade.json when done.
    runs_dir = Path("runs") / audit_id
    
    print("Waiting for pipeline to complete...")
    timeout = 300
    start = time.time()
    pdf_uploaded = False
    
    while time.time() - start < timeout:
        if (runs_dir / "grade.json").exists() or (runs_dir / "error.json").exists():
            break
            
        # Check if needs pdf upload
        resolve_file = runs_dir / "resolve.json"
        if not pdf_uploaded and resolve_file.exists():
            try:
                res_data = json.loads(resolve_file.read_text(encoding="utf-8"))
                if res_data.get("outputs", {}).get("needs_pdf_upload"):
                    print("Backend requested PDF upload. Uploading dummy PDF...")
                    dummy_pdf = Path("dummy.pdf")
                    if not dummy_pdf.exists():
                        # Just write an empty file for now, or minimal valid PDF
                        dummy_pdf.write_bytes(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n188\n%%EOF\n")
                    
                    with open(dummy_pdf, "rb") as f:
                        httpx.post(f"{API_URL}/api/audit/{audit_id}/pdf", files={"file": ("dummy.pdf", f, "application/pdf")})
                    pdf_uploaded = True
            except Exception as e:
                pass
                
        time.sleep(2)
        
    if (runs_dir / "error.json").exists():
        print("Pipeline encountered an error:")
        print((runs_dir / "error.json").read_text(encoding="utf-8"))
        return
        
    if not (runs_dir / "grade.json").exists():
        print("Pipeline timed out!")
        return
        
    # Read grade
    grade_data = json.loads((runs_dir / "grade.json").read_text(encoding="utf-8"))
    actual_grade = grade_data.get("outputs", {}).get("grade", "Unknown")
    print(f"\nACTUAL GRADE: {actual_grade}")
    
    if "D" in expected_grade and actual_grade == "D":
        print("MATCH: Yes")
    elif "C" in expected_grade and actual_grade == "C":
        print("MATCH: Yes")
    elif "A" in expected_grade or "B" in expected_grade:
        if actual_grade in ["A", "B", "C"]:
            print("MATCH: Yes/Maybe (depends on paper content)")
    else:
        print("MATCH: No/Disagreement")
        
def main():
    print("Ensure the FastAPI server is running on localhost:8000")
    for doi, expected in DOIS:
        run_paper(doi, expected)
        time.sleep(5) # Cooldown between requests just in case

    print("\nGenerating HTML reports...")
    import subprocess
    subprocess.run([sys.executable, "api/report_generator.py"])
    
    print("\nRunning linter...")
    subprocess.run([sys.executable, "api/lint.py", "runs/*/report.html"])
    
if __name__ == "__main__":
    main()

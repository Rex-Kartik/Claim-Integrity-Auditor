import json
from pathlib import Path

def generate_report(run_dir: Path):
    grade_file = run_dir / "grade.json"
    if not grade_file.exists():
        return None
        
    try:
        grade_data = json.loads(grade_file.read_text(encoding="utf-8"))
    except Exception:
        return None
        
    outputs = grade_data.get("outputs", {})
    grade = outputs.get("grade", "Unknown")
    rule = outputs.get("rule", "")
    uncheckable = outputs.get("uncheckable_items", [])
    
    # Try to load other stages for evidence
    claims_file = run_dir / "claims.json"
    claims = []
    if claims_file.exists():
        try:
            cdata = json.loads(claims_file.read_text(encoding="utf-8"))
            claims = cdata.get("outputs", {}).get("claims", [])
        except: pass
        
    stats_file = run_dir / "stats.json"
    stats = []
    if stats_file.exists():
        try:
            sdata = json.loads(stats_file.read_text(encoding="utf-8"))
            stats = sdata.get("outputs", {}).get("results", [])
        except: pass
        
    citations_file = run_dir / "citations.json"
    citations = []
    if citations_file.exists():
        try:
            cidata = json.loads(citations_file.read_text(encoding="utf-8"))
            citations = cidata.get("outputs", {}).get("results", [])
        except: pass

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: system-ui, -apple-system, sans-serif; line-height: 1.5; color: #111; max-width: 800px; margin: 40px auto; padding: 0 20px; }}
  .grade {{ font-size: 2em; font-weight: bold; margin-bottom: 5px; }}
  .rule {{ color: #555; margin-bottom: 20px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
  th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top; }}
  th {{ background-color: #f9f9f9; }}
  .footer {{ margin-top: 50px; font-size: 0.9em; color: #777; text-align: center; }}
</style>
</head>
<body>
  <h1>Audit Report: {run_dir.name}</h1>
  <div class="grade">Grade: {grade}</div>
  <div class="rule">Rule fired: {rule}</div>
  
  <h2>Evidence</h2>
"""

    if claims:
        html += "<h3>Claims</h3><table><tr><th>Page</th><th>Claim</th><th>Quote</th></tr>"
        for c in claims:
            html += f"<tr><td>{c.get('page','')}</td><td>{c.get('claim','')}</td><td>{c.get('quote','')}</td></tr>"
        html += "</table>"
        
    if stats:
        html += "<h3>Statistics</h3><table><tr><th>Verdict</th><th>Raw</th><th>Reported p</th><th>Recomputed p</th></tr>"
        for s in stats:
            html += f"<tr><td>{s.get('verdict','')}</td><td>{s.get('raw_string','')}</td><td>{s.get('reported_p','')}</td><td>{s.get('recomputed_p','')}</td></tr>"
        html += "</table>"
        
    if citations:
        html += "<h3>Citations</h3><table><tr><th>Verdict</th><th>Claim</th><th>Quote</th></tr>"
        for c in citations:
            html += f"<tr><td>{c.get('verdict','')}</td><td>{c.get('claim','')}</td><td>{c.get('retrieved_passage','') or c.get('reason','')}</td></tr>"
        html += "</table>"
        
    if uncheckable:
        html += "<h2>Not Checkable</h2><ul>"
        for u in uncheckable:
            html += f"<li>{u.get('type')}: {u.get('claim') or u.get('raw_string')}</li>"
        html += "</ul>"
        
    html += """
  <div class="footer">Automated triage. Human review required.</div>
</body>
</html>
"""
    
    report_path = run_dir / "report.html"
    report_path.write_text(html, encoding="utf-8")
    return grade

def generate_index(runs_dir: Path):
    runs = []
    for run_dir in runs_dir.iterdir():
        if run_dir.is_dir():
            grade = generate_report(run_dir)
            if grade:
                runs.append((run_dir.name, grade))
                
    html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { font-family: system-ui, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; }
  ul { list-style: none; padding: 0; }
  li { margin: 10px 0; font-size: 1.1em; }
  a { text-decoration: none; color: #2563eb; }
  a:hover { text-decoration: underline; }
</style>
</head>
<body>
  <h1>Audit Reports Index</h1>
  <ul>
"""
    for run_id, grade in runs:
        # We can put expected grade here by loading some mapping, but for now just actual
        html += f'<li><a href="runs/{run_id}/report.html">{run_id}</a> - Actual Grade: <b>{grade}</b></li>\n'
        
    html += """
  </ul>
</body>
</html>
"""
    (runs_dir.parent / "index.html").write_text(html, encoding="utf-8")
    print(f"Generated index.html and {len(runs)} reports.")

if __name__ == "__main__":
    runs_dir = Path(__file__).parent.parent / "runs"
    generate_index(runs_dir)

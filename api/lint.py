"""
Wording lint: fails if any forbidden word appears in report text.
Checks all stage JSON files in a run directory.
"""
import json
import sys
from pathlib import Path

FORBIDDEN = ["fraud", "fabricat", "misconduct", "cheat", "fake", "dishonest", "guilty"]


def lint_text(text: str, source: str) -> list[str]:
    """Return list of violations in text."""
    violations = []
    lower = text.lower()
    for word in FORBIDDEN:
        if word in lower:
            # Find context
            idx = lower.find(word)
            context = text[max(0, idx - 30) : idx + len(word) + 30]
            violations.append(f"  {source}: found '{word}' near: ...{context}...")
    return violations


def lint_json(data, source: str) -> list[str]:
    """Recursively lint all string values in a JSON structure."""
    violations = []
    if isinstance(data, dict):
        for k, v in data.items():
            violations.extend(lint_json(v, f"{source}.{k}"))
    elif isinstance(data, list):
        for i, v in enumerate(data):
            violations.extend(lint_json(v, f"{source}[{i}]"))
    elif isinstance(data, str):
        violations.extend(lint_text(data, source))
    return violations


def lint_run(run_id: str, runs_dir: Path) -> list[str]:
    """Lint all stage JSON and HTML files for a run."""
    run_path = runs_dir / run_id
    if not run_path.exists():
        return [f"Run directory not found: {run_path}"]

    violations = []
    # Check JSON
    for json_file in run_path.glob("*.json"):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            violations.extend(lint_json(data, str(json_file.name)))
        except Exception as e:
            violations.append(f"  Could not read {json_file.name}: {e}")
            
    # Check HTML
    for html_file in run_path.glob("*.html"):
        try:
            text = html_file.read_text(encoding="utf-8")
            violations.extend(lint_text(text, str(html_file.name)))
        except Exception as e:
            violations.append(f"  Could not read {html_file.name}: {e}")
            
    return violations

def lint_all(runs_dir: Path) -> dict[str, list[str]]:
    """Lint all runs."""
    results = {}
    for run_path in runs_dir.iterdir():
        if run_path.is_dir():
            results[run_path.name] = lint_run(run_path.name, runs_dir)
            
    # Check any HTML files in the root of runs_dir or direct arguments
    for html_file in runs_dir.glob("*.html"):
        try:
            text = html_file.read_text(encoding="utf-8")
            results[html_file.name] = lint_text(text, str(html_file.name))
        except Exception:
            pass
            
    return results

if __name__ == "__main__":
    import sys
    # Handle direct file arguments like `python lint.py runs/*/report.html`
    if len(sys.argv) > 1 and ("*" in sys.argv[1] or sys.argv[1].endswith(".html")):
        import glob
        failed = False
        for arg in sys.argv[1:]:
            for file_path in glob.glob(arg):
                path = Path(file_path)
                try:
                    text = path.read_text(encoding="utf-8")
                    violations = lint_text(text, str(path))
                    if violations:
                        print(f"LINT FAILED for {path}:")
                        for v in violations:
                            print(v)
                        failed = True
                    else:
                        print(f"LINT PASSED for {path}")
                except Exception as e:
                    print(f"Could not read {path}: {e}")
        sys.exit(1 if failed else 0)
    runs_dir = Path(__file__).parent.parent / "runs"
    if len(sys.argv) > 1:
        run_id = sys.argv[1]
        violations = lint_run(run_id, runs_dir)
        if violations:
            print(f"LINT FAILED for run {run_id}:")
            for v in violations:
                print(v)
            sys.exit(1)
        else:
            print(f"LINT PASSED for run {run_id}: no forbidden words found.")
            sys.exit(0)
    else:
        all_violations = lint_all(runs_dir)
        failed = False
        for run_id, violations in all_violations.items():
            if violations:
                print(f"LINT FAILED for run {run_id}:")
                for v in violations:
                    print(v)
                failed = True
            else:
                print(f"LINT PASSED: {run_id}")
        sys.exit(1 if failed else 0)

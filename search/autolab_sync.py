"""Pull official AutoLab climb results into the journal.

For each experiment in `autolab log`, save the signed report printed in its run
log to reports/autolab/<id>.json and record id, name, status and score in
search/notes.json under "autolab_runs". Then regenerate journal.html.

    python3 search/autolab_sync.py
"""
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV = dict(os.environ, COLUMNS="250", PATH=f"{Path.home()}/.local/bin:" + os.environ["PATH"])
CLI = ["autolab", "--url", "https://app.autolab.ai"]


def sh(*args):
    return subprocess.run(CLI + list(args), cwd=ROOT, env=ENV, capture_output=True, text=True).stdout


def report_from_logs(exp_id):
    text = sh("logs", exp_id)
    start = text.find('{\n  "hill"')
    if start < 0:
        return None
    depth = 0
    for i, ch in enumerate(text[start:], start):
        depth += ch == "{"
        depth -= ch == "}"
        if depth == 0:
            return json.loads(text[start : i + 1])
    return None


def main():
    rows = []
    for line in sh("log", "--limit", "200").splitlines():
        m = re.match(r"\s*(?:→\s*)?([0-9a-f]{8})\s+(\S+)\s+(\S+)\s+(?:triangles\s+(\d+)\s+)?(.*?)\s+(\d{4}-\d\d-\d\dT[\d:]+)\s*$", line)
        if m:
            rows.append({"id": m[1], "status": m[2], "commit": m[3], "title": m[5], "created": m[6]})
    notes_path = ROOT / "search" / "notes.json"
    notes = json.loads(notes_path.read_text())
    known = {r["id"]: r for r in notes.get("autolab_runs", [])}
    out_dir = ROOT / "reports" / "autolab"
    out_dir.mkdir(parents=True, exist_ok=True)
    for row in rows:
        old = known.get(row["id"], {})
        row.update({k: old[k] for k in ("what", "origin", "decision", "node") if k in old})
        path = out_dir / f"{row['id']}.json"
        if not path.exists() and row["status"] in ("merged", "discarded", "done", "failed", "analyzing", "crashed", "kept"):
            report = report_from_logs(row["id"])
            if report:
                path.write_text(json.dumps(report, indent=1) + "\n")
        if path.exists():
            report = json.loads(path.read_text())
            row["report"] = f"reports/autolab/{path.name}"
            row["passed"] = report["passed"]
            row["value"] = next((m["value"] for m in report["metrics"] if m["name"] == "triangles"), None)
            row["tree"] = report["tree_hash"][:8]
            row["sig"] = report["signature"][:26]
            row["git"] = report.get("submission_git")
    notes["autolab_runs"] = sorted(rows, key=lambda r: r["created"])
    notes_path.write_text(json.dumps(notes, indent=2) + "\n")
    subprocess.run(["python3", str(ROOT / "search" / "journal.py")], check=True)
    for r in notes["autolab_runs"]:
        print(r["id"], r["status"], r.get("value"), r["title"])


if __name__ == "__main__":
    main()

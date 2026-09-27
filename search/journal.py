"""Regenerate journal.html from reports/*.json plus hand-written notes in search/notes.json.

Only numbers read from signed reports appear in the results table and charts.
Dev numbers live in notes.json under "dev" and are rendered as unofficial.
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
NOTES = json.loads((ROOT / "search" / "notes.json").read_text())


def esc(text):
    return html.escape(str(text))


def load_reports():
    rows = []
    for path in sorted(REPORTS.glob("*.json")):
        report = json.loads(path.read_text())
        slug = path.stem
        note = NOTES["runs"].get(slug, {})
        value = next((m["value"] for m in report.get("metrics", []) if m["name"] == "triangles"), None)
        rows.append({
            "slug": slug,
            "file": f"reports/{path.name}",
            "n": report.get("params", {}).get("n"),
            "passed": report.get("passed"),
            "value": value,
            "final": report.get("final"),
            "git": report.get("submission_git"),
            "sub_hash": (report.get("submission_hash") or "")[:19],
            "sig": (report.get("signature") or "")[:26],
            "tree": (report.get("tree_hash") or "none")[:8],
            "time": report.get("timestamp", ""),
            "error": (report.get("details") or {}).get("error"),
            "what": note.get("what", ""),
            "origin": note.get("origin", ""),
            "decision": note.get("decision", ""),
        })
    return rows


def chart(rows, n):
    points = [r for r in rows if r["n"] == n and r["passed"] and r["value"] is not None]
    if not points:
        return f"<p class='muted'>n = {n}: no scored runs yet.</p>"
    record = NOTES["records"].get(str(n))
    top = max([p["value"] for p in points] + ([record["bound"]] if record else []))
    width, height, pad = 520, 180, 34
    step = (width - 2 * pad) / max(1, len(points) - 1)
    scale = lambda v: height - pad - (v / top) * (height - 2 * pad)
    parts = [f"<svg viewBox='0 0 {width} {height}' width='{width}' height='{height}' role='img'>"]
    parts.append(f"<line x1='{pad}' y1='{height - pad}' x2='{width - pad}' y2='{height - pad}' class='axis'/>")
    if record:
        for label, v, cls in (("best known", record["best"], "ref"), ("upper bound", record["bound"], "bound")):
            y = scale(v)
            parts.append(f"<line x1='{pad}' y1='{y:.1f}' x2='{width - pad}' y2='{y:.1f}' class='{cls}'/>")
            parts.append(f"<text x='{width - pad}' y='{y - 4:.1f}' text-anchor='end' class='lbl'>{label} {v}</text>")
    best, coords = 0, []
    for i, p in enumerate(points):
        best = max(best, p["value"])
        coords.append((pad + i * step, scale(best), p))
    parts.append("<polyline class='best' points='" + " ".join(f"{x:.1f},{y:.1f}" for x, y, _ in coords) + "'/>")
    for i, p in enumerate(points):
        x, y = pad + i * step, scale(p["value"])
        parts.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='3.5' class='dot'><title>{esc(p['slug'])}: {p['value']}</title></circle>")
        parts.append(f"<text x='{x:.1f}' y='{height - pad + 14}' text-anchor='middle' class='lbl'>{esc(p['slug'][:3])}</text>")
    parts.append(f"<text x='{pad}' y='14' class='lbl'>n = {n}: triangles per official run (dots), running best (line)</text>")
    parts.append("</svg>")
    return "".join(parts)


def main():
    rows = load_reports()
    status = NOTES["status"]
    groups = sorted({r["n"] for r in rows if r["n"] is not None} | {int(k) for k in NOTES["records"]})
    best_by_n = {}
    for r in rows:
        if r["passed"] and r["value"] is not None:
            best_by_n[r["n"]] = max(best_by_n.get(r["n"], 0), r["value"])
    summary = "".join(
        f"<tr><td>{n}</td><td>{best_by_n.get(n, '—')}</td><td>{NOTES['records'][str(n)]['best']}</td>"
        f"<td>{NOTES['records'][str(n)]['bound']}</td><td>{esc(NOTES['records'][str(n)]['note'])}</td></tr>"
        for n in groups if str(n) in NOTES["records"]
    )
    table = "".join(
        f"<tr class='{'fail' if not r['passed'] else ''}'><td><a href='{esc(r['file'])}'>{esc(r['slug'])}</a></td>"
        f"<td>{r['n']}</td><td class='num'>{r['value'] if r['passed'] else 'FAILED'}</td>"
        f"<td>{'yes' if r['final'] else ''}</td><td>{esc(r['origin'])}</td><td>{esc(r['what'])}"
        f"{'<br><span class=err>' + esc(r['error']) + '</span>' if r['error'] else ''}</td>"
        f"<td>{esc(r['decision'])}</td><td class='mono'>{esc(r['git'])}<br>{esc(r['sub_hash'])}<br>{esc(r['sig'])}…</td></tr>"
        for r in rows
    ) or "<tr><td colspan='8' class='muted'>No runs scored yet.</td></tr>"
    climb = NOTES.get("autolab_runs", [])
    climb_rows = "".join(
        f"<tr class='{'fail' if r.get('passed') is False else ''}'><td>{esc(r['id'])}</td><td>{esc(r['title'])}</td><td>{esc(r['status'])}</td>"
        f"<td class='num'>{r.get('value') if r.get('value') is not None else '—'}</td><td>{esc(r.get('origin', ''))}</td><td>{esc(r.get('what', ''))}</td>"
        f"<td>{esc(r.get('decision', ''))}</td>"
        f"<td class='mono'>{('<a href=' + chr(39) + esc(r['report']) + chr(39) + '>report</a> · ' + esc(r.get('tree', '')) + '<br>' + esc(r.get('sig', '')) + '…') if r.get('report') else ''}</td></tr>"
        for r in climb
    ) or "<tr><td colspan='8' class='muted'>No AutoLab runs yet.</td></tr>"
    climb_best = max((r["value"] for r in climb if r.get("passed") and r.get("value") is not None), default="—")
    ideas = "".join(
        f"<li><b>{esc(i['state'])}</b> — {esc(i['text'])}</li>" for i in NOTES["ideas"]
    )
    dev = "".join(f"<li>{esc(d)}</li>" for d in NOTES.get("dev", [])) or "<li class='muted'>none</li>"
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>kobon-triangles climb journal</title>
<style>
body {{ font: 14px/1.5 system-ui, sans-serif; max-width: 1100px; margin: 24px auto; padding: 0 16px; color: #1d1d1f; }}
h1 {{ font-size: 22px; margin-bottom: 4px; }} h2 {{ font-size: 17px; margin-top: 28px; border-bottom: 1px solid #ddd; }}
.status {{ display: flex; gap: 12px; flex-wrap: wrap; margin: 12px 0; }}
.tile {{ border: 1px solid #ccc; border-radius: 6px; padding: 8px 12px; min-width: 120px; }}
.tile b {{ display: block; font-size: 20px; }}
table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
td, th {{ border: 1px solid #ddd; padding: 4px 6px; vertical-align: top; text-align: left; }}
th {{ background: #f4f4f6; }} .num {{ text-align: right; font-weight: 600; }}
.mono {{ font-family: ui-monospace, monospace; font-size: 11px; color: #555; }}
.muted {{ color: #777; }} .fail {{ background: #fdecec; }} .err {{ color: #b00020; }}
.warn {{ border: 2px solid #c77700; background: #fff6e6; padding: 8px 12px; border-radius: 6px; }}
.unofficial {{ border: 1px dashed #999; background: #f7f7f7; padding: 6px 12px; }}
svg {{ background: #fafafa; border: 1px solid #e3e3e3; margin: 6px 12px 6px 0; }}
.axis {{ stroke: #999; }} .ref {{ stroke: #2a7; stroke-dasharray: 4 3; }} .bound {{ stroke: #c33; stroke-dasharray: 2 3; }}
.best {{ fill: none; stroke: #1f5fbf; stroke-width: 2; }} .dot {{ fill: #1f5fbf; }} .lbl {{ font-size: 10px; fill: #555; }}
</style></head><body>
<h1>Kobon triangles — climb journal</h1>
<div class="muted">Last updated {esc(status['updated'])} · hill kobon-triangles, local tree hash {esc(status['tree_hash'])}</div>
<div class="status">
  <div class="tile">Phase<b>{esc(status['phase'])}</b></div>
  <div class="tile">Loop<b>{esc(status['loop'])}</b></div>
  <div class="tile">Official runs<b>{len(rows)}</b></div>
  <div class="tile">Time budget<b>{esc(status['budget'])}</b></div>
</div>
<table><tr><th>n (lines)</th><th>best official score here</th><th>best known (literature)</th><th>upper bound</th><th>note</th></tr>{summary}</table>
<p><b>Now:</b> {esc(status['now'])}</p>

<h2>What is being measured</h2>
<p>{NOTES['measured']}</p>
<div class="warn">{NOTES['hill_warning']}</div>

<h2>Score over time</h2>
{''.join(chart(rows, n) for n in groups)}

<h2>AutoLab climb: official scores (hill 7d3f1d91, n = 18)</h2>
<p>Climb <b>srirangam-r/kobon-triangles-18</b>, scored by AutoLab against the official hill, so these results rank on the public leaderboard. Best so far: <b>{climb_best}</b>. The AutoLab agent's idea generation is off, so every run here was queued from Claude Code. Reports were copied from each run's log. They are signed with the node's key, so <code>hills verify</code> only succeeds on the machine that produced them.</p>
<table><tr><th>id</th><th>experiment</th><th>status</th><th>triangles</th><th>origin</th><th>what</th><th>decision</th><th>report · tree · signature</th></tr>{climb_rows}</table>

<h2>Every scored run (local hill 966e6945, unofficial)</h2>
<p class="muted">Each row links to its signed report. The last column shows the submission git ref, submission hash and signature prefix; check a report with <code>hills verify reports/&lt;file&gt;.json</code>. "Origin" says whether the arrangement came from my own search or was reproduced from published work.</p>
<table><tr><th>run</th><th>n</th><th>triangles</th><th>final</th><th>origin</th><th>what</th><th>decision</th><th>git · hash · signature</th></tr>{table}</table>

<h2>Ideas: running, queued, ruled out</h2>
<ul>{ideas}</ul>

<h2 class="unofficial">Unofficial dev numbers (not from the evaluator)</h2>
<ul class="unofficial">{dev}</ul>

<h2>Plan agreed with the user</h2>
<p>{NOTES['plan']}</p>
</body></html>
"""
    (ROOT / "journal.html").write_text(page)


if __name__ == "__main__":
    main()

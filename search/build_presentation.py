"""Refresh the data block of presentation.html: arrangement geometry (exact, from the certificates),
the claims ledger (work/loop/ledger.md) and the live k6z solver snapshot.

    python3 search/build_presentation.py
"""
import json
import os
import re
import sys
import time
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / ".autolab" / "hills" / "kobon-triangles"))
sys.path.insert(0, str(ROOT / "search"))
from eval import _intersection, _normalize, count_triangles  # noqa: E402
from structure import stats  # noqa: E402

PAGE = ROOT / "presentation.html"


def fl(p):
    x, y, w = p
    return float(Fraction(x, w)), float(Fraction(y, w))


def geometry(source, frame="core", zoom_pct=0.5, with_segments=False):
    raw = json.loads((ROOT / source).read_text())["lines"]
    lines = [_normalize(tuple(l)) for l in raw]
    n = len(lines)
    tris = count_triangles(lines)
    meets, on_line = {}, [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            p = _intersection(lines[i], lines[j])
            if p is not None:
                meets.setdefault(p, set()).update((i, j))
                on_line[i].add(p)
                on_line[j].add(p)
    triples = [fl(p) for p, ls in meets.items() if len(ls) >= 3]
    polys = [[fl(_intersection(lines[a], lines[b])) for a, b in ((i, j), (i, k), (j, k))] for i, j, k in tris]
    verts = [v for pl in polys for v in pl]
    if frame == "core":  # same framing as the thumbnail: dense core of triangle vertices plus every triple point
        cx0 = sorted(x for x, _ in verts)[len(verts) // 2]
        cy0 = sorted(y for _, y in verts)[len(verts) // 2]
        r = sorted(max(abs(x - cx0), abs(y - cy0)) for x, y in verts)[int(zoom_pct * (len(verts) - 1))]
        box = [(x, y) for x, y in verts if max(abs(x - cx0), abs(y - cy0)) <= r] + triples
    else:  # every triangle
        box = verts + triples
    x0, x1 = min(x for x, _ in box), max(x for x, _ in box)
    y0, y1 = min(y for _, y in box), max(y for _, y in box)
    half = max(x1 - x0, y1 - y0) / 2 * 1.08
    out = {
        "view": [round((x0 + x1) / 2, 5), round(-(y0 + y1) / 2, 5), round(half, 5)],  # y flipped for SVG
        "lines": [],
        "tris": [[[round(x, 5), round(-y, 5)] for x, y in pl] for pl in polys],
        "triples": [[round(x, 5), round(-y, 5)] for x, y in triples],
        "stats": {k: v for k, v in stats(raw).items() if k in ("n", "T", "segments", "Z", "D")} | {"t": len(triples)},
    }
    for a, b, c in lines:  # a x + b y + c = 0, scaled; SVG y = -y, so a x - b Y + c = 0
        s = max(abs(a), abs(b))
        out["lines"].append([a / s, -b / s, c / s])
    if with_segments:  # bounded segments with their use count (0 = unused, 2 = side of two triangles)
        use = {}
        for i, j, k in tris:
            for a, b, c in ((i, j, k), (j, i, k), (k, i, j)):  # the triangle's side on line a
                key = (a, frozenset((_intersection(lines[a], lines[b]), _intersection(lines[a], lines[c]))))
                use[key] = use.get(key, 0) + 1
        segs = []
        for a in range(n):
            axis = 0 if lines[a][1] else 1
            pts = sorted(on_line[a], key=lambda p: Fraction(p[axis], p[2]))
            for p, q in zip(pts, pts[1:]):
                (px, py), (qx, qy) = fl(p), fl(q)
                segs.append([round(px, 5), round(-py, 5), round(qx, 5), round(-qy, 5), use.get((a, frozenset((p, q))), 0)])
        out["segs"] = segs
    return out


def ledger():
    rows = []
    for line in (ROOT / "work/loop/ledger.md").read_text().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 5 and re.fullmatch(r"C\d+", cells[0]):
            rows.append({"id": cells[0], "claim": cells[1], "status": cells[3], "tag": cells[4]})
    return rows


def k6z():
    log = ROOT / "work/k6z/prove/results.jsonl"
    rs = [json.loads(l) for l in log.read_text().splitlines()] if log.exists() else []
    by_depth = {}
    for r in rs:
        d = by_depth.setdefault(len(r["prefix"]), {"UNSAT": 0, "timeout": 0, "SAT": 0})
        d[r["verdict"]] += 1
    # fraction of the line-0 order space closed: a depth-d cube covers 1/(17*16*...*(17-d+1)) of it
    closed = 0.0
    for r in rs:
        if r["verdict"] == "UNSAT":
            w = 1.0
            for i in range(len(r["prefix"])):
                w /= 17 - i
            closed += w
    running = False  # a python process whose own argv is "... prove.py work/k6z/k6z.cnf ..."
    for d in filter(str.isdigit, os.listdir("/proc")):
        try:
            argv = open(f"/proc/{d}/cmdline", "rb").read().decode(errors="ignore").split("\0")
        except OSError:
            continue
        if "python" in argv[0] and any(x.endswith("prove.py") for x in argv) and "work/k6z/k6z.cnf" in argv:
            running = True
    return {"running": running, "results": len(rs), "by_depth": {str(k): v for k, v in sorted(by_depth.items())},
            "closed_fraction": round(closed, 5), "elapsed_s": max((r["t"] for r in rs), default=0),
            "sat": sum(r["verdict"] == "SAT" for r in rs)}


def main():
    data = {
        "built": time.strftime("%Y-%m-%d %H:%M %Z"),
        "gallery": geometry("submissions/005-gallery-n18/solution.json", "core", 0.5),
        "own": geometry("submissions/007-anneal-n18/solution.json", "core", 0.7),
        "eight": geometry("work/certs/8-1yvz24guzamh9/solution.json", "all", with_segments=True),
        "ledger": ledger(),
        "k6z": k6z(),
    }
    page = PAGE.read_text()
    blob = json.dumps(data, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    page, n = re.subn(r'(<script id="data" type="application/json">).*?(</script>)',
                      lambda m: m.group(1) + blob + m.group(2), page, count=1, flags=re.S)
    assert n == 1, "data block not found"
    PAGE.write_text(page)
    k = data["k6z"]
    print(f"wrote {PAGE.name}: {len(blob) // 1024} KB data, {len(data['ledger'])} ledger rows, "
          f"k6z {k['results']} cubes, {100 * k['closed_fraction']:.1f}% closed")


if __name__ == "__main__":
    main()

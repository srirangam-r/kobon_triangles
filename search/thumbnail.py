"""Render the project thumbnail: the 18-line, 93-triangle arrangement (gallery certificate with
3 triple crossings), triangles shaded, triple crossings marked, title on the left.

    python3 search/thumbnail.py [out.png] [solution.json] [zoom_pct]
"""
import json
import sys
from fractions import Fraction
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / ".autolab" / "hills" / "kobon-triangles"))
sys.path.insert(0, str(ROOT / "search"))
from eval import _intersection, _normalize, count_triangles  # noqa: E402

SURFACE, INK, INK2, MUTED = "#1a1a19", "#ffffff", "#c3c2b7", "#6b6a63"
TRI, TRIPLE = "#3987e5", "#d95926"  # validated dark categorical slots 1-2


def point(p):
    x, y, w = p
    return float(Fraction(x, w)), float(Fraction(y, w))


def main(out, source="submissions/005-gallery-n18/solution.json", zoom_pct=0.5):
    lines = [_normalize(tuple(l)) for l in json.loads((ROOT / source).read_text())["lines"]]
    tris = count_triangles(lines)
    polys = []
    for i, j, k in tris:
        polys.append([point(_intersection(lines[a], lines[b])) for a, b in ((i, j), (i, k), (j, k))])
    meets = {}
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            p = _intersection(lines[i], lines[j])
            if p is not None:
                meets.setdefault(p, set()).update((i, j))
    triples = [point(p) for p, ls in meets.items() if len(ls) >= 3]
    # frame the dense core of triangle vertices plus every triple crossing (outer triangles may run off)
    verts = [v for pl in polys for v in pl]
    cx0 = sorted(x for x, _ in verts)[len(verts) // 2]
    cy0 = sorted(y for _, y in verts)[len(verts) // 2]
    r = sorted(max(abs(x - cx0), abs(y - cy0)) for x, y in verts)[int(zoom_pct * (len(verts) - 1))]
    core = [(x, y) for x, y in verts if max(abs(x - cx0), abs(y - cy0)) <= r] + triples
    x0, x1 = min(x for x, _ in core), max(x for x, _ in core)
    y0, y1 = min(y for _, y in core), max(y for _, y in core)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    half = max(x1 - x0, y1 - y0) / 2 * 1.08
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.add_axes([0.40, 0.02, 0.58, 0.96])
    ax.set_facecolor(SURFACE)
    ax.set_xlim(cx - half * 1.0, cx + half * 1.0)
    ax.set_ylim(cy - half * 0.97, cy + half * 0.97)
    ax.set_aspect("equal")
    ax.axis("off")
    # lines, clipped by the axes
    big = half * 50
    for a, b, c in lines:
        if abs(b) > abs(a):
            x0, x1 = cx - big, cx + big
            ax.plot([x0, x1], [(-c - a * x0) / b, (-c - a * x1) / b], color=INK2, lw=0.9, alpha=0.55, zorder=1)
        else:
            y0, y1 = cy - big, cy + big
            ax.plot([(-c - b * y0) / a, (-c - b * y1) / a], [y0, y1], color=INK2, lw=0.9, alpha=0.55, zorder=1)
    for poly in polys:  # triangles with a thin surface-coloured gap between neighbours
        ax.add_patch(Polygon(poly, closed=True, facecolor=TRI, edgecolor=SURFACE, lw=1.2, alpha=0.9, zorder=2))
    for x, y in triples:  # triple crossings: marker with a surface ring
        ax.scatter([x], [y], s=150, color=TRIPLE, edgecolor=SURFACE, linewidth=2.2, zorder=4)

    fig.text(0.045, 0.80, "Shrinking the", color=INK, fontsize=34, fontweight="bold", family="DejaVu Sans")
    fig.text(0.045, 0.705, "Kobon Gap", color=INK, fontsize=34, fontweight="bold", family="DejaVu Sans")
    fig.text(0.045, 0.62, "Can 18 lines make 94 triangles?", color=INK2, fontsize=17)
    fig.text(0.045, 0.565, "Theorems + SAT solver + AI referees", color=INK2, fontsize=17)
    # legend (two series: both named in text next to their mark)
    lx, ly = 0.047, 0.40
    fig.patches.append(matplotlib.patches.Rectangle((lx, ly), 0.018, 0.032, transform=fig.transFigure,
                                                    facecolor=TRI, edgecolor="none", figure=fig))
    fig.text(lx + 0.028, ly + 0.004, f"{len(tris)} triangles (best known)", color=INK2, fontsize=14)
    fig.lines.append(matplotlib.lines.Line2D([lx + 0.009], [ly - 0.055], marker="o", markersize=11, color=TRIPLE,
                                             markeredgecolor=SURFACE, transform=fig.transFigure, figure=fig))
    fig.text(lx + 0.028, ly - 0.066, f"{len(triples)} triple crossings", color=INK2, fontsize=14)
    fig.text(0.045, 0.10, "No 94 with ≤ 3 triple crossings", color=MUTED, fontsize=12.5)
    fig.text(0.045, 0.065, "or in general position (AI-refereed)", color=MUTED, fontsize=12.5)
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}: {len(tris)} triangles, {len(triples)} triple points, view half-width {half:.3g}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "assets" / "thumbnail.png")
    src = sys.argv[2] if len(sys.argv) > 2 else "submissions/005-gallery-n18/solution.json"
    pct = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
    main(out, src, pct)

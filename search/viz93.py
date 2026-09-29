"""Render an 18-line solution with its triangles, triple points and bridges (segments between two triple points that
border a triangle on both sides). Left: overview; right: zoom on the triple-point cluster.

    python search/viz93.py <solution.json> <out.png> [title]
"""
import json
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon, Rectangle

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / ".autolab" / "hills" / "kobon-triangles"))
from eval import _intersection, _normalize, count_triangles  # noqa: E402

SURFACE, INK, INK2, MUTED = "#1a1a19", "#ffffff", "#c3c2b7", "#6b6a63"
TRI, TRIPLE = "#3987e5", "#d95926"  # validated dark categorical slots 1-2 (same as the thumbnail)


def fpt(p):
    x, y, w = p
    return float(Fraction(x, w)), float(Fraction(y, w))


def structure(lines):
    tris = count_triangles(lines)
    meets = defaultdict(set)
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            p = _intersection(lines[i], lines[j])
            if p is not None:
                meets[p].update((i, j))
    triple = {p for p, ls in meets.items() if len(ls) >= 3}
    side_use = defaultdict(int)  # (line, P, Q) segment sides used by triangles
    polys = []
    for i, j, k in tris:
        vs = {(a, b): _intersection(lines[a], lines[b]) for a, b in ((i, j), (i, k), (j, k))}
        polys.append([fpt(v) for v in vs.values()])
        for L, (P, Q) in ((i, (vs[(i, j)], vs[(i, k)])), (j, (vs[(i, j)], vs[(j, k)])), (k, (vs[(i, k)], vs[(j, k)]))):
            side_use[(L,) + tuple(sorted((P, Q)))] += 1
    bridges = [(fpt(P), fpt(Q)) for (L, P, Q), c in side_use.items() if c == 2 and P in triple and Q in triple]
    return tris, polys, [fpt(p) for p in triple], bridges


def draw(ax, lines, polys, triples, bridges, cx, cy, half, ms):
    ax.set_facecolor(SURFACE)
    ax.set_xlim(cx - half, cx + half)
    ax.set_ylim(cy - half, cy + half)
    ax.set_aspect("equal")
    ax.axis("off")
    big = half * 60
    for a, b, c in lines:
        a, b, c = float(a), float(b), float(c)
        if abs(b) > abs(a):
            x0, x1 = cx - big, cx + big
            ax.plot([x0, x1], [(-c - a * x0) / b, (-c - a * x1) / b], color=INK2, lw=0.8, alpha=0.5, zorder=1)
        else:
            y0, y1 = cy - big, cy + big
            ax.plot([(-c - b * y0) / a, (-c - b * y1) / a], [y0, y1], color=INK2, lw=0.8, alpha=0.5, zorder=1)
    for poly in polys:
        ax.add_patch(Polygon(poly, closed=True, facecolor=TRI, edgecolor=SURFACE, lw=1.0, alpha=0.9, zorder=2))
    for (x0, y0), (x1, y1) in bridges:
        ax.plot([x0, x1], [y0, y1], color=TRIPLE, lw=3.2, solid_capstyle="round", zorder=3)
    for x, y in triples:
        ax.scatter([x], [y], s=ms, color=TRIPLE, edgecolor=SURFACE, linewidth=2.0, zorder=4)


def frame(pts, pad=1.12):
    x0, x1 = min(x for x, _ in pts), max(x for x, _ in pts)
    y0, y1 = min(y for _, y in pts), max(y for _, y in pts)
    return (x0 + x1) / 2, (y0 + y1) / 2, max(x1 - x0, y1 - y0) / 2 * pad


def main():
    src, out = sys.argv[1], sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else "A new 93"
    lines = [_normalize(tuple(l)) for l in json.load(open(src))["lines"]]
    tris, polys, triples, bridges = structure(lines)
    verts = [v for pl in polys for v in pl]
    xs, ys = sorted(x for x, _ in verts), sorted(y for _, y in verts)
    cx0, cy0 = xs[len(xs) // 2], ys[len(ys) // 2]
    r = sorted(max(abs(x - cx0), abs(y - cy0)) for x, y in verts)[int(0.6 * (len(verts) - 1))]
    core = [(x, y) for x, y in verts if max(abs(x - cx0), abs(y - cy0)) <= r] + triples
    fig = plt.figure(figsize=(14, 7.6), dpi=110)
    fig.patch.set_facecolor(SURFACE)
    axL = fig.add_axes([0.02, 0.05, 0.46, 0.80])
    axR = fig.add_axes([0.52, 0.05, 0.46, 0.80])
    draw(axL, lines, polys, triples, bridges, *frame(core), ms=70)
    cl = triples + [p for b in bridges for p in b]
    cx, cy, h = frame(cl, pad=1.35)
    draw(axR, lines, polys, triples, bridges, cx, cy, h, ms=140)
    L = axL.get_xlim(), axL.get_ylim()
    if h < (L[0][1] - L[0][0]) / 2:  # show the zoom window on the overview
        axL.add_patch(Rectangle((cx - h, cy - h), 2 * h, 2 * h, fill=False, edgecolor=INK, lw=1.0, ls="--", zorder=5))
    fig.text(0.02, 0.93, f"{title}: 18 lines, {len(tris)} triangles", color=INK, fontsize=22, fontweight="bold")
    fig.text(0.02, 0.885, f"{len(triples)} triple points, {len(bridges)} bridges (segments between two triple points with a "
             f"triangle on both sides); integer lines, exact count by the hill's evaluator", color=INK2, fontsize=12.5)
    fig.text(0.02, 0.02, "overview", color=MUTED, fontsize=11)
    fig.text(0.52, 0.02, "zoom: triple-point cluster", color=MUTED, fontsize=11)
    handles = [Rectangle((0, 0), 1, 1, facecolor=TRI, edgecolor="none"),
               Line2D([0], [0], marker="o", color="none", markerfacecolor=TRIPLE, markeredgecolor=SURFACE, markersize=10),
               Line2D([0], [0], color=TRIPLE, lw=3.2)]
    leg = fig.legend(handles, [f"triangles ({len(tris)})", f"triple points ({len(triples)})", f"bridges ({len(bridges)})"],
                     loc="upper right", bbox_to_anchor=(0.985, 0.975), frameon=False, fontsize=12, labelcolor=INK2, ncol=3)
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}: {len(tris)} triangles, {len(triples)} triple points, {len(bridges)} bridges")


if __name__ == "__main__":
    main()

# Paper figure: the two published 93s, triangles from the exact certificates (arrangements/*/triangles.json).
import json, sys
from fractions import Fraction
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

def load(name):
    d = json.load(open(f"arrangements/{name}/triangles.json"))
    tris = d["triangles"] if "triangles" in d else d
    out = []
    for t in tris:
        vs = t["vertices"] if isinstance(t, dict) else t[1]
        out.append([(float(Fraction(x)), float(Fraction(y))) for x, y in vs])
    lines = json.load(open(f"arrangements/{name}/solution.json"))["lines"]
    return out, lines

def panel(ax, name, title, q=0.10):
    tris, lines = load(name)
    cx = sorted(sum(p[0] for p in t) / 3 for t in tris); cy = sorted(sum(p[1] for p in t) / 3 for t in tris)
    k = int(q * len(cx)); x0, x1, y0, y1 = cx[k], cx[-1 - k], cy[k], cy[-1 - k]
    w = max(x1 - x0, y1 - y0) * 0.65; mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    ax.set_xlim(mx - w, mx + w); ax.set_ylim(my - w, my + w)
    for t in tris:
        ax.add_patch(Polygon(t, closed=True, facecolor="#7fb2d9", edgecolor="none", alpha=0.85))
    import numpy as np
    xs = np.array([mx - 3 * w, mx + 3 * w])
    for a, b, c in lines:
        if b != 0:
            ax.plot(xs, (-a * xs - c) / b, color="#444444", lw=0.6)
        else:
            ax.axvline(-c / a, color="#444444", lw=0.6)
    ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([]); ax.set_title(title, fontsize=14)

fig, axs = plt.subplots(1, 2, figsize=(10, 5))
panel(axs[0], "n18_T93_anneal_official", "official 93: annealing, no multiple points")
panel(axs[1], "n18_T93_gallery", "gallery 93 (Utkin–Parpalak): 3 triple points")
plt.tight_layout(); plt.savefig("paper/figures/two93.pdf"); plt.savefig("paper/figures/two93.png", dpi=150)
print("ok")

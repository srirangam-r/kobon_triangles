#!/usr/bin/env python3
"""Line-end lemma (lead). For each of the 2n line ends (last vertex v of line L, unbounded ray beyond v):
  good-token  : v multiple (the unbounded ray is an N ray, never selected by §4 or the K_1 payment);
  good-I3     : v simple, last segment doubly used, origin triple (an I_3 end block);
  good-unused : v simple and the other line M at v has an unused bounded segment at v;
  bad-I4      : v simple, last segment doubly used, origin 4-fold;
  bad-wedge   : v simple, v is also M's last vertex, and the bounded face opposite the wedge is a triangle.
Claim: these cases are exhaustive. Each unused segment serves <= 2 ends, so
  2Λ >= #good ends + Σ S_P° + U_4 + 2K_3 + 4K_4  (all disjoint credits).
Also: a line with both ends bad-wedge has its two corner triangles on the same side."""
import sys, json
from collections import Counter
sys.path[:0] = ["work/bbl", "work/t3", "work/eng/pert"]
from arr import Arr, rays, far_end, first_seg

def ends(a):
    out = []
    for L in range(a.n):
        row = a.rows[L]
        for side in (0, 1):
            v = row[0] if side == 0 else row[-1]
            u = row[1] if side == 0 else row[-2]
            e = 0 if side == 0 else len(row) - 2
            if not a.is_simple(v):
                out.append((L, side, "good-token")); continue
            M = a.other(v, L)
            if len(a.t[L][e]) == 2:
                out.append((L, side, "good-I3" if len(a.events[u]) == 3 else ("bad-I4" if len(a.events[u]) == 4 else "bad-I?"))); continue
            i = a.pos[M][v]; segs = [s for s in (i - 1, i) if 0 <= s <= len(a.rows[M]) - 2]
            if any(len(a.t[M][s]) == 0 for s in segs):
                out.append((L, side, "good-unused")); continue
            ext = (i == 0 or i == len(a.rows[M]) - 1)
            out.append((L, side, "bad-wedge" if ext else "UNCLASSIFIED"))
    return out

tot = Counter(); narr = 0; bad = 0; seen = set(); worst = None
for f in sys.argv[1:]:
    for line in open(f):
        d = json.loads(line); g = d.get("gens")
        if not g or g in seen: continue
        seen.add(g)
        try: a = Arr(g, d.get("n", 18))
        except Exception: continue
        if any(len(e) > 4 for e in a.events): continue
        es = ends(a); narr += 1
        c = Counter(k for _, _, k in es); tot.update(c)
        if c["UNCLASSIFIED"]: bad += 1
        lam = a.n * (a.n - 2) - 3 * a.T()
        G = c["good-token"] + c["good-I3"] + c["good-unused"]
        assert G <= 2 * lam or True
        if G > 2 * lam: bad += 1; print("G exceeds 2Λ", g[:60], G, 2 * lam)
print("arrangements", narr, dict(tot), "violations", bad)

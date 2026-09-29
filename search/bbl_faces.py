"""Planarity accounting for bridged units. The bridge graph (triple points, bridges) is a plane graph; its rotation
system comes from the ray order at each point (arr.rays). For a connected component C with |C| >= 3:
  beta_C = 3|C| - 6 - sum_f (deg_f - 3)      (Euler; the sum is over all faces incl. the outer one)
Conservative unit slack = 6|K| - 3B - 2beta + nb - PC + U + Upc. Plugging Euler in per component, the unit lemma for
bridged units reads   3B + PC - U - Upc - nb  <=  sum_C const_C + 2 * sum_f (deg_f - 3),
const = 12 for |C| >= 3, 10 for |C| = 2, 6 for |C| = 1. This tool attributes every block to the bridge-graph face its
ray points into and prints per-face (deg, #blocks, inner/outer) statistics and the tightest faces.
    python search/bbl_faces.py <in>...
"""
import collections, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search")); sys.path.append(str(ROOT / "work/t3"))
from arr import Arr, rays, far_end
from cluster import records
from bbl_rules import Charge
from bbl_point import costs


def faces(ch):
    a, trip = ch.a, ch.trip
    rot = {}                      # P -> list of (ray index, neighbour or None, status)
    for P in a.triples:
        rs = rays(a, P)
        lst = []
        for i, r in enumerate(rs):
            nb = far_end(a, P, r) if ch.st[P][i] == "R" else None
            lst.append((i, nb, ch.st[P][i]))
        rot[P] = lst
    # darts P->Q along bridges; next dart around face: at Q, take the next bridge ray after the reverse dart (ccw)
    darts = {}
    for P, lst in rot.items():
        for i, nb, s in lst:
            if s == "R":
                darts[(P, i)] = nb
    def ray_to(Q, P):
        for i, nb, s in rot[Q]:
            if s == "R" and nb == P:
                return i
    out = []
    used = set()
    for d0 in darts:
        if d0 in used:
            continue
        face = []
        blocks = 0
        corners = []
        d = d0
        while d not in used:
            used.add(d)
            P, i = d
            Q = darts[d]
            face.append(P)
            j = ray_to(Q, P)
            # scan rays of Q after j (cyclic) until next bridge; count blocks passed (they point into this face)
            k = (j + 1) % 6
            a_c, b_c, seq = 1, 0, ""
            while rot[Q][k][2] != "R":
                seq += rot[Q][k][2]
                if rot[Q][k][2] == "B":
                    blocks += 1
                    b_c += 1
                k = (k + 1) % 6
                a_c += 1
            corners.append((a_c, b_c, seq))
            d = (Q, k)
        kappa = sum(c[0] for c in corners) - 3 * len(corners) + 6
        out.append((len(face), blocks, face, corners, kappa))
    return out


def main():
    stat = collections.Counter()
    worst = collections.Counter()
    corner_stat = collections.Counter()
    for inp in sys.argv[1:]:
        seen = set()
        for r in records(inp):
            g = r["gens"] if isinstance(r["gens"], str) else " ".join(r["gens"])
            if g in seen: continue
            seen.add(g)
            try: ch = Charge(Arr(g, r.get("n")))
            except ValueError: continue
            fs = faces(ch)
            for deg, bl, face, corners, kappa in fs:
                inner = kappa != 12
                stat[("inner" if inner else "outer", min(deg, 12), min(bl, 12), kappa if inner else 12)] += 1
                worst[(deg, bl, 3 * bl - 2 * (deg - 3))] += 1
                if not inner:
                    for c in corners:
                        corner_stat[c] += 1
    print("faces (deg, blocks inside):")
    for k in sorted(stat): print("  ", k, stat[k])
    print("outer-face corners (a_c sectors, blocks, interior ray statuses):")
    for k, v in corner_stat.most_common(25): print("  ", k, v)
    print("largest 3*blocks - 2*(deg-3) per face:")
    for k, v in sorted(worst.items(), key=lambda kv: -kv[0][2])[:15]: print("  deg %d blocks %d excess %d : %d" % (k + (v,)))


if __name__ == "__main__":
    main()

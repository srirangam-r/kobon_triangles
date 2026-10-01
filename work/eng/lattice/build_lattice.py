# Square grid (H: y=j, V: x=i) + one diagonal family A: x+y=k (combinatorially a triangular lattice) + a few
# lines D: y=x+c through lattice points (all-8 4-fold points adjacent to full triple points).
# Projective tweak removes parallels; far multiple points (old parallel classes) and non-bad 4-fold points are
# split into simple crossings so the result lies in the THEORY section 24 class.
import sys, json, itertools
from fractions import Fraction as F
sys.path.insert(0, "/home/nail/stuff/sundai_math/work/t3"); sys.path.insert(0, "/home/nail/stuff/sundai_math/work/eng/comp")
sys.path.insert(0, ".")
from lines2gens import transform, to_gens
from arr import Arr, rays, far_end
from bad_comp import tri_sectors, canon, BAD

def simple_word(g, m):
    # bubble-sort reversal of m consecutive tracks starting at g (all crossings simple)
    toks = []
    perm = list(range(m))
    for i in range(m):
        for j in range(m - 1 - i):
            toks.append(str(g + j))
    return toks

def clean(gens):
    toks = gens.split(); changed = True
    while changed:
        changed = False
        a = Arr(" ".join(toks))
        for idx, t in enumerate(toks):
            m = 2 + t.count("*")
            if m >= 5 or (m == 4 and canon(tri_sectors(a, idx)) not in BAD):
                toks = toks[:idx] + simple_word(int(t.rstrip("*")), m) + toks[idx+1:]
                changed = True; break
    return " ".join(toks)

def build(H, V, A, D, e1=F(1, 97), e2=F(1, 89)):
    L = [(0, 1, -j) for j in H] + [(1, 0, -i) for i in V] + [(1, 1, -k) for k in A] + [(1, -1, c) for c in D]
    g, mults = to_gens(transform(L, e1, e2))
    return clean(g), len(L)

def cluster_stats(gens):
    a = Arr(gens); c8 = 0; adj = 0; full3 = 0
    for P, ev in enumerate(a.events):
        if len(ev) == 4 and canon(tri_sectors(a, P)) == "11111111":
            c8 += 1
            for r in rays(a, P):
                Q = far_end(a, P, r)
                if Q is not None and len(a.events[Q]) == 3 and sum(tri_sectors(a, Q)) == 6: adj += 1
    mult = {}
    for ev in a.events: mult[len(ev)] = mult.get(len(ev), 0) + 1
    return a.T(), c8, adj, mult

if __name__ == "__main__":
    out = []
    for H, V, A, D in [((1, 2, 3, 4, 5), (1, 2, 3, 4, 5), (4, 5, 6, 7, 8), (-1, 0, 1)),
                       ((1, 2, 3, 4), (1, 2, 3, 4, 5), (3, 4, 5, 6, 7, 8), (-1, 0, 1)),
                       ((1, 2, 3, 4, 5), (1, 2, 3, 4, 5), (3, 4, 5, 6, 7, 8), (0, 1)),
                       ((1, 2, 3, 4, 5, 6), (1, 2, 3, 4, 5), (4, 5, 6, 7, 8), (0, 1)),
                       ((1, 2, 3, 4, 5), (1, 2, 3, 4, 5), (4, 5, 6, 7), (-1, 0, 1, 2)),
                       ((1, 2, 3, 4), (1, 2, 3, 4), (3, 4, 5, 6, 7), (-2, -1, 0, 1, 2))]:
        g, n = build(H, V, A, D)
        T, c8, adj, mult = cluster_stats(g)
        print(f"n={n} H{len(H)} V{len(V)} A{len(A)} D{len(D)}: T={T} all8={c8} all8-fulltriple adjacencies={adj} mult={mult}")
        out.append({"n": n, "gens": g, "src": f"lattice H{H} V{V} A{A} D{D}"})
    with open("lattice18.jsonl", "w") as f:
        for o in out: f.write(json.dumps(o) + "\n")

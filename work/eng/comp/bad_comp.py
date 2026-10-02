import sys, json
from collections import Counter, defaultdict
_R = __import__("pathlib").Path(__file__).resolve().parents[3].as_posix()
sys.path.insert(0, _R + "/work/t3"); sys.path.insert(0, _R + "/work/eng/comp")
from arr import Arr, rays, first_seg
from comp_cost import analyse

def tri_sectors(a, P):
    rs = rays(a, P); m2 = len(rs)
    fs = {first_seg(a, P, r): k for k, r in enumerate(rs) if first_seg(a, P, r) is not None}
    bits = [0]*m2
    for f in a.tris:
        ks = [fs[(x, e)] for (x, e, side) in f if (x, e) in fs]
        # a triangle with apex P has exactly two edges that are first segments at P, adjacent rays
        for i in range(len(ks)):
            for j in range(i+1, len(ks)):
                p, q = ks[i], ks[j]
                if (q - p) % m2 == 1: bits[p] = 1
                elif (p - q) % m2 == 1: bits[q] = 1
    return bits

def canon(bits):
    n = len(bits); best = None
    for r in range(n):
        for refl in (1, -1):
            t = tuple(bits[(r + refl*s) % n] for s in range(n))
            best = t if best is None or t > best else best
    return "".join(map(str, best))

BAD = {"11111111", "11111110", "11101110"}
if __name__ == "__main__":
    pat = Counter(); badcomp = Counter(); ex = []
    for f in sys.argv[1:]:
        for line in open(f):
            d = json.loads(line)
            a = Arr(d["gens"], d.get("n"))
            if max(len(ev) for ev in a.events) < 4: continue
            c, ring, comps, Lam = analyse(a)
            for K in comps:
                nb = 0
                for P in K:
                    if len(a.events[P]) == 4:
                        cp = canon(tri_sectors(a, P)); pat[cp] += 1
                        if cp in BAD: nb += 1
                if nb:
                    s = sum(c[P] for P in K); badcomp[(nb, s)] += 1
                    ex.append((s, nb, a.n, a.T(), f))
    print("4-fold sector patterns (canonical):", pat.most_common(12))
    print("components with bad points: (#bad, cost) ->", sorted(badcomp.items())[:20])
    ex.sort(); print(ex[:5])

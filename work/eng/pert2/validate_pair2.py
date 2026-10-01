# Validate pair_PQ_all.json on real arrangements: every real (4-fold P, triple Q) pair consecutive on a line whose
# canonical pattern is EXCLUDED must have a direct rearrangement with dT > 0, or dT = 0 and dV > 0.
import sys, json, glob, random
sys.path.insert(0, "/home/nail/stuff/sundai_math/work/t3"); sys.path.insert(0, "/home/nail/stuff/sundai_math/work/eng/comp")
from arr import Arr, rays, far_end
from bad_comp import tri_sectors
from direct import test
D = json.load(open("pair_PQ_all.json")); EX = set(map(tuple, D["excluded"])); AL = set(map(tuple, D["allowed"]))
def listing(bits, r, sense):
    n = len(bits)
    return "".join(str(bits[(r + sense*i) % n]) if sense == 1 else str(bits[(r - 1 - i) % n]) for i in range(n))
def canon(a, P, Q, line):
    rP = [i for i, (w, d) in enumerate(rays(a, P)) if w == line and far_end(a, P, (w, d)) == Q][0]
    rQ = [i for i, (w, d) in enumerate(rays(a, Q)) if w == line and far_end(a, Q, (w, d)) == P][0]
    bP, bQ = tri_sectors(a, P), tri_sectors(a, Q)
    x = (listing(bP, rP, 1), listing(bQ, rQ, 1)); y = (listing(bP, rP, -1), listing(bQ, rQ, -1))
    return min(x, y)
rng = random.Random(5); lines = [l for f in ["/home/nail/stuff/sundai_math/work/eng/lattice/mixed_all.jsonl","/home/nail/stuff/sundai_math/work/eng/lattice/lattice18.jsonl","/home/nail/stuff/sundai_math/work/eng/lattice/lattice_family.jsonl"] for l in open(f)]
rng.shuffle(lines)
n_ex = n_ok = n_fail = n_al = n_skip = 0
for line in lines[:1100]:
    d = json.loads(line); a = Arr(d["gens"], d.get("n"))
    for P, ev in enumerate(a.events):
        if len(ev) != 4: continue
        for (w, dd) in rays(a, P):
            Q = far_end(a, P, (w, dd))
            if Q is None or len(a.events[Q]) != 3: continue
            key = canon(a, P, Q, w)
            if key in AL: n_al += 1; continue
            assert key in EX, key
            r = test(d["gens"], sorted([P, Q]), a.n)
            if r is None: n_skip += 1; continue
            n_ex += 1
            if any(dT > 0 or (dT == 0 and dV > 0) for dT, dV, _ in r[1]): n_ok += 1
            else:
                n_fail += 1
                if n_fail <= 3: print("FAIL", key, r[0], r[1][:2])
print(f"excluded pairs tested {n_ex}: reducible {n_ok}, FAIL {n_fail}; allowed-pattern pairs {n_al}; not adjacent in sweep {n_skip}")

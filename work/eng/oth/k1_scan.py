# Count kites by number of quadruple corners (K_q) in IN-CLASS arrangements: only triple + bad 4-fold (no 6-type),
# allowed (4-fold, triple) pair patterns, and the triple optimality condition (both alternating sector sums >= 2).
import sys, json, glob
from collections import Counter
sys.path.insert(0, "work/t3"); sys.path.insert(0, "work/eng/comp"); sys.path.insert(0, "work/eng/pert2")
from arr import Arr, rays, far_end
from bad_comp import tri_sectors, canon
AL = {tuple(x) for x in json.load(open("work/eng/pert2/pair_PQ_all.json"))["allowed"]}
def listing(b, r, s): n = len(b); return "".join(str(b[(r + i) % n]) if s == 1 else str(b[(r - 1 - i) % n]) for i in range(n))
def inclass(a):
    for P, ev in enumerate(a.events):
        m = len(ev)
        if m >= 5: return False
        if m == 4 and canon(tri_sectors(a, P)) not in ("11111111", "11111110"): return False
        if m == 3:
            b = tri_sectors(a, P)
            if b[0] + b[2] + b[4] < 2 or b[1] + b[3] + b[5] < 2: return False
    for P, ev in enumerate(a.events):
        if len(ev) != 4: continue
        for (w, d) in rays(a, P):
            Q = far_end(a, P, (w, d))
            if Q is None or len(a.events[Q]) != 3: continue
            rP = [i for i, (ww, dd) in enumerate(rays(a, P)) if ww == w and far_end(a, P, (ww, dd)) == Q][0]
            rQ = [i for i, (ww, dd) in enumerate(rays(a, Q)) if ww == w and far_end(a, Q, (ww, dd)) == P][0]
            bP, bQ = tri_sectors(a, P), tri_sectors(a, Q)
            if min((listing(bP, rP, 1), listing(bQ, rQ, 1)), (listing(bP, rP, -1), listing(bQ, rQ, -1))) not in AL: return False
    return True
files = ["work/eng/lattice/lattice18.jsonl", "work/eng/lattice/lattice_family.jsonl", "work/eng/lattice/mixed_all.jsonl", "work/eng/lattice/t22_clean.jsonl"] + glob.glob("work/eng/T27/cegar/**/*.jsonl", recursive=True) + glob.glob("work/eng/T22/gen_*.jsonl")
seen = set(); nin = 0; K = Counter(); kq1_examples = []
for f in files:
    if "cuts" in f: continue
    for line in open(f):
        try: d = json.loads(line)
        except Exception: continue
        g = d.get("gens")
        if not g or g in seen: continue
        seen.add(g)
        try: a = Arr(g, d.get("n", 18))
        except Exception: continue
        if a.n != 18 or not any(len(ev) == 4 for ev in a.events): continue
        if not inclass(a): continue
        nin += 1
        for X, ev in enumerate(a.events):
            if len(ev) != 2 or sum(tri_sectors(a, X)) != 4: continue
            corners = [far_end(a, X, r) for r in rays(a, X)]
            if any(c is None for c in corners): continue
            q = sum(1 for c in corners if len(a.events[c]) == 4)
            K[q] += 1
            if q == 1 and len(kq1_examples) < 3: kq1_examples.append((g[:80], X))
print("in-class arrangements with a 4-fold point:", nin, " kites by #quadruple corners:", dict(K))
print("K_1 examples:", kq1_examples)

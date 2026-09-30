# Validate the perturbation lemma on real arrangements: for 4-fold points, splice every local word into the
# wiring word, recompute T directly, and compare the best Delta T with pert.py's prediction for the sector pattern.
import sys, json, glob, random
sys.path.insert(0, "work/t3"); sys.path.insert(0, "work/eng/comp"); sys.path.insert(0, "work/eng/pert")
from arr import Arr
from bad_comp import tri_sectors, canon
from pert import words, faces
from collections import Counter
m = 4
W = words(m)
opts = set(faces(m, w) for w in W)
def pred_best(bits):
    return max(t - sum(1 for s in range(2*m) if bits[s] and e[s] > 0) for (e, t, mm) in opts)
# canonical pattern -> predicted best (dihedral invariance of the option set checked below)
rng = random.Random(3); ok = bad = 0; seen = Counter()
lines = [l for f in sorted(glob.glob("work/eng/T22/gen_*.jsonl")) for l in open(f)]
rng.shuffle(lines)
for line in lines[:400]:
    d = json.loads(line); gens = d["gens"].split(); a = Arr(d["gens"], d.get("n")); T0 = a.T()
    for idx, tok in enumerate(gens):
        if tok.count("*") != 2: continue
        eid = idx  # event ids follow token order
        bits = tri_sectors(a, eid)
        g = int(tok.rstrip("*"))
        best = None
        for w in W:
            new = gens[:idx] + [str(g+i) + "*"*(j-i-1) for (i, j) in w] + gens[idx+1:]
            T1 = Arr(" ".join(new), a.n).T()
            best = T1 - T0 if best is None else max(best, T1 - T0)
        p = pred_best(bits)
        seen[canon(bits)] += 1
        if p == best: ok += 1
        else:
            bad += 1
            if bad <= 5: print("MISMATCH", canon(bits), "pred", p, "direct", best)
print("4-fold points checked:", ok + bad, "agree:", ok, "disagree:", bad, "patterns:", len(seen))

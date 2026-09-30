"""necessary test: uniform strictness on NO-CLEAN real n=18 93s (C2 or full), separate weights. rows -> LP max eps."""
import sys, json, collections, pickle
from fractions import Fraction as F
ROOT = "/home/nail/stuff/sundai_math"
sys.path.insert(0, ROOT + "/search"); sys.path.append(ROOT + "/work/t3")
import inspect  # noqa
from multiprocessing import Pool
def work(args):
    fn, mod, part, cls = args
    import line_automaton as LA, rule_lp_t25 as T, rule_ref as RR
    LA._imports()
    C2 = {RR.canon_ring(x) for x in "NNNNNN,BNNNNN,BNNBNN,BNNRNN,NNNNNR,NNNNRR,NNRNNR,NNNRRR,NNRRRR,RRRRRR,BNNNNR,BNNNRR,BRNNNR,BNNRRR,BRNNRR".split(",")}
    rows = []
    for g, ch in LA.iter_arrangements([fn], True, 10**9, mod=mod, part=part):
        a = ch.a
        if a.n != 18 or not ch.trip or a.T() < 93: continue
        if cls == "C2" and any(RR.canon_ring(ch.st[P]) not in C2 for P in a.triples): continue
        caps = {b[5] for b in ch.blk}
        if any(not ch.onl[L] and L not in caps for L in range(a.n)): continue      # has a clean line
        res, unk = T.real_line_vectors(a, None, t1pp=True, extras=True)
        for L, (v, nt) in res.items():
            rows.append((v, tuple(sorted(((str(k), c) for k, c in nt.items() if k != ("a",)), key=str))))
    return rows
if __name__ == "__main__":
    cls = sys.argv[1]
    files = sys.argv[2:]
    tasks = [(f, 4, p, cls) for f in files for p in range(4)]
    allrows = set()
    with Pool(12) as pool:
        for rs in pool.imap_unordered(work, tasks):
            allrows.update(rs)
    allrows = list(allrows)
    cols = sorted({k for _, nt in allrows for k, _ in nt})
    ci = {k: i for i, k in enumerate(cols)}
    print(cls, "distinct rows", len(allrows), "cols", len(cols), flush=True)
    import numpy as np
    from scipy.optimize import linprog
    # variables: w_k (k != alpha) in [0, 20], alpha in [0, 1], eps free in [0, 1]; maximize eps
    nv = len(cols) + 1
    A, b = [], []
    for v, nt in allrows:
        row = np.zeros(nv)
        for k, c in nt:
            row[ci[k]] = float(c)
        row[-1] = -3.0
        A.append(-row); b.append(float(v))          # -(v + w.nt - 3eps) <= 0  ->  -w.nt + 3 eps <= v
    bounds = [(0, 1) if k == "('alpha',)" else (0, 20) for k in cols] + [(0, 1)]
    c = np.zeros(nv); c[-1] = -1
    r = linprog(c, A_ub=np.array(A), b_ub=np.array(b), bounds=bounds, method="highs")
    print(cls, "status", r.status, "max eps", r.x[-1] if r.status == 0 else None, flush=True)

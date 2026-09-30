"""necessary test: NC real 93s, target final_L >= 3 eps * [L has >= 2 triple points] (and variant sigma = k_L - 1)"""
import sys, pickle, collections
ROOT = "/home/nail/stuff/sundai_math"
sys.path.insert(0, ROOT + "/search"); sys.path.append(ROOT + "/work/t3")
import inspect  # noqa
from multiprocessing import Pool
def work(args):
    fn, mod, part, cls = args
    import line_automaton as LA, rule_lp_t25 as T, rule_ref as RR
    LA._imports()
    C2 = {RR.canon_ring(x) for x in "NNNNNN,BNNNNN,BNNBNN,BNNRNN,NNNNNR,NNNNRR,NNRNNR,NNNRRR,NNRRRR,RRRRRR,BNNNNR,BNNNRR,BRNNNR,BNNRRR,BRNNRR".split(",")}
    rows = set(); nonGP = 0; narr = 0
    for g, ch in LA.iter_arrangements([fn], True, 10**9, mod=mod, part=part):
        a = ch.a
        if a.n != 18 or not ch.trip or a.T() < 93: continue
        if cls == "C2" and any(RR.canon_ring(ch.st[P]) not in C2 for P in a.triples): continue
        caps = {b[5] for b in ch.blk}
        if any(not ch.onl[L] and L not in caps for L in range(a.n)): continue
        kL = {L: sum(1 for V in a.rows[L] if V in ch.trip) for L in range(a.n)}
        narr += 1; nonGP += max(kL.values()) >= 2
        res, unk = T.real_line_vectors(a, None, t1pp=True, extras=True)
        for L, (v, nt) in res.items():
            rows.add((v, tuple(sorted(((str(k), c) for k, c in nt.items() if k != ("a",)), key=str)), kL[L]))
    return rows, narr, nonGP
if __name__ == "__main__":
    cls = sys.argv[1]
    tasks = [(f, 4, p, cls) for f in sys.argv[2:] for p in range(4)]
    allr = set(); na = ng = 0
    with Pool(12) as pool:
        for r, a_, g_ in pool.imap_unordered(work, tasks): allr |= r; na += a_; ng += g_
    allr = list(allr)
    print(cls, "NC arrangements", na, "non-GP", ng, "distinct rows", len(allr), flush=True)
    import numpy as np
    from scipy.optimize import linprog
    cols = sorted({k for _, nt, _ in allr for k, _ in nt}); ci = {k: i for i, k in enumerate(cols)}
    for mode in ("k>=2", "k-1"):
        nv = len(cols) + 1; A, b = [], []
        for v, nt, k in allr:
            row = np.zeros(nv)
            for kk, c in nt: row[ci[kk]] = float(c)
            cred = (1 if k >= 2 else 0) if mode == "k>=2" else max(k - 1, 0)
            row[-1] = -3.0 * cred
            A.append(-row); b.append(float(v))
        bounds = [(0, 1) if k == "('alpha',)" else (0, 20) for k in cols] + [(0, 1)]
        c = np.zeros(nv); c[-1] = -1
        r = linprog(c, A_ub=np.array(A), b_ub=np.array(b), bounds=bounds, method="highs")
        print(cls, mode, "status", r.status, "max eps", r.x[-1] if r.status == 0 else None, flush=True)

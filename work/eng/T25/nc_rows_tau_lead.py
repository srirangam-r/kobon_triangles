import sys, pickle
ROOT = "/home/nail/stuff/sundai_math"
sys.path.insert(0, ROOT + "/search"); sys.path.append(ROOT + "/work/t3")
import inspect  # noqa
from multiprocessing import Pool
def work(args):
    fn, mod, part, cls = args
    import line_automaton as LA, rule_lp_t25 as T, rule_ref as RR
    LA._imports()
    C2 = {RR.canon_ring(x) for x in "NNNNNN,BNNNNN,BNNBNN,BNNRNN,NNNNNR,NNNNRR,NNRNNR,NNNRRR,NNRRRR,RRRRRR,BNNNNR,BNNNRR,BRNNNR,BNNRRR,BRNNRR".split(",")}
    rows = {}
    for g, ch in LA.iter_arrangements([fn], True, 10**9, mod=mod, part=part):
        a = ch.a
        if a.n != 18 or not ch.trip or a.T() < 93: continue
        if cls == "C2" and any(RR.canon_ring(ch.st[P]) not in C2 for P in a.triples): continue
        caps = {b[5] for b in ch.blk}
        if any(not ch.onl[L] and L not in caps for L in range(a.n)): continue
        res, unk = T.real_line_vectors(a, None, t1pp=True, extras=True, credit=True)
        for L, (v, nt) in res.items():
            rows[(v, tuple(sorted(nt.items(), key=str)))] = (fn.split("/")[-1], g, L)
    return rows
if __name__ == "__main__":
    out, cls = sys.argv[1], sys.argv[2]
    tasks = [(f, 4, p, cls) for f in sys.argv[3:] for p in range(4)]
    allr = {}
    with Pool(12) as pool:
        for r in pool.imap_unordered(work, tasks): allr.update(r)
    pickle.dump(allr, open(out, "wb")); print(cls, "rows", len(allr))

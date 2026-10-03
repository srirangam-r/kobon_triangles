"""data check of the FC weights on real arrangements with n in {14,16,20} (multiplicity<=3, with triple points):
exact final of every line, conservation of rule columns per arrangement, identity sum_L final <= 3 Lambda - n.
usage: data_check.py NPROC files..."""
import sys, pickle, collections, time
from fractions import Fraction as F
ROOT = str(__import__("pathlib").Path(__file__).resolve().parents[3])
sys.path.insert(0, ROOT + "/search"); sys.path.append(ROOT + "/work/t3")
sys.path.insert(0, ROOT + "/work/eng/A30/elim")
from multiprocessing import Pool
NS = (14, 16, 20)
_st = pickle.load(open(ROOT + "/work/eng/T25/elim/state_2.pkl", "rb"))
import __main__, rule_lp as RL
__main__.EFrame = RL.EFrame
_c = _st["certs"][1]; assert _c["name"] == "FC"
D = _c["D"]; W = {k: F(x, D) for k, x in _c["w"].items()}

def work(fn):
    import line_automaton as LA, rule_lp_t25 as T
    LA._imports()
    c = collections.Counter(); minfin = {}; worst = {}
    for g, ch in LA.iter_arrangements([fn], True, 10**9):
        n = ch.a.n
        if n not in NS or not ch.trip: continue
        res, unk = T.real_line_vectors(ch.a, None, t1pp=True, extras=True)
        c[f"arr{n}"] += 1
        tot = collections.Counter(); sumfin = F(0)
        for L, (v, nt) in res.items():
            fin = F(v)
            for k, x in nt.items():
                wk = W.get(k)
                if wk: fin += wk * x
                if k not in (("a",), ("alpha",), ("wr",)) and k[0] != "U": tot[k] += x
            c[f"lines{n}"] += 1
            if fin < 0: c[f"neg{n}"] += 1
            if fin == 0: c[f"tight{n}"] += 1
            if n not in minfin or fin < minfin[n]: minfin[n] = fin; worst[n] = (g[:80], L)
            sumfin += fin
        if any(x != 0 for x in tot.values()): c[f"nonconserved{n}"] += 1
        lam3 = 3 * (n * (n - 2) - 3 * ch.a.T()) - n
        if sumfin > lam3: c[f"identity_violation{n}"] += 1
        if lam3 == 0: c[f"T_at_bound{n}"] += 1
    return fn, dict(c), minfin, worst

if __name__ == "__main__":
    nproc = int(sys.argv[1]); files = sys.argv[2:]
    tot = collections.Counter(); mn = {}; t0 = time.time()
    with Pool(nproc) as p:
        for fn, c, mf, wo in p.imap_unordered(work, files):
            tot.update(c)
            for n, v in mf.items():
                if n not in mn or v < mn[n][0]: mn[n] = (v, wo[n])
            print(f"[{time.time()-t0:.0f}s] {fn.split('/')[-3:]} {c} min {dict((k, str(v)) for k, v in mf.items())}", flush=True)
    print("TOTAL", dict(sorted(tot.items())))
    print("MIN FINAL per n:", {n: str(v[0]) for n, v in mn.items()}, {n: v[1] for n, v in mn.items()})

# Small-n probe: does a structural-class arrangement (mult<=4, bad quads only, pair lemma lazily, optionally the triple
# alternating-sum optimality) with an ALL-8 point and Lambda = n(n-2)-3T <= LAM exist?  Uses sol's global_sat.build.
# Every SAT model is reconstructed to a wiring word and re-evaluated independently (arr.py) before being reported.
import sys, json, time, argparse
ROOT = "/home/nail/stuff/sundai_math"
sys.path[:0] = [ROOT + "/work/bbl/all8_work/pydeps", ROOT + "/work/bbl/all8_work", ROOT + "/work/bbl", ROOT + "/work/eng/T27", ROOT + "/search", ROOT + "/work/t3"]
import global_sat as G, q_probe as QP
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver
ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int); ap.add_argument("--lam", type=int, default=6)
ap.add_argument("--opt", type=int, default=1); ap.add_argument("--seconds", type=int, default=600)
a_ = ap.parse_args(); n = a_.n
B = G.build(n, None)
C = G.C
if a_.opt:
    for t in B.trip:
        ring = C.triple_ring(B, t); z = B.z[t]
        for par in (0, 1):
            e = [ring[par], ring[par + 2], ring[par + 4]]
            for i in range(3):
                for j in range(i + 1, 3):
                    B.cl.append([-z, e[i], e[j]])
tmin = -(-(n * (n - 2) - a_.lam) // 3)
ts = list(B.tri.values())
card = CardEnc.atleast(ts, tmin, top_id=B.nv, encoding=EncType.seqcounter); B.nv = card.nv; B.cl.extend(card.clauses)
t0 = time.time(); lazy = 0
with Solver(name="cadical153", bootstrap_with=B.cl) as sv:
    while True:
        r = sv.solve()
        if not r:
            print(json.dumps(dict(n=n, lam=a_.lam, opt=a_.opt, result="UNSAT", lazy=lazy, sec=round(time.time() - t0, 1)))); break
        Ms = {x for x in sv.get_model() if x > 0}
        vio = C.pair_violations(B, Ms)
        if vio:
            for v in vio: sv.add_clause(C.violation_clause(B, v))
            lazy += len(vio); continue
        arr, gens = QP.to_arr(B, Ms)
        from arr import Arr
        a = Arr(gens, n)
        T = a.T() if callable(getattr(a, "T", None)) else None
        mult = sorted(len(e) for e in a.events if len(e) > 2)
        print(json.dumps(dict(n=n, lam=a_.lam, opt=a_.opt, result="SAT", T=T, Lambda=(n * (n - 2) - 3 * T) if T is not None else None, mult=mult, gens=gens, sec=round(time.time() - t0, 1)))); break

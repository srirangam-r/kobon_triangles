"""Run T15's Hall query (search/hall_sat.py, read-only) with the order-free parity lemmas of search/parity_lemmas.py
added to the base model.

    python search/hall_lemma_run.py --n 8 --eps 1/6 [--nolemmas] [--workers 4] [--tlimit 900] [--strict]
--strict: violation means Hall sum <= 0 (in scaled units) instead of < 0 (use with --eps 0 for the strict-Hall variant)
"""
import argparse
import json
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.append(str(ROOT / "work/t3"))
import hall_model_frozen as hs  # noqa: E402  (frozen copy of T15's search/hall_sat.py)
from parity_lemmas import add_parity_lemmas  # noqa: E402


def layer(cp, n, dv, dlo, dhi, rel2, inS, thr=-1):
    """copy of hall_sat.add_layer with the violation threshold as a parameter: sum_S d + sum_{N2(S),d>0} d <= thr"""
    R = range(n)
    BIG = hs.BIG
    sd, w, nb = [], [], []
    for L in R:
        cp.linear([dv[L]], [1], -BIG, -1, enforce=[inS[L]])
        s_ = cp.nint(min(0, dlo[L]), 0)
        cp.linear([s_, dv[L]], [1, -1], 0, BIG, enforce=[inS[L]])
        cp.linear([s_], [1], 0, 0, enforce=[~inS[L]])
        w_ = cp.nint(0, max(0, dhi[L]))
        nbL = cp.nbool()
        if dhi[L] > 0:
            cp.linear([w_, dv[L]], [1, -1], 0, BIG, enforce=[nbL])
        sd.append(s_)
        w.append(w_)
        nb.append(nbL)
    for L in R:
        for M in R:
            if L == M or rel2[L, M] is False or dhi[M] <= 0:
                continue
            cl = [~inS[L], nb[M]]
            if rel2[L, M] is not True:
                cl.append(~rel2[L, M])
            cp.clause(cl)
    cp.linear(sd + w, [1] * (2 * n), -BIG, thr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--eps", default="1/6")
    ap.add_argument("--hops", type=int, default=2)
    ap.add_argument("--nolemmas", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--tlimit", type=float, default=900)
    ap.add_argument("--tree", type=int, default=0)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--cubeB", action="store_true", help="line 0 has no triple point and caps a block")
    ap.add_argument("--S0", action="store_true", help="fix S = {line 0}")
    o = ap.parse_args()
    t0 = time.time()
    hm = hs.HallModel(o.n, Fr(o.eps), o.hops)
    k = 0 if o.nolemmas else add_parity_lemmas(hm.um)
    if o.strict:
        hs.add_layer = lambda cp, n, dv, dlo, dhi, rel2, inS: layer(cp, n, dv, dlo, dhi, rel2, inS, thr=0)
    cp, inS, dv = hs.build_cp(hm, tree=o.tree)
    print(f"n={o.n} eps={o.eps} lemmas={'no' if o.nolemmas else k}: {hm.f.nv} vars {hm.f.ncl} clauses, "
          f"built {time.time() - t0:.1f}s", flush=True)
    extra = list(hs.sign_prefix(hm))
    if o.cubeB:
        um = hm.um
        extra.append([-um.zl[0]])
        extra.append([um.Bk[l, 0, d] for l in range(1, o.n) for d in (1, -1)])
    if o.S0:
        extra += [[inS[L] + 1] if L == 0 else [-(inS[L] + 1)] for L in range(o.n)]
    res, val, sol, secs = hs.solve_cp(cp.proto, extra, tlimit=o.tlimit, workers=o.workers)
    rec = dict(n=o.n, eps=o.eps, lemmas=not o.nolemmas, strict=o.strict, cubeB=o.cubeB, S0=o.S0, result=res, secs=round(secs, 1))
    if res == "SAT":
        rec["witness"] = hs.witness_info(hm, val, o.n, Fr(o.eps))
        rec["witness"]["S"] = [L for L in range(o.n) if sol[inS[L]]]
    print(json.dumps(rec), flush=True)
    if o.out:
        open(o.out, "a").write(json.dumps(rec) + "\n")


if __name__ == "__main__":
    main()

"""Pure-SAT (CaDiCaL) Hall layer for HL(eps) on the frozen T15 value model (search/hall_model_frozen.py).

Soundness design: every encoded line value d_enc satisfies d_enc <= d (positive part saturated at a cap, negative part
saturating to -infinity), so a real violation stays satisfiable. UNSAT therefore proves HL at that n. SAT answers
must be re-checked with search/bbl_hall.py; they can be spurious only through saturation.

Violation (thr = -1: Hall sum <= -1, i.e. < 0;  --strict thr = 0: Hall sum <= 0, i.e. < 1/2 at eps = 0):
  S nonempty, line 0 in S, d < 0 on S,   sum_{T} max(d, 0) <= sum_{S} |d| + thr,   T = N2(S) \ S.

    python search/hall_pure.py --n 8 --eps 0 --strict [--lemmas] [--caps 40] [--J 12]
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
import hall_model_frozen as hs  # noqa: E402
from unit_sat import _tot  # noqa: E402


def thermo(f, lits, cap):
    """T[k-1] <-> min(count, cap) >= k, k = 1..min(len, cap)"""
    if not lits:
        return []
    up = _tot(f, lits, cap, True)
    dn = _tot(f, lits, cap, False)
    T = []
    for k in range(min(len(up), len(dn))):
        v = f.new()
        f.add([-up[k], v])
        f.add([-v, dn[k]])
        T.append(v)
    return T


def line_ge(f, P, N, c, ks):
    """dge[k] <-> c + P_enc - N_enc >= k, with P_enc = min(P, cap) and N_enc = N if N < len(N) thermometer else +inf"""
    KP, KN = len(P), len(N)
    Pa = lambda a: True if a <= 0 else (P[a - 1] if a <= KP else False)  # noqa: E731

    def Nb(b):          # literal [N_enc >= b]
        if b <= 0:
            return True
        return N[b - 1] if b <= KN else (N[KN - 1] if KN else False)
    out = {}
    for k in ks:
        v = f.new()
        for a in range(0, KP + 1):
            b = a + c - k + 1           # need N_enc <= a + c - k, i.e. not [N >= b]
            pa, pa1, nb = Pa(a), Pa(a + 1), Nb(b)
            # v <- P_enc >= a and N_enc < b
            if pa is not False and nb is not True:
                cl = [v]
                if pa is not True:
                    cl.append(-pa)
                if nb is not False:
                    cl.append(nb)
                f.add(cl)
            # v and P_enc == a  ->  N_enc < b
            if pa is not False and pa1 is not True:
                cl = [-v]
                if pa is not True:
                    cl.append(-pa)
                if pa1 is not False:
                    cl.append(pa1)
                if nb is True:
                    f.add(cl)
                elif nb is not False:
                    f.add(cl + [-nb])
        out[k] = v
    return out


def build(n, eps, hops, strict, lemmas, cap, J):
    hm = hs.HallModel(n, Fr(eps), hops)
    f = hm.f
    if lemmas:
        from parity_lemmas import add_parity_lemmas
        add_parity_lemmas(hm.um)
    R = range(n)
    inS = [f.new() for _ in R]
    dge = {}
    for L in R:
        terms, c = hm.dwork(L)
        P = [x for x, w in terms if w > 0 for _ in range(w)]
        Nn = [x for x, w in terms if w < 0 for _ in range(-w)]
        TP, TN = thermo(f, P, cap), thermo(f, Nn, cap)
        dge[L] = line_ge(f, TP, TN, c, list(range(-J, J + 1)))
    ovf = []
    for L in R:
        f.add([-inS[L], -dge[L][0]])                   # S-lines are negative
        o = f.AND([inS[L], -dge[L][-J]])               # deficit beyond the window: counts as a violation (sound)
        ovf.append(o)
    OV = f.OR(ovf)
    inT = []
    for M in R:
        nbrs = [f.AND([inS[K], hm.rel2[K, M]]) for K in R if K != M]
        inT.append(f.AND([f.OR(nbrs), -inS[M]]))
    lhs_items = [f.AND([inT[M], dge[M][j]]) for M in R for j in range(1, J + 1)]
    rhs_items = [f.AND([inS[L], -dge[L][-j + 1]]) for L in R for j in range(1, J + 1)]
    Kc = len(rhs_items)
    LHS = _tot(f, lhs_items, Kc + 1, True)
    RHS = _tot(f, rhs_items, Kc + 1, False)
    thr = 0 if strict else -1
    # LHS <= RHS + thr   <=>   for all k >= 0: LHS >= k  ->  RHS >= k - thr
    for k in range(0, len(LHS) + 1):
        need = k - thr
        if need <= 0:
            continue
        cl = [OV]
        if k >= 1:
            cl.append(-LHS[k - 1])
        if need <= len(RHS):
            cl.append(RHS[need - 1])
        f.add(cl)
    f.add([inS[0]])
    for cl in hs.sign_prefix(hm):
        f.add(cl)
    return hm, inS, dge, OV


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--eps", default="0")
    ap.add_argument("--hops", type=int, default=2)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--lemmas", action="store_true")
    ap.add_argument("--cap", type=int, default=40)
    ap.add_argument("--J", type=int, default=12)
    ap.add_argument("--out")
    o = ap.parse_args()
    t0 = time.time()
    hm, inS, dge, OV = build(o.n, o.eps, o.hops, o.strict, o.lemmas, o.cap, o.J)
    from pysat.solvers import Solver
    s = Solver(name="cadical195", bootstrap_with=list(hm.f.clauses()))
    t1 = time.time()
    print(f"n={o.n} eps={o.eps} strict={o.strict} lemmas={o.lemmas}: {hm.f.nv} vars {hm.f.ncl} clauses, "
          f"built {t1 - t0:.1f}s", flush=True)
    ok = s.solve()
    rec = dict(n=o.n, eps=o.eps, strict=o.strict, lemmas=o.lemmas, cap=o.cap, J=o.J,
               result="SAT" if ok else "UNSAT", secs=round(time.time() - t1, 1))
    if ok:
        mod = s.get_model()
        val = lambda v: mod[v - 1] > 0  # noqa: E731
        rec["S"] = [L for L in range(o.n) if val(inS[L])]
        rec["overflow"] = val(OV)
        rec["word"] = hs.word_from_chi(hm.um.chi_from_model(val), o.n)
        rec["d_enc"] = [max([k for k in dge[L] if val(dge[L][k])], default=-o.J - 1) for L in range(o.n)]
    print(json.dumps(rec), flush=True)
    if o.out:
        open(o.out, "a").write(json.dumps(rec) + "\n")


if __name__ == "__main__":
    main()

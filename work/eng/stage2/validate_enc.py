#!/usr/bin/env python3
"""Validate the c2..c9 encodings: pin a known arrangement's chi (assumptions), solve with ONE constraint guard
switched on; result must equal the exact predicate.  Also checks T and W readbacks."""
import sys, json, time, random
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stage2_sat as S
import stage2_exact as X
import note3_check as N3c
from pysat.solvers import Solver
from collections import Counter

def pins(B, a):
    out = []
    for t in B.trip:
        r, i, j = t
        vi = next(v for v in a.rows[r] if i in a.events[v]); vj = next(v for v in a.rows[r] if j in a.events[v])
        out.append(B.z[t] if vi == vj else B.ng[t] if a.pos[r][vi] < a.pos[r][vj] else B.pz[t])
    return out

def main(files, nmax, seed):
    B = S.base_class(18, None, all8=False)
    S2 = S.Stage2(B, guard=True).build_all(None, True, True, True)
    print('model', B.nv, len(B.cl), flush=True)
    recs = []
    for f in files:
        L = [json.loads(l) for l in open(f)]
        random.Random(seed).shuffle(L)
        recs += [(f, d['gens']) for d in L[:nmax]]
    sv = Solver(name='cadical153', bootstrap_with=B.cl)
    tot = Counter(); bad = 0; t0 = time.time()
    for f, g in recs:
        a = X.Arr(g, 18)
        if max(map(len, a.events)) > 4: continue
        pr = X.preds(a); pa = pins(B, a)
        if not sv.solve(assumptions=pa):
            tot['base_unsat'] += 1; continue
        m = set(x for x in sv.get_model() if x > 0)
        T = sum(v in m for v in B.tri.values()); W = sum(v in m for v in S2.wedges)
        if T != pr['T'] or W != pr['W']:
            print('MISMATCH T/W', T, pr['T'], W, pr['W']); bad += 1
        tot['arr'] += 1
        qd = X.quad_dkc(a)
        cr = N3c.credit_state(a)['Scorr'] if qd else {}
        for P, (D, k, cB) in qd.items():
            Q = tuple(sorted(a.events[P]))
            got = sv.solve(assumptions=pa + [S2.gq[Q]])
            exp = (k + cB == 4)
            tot['c10', 'sat' if exp else 'unsat'] += 1
            if got != exp: bad += 1; print('MISMATCH c10', Q, D, k, cB, got, g[:60], flush=True)
            if cr[P] != 8 - D - k - 2 * cB: bad += 1; print('MISMATCH Scorr formula', P, cr[P], D, k, cB, flush=True)
            tot['Scorr_formula_ok'] += 1
            kt = {X_: (cs_, q_, caps_) for X_, cs_, q_, caps_ in X.kites(a)}
            for L_ in Q:
                x_ = min(y for y in Q if y != L_)
                for d_ in (1, -1):
                    Xv = X.far_end(a, P, (L_, d_))
                    ek = Xv in kt
                    ecb = ek and kt[Xv][1] == 1 and not any(X.single(a, e) for e in kt[Xv][2])
                    sk = S2.kr[L_, x_, d_] in m; scb = S2.cb[L_, x_, d_] in m
                    tot['ray_checks'] += 1
                    if (ek, ecb) != (sk, scb): bad += 1; print('MISMATCH ray', Q, L_, d_, ek, ecb, sk, scb, flush=True)
        for c in ['c2','c3','c4','c5','c6','c7','c8','c9']:
            got = sv.solve(assumptions=pa + [S2.g[c]])
            exp = pr[c]
            tot[c, 'sat' if exp else 'unsat'] += 1
            if got != exp:
                bad += 1; print('MISMATCH', c, got, exp, g[:60], flush=True)
    print('done', time.time()-t0, 'bad', bad); print(sorted(tot.items(), key=str))
if __name__ == '__main__':
    nmax = int(sys.argv[1]); seed = int(sys.argv[2]); main(sys.argv[3:], nmax, seed)

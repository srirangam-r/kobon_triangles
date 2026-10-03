#!/usr/bin/env python3
"""Global all-8/T=94 probe. An UNKNOWN is not a certificate.

Uses the existing signotope/triangle model and class constraints, without
anchoring the all-8 point's slope labels. Pair clauses are added lazily.
Any UNSAT result still needs proof checking and an encoding audit.
"""
from pathlib import Path
from itertools import combinations
import argparse
import json
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'work/bbl/all8_work/pydeps'),
                str(ROOT / 'work/eng/T27'), str(ROOT / 'search')]
import classsat as C
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver


def dump_cnf(clauses, nv, path):
    with path.open('w') as f:
        f.write(f'p cnf {nv} {len(clauses)}\n')
        for cl in clauses:
            f.write(' '.join(map(str, cl)) + ' 0\n')


def build(K, target, known_gens=None):
    B = C.P.Base(K)
    C.add_class(B)
    selectors = []
    for quad in combinations(range(K), 4):
        zq = [B.z[C.P.key3(*t)] for t in combinations(quad, 3)]
        ring = C.quad_ring(B, quad)
        # In the remaining class there are no 6-type points.
        for i in range(8):
            B.cl.append([-x for x in zq] + [ring[i], ring[(i + 4) % 8]])
        selectors.append(B.AND(zq + ring))
    B.cl.append(selectors)
    ts = list(B.tri.values())
    # T <=94 is already certified for this class; test the sole possible violation.
    if target is not None:
        card = CardEnc.equals(ts, target, top_id=B.nv, encoding=EncType.seqcounter)
        B.nv = card.nv
        B.cl.extend(card.clauses)
    if known_gens is not None:
        sys.path.insert(0, str(ROOT / 'work/t3'))
        from arr import Arr
        a = Arr(known_gens, K)
        for t in B.trip:
            r, i, j = t
            vi = next(v for v in a.rows[r] if i in a.events[v])
            vj = next(v for v in a.rows[r] if j in a.events[v])
            if vi == vj:
                B.cl.append([B.z[t]])
            elif a.pos[r][vi] < a.pos[r][vj]:
                B.cl.append([B.ng[t]])
            else:
                B.cl.append([B.pz[t]])
    return B


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=int, default=1200)
    ap.add_argument('--solver', default='glucose4')
    ap.add_argument('--out', default=str(ROOT / 'work/bbl/all8_work/global18'))
    ap.add_argument('--validate-witness', action='store_true')
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    known = None
    target = 94
    if args.validate_witness:
        sys.path.insert(0, str(ROOT / 'work/bbl'))
        import all8_boundary_check as ck
        from lines2gens import to_gens
        from fractions import Fraction as F
        ls = [(0,1,0),(1,0,0),(1,1,-6),(1,-1,0),(1,2,-6),(2,1,-6),
              (4,-5,2),(-3,6,214),(15,12,4),(-6,7,-222)]
        ls += [(7+i,1,1000000+101*i**3) for i in range(8)]
        known, _ = to_gens([(F(a),F(b)-F(a,37),F(c)) for a,b,c in ls])
        target = 29
    B = build(18, target, known)
    print(json.dumps(dict(event='built', variables=B.nv, clauses=len(B.cl),
                          seconds=time.time()-t0)), flush=True)
    dump_cnf(B.cl, B.nv, out / 'problem.cnf')
    lazy = 0
    with Solver(name=args.solver, bootstrap_with=B.cl, with_proof=True) as sv:
        while True:
            left = args.seconds - (time.time() - t0)
            if left <= 0:
                result = 'UNKNOWN'
                break
            sv.clear_interrupt()
            timer = threading.Timer(left, sv.interrupt)
            timer.daemon = True
            timer.start()
            try:
                res = sv.solve_limited(expect_interrupt=True)
            finally:
                timer.cancel()
            if res is None:
                result = 'UNKNOWN'
                break
            if not res:
                result = 'UNSAT'
                # Save the final clause set, including sound lazy pair clauses.
                dump_cnf(B.cl, B.nv, out / 'problem.cnf')
                proof = sv.get_proof()
                if proof is not None:
                    (out / 'proof.drat').write_text('\n'.join(proof) + '\n')
                break
            Ms = {x for x in sv.get_model() if x > 0}
            vio = C.pair_violations(B, Ms)
            if not vio:
                result = 'SAT'
                chi = C.chi_of(B, Ms)
                (out / 'model_chi.json').write_text(json.dumps(
                    [[list(t), v] for t, v in chi.items()]))
                print(json.dumps(dict(event='model', triangles=sum(v in Ms for v in B.tri.values()))), flush=True)
                break
            for v in vio:
                clause = C.violation_clause(B, v)
                sv.add_clause(clause)
                B.cl.append(clause)
            lazy += len(vio)
            print(json.dumps(dict(event='lazy', new=len(vio), total=lazy,
                                  seconds=time.time()-t0)), flush=True)
        summary = dict(result=result, seconds=time.time()-t0, lazy_clauses=lazy,
                       variables=B.nv, clauses=len(B.cl), statistics=sv.accum_stats(),
                       validation=args.validate_witness)
    (out / 'result.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()

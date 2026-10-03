#!/usr/bin/env python3
"""Run one cube of the stage-2 probe.
  --cube I      : all-8 point on the lines of orbit representative I (cubes.py)
  --quad a,b,c,d: explicit quad
  --nocube      : no cube (all-8 selector clause only)
  --no-extra    : base class model only (T target, W>=minW, selector), constraints c1..c9 OFF
Result JSON/log in --out. UNSAT => gzip CNF (with lazy pair clauses) for later DRAT."""
import sys, json, time, argparse, gzip, os
from itertools import combinations
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stage2_sat as S
import stage2_exact as X
import cubes as CU
from pysat.solvers import Solver
import q_probe as Q
import note3_check as N3

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cube', type=int); ap.add_argument('--quad'); ap.add_argument('--nocube', action='store_true')
    ap.add_argument('--seconds', type=int, default=300); ap.add_argument('--out', required=True)
    ap.add_argument('--target', type=int, default=94); ap.add_argument('--solver', default='cadical153')
    ap.add_argument('--no-extra', action='store_true'); ap.add_argument('--minW', type=int, default=12)
    ap.add_argument('--drop', default='', help='comma list of constraints among c2..c9 to drop')
    ap.add_argument('--chunk', type=int, default=20000); ap.add_argument('--no-c10', action='store_true'); ap.add_argument('--tcard', default='equals_seq'); ap.add_argument('--mask'); ap.add_argument('--pins', action='store_true')
    ap.add_argument('--qpin', action='store_true', help='single-B cubes: the quad first neighbour Q on H = line of ray i+4 is a single-case-B endpoint (k=2 path; k>=3 and alternating endpoints excluded by hand, STAGE2_TASK6 s5-s6), so its case-B block is the ray of H at Q pointing away from P')
    ap.add_argument('--dump', default='', help='write the CNF (mask, pins, split included; no lazy pair clauses) and exit')
    ap.add_argument('--split', default='', help='cube-and-conquer: comma list mm:c; asserts that the first multiple neighbour on ray mm is formed with line c (one disjunct of the pinned far(mm) clause)')
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    t0 = time.time()
    quad = None
    if args.cube is not None: quad = CU.orbit_reps()[args.cube][0]
    if args.quad: quad = tuple(int(x) for x in args.quad.split(','))
    cubed = quad is not None
    if args.no_extra:
        B = S.base_class(18, args.target, all8=not cubed, tcard=args.tcard)
        wed = S.E.augment(B, args.minW)
    else:
        B = S.base_class(18, args.target, all8=not cubed, tcard=args.tcard)
        S2 = S.Stage2(B, guard=True)
        S2.build_all(12, True, True, not args.no_c10)
        wed = S2.wedges
        drop = [x for x in args.drop.split(',') if x]
        for name, g in S2.g.items():
            if name not in drop: B.cl.append([g])
    if cubed:
        for t in combinations(quad, 3): B.cl.append([B.z[S.key3(*t)]])
        for lit in S.C.quad_ring(B, quad): B.cl.append([lit])
    if args.mask:
        assert cubed and not args.no_extra and not args.no_c10
        m = args.mask
        def ray(mm): return quad[mm % 4], (1 if mm < 4 else -1)
        for mm in range(8):
            L, d = ray(mm); x = min(y for y in quad if y != L)
            B.cl.append([S2.kr[L, x, d] if m[mm] in 'KC' else -S2.kr[L, x, d]])
            B.cl.append([S2.cb[L, x, d] if m[mm] == 'C' else -S2.cb[L, x, d]])
        if args.pins:
            def far(mm, quadf):
                L, d = ray(mm); x = min(y for y in quad if y != L)
                lits = [B.AND([B.A[L, x, c] if d == 1 else B.A[L, c, x], (B.zp2[L, c] if quadf else -B.zp2[L, c])]) for c in range(18) if c not in (L, x)]
                return B.OR(lits)
            nC = m.count('C'); nK = m.count('K')
            Rr = [mm for mm in range(8) if m[mm] == '.']
            if nC == 2:       # isolated double case-B star: all six first multiple neighbours triple (STAGE2_TASK5 s3)
                for mm in Rr: B.cl.append([far(mm, False)])
            elif nC == 0:     # alternating P chosen as a path ENDPOINT (WLOG, STAGE2_TASK5 s4): exactly one quad first neighbour
                fq = [far(mm, True) for mm in Rr]
                B.cl.append(fq)
                for a_, b_ in combinations(range(len(fq)), 2): B.cl.append([-fq[a_], -fq[b_]])
            elif nC == 1:     # single case-B: blocks i, i+3, i+5; Q4 = ray i+4 quad, the rest triple (Note3 s8 propagation)
                i = m.index('C')
                for mm in Rr:
                    B.cl.append([far(mm, mm == (i + 4) % 8)])
    if args.qpin:
        assert args.mask and args.pins and args.mask.count('C') == 1
        i = args.mask.index('C'); H, d = ray((i + 4) % 8); x = min(y for y in quad if y != H)
        for c in range(18):
            if c in quad: continue
            a_lit = B.A[H, x, c] if d == 1 else B.A[H, c, x]
            B.cl.append([-a_lit, -B.zp2[H, c], S2.cb[H, c, d]])
    if args.split:
        assert args.mask and args.pins
        m = args.mask; nC = m.count('C')
        for spec in args.split.split(','):
            mm, c = (int(v) for v in spec.split(':'))
            assert m[mm] == '.', 'split only on pinned rays'
            L, d = ray(mm); x = min(y for y in quad if y != L)
            assert c not in (L, x)
            quadf = (nC == 1 and mm == (m.index('C') + 4) % 8)
            B.cl.append([B.A[L, x, c] if d == 1 else B.A[L, c, x]])
            B.cl.append([B.zp2[L, c] if quadf else -B.zp2[L, c]])
    if args.dump:
        with open(args.dump, 'w') as f:
            f.write(f'p cnf {B.nv} {len(B.cl)}\n')
            for cl in B.cl: f.write(' '.join(map(str, cl)) + ' 0\n')
        print('dumped', B.nv, len(B.cl)); return
    log = open(os.path.join(args.out, 'log.jsonl'), 'a')
    def L(**kw):
        kw['t'] = round(time.time() - t0, 1); log.write(json.dumps(kw) + '\n'); log.flush()
    L(event='built', qpin=args.qpin, split=args.split, mask=args.mask, pins=args.pins, vars=B.nv, clauses=len(B.cl), quad=quad, target=args.target, no_extra=args.no_extra)
    sv = Solver(name=args.solver, bootstrap_with=B.cl)
    lazy = 0; result = 'UNKNOWN'; ncalls = 0
    while True:
        if time.time() - t0 > args.seconds: result = 'UNKNOWN'; break
        sv.conf_budget(args.chunk)
        r = sv.solve_limited()
        ncalls += 1
        if r is None:
            continue
        if r is False: result = 'UNSAT'; break
        Ms = {x for x in sv.get_model() if x > 0}
        vio = S.C.pair_violations(B, Ms)
        if vio:
            for v in vio:
                cl = S.C.violation_clause(B, v); B.cl.append(cl); sv.add_clause(cl)
            lazy += len(vio); L(event='lazy', total=lazy); continue
        a, word = Q.to_arr(B, Ms)
        pr = X.preds(a)
        chk = dict(T=a.T(), W=pr['W'], Lambda=N3.credit_state(a)['C'] // 2, class_ok=bool(N3.GB.class_check(a)[0]),
                   opt=bool(N3.opt_triples(a)), preds={k: v for k, v in pr.items() if k.startswith('c')},
                   nquad=sum(len(e) == 4 for e in a.events), gens=word)
        json.dump(chk, open(os.path.join(args.out, 'model.json'), 'w'), indent=1)
        L(event='MODEL', **{k: v for k, v in chk.items() if k != 'gens'})
        result = 'SAT'; break
    st = sv.accum_stats()
    summ = dict(result=result, seconds=round(time.time() - t0, 1), lazy=lazy, vars=B.nv, clauses=len(B.cl), quad=quad, stats=st)
    json.dump(summ, open(os.path.join(args.out, 'result.json'), 'w'))
    L(event='done', **{k: v for k, v in summ.items() if k != 'stats'}, conflicts=st.get('conflicts'))
    if result == 'UNSAT':
        with gzip.open(os.path.join(args.out, 'final.cnf.gz'), 'wt', compresslevel=3) as f:
            f.write(f'p cnf {B.nv} {len(B.cl)}\n')
            for cl in B.cl: f.write(' '.join(map(str, cl)) + ' 0\n')
    print(json.dumps(summ))

if __name__ == '__main__': main()

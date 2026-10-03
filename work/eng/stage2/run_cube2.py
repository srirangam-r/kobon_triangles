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
    ap.add_argument('--fullpin', action='store_true', help='every case-B ray C of P: the far kite corner T on H and both kite corners on the diagonal e are full six-sector triples (STAGE2_TASK6 s4, Delta=0), so the first segments of H beyond T, of e beyond both corners, and of T\'s other lines at T are doubly used')
    ap.add_argument('--beyond2', action='store_true', help='every case-B ray of P on line H: at least two distinct lines cross H beyond the far kite corner T (STAGE2_TASK6 s4, applies to single-B endpoints and the double-B star)')
    ap.add_argument('--vmult', action='store_true', help='every case-B ray of P on H: the first vertex V on H beyond the far kite corner T is multiple (STAGE2_TASK7 star pin)')
    ap.add_argument('--tnbr', action='store_true', help='every case-B ray of P on H: all first neighbours of the far corner T along its two non-H lines are multiple (kite corners A,F triple; exterior apices Y,Z multiple, STAGE2_TASK7 Pin 1)')
    ap.add_argument('--vtriple', action='store_true', help='with --vmult: V is not a quad, hence a triple (STAGE2_TASK8 s3)')
    ap.add_argument('--ttriple', action='store_true', help='with --tnbr: the four off-H neighbours of T (kite corners A,F and apices Y,Z) are triples (lead lemma, after STAGE2_TASK8 s3)')
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
    if args.fullpin:
        assert args.mask and args.pins
        Rl = range(18)
        def nxt(L, u, w, d):   # on line L, vertex L^w immediately follows L^u in direction d
            return B.A[L, u, w] if d == 1 else B.A[L, w, u]
        for mm in range(8):
            if args.mask[mm] != 'C': continue
            H, d = ray(mm); x = min(y for y in quad if y != H)
            for e in Rl:
                if e in quad: continue
                a1 = nxt(H, x, e, d)                                   # X = H^e is the case-B kite centre
                for t in Rl:
                    if t in (H, e) or t in quad: continue
                    a2 = nxt(H, e, t, d)                               # T = H^t, far kite corner
                    B.cl.append([-a1, -a2] + [nxt(H, t, v, d) for v in Rl if v not in (H, e, t)])
                    for v in Rl:
                        if v in (H, e, t): continue
                        B.cl.append([-a1, -a2, -nxt(H, t, v, d), S2.use2(H, t, v)])        # H beyond T
                        for dd in (1, -1):
                            B.cl.append([-a1, -a2, -nxt(t, H, v, dd), S2.use2(t, H, v)])  # T's line t, both rays
                for dd in (1, -1):                                      # kite corners on e: e^a next to X both ways
                    for a in Rl:
                        if a in (H, e): continue
                        b1 = nxt(e, H, a, dd)
                        B.cl.append([-a1, -b1] + [nxt(e, a, w, dd) for w in Rl if w not in (H, e, a)])
                        for w in Rl:
                            if w in (H, e, a): continue
                            B.cl.append([-a1, -b1, -nxt(e, a, w, dd), S2.use2(e, a, w)])
    if args.beyond2:
        assert args.mask and args.pins
        Rl = range(18)
        def nxt2(L, u, w, d):
            return B.A[L, u, w] if d == 1 else B.A[L, w, u]
        for mm in range(8):
            if args.mask[mm] != 'C': continue
            H, d = ray(mm); x = min(y for y in quad if y != H)
            for e in Rl:
                if e in quad: continue
                a1 = nxt2(H, x, e, d)
                for t in Rl:
                    if t in (H, e) or t in quad: continue
                    a2 = nxt2(H, e, t, d)
                    B.cl.append([-a1, -a2] + [nxt2(H, t, v, d) for v in Rl if v not in (H, e, t)])
                    for v in Rl:
                        if v in (H, e, t): continue
                        a3 = nxt2(H, t, v, d)
                        B.cl.append([-a1, -a2, -a3, B.zp[H, v]] + [nxt2(H, v, w, d) for w in Rl if w not in (H, e, t, v)])
    if args.vmult:
        assert args.mask and args.pins
        Rl = range(18)
        def nxt3(L, u, w, d):
            return B.A[L, u, w] if d == 1 else B.A[L, w, u]
        for mm in range(8):
            if args.mask[mm] != 'C': continue
            H, d = ray(mm); x = min(y for y in quad if y != H)
            for e in Rl:
                if e in quad: continue
                a1 = nxt3(H, x, e, d)
                for t in Rl:
                    if t in (H, e) or t in quad: continue
                    a2 = nxt3(H, e, t, d)
                    for v in Rl:
                        if v in (H, e, t): continue
                        B.cl.append([-a1, -a2, -nxt3(H, t, v, d), B.zp[H, v]])
                        if args.vtriple: B.cl.append([-a1, -a2, -nxt3(H, t, v, d), -B.zp2[H, v]])
    if args.tnbr:
        assert args.mask and args.pins
        Rl = range(18)
        def nxt4(L, u, w, d):
            return B.A[L, u, w] if d == 1 else B.A[L, w, u]
        for mm in range(8):
            if args.mask[mm] != 'C': continue
            H, d = ray(mm); x = min(y for y in quad if y != H)
            for e in Rl:
                if e in quad: continue
                a1 = nxt4(H, x, e, d)
                for t in Rl:
                    if t in (H, e) or t in quad: continue
                    a2 = nxt4(H, e, t, d)                     # T = H^t, t any line through T other than H
                    for dd in (1, -1):
                        for w in Rl:
                            if w in (H, t): continue
                            B.cl.append([-a1, -a2, -nxt4(t, H, w, dd), B.zp[t, w]])
                            if args.ttriple: B.cl.append([-a1, -a2, -nxt4(t, H, w, dd), -B.zp2[t, w]])
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
    L(event='built', ttriple=args.ttriple, vtriple=args.vtriple, tnbr=args.tnbr, vmult=args.vmult, beyond2=args.beyond2, fullpin=args.fullpin, qpin=args.qpin, split=args.split, mask=args.mask, pins=args.pins, vars=B.nv, clauses=len(B.cl), quad=quad, target=args.target, no_extra=args.no_extra)
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

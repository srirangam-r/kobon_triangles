#!/usr/bin/env python3
"""Probe Q=Lambda-(Z-U/2)<7. A Q counterexample is not a Lambda counterexample."""
from pathlib import Path
from itertools import combinations
from collections import defaultdict
from functools import cmp_to_key
import argparse
import json
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'work/bbl/all8_work/pydeps'),
                str(ROOT / 'work/bbl/all8_work'), str(ROOT / 'work/bbl')]
import global_sat as G
import all8_block_check as BC
from pysat.solvers import Solver


def xor(B, a, b):
    false = -B.TRUE
    if a == false:
        return b
    if b == false:
        return a
    if a == b:
        return false
    v = B.new()
    B.cl.extend([[-a, -b, -v], [a, b, -v], [a, -b, v], [-a, b, v]])
    return v


def maj(B, a, b, c):
    if a == -B.TRUE:
        return B.AND([b, c])
    if b == -B.TRUE:
        return B.AND([a, c])
    if c == -B.TRUE:
        return B.AND([a, b])
    v = B.new()
    B.cl.extend([[-a, -b, v], [-a, -c, v], [-b, -c, v],
                 [a, b, -v], [a, c, -v], [b, c, -v]])
    return v


def add(B, u, v):
    false = -B.TRUE
    out = []
    carry = false
    for i in range(max(len(u), len(v))):
        a = u[i] if i < len(u) else false
        b = v[i] if i < len(v) else false
        out.append(xor(B, xor(B, a, b), carry))
        carry = maj(B, a, b, carry)
    if carry != false:
        out.append(carry)
    return out


def weighted_atmost(B, terms, bound):
    vectors = []
    offset = 0
    for lit, w in terms:
        if not w:
            continue
        if w < 0:
            lit, w = -lit, -w
            offset += w
        vectors.append([lit if (w >> i) & 1 else -B.TRUE
                        for i in range(w.bit_length())])
    limit = bound + offset
    if limit < 0:
        B.cl.append([])
        return
    while len(vectors) > 1:
        vectors = [add(B, vectors[i], vectors[i + 1])
                   if i + 1 < len(vectors) else vectors[i]
                   for i in range(0, len(vectors), 2)]
    bits = vectors[0] if vectors else []
    if limit >= (1 << len(bits)) - 1:
        return
    eq = B.TRUE
    for i in reversed(range(len(bits))):
        if not (limit >> i) & 1:
            B.cl.append([-eq, -bits[i]])
        eq = B.AND([eq, bits[i] if (limit >> i) & 1 else -bits[i]])


def q_terms(B):
    C = G.C
    R = list(range(B.K))
    groups = defaultdict(list)
    for t in B.trip:
        exact = B.AND([B.z[t], -B.zp2[t[0], t[1]]])
        ring = C.triple_ring(B, t)
        for i in range(6):
            groups['N'].append(B.AND([exact, -B.AND([ring[i - 1], ring[i]])]))
    for q in combinations(R, 4):
        conc = B.AND([B.z[C.P.key3(*t)] for t in combinations(q, 3)])
        ring = C.quad_ring(B, q)
        groups['quad'].append(conc)
        groups['A'].append(B.AND([conc] + ring))
    for p, q in combinations(R, 2):
        simple = -B.zp[p, q]
        pp, qp, mm, pq = [B.S[p, q, k] for k in ['pp', 'qp', 'mm', 'pq']]
        ring = [pp, qp, mm, pq]
        full = B.AND(ring)
        three = B.OR([B.AND(list(t)) for t in combinations(ring, 3)])
        groups['K'].append(B.AND([simple, full]))
        groups['H'].append(B.AND([simple, three, -full]))
        for axis, oth, plus in [(p, q, [pp, pq]), (q, p, [pp, qp])]:
            minus = [qp, mm] if axis == p else [mm, pq]
            first = B.AND([B.before(axis, oth, r) for r in R if r not in (p, q)])
            last = B.AND([B.before(axis, r, oth) for r in R if r not in (p, q)])
            groups['I'].append(B.AND([simple, first] + plus))
            groups['I'].append(B.AND([simple, last] + minus))
    weights = dict(N=1, quad=10, A=-2, K=-4, H=-2, I=-1)
    terms = [(lit, weights[name]) for name, lits in groups.items() for lit in lits]
    return groups, terms


def to_arr(B, Ms):
    """Convert the model's weak crossing orders to an actual wiring word."""
    pairs = list(combinations(range(B.K), 2))
    index = {p: i for i, p in enumerate(pairs)}
    dsu = BC.GB.DSU(len(pairs))
    for t in B.trip:
        if B.z[t] in Ms:
            ps = [index[p] for p in combinations(t, 2)]
            dsu.join(ps[0], ps[1])
            dsu.join(ps[0], ps[2])
    groups = defaultdict(set)
    for p in pairs:
        groups[dsu.find(index[p])].update(p)
    events = list(groups.values())
    graph = defaultdict(set)
    indeg = [0] * len(events)
    for L in range(B.K):
        ev = [i for i, e in enumerate(events) if L in e]
        def cmp(i, j):
            a = min(events[i] - {L})
            b = min(events[j] - {L})
            if a == b:
                raise ValueError('distinct events share a line pair')
            return -1 if B.before(L, a, b) in Ms else 1
        ev.sort(key=cmp_to_key(cmp))
        for i, j in zip(ev, ev[1:]):
            if j not in graph[i]:
                graph[i].add(j)
                indeg[j] += 1
    tracks = list(range(B.K))
    done = set()
    tokens = []
    while len(done) < len(events):
        picked = None
        for i, e in enumerate(events):
            if i in done or indeg[i]:
                continue
            pos = sorted(tracks.index(L) for L in e)
            if pos != list(range(pos[0], pos[0] + len(pos))):
                continue
            picked = i, pos
            break
        if picked is None:
            raise ValueError('model does not admit a wiring sweep')
        i, pos = picked
        g, size = pos[0], len(pos)
        tokens.append(str(g) + '*' * (size - 2))
        tracks[g:g + size] = reversed(tracks[g:g + size])
        done.add(i)
        for j in graph[i]:
            indeg[j] -= 1
    gens = ' '.join(tokens)
    return BC.GB.Arr(gens, B.K), gens


def adder_test():
    import random
    rng = random.Random(8839)
    checked = 0
    for n in range(1, 8):
        for _ in range(6):
            B = G.C.P.Base(2)
            xs = [B.new() for i in range(n)]
            weights = [rng.randint(-5, 5) for i in range(n)]
            bound = rng.randint(-6, 6)
            weighted_atmost(B, list(zip(xs, weights)), bound)
            with Solver(name='glucose4', bootstrap_with=B.cl) as s:
                for mask in range(1 << n):
                    value = sum(w for i, w in enumerate(weights) if mask >> i & 1)
                    res = s.solve(assumptions=[x if mask >> i & 1 else -x
                                               for i, x in enumerate(xs)])
                    assert res == (value <= bound)
                    checked += 1
    print('Weighted-adder exhaustive assignment checks:', checked, '; failures=0', flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=18)
    ap.add_argument('--bound', type=int, default=13, help='upper bound on 2Q')
    ap.add_argument('--seconds', type=int, default=300)
    ap.add_argument('--out', default=str(ROOT / 'work/bbl/all8_work/q18'))
    ap.add_argument('--self-test', action='store_true')
    ap.add_argument('--validate', action='store_true')
    args = ap.parse_args()
    if args.self_test:
        adder_test()
        return
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    known = None
    if args.validate:
        # Use the independently constructed exact witness, obtaining its word by sweep.
        from lines2gens import to_gens
        from fractions import Fraction as F
        ls = [(0,1,0),(1,0,0),(1,1,-6),(1,-1,0),(1,2,-6),(2,1,-6),
              (4,-5,2),(-3,6,214),(15,12,4),(-6,7,-222)]
        ls += [(7+i,1,1000000+101*i**3) for i in range(8)]
        known, _ = to_gens([(F(a), F(b)-F(a,37), F(c)) for a,b,c in ls])
    B = G.build(args.n, None, known)
    groups, terms = q_terms(B)
    weighted_atmost(B, terms, args.bound)
    print(json.dumps(dict(event='built', n=args.n, bound=args.bound,
                          variables=B.nv, clauses=len(B.cl))), flush=True)
    lazy = 0
    with Solver(name='glucose4', bootstrap_with=B.cl) as sv:
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
                result = 'UNSAT_UNCERTIFIED'
                break
            Ms = {x for x in sv.get_model() if x > 0}
            vio = G.C.pair_violations(B, Ms)
            if vio:
                for v in vio:
                    cl = G.C.violation_clause(B, v)
                    sv.add_clause(cl)
                    B.cl.append(cl)
                lazy += len(vio)
                print(json.dumps(dict(event='lazy', total=lazy)), flush=True)
                continue
            a, gens = to_arr(B, Ms)
            good, _ = BC.GB.class_check(a)
            assert good
            assert a.T() == sum(lit in Ms for lit in B.tri.values())
            dec = BC.decomposition(a, BC.block_partition(a))
            computed = {name: sum(lit in Ms for lit in lits) for name, lits in groups.items()}
            q2 = computed['N'] + 10*computed['quad'] - 2*computed['A'] - 4*computed['K'] - 2*computed['H'] - computed['I']
            assert q2 == dec['Q2'] and q2 <= args.bound
            evidence = dict(n=args.n, gens=gens, T=a.T(), Q2=q2, decomposition=dec,
                            counted=computed)
            (out / 'witness.json').write_text(json.dumps(evidence, indent=2))
            print(json.dumps(dict(event='verified_model', **evidence)), flush=True)
            result = 'SAT_VERIFIED'
            break
        summary = dict(result=result, seconds=time.time()-t0, n=args.n,
                       bound=args.bound, lazy_clauses=lazy, statistics=sv.accum_stats())
    (out / 'result.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()

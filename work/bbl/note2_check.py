#!/usr/bin/env python3
"""Exact checks for ALL8_NOTE2.md; no claim to have proved Lambda>=7."""
from pathlib import Path
from collections import Counter, defaultdict
from fractions import Fraction as F
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'work/bbl'), str(ROOT / 'work/eng/pert')]
import all8_block_check as BC
import all8_boundary_check as GB
from arr import rays, far_end
from lines2gens import transform, to_gens
from pert import words, faces


def edge(a, p, q):
    common = a.events[p] & a.events[q]
    assert len(common) == 1
    L = next(iter(common))
    i, j = a.pos[L][p], a.pos[L][q]
    assert abs(i-j) == 1
    return L, min(i, j)


def tri_vertices(a, f):
    out = {p for L, e, _ in f for p in a.rows[L][e:e+2]}
    assert len(out) == 3
    return out


def local_payments(a):
    records = BC.block_partition(a)
    at = defaultdict(list)
    for r in records:
        at[r['far']].append(r)
    tf = defaultdict(list)
    for f in a.tris:
        vertices = tri_vertices(a, f)
        for L, e, _ in f:
            tf[L, e].append(vertices)
    spent = {}
    counts = Counter()

    def spend(credit, source):
        P, seg = credit
        assert len(a.events[P]) >= 3
        assert len(a.t[seg[0]][seg[1]]) == 1
        assert P in a.rows[seg[0]][seg[1]:seg[1]+2]
        assert credit not in spent, (credit, source, spent.get(credit))
        spent[credit] = source

    def candidate(P, X, T):
        pt = edge(a, P, T)
        if len(a.t[pt[0]][pt[1]]) == 1:
            return P, pt
        assert len(a.t[pt[0]][pt[1]]) == 2
        assert len(a.events[T]) >= 3   # consecutive B's at the triple P forbidden
        tx = edge(a, T, X)
        assert len(a.t[tx[0]][tx[1]]) == 1
        return T, tx

    for r in records:
        P, X = r['point'], r['far']
        if len(a.events[P]) != 3:
            continue
        fs = tf[edge(a, P, X)]
        assert len(fs) == 2
        if r['kind'] in ('U', 'I'):
            counts[r['kind'] + '_T'] += 1
            for f in fs:
                (T,) = f - {P, X}
                spend(candidate(P, X, T), (r['kind'], P, X, T))
        elif len(at[X]) == 2:
            counts['H_T'] += 1
            (Q,) = {s['point'] for s in at[X]} - {P}
            (f,) = [f for f in fs if Q not in f]
            (T,) = f - {P, X}
            spend(candidate(P, X, T), ('H', P, X, T))

    for X, rr in at.items():
        if len(rr) != 4:
            continue
        corners = [far_end(a, X, ray) for ray in rays(a, X)]
        assert all(len(a.events[p]) >= 3 for p in corners)
        q = sum(len(a.events[p]) == 4 for p in corners)
        if q:
            counts['K_mixed'] += 1
            counts[f'K_q{q}'] += 1
            continue
        counts['K_0'] += 1
        sides = [edge(a, corners[i], corners[(i+1)%4]) for i in range(4)]
        use = [len(a.t[L][e]) for L, e in sides]
        assert not (use[0] == use[2] == 2)
        assert not (use[1] == use[3] == 2)
        singles = [i for i, k in enumerate(use) if k == 1]
        assert len(singles) >= 2
        for i in singles[:2]:
            spend((corners[i], sides[i]), ('K0', X, i))
            spend((corners[(i+1)%4], sides[i]), ('K0', X, i))

    costs, ring, comps, lam = GB.analyse(a)
    counts['C_pure'] = pure_line_components(a, ring, records)
    ntotal = sum(s.count('N') for s in ring.values())
    claimed = counts['H_T'] + 2*(counts['U_T']+counts['I_T']) + 4*counts['K_0']
    assert len(spent) == claimed
    assert ntotal >= claimed
    counts['N_total'] = ntotal
    counts['N_star'] = ntotal - claimed
    kite_at = Counter(r['point'] for r in records if len(at[r['far']]) == 4)
    counts['S_4'] = 0
    for P, s in ring.items():
        if len(a.events[P]) == 4:
            slack = 8 - s.count('B') - kite_at[P]
            assert slack >= 0
            counts['S_4'] += slack
    counts['U_4'] = sum(r['kind']=='U' and len(a.events[r['point']])==4
                        for r in records)
    U = sum(r['kind']=='U' for r in records)
    R2 = 2*a.Z() - U
    assert R2 >= 0
    typed = (R2 + counts['N_star'] + 2*counts['U_T'] + counts['I_T'] +
             counts['U_4'] + counts['S_4'] + 2*counts['K_q3'] +
             4*counts['K_q4'] - 2*counts['K_q1'])
    assert typed == 2*lam
    dec = BC.decomposition(a, records)
    if dec is not None:
        H4 = sum(r['kind'] == 'M' and len(a.events[r['point']]) == 4 and
                 len(at[r['far']]) == 2 for r in records)
        I4 = sum(r['kind'] == 'I' and len(a.events[r['point']]) == 4 for r in records)
        rhs = (dec['residual2'] + counts['N_star'] + 2*counts['U_T'] +
               counts['I_T'] + 8*(dec['A']+dec['J']) -
               4*counts['K_mixed'] - H4 - I4)
        assert rhs == 2*lam, (rhs, 2*lam)
    return counts


def pure_line_components(a, ring, records):
    mult = list(ring)
    idx = {p:i for i,p in enumerate(mult)}
    dsu = GB.DSU(len(mult))
    for row in a.rows:
        pts = [p for p in row if p in idx]
        for p in pts[1:]:
            dsu.join(idx[pts[0]], idx[p])
    comps = defaultdict(set)
    for p in mult:
        comps[dsu.find(idx[p])].add(p)
    count = 0
    for K in comps.values():
        if any(len(a.events[p]) != 3 for p in K):
            continue
        rr = [r for r in records if r['point'] in K]
        n = sum(ring[p].count('N') for p in K)
        ui = sum(r['kind'] in ('U','I') for r in rr)
        assert n - len(rr) >= ui
        count += 1
    return count


def perfect_star():
    gens = ('5 6 7 8 5 6 7 5 6 5 9 14 10 8 0 1 2 3 0 1 2 0 1 0 4 5 '
            '6* 8* 10* 12* 14* 16 11 3 4* 6* 8** 11** 14* 7 10 13 '
            '2* 4** 7** 10** 13* 3 6 9 1* 3** 6** 9* 11* 13 5 '
            '0 1* 3* 5* 7* 9* 11 12 2 6 8 7 0* 3 4 5 6 3 4 5 3 4 3')
    a = GB.Arr(gens,18)
    good, _ = GB.class_check(a)
    assert good
    p = 44
    c, ring, comps, lam = GB.analyse(a)
    first = [far_end(a,p,r) for r in rays(a,p)]
    multi = [v for v in first if len(a.events[v])>=3]
    rr = [r for r in BC.block_partition(a) if r['point']==p]
    assert ring[p]=='RBRBRBRB'
    assert len(rr)==4 and all(r['kind']=='M' and
                             all(GB.tri_sectors(a,r['far'])) for r in rr)
    assert all(ring[v].count('N')==0 for v in multi)
    assert (a.T(),a.Z(),lam)==(74,34,66)
    return dict(n=18,T=a.T(),Z=a.Z(),Lambda=lam,structural_class=good,
                P=p,ring=ring[p],multiple_first=multi,touch_at_P=0,
                first_multiple_N=0,gens=gens)


def closed_star_witness():
    a = GB.witness()
    costs, ring, _, lam = GB.analyse(a)
    assert len(ring)==4 and sum(costs.values())==6
    (P,) = [p for p in ring if len(a.events[p])==4]
    rr = BC.block_partition(a)
    pb = [r for r in rr if r['point']==P]
    assert len(pb)==5 and all(r['kind']!='M' for r in pb)
    for Q in ring:
        if Q==P:
            continue
        (r,) = [r for r in rr if r['point']==Q]
        L,d = rays(a,Q)[r['ray']]
        assert P in a.rows[L]
        assert (a.pos[L][P]-a.pos[L][Q])*d<0
        assert ring[Q].count('N')==4
    h = BC.pencil_touch(a,P,rr,check_all_witnesses=True)
    assert h==2
    return dict(component_cost=6,pencil_h=h,proven_Lambda_lower=8,actual_Lambda=lam)


def triple_perturbation():
    opts = [faces(3, w) for w in words(3)]
    out = []
    for mask in range(64):
        bits = [(mask >> i) & 1 for i in range(6)]
        delta = max(t-sum(bits[i] for i in range(6) if extra[i])
                    for extra, t, _ in opts)
        irreducible = sum(bits[::2]) >= 2 and sum(bits[1::2]) >= 2
        assert (delta < 0) == irreducible
        if irreducible:
            out.append(''.join(map(str,bits)))
    return opts, out


def six_line_kite():
    ls = [(1,0,-1),(1,0,1),(0,1,-1),(0,1,1),(1,1,0),(1,-1,0)]
    ls = transform(ls, F(1,97), F(1,89))
    ls = [(a,b-a/F(37),c) for a,b,c in ls]
    gens, _ = to_gens(ls)
    return GB.Arr(gens,6), gens


def main():
    opts, irreducible = triple_perturbation()
    print('Triple perturbations:', opts)
    print('Irreducible triple words:', irreducible)
    print('Triple sector-word checks: 64; failures=0')
    print('Closed-star witness:', closed_star_witness())
    print('Perfect-star counterexample:', perfect_star())
    k, kg = six_line_kite()
    kc = local_payments(k)
    print('Six-line triple-corner kite:', dict(n=6, gens=kg, T=k.T(), Z=k.Z(),
                                              Lambda=24-3*k.T(), counts=dict(kc)))
    counts = Counter()
    arrangements = points = all8 = 0
    inputs = [GB.witness()]
    for name in sys.argv[1:]:
        for row in Path(name).open():
            d=json.loads(row)
            inputs.append(GB.Arr(d['gens'],d.get('n')))
    for a in inputs:
        if max(map(len,a.events)) > 4:
            continue
        c = local_payments(a)
        counts.update(c)
        records = BC.block_partition(a)
        for p, event in enumerate(a.events):
            if len(event)<3:
                continue
            if BC.pencil_touch(a,p,records) is not None:
                points += 1
                all8 += int(len(event)==4 and all(GB.tri_sectors(a,p)))
        arrangements += 1
    print('Payment checks:', arrangements, 'arrangements; failures=0')
    print('Pencil-touch checks:', points, 'points;', all8, 'all-8 points; failures=0')
    print('Payment totals:', dict(sorted(counts.items())))


if __name__ == '__main__':
    main()

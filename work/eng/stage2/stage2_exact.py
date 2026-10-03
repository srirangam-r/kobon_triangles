"""Exact (arrangement-based) evaluation of the stage-2 constraints c2..c9 on a wiring word.
Independent of the SAT encoding; uses work/t3/arr.py and the bbl helpers. Each function returns True iff the
arrangement SATISFIES the constraint."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT/'work/bbl'), str(ROOT/'work/t3')]
import note3_check as N3
import note2_check as NC
from arr import Arr, rays, far_end, blocks, first_seg
BC, GB = NC.BC, NC.GB


def kites(a):
    out = []
    for X, e in enumerate(a.events):
        if len(e) == 2 and all(GB.tri_sectors(a, X)):
            cs = [far_end(a, X, r) for r in rays(a, X)]
            assert None not in cs
            q = sum(len(a.events[p]) == 4 for p in cs)
            caps = [NC.edge(a, u, v) for u, v in zip(cs, cs[1:]+cs[:1])]
            out.append((X, cs, q, caps))
    return out


def single(a, e):
    return len(a.t[e[0]][e[1]]) == 1


def preds(a):
    r = {}
    recs = BC.block_partition(a)
    r['c2'] = not any(x['kind'] == 'U' for x in recs)
    ks = kites(a)
    r['c3'] = not any(q >= 3 for _, _, q, _ in ks)
    ok = True
    for P, e in enumerate(a.events):
        if len(e) != 4:
            continue
        for k, cap in blocks(a, P):
            X = far_end(a, P, rays(a, P)[k])
            if not (len(a.events[X]) == 2 and all(GB.tri_sectors(a, X))):
                ok = False
    r['c4'] = ok
    ok = True
    for L, row in enumerate(a.rows):
        for ei, t in enumerate(a.t[L]):
            if not t and any(len(a.events[v]) >= 3 for v in row[ei:ei+2]):
                ok = False
    r['c5'] = ok
    r['c6'] = all(not single(a, e) for _, _, q, caps in ks if q >= 2 for e in caps)
    ok = True
    for f in a.tris:
        if all(len(a.events[v]) >= 3 for v in NC.tri_vertices(a, f)):
            if not all(len(a.t[L][e]) == 2 for L, e, _ in f):
                ok = False
    r['c7'] = ok
    r['c8'] = all(sum(single(a, e) for e in caps) == 2 for _, _, q, caps in ks if q == 0)
    r['c9'] = all(sum(single(a, e) for e in caps) <= 1 for _, _, q, caps in ks if q == 1)
    r['T'] = a.T()
    r['W'] = N3.credit_state(a)['W'] if True else None
    return r


def quad_dkc(a):
    """for each 4-fold point P: (D_P, k_P, c_B(P)) computed directly from the arrangement"""
    out = {}
    kt = {X: (cs, q, caps) for X, cs, q, caps in kites(a)}
    for P, e in enumerate(a.events):
        if len(e) != 4:
            continue
        D = len(blocks(a, P))
        k = cB = 0
        for r in rays(a, P):
            X = far_end(a, P, r)
            if X is not None and X in kt:
                k += 1
                cs, q, caps = kt[X]
                if q == 1 and not any(single(a, ed) for ed in caps):
                    cB += 1
        out[P] = (D, k, cB)
    return out

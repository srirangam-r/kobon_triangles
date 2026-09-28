"""Empirical checks of the lemmas used in the three-triple-point argument (notes.md).

Run: python3 lemmas.py <series>...   (gallery series names, e.g. 18 16 20 18-4)
Skips arrangements with 4-fold points or parallel pairs.
"""
import glob, sys, collections
sys.path.insert(0, '.')
from arr import *

R = '../../tools/external/kobon-solutions/gallery/data'


def kappa(a):
    """touches per line: number of (unused segment, simple endpoint) pairs whose other line is L"""
    k = collections.Counter()
    ztr = 0
    for (L, e) in unused(a):
        for X in seg_ends(a, L, e):
            if a.is_simple(X):
                k[a.other(X, L)] += 1
            else:
                ztr += 1
    return k, ztr


def point_info(a, P):
    rs = rays(a, P)
    bl = blocks(a, P)
    kind = 'b%d' % len(bl)
    axis = None
    bent_to = None
    if len(bl) == 2:
        (k1, c1), (k2, c2) = bl
        if (k1 - k2) % 6 == 3:
            kind = 'X'
            axis = rs[k1][0]
        else:
            kind = 'V'
            # shared side ray
            sh = [j for j in range(6) if (j - k1) % 6 in (1, 5) and (j - k2) % 6 in (1, 5)]
            assert len(sh) == 1, (k1, k2)
            bent_to = far_end(a, P, rs[sh[0]])
    return dict(rays=rs, blocks=bl, kind=kind, axis=axis, bent_to=bent_to)


def check(a, stats, fname):
    n = a.n
    T = a.triples
    info = {P: point_info(a, P) for P in T}
    trip_lines = set().union(*[a.events[P] for P in T]) if T else set()
    caps = collections.defaultdict(list)
    for P in T:
        for k, c in info[P]['blocks']:
            caps[c].append(P)
    # 1. L1
    for L in range(n):
        for e, s in enumerate(a.t[L]):
            if len(s) == 2:
                X, Y = seg_ends(a, L, e)
                if a.is_simple(X) and a.is_simple(Y):
                    stats['L1 FAIL'] += 1
    kap, ztr = kappa(a)
    assert 2 * a.Z() == sum(kap.values()) + ztr
    # 2. blocks <= 2 unless enough triple side vertices
    for P in T:
        if len(info[P]['blocks']) > 2:
            stats['3 blocks'] += 1
    # 3. Lemma A
    credA = 0
    killed = 0
    for P in T:
        I = info[P]
        if I['kind'] != 'X':
            continue
        ax = I['axis']
        p = a.pos[ax][P]
        rs = I['rays']
        got = 0
        for (k, cap) in I['blocks']:
            d = rs[k][1]
            Xc = a.rows[ax][p + d]          # cap point
            e = p + d if d == +1 else p - 2  # segment beyond the cap point
            if not (0 <= e < len(a.t[ax])):
                stats['A side unbounded'] += 1
                continue
            if not a.t[ax][e]:
                got += 1
                stats['A zero'] += 1
                # touched at Xc by cap
                assert a.other(Xc, ax) == cap
            else:
                # must be mutual pair: apex V_s triple on cap, and ax caps a block at V_s with middle [V_s, Xc]
                ok = False
                ic = a.pos[cap][Xc]
                for j in (ic - 1, ic + 1):
                    if 0 <= j < len(a.rows[cap]):
                        V = a.rows[cap][j]
                        if len(a.events[V]) == 3 and P != V:
                            # does V have a block with middle toward Xc along cap, capped by ax?
                            for (kk, cc) in info[V]['blocks']:
                                if info[V]['rays'][kk][0] == cap and far_end(a, V, info[V]['rays'][kk]) == Xc and cc == ax:
                                    ok = True
                stats['A nonzero mutual' if ok else 'A nonzero FAIL'] += 1
        if got == 0:
            killed += 1
            if not any(c in trip_lines for _, c in I['blocks']):
                stats['killed without triple cap FAIL'] += 1
        credA += got
    # 4. bridge principle
    beta = 0
    for L in trip_lines:
        ps = sorted((a.pos[L][P], P) for P in T if L in a.events[P])
        for (i, P), (j, Q) in zip(ps, ps[1:]):
            if j == i + 1:
                e = i
                if len(a.t[L][e]) == 2:
                    beta += 1
                    for (U, W) in ((P, Q), (Q, P)):
                        if len(info[U]['blocks']) == 2:
                            if info[U]['kind'] == 'V' and info[U]['bent_to'] == W:
                                stats['bridge at 2-block pt: V toward'] += 1
                            else:
                                # triangle face U W R ?
                                face = any(set(t_) for t_ in [])
                                tri_face = False
                                for Rr in T:
                                    if Rr in (U, W):
                                        continue
                                    lines3 = [a.events[U] & a.events[W], a.events[U] & a.events[Rr], a.events[W] & a.events[Rr]]
                                    if all(len(s) == 1 for s in lines3):
                                        tri_face = True
                                stats['bridge at 2-block pt: triangle-face' if tri_face else 'bridge principle FAIL'] += 1
    # 5. type V caps
    for P in T:
        I = info[P]
        if I['kind'] == 'V':
            Q = I['bent_to']
            capsP = {c for _, c in I['blocks']}
            if not (len(a.events[Q]) == 3 and capsP <= a.events[Q]):
                stats['V caps FAIL'] += 1
            else:
                stats['V ok'] += 1
    # 6. clean lines
    clean = [L for L in range(n) if L not in trip_lines and L not in caps]
    for L in clean:
        stats['clean ok' if kap[L] >= 1 else 'clean FAIL'] += 1
    # 7. valid axes without other triple points
    va = 0
    for P in T:
        ax = info[P]['axis']
        if ax is None:
            continue
        others = [Q for Q in T if Q != P and ax in a.events[Q]]
        if others or ax in caps:
            continue
        stats['valid axis ok' if kap[ax] >= 1 else 'valid axis FAIL'] += 1
        va += 1
    # 8. chain
    lhs = 2 * a.Z()
    rhs = len(clean) + credA
    stats['chain ok' if lhs >= rhs else 'chain FAIL'] += 1
    return dict(clean=len(clean), credA=credA, killed=killed, beta=beta)


if __name__ == '__main__':
    stats = collections.Counter()
    for series in sys.argv[1:]:
        for f in sorted(glob.glob(f'{R}/{series}/*.json')):
            a = load(f)
            if any(len(ev) > 3 for ev in a.events):
                stats['skip 4fold'] += 1
                continue
            if len(a.events) != a.n * (a.n - 1) // 2 - 2 * len(a.triples):
                stats['skip parallel'] += 1
                continue
            check(a, stats, f)
    for k, v in sorted(stats.items()):
        print(f'{v:7d}  {k}')

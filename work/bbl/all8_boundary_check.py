#!/usr/bin/env python3
"""Exact checks for ALL8_GB_NOTE.md; not a certificate excluding T=94.

Run from any directory. With no arguments, check the explicit 18-line witness.
With JSONL arguments, also check every multiplicity <=4 arrangement therein.
The Gauss--Bonnet identity is valid without the bad-word/pair restrictions.
"""
from pathlib import Path
from collections import Counter, defaultdict
from fractions import Fraction
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'work/t3'), str(ROOT / 'work/eng/comp'),
                str(ROOT / 'work/eng/lattice')]
from arr import Arr, rays, far_end
from comp_cost import analyse
from bad_comp import tri_sectors, canon
from lines2gens import to_gens


class DSU:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def join(self, x, y):
        self.p[self.find(x)] = self.find(y)


def normalized_surface(a):
    """Glue triangle sides, never identify separate fans just at a vertex."""
    corners = []
    sides = defaultdict(list)
    for f, tri in enumerate(a.tris):
        vertices = sorted({v for L, e, _ in tri
                           for v in (a.rows[L][e], a.rows[L][e + 1])})
        assert len(vertices) == 3
        loc = {v: len(corners) + i for i, v in enumerate(vertices)}
        corners.extend(vertices)
        for L, e, _ in tri:
            u, v = a.rows[L][e:e + 2]
            sides[L, e].append((f, loc[u], loc[v]))
    vd = DSU(len(corners))
    fd = DSU(len(a.tris))
    for entries in sides.values():
        assert 1 <= len(entries) <= 2
        if len(entries) == 2:
            (f, u, v), (g, x, y) = entries
            assert corners[u] == corners[x] and corners[v] == corners[y]
            vd.join(u, x)
            vd.join(v, y)
            fd.join(f, g)
    V = len({vd.find(i) for i in range(len(corners))})
    E, T = len(sides), len(a.tris)
    chi = V - E + T
    components = len({fd.find(i) for i in range(T)})
    return chi, components


def stats(a):
    assert max(map(len, a.events), default=2) <= 4
    c, ring, comps, lam = analyse(a)
    chi, components = normalized_surface(a)
    full = 0
    A = 0
    s = Counter()
    # Twice the multiple-boundary terms, including vertices with no triangles.
    triple_boundary2 = quad_boundary2 = 0
    for p, event in enumerate(a.events):
        bits = tri_sectors(a, p)
        t, m = sum(bits), len(event)
        is_full = all(bits)
        full += int(is_full)
        if is_full:
            A += int(m == 4)
            continue
        runs = sum(bits[i] and not bits[i - 1] for i in range(len(bits)))
        if m == 3:
            triple_boundary2 += 6 + 7 * runs - 3 * t
        elif m == 4:
            quad_boundary2 += 16 + 7 * runs - 3 * t
        else:
            for i, bit in enumerate(bits):
                if not bit or bits[i - 1]:
                    continue
                k = 1
                while bits[(i + k) % 4]:
                    k += 1
                assert k in (1, 2, 3)
                s[k] += 1
    assert chi == a.T() - a.D() + full
    boundary2 = triple_boundary2 + quad_boundary2 + 4 * s[1] + s[2] - 2 * s[3]
    # 2 Lambda = 2Z - 12chi + 4A + 2 (remaining boundary terms).
    rhs2 = 2 * a.Z() - 12 * chi + 4 * A + boundary2
    assert 2 * lam == rhs2, (lam, rhs2)
    assert 2 * sum(c.values()) == -12 * chi + 4 * A + boundary2
    return dict(T=a.T(), Z=a.Z(), Lambda=lam, chi=chi,
                components=components, holes=components - chi,
                all8=A, s1=s[1], s2=s[2], s3=s[3],
                triple_boundary2=triple_boundary2, quad_boundary2=quad_boundary2,
                c=c, ring=ring, comps=comps)


def class_check(a):
    allowed = {tuple(x) for x in json.loads(
        (ROOT / 'work/eng/pert2/pair_PQ_all.json').read_text())['allowed']}
    if max(map(len, a.events), default=2) > 4:
        return False, []
    pairs = []
    for p, event in enumerate(a.events):
        if len(event) != 4:
            continue
        pb = tri_sectors(a, p)
        if canon(pb) not in {'11111111', '11111110'}:
            return False, pairs
        for i, ray in enumerate(rays(a, p)):
            q = far_end(a, p, ray)
            if q is None or len(a.events[q]) != 3:
                continue
            qb = tri_sectors(a, q)
            j = rays(a, q).index((ray[0], -ray[1]))
            key = min(
                (''.join(str(pb[(i + k) % 8]) for k in range(8)),
                 ''.join(str(qb[(j + k) % 6]) for k in range(6))),
                (''.join(str(pb[(i - 1 - k) % 8]) for k in range(8)),
                 ''.join(str(qb[(j - 1 - k) % 6]) for k in range(6))))
            pairs.append(key)
            if key not in allowed:
                return False, pairs
    return True, pairs


def witness():
    lines = [(0, 1, 0), (1, 0, 0), (1, 1, -6), (1, -1, 0),
             (1, 2, -6), (2, 1, -6), (4, -5, 2), (-3, 6, 214),
             (15, 12, 4), (-6, 7, -222)]
    lines += [(7 + i, 1, 1000000 + 101 * i ** 3) for i in range(8)]
    # Remove vertical lines by a shear, not by changing the infinity line.
    sheared = [(Fraction(x), Fraction(y) - Fraction(x, 37), Fraction(z))
               for x, y, z in lines]
    gens, _ = to_gens(sheared)
    return Arr(gens, 18)


def main():
    a = witness()
    out = stats(a)
    good, pairs = class_check(a)
    assert good and out['all8'] == 1
    assert (out['T'], out['Z'], out['Lambda']) == (29, 195, 201)
    assert len(out['comps']) == 1
    assert sum(out['c'].values()) == 6
    print('18-line witness: class=True, T=29, Z=195, Lambda=201, component cost=6')
    print('Pair patterns:', pairs)
    print('Surface:', {k: v for k, v in out.items() if k not in {'c', 'ring', 'comps'}})
    checked = skipped = inclass_all8 = 0
    for name in sys.argv[1:]:
        for number, line in enumerate(Path(name).open(), 1):
            d = json.loads(line)
            a = Arr(d['gens'], d.get('n'))
            if max(map(len, a.events), default=2) > 4:
                skipped += 1
                continue
            try:
                st = stats(a)
            except AssertionError as e:
                raise AssertionError(f'{name}:{number}: {e}') from e
            checked += 1
            if st['all8'] and class_check(a)[0]:
                inclass_all8 += 1
    if sys.argv[1:]:
        print(f'Gauss--Bonnet identity checks: {checked}; multiplicity>4 skipped: {skipped}; '
              f'in-class all8 records: {inclass_all8}')


if __name__ == '__main__':
    main()

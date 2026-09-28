"""A04 proof diagnostics, not a construction search or submission scorer.

Reuses round-1 exact geometry only to inspect block/cap incidences.
No candidate is ranked or selected. --profiles enumerates aggregate necessary
conditions, NOT arrangements or SAT certificates. Python standard library only.
"""
from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations, product
import json
import random

from a_struct import Arrangement, BENT_E4, FAR, random_arrangement


def gap_check(lines):
    a = Arrangement(lines)
    if any(len(s) > 3 for s in a.pts.values()):
        return None
    r = a.report()
    gaps, interrupted, bridges = set(), set(), set()
    for line, order in enumerate(a.order):
        triples = [p for p in order if p in a.mult]
        for p, q in zip(triples, triples[1:]):
            key = (line, p, q)
            gaps.add(key)
            lo, hi = a.pos[line][p], a.pos[line][q]
            if hi == lo + 1 and a.use[line, lo] == 2:
                bridges.add(key)
            if hi == lo + 2 and len(a.pts[order[lo + 1]]) == 2:
                interrupted.add(key)
    charges = Counter()
    centroids = 0
    for p, data in r['data'].items():
        rays = data['rays']
        centroids += data['b'] == 3
        for k, ray in enumerate(rays):
            if not ray['middle']:
                continue
            q, s = rays[(k - 1) % 6]['far'], rays[(k + 1) % 6]['far']
            if q not in a.mult or s not in a.mult:
                continue
            cap = ray['cap']
            q, s = sorted((q, s), key=a.pos[cap].__getitem__)
            key = (cap, q, s)
            assert key in interrupted
            assert a.order[cap][a.pos[cap][q] + 1] == ray['far']
            charges[key] += 1
    assert len(gaps) == r['sigma']
    assert len(bridges) == r['beta']
    assert max(charges.values(), default=0) <= 2
    assert 3 * centroids <= sum(charges.values()) <= 2 * len(charges)
    h = len(gaps - bridges)
    assert 3 * centroids <= 2 * h
    if centroids:
        assert len(gaps) >= 6
        if len(gaps) == 6:
            assert r['sum_c'] <= 1
    return {'cap_incidences': sum(charges.values()), 'centroids': centroids,
            'interrupted_gaps': len(charges), 'bridges': len(bridges)}


def graph_check():
    # All simple graphs with exactly 3 edges, after deleting isolated vertices.
    shapes = {
        'triangle': [(0, 1), (1, 2), (0, 2)],
        'star': [(0, 1), (0, 2), (0, 3)],
        'path': [(0, 1), (1, 2), (2, 3)],
        'two_plus_one': [(0, 1), (1, 2), (3, 4)],
        'matching': [(0, 1), (2, 3), (4, 5)],
    }
    checked = 0
    for name, edges in shapes.items():
        n = max(max(e) for e in edges) + 1
        g = {frozenset(e) for e in edges}
        isolated = 7 - n
        for mask in range(1, 8):
            h = {frozenset(edges[k]) for k in range(3) if mask & (1 << k)}
            nbr = [{next(iter(e - {i})) for e in h if i in e} for i in range(n)]
            # 0=blockless, 1=one block, 2=axis, 3=bent. No centroids at sigma=3.
            for ty in product(range(4), repeat=n):
                b = [min(x, 2) for x in ty]
                deficit = sum(2 - v for v in b)
                if deficit > 2:
                    continue
                valid = True
                for i, x in enumerate(ty):
                    deg = len(nbr[i])
                    if x == 2:
                        # Every axis bridge needs an all-multiple triangular face.
                        if any(not any(j != k and frozenset((j, k)) in g
                                       for k in nbr[i]) for j in nbr[i]):
                            valid = False
                    elif x == 3:
                        # Every bent point has a bridge partner with <=1 block.
                        if not any(ty[j] in (0, 1) for j in nbr[i]):
                            valid = False
                        if name != 'triangle':
                            # In a forest a bent point has exactly its partner edge.
                            if deg != 1 or ty[next(iter(nbr[i]))] not in (0, 1):
                                valid = False
                        elif deg not in (1, 2):
                            valid = False
                if name == 'triangle' and all(x == 2 for x in ty):
                    valid = False
                if name != 'triangle':
                    for i, x in enumerate(ty):
                        if x in (0, 1):
                            leaves = sum(ty[j] == 3 for j in nbr[i])
                            if leaves > (2 if x == 0 else 1):
                                valid = False
                if not valid:
                    continue
                for n0 in range(isolated + 1):
                    for n1 in range(isolated - n0 + 1):
                        d = deficit + 2 * n0 + n1
                        axes = isolated - n0 - n1
                        for z in range(3):
                            checked += 1
                            if len(h) - d >= 1 + z and 2 * z >= axes:
                                raise AssertionError((name, mask, ty, n0, n1, z))
    return checked


def profiles():
    for t, m in ((7, 17), (7, 16), (8, 18)):
        sigma = 3 * t - m
        for d in range(2 * t + 7 - m):
            for z in range(2 * t + 7 - m - d):
                for beta in range(t - 6 + z + d, sigma + 1):
                    for n0 in range(d // 2 + 1):
                        n1 = d - 2 * n0
                        n2 = t - n0 - n1
                        if n2 >= 0:
                            yield dict(t=t, m=m, C=0, Z=z, B=2*t-d,
                                       beta=beta, h=sigma-beta,
                                       n0=n0, n1=n1, n2=n2)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--selftest', type=int, default=0)
    p.add_argument('--profiles', action='store_true')
    args = p.parse_args()
    if args.profiles:
        for row in profiles():
            print(json.dumps(row, sort_keys=True))
    if args.selftest:
        totals = Counter()
        fixtures = [BENT_E4, BENT_E4 + FAR]
        # The three medians and sides of a triangle: a centroid with exactly
        # three outer triple points and six triple gaps. Exercises q=3,h=3.
        fixtures.append([(0, 1, 0), (1, 0, 0), (1, 1, -6),
                         (1, -1, 0), (1, 2, -6), (2, 1, -6)])
        rng = random.Random(20260928)
        for i in range(args.selftest + len(fixtures)):
            lines = fixtures[i] if i < len(fixtures) else random_arrangement(rng.choice([8, 9, 10, 11]), rng)
            result = gap_check(lines)
            if result is None:
                totals['skipped_higher_points'] += 1
                continue
            totals['arrangements'] += 1
            totals.update(result)
        states = graph_check()
        counts = Counter((r['t'], r['m']) for r in profiles())
        print(json.dumps({'geometry': dict(totals), 'abstract_states_checked': states,
                          'aggregate_profile_counts': {f't{t}_m{m}': v for (t, m), v in counts.items()},
                          'status': 'PASS'}, sort_keys=True))


if __name__ == '__main__':
    main()

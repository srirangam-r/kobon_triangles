#!/usr/bin/env python3
"""Check the block decomposition and pencil-touch lemma (not the open bound)."""
from pathlib import Path
from collections import Counter
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'work/bbl'), str(ROOT / 'work/t3')]
import all8_boundary_check as GB
from arr import blocks, first_seg, far_end, rays


def block_partition(a):
    records = []
    for p, event in enumerate(a.events):
        if len(event) < 3:
            continue
        for index, cap in blocks(a, p):
            ray = rays(a, p)[index]
            x = far_end(a, p, ray)
            beyond = first_seg(a, x, ray)
            kind = ('I' if beyond is None else
                    'U' if not a.t[beyond[0]][beyond[1]] else 'M')
            records.append(dict(point=p, ray=index, cap=cap, far=x,
                                kind=kind, beyond=beyond))
    return records


def decomposition(a, records):
    count = Counter(r['kind'] for r in records)
    K = H = 0
    for p, event in enumerate(a.events):
        if len(event) == 2:
            t = sum(GB.tri_sectors(a, p))
            K += int(t == 4)
            H += int(t == 3)
    assert count['M'] == 4 * K + 2 * H
    used = Counter(r['beyond'] for r in records if r['kind'] == 'U')
    assert max(used.values(), default=0) <= 2
    residual2 = 2 * a.Z() - count['U']
    assert residual2 >= 0
    costs, ring, comps, lam = GB.analyse(a)
    if any(len(e) == 4 and sum(GB.tri_sectors(a, p)) not in (7, 8)
           for p, e in enumerate(a.events)):
        return None
    nt = sum(s.count('N') for p, s in ring.items() if len(a.events[p]) == 3)
    A = sum(len(e) == 4 and all(GB.tri_sectors(a, p))
            for p, e in enumerate(a.events))
    J = sum(len(e) == 4 and sum(GB.tri_sectors(a, p)) == 7
            for p, e in enumerate(a.events))
    q2 = nt + 8 * A + 10 * J - 4 * K - 2 * H - count['I']
    assert residual2 + q2 == 2 * lam
    return dict(K=K, H=H, U=count['U'], I=count['I'],
                residual2=residual2, Q2=q2, Lambda=lam, A=A, J=J)


def pencil_touch(a, p, records, check_all_witnesses=False):
    m = len(a.events[p])
    rs = rays(a, p)
    rr = [r for r in records if r['point'] == p]
    nonmutual = {r['ray'] for r in rr if r['kind'] != 'M'}
    capset = {r['cap'] for r in rr if r['kind'] != 'M'}
    witnesses = set(range(a.n)) - set(a.events[p]) - capset
    if not witnesses:
        return None
    lower = min(sum((i + j) % (2 * m) in nonmutual for j in range(m))
                for i in range(2 * m))
    touches = {r['beyond'] for r in rr if r['kind'] == 'U'}
    assert len(touches) >= lower
    assert a.Z() >= lower
    end = {r['ray'] for r in rr if r['kind'] == 'I'}
    ws = sorted(witnesses) if check_all_witnesses else [min(witnesses)]
    for W in ws:
        half = set()
        for i, (L, direction) in enumerate(rs):
            v = next(v for v in a.rows[L] if W in a.events[v])
            if (a.pos[L][v] - a.pos[L][p]) * direction > 0:
                half.add(i)
        assert len(half) == m
        assert any(half == {(i + j) % (2 * m) for j in range(m)}
                   for i in range(2 * m))
        assert not half & end
        for i in half & nonmutual:
            r = next(r for r in rr if r['ray'] == i)
            assert r['kind'] == 'U'
    return lower


def check(a, counts):
    if max(map(len, a.events), default=2) > 4:
        counts['skipped'] += 1
        return
    rr = block_partition(a)
    dec = decomposition(a, rr)
    counts['decompositions'] += 1
    for p, event in enumerate(a.events):
        if len(event) < 3:
            continue
        low = pencil_touch(a, p, rr)
        if low is None:
            continue
        counts['points'] += 1
        counts['positive'] += int(low > 0)
        if len(event) == 4 and all(GB.tri_sectors(a, p)):
            counts['all8'] += 1
            counts['all8_positive'] += int(low > 0)
    return dec


def main():
    counts = Counter()
    w = GB.witness()
    dec = check(w, counts)
    assert dec == dict(K=0, H=0, U=6, I=2, residual2=384,
                       Q2=18, Lambda=201, A=1, J=0)
    print('Explicit 18-line witness:', dec)
    for name in sys.argv[1:]:
        for lineno, line in enumerate(Path(name).open(), 1):
            d = json.loads(line)
            a = GB.Arr(d['gens'], d.get('n'))
            try:
                check(a, counts)
            except AssertionError as e:
                raise AssertionError(f'{name}:{lineno}: {e}') from e
    print('Exact checks:', dict(counts), '; failures=0')


if __name__ == '__main__':
    main()

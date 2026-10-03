#!/usr/bin/env python3
"""Task 5 Stage 2: local zero-slack quadruple audits, no global exclusion.

Use Note 3's accepted reconstruction; do not invoke Note 4's secondary
geometry assertions. The tiny mask enumeration is exhaustive. Arrangement
checks are sample checks, never an arrangement-realizability certificate.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import note3_check as N3
from arr import Arr, far_end, rays


def masks():
    counts = Counter()
    for bits in range(256):
        B = {i for i in range(8) if bits >> i & 1}
        if B & {1, 2, 3}:
            continue
        if any(all((i + j) % 8 in B for j in range(3)) for i in range(8)):
            continue
        isolated = [i for i in B if not {(i-1) % 8, (i+1) % 8} & B]
        for km in range(1 << len(isolated)):
            K = {i for j, i in enumerate(isolated) if km >> j & 1}
            possible = [i for i in K if not {(i-2) % 8, (i+2) % 8} & B]
            for cm in range(1 << len(possible)):
                CB = {i for j, i in enumerate(possible) if cm >> j & 1}
                if len(CB) > 2:
                    continue
                if len(CB) == 2:
                    i, j = sorted(CB)
                    if (j-i) % 8 != 4:
                        continue
                slack = 8 - len(B) - len(K) - 2*len(CB)
                assert slack >= 0 and slack != 1
                if slack == 0:
                    assert B == K == CB == {0, 4}
                counts[slack] += 1
    assert counts == Counter({0: 1, 2: 9, 3: 9, 4: 21, 5: 19,
                              6: 15, 7: 5, 8: 1})
    return dict(configurations=sum(counts.values()),
                slack_counts=dict(sorted(counts.items())), failures=0)


def check(a):
    N3.word_valid(' '.join(a.gens.split()), a.n)
    class_ok, _ = N3.GB.class_check(a)
    if not class_ok:
        return Counter(skipped_outside_structural_class=1)
    z = N3.credit_state(a)
    at = defaultdict(list)
    for r in N3.BC.block_partition(a):
        at[r['far']].append(r)
    cb = defaultdict(list)
    for x, rr in at.items():
        if len(rr) != 4:
            continue
        corners = [far_end(a, x, ray) for ray in rays(a, x)]
        quad = [p for p in corners if len(a.events[p]) == 4]
        if len(quad) != 1:
            continue
        edges = [N3.NC.edge(a, p, q)
                 for p, q in zip(corners, corners[1:] + corners[:1])]
        if all(len(a.t[L][e]) == 2 for L, e in edges):
            p = quad[0]
            cb[p].append(next(i for i, ray in enumerate(rays(a, p))
                              if far_end(a, p, ray) == x))
    counts = Counter(arrangements=1, quadruples=len(z['Scorr']))
    for p, slack in z['Scorr'].items():
        sectors = N3.GB.tri_sectors(a, p)
        if sum(sectors) == 7:
            assert slack >= 2
            counts['seven_type_points'] += 1
        if slack == 0:
            assert all(sectors)
            counts['zero_slack_points'] += 1
        if len(cb[p]) == 2:
            i, j = cb[p]
            assert (j-i) % 8 == 4 and all(sectors)
            counts['double_case_B_points'] += 1
            for ray in rays(a, p):
                q = far_end(a, p, ray)
                if q is not None and len(a.events[q]) == 4:
                    assert z['Scorr'][q] >= 2
                    counts['double_case_B_quad_first_neighbours'] += 1
    if z['Scorr'] and not any(z['Scorr'].values()):
        counts['globally_zero_slack_quad_arrangements'] += 1
        if N3.opt_triples(a) and z['C'] == 2*z['paths']:
            counts['globally_zero_credit_all8_arrangements'] += 1
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='*')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    total = Counter(globally_zero_slack_quad_arrangements=0,
                    globally_zero_credit_all8_arrangements=0)
    for name in args.paths:
        for number, line in enumerate(Path(name).open(), 1):
            d = json.loads(line)
            if not d.get('gens'):
                continue
            a = Arr(d['gens'], d.get('n', 18))
            a.gens = d['gens']
            try:
                total.update(check(a))
            except AssertionError as error:
                raise AssertionError((name, number, error)) from error
    result = dict(mask_enumeration=masks(), sample_counts=dict(sorted(total.items())),
                  sample_failures=0,
                  limitation='No global zero-credit all-8 certificate or contradiction.')
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()

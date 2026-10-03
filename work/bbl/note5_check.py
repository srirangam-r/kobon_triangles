#!/usr/bin/env python3
"""Task 5 bookkeeping and local zero-credit geometry, using accepted helpers.

This does not prove B, O2Q, or the exclusion of a 94. Input metrics must be
complete outputs of tradeoff_check.py. New bounds are checked on all records;
claims needing structural/triple optimality are checked on eligible records.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import note3_check as N3
import note5_allocation as N5A
from arr import Arr, first_seg, far_end, rays


def use(a, e):
    return 0 if e is None else len(a.t[e[0]][e[1]])


def fork_inventory(a, records, at):
    """A triple with two simple block tips around one bridge.

    Require the two cap sides at the opposite multiple endpoint to be single.
    A proposed universal four-sector conclusion is tested, not assumed:
    extra lines through the opposite cap corners can close another sector.
"""
    forks = []
    by_side = {(r['point'], r['far']): r for r in records}
    by_edge = defaultdict(list)
    for f in a.tris:
        vs = N3.NC.tri_vertices(a, f)
        for L, e, _ in f:
            by_edge[L, e].append(vs)
    for q in a.triples:
        for ray in rays(a, q):
            e = first_seg(a, q, ray)
            p = far_end(a, q, ray)
            if use(a, e) != 2 or len(a.events[p]) < 3:
                continue
            apexes = [next(iter(vs - {p, q})) for vs in by_edge[e]]
            assert len(apexes) == 2
            if not all(a.is_simple(x) and (q, x) in by_side for x in apexes):
                continue
            if not all(use(a, N3.NC.edge(a, p, x)) == 1 for x in apexes):
                continue
            bits = N3.GB.tri_sectors(a, q)
            opposite = (ray[0], -ray[1])
            empty = first_seg(a, q, opposite)
            four_run = N3.GB.canon(bits) == '111100'
            if four_run:
                assert use(a, empty) == 0
            kinds = [by_side[q, x]['kind'] for x in apexes]
            for x, kind in zip(apexes, kinds):
                if kind == 'M' and four_run:
                    assert len(at[x]) == 2
                    other = next(r['point'] for r in at[x] if r['point'] != q)
                    central = N3.NC.edge(a, q, other)
                    assert use(a, central) == 1
            if kinds == ['I', 'I'] and a.n > 5:
                assert empty is not None
            forks.append(dict(q=q, p=p, tips=apexes, kinds=kinds,
                              opposite_ray=opposite, opposite_use=use(a, empty),
                              opposite_bounded=empty is not None,
                              four_run=four_run, sectors=bits))
    return forks


def geometry(a, m):
    records = N3.BC.block_partition(a)
    at = defaultdict(list)
    for r in records:
        at[r['far']].append(r)
    free = set(N5A.residual_tokens(a, records, at))
    assert len(free) == m['Delta_N']
    eligible = m['structural_class'] and m['triple_optimality']
    perfect = set(m['perfect_lines'])
    perfect_triples = {p for L in perfect for p in a.rows[L] if len(a.events[p]) == 3}
    forks = fork_inventory(a, records, at)
    kite_surplus = 0
    kite_free = set()
    h_tokens = set()
    kite_perfect = []
    for x, rr in at.items():
        if len(rr) == 2:
            p, q = [r['point'] for r in rr]
            e = N3.NC.edge(a, p, q)
            if use(a, e) == 1:
                h_tokens.update(((p, e), (q, e)))
        elif len(rr) == 4:
            cs = [far_end(a, x, r) for r in rays(a, x)]
            edges = [N3.NC.edge(a, p, q) for p, q in zip(cs, cs[1:] + cs[:1])]
            singles = sum(use(a, e) == 1 for e in edges)
            quads = sum(len(a.events[p]) == 4 for p in cs)
            paid_edges = 2 if quads == 0 else 1 if quads == 1 and singles else 0
            assert singles >= paid_edges
            kite_surplus += 2 * (singles - paid_edges)
            tokens = {(p, e) for e in edges if use(a, e) == 1
                      for p in a.rows[e[0]][e[1]:e[1]+2]}
            surplus_tokens = tokens & free
            assert len(surplus_tokens) == 2 * (singles - paid_edges)
            assert not kite_free & surplus_tokens
            kite_free |= surplus_tokens
            if eligible and any(e[0] in perfect for e in edges):
                assert singles >= 3
                assert 2 * (singles - paid_edges) >= 2
                kite_perfect.append(dict(centre=x, quads=quads, singles=singles))
    empty_tokens = set()
    for p, ev in enumerate(a.events):
        if len(ev) < 3:
            continue
        for ray in rays(a, p):
            e = first_seg(a, p, ray)
            if e is not None and use(a, e) == 0:
                empty_tokens.add((p, e))
    all_multiple = set()
    onefan = set()
    twofan_other = set()
    for f in a.tris:
        vs = N3.NC.tri_vertices(a, f)
        mult = [p for p in vs if len(a.events[p]) >= 3]
        simple = list(vs - set(mult))
        if len(mult) == 3:
            for L, e, _ in f:
                if use(a, (L, e)) == 1:
                    all_multiple.update((p, (L, e)) for p in a.rows[L][e:e+2])
        elif len(mult) == 2:
            (x,) = simple
            p, q = mult
            px, qx = N3.NC.edge(a, p, x), N3.NC.edge(a, q, x)
            if use(a, px) == use(a, qx) == 1:
                onefan.update(((p, px), (q, qx)))
                pq = N3.NC.edge(a, p, q)
                if use(a, pq) == 1:
                    onefan.update(((p, pq), (q, pq)))
            elif len(at[x]) == 1:
                (r,) = at[x]
                if r['kind'] in ('U', 'I'):
                    p = r['point']
                    (q,) = set(mult) - {p}
                    pq = N3.NC.edge(a, p, q)
                    if use(a, pq) == 1:
                        twofan_other.add((q, pq))
    groups = [empty_tokens, h_tokens, all_multiple, onefan, twofan_other, kite_free]
    all_selected = set()
    for tokens in groups:
        assert not all_selected & tokens
        assert tokens <= free
        all_selected |= tokens
    assert not all_selected & N3.KP.claimed_tokens(a)
    assert len(kite_free) == kite_surplus
    lower = len(all_selected)
    assert m['Delta_N'] >= lower
    ii_same_axis = 0
    for p in a.triples:
        rr = [r for r in records if r['point'] == p]
        for i, r in enumerate(rr):
            for s in rr[i+1:]:
                if r['kind'] == s['kind'] == 'I' and rays(a, p)[r['ray']][0] == rays(a, p)[s['ray']][0]:
                    assert a.n == 5
                    ii_same_axis += 1
    zero = eligible and m['E'] == 0
    return dict(forks=forks, perfect_kites=kite_perfect,
                perfect_triples=len(perfect_triples),
                empty_tokens=len(empty_tokens), H_tokens=len(h_tokens),
                all_multiple_tokens=len(all_multiple), onefan_tokens=len(onefan),
                twofan_other_tokens=len(twofan_other), kite_surplus=kite_surplus,
                residual_lower=lower, residual_slack=m['Delta_N']-lower,
                II_same_axis=ii_same_axis, zero_credit_eligible=zero)


def accounting(m):
    j = len(m['interior_lines'])
    q = len(set(m['interior_lines']) - set(m['interior_with_zero']))
    hz = j - q
    sigma = j - 18 + 2*m['pi']
    assert sigma >= 0
    dz = m['Delta'] - m['Delta_N']
    a = m['E'] - 2*m['U'] - m['Delta']
    assert min(dz, a) >= 0
    c = 2*m['I'] + 2*m['U'] + m['Delta_N'] - q
    r = m['pi'] + sigma + dz + a - 2*m['I'] - hz
    b = m['E'] - 18 + 3*m['pi']
    assert c+r == b
    return dict(J=j, Q0=q, HZ=hz, isolated_lines=sigma, Delta_Z=dz,
                quad_kite_credit=a, allocation_slack=c, reconciliation=r,
                B_slack=b)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('metrics', nargs='+', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--progress', type=int, default=3000)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    sources = {}
    totals = Counter()
    eligible_totals = Counter()
    minima = {}
    first_nonfour_saved = False
    cohorts = defaultdict(Counter)
    with (args.out / 'records.jsonl').open('w') as out:
        for filename in args.metrics:
            for line in filename.open():
                m = json.loads(line)
                source = m['source']
                if source not in sources:
                    sources[source] = [json.loads(s) for s in Path(source).open()]
                d = sources[source][m['record_1_based']-1]
                a = Arr(d['gens'], m['n'])
                assert a.T() == m['T'] and a.Z() == m['Z']
                v = geometry(a, m)
                b = accounting(m)
                eligible = m['structural_class'] and m['triple_optimality']
                if any(not f['four_run'] for f in v['forks']) and not first_nonfour_saved:
                    first_nonfour_saved = True
                    witness = dict(gens=d['gens'], metrics=m, accounting=b, geometry=v)
                    (args.out/'raw_fork_first_counterexample.json').write_text(json.dumps(witness, indent=2)+'\n')
                for cohort, counts in [('all', totals), ('eligible', eligible_totals)] if eligible else [('all', totals)]:
                    counts['records'] += 1
                    counts['with_forks'] += bool(v['forks'])
                    counts['forks'] += len(v['forks'])
                    counts['II_forks'] += sum(f['kinds'] == ['I','I'] for f in v['forks'])
                    counts['fork_M_blocks'] += sum(f['kinds'].count('M') for f in v['forks'])
                    counts['non_four_forks'] += sum(not f['four_run'] for f in v['forks'])
                    counts['perfect_kites'] += len(v['perfect_kites'])
                    counts['with_perfect_triples'] += bool(v['perfect_triples'])
                    counts['zero_credit_records'] += v['zero_credit_eligible']
                    counts['zero_credit_with_all8'] += v['zero_credit_eligible'] and bool(m['all8'])
                    counts['negative_reconciliation'] += b['reconciliation'] < 0
                    counts['O2Q_failures'] += b['allocation_slack'] < 0
                    counts['B_failures'] += b['B_slack'] < 0
                    counts['residual_failures'] += v['residual_slack'] < 0
                    for name, slack in [('reconciliation', b['reconciliation']),
                                        ('residual', v['residual_slack'])]:
                        key = cohort+'_'+name
                        if key not in minima or slack < minima[key]['slack']:
                            minima[key] = dict(slack=slack, source=source,
                                               record_1_based=m['record_1_based'])
                            witness = dict(gens=d['gens'], metrics=m, accounting=b, geometry=v)
                            (args.out / (key+'_minimum.json')).write_text(json.dumps(witness, indent=2)+'\n')
                cohorts[source]['records'] += 1
                out.write(json.dumps(dict(source=source, record_1_based=m['record_1_based'],
                                          eligible=eligible, accounting=b, geometry=v), sort_keys=True)+'\n')
                if args.progress and totals['records'] % args.progress == 0:
                    print(json.dumps(dict(progress=totals['records'], totals=dict(totals))), flush=True)
    result = dict(totals=dict(totals), eligible=dict(eligible_totals),
                  minima=minima, inputs=dict(cohorts), failures=0)
    (args.out / 'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()

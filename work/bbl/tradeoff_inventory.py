#!/usr/bin/env python3
"""Inspect perfect-line defects and test an extension to double interior lines.

Input is the complete metrics.jsonl written by tradeoff_check.py. Words are
read from the recorded JSONL sources. No new global inequality is asserted.
"""
import argparse
from collections import Counter, defaultdict
from itertools import product
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import note3_check as N3
from arr import Arr, first_seg, rays


def axis_masks():
    accepted = []
    for s in product((0, 1), repeat=6):
        if (s[5] + s[0] == s[2] + s[3] == 1 and
                sum(s[::2]) >= 2 and sum(s[1::2]) >= 2):
            accepted.append(''.join(map(str, s)))
    assert accepted == ['011011', '110110']
    return dict(tested=64, accepted=accepted)


def inventory(m, d):
    a = Arr(d['gens'], m['n'])
    records = N3.BC.block_partition(a)
    blocks = {(r['point'], rays(a, r['point'])[r['ray']]): r for r in records}
    incident = m['perfect_triple_incidence']
    details = {}
    for key, count in incident.items():
        p = int(key)
        rs = rays(a, p)
        double = [r for r in rs if first_seg(a, p, r) is not None
                  and len(a.t[first_seg(a, p, r)[0]][first_seg(a, p, r)[1]]) == 2]
        kinds = [blocks[p, r]['kind'] if (p, r) in blocks else 'R' for r in double]
        details[p] = dict(incidences=count, sectors=N3.GB.tri_sectors(a, p),
                          double_rays=double, kinds=kinds,
                          both_UI=len(kinds) == 2 and all(k in ('U', 'I') for k in kinds))
        if m['triple_optimality']:
            assert len(double) == 2 and double[0][0] == double[1][0]
            assert double[0][1] == -double[1][1]
    ui_lines = [q['L'] for q in m['perfect_line_details']
                if all(details[p]['both_UI'] for p in q['triples'])]
    ui_inc = sum(v['incidences'] for v in details.values() if v['both_UI'])
    non_ui_inc = sum(v['incidences'] for v in details.values() if not v['both_UI'])
    nozero = set(m['interior_lines']) - set(m['interior_with_zero'])
    extra_double = sorted(nozero - set(m['perfect_lines']))
    u4 = sum(r['kind'] == 'U' and len(a.events[r['point']]) == 4 for r in records)
    i4 = m['end_counts'].get('I4', 0)
    ui_rhs = 2 * (m['I'] + m['U']) - u4 - i4
    ui_slack = ui_rhs - len(ui_lines)
    at = defaultdict(list)
    for r in records:
        at[r['far']].append(r)
    h_caps = []
    mixed_caps = []
    for x, rr in at.items():
        if len(rr) == 2 and any(r['point'] in details and
                               len(details[r['point']]['double_rays']) == 2 and
                               details[r['point']]['double_rays'][0][0] ==
                               details[r['point']]['double_rays'][1][0]
                               for r in rr):
            p, q = [r['point'] for r in rr]
            e = N3.NC.edge(a, p, q)
            assert len(a.t[e[0]][e[1]]) == 1
            h_caps.append(dict(centre=x, corners=[p, q], edge=e))
        if len(rr) == 4:
            cs = [N3.NC.far_end(a, x, r) for r in rays(a, x)]
            if sum(len(a.events[p]) == 4 for p in cs) >= 2:
                mixed_caps.extend(N3.NC.edge(a, p, q)
                                  for p, q in zip(cs, cs[1:] + cs[:1])
                                  if len(a.t[N3.NC.edge(a, p, q)[0]]
                                            [N3.NC.edge(a, p, q)[1]]) == 1)
    empty_tokens = {(p, first_seg(a, p, r))
                    for p, ev in enumerate(a.events) if len(ev) >= 3
                    for r in rays(a, p) if first_seg(a, p, r) is not None
                    and not a.t[first_seg(a, p, r)[0]][first_seg(a, p, r)[1]]}
    h_tokens = {(p, tuple(c['edge'])) for c in h_caps for p in c['corners']}
    mixed_tokens = {(p, tuple(e)) for e in mixed_caps
                    for p in a.rows[e[0]][e[1]:e[1]+2]}
    assert len(h_tokens) == 2 * len(h_caps)
    assert len(mixed_tokens) == 2 * len(mixed_caps)
    assert not h_tokens & mixed_tokens
    assert not (h_tokens | mixed_tokens) & empty_tokens
    assert not h_tokens & N3.KP.claimed_tokens(a)
    residual_lower = len(empty_tokens) + len(h_tokens) + len(mixed_tokens)
    assert m['Delta_N'] >= residual_lower
    assignments = []
    if m['structural_class'] and m['triple_optimality']:
        assert ui_slack >= 0
        # Two labels per triple-origin UI block, one per quad-origin block:
        # a triple-incidence label and a cap-step label. Select one distinct
        # label for each line in this restricted subset.
        options = defaultdict(list)
        incidences = defaultdict(list)
        for q in m['perfect_line_details']:
            if q['L'] not in ui_lines:
                continue
            assert all(len(a.events[p]) < 4 for p in a.rows[q['L']])
            assert (len(q['triples']) + len(q['caps'])) % 2 == 1
            for p in q['triples']:
                incidences[p].append(q['L'])
            for c in q['caps']:
                options[q['L']].append((c['origin'], c['vertex'], 'cap'))
        for p, lines in incidences.items():
            rr = sorted((r for r in records if r['point'] == p), key=lambda r:r['far'])
            assert len(lines) <= len(rr) == 2
            assert all(r['kind'] in ('U', 'I') for r in rr)
            for L, r in zip(sorted(lines), rr):
                options[L].append((p, r['far'], 'triple'))
        assignments = [dict(L=L, resource=min(options[L])) for L in ui_lines]
        assert len({tuple(r['resource']) for r in assignments}) == len(assignments)
    return dict(UI_perfect_lines=ui_lines, UI_slack=ui_slack, UI_rhs=ui_rhs,
                UI_triple_incidences=ui_inc, non_UI_triple_incidences=non_ui_inc,
                triple_details=details, nozero_interior_lines=sorted(nozero),
                extra_double_lines=extra_double,
                O2_extended_slack=2 * (m['I'] + m['U']) + m['Delta_N'] - len(nozero),
                non_UI_payment_slack=m['Delta_N'] - non_ui_inc,
                non_UI_line_payment_slack=m['Delta_N'] - (m['P0']-len(ui_lines)),
                H_central_caps=h_caps, H_tokens=len(h_tokens),
                empty_tokens=len(empty_tokens), mixed_tokens=len(mixed_tokens),
                residual_lower=residual_lower,
                residual_slack=m['Delta_N']-residual_lower,
                UI_assignments=assignments)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('metrics', nargs='+', type=Path)
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()
    masks = axis_masks()
    args.out.mkdir(parents=True, exist_ok=True)
    sources = {}
    counts = Counter()
    kinds = Counter()
    cohort = defaultdict(Counter)
    ext = dict(tested=0, failures=0, minimum=None)
    free = dict(tested=0, failures=0, minimum=None)
    free_lines = dict(tested=0, failures=0, minimum=None)
    ui = dict(tested=0, failures=0, minimum=None)
    residual = dict(tested=0, failures=0, minimum=None)
    with (args.out / 'inventories.jsonl').open('w') as out:
        for filename in args.metrics:
            for line in filename.open():
                m = json.loads(line)
                source = m['source']
                if source not in sources:
                    sources[source] = [json.loads(s) for s in Path(source).open()]
                d = sources[source][m['record_1_based'] - 1]
                v = inventory(m, d)
                eligible = m['structural_class'] and m['triple_optimality']
                counts['records'] += 1
                counts['eligible'] += int(eligible)
                for c in ('all', 'eligible') if eligible else ('all',):
                    cohort[c]['records'] += 1
                    cohort[c]['positive_P0'] += int(m['P0'] > 0)
                    cohort[c]['with_extra_double_lines'] += bool(v['extra_double_lines'])
                    cohort[c]['with_non_UI_triples'] += bool(v['non_UI_triple_incidences'])
                    cohort[c]['O2_tight_positive_P0'] += int(
                        m['P0'] > 0 and 2*(m['I']+m['U'])+m['Delta_N'] == m['P0'])
                    cohort[c]['O2_extended_failures'] += int(v['O2_extended_slack'] < 0)
                    cohort[c]['non_UI_payment_failures'] += int(v['non_UI_payment_slack'] < 0)
                    cohort[c]['non_UI_line_payment_failures'] += int(v['non_UI_line_payment_slack'] < 0)
                    cohort[c]['with_UI_perfect_lines'] += bool(v['UI_perfect_lines'])
                    cohort[c]['UI_perfect_lines'] += len(v['UI_perfect_lines'])
                    cohort[c]['UI_bound_failures'] += int(v['UI_slack'] < 0)
                    cohort[c]['with_H_caps'] += bool(v['H_central_caps'])
                    cohort[c]['H_caps'] += len(v['H_central_caps'])
                    cohort[c]['residual_bound_failures'] += int(v['residual_slack'] < 0)
                for detail in v['triple_details'].values():
                    kinds[''.join(sorted(detail['kinds']))] += 1
                for name, stat, key in [('O2_extended', ext, 'O2_extended_slack'),
                                        ('non_UI_payment', free, 'non_UI_payment_slack'),
                                        ('non_UI_line_payment', free_lines, 'non_UI_line_payment_slack'),
                                        ('UI_bound', ui, 'UI_slack'),
                                        ('H_residual_bound', residual, 'residual_slack')]:
                    slack = v[key]
                    stat['tested'] += 1
                    stat['failures'] += int(slack < 0)
                    if stat['minimum'] is None or slack < stat['minimum']:
                        stat.update(minimum=slack, source=source,
                                    record_1_based=m['record_1_based'])
                        witness = dict(gens=d['gens'], metrics=m, inventory=v,
                                       candidate=name, slack=slack)
                        (args.out / f'{name}_minimum.json').write_text(
                            json.dumps(witness, indent=2) + '\n')
                out.write(json.dumps(dict(source=source, record_1_based=m['record_1_based'],
                                          eligible=eligible, **v), sort_keys=True)+'\n')
    result = dict(counts=dict(counts), cohorts=dict(cohort),
                  triple_axis_masks=masks,
                  perfect_triple_kind_counts=dict(kinds), O2_extended=ext,
                  non_UI_payment=free, non_UI_line_payment=free_lines, UI_bound=ui,
                  H_residual_bound=residual)
    (args.out / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Task 6: test component locality and alternating-star far-cap payments.

No universal Hall or trade-off is asserted. All physical residual tokens
are reconstructed with the accepted helpers; full counterexample words
are retained. The far-cap test applies only to actual K1 kites, never to
an unproved assumption that an opposite corner is triple.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import note3_check as N3
import note5_allocation as N5A
from arr import Arr, far_end, rays


def components(a, records, at):
    mult = {p for p, ev in enumerate(a.events) if len(ev) >= 3}
    adj = {p: set() for p in mult}
    for L, row in enumerate(a.rows):
        for e, (p, q) in enumerate(zip(row, row[1:])):
            if p in mult and q in mult and len(a.t[L][e]) == 2:
                adj[p].add(q)
                adj[q].add(p)
    for rr in at.values():
        if len(rr) < 2:
            continue
        ps = {r['point'] for r in rr}
        for p in ps:
            adj[p] |= ps - {p}
    owner = {}
    out = []
    for p in sorted(mult):
        if p in owner:
            continue
        todo = [p]
        vertices = {p}
        while todo:
            q = todo.pop()
            new = adj[q] - vertices
            vertices |= new
            todo.extend(new)
        i = len(out)
        for q in vertices:
            owner[q] = i
        lines = set().union(*(a.events[q] for q in vertices))
        out.append(dict(vertices=sorted(vertices), lines=sorted(lines)))
    return owner, out


def analyse(a, m):
    records = N3.BC.block_partition(a)
    at = defaultdict(list)
    for r in records:
        at[r['far']].append(r)
    free = set(N5A.residual_tokens(a, records, at))
    assert len(free) == m['Delta_N']
    owner, comps = components(a, records, at)
    qlines = set(m['interior_lines']) - set(m['interior_with_zero'])
    resources = []
    native_pool = []
    cap_strict = []
    for r in records:
        if r['kind'] not in ('U', 'I'):
            continue
        pool = set(comps[owner[r['point']]]['lines'])
        resources.append(dict(kind=r['kind']+'_origin', origin=r['point'], centre=r['far']))
        native_pool.append(pool)
        cap_strict.append(pool)
        resources.append(dict(kind=r['kind']+'_cap', origin=r['point'], centre=r['far'], cap=r['cap']))
        native_pool.append(pool | {r['cap']})
        cap_strict.append({r['cap']})
    for p, e in sorted(free):
        pool = set(comps[owner[p]]['lines'])
        resources.append(dict(kind='N', origin=p, edge=e))
        native_pool.append(pool)
        cap_strict.append(pool)
    native_counts = Counter(owner[r['origin']] for r in resources)
    flexible_counts = Counter(owner[r['origin']] for r in resources
                              if not r['kind'].endswith('_cap'))
    cap_lines = defaultdict(set)
    for r in records:
        if r['kind'] in ('U', 'I'):
            cap_lines[owner[r['point']]].add(r['cap'])
    global_caps = set().union(*cap_lines.values()) if cap_lines else set()
    for i, c in enumerate(comps):
        c['Q0_lines'] = sorted(qlines & set(c['lines']))
        c['Q0_cap_only_lines'] = sorted((qlines & cap_lines[i]) - set(c['lines']))
        c['Q0_footprint'] = sorted(set(c['Q0_lines']) | set(c['Q0_cap_only_lines']))
        c['Q0_noncap_pencil_lines'] = sorted(set(c['Q0_lines']) - cap_lines[i])
        c['Q0_globally_noncap_lines'] = sorted(set(c['Q0_lines']) - global_caps)
        c['native_resources'] = native_counts[i]
        c['flexible_resources'] = flexible_counts[i]
        c['local_slack'] = native_counts[i] - len(c['Q0_lines'])
        c['footprint_slack'] = native_counts[i] - len(c['Q0_footprint'])
        c['strict_local_slack'] = flexible_counts[i] - len(c['Q0_noncap_pencil_lines'])
        c['global_cap_local_slack'] = flexible_counts[i] - len(c['Q0_globally_noncap_lines'])
        c['all_line_slack'] = native_counts[i] - len(c['lines'])
    allocations = {
        'native_pool': N5A.matching(qlines, resources, native_pool),
        'cap_strict': N5A.matching(qlines, resources, cap_strict),
    }
    local_minimum = min((c['local_slack'] for c in comps), default=0)
    footprint_minimum = min((c['footprint_slack'] for c in comps), default=0)
    strict_local_minimum = min((c['strict_local_slack'] for c in comps), default=0)
    global_cap_local_minimum = min((c['global_cap_local_slack'] for c in comps), default=0)
    geometry = []
    if m['structural_class']:
        for p, ev in enumerate(a.events):
            if len(ev) != 4:
                continue
            rr = [r for r in records if r['point'] == p]
            if len(rr) != 4 or any(len(at[r['far']]) != 4 for r in rr):
                continue
            indices = {r['ray'] for r in rr}
            assert indices in ({0, 2, 4, 6}, {1, 3, 5, 7})
            for r in rr:
                x = r['far']
                cs = [far_end(a, x, ray) for ray in rays(a, x)]
                q = sum(len(a.events[v]) == 4 for v in cs)
                j = cs.index(p)
                p0, a0, r0, t0 = cs[j:] + cs[:j]
                # Actual K1 is needed: the extra axis at a quad far
                # corner would invalidate the exterior-apex argument.
                if q != 1:
                    continue
                edges = [N3.NC.edge(a, a0, r0), N3.NC.edge(a, r0, t0)]
                assert all(len(a.t[L][e]) == 1 for L, e in edges)
                assert N3.NC.edge(a, p0, a0) not in edges
                tokens = {(v, e) for e in edges
                          for v in a.rows[e[0]][e[1]:e[1]+2]}
                unspent = tokens & free
                assert len(unspent) == 2
                geometry.append(dict(p=p, centre=x, corners=[p0,a0,r0,t0],
                                     far_single_edges=edges,
                                     residual_tokens=sorted(unspent)))
    return dict(components=comps, local_minimum=local_minimum,
                footprint_minimum=footprint_minimum,
                strict_local_minimum=strict_local_minimum,
                global_cap_local_minimum=global_cap_local_minimum,
                allocations=allocations, alternating_K1=geometry)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('metrics', nargs='+', type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--progress', type=int, default=3000)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    sources = {}
    counts = Counter()
    eligible_counts = Counter()
    minima = {}
    saved = set()
    with (args.out/'records.jsonl').open('w') as out:
        for path in args.metrics:
            for line in path.open():
                m = json.loads(line)
                if m['source'] not in sources:
                    sources[m['source']] = [json.loads(s) for s in Path(m['source']).open()]
                d = sources[m['source']][m['record_1_based']-1]
                a = Arr(d['gens'], m['n'])
                v = analyse(a, m)
                eligible = m['structural_class'] and m['triple_optimality']
                cohorts = [('all',counts)] + ([('eligible',eligible_counts)] if eligible else [])
                for cohort, c in cohorts:
                    c['records'] += 1
                    c['components'] += len(v['components'])
                    c['poor_native_components'] += sum(x['local_slack'] < 0 for x in v['components'])
                    c['with_poor_native_components'] += v['local_minimum'] < 0
                    c['poor_footprints'] += sum(x['footprint_slack'] < 0 for x in v['components'])
                    c['with_poor_footprints'] += v['footprint_minimum'] < 0
                    c['poor_strict_local_components'] += sum(x['strict_local_slack'] < 0 for x in v['components'])
                    c['with_poor_strict_local_components'] += v['strict_local_minimum'] < 0
                    c['poor_global_cap_local_components'] += sum(x['global_cap_local_slack'] < 0 for x in v['components'])
                    c['alternating_K1_kites'] += len(v['alternating_K1'])
                    for scheme, matching in v['allocations'].items():
                        c[scheme+'_failures'] += matching['deficit'] > 0
                        c[scheme+'_missing_lines'] += matching['deficit']
                        key = cohort+'_'+scheme+'_first_failure'
                        if matching['deficit'] and key not in saved:
                            saved.add(key)
                            (args.out/(key+'.json')).write_text(json.dumps(
                                dict(gens=d['gens'], metrics=m, analysis=v),indent=2)+'\n')
                    for name in ('local_minimum', 'footprint_minimum', 'strict_local_minimum', 'global_cap_local_minimum'):
                        key = cohort+'_'+name
                        if key not in minima or v[name] < minima[key]['slack']:
                            minima[key] = dict(slack=v[name],source=m['source'],
                                               record_1_based=m['record_1_based'])
                            (args.out/(key+'.json')).write_text(json.dumps(
                                dict(gens=d['gens'],metrics=m,analysis=v),indent=2)+'\n')
                out.write(json.dumps(dict(source=m['source'],record_1_based=m['record_1_based'],
                                          eligible=eligible,analysis=v),sort_keys=True)+'\n')
                if args.progress and counts['records'] % args.progress == 0:
                    print(json.dumps(dict(progress=counts['records'],counts=dict(counts))),flush=True)
    result = dict(all=dict(counts),eligible=dict(eligible_counts),minima=minima,
                  asserted_failures=0,
                  limitation='Native locality and allocation failures are recorded, not asserted away.')
    (args.out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))


if __name__ == '__main__':
    main()

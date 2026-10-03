#!/usr/bin/env python3
"""Task 7: direct bad-wedge resources and component incidence candidates.

Every conjecture is recorded, not asserted. Identity and physical-token
reconstructions are asserted. Full words and Hall obstructions are saved.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import note3_check as N3
import note5_allocation as N5A
import note6_check as N6
from arr import Arr, first_seg, far_end, rays


def analyse(a, m):
    eligible = m['structural_class'] and m['triple_optimality']
    records = N3.BC.block_partition(a)
    at = defaultdict(list)
    for r in records:
        at[r['far']].append(r)
    free = set(N5A.residual_tokens(a, records, at))
    ends = N3.end_data(a)
    end_n = {r['token'] for r in ends if r['kind'] == 'N'}
    assert not free & end_n
    nres = free | end_n
    assert len(nres) == m['Delta_N'] + len(end_n)
    vertices = [N3.NC.tri_vertices(a, f) for f in a.tris]
    tf = defaultdict(set)
    vf = defaultdict(set)
    for i, (f, vs) in enumerate(zip(a.tris, vertices)):
        for p in vs:
            vf[p].add(i)
        for L, e, _ in f:
            tf[L, e].add(i)
    wedge_points = {r['v'] for r in ends if r['kind'] == 'W'}
    wedges = {}
    for x in sorted(wedge_points):
        assert len(vf[x]) == 1
        (f,) = vf[x]
        corners = sorted(vertices[f] - {x})
        assert all(len(a.t[L][e]) == 1 for p in corners
                   for L, e in [N3.NC.edge(a, x, p)])
        wedges[x] = dict(face=f, corners=corners,
                         lines=sorted(a.events[x]),
                         mult_corners=[p for p in corners if len(a.events[p]) >= 3])
    assert len(wedges) == m['W']
    assert len({r['face'] for r in wedges.values()}) == len(wedges)
    owner, comps = N6.components(a, records, at)
    qlines = set(m['interior_lines']) - set(m['interior_with_zero'])
    global_caps = {r['cap'] for r in records if r['kind'] in ('U', 'I')}
    both_single = {}
    no_single_pair = []
    for L in sorted(qlines):
        ps = []
        for p in a.rows[L]:
            if len(a.events[p]) < 3:
                continue
            es = [first_seg(a, p, (L, d)) for d in (-1, 1)]
            if all(e is not None and len(a.t[e[0]][e[1]]) == 1 for e in es):
                ps.append(p)
        both_single[L] = ps
        if L not in global_caps and not ps:
            no_single_pair.append(L)
    # Triangles sharing any simple vertex are pooled; this includes
    # opposite isolated fans, not merely edge-connected triangles.
    ds = N3.GB.DSU(len(vertices))
    for p, fs in vf.items():
        if len(a.events[p]) == 2 and fs:
            first = min(fs)
            for f in fs:
                ds.join(first, f)
    triangle_pool = {f: ds.find(f) for f in range(len(vertices))}
    resources, incident, native, fan_pool, line_pool = [], [], [], [], []
    all_wedges = set(wedges)

    def add(resource, roots, faces, direct=None):
        resources.append(resource)
        roots = set(roots)
        incident.append({x for x, w in wedges.items()
                         if x in roots or roots & set(w['corners'])}
                        if direct is None else set(direct))
        cs = {owner[p] for p in roots if p in owner}
        native.append({x for x, w in wedges.items()
                       if x in roots or roots & set(w['corners']) or
                       cs & {owner[p] for p in w['mult_corners']}})
        pools = {triangle_pool[f] for f in faces}
        fan_pool.append({x for x, w in wedges.items()
                         if triangle_pool[w['face']] in pools})
        root_lines = set().union(*(a.events[p] for p in roots)) if roots else set()
        line_pool.append({x for x, w in wedges.items()
                          if root_lines & set(w['lines'])})

    for L, row in enumerate(a.rows):
        for e, use in enumerate(a.t[L]):
            if use:
                continue
            for p in row[e:e+2]:
                add(dict(kind='Z', edge=[L, e], endpoint=p), [p], vf[p])
    for r in records:
        if r['kind'] in ('U', 'I'):
            add(dict(kind=r['kind'], origin=r['point'], centre=r['far']),
                [r['point'], r['far']], vf[r['far']])
    for p, e in sorted(nres, key=lambda item: (item[0], str(item[1]))):
        faces = tf[e] if len(e) == 2 and a.t[e[0]][e[1]] else vf[p]
        direct = {x for x, w in wedges.items() if p in w['corners'] and
                  len(e) == 2 and e == N3.NC.edge(a, p, x)}
        add(dict(kind='N_res', origin=p, edge=e), [p], faces, direct)
    ring = N3.GB.analyse(a)[1]
    case_b = Counter()
    kite_at = Counter(r['point'] for r in records if len(at[r['far']]) == 4)
    bonus = 0
    for x, rr in at.items():
        if len(rr) != 4:
            continue
        cs = [far_end(a, x, r) for r in rays(a, x)]
        q = sum(len(a.events[p]) == 4 for p in cs)
        singles = sum(len(a.t[L][e]) == 1 for p, r in zip(cs, cs[1:]+cs[:1])
                      for L, e in [N3.NC.edge(a, p, r)])
        if q == 1 and not singles:
            case_b.update(p for p in cs if len(a.events[p]) == 4)
        k = 2 if q == 3 else 4 if q == 4 else 0
        bonus += k
        for j in range(k):
            add(dict(kind='K_bonus', centre=x, unit=j), cs, vf[x])
    scorr = {}
    for p, word in ring.items():
        if len(a.events[p]) != 4:
            continue
        s = 8-word.count('B')-kite_at[p]-2*case_b[p]
        assert s >= 0
        scorr[p] = s
        for j in range(s):
            add(dict(kind='S_corr', origin=p, unit=j), [p], vf[p])
    cq = sum(scorr.values()) + bonus
    expected = 2*m['Z'] + m['U'] + m['I'] + len(nres) + cq
    assert len(resources) == expected
    assert expected-m['W'] == m['E']-18+3*m['pi']
    # Proved partial direct payments, with physical resource identities.
    partial = []
    selected = set()
    wedge_cases = Counter()
    quad_wedges = defaultdict(list)
    for x, w in wedges.items():
        multi = w['mult_corners']
        if not multi:
            wedge_cases['all_simple'] += 1
            continue
        if len(multi) == 2:
            p = min(multi)
            tok = (p, N3.NC.edge(a, p, x))
            assert tok in nres
            resource = ('N_res', p, tok[1])
            case = 'two_multiple'
        else:
            (p,) = multi
            (b,) = set(w['corners']) - {p}
            opposite = N3.NC.edge(a, p, b)
            if len(a.events[p]) == 4:
                quad_wedges[p].append(x)
                if eligible:
                    assert sum(N3.GB.tri_sectors(a, p)) == 7 and scorr[p] >= 2
                case = 'one_quad'
                resource = ('S_corr', p, len(quad_wedges[p])-1)
            elif len(a.t[opposite[0]][opposite[1]]) == 1:
                tok = (p, N3.NC.edge(a, p, x))
                assert tok in nres
                resource = ('N_res', p, tok[1])
                case = 'one_triple_single_opposite'
            else:
                rr = at[b]
                block = next(r for r in rr if r['point'] == p)
                if block['kind'] in ('U', 'I'):
                    case = 'one_triple_UI'
                    resource = (block['kind'], p, b)
                else:
                    assert len(rr) == 2
                    (q,) = {r['point'] for r in rr} - {p}
                    central = N3.NC.edge(a, p, q)
                    if len(a.t[central[0]][central[1]]) == 2:
                        wedge_cases['one_triple_H_double'] += 1
                        continue
                    tok = (p, central)
                    assert tok in nres
                    case = 'one_triple_H_single'
                    resource = ('N_res', p, central)
        if case != 'one_quad' or eligible:
            assert resource not in selected
            selected.add(resource)
            partial.append(dict(wedge=x, case=case, resource=resource))
        wedge_cases[case] += 1
    if eligible:
        assert all(len(xs) <= 2 for xs in quad_wedges.values())
    matches = {name: N5A.matching(all_wedges, resources, options)
               for name, options in [('corner_incident', incident),
                                      ('bridge_mutual', native),
                                      ('simple_fan_pool', fan_pool),
                                      ('wedge_line_pool', line_pool)]}
    def resource_key(r):
        if r['kind'] == 'Z':
            return ('Z', tuple(r['edge']), r['endpoint'])
        if r['kind'] in ('U', 'I'):
            return (r['kind'], r['origin'], r['centre'])
        if r['kind'] == 'N_res':
            return ('N_res', r['origin'], tuple(r['edge']))
        if r['kind'] == 'S_corr':
            return ('S_corr', r['origin'], r['unit'])
        return ('K_bonus', r['centre'], r['unit'])
    paid_wedges = {r['wedge'] for r in partial}
    rest_resources = [r for r in resources if resource_key(r) not in selected]
    rest_options = [opt for r, opt in zip(resources, line_pool)
                    if resource_key(r) not in selected]
    assert len(rest_resources) == len(resources)-len(partial)
    matches['locked_wedge_line_pool'] = N5A.matching(all_wedges-paid_wedges,
                                                   rest_resources, rest_options)
    # A bipartite component/line test charges a Q0 line to a multiple
    # where BOTH first rays are single, rather than assuming existence.
    lc_resources, lc_options = [], []
    for r in records:
        if r['kind'] in ('U', 'I'):
            c = owner[r['point']]
            lc_resources.append(dict(kind=r['kind'], origin=r['point'], centre=r['far']))
            lc_options.append({L for L in qlines-global_caps
                               if any(owner[p] == c for p in both_single[L])})
    for p, e in sorted(free):
        c = owner[p]
        lc_resources.append(dict(kind='N', origin=p, edge=e))
        lc_options.append({L for L in qlines-global_caps
                           if any(owner[q] == c for q in both_single[L])})
    lc_match = N5A.matching(qlines-global_caps, lc_resources, lc_options)
    four_sector = []
    pure_formulas = []
    two_vertex = []
    for i, c in enumerate(comps):
        ps = set(c['vertices'])
        if not eligible:
            continue
        if len(ps) == 2:
            assert all(len(a.events[p]) == 3 for p in ps)
        if not all(len(a.events[p]) == 3 for p in ps):
            continue
        kinds = Counter(N3.GB.canon(N3.GB.tri_sectors(a, p)) for p in ps)
        assert set(kinds) <= {'110110', '111100', '111110', '111111'}
        rr = [r for r in records if r['point'] in ps]
        bridges = sum(len(a.t[L][e]) == 2 and p in ps and q in ps
                      for L, row in enumerate(a.rows)
                      for e, (p, q) in enumerate(zip(row, row[1:])))
        ui = sum(r['kind'] in ('U', 'I') for r in rr)
        capacity = ui + sum(p in ps for p, e in free)
        fends = sum(r['kind'] == 'N' and r['v'] in ps for r in ends)
        formula = (2*kinds['110110'] - 2*kinds['111110'] -
                   6*kinds['111111'] + 2*bridges - fends)
        assert formula == capacity
        pure_formulas.append(dict(vertices=sorted(ps), pattern_counts=dict(kinds),
                                  bridge_edges=bridges, F=fends, capacity=capacity))
        if len(ps) != 2:
            continue
        assert set(kinds) <= {'110110', '111100'}
        demands = qlines & set(c['lines']) - global_caps
        if kinds['111100']:
            assert kinds['111100'] == 1 and bridges == 1
            p = next(p for p in ps if N3.GB.canon(N3.GB.tri_sectors(a, p)) == '111100')
            blocks = [r for r in rr if r['point'] == p]
            assert len(blocks) == 2 and all(r['kind'] in ('U', 'I') for r in blocks)
            assert not a.events[p] & qlines
            assert capacity in (3, 4) and len(demands) <= 2
            case = 'one_four_run'
        else:
            case = 'opposite_four_only'
        assert capacity >= len(demands)
        two_vertex.append(dict(vertices=sorted(ps), case=case, capacity=capacity,
                               demands=sorted(demands), slack=capacity-len(demands)))
    for i, c in enumerate(comps):
        ps = set(c['vertices'])
        if not all(len(a.events[p]) == 3 and
                   N3.GB.canon(N3.GB.tri_sectors(a, p)) == '110110'
                   for p in ps):
            continue
        rr = [r for r in records if r['point'] in ps]
        b = len(rr)
        bridges = sum(len(a.t[L][e]) == 2 and p in ps and q in ps
                      for L, row in enumerate(a.rows)
                      for e, (p, q) in enumerate(zip(row, row[1:])))
        ui = sum(r['kind'] in ('U', 'I') for r in rr)
        free_c = {(p, e) for p, e in free if p in ps}
        capacity = ui + len(free_c)
        assert all(first_seg(a, p, ray) is not None for p in ps for ray in rays(a, p))
        assert b + 2*bridges == 2*len(ps)
        assert capacity == 2*len(ps) + 2*bridges
        lines = set(c['lines'])
        demands = qlines & lines - global_caps
        assert len(lines) <= 2*len(ps)+1
        mutual_cap_edges = set()
        kites = 0
        for x, blocks in at.items():
            if blocks[0]['point'] not in ps or len(blocks) < 2:
                continue
            assert all(r['point'] in ps for r in blocks)
            if len(blocks) == 2:
                p, q = [r['point'] for r in blocks]
                mutual_cap_edges.add(N3.NC.edge(a, p, q))
            else:
                assert len(blocks) == 4
                kites += 1
                cs = [far_end(a, x, ray) for ray in rays(a, x)]
                mutual_cap_edges.update(N3.NC.edge(a, p, q)
                                        for p, q in zip(cs, cs[1:]+cs[:1]))
        if bridges:
            case = 'has_bridge'
            assert capacity >= len(lines)+1
        elif ui:
            case = 'has_UI'
            axis = next(r for r in rr if r['kind'] in ('U', 'I'))
            L = rays(a, axis['point'])[axis['ray']][0]
            assert L not in qlines
            assert len(demands) <= len(lines)-1 <= capacity
        else:
            case = 'all_mutual'
            assert len(mutual_cap_edges) == len(ps)+2*kites
            assert len(lines) <= 2*len(ps)-2*kites <= capacity
        assert len(demands) <= capacity
        four_sector.append(dict(vertices=sorted(ps), size=len(ps), case=case,
                                capacity=capacity, bridge_edges=bridges,
                                UI=ui, kites=kites, pencil_lines=sorted(lines),
                                demands=sorted(demands), slack=capacity-len(demands)))
    return dict(resources=len(resources), wedges=wedges,
                wedge_types=dict(Counter(len(w['mult_corners']) for w in wedges.values())),
                wedge_cases=dict(wedge_cases), partial_payments=partial,
                matches=matches, no_single_pair_lines=no_single_pair,
                both_single_component_match=lc_match,
                four_sector_components=four_sector,
                pure_triple_formulas=pure_formulas,
                eligible_two_vertex_components=two_vertex,
                triangle_pool_count=len(set(triangle_pool.values())),
                components=len(comps))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('metrics', nargs='+', type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--limit', type=int)
    ap.add_argument('--progress', type=int, default=3000)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    sources = {}
    counts = {'all': Counter(), 'eligible': Counter()}
    saved = set()
    with (args.out/'records.jsonl').open('w') as out:
        for path in args.metrics:
            for line in path.open():
                if args.limit and counts['all']['records'] >= args.limit:
                    break
                m = json.loads(line)
                source = m['source']
                if source not in sources:
                    sources[source] = [json.loads(s) for s in Path(source).open()]
                d = sources[source][m['record_1_based']-1]
                a = Arr(d['gens'], m['n'])
                v = analyse(a, m)
                eligible = m['structural_class'] and m['triple_optimality']
                for name in ['all'] + (['eligible'] if eligible else []):
                    c = counts[name]
                    c['records'] += 1
                    c['wedges'] += len(v['wedges'])
                    for k, n in v['wedge_types'].items():
                        c[f'wedges_{k}_multiple_corners'] += n
                    for case, n in v['wedge_cases'].items():
                        c['wedge_case_'+case] += n
                    c['partial_wedges_paid'] += len(v['partial_payments'])
                    c['without_both_single_records'] += bool(v['no_single_pair_lines'])
                    c['without_both_single_lines'] += len(v['no_single_pair_lines'])
                    for component in v['four_sector_components']:
                        c['four_sector_components'] += 1
                        c['four_sector_vertices'] += component['size']
                        c['four_sector_'+component['case']] += 1
                        if component['size'] >= 2:
                            c['nonisolated_four_sector_components'] += 1
                            c['nonisolated_four_sector_'+component['case']] += 1
                    if name == 'eligible':
                        c['pure_triple_formula_components'] += len(v['pure_triple_formulas'])
                        for component in v['eligible_two_vertex_components']:
                            c['two_vertex_components'] += 1
                            c['two_vertex_'+component['case']] += 1
                    for scheme, result in dict(v['matches'], both_single_component=v['both_single_component_match']).items():
                        c[scheme+'_failures'] += result['deficit'] > 0
                        c[scheme+'_missing'] += result['deficit']
                        key = name+'_'+scheme+'_first_failure'
                        if result['deficit'] and key not in saved:
                            saved.add(key)
                            (args.out/(key+'.json')).write_text(json.dumps(
                                dict(gens=d['gens'], metrics=m, analysis=v), indent=2)+'\n')
                    key = name+'_no_single_pair_first_failure'
                    if v['no_single_pair_lines'] and key not in saved:
                        saved.add(key)
                        (args.out/(key+'.json')).write_text(json.dumps(
                            dict(gens=d['gens'], metrics=m, analysis=v), indent=2)+'\n')
                out.write(json.dumps(dict(source=source, record_1_based=m['record_1_based'],
                                          eligible=eligible, analysis=v), sort_keys=True)+'\n')
                if args.progress and counts['all']['records'] % args.progress == 0:
                    print(json.dumps(dict(progress=counts['all']['records'], counts={k:dict(v) for k,v in counts.items()})), flush=True)
    result = dict(counts={k:dict(v) for k,v in counts.items()}, asserted_failures=0,
                  limitation='Conjectural matchings are tested, not asserted as universal.')
    (args.out/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()

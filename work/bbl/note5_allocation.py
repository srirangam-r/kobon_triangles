#!/usr/bin/env python3
"""Construct finite sample allocations for O2Q; do not assert Hall globally.

Rebuild the exact Note 3 residual token set. Compare three explicitly
specified transport graphs, saving actual injections and Hall obstructions.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import note3_check as N3
from arr import Arr, first_seg, far_end, rays


def residual_tokens(a, records, at):
    _, ring, _, _ = N3.GB.analyse(a)
    all_n = {N3.ray_token(a, p, ray) for p, word in ring.items()
             for i, ray in enumerate(rays(a, p)) if word[i] == 'N'}
    old = N3.KP.claimed_tokens(a)
    k1a = set()
    for x, rr in at.items():
        if len(rr) != 4:
            continue
        cs = [far_end(a, x, r) for r in rays(a, x)]
        if sum(len(a.events[p]) == 4 for p in cs) != 1:
            continue
        i = next(i for i, p in enumerate(cs) if len(a.events[p]) == 4)
        p, q, r, s = cs[i:] + cs[:i]
        edges = [N3.NC.edge(a, u, v) for u, v in [(p,q),(p,s),(q,r),(r,s)]]
        singles = [e for e in edges if len(a.t[e[0]][e[1]]) == 1]
        if singles:
            e = singles[0]
            for v in a.rows[e[0]][e[1]:e[1]+2]:
                k1a.add((v, e))
    tf = defaultdict(list)
    for f in a.tris:
        vertices = N3.NC.tri_vertices(a, f)
        for L, e, _ in f:
            tf[L, e].append(vertices)
    reserved = set()
    for b in records:
        p, x = b['point'], b['far']
        if len(a.events[p]) != 4 or b['kind'] not in ('U','I'):
            continue
        candidates = []
        for vs in tf[N3.NC.edge(a, p, x)]:
            (t,) = vs - {p,x}
            e = N3.NC.edge(a, p, t)
            if len(a.t[e[0]][e[1]]) == 1:
                candidates.append((p, e))
            elif len(a.events[t]) >= 3:
                candidates.append((t, N3.NC.edge(a, t, x)))
        assert candidates
        token = candidates[0]
        assert token not in reserved
        reserved.add(token)
    end_n = {e['token'] for e in N3.end_data(a) if e['kind'] == 'N'}
    assert old <= all_n and k1a <= all_n and reserved <= all_n
    assert not old & k1a and not (old | k1a) & reserved
    assert not (old | k1a | reserved) & end_n
    free = all_n - old - k1a - reserved - end_n
    assert all(len(e) == 2 for p, e in free)
    return sorted(free)


def component_lines(a, records, at, scheme):
    mult = {p for p, ev in enumerate(a.events) if len(ev) >= 3}
    adj = {p:set() for p in mult}
    if scheme != 'incident':
        for L, row in enumerate(a.rows):
            for i, (p, q) in enumerate(zip(row, row[1:])):
                if p in mult and q in mult and len(a.t[L][i]) == 2:
                    adj[p].add(q); adj[q].add(p)
        for rr in at.values():
            if len(rr) < 2:
                continue
            ps = [b['point'] for b in rr]
            for p in ps:
                adj[p].update(set(ps)-{p})
    if scheme == 'line_connected':
        for row in a.rows:
            ps = [p for p in row if p in mult]
            for p, q in zip(ps, ps[1:]):
                adj[p].add(q); adj[q].add(p)
    labels = {}
    while mult - labels.keys():
        first = min(mult-labels.keys())
        component = {first}
        todo = [first]
        while todo:
            p = todo.pop()
            for q in adj[p]-component:
                component.add(q); todo.append(q)
        lines = set().union(*(a.events[p] for p in component))
        for p in component:
            labels[p] = lines
    return labels


def matching(demands, resources, options):
    choices = {L:[i for i, lines in enumerate(options) if L in lines] for L in demands}
    owner = {}
    def augment(L, seen):
        for i in choices[L]:
            if i in seen:
                continue
            seen.add(i)
            if i not in owner or augment(owner[i], seen):
                owner[i] = L
                return True
        return False
    for L in sorted(demands, key=lambda l:(len(choices[l]),l)):
        augment(L, set())
    inverse = {L:i for i,L in owner.items()}
    missing = sorted(set(demands)-inverse.keys())
    injection = [dict(L=L, resource=resources[i]) for L,i in sorted(inverse.items())]
    assert len({json.dumps(v['resource'],sort_keys=True) for v in injection}) == len(injection)
    if not missing:
        return dict(covered=len(inverse), demands=len(demands), deficit=0, injection=injection)
    s = set(missing)
    neighbour = set()
    todo = list(missing)
    while todo:
        L = todo.pop()
        for i in choices[L]:
            neighbour.add(i)
            if i in owner and owner[i] not in s:
                s.add(owner[i]); todo.append(owner[i])
    assert neighbour == {i for L in s for i in choices[L]}
    assert len(s)-len(neighbour) == len(missing)
    return dict(covered=len(inverse), demands=len(demands), deficit=len(missing),
                injection=injection, Hall_lines=sorted(s),
                Hall_resources=[resources[i] for i in sorted(neighbour)])


def allocate(a, m):
    records = N3.BC.block_partition(a)
    at = defaultdict(list)
    for b in records:
        at[b['far']].append(b)
    free = residual_tokens(a, records, at)
    assert len(free) == m['Delta_N']
    ui = [b for b in records if b['kind'] in ('U','I')]
    resources = []
    roots = []
    for b in ui:
        resources.append(dict(kind=b['kind']+'_origin', origin=b['point'], centre=b['far']))
        roots.append(('vertex', b['point']))
        resources.append(dict(kind=b['kind']+'_cap', origin=b['point'], centre=b['far'], cap=b['cap']))
        roots.append(('cap', b['cap']))
    for p, e in free:
        resources.append(dict(kind='N', origin=p, edge=e))
        roots.append(('vertex', p))
    assert len(resources) == 2*m['I'] + 2*m['U'] + m['Delta_N']
    demands = sorted(set(m['interior_lines'])-set(m['interior_with_zero']))
    results = {}
    for scheme in ('incident','bridge_mutual','line_connected'):
        lines = component_lines(a, records, at, scheme)
        options = []
        for kind, root in roots:
            if kind == 'vertex':
                options.append(lines[root])
            else:
                reachable = {root}
                if scheme != 'incident':
                    for p in a.rows[root]:
                        if p in lines:
                            reachable |= lines[p]
                options.append(reachable)
        results[scheme] = matching(demands, resources, options)
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('metrics', nargs='+', type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--progress', type=int, default=3000)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    sources = {}
    counts = Counter()
    stats = {scheme:dict(tested=0, failures=0, maximum_deficit=0,
                         eligible_tested=0, eligible_failures=0)
             for scheme in ('incident','bridge_mutual','line_connected')}
    with (args.out/'allocations.jsonl').open('w') as out:
        for filename in args.metrics:
            for line in filename.open():
                m = json.loads(line)
                source = m['source']
                if source not in sources:
                    sources[source] = [json.loads(s) for s in Path(source).open()]
                d = sources[source][m['record_1_based']-1]
                a = Arr(d['gens'], m['n'])
                results = allocate(a, m)
                eligible = m['structural_class'] and m['triple_optimality']
                counts['records'] += 1
                counts['eligible'] += eligible
                for scheme, result in results.items():
                    s = stats[scheme]
                    s['tested'] += 1
                    s['failures'] += result['deficit'] > 0
                    s['eligible_tested'] += eligible
                    s['eligible_failures'] += eligible and result['deficit'] > 0
                    if result['deficit'] > s['maximum_deficit']:
                        s.update(maximum_deficit=result['deficit'], source=source,
                                 record_1_based=m['record_1_based'])
                        witness = dict(gens=d['gens'], metrics=m, scheme=scheme, result=result)
                        (args.out/(scheme+'_maximum_deficit.json')).write_text(json.dumps(witness,indent=2)+'\n')
                    if eligible and result['deficit'] and not s.get('eligible_first_saved'):
                        s['eligible_first_saved'] = True
                        witness = dict(gens=d['gens'], metrics=m, scheme=scheme, result=result)
                        (args.out/(scheme+'_eligible_first_failure.json')).write_text(json.dumps(witness,indent=2)+'\n')
                out.write(json.dumps(dict(source=source, record_1_based=m['record_1_based'],
                                          eligible=eligible, allocations=results),sort_keys=True)+'\n')
                if args.progress and counts['records'] % args.progress == 0:
                    print(json.dumps(dict(progress=counts['records'], schemes=stats)),flush=True)
    result = dict(counts=dict(counts), schemes=stats, token_reconstruction_errors=0)
    (args.out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))


if __name__ == '__main__':
    main()

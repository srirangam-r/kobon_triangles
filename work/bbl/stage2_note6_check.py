#!/usr/bin/env python3
"""Stage 2 Task 6 local boundary checks; no zero-credit exclusion certificate.

Check the two-single-far-cap lemma ONLY when the far corner is triple.
Record, rather than discard, quadruple far corners in outward kites.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import note3_check as N3
from arr import Arr, first_seg, far_end, rays


DOUBLE_B10 = ('0 4 1 2* 6 4* 3 1* 0 6* 3** 1* 8 6* 5 3* '
              '2 5* 0* 4 7 3')


def mixed_zero_masks():
    surviving = []
    for bits in range(256):
        blocks = {i for i in range(8) if bits >> i & 1}
        if 0 not in blocks or {1, 7} & blocks:
            continue
        if any(all((i+j) % 8 in blocks for j in range(3)) for i in range(8)):
            continue
        possible = [i for i in blocks
                    if not {(i-1) % 8, (i+1) % 8} & blocks]
        for km in range(1 << len(possible)):
            kites = {i for j, i in enumerate(possible) if km >> j & 1}
            if 0 not in kites:
                continue
            bposs = [i for i in kites
                     if not {(i-2) % 8, (i+2) % 8} & blocks]
            for cm in range(1 << len(bposs)):
                case_b = {i for j, i in enumerate(bposs) if cm >> j & 1}
                if 0 in case_b or 8-len(blocks)-len(kites)-2*len(case_b):
                    continue
                # Accepted global zero-slack propagation: at a single-B
                # zero star, its central neighbour is quadruple. Rays 1,7
                # here are prescribed triple, so they cannot be central.
                if len(case_b) == 1 and (next(iter(case_b))+4) % 8 in {1,7}:
                    continue
                surviving.append((sorted(blocks), sorted(kites), sorted(case_b)))
    assert surviving == [([0,2,4,6], [0,2,4,6], [])]
    return dict(surviving_masks=surviving, failures=0)


def check(gens, n, source):
    a = Arr(gens, n)
    N3.word_valid(gens, n)
    if not N3.GB.class_check(a)[0]:
        return Counter(skipped_outside_structural_class=1), []
    z = N3.credit_state(a)
    _, ring, _, _ = N3.GB.analyse(a)
    recs = N3.BC.block_partition(a)
    at = defaultdict(list)
    by_side = {}
    for r in recs:
        at[r['far']].append(r)
        by_side[r['point'], r['ray']] = r
    counts = Counter(arrangements=1)
    details = []
    by_edge = defaultdict(list)
    for face in a.tris:
        vertices = N3.NC.tri_vertices(a, face)
        for line, edge, _ in face:
            by_edge[line, edge].append(vertices)
    for x, rr in at.items():
        if len(rr) != 4:
            continue
        corners = [far_end(a,x,ray) for ray in rays(a,x)]
        quads = [v for v in corners if len(a.events[v]) == 4]
        if len(quads) != 1:
            continue
        i = corners.index(quads[0])
        p, left, t, right = corners[i:] + corners[:i]
        edges = [N3.NC.edge(a,u,v) for u,v in
                 [(p,left),(left,t),(t,right),(right,p)]]
        if not all(len(a.t[line][edge]) == 2 for line,edge in edges):
            continue
        counts['case_B_kites'] += 1
        for adjacent in [left,right]:
            e = N3.NC.edge(a,t,adjacent)
            apex = next(next(iter(vs-{t,adjacent}))
                        for vs in by_edge[e] if x not in vs)
            if a.is_simple(apex):
                ea = N3.NC.edge(a,adjacent,apex)
                et = N3.NC.edge(a,t,apex)
                assert len(a.t[ea[0]][ea[1]]) == len(a.t[et[0]][et[1]]) == 1
                counts['case_B_simple_external_apices_two_single_caps'] += 1
            else:
                counts['case_B_multiple_external_apices'] += 1
    for p, slack in z['Scorr'].items():
        if slack or ring[p] not in {'BRBRBRBR', 'RBRBRBRB'}:
            continue
        rs = rays(a, p)
        bridges = [i for i, c in enumerate(ring[p]) if c == 'R']
        quads = [i for i in bridges if len(a.events[far_end(a,p,rs[i])]) == 4]
        if len(quads) != 1:
            continue
        (inward,) = quads
        outward = (inward+4) % 8
        b = far_end(a, p, rs[inward])
        t = far_end(a, p, rs[outward])
        assert len(a.events[t]) == 3
        counts['alternating_endpoint_stars'] += 1
        for k in [(outward-1) % 8, (outward+1) % 8]:
            r = by_side[p, k]
            x = r['far']
            assert len(at[x]) == 4
            opposite = (rs[k][0], rs[k][1])
            far = far_end(a, x, opposite)
            neighbours = [far_end(a,p,rs[(k+j) % 8]) for j in [-1,1]]
            assert t in neighbours and all(len(a.events[v]) == 3 for v in neighbours)
            far_edges = [N3.NC.edge(a, far, v) for v in neighbours]
            uses = [len(a.t[L][e]) for L,e in far_edges]
            m = len(a.events[far])
            if m == 3:
                assert uses == [1,1]
                counts['outward_triple_far_corners'] += 1
            else:
                assert m == 4
                counts['outward_quad_far_corners'] += 1
                (fourth,) = set(a.events[far]) - {
                    rs[k][0], far_edges[0][0], far_edges[1][0]}
                h = rs[outward][0]
                u = next(v for v in a.rows[h] if fourth in a.events[v])
                t_edge = N3.NC.edge(a, far, t)
                if len(a.t[t_edge[0]][t_edge[1]]) == 2:
                    assert (a.pos[h][u]-a.pos[h][t])*rs[outward][1] > 0
                    counts['outward_quad_double_cap_extra_axis_checks'] += 1
            detail = dict(source=source, p=p, inward_quad=b, outward_triple=t,
                          centre=x, far=far, far_multiplicity=m,
                          far_cap_uses=uses, Scorr_at_far=z['Scorr'].get(far),
                          structural_class=True, triple_optimality=N3.opt_triples(a))
            if m == 4:
                detail.update(fourth_axis=fourth, fourth_H_vertex=u,
                              fourth_H_beyond_boundary=(a.pos[h][u]-a.pos[h][t])*rs[outward][1] > 0)
            details.append(detail)
    return counts, details


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='*')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    counts = Counter(alternating_endpoint_stars=0,
                     outward_triple_far_corners=0, outward_quad_far_corners=0)
    details = []
    cores = [('double_B10', DOUBLE_B10, 10),
             ('extended_double_B10', N3.extend_right(DOUBLE_B10,10,18),18),
             ('CORE10', N3.CORE10,10),
             ('extended_CORE10', N3.extend_right(N3.CORE10,10,18),18),
             ('PARITY12', N3.PARITY12,12)]
    for source, g, n in cores:
        c, d = check(g,n,source)
        counts.update(c); details.extend(d)
    for name in args.paths:
        for number, line in enumerate(Path(name).open(),1):
            d = json.loads(line)
            if not d.get('gens'):
                continue
            c, out = check(d['gens'],d.get('n',18),f'{name}:{number}')
            counts.update(c); details.extend(out)
    result = dict(counts=dict(sorted(counts.items())),
                  mixed_zero_mask_check=mixed_zero_masks(), failures=0,
                  limitation='No global Stage 2 certificate; alternating-endpoint boundary has zero sample coverage.')
    (args.out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    (args.out/'boundary_details.json').write_text(json.dumps(details,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))


if __name__ == '__main__':
    main()

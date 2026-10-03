#!/usr/bin/env python3
"""Task 7 local geometric checks, not a global Stage 2 certificate.

The main exercised assertion is the triple-cap continuation rule.  The
case-B return-axis assertions retain their actual sample eligibility.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stage2_note6_check as S6
N3 = S6.N3
Arr, far_end, rays = S6.Arr, S6.far_end, S6.rays


def exterior_apex(a, by_edge, u, v, interior):
    edge = N3.NC.edge(a, u, v)
    faces = by_edge[edge]
    if len(faces) != 2:
        return None
    (face,) = [f for f in faces if interior not in f]
    return next(iter(face - {u, v}))


def check(gens, n, source):
    N3.word_valid(gens, n)
    a = Arr(gens, n)
    records = N3.BC.block_partition(a)
    at = defaultdict(list)
    for record in records:
        at[record['far']].append(record)
    by_edge = defaultdict(list)
    for face in a.tris:
        vertices = N3.NC.tri_vertices(a, face)
        for line, edge, _ in face:
            by_edge[line, edge].append(vertices)
    counts = Counter(arrangements=1, triple_cap_continuations=0,
                     full_case_B_diagonal_corners=0,
                     full_case_B_return_axis_checks=0,
                     full_case_B_first_H_apices=0,
                     full_case_B_simple_first_H_apices=0,
                     full_case_B_simple_first_H_apex_quad_side_checks=0,
                     zero_single_B_quad_neighbour_pairs=0)
    details = []
    case_b_indices = defaultdict(list)
    for x, rr in at.items():
        if len(rr) != 4:
            continue
        corners = [far_end(a, x, ray) for ray in rays(a, x)]
        for i, v in enumerate(corners):
            if len(a.events[v]) != 3:
                continue
            for step in [-1, 1]:
                m, other = corners[(i+step) % 4], corners[(i-step) % 4]
                w = exterior_apex(a, by_edge, v, m, x)
                if w is None:
                    continue
                line = N3.NC.edge(a, v, other)[0]
                assert line in a.events[w], (source, x, v, m, other, w)
                assert ((a.pos[line][w]-a.pos[line][v]) *
                        (a.pos[line][other]-a.pos[line][v])) < 0
                counts['triple_cap_continuations'] += 1
        quads = [v for v in corners if len(a.events[v]) == 4]
        if len(quads) != 1:
            continue
        i = corners.index(quads[0])
        p, left, t, right = corners[i:] + corners[:i]
        caps = [N3.NC.edge(a, u, v) for u, v in
                [(p, left), (left, t), (t, right), (right, p)]]
        if not all(len(a.t[line][edge]) == 2 for line, edge in caps):
            continue
        case_b_indices[p].append(next(i for i, ray in enumerate(rays(a, p))
                                      if far_end(a, p, ray) == x))
        h = N3.NC.edge(a, p, x)[0]
        diagonal = N3.NC.edge(a, left, x)[0]
        ys = []
        return_points = []
        for adjacent, opposite in [(left, right), (right, left)]:
            y = exterior_apex(a, by_edge, t, adjacent, x)
            pa = N3.NC.edge(a, p, adjacent)[0]
            tf = N3.NC.edge(a, t, opposite)[0]
            assert pa in a.events[y] and tf in a.events[y]
            ys.append(y)
            if not all(N3.GB.tri_sectors(a, adjacent)):
                return_points.append(None)
                continue
            counts['full_case_B_diagonal_corners'] += 1
            # Simple Y would make AY single, contrary to full adjacent.
            assert not a.is_simple(y)
            u = exterior_apex(a, by_edge, adjacent, y, t)
            assert u is not None and diagonal in a.events[u]
            assert ((a.pos[diagonal][u]-a.pos[diagonal][adjacent]) *
                    (a.pos[diagonal][x]-a.pos[diagonal][adjacent])) < 0
            extra = set(a.events[y]) - {pa, tf}
            assert extra & set(a.events[u])
            counts['full_case_B_return_axis_checks'] += 1
            return_points.append(u)
        if not (all(N3.GB.tri_sectors(a, t)) and
                all(point is not None for point in return_points)):
            continue
        direction = 1 if a.pos[h][t] > a.pos[h][p] else -1
        v = far_end(a, t, (h, direction))
        assert v is not None
        assert exterior_apex(a, by_edge, t, ys[0], left) == v
        assert exterior_apex(a, by_edge, t, ys[1], right) == v
        counts['full_case_B_first_H_apices'] += 1
        if a.is_simple(v):
            counts['full_case_B_simple_first_H_apices'] += 1
            # If return points coincide, this general context does not
            # satisfy the distinct-opposite-cap hypothesis used in Task 7.
            if return_points[0] != return_points[1]:
                assert any(len(a.events[y]) == 4 for y in ys)
                counts['full_case_B_simple_first_H_apex_quad_side_checks'] += 1
        details.append(dict(source=source, p=p, centre=x, far=t,
                            diagonal_corners=[left, right], exterior=ys,
                            return_points=return_points, first_H_apex=v,
                            first_H_apex_multiplicity=len(a.events[v])))

    if N3.GB.class_check(a)[0]:
        counts['structural_class_arrangements'] += 1
        state = N3.credit_state(a)
        for p, slack in state['Scorr'].items():
            if slack or len(case_b_indices[p]) != 1:
                continue
            (i,) = case_b_indices[p]
            q = far_end(a, p, rays(a, p)[(i+4) % 8])
            if (len(a.events[q]) == 4 and not state['Scorr'][q] and
                    len(case_b_indices[q]) == 1):
                # Local slack at P,Q does not by itself enforce the
                # global zero-path reduction. Require the orientation
                # and triple opposite corners used in the hand proof.
                (j,) = case_b_indices[q]
                if far_end(a, q, rays(a, q)[(j+4) % 8]) != p:
                    continue
                if not (all(N3.GB.tri_sectors(a, p)) and
                        all(N3.GB.tri_sectors(a, q))):
                    continue
                mixed = []
                for x, blocks in at.items():
                    if len(blocks) != 4:
                        continue
                    corners = [far_end(a, x, ray) for ray in rays(a, x)]
                    if p not in corners or q not in corners:
                        continue
                    ip, iq = corners.index(p), corners.index(q)
                    if (ip-iq) % 4 not in (1, 3):
                        continue
                    mixed.append(corners)
                if len(mixed) != 2 or not all(
                        len(a.events[v]) == 3 for corners in mixed
                        for v in corners if v not in (p, q)):
                    continue
                counts['zero_single_B_quad_neighbour_pairs'] += 1
                # The Task 7 hand proof excludes this geometric motif.
                raise AssertionError(('forbidden B--B motif', source, p, q))
    else:
        counts['outside_structural_class_arrangements'] += 1
    return counts, details


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='*')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    counts = Counter()
    details = []
    cores = [('double_B10', S6.DOUBLE_B10, 10),
             ('extended_double_B10', N3.extend_right(S6.DOUBLE_B10, 10, 18), 18),
             ('CORE10', N3.CORE10, 10),
             ('extended_CORE10', N3.extend_right(N3.CORE10, 10, 18), 18),
             ('PARITY12', N3.PARITY12, 12)]
    for source, gens, n in cores:
        c, d = check(gens, n, source)
        counts.update(c)
        details.extend(d)
    for name in args.paths:
        for number, line in enumerate(Path(name).open(), 1):
            obj = json.loads(line)
            if not obj.get('gens'):
                continue
            c, d = check(obj['gens'], obj.get('n', 18), f'{name}:{number}')
            counts.update(c)
            details.extend(d)
    summary = dict(counts=dict(sorted(counts.items())), failures=0,
                   limitation='Local geometric checks only; no global Stage 2 certificate.')
    (args.out/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    (args.out/'return_details.json').write_text(json.dumps(details, indent=2)+'\n')
    print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    main()

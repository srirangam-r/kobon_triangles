"""Soundness regressions, not score measurements.

uv run --no-project --with 'python-sat==1.8.dev24' python search/test_symmetry.py
Use --quick for a smoke test. No submitted arrangement is written.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
from itertools import combinations, product
import json
from pathlib import Path
import random

from pysat.formula import CNF, IDPool
from pysat.solvers import Solver
from kobon_sat import build, build_defect, chi3_from_lines, count_general
from lexleader import VALUE_ORDER, add_lex_leaders, lex_leader_holds
from symmetry import Action, actions

ROOT = Path(__file__).resolve().parents[1]


def coordinate_action(lines, action):
    """Independent rational plane map realizing an end-circle action."""
    n = len(lines)
    lines = [tuple(map(F, row)) for row in lines]
    if action.mirror:
        lines = [(a, -b, c) for a, b, c in lines]  # y -> -y
        start = (n - 1 - action.start) % (2*n)
    else:
        start = action.start % (2*n)
    if action.orientation == -1:
        start = (start + n) % (2*n)
    cut = start % n
    if cut:
        slopes = sorted(-a/b for a, b, _ in lines)
        h = (slopes[cut-1] + slopes[cut])/2
        # x' = y-h*x, y' = -x, determinant +1 (an affine map).
        lines = [(b, -a-h*b, c) for a, b, c in lines]
    if start >= n:
        lines = [(-a, -b, c) for a, b, c in lines]
    return lines


def multiplicities(chi, n):
    """Concurrency components of pair intersections, including simple points."""
    parent = {p: p for p in combinations(range(n), 2)}
    def find(p):
        while parent[p] != p:
            parent[p] = parent[parent[p]]
            p = parent[p]
        return p
    for t, v in chi.items():
        if v == 0:
            pairs = list(combinations(t, 2))
            for p in pairs[1:]:
                parent[find(p)] = find(pairs[0])
    members = {}
    for p in parent:
        members.setdefault(find(p), set()).update(p)
    return Counter(len(lines) for lines in members.values())


def geometric_checks(quick):
    paths = sorted(set(ROOT.glob('submissions/*/solution.json')) |
                   set(ROOT.glob('work/certs/*/solution.json')))
    assert paths, 'no certificate fixtures found'
    cases = [(str(p.relative_to(ROOT)), json.loads(p.read_text())['lines']) for p in paths]
    # Exercise zeros, fourfold concurrency, a vertical-line chart change,
    # and all lines incident with triple points (no simple-line WLOG).
    cases += [('triple', [(i, -1, 0 if i < 3 else i*i+1) for i in range(6)]),
              ('fourfold', [(i, -1, 0 if i < 4 else i*i+1) for i in range(6)]),
              ('pencil', [(i, -1, 0) for i in range(6)])]
    checked = 0
    for name, raw in cases:
        lines = [tuple(map(F, row)) for row in raw]
        if any(b == 0 for _, b, _ in lines):
            # Invertible shear to remove verticals; does not remove parallels.
            h = next(F(k) for k in range(1, len(lines)+2)
                     if all(b-a*k != 0 for a, b, _ in lines))
            lines = [(a, b-a*h, c) for a, b, c in lines]
        order, chi = chi3_from_lines(lines)
        assert chi is not None, f'{name}: parallel lines outside this SAT model'
        lines = [lines[i] for i in order]
        n = len(lines)
        # This reuses the repository's existing helper solely for invariance;
        # it neither produces nor claims an official triangle score.
        triangles = {tuple(t) for t in count_general(n, chi)}
        mult = multiplicities(chi, n)
        gs = list(actions(n, unique=False))
        if quick:
            gs = [Action(0), Action(1), Action(n+1, -1, True), Action(n-1, 1, True)]
        unique_seen = set()
        for g in gs:
            got_order, actual = chi3_from_lines(coordinate_action(lines, g))
            predicted = g.apply(chi, n)
            assert tuple(got_order) == g.permutation(n), (name, g, 'label map')
            assert actual == predicted, (name, g, 'sign map')
            key = (g.ends(n), g.mirror)
            if key not in unique_seen:
                perm = g.permutation(n)
                after = count_general(n, actual)
                assert {tuple(sorted(perm[i] for i in t)) for t in after} == triangles, (name, g)
                assert multiplicities(actual, n) == mult, (name, g, 'multiplicity')
                unique_seen.add(key)
            checked += 1
        print(f'fixture {name}: exact affine actions and invariants PASS', flush=True)
    return dict(fixtures=len(cases), geometric_actions=checked,
                work_certs_present=(ROOT/'work/certs').exists())


def onehot(n):
    cnf, maps = CNF(), [{}, {}, {}]
    pool = IDPool()
    for t in combinations(range(n), 3):
        vs = [pool.id((t, v)) for v in VALUE_ORDER]
        for d, var in zip(maps, vs):
            d[t] = var
        cnf.append(vs)
        for a, b in combinations(vs, 2):
            cnf.append([-a, -b])
    # Deliberately leave the pool behind the CNF header, like cube callers.
    cnf.append([pool.top + 17])
    cnf.pool = pool
    return cnf, maps


def fix(chi, maps):
    codes = dict(zip(VALUE_ORDER, maps))
    return [codes[v][t] for t, v in chi.items()]


def clause_checks():
    n = 4
    triples = list(combinations(range(n), 3))
    checked = 0
    for anchored, prefix in product((False, True), (0, 1, 4)):
        cnf, maps = onehot(n)
        old_nv = cnf.nv
        info = add_lex_leaders(cnf, *maps, prefix, fixed_line0=anchored)
        assert cnf.nv >= old_nv
        if prefix:
            assert cnf.pool.id(('after_lex',)) > cnf.nv
        with Solver(name='cadical195', bootstrap_with=cnf.clauses) as solver:
            for vals in product(VALUE_ORDER, repeat=len(triples)):
                chi = dict(zip(triples, vals))
                expected = lex_leader_holds(chi, n, prefix, fixed_line0=anchored)
                assert solver.solve(assumptions=fix(chi, maps)) == expected, (info, chi)
                checked += 1
    # Small integration test: optional builders remain usable with one-hot
    # witnesses fixed; the two no-lex invocations are byte-for-byte identical.
    a = build_defect(5, 0, 1)
    b = build_defect(5, 0, 1, lex_prefix=0)
    assert a[0].clauses == b[0].clauses
    c = build_defect(5, 0, 1, lex_prefix=4)
    assert c[0].lex_info['fixed_line0'] is False
    d = build_defect(5, 0, 1, lex_prefix=4, lex_fixed_line0=True)
    assert d[0].lex_info['fixed_line0'] is True
    for obj in (a, c, d):
        with Solver(name='cadical195', bootstrap_with=obj[0].clauses) as solver:
            assert solver.solve()
    # This budget activates the legacy defect-free-line-0 break.
    anchored = build_defect(5, 4, 0, lex_prefix=4)
    assert anchored[0].lex_info['fixed_line0'] is True
    return dict(exhaustive_clause_assignments=checked, builder_checks=5)


def orbit_checks(samples):
    n = 7
    cnf, x, _ = build(n, 0)
    rng = random.Random(70419)
    triples = list(combinations(range(n), 3))
    rank = {v: i for i, v in enumerate(VALUE_ORDER)}
    groups = {a: [g.signed_map(n) for g in actions(n, fixed_line0=a)] for a in (False, True)}
    def apply(chi, mapping):
        return {t: f*chi[s] for t, (s, f) in mapping.items()}
    lex_solvers = {}
    for anchored in (False, True):
        c, maps = onehot(n)
        add_lex_leaders(c, *maps, 12, fixed_line0=anchored)
        c.append([-maps[2][0, 1, 2]])
        if anchored:
            c.extend([[-maps[0][t]] for t in triples if 0 in t])
        lex_solvers[anchored] = (Solver(name='cadical195', bootstrap_with=c.clauses), maps)
    def check(chi):
        orbit = [apply(chi, g) for g in groups[False]]
        for anchored in (False, True):
            if anchored:
                eligible = [v for v in orbit if all(v[t] != 0 for t in triples if 0 in t)]
                if not eligible:  # no off-triple line exists: do not impose that WLOG
                    continue
                seed = eligible[0]
                orbit2 = [apply(seed, g) for g in groups[True]]
            else:
                orbit2 = orbit
            chosen = min(orbit2, key=lambda v: tuple(rank[v[t]] for t in triples))
            assert chosen[0, 1, 2] != -1
            solver, maps = lex_solvers[anchored]
            assert solver.solve(assumptions=fix(chosen, maps)), (anchored, chi)
    try:
        with Solver(name='cadical195', bootstrap_with=cnf.clauses) as solver:
            for _ in range(samples):
                solver.set_phases([var if rng.randrange(2) else -var for var in x.values()])
                assert solver.solve(), 'unexpected exhaustion of simple signotopes'
                model = set(solver.get_model())
                chi = {t: (1 if var in model else -1) for t, var in x.items()}
                check(chi)
                solver.add_clause([-var if chi[t] == 1 else var for t, var in x.items()])
        # Exact nonsimple arrangements exercise the third value too.
        for i in range(samples):
            slopes = sorted(rng.sample(range(-40, 41), n))
            lines = [(m, -1, 0 if j < 3 else rng.randint(-30, 30)) for j, m in enumerate(slopes)]
            _, chi = chi3_from_lines(lines)
            check(chi)
    finally:
        for solver, _ in lex_solvers.values():
            solver.delete()
    return dict(sat_pseudoline_orbits=samples, concurrent_geometric_orbits=samples)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--quick', action='store_true')
    ap.add_argument('--json', type=Path)
    args = ap.parse_args()
    result = clause_checks()
    print('exhaustive one-hot clauses and builder checks PASS', flush=True)
    result.update(geometric_checks(args.quick))
    result.update(orbit_checks(5 if args.quick else 200))
    print(json.dumps(result, sort_keys=True), flush=True)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    main()

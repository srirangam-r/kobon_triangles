"""Soundness regression: real arrangements must satisfy the defect-budget CNF.

For each exact arrangement (gallery certificates, including ones with triple points):
  1. rotate it exactly (rational rotation) so that a line with no defect -- and, when the
     model requires it, through no triple point -- has the smallest slope (line 0), as the
     rotation symmetry breaking in build_defect assumes;
  2. compute its 3-valued chi, its triangle count T and number of triple points k;
  3. add chi as unit clauses to build_defect(n, T, k) and check the CNF is satisfiable.
A failure would mean the model wrongly excludes a real arrangement.

    uv run --no-project --with python-sat python search/regress_real.py <solution.json> [...]
"""
import json
import sys
from fractions import Fraction
from itertools import combinations
from pathlib import Path

from pysat.solvers import Solver

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kobon_sat import build_defect, chi3_from_lines, count_general  # noqa: E402
from structure import stats  # noqa: E402


def rotate(lines, t):
    """Rotate the plane by the angle with cos=(1-t^2)/(1+t^2), sin=2t/(1+t^2) (exact)."""
    c, s = Fraction(1 - t * t, 1 + t * t), Fraction(2 * t, 1 + t * t)
    out = []
    for a, b, k in lines:
        # a x + b y + k = 0 with (x, y) = R^-1 (x', y'): x = c x' + s y', y = -s x' + c y'
        na, nb = a * c - b * s, a * s + b * c
        den = na.denominator * nb.denominator
        out.append((int(na * den), int(nb * den), int(k * den)))
    return out


def defects_per_line(n, chi):
    """Consecutive pairs on each line that are not triangle sides, from chi."""
    tris = set(count_general(n, chi))
    bad = [0] * n
    for r in range(n):
        others = [x for x in range(n) if x != r]
        def before(i, j):
            t = tuple(sorted((r, i, j)))
            return chi[t] == (-1 if i < j else 1)
        for i in others:
            for j in others:
                if i == j or not before(i, j):
                    continue
                if any(before(i, l) and before(l, j) for l in others if l not in (i, j)):
                    continue
                if tuple(sorted((r, i, j))) not in tris:
                    bad[r] += 1
    return bad


def check(path):
    lines = [tuple(l) for l in json.loads(Path(path).read_text())["lines"]]
    n = len(lines)
    st = stats(lines)
    T, k = st["T"], st["multiple_points"].get(3, 0)
    if set(st["multiple_points"]) - {3}:
        return f"{path}: has 4+-fold points {st['multiple_points']}; outside the K-triple-point class, skipped"
    budget = n * (n - 2) + 3 * k + k * (k - 1) // 2 - 3 * T
    need_simple0 = budget < n and n - budget - 3 * k > 0
    for num in range(1, 400):
        for den in (7, 13, 29, 61):
            t = Fraction(num, den) - Fraction(200, den) * 0
            rl = rotate(lines, Fraction(num - 200, den))
            order, chi = chi3_from_lines(rl)
            if chi is None:
                continue
            if chi[0, 1, 2] == -1:  # 180-degree rotation flips every sign, keeps labels
                chi = {t3: -v for t3, v in chi.items()}
            per = defects_per_line(n, chi)
            ok0 = per[0] == 0 if budget < n else True
            if need_simple0:
                ok0 = ok0 and all(chi[t3] != 0 for t3 in combinations(range(n), 3) if 0 in t3)
            if ok0:
                cnf, z, pz, ng, tri, b = build_defect(n, T, k, alternate=ALTERNATE, blanc=BLANC)
                units = [[z[t3]] if v == 0 else [pz[t3]] if v == 1 else [ng[t3]] for t3, v in chi.items()]
                with Solver(name="cadical195", bootstrap_with=cnf.clauses + units) as s:
                    sat = s.solve()
                return (f"{path}: n={n} T={T} triple={k} budget={b} defects={sum(per)} line0-defects={per[0]} "
                        f"-> {'SAT (model admits this real arrangement)' if sat else 'UNSAT  <-- SOUNDNESS BUG'}")
    return f"{path}: could not find a rotation putting a suitable line first"


ALTERNATE = "--alternate" in sys.argv
BLANC = "--blanc" in sys.argv
if __name__ == "__main__":
    for p in [a for a in sys.argv[1:] if not a.startswith("--")]:
        print(check(p), flush=True)

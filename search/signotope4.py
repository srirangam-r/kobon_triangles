"""Derive the 4-line rule table empirically from real line arrangements.

Lines are labelled by increasing slope. For i<j<k, chi(i,j,k) = +1 if the
crossing of lines i and k lies above line j, else -1. For 4 lines a<b<c<d the
sign vector (chi(bcd), chi(acd), chi(abd), chi(abc)) should have at most one
sign change (the signotope axiom), and each pattern fixes which of the four
triples bound an uncrossed triangle. Uses the hill's exact counter.
"""
import random
import sys
from fractions import Fraction
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".autolab" / "hills" / "kobon-triangles"))
from eval import count_triangles  # noqa: E402


def chi(lines, i, j, k):
    (mi, bi), (mj, bj), (mk, bk) = lines[i], lines[j], lines[k]
    x = (bk - bi) / (mi - mk)
    y = mi * x + bi
    if y == mj * x + bj:
        return 0  # three lines through one point: not a simple arrangement
    return 1 if y > mj * x + bj else -1


table = {}
rng = random.Random(1)
for _ in range(20000):
    slopes = sorted(rng.sample(range(-60, 61), 4))
    lines = [(Fraction(m, 7), Fraction(rng.randint(-60, 60), 7)) for m in slopes]
    a, b, c, d = range(4)
    vec = (chi(lines, b, c, d), chi(lines, a, c, d), chi(lines, a, b, d), chi(lines, a, b, c))
    if 0 in vec:
        continue
    int_lines = []
    for m, q in lines:  # y = m x + q  ->  m x - y + q = 0, cleared of denominators
        den = m.denominator * q.denominator
        int_lines.append((int(m * den), -den, int(q * den)))
    tris = frozenset(tuple(t) for t in count_triangles(int_lines))
    if vec in table:
        assert table[vec] == tris, (vec, table[vec], tris)
    table[vec] = tris
changes = lambda v: sum(v[i] != v[i + 1] for i in range(3))
print(len(table), "sign patterns seen; all have <= 1 sign change:", all(changes(v) <= 1 for v in table))
names = {(1, 2, 3): "bcd", (0, 2, 3): "acd", (0, 1, 3): "abd", (0, 1, 2): "abc"}
for vec in sorted(table):
    print(vec, "triangles:", sorted(names[t] for t in table[vec]))

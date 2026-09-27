"""Which 3-valued sign patterns do real 4-line arrangements produce, concurrencies included?

Lines labelled by increasing slope (distinct slopes; parallels are removable by a
projective map). chi(i,j,k) for i<j<k: +1 if the crossing of i and k lies above
line j, 0 if all three pass through one point, -1 if below. Also checks how the
side of the other two vertices relates to chi, which the SAT model needs:
    side(line c; vertex a∩b) and side(line a; vertex b∩c) as functions of chi(a,b,c).
Samples three concurrency types on purpose: none, one triple point, all four.
"""
import random
from fractions import Fraction as F
from itertools import combinations


def side(line, p):
    m, q = line
    y = m * p[0] + q
    return (p[1] > y) - (p[1] < y)


def meet(l1, l2):
    (m1, q1), (m2, q2) = l1, l2
    x = (q2 - q1) / (m1 - m2)
    return x, m1 * x + q1


def chi(lines, i, j, k):
    return side(lines[j], meet(lines[i], lines[k]))


def through(point, slope):
    return slope, point[1] - slope * point[0]


rng = random.Random(7)
patterns, side_rel = {}, set()
for trial in range(60000):
    slopes = sorted(F(s, 11) for s in rng.sample(range(-200, 201), 4))
    kind = trial % 3
    if kind == 0:
        lines = [(m, F(rng.randint(-90, 90), 13)) for m in slopes]
    elif kind == 1:
        p = (F(rng.randint(-50, 50), 7), F(rng.randint(-50, 50), 7))
        trip = rng.sample(range(4), 3)
        lines = [through(p, m) if idx in trip else (m, F(rng.randint(-90, 90), 13)) for idx, m in enumerate(slopes)]
    else:
        p = (F(rng.randint(-50, 50), 7), F(rng.randint(-50, 50), 7))
        lines = [through(p, m) for m in slopes]
    for a, b, c in combinations(range(4), 3):
        x = chi(lines, a, b, c)
        side_rel.add((x, side(lines[c], meet(lines[a], lines[b])), side(lines[a], meet(lines[b], lines[c]))))
    a, b, c, d = range(4)
    vec = (chi(lines, b, c, d), chi(lines, a, c, d), chi(lines, a, b, d), chi(lines, a, b, c))
    patterns[vec] = patterns.get(vec, 0) + 1

print("side relations (chi(abc), side(c; a∩b), side(a; b∩c)):", sorted(side_rel))
print(len(patterns), "realizable 4-line patterns (bcd, acd, abd, abc):")
for v in sorted(patterns):
    print("  ", v, patterns[v])

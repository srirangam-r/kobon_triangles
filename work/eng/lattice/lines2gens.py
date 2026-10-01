# Exact straight-line arrangement -> wiring word (gens), concurrency preserved. Lines are projective integer
# vectors (a, b, c): a x + b y + c z = 0. A projective map z' = z + e1 x + e2 y removes parallels (old points at
# infinity become finite far points). Sweep by X, ties by Y (tilted sweep).
import sys
from fractions import Fraction as F
from itertools import combinations
sys.path.insert(0, "/home/nail/stuff/sundai_math/work/t3")

def transform(lines, e1, e2):
    # point (x,y,z) -> (x, y, z + e1 x + e2 y); line l . p = 0 -> l' = l M^{-1}; M^{-1}: z = z' - e1 x - e2 y
    out = []
    for (a, b, c) in lines:
        out.append((a - c * e1, b - c * e2, c))
    return out

def meet(l1, l2):
    a, b, c = l1; d, e, f = l2
    x, y, z = b*f - c*e, c*d - a*f, a*e - b*d
    if z == 0: return None
    return (F(x, z), F(y, z))

def to_gens(lines):
    n = len(lines)
    for (a, b, c) in lines: assert b != 0, "vertical line"
    pts = {}
    for i, j in combinations(range(n), 2):
        p = meet(lines[i], lines[j]); assert p is not None, "parallel pair"
        pts.setdefault(p, set()).update((i, j))
    slope = lambda l: F(-l[0], l[1])
    order = sorted(range(n), key=lambda i: slope(lines[i]))       # track 0 = top = smallest slope at X -> -inf
    assert len(set(slope(l) for l in lines)) == n
    toks = []; mults = []
    for p in sorted(pts, key=lambda p: (p[0], p[1])):
        L = pts[p]; tr = sorted(order.index(i) for i in L)
        assert tr == list(range(tr[0], tr[0] + len(tr))), ("not consecutive", p, tr)
        g = tr[0]; m = len(tr)
        toks.append(str(g) + "*" * (m - 2)); mults.append(m)
        order[g:g+m] = list(reversed(order[g:g+m]))
    return " ".join(toks), mults

if __name__ == "__main__":
    from arr import Arr
    import random
    # self-test against the hill's exact counter on random integer lines
    sys.path.insert(0, ".")
    from hill_eval import count_triangles
    rng = random.Random(1)
    for t in range(20):
        ls = [(rng.randint(-9, 9), rng.randint(1, 9), rng.randint(-20, 20)) for _ in range(9)]
        try:
            g, _ = to_gens(ls)
        except AssertionError:
            continue
        T1 = Arr(g, len(ls)).T(); T2 = len(count_triangles(ls))
        assert T1 == T2, (T1, T2, ls)
    print("self-test OK")

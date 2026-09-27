"""Structure of an arrangement: the counting identity behind the Kobon bounds.

For exact integer lines, compute the triangles, the multiple points (k lines through
one point), each line's bounded segments, and how many triangles use each segment:
    Z = unused bounded segments, D = segments that are a side of two triangles.
Identity (no parallels): 3T = n(n-2) - Lambda, Lambda = Z - D + sum_P k_P(k_P - 2).
At 18 lines, 94 triangles means Lambda <= 6; every 93 has Lambda = 9.

    python3 search/structure.py <solution.json> [...]
"""
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".autolab" / "hills" / "kobon-triangles"))
from eval import _intersection, _normalize, count_triangles  # noqa: E402


def stats(lines):
    lines = [_normalize(tuple(l)) for l in lines]
    n = len(lines)
    tris = count_triangles(lines)
    pts = {}
    on_line = [dict() for _ in range(n)]
    parallel_pairs = 0
    for i in range(n):
        for j in range(i + 1, n):
            p = _intersection(lines[i], lines[j])
            if p is None:
                parallel_pairs += 1
                continue
            pts.setdefault(p, set()).update((i, j))
            on_line[i][p] = True
            on_line[j][p] = True
    order = []
    for i, line in enumerate(lines):
        axis = 0 if line[1] else 1
        order.append(sorted(on_line[i], key=lambda p: Fraction(p[axis], p[2])))
    seg_use = Counter()
    for i, j, k in tris:
        for a, b, c in ((i, j, k), (j, i, k), (k, i, j)):  # side of triangle on line a
            p, q = _intersection(lines[a], lines[b]), _intersection(lines[a], lines[c])
            ra, rb = order[a].index(p), order[a].index(q)
            seg_use[a, min(ra, rb)] += 1
    segments = sum(max(0, len(o) - 1) for o in order)
    uses = [seg_use.get((a, s), 0) for a in range(n) for s in range(max(0, len(order[a]) - 1))]
    Z, D = uses.count(0), uses.count(2)
    mult = Counter(len(v) for v in pts.values() if len(v) >= 3)
    charge = sum(k * (k - 2) * c for k, c in mult.items())
    lam = Z - D + charge + 2 * parallel_pairs
    return {"n": n, "T": len(tris), "segments": segments, "Z": Z, "D": D,
            "multiple_points": dict(sorted(mult.items())), "parallel_pairs": parallel_pairs,
            "Lambda": lam, "identity_ok": 3 * len(tris) == n * (n - 2) - lam}


if __name__ == "__main__":
    for path in sys.argv[1:]:
        print(path, stats(json.loads(Path(path).read_text())["lines"]))

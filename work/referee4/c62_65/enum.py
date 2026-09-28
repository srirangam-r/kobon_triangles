"""Exhaustive enumeration of rank-3 signotopes with zeros on n elements (4-element patterns from
search/kobon_sat.allowed4, 4-fold points excluded), then the C62-C65 checks of struct.check.
    python3 enum.py N [simple]"""
import sys
from collections import Counter
from itertools import combinations
sys.path.insert(0, '/home/nail/stuff/sundai_math/search')
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee4/c62_65')
from kobon_sat import allowed4
from struct_ import Arr, check  # noqa

n = int(sys.argv[1])
simple = len(sys.argv) > 2 and sys.argv[2] == 'simple'
ok = {v for v in allowed4() if v != (0, 0, 0, 0)}
trips = list(combinations(range(n), 3))
tidx = {t: k for k, t in enumerate(trips)}
checks = {k: [] for k in range(len(trips))}
for a, b, c, d in combinations(range(n), 4):
    ts = [(b, c, d), (a, c, d), (a, b, d), (a, b, c)]
    last = max(tidx[t] for t in ts)
    checks[last].append([tidx[t] for t in ts])
vals = (-1, 1) if simple else (-1, 0, 1)
cur = [None] * len(trips)
st, bad = Counter(), []
count = 0


def rec(k):
    global count
    if k == len(trips):
        count += 1
        sigma = {t: cur[tidx[t]] for t in trips}
        A = Arr(n, sigma)
        check(A, st, bad, f'#{count}')
        return
    for v in vals:
        cur[k] = v
        if all(tuple(cur[x] for x in q) in ok for q in checks[k]):
            rec(k + 1)
    cur[k] = None


rec(0)
print(f'n={n} simple={simple}: {count} signotopes')
for key in sorted(st, key=str):
    print(f'  {st[key]:8d} {key}')
print('FAILS', len(bad))
for b in bad[:10]:
    print('  ', b)

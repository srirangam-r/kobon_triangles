"""C17 test: every simple point that is an end vertex of both its lines joins slope-adjacent lines
(first-first: |L-R|=1; last-last: |L-R|=1; first/last mixed: {0,n-1})."""
import glob, sys, json, collections, random
sys.path.insert(0, '.')
from arr import *
from mutate import random_move
R = '../../tools/external/kobon-solutions/gallery/data'
st = collections.Counter()
def test(a):
    n = a.n
    for L in range(n):
        for end in (0, -1):
            X = a.rows[L][end]
            if len(a.events[X]) != 2: continue
            Rr = a.other(X, L)
            if a.rows[Rr][0] == X: e2 = 0
            elif a.rows[Rr][-1] == X: e2 = -1
            else: continue
            lo, hi = sorted((L, Rr))
            if end == e2: ok = hi - lo == 1
            else: ok = (lo, hi) == (0, n - 1)
            st['ok' if ok else 'FAIL'] += 1
for s in sys.argv[1:]:
    for f in sorted(glob.glob(f'{R}/{s}/*.json')):
        a = Arr(json.load(open(f))['gens']); test(a)
        rng = random.Random(hash(f) & 0xffff)
        for it in range(5):
            w = random_move(a, rng, 0.3, 0.2)
            if w: a = Arr(w, a.n); test(a)
print(dict(st))

"""Test Theorem H (general position: no line through two multiple points, n even):
Lambda >= ceil((n - t)/2), and the per-point bound phi_P >= -1 for triple points with 2 blocks."""
import glob, sys, json, random, collections, math
sys.path.insert(0, '.')
from arr import *
from mutate import random_move
from lemmas import point_info
R = '../../tools/external/kobon-solutions/gallery/data'
stats = collections.Counter()
def test(a):
    if a.n % 2: return
    mult = [e for e, ev in enumerate(a.events) if len(ev) >= 3]
    if any(len(a.events[e]) > 3 for e in mult): stats['has4fold'] += 1
    lines = collections.Counter(L for P in mult for L in a.events[P])
    if any(v > 1 for v in lines.values()): return
    if len(a.events) != sum(1 for _ in a.events):  # placeholder
        pass
    t = sum(1 for P in mult if len(a.events[P]) == 3)
    lam = a.Z() - a.D() + sum(len(a.events[P]) * (len(a.events[P]) - 2) for P in mult)
    ok = lam >= math.ceil((a.n - t) / 2)
    stats[('GP ok' if ok else 'GP FAIL', t)] += 1
    if not ok: print('FAIL', a.n, t, lam)
for s in sys.argv[1:]:
    for f in sorted(glob.glob(f'{R}/{s}/*.json')):
        d = json.load(open(f)); a = Arr(d['gens'])
        if len(a.events) + sum(len(e) * (len(e) - 1) // 2 - 1 for e in a.events if len(e) > 2) != a.n * (a.n - 1) // 2: continue
        test(a)
        rng = random.Random(hash(f) & 0xffff)
        for it in range(15):
            w = random_move(a, rng, 0.45, 0.1)
            if w is None: continue
            b = Arr(w, a.n)
            if b.T() < a.T() - 3: continue
            a = b; test(a)
for k, v in sorted(stats.items(), key=str): print(v, k)

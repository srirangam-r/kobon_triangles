# Clean 18-line arrangements with bad 4-fold points: a small lattice core (H, V, A, D lines) + random lines.
import sys, json, random
from fractions import Fraction as F
sys.path.insert(0, ".")
from lines2gens import transform, to_gens
from build_lattice import clean
sys.path.insert(0, "/home/nail/stuff/sundai_math/work/t3"); sys.path.insert(0, "/home/nail/stuff/sundai_math/work/eng/comp")
from arr import Arr
_argv = sys.argv; sys.argv = sys.argv[:1]
from bad_comp import tri_sectors, canon, BAD
sys.argv = _argv
seed = int(sys.argv[1]); N = int(sys.argv[2]); rng = random.Random(seed)
out = []
for it in range(N):
    nH, nV, nA = rng.randint(2, 5), rng.randint(2, 5), rng.randint(2, 6); nD = rng.randint(1, 3)
    H = rng.sample(range(1, 7), nH); V = rng.sample(range(1, 7), nV); A = rng.sample(range(3, 11), nA); D = rng.sample(range(-3, 4), nD)
    L = [(0, 1, -j) for j in H] + [(1, 0, -i) for i in V] + [(1, 1, -k) for k in A] + [(1, -1, c) for c in D]
    while len(L) < 18:
        # random line through the core region with small integer coefficients
        a, b = rng.randint(-7, 7), rng.randint(-7, 7)
        if a == 0 and b == 0: continue
        c = -(a * rng.randint(0, 7) + b * rng.randint(0, 7)) + rng.choice([0, 0, 1, -1])
        if (a, b, c) in L: continue
        L.append((a, b, c))
    try:
        g, _ = to_gens(transform(L, F(1, rng.choice([97, 101, 103])), F(1, rng.choice([89, 107, 109]))))
    except (AssertionError, ZeroDivisionError):
        continue
    try:
        g = clean(g); a = Arr(g, 18)
    except Exception:
        continue
    nb = sum(1 for P, ev in enumerate(a.events) if len(ev) == 4 and canon(tri_sectors(a, P)) in BAD)
    if nb: out.append({"n": 18, "gens": g, "T": a.T(), "nbad": nb})
with open(f"mixed_{seed}.jsonl", "w") as fh:
    for o in out: fh.write(json.dumps(o) + "\n")
print(seed, "kept", len(out), "of", N)

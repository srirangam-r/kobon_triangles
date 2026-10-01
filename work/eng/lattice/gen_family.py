import random, json, sys
sys.path.insert(0, ".")
from build_lattice import build, cluster_stats
from fractions import Fraction as F
rng = random.Random(11); out = []; seen = set(); tries = 0
while len(out) < 250 and tries < 3000:
    tries += 1
    nD = rng.randint(1, 5); nA = rng.randint(3, 7); nH = rng.randint(3, 6); nV = 18 - nD - nA - nH
    if nV < 3 or nV > 7: continue
    H = tuple(sorted(rng.sample(range(1, 9), nH))); V = tuple(sorted(rng.sample(range(1, 9), nV)))
    A = tuple(sorted(rng.sample(range(2, 15), nA))); D = tuple(sorted(rng.sample(range(-5, 6), nD)))
    key = (H, V, A, D)
    if key in seen: continue
    seen.add(key)
    e1 = F(1, rng.choice([89, 97, 101, 103])); e2 = F(1, rng.choice([83, 107, 109, 113]))
    try:
        g, n = build(H, V, A, D, e1, e2)
    except AssertionError:
        continue
    T, c8, adj, mult = cluster_stats(g)
    if adj == 0: continue
    out.append({"n": 18, "gens": g, "T": T, "all8": c8, "adj": adj, "src": f"lattice H{H} V{V} A{A} D{D}"})
with open("lattice_family.jsonl", "w") as f:
    for o in out: f.write(json.dumps(o) + "\n")
Ts = sorted(o["T"] for o in out)
print("arrangements", len(out), "tries", tries, "T range", Ts[0], Ts[-1], "adjacencies total", sum(o["adj"] for o in out))

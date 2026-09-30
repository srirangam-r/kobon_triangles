# random search for a local arrangement W_m of m pseudolines (simple wiring word of w0) with
# tloc - #affected sectors >= 0, i.e. lossless for EVERY sector pattern.
import random, sys
from pert import faces
def rand_word(m, rng):
    perm = list(range(m)); w = []
    while True:
        cand = [i for i in range(m-1) if perm[i] < perm[i+1]]
        if not cand: return w
        i = rng.choice(cand); perm[i], perm[i+1] = perm[i+1], perm[i]; w.append((i, i+1))
m = int(sys.argv[1]); N = int(sys.argv[2]); rng = random.Random(1)
best = None
for it in range(N):
    w = rand_word(m, rng)
    e, t, mm = faces(m, w)
    sc = t - sum(1 for x in e if x > 0)
    if best is None or sc > best[0]:
        best = (sc, t, e, w); print(it, sc, t, e, flush=True)
    if sc >= 0 and it > 1000: break
print("BEST", best)

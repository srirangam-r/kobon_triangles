# m = 6: gather local arrangements (random words with multi-crossing letters) and check that every
# sector pattern Tri (2^12) has an option with tloc - |Tri ∩ supp e| >= 0.
import random, sys
from pert import faces
m = int(sys.argv[1]); N = int(sys.argv[2]); rng = random.Random(7)
def rand_word(pmulti):
    perm = list(range(m)); w = []
    while True:
        cand = [i for i in range(m-1) if perm[i] < perm[i+1]]
        if not cand: return w
        i = rng.choice(cand); j = i + 1
        while rng.random() < pmulti and j+1 < m and all(perm[k] < perm[k+1] for k in range(i, j+1)):
            j += 1
        if (i, j) == (0, m-1): continue
        perm[i:j+1] = perm[i:j+1][::-1]; w.append((i, j))
opts = {}
for it in range(N):
    w = rand_word(rng.choice([0.0, 0.2, 0.5]))
    e, t, mm = faces(m, w)
    key = (sum(1 << s for s in range(2*m) if e[s] > 0), t)
    if key not in opts: opts[key] = w
print("distinct options", len(opts))
# prune dominated
ol = list(opts)
unc = []
for mask in range(1 << (2*m)):
    if not any(t - bin(mask & sup).count("1") >= 0 for sup, t in ol):
        unc.append(mask)
print("uncovered patterns", len(unc))
for u in unc[:20]:
    print("  ", format(u, f"0{2*m}b")[::-1], bin(u).count("1"))

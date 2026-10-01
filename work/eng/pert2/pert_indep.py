# Independent re-check of the perturbation lemma (THEORY section 24) with faces_indep:
#  m = 6: random multi-letter words cover every sector pattern with a lossless option;
#  7 <= m <= 17: some simple word has t_loc >= #affected sectors (lossless for every pattern).
import random, sys
from faces_indep import faces_indep
def sector_extras(m, vec):
    top, bot = vec[0], vec[1]; Lf = vec[2:2 + m - 1]; Rf = vec[2 + m - 1:]
    return (top - 1,) + tuple(x - 1 for x in Rf) + (bot - 1,) + tuple(x - 1 for x in Lf[::-1])
def rand_word(m, rng, pmulti):
    perm = list(range(m)); w = []
    while True:
        cand = [i for i in range(m - 1) if perm[i] < perm[i + 1]]
        if not cand: return w
        i = rng.choice(cand); j = i + 1
        while rng.random() < pmulti and j + 1 < m and all(perm[k] < perm[k + 1] for k in range(i, j + 1)): j += 1
        if (i, j) == (0, m - 1): continue
        perm[i:j + 1] = perm[i:j + 1][::-1]; w.append((i, j))
rng = random.Random(11)
m = 6; opts = set()
for it in range(60000):
    w = rand_word(m, rng, rng.choice([0.0, 0.2, 0.5]))
    v, t, _ = faces_indep(m, w); e = sector_extras(m, v)
    opts.add((sum(1 << s for s in range(2 * m) if e[s] > 0), t))
unc = [mask for mask in range(1 << (2 * m)) if not any(t - bin(mask & sup).count("1") >= 0 for sup, t in opts)]
print("m=6 options", len(opts), "uncovered patterns", len(unc), flush=True)
for m in range(7, 18):
    best = None
    for it in range(4000):
        w = rand_word(m, rng, 0.0)
        v, t, _ = faces_indep(m, w); e = sector_extras(m, v)
        sc = t - sum(1 for x in e if x > 0)
        best = sc if best is None else max(best, sc)
        if best >= 0 and it > 200: break
    print("m", m, "best score (t_loc - affected)", best, flush=True)

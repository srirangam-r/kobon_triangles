"""Perturbation-lemma coverage for m = lo..hi: search a simple wiring word W_m with t_loc - #affected sectors >= 0 (lossless for every sector pattern).
Score computed by pert.faces (e, t) and independently by pert2/faces_indep (sector_extras convention of pert_indep.py); both must agree on >= 0.
usage: pert_cover.py lo hi [maxiter]"""
import random, sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "work/eng/pert")); sys.path.insert(0, str(ROOT / "work/eng/pert2"))
from pert import faces
from faces_indep import faces_indep
def sector_extras(m, vec):
    top, bot = vec[0], vec[1]; Lf = vec[2:2 + m - 1]; Rf = vec[2 + m - 1:]
    return (top - 1,) + tuple(x - 1 for x in Rf) + (bot - 1,) + tuple(x - 1 for x in Lf[::-1])
def rand_word(m, rng):
    perm = list(range(m)); w = []
    while True:
        cand = [i for i in range(m - 1) if perm[i] < perm[i + 1]]
        if not cand: return w
        i = rng.choice(cand); perm[i], perm[i + 1] = perm[i + 1], perm[i]; w.append((i, i + 1))
lo, hi = int(sys.argv[1]), int(sys.argv[2]); N = int(sys.argv[3]) if len(sys.argv) > 3 else 20000
rng = random.Random(11)
for m in range(lo, hi + 1):
    best = None
    for it in range(N):
        w = rand_word(m, rng)
        v, t, _ = faces_indep(m, w); e = sector_extras(m, v)
        sc = t - sum(1 for x in e if x > 0)
        if best is None or sc > best[0]: best = (sc, t, w)
        if sc >= 0 and it >= 20: break
    sc, t, w = best
    e2, t2, _ = faces(m, w); sc2 = t2 - sum(1 for x in e2 if x > 0)
    print(f"m {m} iters {it+1} score_indep {sc} score_pert {sc2} t_loc {t} word {json.dumps(w)}", flush=True)

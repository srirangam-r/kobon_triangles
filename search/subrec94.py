"""Count triangles of every 18-line sub-arrangement of larger gallery records (delete n-18 lines).
Constructive check, exact: chi restricted to the kept lines, counted with kobon_sat.count_general.

    python search/subrec94.py <n> [max_subsets_per_record] [workers]
"""
import glob, json, random, sys
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
from base2 import chi_from_word
from kobon_sat import count_general


def work(args):
    name, gens, n, subsets = args
    chi = chi_from_word(gens, n)
    best, hits = 0, []
    for R in subsets:
        keep = [x for x in range(n) if x not in R]
        idx = {x: i for i, x in enumerate(keep)}
        c = {tuple(idx[x] for x in t): v for t, v in chi.items() if not set(t) & set(R)}
        T = len(count_general(18, c))
        best = max(best, T)
        if T >= 94:
            hits.append((R, T))
    return name, best, hits


def main():
    n = int(sys.argv[1]); cap = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 9
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    jobs = []
    for f in sorted(glob.glob(str(ROOT / f"tools/external/kobon-solutions/gallery/data/{n}/*.json"))):
        gens = json.load(open(f))["gens"]
        subs = list(combinations(range(n), n - 18))
        if len(subs) > cap:
            subs = random.Random(f).sample(subs, cap)
        jobs.append((Path(f).name, gens, n, subs))
    dist = {}
    with Pool(workers) as p:
        for name, best, hits in p.imap_unordered(work, jobs):
            dist[best] = dist.get(best, 0) + 1
            for R, T in hits:
                print("HIT", name, R, T, flush=True)
    print(f"n={n}: {len(jobs)} records; best 18-line sub-arrangement T per record: {dict(sorted(dist.items()))}")


if __name__ == "__main__":
    main()

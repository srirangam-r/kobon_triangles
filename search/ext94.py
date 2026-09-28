"""Extension search (constructive; not a proof tool): insert new pseudolines into a record arrangement with fewer
lines and ask for >= TARGET triangles at n = 18. The old lines keep their relative slope order; the new lines get
slope ranks `ranks` (a sorted tuple), old signs are fixed by assumptions, and every call runs to completion (no
conflict budget), so each (base, ranks, orientation) gets a definite SAT/UNSAT.

    uv run --no-project --with python-sat python search/ext94.py <out.jsonl> <n0> <target> [kmax] [shard/nshards] [max_base]
"""
import glob
import json
import sys
import time
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.append(str(ROOT / "work/t3"))
from arr import Arr  # noqa: E402
from base2 import chi_from_word  # noqa: E402
from kobon_sat import build_defect, count_general  # noqa: E402
from pysat.solvers import Solver  # noqa: E402

n = 18


def main():
    out, n0, target = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    kmax = int(sys.argv[4]) if len(sys.argv) > 4 else 20
    shard, nsh = (map(int, sys.argv[5].split("/")) if len(sys.argv) > 5 else (0, 1))
    max_base = int(sys.argv[6]) if len(sys.argv) > 6 else 10 ** 9
    bases = []
    for f in sorted(glob.glob(str(ROOT / f"tools/external/kobon-solutions/gallery/data/{n0}/*.json"))):
        d = json.load(open(f))
        a = Arr(d["gens"])
        if a.n == n0 and not any(len(e) > 3 for e in a.events):
            bases.append((Path(f).name, d["gens"], a.T()))
    bases = bases[:max_base]
    cnf, z, pz, ng, tri, budget = build_defect(n, target, kmax, alternate=True, card="cardnetwrk")
    assert budget >= n
    trip = list(combinations(range(n), 3))
    jobs = [(b, R, s) for b in range(len(bases)) for R in combinations(range(n), n - n0) for s in (1, -1)]
    log = open(out, "a")
    t0 = time.time()
    with Solver(name="cadical153", bootstrap_with=cnf.clauses) as sv:
        for ji, (b, R, sgn) in enumerate(jobs):
            if ji % nsh != shard:
                continue
            name, gens, T0 = bases[b]
            chi0 = chi_from_word(gens, n0)
            old = [x for x in range(n) if x not in R]  # new label of old line i is old[i]
            assum = []
            for t in combinations(range(n0), 3):
                v = sgn * chi0[t]
                u = tuple(old[i] for i in t)
                assum.append(z[u] if v == 0 else pz[u] if v == 1 else ng[u])
            t1 = time.time()
            res = sv.solve(assumptions=assum)
            rec = {"base": name, "T0": T0, "ranks": R, "sign": sgn, "res": "SAT" if res else "UNSAT",
                   "secs": round(time.time() - t1, 2)}
            if res:
                m = set(v for v in sv.get_model() if v > 0)
                chi = {t: (0 if z[t] in m else 1 if pz[t] in m else -1) for t in trip}
                rec["T"] = len(count_general(n, chi))
                rec["chi"] = {",".join(map(str, t)): v for t, v in chi.items()}
                print(f"SAT {name} ranks={R} sign={sgn} T={rec['T']}", flush=True)
            log.write(json.dumps(rec) + "\n")
            log.flush()
    print(f"shard {shard}: done in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()

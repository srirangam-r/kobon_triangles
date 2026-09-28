"""Large-neighbourhood SAT search for a 94 near known 93s (constructive; not a proof tool).
Base: kobon_sat.build_defect(18, 94, max_triple=KMAX) (pseudoline model, exact triangle rule, >= 94 triangles).
For a gallery 93 and a set R of removed lines, the signs of all triples avoiding R are fixed by assumptions and
the solver re-places the lines of R (same slope ranks) as pseudolines. A SAT answer is re-counted with
count_general and saved; realizability is checked separately.

    uv run --no-project --with python-sat python search/lns94.py <out.jsonl> <r> <k-list> [max_arr] [conf_budget] [shard/nshards]
"""
import glob
import json
import random
import sys
import time
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.insert(0, str(ROOT / "work/t3"))
from arr import Arr  # noqa: E402
from base2 import chi_from_word  # noqa: E402
from kobon_sat import build_defect, count_general  # noqa: E402
from pysat.solvers import Solver  # noqa: E402

import os  # noqa: E402
n, KMAX = 18, 12
TARGET = int(os.environ.get("LNS_TARGET", "94"))


def gallery(ks):
    seeds = os.environ.get("LNS_SEEDS")  # "file.json:key" -> only these gallery names (any k)
    names = set(json.load(open(seeds.split(":")[0]))[seeds.split(":")[1]]) if seeds else None
    out = []
    for f in sorted(glob.glob(str(ROOT / "tools/external/kobon-solutions/gallery/data/18/*.json"))):
        d = json.load(open(f))
        a = Arr(d["gens"])
        if names is not None and Path(f).name not in names:
            continue
        if a.T() == 93 and (names is not None or len(a.triples) in ks) and not any(len(e) > 3 for e in a.events):
            out.append((Path(f).name, d["gens"], len(a.triples)))
    return out


def main():
    out, r, ks = sys.argv[1], int(sys.argv[2]), {int(x) for x in sys.argv[3].split(",")}
    max_arr = int(sys.argv[4]) if len(sys.argv) > 4 else 10 ** 9
    budget = int(sys.argv[5]) if len(sys.argv) > 5 else 200000
    shard, nsh = (map(int, sys.argv[6].split("/")) if len(sys.argv) > 6 else (0, 1))
    cnf, z, pz, ng, tri, _ = build_defect(n, TARGET, KMAX, alternate=True, card="cardnetwrk")
    arrs = gallery(ks)
    random.Random(1).shuffle(arrs)
    arrs = arrs[:max_arr]
    trip = list(combinations(range(n), 3))
    log = open(out, "a")
    with Solver(name="cadical153", bootstrap_with=cnf.clauses) as sv:
        for ai, (name, gens, k) in enumerate(arrs):
            chi = chi_from_word(gens, n)
            if chi[0, 1, 2] == -1:  # model symmetry break: use the 180-degree rotation (all signs flipped)
                chi = {t: -v for t, v in chi.items()}
            lit = {t: (z[t] if chi[t] == 0 else pz[t] if chi[t] == 1 else ng[t]) for t in trip}
            subsets = list(combinations(range(n), r))
            stats = {"UNSAT": 0, "SAT": 0, "UNKNOWN": 0}
            t0 = time.time()
            for si, R in enumerate(subsets):
                if si % nsh != shard:
                    continue
                Rs = set(R)
                assum = [lit[t] for t in trip if not (Rs & set(t))]
                sv.conf_budget(budget)
                res = sv.solve_limited(assumptions=assum)
                if res is None:
                    stats["UNKNOWN"] += 1
                elif not res:
                    stats["UNSAT"] += 1
                else:
                    stats["SAT"] += 1
                    m = set(v for v in sv.get_model() if v > 0)
                    chi2 = {t: (0 if z[t] in m else 1 if pz[t] in m else -1) for t in trip}
                    T = len(count_general(n, chi2))
                    log.write(json.dumps({"base": name, "k": k, "removed": R, "T": T,
                                          "chi": {",".join(map(str, t)): v for t, v in chi2.items()}}) + "\n")
                    log.flush()
                    print(f"SAT {name} R={R} T={T}", flush=True)
            print(f"{name} k={k} r={r}: {stats} {time.time() - t0:.0f}s", flush=True)
            log.write(json.dumps({"base": name, "k": k, "r": r, "shard": shard, "stats": stats}) + "\n")
            log.flush()


if __name__ == "__main__":
    main()

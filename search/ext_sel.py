"""One-call extension search: all slope-rank placements of the new lines in a single SAT instance.
Selector sel[(R, f)] = "the new lines get slope ranks R and the base has orientation f"; exactly one selector is
true, and each selector implies the base's fixed signs at the mapped labels. Equivalent to the union of the
per-placement calls of push94/run_ext.py, but the solver can share learned clauses across placements.
Returns SAT (with the placement) or UNSAT for the whole seed.

    python search/ext_sel.py <seeds.json> <seed-index> [solver] [--blanc]
"""
import json
import sys
import time
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "work/lns/push"))
from run_lns import chi_from_word  # noqa: E402
from kobon_sat import build_defect, count_general  # noqa: E402
from pysat.card import CardEnc, EncType  # noqa: E402
from pysat.solvers import Solver  # noqa: E402

n = 18


def add_placements(cnf, pool, z, pz, ng, chi0, n0):
    sels = {}
    for R in combinations(range(n), n - n0):
        fs = (1, -1) if set(R) & {0, 1, 2} else ((-1 if chi0[0, 1, 2] == -1 else 1),)
        old = [x for x in range(n) if x not in R]
        for f in fs:
            s = pool.id(("sel", R, f))
            sels[R, f] = s
            for t in combinations(range(n0), 3):
                v = f * chi0[t]
                u = tuple(old[i] for i in t)
                cnf.append([-s, z[u] if v == 0 else pz[u] if v == 1 else ng[u]])
    lits = list(sels.values())
    cnf.append(lits)
    cnf.extend(CardEnc.atmost(lits=lits, bound=1, vpool=pool, encoding=EncType.seqcounter).clauses)
    return sels


def main():
    seeds = json.load(open(sys.argv[1]))
    si = int(sys.argv[2])
    solver = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else "cadical153"
    seed = seeds[si]
    n0 = seed.get("n0", 16)
    t0 = time.time()
    cnf, z, pz, ng, tri, _ = build_defect(n, int(__import__("os").environ.get("EXT_TARGET", "94")), 16, alternate=True, card="cardnetwrk", blanc="--blanc" in sys.argv)
    chi0 = chi_from_word(seed["gens"], n0)
    sels = add_placements(cnf, cnf.pool, z, pz, ng, chi0, n0)
    t1 = time.time()
    with Solver(name=solver, bootstrap_with=cnf.clauses) as sv:
        res = sv.solve()
        t2 = time.time()
        out = {"seed": seed["name"], "placements": len(sels), "res": "SAT" if res else "UNSAT",
               "build_s": round(t1 - t0, 1), "solve_s": round(t2 - t1, 1), "solver": solver, "blanc": "--blanc" in sys.argv}
        if res:
            m = set(v for v in sv.get_model() if v > 0)
            out["placement"] = [k for k, v in sels.items() if v in m]
            trip = list(combinations(range(n), 3))
            c2 = {t: (0 if z[t] in m else 1 if pz[t] in m else -1) for t in trip}
            out["T"] = len(count_general(n, c2))
            out["chi"] = {",".join(map(str, t)): v for t, v in c2.items()}
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()

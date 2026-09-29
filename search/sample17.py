"""Generate bridge-rich near-optimal arrangements of n pseudolines (default 17) by SAT, then test each for a
one-line completion to 18 lines with >= 94 triangles (all 18 slope ranks, one selector call; see ext_sel.py).

Family: exactly k triple points, >= b doubly used bridges (segments between two triple points with a triangle on
each side), >= T triangles. Samples are made distinct with blocking clauses on the full sign vector and a random
phase per solve. Each completion call runs to SAT/UNSAT.

    python search/sample17.py <out.jsonl> --n 17 --T 83 --k 7 --b 3 --samples 20 [--seed 1]
"""
import argparse
import json
import random
import sys
import time
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
from kobon_sat import build_defect, count_general  # noqa: E402
from ext_sel import add_placements  # noqa: E402
from pysat.card import CardEnc, EncType  # noqa: E402
from pysat.solvers import Solver  # noqa: E402

S = lambda *x: tuple(sorted(x))


def bridges(cnf, pool, n, z, tri):
    """br -> a doubly used segment on r between triple points t1, t2 (one pairing of the two triangles)."""
    trip = list(combinations(range(n), 3))
    brs = []
    for r in range(n):
        ts = [t for t in trip if r in t]
        for t1, t2 in combinations(ts, 2):
            o1, o2 = [x for x in t1 if x != r], [y for y in t2 if y != r]
            if set(o1) & set(o2):
                continue
            (x, x2), (y, y2) = o1, o2
            for (p1, q1), (p2, q2) in (((x, y), (x2, y2)), ((x, y2), (x2, y))):
                v = pool.id(("br", r, t1, t2, p1, q1))
                cnf.extend([[-v, z[t1]], [-v, z[t2]], [-v, tri[S(r, p1, q1)]], [-v, tri[S(r, p2, q2)]]])
                brs.append(v)
    return brs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--n", type=int, default=17)
    ap.add_argument("--T", type=int, default=83)
    ap.add_argument("--k", type=int, default=7)
    ap.add_argument("--b", type=int, default=3)
    ap.add_argument("--samples", type=int, default=20)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    n = a.n
    rng = random.Random(a.seed)
    cnf, z, pz, ng, tri, budget = build_defect(n, a.T, a.k, alternate=True, card="cardnetwrk", exact_triple=True, blanc=True)
    pool = cnf.pool
    brs = bridges(cnf, pool, n, z, tri)
    cnf.extend(CardEnc.atleast(lits=brs, bound=a.b, vpool=pool, encoding=EncType.seqcounter).clauses)
    trip = list(combinations(range(n), 3))
    lit = lambda t, v: z[t] if v == 0 else pz[t] if v == 1 else ng[t]
    log = open(a.out, "a")
    with Solver(name="cadical153", bootstrap_with=cnf.clauses) as sv:
        for i in range(a.samples):
            try:
                sv.set_phases([rng.choice((1, -1)) * v for v in list(pz.values()) + list(ng.values())])
            except NotImplementedError:
                pass
            t0 = time.time()
            if not sv.solve():
                print(f"family exhausted after {i} samples", flush=True)
                break
            m = set(v for v in sv.get_model() if v > 0)
            chi = {t: (0 if z[t] in m else 1 if pz[t] in m else -1) for t in trip}
            sv.add_clause([-lit(t, chi[t]) for t in trip])
            T = len(count_general(n, chi))
            t1 = time.time()
            # one-line completion to 18 lines with >= 94 triangles, all slope ranks, one call
            c2, z2, pz2, ng2, tri2, b2 = build_defect(18, 94, 16, alternate=True, card="cardnetwrk", blanc=True)
            add_placements(c2, c2.pool, z2, pz2, ng2, chi, n)
            with Solver(name="cadical153", bootstrap_with=c2.clauses) as s2:
                res = s2.solve()
                m2 = set(v for v in s2.get_model() if v > 0) if res else None
            rec = {"i": i, "n": n, "T": T, "k": a.k, "b": a.b, "sample_s": round(t1 - t0, 1), "ext_s": round(time.time() - t1, 1),
                   "ext94": "SAT" if res else "UNSAT", "chi": {",".join(map(str, t)): v for t, v in chi.items()}}
            if res:
                t18 = list(combinations(range(18), 3))
                c18 = {t: (0 if z2[t] in m2 else 1 if pz2[t] in m2 else -1) for t in t18}
                rec["T18"] = len(count_general(18, c18))
                rec["chi18"] = {",".join(map(str, t)): v for t, v in c18.items()}
            log.write(json.dumps(rec) + "\n")
            log.flush()
            print(f"sample {i}: T={T} ({rec['sample_s']}s) -> 94-completion {rec['ext94']} ({rec['ext_s']}s)", flush=True)


if __name__ == "__main__":
    main()

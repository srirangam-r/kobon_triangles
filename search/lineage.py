"""Bridge-core lineage: grow a record arrangement two lines at a time with SAT, keeping record-level extensions.

One step: base chi on n0 lines -> all distinct (up to end-circle symmetry) extensions by `add` new pseudolines at
any slope ranks with >= target triangles (one selector per placement, see search/ext_sel.py; blocking clauses on
the new lines' signs enumerate further solutions, up to --cap per base). Output jsonl rows {name, n, T, k, chi}.
Every solve runs to completion (no budget), so each step is exhaustive up to the cap.

    python search/lineage.py step <in.jsonl|gallery:<n>/<file.json>> <out.jsonl> <target> [--add 2] [--cap 200] [--workers 4]
"""
import argparse
import json
import sys
import time
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.insert(1, str(ROOT / "work/lns/push"))
from run_lns import chi_from_word  # noqa: E402
from kobon_sat import build_defect, count_general  # noqa: E402
from symmetry import actions  # noqa: E402
from pysat.card import CardEnc, EncType  # noqa: E402
from pysat.solvers import Solver  # noqa: E402

_MAPS = {}


def canon(chi, n):
    if n not in _MAPS:
        _MAPS[n] = [g.signed_map(n) for g in actions(n)]
    trip = list(combinations(range(n), 3))
    best = None
    for m in _MAPS[n]:
        for s in (1, -1):
            key = tuple(s * m[t][1] * chi[m[t][0]] for t in trip)
            if best is None or key < best:
                best = key
    return best


def extend(args):
    name, chi0, n0, add, target, cap, stream = args
    n = n0 + add
    cnf, z, pz, ng, tri, budget = build_defect(n, target, 16, alternate=True, card="cardnetwrk", blanc=True)
    assert budget >= n
    pool = cnf.pool
    sels = {}
    for R in combinations(range(n), add):
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
    trip = list(combinations(range(n), 3))
    lit = lambda t, v: z[t] if v == 0 else pz[t] if v == 1 else ng[t]
    out, seen = [], set()
    t0 = time.time()
    with Solver(name="cadical153", bootstrap_with=cnf.clauses) as sv:
        while len(out) < cap and sv.solve():
            m = set(v for v in sv.get_model() if v > 0)
            chi = {t: (0 if z[t] in m else 1 if pz[t] in m else -1) for t in trip}
            R = next(k[0] for k, v in sels.items() if v in m)
            new = [t for t in trip if set(t) & set(R)]
            f = next(k[1] for k, v in sels.items() if v in m)
            sv.add_clause([-lit(t, chi[t]) for t in new] + [-sels[R, f]])  # block this completion of this placement
            c = canon(chi, n)
            if c in seen:
                continue
            seen.add(c)
            T = len(count_general(n, chi))
            k = sum(1 for v in chi.values() if v == 0)
            rec = {"name": f"{name}+{R}", "n": n, "T": T, "k": k, "chi": {",".join(map(str, t)): v for t, v in chi.items()}}
            out.append(rec)
            with open(stream, "a") as fs_:  # progress survives interruption
                fs_.write(json.dumps(rec) + "\n")
    return name, out, round(time.time() - t0, 1)


def load(src):
    if src.startswith("gallery:"):
        f = ROOT / "tools/external/kobon-solutions/gallery/data" / src[8:]
        gens = json.load(open(f))["gens"]
        n = 1 + max(int(t.rstrip("*")) + (2 if t.endswith("*") else 1) for t in gens.split())
        return [(f.name, chi_from_word(gens, n), n)]
    rows = [json.loads(l) for l in open(src)]
    return [(r["name"], {tuple(map(int, k.split(","))): v for k, v in r["chi"].items()}, r["n"]) for r in rows]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode")
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("target", type=int)
    ap.add_argument("--add", type=int, default=2)
    ap.add_argument("--cap", type=int, default=200)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--max-bases", type=int, default=10 ** 9)
    a = ap.parse_args()
    bases = load(a.src)
    bases.sort(key=lambda b: -sum(1 for v in b[1].values() if v == 0))  # most triple points first
    bases = bases[:a.max_bases]
    allc, fout = set(), open(a.out, "a")
    with Pool(a.workers) as p:
        for name, out, secs in p.imap_unordered(extend, [(nm, chi, n0, a.add, a.target, a.cap, a.out + ".stream") for nm, chi, n0 in bases]):
            fresh = 0
            for r in out:
                chi = {tuple(map(int, k.split(","))): v for k, v in r["chi"].items()}
                c = canon(chi, r["n"])
                if c in allc:
                    continue
                allc.add(c)
                fresh += 1
                fout.write(json.dumps(r) + "\n")
            fout.flush()
            print(f"{name}: {len(out)} extensions with T >= {a.target} ({fresh} new overall) in {secs}s; "
                  f"T values {sorted(set(r['T'] for r in out))}", flush=True)


if __name__ == "__main__":
    main()

"""Seeded large-neighbourhood SAT search for a 94-triangle arrangement of 18 (pseudo)lines.

For each seed (a known 93, as a wiring word) and each set R of r lines, the signs of all triples avoiding R are
fixed and CaDiCaL re-places the lines of R (same slope ranks), asking for >= 94 triangles. Every call runs to
completion (no conflict budget): each (seed, R, orientation) gets a definite SAT or UNSAT. When R meets {0,1,2},
both orientations of the seed are tried (the model breaks the 180-degree symmetry with chi(0,1,2) != -1).
A SAT answer is re-counted exactly with count_general and written with its full sign vector.

    python push94/run_lns.py --seeds push94/seeds.json --select k=6 --r 2 --workers 30 \
        --out push94/results/k6_r2 --deadline-min 170

Output: <out>/part_<w>.jsonl (one line per call), <out>/summary.json, and <out>/remaining.json if the
deadline stopped it early (rerun the same command: finished calls are skipped).
"""
import argparse
import json
import os
import sys
import time
from itertools import combinations
from multiprocessing import Process
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
n = 18


def chi_from_word(gens, n):
    """Wire labels = initial slots (slope order); g = adjacent swap, g* = 3-wire reversal."""
    wires = list(range(n))
    slot_of = list(range(n))
    chi = {}
    for tok in gens.split():
        g = int(tok.rstrip("*"))
        w = 3 if tok.endswith("*") else 2
        block = wires[g:g + w]
        for i, k in combinations(sorted(block), 2):
            for j in range(i + 1, k):
                chi[i, j, k] = 0 if j in block else (1 if g > slot_of[j] else -1)
        block.reverse()
        wires[g:g + w] = block
        for s in range(g, g + w):
            slot_of[wires[s]] = s
    return chi


def jobs_for(seeds, r):
    out = []
    for si, s in enumerate(seeds):
        for R in combinations(range(n), r):
            signs = (1, -1) if set(R) & {0, 1, 2} else (None,)
            for sg in signs:
                out.append((si, R, sg))
    return out


def worker(w, nw, seeds, jobs, outdir, deadline, kmax, blanc=True):
    from kobon_sat import build_defect, count_general
    from pysat.solvers import Solver
    cnf, z, pz, ng, tri, _ = build_defect(n, 94, kmax, alternate=True, card="cardnetwrk", blanc=blanc)
    trip = list(combinations(range(n), 3))
    chis = {}
    done = set()
    done_all = set()
    part = Path(outdir) / f"part_{w}.jsonl"
    for other in Path(outdir).glob("part_*.jsonl"):  # resume across any worker count
        for l in open(other):
            d0 = json.loads(l)
            done_all.add((d0["seed"], tuple(d0["R"]), d0["sign"]))
    if part.exists():
        for l in open(part):
            d = json.loads(l)
            done.add((d["seed"], tuple(d["R"]), d["sign"]))
    with Solver(name="cadical153", bootstrap_with=cnf.clauses) as sv, open(part, "a") as log:
        for ji, (si, R, sg) in enumerate(jobs):
            if ji % nw != w or (si, R, sg) in done or (si, R, sg) in done_all:
                continue
            if time.time() > deadline:
                break
            if si not in chis:
                chis[si] = chi_from_word(seeds[si]["gens"], n)
            chi = chis[si]
            f = sg if sg is not None else (-1 if chi[0, 1, 2] == -1 else 1)
            Rs = set(R)
            assum = []
            for t in trip:
                if Rs & set(t):
                    continue
                v = f * chi[t]
                assum.append(z[t] if v == 0 else pz[t] if v == 1 else ng[t])
            t0 = time.time()
            res = sv.solve(assumptions=assum)
            rec = {"seed": si, "name": seeds[si]["name"], "R": list(R), "sign": sg, "res": "SAT" if res else "UNSAT",
                   "secs": round(time.time() - t0, 2)}
            if res:
                m = set(v for v in sv.get_model() if v > 0)
                c2 = {t: (0 if z[t] in m else 1 if pz[t] in m else -1) for t in trip}
                rec["T"] = len(count_general(n, c2))
                rec["chi"] = {",".join(map(str, t)): v for t, v in c2.items()}
            log.write(json.dumps(rec) + "\n")
            log.flush()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", required=True)
    ap.add_argument("--select", default="all", help="all | k=6 | k=7 | k=8 | beta>0 | names:a,b")
    ap.add_argument("--r", type=int, default=2)
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--out", required=True)
    ap.add_argument("--deadline-min", type=float, default=170)
    ap.add_argument("--kmax", type=int, default=16)
    ap.add_argument("--no-blanc", action="store_true", help="drop the Blanc clean-line clauses (1.8x slower)")
    a = ap.parse_args()
    seeds = json.load(open(a.seeds))
    if a.select.startswith("k="):
        seeds = [s for s in seeds if s["k"] == int(a.select[2:])]
    elif a.select == "beta>0":
        seeds = [s for s in seeds if s["beta"] > 0]
    elif a.select.startswith("names:"):
        want = set(a.select[6:].split(","))
        seeds = [s for s in seeds if s["name"] in want]
    Path(a.out).mkdir(parents=True, exist_ok=True)
    jobs = jobs_for(seeds, a.r)
    deadline = time.time() + 60 * a.deadline_min
    print(f"{len(seeds)} seeds, r={a.r}: {len(jobs)} calls on {a.workers} workers", flush=True)
    ps = [Process(target=worker, args=(w, a.workers, seeds, jobs, a.out, deadline, a.kmax, not a.no_blanc)) for w in range(a.workers)]
    for p in ps:
        p.start()
    for p in ps:
        p.join()
    recs = [json.loads(l) for w in range(a.workers) if (Path(a.out) / f"part_{w}.jsonl").exists()
            for l in open(Path(a.out) / f"part_{w}.jsonl")]
    got = {(d["seed"], tuple(d["R"]), d["sign"]) for d in recs}
    remaining = [j for j in jobs if (j[0], j[1], j[2]) not in got]
    sats = [{k: d[k] for k in ("name", "R", "sign", "T")} for d in recs if d["res"] == "SAT"]
    summary = {"select": a.select, "r": a.r, "seeds": len(seeds), "calls": len(jobs), "done": len(recs),
               "UNSAT": sum(d["res"] == "UNSAT" for d in recs), "SAT": len(sats), "sat": sats,
               "remaining": len(remaining), "max_secs": max((d["secs"] for d in recs), default=0),
               "mean_secs": round(sum(d["secs"] for d in recs) / max(len(recs), 1), 2)}
    json.dump(summary, open(Path(a.out) / "summary.json", "w"), indent=1)
    if remaining:
        json.dump(remaining, open(Path(a.out) / "remaining.json", "w"))
    print(json.dumps(summary, indent=1), flush=True)


if __name__ == "__main__":
    main()

"""Seeded extension SAT search for a 94-triangle arrangement of 18 (pseudo)lines.

For each seed (a record arrangement on n0 < 18 lines, as a wiring word) and each choice of slope ranks R for the
18 - n0 new lines, the signs of all old triples are fixed and CaDiCaL places the new lines, asking for >= 94
triangles. Every call runs to completion (no conflict budget). When R meets {0,1,2}, both orientations of the
seed are tried (the model breaks the 180-degree symmetry with chi(0,1,2) != -1).

    python push94/run_ext.py --seeds push94/seeds16.json --select bridges --workers 30 \
        --out push94/results/ext16 --deadline-min 150

Output as run_lns.py: <out>/part_<w>.jsonl, <out>/summary.json, <out>/remaining.json (rerun to finish).
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
from run_lns import chi_from_word  # noqa: E402

n = 18


def jobs_for(seeds):
    out = []
    for si, s in enumerate(seeds):
        for R in combinations(range(n), n - s["n0"]):
            for sg in ((1, -1) if set(R) & {0, 1, 2} else (None,)):
                out.append((si, R, sg))
    return out


def worker(w, nw, seeds, jobs, outdir, deadline, kmax, blanc=True):
    from kobon_sat import build_defect, count_general
    from pysat.solvers import Solver
    cnf, z, pz, ng, tri, _ = build_defect(n, 94, kmax, alternate=True, card="cardnetwrk", blanc=blanc)
    trip = list(combinations(range(n), 3))
    done_all = set()
    part = Path(outdir) / f"part_{w}.jsonl"
    for other in Path(outdir).glob("part_*.jsonl"):  # resume across any worker count
        for l in open(other):
            d0 = json.loads(l)
            done_all.add((d0["seed"], tuple(d0["R"]), d0["sign"]))
    done = set()
    if part.exists():
        done = {(d["seed"], tuple(d["R"]), d["sign"]) for d in map(json.loads, open(part))}
    chis = {}
    with Solver(name="cadical153", bootstrap_with=cnf.clauses) as sv, open(part, "a") as log:
        for ji, (si, R, sg) in enumerate(jobs):
            if ji % nw != w or (si, R, sg) in done or (si, R, sg) in done_all:
                continue
            if time.time() > deadline:
                break
            n0 = seeds[si]["n0"]
            if si not in chis:
                chis[si] = chi_from_word(seeds[si]["gens"], n0)
            chi0 = chis[si]
            old = [x for x in range(n) if x not in R]
            if sg is None:  # (0,1,2) are old lines 0,1,2: pick the orientation the model allows
                f = -1 if chi0[0, 1, 2] == -1 else 1
            else:
                f = sg
            assum = []
            for t in combinations(range(n0), 3):
                v = f * chi0[t]
                u = tuple(old[i] for i in t)
                assum.append(z[u] if v == 0 else pz[u] if v == 1 else ng[u])
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
    ap.add_argument("--select", default="all", help="all | bridges | nobridges")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--out", required=True)
    ap.add_argument("--deadline-min", type=float, default=150)
    ap.add_argument("--kmax", type=int, default=16)
    ap.add_argument("--no-blanc", action="store_true", help="drop the Blanc clean-line clauses (1.8x slower)")
    a = ap.parse_args()
    seeds = json.load(open(a.seeds))
    if a.select == "bridges":
        seeds = [s for s in seeds if s["beta"] > 0]
    elif a.select == "nobridges":
        seeds = [s for s in seeds if s["beta"] == 0]
    seeds.sort(key=lambda s: (-s["beta"], -s["k"]))
    Path(a.out).mkdir(parents=True, exist_ok=True)
    jobs = jobs_for(seeds)
    deadline = time.time() + 60 * a.deadline_min
    print(f"{len(seeds)} seeds: {len(jobs)} calls on {a.workers} workers", flush=True)
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
    summary = {"select": a.select, "seeds": len(seeds), "calls": len(jobs), "done": len(recs),
               "UNSAT": sum(d["res"] == "UNSAT" for d in recs), "SAT": len(sats), "sat": sats,
               "remaining": len(remaining), "max_secs": max((d["secs"] for d in recs), default=0),
               "mean_secs": round(sum(d["secs"] for d in recs) / max(len(recs), 1), 2)}
    json.dump(summary, open(Path(a.out) / "summary.json", "w"), indent=1)
    if remaining:
        json.dump(remaining, open(Path(a.out) / "remaining.json", "w"))
    print(json.dumps(summary, indent=1), flush=True)


if __name__ == "__main__":
    main()

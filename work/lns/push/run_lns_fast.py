"""run_lns.py with the reduced extension model (search/fastext.py): re-placing the lines R of a seed at the same
slope ranks = extending the seed's sub-arrangement on the other lines by lines at ranks R. Same jobs, orientation
handling (symmetry break kept), resume keys and output format as run_lns.py.
Control: at --target 93 every call on a 93 seed is SAT (the seed itself is a solution).

    python work/lns/push/run_lns_fast.py --seeds <seeds.json> --select k=8 --r 2 --workers 8 --out <dir>
"""
import argparse
import json
import os
import sys
import time
from itertools import combinations
from multiprocessing import Process, Queue
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent.parent / "search"))
from run_lns import chi_from_word  # noqa: E402

n = 18


def worker(w, q, seeds, outdir, deadline, target):
    from fastext import Ext
    from kobon_sat import count_general
    part = Path(outdir) / f"part_{w}.jsonl"
    chis = {}
    with open(part, "a") as log:
        while time.time() < deadline:
            job = q.get()
            if job is None:
                break
            si, R, sg = job
            if si not in chis:
                chis[si] = chi_from_word(seeds[si]["gens"], n)
            chi = chis[si]
            f = sg if sg is not None else (-1 if chi[0, 1, 2] == -1 else 1)
            keep = [x for x in range(n) if x not in R]
            idx = {x: i for i, x in enumerate(keep)}
            sub = {tuple(idx[x] for x in t): v for t, v in chi.items() if not set(t) & set(R)}
            t0 = time.time()
            sol = Ext(sub, n - len(R), R, f, target).solve()
            rec = {"seed": si, "name": seeds[si]["name"], "R": list(R), "sign": sg, "res": "SAT" if sol else "UNSAT",
                   "secs": round(time.time() - t0, 2)}
            if sol:
                rec["T"] = len(count_general(n, sol))
                rec["chi"] = {",".join(map(str, t)): v for t, v in sol.items()}
            log.write(json.dumps(rec) + "\n")
            log.flush()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", required=True)
    ap.add_argument("--select", default="all", help="all | k=6 | k=7 | k=8 | beta>0")
    ap.add_argument("--r", type=int, default=2)
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--out", required=True)
    ap.add_argument("--deadline-min", type=float, default=900)
    ap.add_argument("--target", type=int, default=94)
    ap.add_argument("--max-seeds", type=int, default=10 ** 9)
    a = ap.parse_args()
    seeds = json.load(open(a.seeds))
    if a.select.startswith("k="):
        seeds = [s for s in seeds if s["k"] == int(a.select[2:])]
    elif a.select == "beta>0":
        seeds = [s for s in seeds if s["beta"] > 0]
    seeds = seeds[:a.max_seeds]
    jobs = [(si, R, sg) for si in range(len(seeds)) for R in combinations(range(n), a.r)
            for sg in ((1, -1) if set(R) & {0, 1, 2} else (None,))]
    Path(a.out).mkdir(parents=True, exist_ok=True)
    prev = set()
    for f_ in Path(a.out).glob("part_*.jsonl"):
        for l in open(f_):
            d0 = json.loads(l)
            prev.add((d0["seed"], tuple(d0["R"]), d0["sign"]))
    pending = [j for j in jobs if j not in prev]
    print(f"{len(seeds)} seeds, r={a.r}: {len(jobs)} calls, {len(pending)} pending, {a.workers} workers", flush=True)
    q = Queue()
    for j in pending:
        q.put(j)
    for _ in range(a.workers):
        q.put(None)
    deadline = time.time() + 60 * a.deadline_min
    ps = [Process(target=worker, args=(w, q, seeds, a.out, deadline, a.target)) for w in range(a.workers)]
    for p in ps:
        p.start()
    for p in ps:
        p.join()
    recs = [json.loads(l) for f_ in Path(a.out).glob("part_*.jsonl") for l in open(f_)]
    got = {(d["seed"], tuple(d["R"]), d["sign"]) for d in recs}
    sats = [{k: d[k] for k in ("name", "R", "sign", "T")} for d in recs if d["res"] == "SAT"]
    summary = {"select": a.select, "r": a.r, "target": a.target, "seeds": len(seeds), "calls": len(jobs), "done": len(recs),
               "UNSAT": sum(d["res"] == "UNSAT" for d in recs), "SAT": len(sats), "sat": sats[:50],
               "remaining": len([j for j in jobs if j not in got]), "max_secs": max((d["secs"] for d in recs), default=0),
               "mean_secs": round(sum(d["secs"] for d in recs) / max(len(recs), 1), 2)}
    json.dump(summary, open(Path(a.out) / "summary.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k != "sat"}, indent=1), flush=True)


if __name__ == "__main__":
    main()

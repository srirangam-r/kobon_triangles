"""run_ext.py with the reduced extension model (search/fastext.py, validated 720/720 against the full model).
Same jobs, orientation handling (symmetry break kept), resume format and output as run_ext.py.

    python work/lns/push/run_ext_fast.py --seeds <seeds.json> --workers 8 --out <dir> [--deadline-min 900]
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


def jobs_for(seeds):
    out = []
    for si, s in enumerate(seeds):
        for R in combinations(range(n), n - s["n0"]):
            for sg in ((1, -1) if set(R) & {0, 1, 2} else (None,)):
                out.append((si, R, sg))
    return out


def worker(w, q, seeds, outdir, deadline, target):
    from fastext import Ext
    from kobon_sat import count_general
    part = Path(outdir) / f"part_{w}.jsonl"
    chis, tris = {}, {}
    with open(part, "a") as log:
        while time.time() < deadline:
            job = q.get()
            if job is None:
                break
            si, R, sg = job
            n0 = seeds[si]["n0"]
            if si not in chis:
                chis[si] = ({tuple(map(int, k.split(","))): v for k, v in seeds[si]["chi"].items()} if "chi" in seeds[si]
                            else chi_from_word(seeds[si]["gens"], n0))
                tris[si] = [tuple(sorted(t)) for t in count_general(n0, chis[si])]
            chi0 = chis[si]
            f = sg if sg is not None else (-1 if chi0[0, 1, 2] == -1 else 1)
            t0 = time.time()
            chi = Ext(chi0, n0, R, f, target, base_tris=tris[si]).solve()
            rec = {"seed": si, "name": seeds[si]["name"], "R": list(R), "sign": sg, "res": "SAT" if chi else "UNSAT",
                   "secs": round(time.time() - t0, 2)}
            if chi:
                rec["T"] = len(count_general(n, chi))
                rec["chi"] = {",".join(map(str, t)): v for t, v in chi.items()}
            log.write(json.dumps(rec) + "\n")
            log.flush()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", required=True)
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--out", required=True)
    ap.add_argument("--deadline-min", type=float, default=900)
    ap.add_argument("--target", type=int, default=int(os.environ.get("EXT_TARGET", "94")))
    a = ap.parse_args()
    seeds = json.load(open(a.seeds))
    Path(a.out).mkdir(parents=True, exist_ok=True)
    jobs = jobs_for(seeds)
    prev = set()
    for f_ in Path(a.out).glob("part_*.jsonl"):
        for l in open(f_):
            d0 = json.loads(l)
            prev.add((d0["seed"], tuple(d0["R"]), d0["sign"]))
    pending = [j for j in jobs if j not in prev]
    print(f"{len(seeds)} seeds: {len(jobs)} calls, {len(pending)} pending, {a.workers} workers", flush=True)
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
    summary = {"seeds": len(seeds), "calls": len(jobs), "done": len(recs), "UNSAT": sum(d["res"] == "UNSAT" for d in recs),
               "SAT": len(sats), "sat": sats, "remaining": len([j for j in jobs if j not in got]),
               "max_secs": max((d["secs"] for d in recs), default=0),
               "mean_secs": round(sum(d["secs"] for d in recs) / max(len(recs), 1), 2)}
    json.dump(summary, open(Path(a.out) / "summary.json", "w"), indent=1)
    print(json.dumps(summary, indent=1), flush=True)


if __name__ == "__main__":
    main()

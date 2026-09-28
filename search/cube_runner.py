"""Incremental cube-and-conquer: each worker loads the formula once into CaDiCaL (pysat) and solves cubes
under assumptions, so easy cubes cost milliseconds instead of a 200 MB write and parse each.

A task is (cube id, line-0 prefix). Assumptions = the cube's units + "prefix[i] precedes every later line on
line 0". A task that exceeds the time limit is split one crossing deeper on line 0 (all children, so
coverage is kept); results append to <workdir>/results.jsonl and a restart resumes from it. SAT stops the run.
Solver claims only: no proof logs in this pass.

    uv run --no-project --with python-sat python search/cube_runner.py <cnf> <spec.json> <cubes.jsonl> <workdir>
        [--workers 12] [--timeout 20] [--limit N]
"""
import argparse
import json
import os
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path

_g = {}


def init(cnf_path, spec_path, cubes_path):
    from pysat.solvers import Cadical195
    s = Cadical195()
    with open(cnf_path) as fh:
        for line in fh:
            if line[0] in "cp":
                continue
            lits = [int(x) for x in line.split()]
            if lits and lits[-1] == 0:
                lits.pop()
            s.add_clause(lits)
    spec = json.load(open(spec_path))
    _g.update(s=s, pz=spec["pz"], ng=spec["ng"], cubes=[json.loads(l)["units"] for l in open(cubes_path)])


def before0(x, y):
    return _g["ng"][f"0,{x},{y}"] if x < y else _g["pz"][f"0,{y},{x}"]


def solve(task):
    cid, prefix, timeout = task
    assum = list(_g["cubes"][cid])
    for pos, a in enumerate(prefix):
        assum += [before0(a, y) for y in range(1, 18) if y not in prefix[:pos + 1]]
    s = _g["s"]
    timer = threading.Timer(timeout, s.interrupt)
    t = time.time()
    timer.start()
    r = s.solve_limited(assumptions=assum, expect_interrupt=True)
    timer.cancel()
    s.clear_interrupt()
    verdict = {True: "SAT", False: "UNSAT", None: "timeout"}[r]
    model = s.get_model() if r else None
    return cid, list(prefix), verdict, round(time.time() - t, 2), model


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cnf"); ap.add_argument("spec"); ap.add_argument("cubes"); ap.add_argument("workdir")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--timeout", type=float, default=20)
    ap.add_argument("--limit", type=int, default=0, help="only the first N cubes (pilot)")
    a = ap.parse_args()
    work = Path(a.workdir); work.mkdir(parents=True, exist_ok=True)
    log = work / "results.jsonl"
    cubes = [json.loads(l) for l in open(a.cubes)]
    n = a.limit or len(cubes)
    done, split = set(), set()
    if log.exists():
        for line in log.read_text().splitlines():
            r = json.loads(line)
            (split if r["verdict"] == "timeout" else done).add((r["cube"], tuple(r["prefix"])))
    # frontier: each cube starts at the empty prefix; split tasks are replaced by their children
    frontier, stack = [], [(c, ()) for c in range(n)]
    while stack:
        c, p = stack.pop()
        if (c, p) in done:
            continue
        if (c, p) in split:
            stack += [(c, p + (x,)) for x in range(1, 18) if x not in p]
        else:
            frontier.append((c, p))
    frontier.sort(key=lambda t: (len(t[1]), t[0]))
    print(f"resume: {len(done)} done, {len(split)} split, {len(frontier)} to do", flush=True)
    t0 = time.time()
    counts = {"UNSAT": 0, "timeout": 0, "SAT": 0}
    with ProcessPoolExecutor(a.workers, initializer=init, initargs=(a.cnf, a.spec, a.cubes)) as ex, log.open("a") as fh:
        queue = list(frontier)
        pending = {}
        while queue and len(pending) < a.workers * 2:
            c, p = queue.pop(0)
            pending[ex.submit(solve, (c, p, a.timeout))] = (c, p)
        while pending:
            fin, _ = wait(pending, return_when=FIRST_COMPLETED)
            for f in fin:
                pending.pop(f)
                cid, prefix, verdict, secs, model = f.result()
                fh.write(json.dumps({"cube": cid, "prefix": prefix, "verdict": verdict, "secs": secs, "t": round(time.time() - t0)}) + "\n")
                fh.flush()
                counts[verdict] += 1
                if verdict == "SAT":
                    (work / f"SAT_cube{cid}_{'_'.join(map(str, prefix))}.model").write_text(" ".join(map(str, model)))
                    print(f"SAT at cube {cid} prefix {prefix} -- candidate, stopping", flush=True)
                    os._exit(0)
                if verdict == "timeout":
                    queue += [(cid, tuple(prefix) + (x,)) for x in range(1, 18) if x not in prefix]
                while queue and len(pending) < a.workers * 2:
                    c, p = queue.pop(0)
                    pending[ex.submit(solve, (c, p, a.timeout))] = (c, p)
            tot = sum(counts.values())
            if tot % 100 == 0:
                print(f"{time.time() - t0:.0f}s: {counts}, queued {len(queue)}", flush=True)
    print(f"ALL DONE in {time.time() - t0:.0f}s: {counts}", flush=True)


if __name__ == "__main__":
    main()

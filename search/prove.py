"""Adaptive cube-and-conquer for the 18/94 question, split along line 0's crossing order.

Cubes are prefixes (a, b, c, ...) of the order in which line 0 meets the other lines
(line 0 is defect-free and avoids the triple point, by the model's symmetry breaking).
Every order has exactly one prefix of each length, so the cubes at any mix of depths
cover everything as long as each timed-out cube is replaced by all its children.
Each cube runs Kissat on formula + unit clauses with a time limit; a timeout splits
it one crossing deeper. SAT stops the run (candidate). Results append to a JSONL
log, and a restart resumes from it.

This pass writes no proof logs: an all-UNSAT outcome is a solver claim until the
verification pass (re-solve with proofs, check with drat-trim or an LRAT checker).

    python3 search/prove.py <formula.cnf> <prefix_spec.json> <workdir> [--workers 22] [--timeout 240] [--depth 3]
"""
import argparse
import json
import os
import subprocess
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from itertools import permutations
from pathlib import Path

KISSAT = Path(__file__).resolve().parent.parent / "tools" / "kissat" / "build" / "kissat"
_g = {}


def init(cnf_path, spec_path, workdir):
    text = Path(cnf_path).read_text()
    head, body = text.split("\n", 1)
    spec = json.loads(Path(spec_path).read_text())
    _g.update(nv=int(head.split()[2]), nc=int(head.split()[3]), body=body, spec=spec, work=Path(workdir))


def lits_for(pre):
    spec = _g["spec"]
    n, pzv, ngv = spec["n"], spec["pz"], spec["ng"]
    before = lambda x, y: ngv[f"0,{x},{y}"] if x < y else pzv[f"0,{y},{x}"]
    others = list(range(1, n))
    out = []
    for pos, a in enumerate(pre):
        out += [before(a, x) for x in others if x not in pre[:pos + 1]]
    return out


def solve(args):
    pre, timeout = args
    lits = lits_for(pre)
    path = _g["work"] / f"cube_{'_'.join(map(str, pre))}.cnf"
    path.write_text(f"p cnf {_g['nv']} {_g['nc'] + len(lits)}\n" + _g["body"] + "".join(f"{l} 0\n" for l in lits))
    t = time.time()
    r = subprocess.run(["timeout", str(timeout), str(KISSAT), "-q", str(path)], capture_output=True, text=True)
    secs = round(time.time() - t, 1)
    verdict = {10: "SAT", 20: "UNSAT"}.get(r.returncode, "timeout")
    if verdict == "SAT":
        (_g["work"] / f"SAT_{'_'.join(map(str, pre))}.model").write_text(r.stdout)
    path.unlink()
    return list(pre), verdict, secs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cnf")
    ap.add_argument("spec")
    ap.add_argument("workdir")
    ap.add_argument("--workers", type=int, default=22)
    ap.add_argument("--timeout", type=int, default=240)
    ap.add_argument("--depth", type=int, default=3)
    a = ap.parse_args()
    work = Path(a.workdir)
    work.mkdir(parents=True, exist_ok=True)
    log = work / "results.jsonl"
    spec = json.loads(Path(a.spec).read_text())
    others = list(range(1, spec["n"]))
    done, split = set(), set()
    if log.exists():
        for line in log.read_text().splitlines():
            r = json.loads(line)
            key = tuple(r["prefix"])
            (split if r["verdict"] == "timeout" else done).add(key)
    # frontier: all depth-d prefixes, replacing split ones by their children, minus finished ones
    frontier, stack = [], list(permutations(others, a.depth))
    while stack:
        p = stack.pop()
        if any(p[:k] in done for k in range(1, len(p) + 1)):  # this cube or an ancestor is finished
            continue
        if p in split:
            stack += [p + (x,) for x in others if x not in p]
        else:
            frontier.append(p)
    print(f"resume: {len(done)} finished, {len(split)} split, {len(frontier)} to do", flush=True)
    t0 = time.time()
    with ProcessPoolExecutor(a.workers, initializer=init, initargs=(a.cnf, a.spec, str(work))) as ex, log.open("a") as fh:
        pending = {ex.submit(solve, (p, a.timeout)): p for p in frontier[: a.workers * 2]}
        queue = frontier[a.workers * 2:]
        counts = {"UNSAT": 0, "timeout": 0, "SAT": 0}
        while pending:
            fin, _ = wait(pending, return_when=FIRST_COMPLETED)
            for f in fin:
                pending.pop(f)
                pre, verdict, secs = f.result()
                fh.write(json.dumps({"prefix": pre, "verdict": verdict, "secs": secs, "t": round(time.time() - t0)}) + "\n")
                fh.flush()
                counts[verdict] += 1
                if verdict == "SAT":
                    print(f"SAT at prefix {pre} after {secs}s -- candidate found, stopping", flush=True)
                    for g in pending:
                        g.cancel()
                    os.system("pkill -x kissat")
                    return
                if verdict == "timeout":
                    queue = [tuple(pre) + (x,) for x in others if x not in pre] + queue
                while queue and len(pending) < a.workers * 2:
                    p = queue.pop(0)
                    pending[ex.submit(solve, (p, a.timeout))] = p
            done_n = counts["UNSAT"]
            if done_n % 50 == 0:
                print(f"{time.time() - t0:.0f}s: UNSAT {counts['UNSAT']}, split {counts['timeout']}, queued {len(queue)}", flush=True)
    print(f"ALL DONE in {time.time() - t0:.0f}s: {counts}", flush=True)


if __name__ == "__main__":
    main()

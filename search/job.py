"""One search job for an AutoLab node. Settings come from search/job_config.json.

Methods:
  anneal  simulated annealing from random starts on all cores, then an exact
          single-line re-insert pass on the best few results
  walk    exact plateau walk from a committed arrangement: repeatedly replace one
          line by a tied-or-better line through two crossing points

Writes the best arrangement it found to ./solution.json (what the hill scores) and
its own unofficial numbers to ./search_log.json. The committed ./solution.json is
deleted first, so a crashed job fails instead of re-scoring an old arrangement.
The score that counts is the hill's report for the experiment.

    sh search/job.sh ['{"method": "anneal", "minutes": 30, "seed": 1}']
"""
import json
import os
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from anneal import anneal, count, to_integer_lines, worker  # noqa: E402
from reinsert import Fixed, best_reinsert, norm_line, size  # noqa: E402

LIMIT = 10**30


def exact_count(lines):
    return Fixed(lines[1:]).count_with(lines[0])


def polish(lines, pool):
    passes = pool.map(best_reinsert, [(lines, r, True) for r in range(len(lines))])
    r, top, cands = max(passes, key=lambda x: x[1])
    pick = min(cands, key=size)
    return top, lines[:r] + [pick] + lines[r + 1:]


def run_anneal(cfg, workers, log):
    schedule = {"iters": cfg.get("iters", 200_000), "t_hot": cfg.get("t_hot", 1.5), "t_cold": cfg.get("t_cold", 0.05)}
    seconds = cfg["minutes"] * 60 * 0.8
    jobs = [(cfg["n"], seconds, cfg["seed"] * 1000 + w, None, schedule) for w in range(workers)]
    with Pool(workers) as pool:
        results = pool.map(worker, jobs)
    found = sorted(([norm_line(*row) for row in to_integer_lines(t, d)] for _, t, d, _ in results),
                   key=exact_count, reverse=True)
    counts = [exact_count(l) for l in found]
    log["anneal_exact_counts"] = counts
    best_score, best_lines = counts[0], found[0]
    log["polish"] = []
    with Pool(min(workers, cfg["n"])) as pool:
        for lines, c in list(zip(found, counts))[: cfg.get("polish", 6)]:
            top, new = polish(lines, pool)
            log["polish"].append({"start": c, "after": top})
            if top > best_score and max(map(size, new)) <= LIMIT:
                best_score, best_lines = top, new
    return best_score, best_lines


def walk_one(args):
    start, seconds, seed = args
    rng = random.Random(seed)
    deadline = time.time() + seconds
    lines, score = list(start), exact_count(start)
    best, best_lines, steps = score, list(lines), 0
    while time.time() < deadline:
        r = rng.randrange(len(lines))
        _, top, cands = best_reinsert((lines, r, True))
        cands = sorted((c for c in cands if c != lines[r]), key=size)[:3]
        if top >= score and cands:
            lines = lines[:r] + [rng.choice(cands)] + lines[r + 1:]
            score, steps = top, steps + 1
            if score > best and max(map(size, lines)) <= LIMIT:
                best, best_lines = score, list(lines)
        if max(map(size, lines)) > 10**120:
            lines, score = list(start), exact_count(start)
    return best, best_lines, steps


def run_walk(cfg, workers, log):
    start = [norm_line(*row) for row in json.loads((HERE.parent / cfg["seed_file"]).read_text())["lines"]]
    seconds = cfg["minutes"] * 60 * 0.9
    with Pool(workers) as pool:
        results = pool.map(walk_one, [(start, seconds, cfg["seed"] * 1000 + w) for w in range(workers)])
    results.sort(key=lambda x: (-x[0], max(map(size, x[1]))))
    log["walk_best_per_worker"] = [b for b, _, _ in results]
    log["walk_steps"] = sum(s for _, _, s in results)
    return results[0][0], results[0][1]


def main():
    Path("solution.json").unlink(missing_ok=True)
    cfg = {"n": 18, "method": "anneal", "minutes": 20, "seed": 0}
    cfg.update(json.loads((HERE / "job_config.json").read_text()))
    if len(sys.argv) > 1:  # a JSON config on the command line overrides the file
        cfg.update(json.loads(sys.argv[1]))
    workers = cfg.get("workers") or os.cpu_count()
    started = time.time()
    count(np.zeros(3), np.zeros(3))  # compile before forking
    anneal(np.zeros(3), np.zeros(3), 1, 1.0, 0.1, 0)
    log = {"config": cfg, "workers": workers, "host_cpus": os.cpu_count()}
    best_score, best_lines = (run_walk if cfg["method"] == "walk" else run_anneal)(cfg, workers, log)
    log["best_exact_unofficial"] = best_score
    log["seconds"] = round(time.time() - started, 1)
    Path("solution.json").write_text(json.dumps({"lines": [list(l) for l in best_lines]}) + "\n")
    Path("search_log.json").write_text(json.dumps(log, indent=1) + "\n")
    print("DEV (unofficial):", json.dumps(log))


if __name__ == "__main__":
    main()

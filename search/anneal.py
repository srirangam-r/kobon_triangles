"""Simulated annealing over line angles/offsets, with a fast float triangle counter.

Everything this prints is a DEV number: the float counter assumes general
position and is only a search heuristic. Official scores come from `hills eval`.

    python3 search/anneal.py <n> <seconds> <submission_dir> [--workers W] [--seed-from solution.json]
"""
import argparse
import json
import math
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from numba import njit

SCALE = 10**17  # float -> integer coefficients; far inside the 10^30 limit


@njit(cache=True)
def count(theta, d):
    n = theta.shape[0]
    c, s = np.cos(theta), np.sin(theta)
    t = np.full((n, n), np.inf)
    for i in range(n):
        for j in range(i + 1, n):
            det = c[i] * s[j] - s[i] * c[j]
            if abs(det) < 1e-13:
                continue
            x = (d[i] * s[j] - s[i] * d[j]) / det
            y = (c[i] * d[j] - d[i] * c[j]) / det
            t[i, j] = -s[i] * x + c[i] * y
            t[j, i] = -s[j] * x + c[j] * y
    rank = np.zeros((n, n), dtype=np.int64)
    for i in range(n):
        order = np.argsort(t[i])
        for r in range(n):
            rank[i, order[r]] = r
    total = 0
    for i in range(n):
        for j in range(i + 1, n):
            if t[i, j] == np.inf:
                continue
            for k in range(j + 1, n):
                if t[i, k] == np.inf or t[j, k] == np.inf:
                    continue
                if (abs(rank[i, j] - rank[i, k]) == 1 and abs(rank[j, i] - rank[j, k]) == 1
                        and abs(rank[k, i] - rank[k, j]) == 1):
                    total += 1
    return total


@njit(cache=True)
def anneal(theta, d, iters, t_hot, t_cold, seed):
    np.random.seed(seed)
    n = theta.shape[0]
    cur = count(theta, d)
    best, best_theta, best_d = cur, theta.copy(), d.copy()
    for it in range(iters):
        temp = t_hot * (t_cold / t_hot) ** (it / iters)
        i = np.random.randint(n)
        sigma = 10.0 ** np.random.uniform(-5.0, -0.5)
        old_t, old_d = theta[i], d[i]
        theta[i] += np.random.normal() * sigma
        d[i] += np.random.normal() * sigma
        new = count(theta, d)
        if new >= cur or np.random.random() < math.exp((new - cur) / temp):
            cur = new
            if cur > best:
                best, best_theta, best_d = cur, theta.copy(), d.copy()
        else:
            theta[i], d[i] = old_t, old_d
    return best, best_theta, best_d


def worker(args):
    n, seconds, seed, start = args[:4]
    schedule = args[4] if len(args) > 4 else {"iters": 200_000, "t_hot": 1.5, "t_cold": 0.05}
    rng = np.random.default_rng(seed)
    deadline = time.time() + seconds
    best = (-1, None, None)
    restart = 0
    while time.time() < deadline:
        if start is not None and restart % 2 == 0:
            theta, d = start[0].copy(), start[1].copy()
        else:
            theta, d = rng.uniform(0, math.pi, n), rng.normal(0, 1, n)
        result = anneal(theta, d, schedule["iters"], schedule["t_hot"], schedule["t_cold"], int(rng.integers(2**31)))
        if result[0] > best[0]:
            best = result
        restart += 1
    return best[0], best[1].tolist(), best[2].tolist(), restart


def to_integer_lines(theta, d):
    # cos(t) x + sin(t) y - d = 0, scaled and rounded; this integer line is what gets scored.
    return [[round(math.cos(a) * SCALE), round(math.sin(a) * SCALE), -round(b * SCALE)] for a, b in zip(theta, d)]


def from_solution(path):
    lines = json.loads(Path(path).read_text())["lines"]
    theta, d = [], []
    for a, b, c in lines:
        norm = math.hypot(a, b)
        theta.append(math.atan2(b, a))
        d.append(-c / norm)
    return np.array(theta), np.array(d)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("n", type=int)
    parser.add_argument("seconds", type=float)
    parser.add_argument("out")
    parser.add_argument("--workers", type=int, default=22)
    parser.add_argument("--seed-from")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    start = from_solution(args.seed_from) if args.seed_from else None
    count(np.zeros(3), np.zeros(3))  # compile once before forking
    anneal(np.zeros(3), np.zeros(3), 1, 1.0, 0.1, 0)
    jobs = [(args.n, args.seconds, args.seed * 1000 + w, start) for w in range(args.workers)]
    with Pool(args.workers) as pool:
        results = pool.map(worker, jobs)
    results.sort(key=lambda r: -r[0])
    counts = [r[0] for r in results]
    print(f"DEV (float, unofficial): best {counts[0]}, per-worker {counts}, restarts {sum(r[3] for r in results)}")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "solution.json").write_text(json.dumps({"lines": to_integer_lines(results[0][1], results[0][2])}) + "\n")
    (out / "search.json").write_text(json.dumps({"dev_float_count": counts[0], "theta": results[0][1], "d": results[0][2],
                                                 "args": vars(args)}) + "\n")
    for w, (c, theta, d, _) in enumerate(results):  # every worker's best, as seeds for other searches
        (out / f"worker{w:02d}-{c}.json").write_text(json.dumps({"lines": to_integer_lines(theta, d)}) + "\n")


if __name__ == "__main__":
    main()

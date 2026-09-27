"""Exact annealing over line-replacement moves, guided by the Kobon counting identity.

Move: pick a line, remove it, evaluate (exactly) every line through two crossing
points of the remaining lines, and pick a replacement with Metropolis weights on
the triangle count. Lines through two crossing points make triple points (4-fold
points if one of them already is one), which the float annealer cannot produce.
Among near-equal candidates it prefers more multiple points (the literature's
hint: records cluster triple points on a line) and smaller coefficients. It
accepts drops to 92/91 now and then to leave the 93 plateau, and keeps a tabu set
of visited arrangements. Counts are DEV numbers; only the hill scores officially.

    python3 search/exact_anneal.py <seed solution.json> <out_dir> <seconds> [--workers W]
"""
import argparse
import json
import math
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reinsert import Fixed, load, norm_line, size  # noqa: E402

LIMIT = 10**30


def through_count(fixed, cand):
    a, b, c = cand
    return sum(1 for (x, y, w) in fixed.vertices if a * x + b * y + c * w == 0)


def run(args):
    start, seconds, seed, t_hot, t_cold = args
    rng = random.Random(seed)
    deadline = time.time() + seconds
    lines = list(start)
    cur = Fixed(lines[1:]).count_with(lines[0])
    best, best_lines = cur, list(lines)
    seen, found94, max_mult, steps, t0 = set(), [], 0, 0, time.time()
    history = {}
    while time.time() < deadline:
        frac = (time.time() - t0) / seconds
        temp = t_hot * (t_cold / t_hot) ** frac
        r = rng.randrange(len(lines))
        fixed = Fixed(lines[:r] + lines[r + 1:])
        scored = []
        for cand in fixed.candidates():
            if cand == lines[r]:
                continue
            s = fixed.count_with(cand)
            if s >= cur - 1:
                scored.append((s, cand))
        # choose the score level by Metropolis (one weight per level, not per candidate,
        # or the many worse candidates swamp the ties), then a candidate within it
        levels = {}
        for sc, cand in scored:
            levels.setdefault(sc, []).append(cand)
        levels.setdefault(cur, []).append(lines[r])  # staying put is always an option
        lv = sorted(levels)
        s = rng.choices(lv, weights=[math.exp((x - cur) / temp) for x in lv])[0]
        pool_ = levels[s]
        weights = [math.exp(0.5 * through_count(fixed, c) - 0.05 * math.log10(max(2, size(c)))) for c in pool_]
        cand = rng.choices(pool_, weights=weights)[0]
        if cand == lines[r]:
            continue
        new_lines = lines[:r] + [cand] + lines[r + 1:]
        key = frozenset(new_lines)
        if key in seen and s <= cur:
            continue
        seen.add(key)
        lines, cur, steps = new_lines, s, steps + 1
        history[cur] = history.get(cur, 0) + 1
        mult = through_count(fixed, cand)
        max_mult = max(max_mult, mult)
        if cur > best or (cur == best and max(map(size, lines)) < max(map(size, best_lines))):
            best, best_lines = cur, list(lines)
        if cur >= 94:
            found94.append([list(l) for l in lines])
        if max(map(size, lines)) > 10**150:  # coefficients explode through repeated joins: restart
            lines = list(start)
            cur = Fixed(lines[1:]).count_with(lines[0])
    return {"best": best, "best_lines": [list(l) for l in best_lines], "steps": steps, "distinct": len(seen),
            "visits_by_score": history, "found94": found94, "max_new_line_through_vertices": max_mult}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("seed")
    parser.add_argument("out")
    parser.add_argument("seconds", type=float)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--t-hot", type=float, default=0.6)
    parser.add_argument("--t-cold", type=float, default=0.15)
    args = parser.parse_args()
    start = load(args.seed)
    jobs = [(start, args.seconds, 1000 + w, args.t_hot, args.t_cold) for w in range(args.workers)]
    with Pool(args.workers) as pool:
        results = pool.map(run, jobs)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    summary = [{k: v for k, v in r.items() if k not in ("best_lines", "found94")} for r in results]
    hits = [l for r in results for l in r["found94"]]
    best = max(results, key=lambda r: r["best"])
    (out / "summary.json").write_text(json.dumps({"seed": args.seed, "workers": summary, "any94": len(hits)}, indent=1) + "\n")
    (out / "best.json").write_text(json.dumps({"lines": best["best_lines"]}) + "\n")
    if hits:
        for i, l in enumerate(hits[:20]):
            (out / f"hit94_{i}.json").write_text(json.dumps({"lines": l}) + "\n")
    print("DEV (unofficial):", json.dumps({"best": best["best"], "any94": len(hits),
                                          "distinct_per_worker": [r["distinct"] for r in results],
                                          "visits": [r["visits_by_score"] for r in results]}))


if __name__ == "__main__":
    main()

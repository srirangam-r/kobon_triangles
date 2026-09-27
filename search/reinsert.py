"""Exact drop-one-line / re-insert search.

Remove line r from an arrangement, then try every line through two crossing
points of the remaining n-1 lines (these create exact triple points, which the
float annealer cannot see), plus small perturbations of the best ones. The
count for "fixed lines + one candidate" is computed incrementally and exactly
from which side of the candidate each crossing point lies on. Counts printed
here are DEV numbers; only `hills eval` scores are official.

    python3 search/reinsert.py check <solution.json>          # validate against the hill's counter
    python3 search/reinsert.py pass <solution.json> <out_dir> [--workers W]
    python3 search/reinsert.py walk <solution.json> <out_dir> <seconds> [--workers W]
"""
import argparse
import json
import random
import sys
import time
from fractions import Fraction
from itertools import combinations
from math import gcd
from multiprocessing import Pool
from pathlib import Path

HILL = Path(__file__).resolve().parent.parent / ".autolab" / "hills" / "kobon-triangles"
LIMIT = 10**30


def norm_line(a, b, c):
    g = gcd(gcd(abs(a), abs(b)), abs(c)) or 1
    a, b, c = a // g, b // g, c // g
    first = next(v for v in (a, b, c) if v)
    return (-a, -b, -c) if first < 0 else (a, b, c)


def meet(l1, l2):
    """Homogeneous intersection (x, y, w) with w > 0 and gcd 1, or None if parallel."""
    a, b, c = l1
    d, e, f = l2
    w = a * e - b * d
    if w == 0:
        return None
    x, y = b * f - c * e, c * d - a * f
    g = gcd(gcd(abs(x), abs(y)), abs(w))
    if w < 0:
        g = -g
    return x // g, y // g, w // g


def join(p, q):
    """Line through homogeneous points p, q."""
    x1, y1, w1 = p
    x2, y2, w2 = q
    return norm_line(y1 * w2 - w1 * y2, w1 * x2 - x1 * w2, x1 * y2 - y1 * x2)


def key_on(line, p):
    return Fraction(p[0], p[2]) if line[1] else Fraction(p[1], p[2])


class Fixed:
    """The n-1 fixed lines, with everything the incremental count needs."""

    def __init__(self, lines):
        self.lines = lines
        m = len(lines)
        self.pt = {}
        on = [set() for _ in lines]
        for i, j in combinations(range(m), 2):
            p = meet(lines[i], lines[j])
            self.pt[i, j] = self.pt[j, i] = p
            if p is not None:
                on[i].add(p)
                on[j].add(p)
        self.order = [sorted(s, key=lambda p, l=lines[i]: key_on(l, p)) for i, s in enumerate(on)]
        self.vertices = sorted(set().union(*on))
        # triangles among the fixed lines (same rule as the hill: consecutive vertices on all three sides)
        rank = [{p: r for r, p in enumerate(o)} for o in self.order]
        self.tris = []
        for i, j, k in combinations(range(m), 3):
            a, b, c = self.pt[i, j], self.pt[i, k], self.pt[j, k]
            if a is None or b is None or c is None or a == b:
                continue
            if abs(rank[i][a] - rank[i][b]) == 1 and abs(rank[j][a] - rank[j][c]) == 1 and abs(rank[k][b] - rank[k][c]) == 1:
                self.tris.append((a, b, c))
        self.line_set = set(lines)

    def count_with(self, cand):
        if cand in self.line_set or (cand[0] == 0 and cand[1] == 0):
            return -1
        a, b, c = cand
        sign = {}
        for (x, y, w) in self.vertices:
            v = a * x + b * y + c * w
            sign[(x, y, w)] = (v > 0) - (v < 0)
        total = 0
        for p, q, r in self.tris:
            s = (sign[p], sign[q], sign[r])
            if not (1 in s and -1 in s):
                total += 1
        m = len(self.lines)
        hit, nbrs = [None] * m, [()] * m
        for i in range(m):
            p = meet(cand, self.lines[i])
            if p is None:
                continue
            hit[i] = p
            o = self.order[i]
            zero = [t for t, v in enumerate(o) if sign[v] == 0]
            if zero:
                t = zero[0]
                nbrs[i] = tuple(o[u] for u in (t - 1, t + 1) if 0 <= u < len(o))
            else:
                t = 0
                while t < len(o) and sign[o[t]] == sign[o[0]]:
                    t += 1
                if t == len(o):  # every vertex on one side: the new point is past one end
                    t = 0 if key_on(self.lines[i], p) < key_on(self.lines[i], o[0]) else len(o)
                nbrs[i] = tuple(o[u] for u in (t - 1, t) if 0 <= u < len(o))
        points = sorted({p for p in hit if p is not None}, key=lambda p: key_on(cand, p))
        rank = {p: r for r, p in enumerate(points)}
        for i, j in combinations(range(m), 2):
            pi, pj, v = hit[i], hit[j], self.pt[i, j]
            if pi is None or pj is None or v is None or pi == pj or sign[v] == 0:
                continue
            if v in nbrs[i] and v in nbrs[j] and abs(rank[pi] - rank[pj]) == 1:
                total += 1
        return total

    def candidates(self):
        seen = set()
        for p, q in combinations(self.vertices, 2):
            line = join(p, q)
            if line not in seen:
                seen.add(line)
                yield line


def perturbations(line, fixed, eps_exp=40):
    """Lines combinatorially next to `line`: tiny rotations about each vertex it passes through, and shifts."""
    a, b, c = line
    big = 10**eps_exp
    out = [norm_line(a * big, b * big, c * big + s * (abs(a) + abs(b))) for s in (1, -1)]
    through = [v for v in fixed.vertices if a * v[0] + b * v[1] + c * v[2] == 0]
    for x, y, w in through[:4]:
        for s in (1, -1):
            # rotate direction slightly, keep passing through (x, y, w)
            na, nb = a * big + s * b, b * big - s * a
            out.append(norm_line(na * w, nb * w, -(na * x + nb * y)))
    return out


def load(path):
    return [norm_line(*row) for row in json.loads(Path(path).read_text())["lines"]]


def hill_count(lines):
    sys.path.insert(0, str(HILL))
    from eval import count_triangles  # dev check only; official scores come from `hills eval`
    return len(count_triangles(lines))


def best_reinsert(args):
    lines, r, perturb = args
    fixed = Fixed(lines[:r] + lines[r + 1:])
    scored = [(fixed.count_with(c), c) for c in fixed.candidates()]
    if perturb:
        top = max(s for s, _ in scored)
        for s, c in [x for x in scored if x[0] >= top - 1]:
            scored.extend((fixed.count_with(p), p) for p in perturbations(c, fixed))
    top = max(s for s, _ in scored)
    return r, top, [c for s, c in scored if s == top]


def write(out, lines, note):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "solution.json").write_text(json.dumps({"lines": [list(l) for l in lines]}) + "\n")
    (out / "search.json").write_text(json.dumps(note) + "\n")


def size(line):
    return max(abs(v) for v in line)


def walk_worker(args):
    """Random walk over equal-or-better single-line replacements (a plateau walk).

    Among tied replacements, one of the three with the smallest coefficients is
    chosen, since coefficients grow when lines are drawn through crossing
    points. A walk whose coefficients pass 10^120 restarts from the seed.
    """
    start, seconds, seed = args
    rng = random.Random(seed)
    deadline = time.time() + seconds
    lines, score = list(start), hill_count(start)
    best, best_lines, steps, visited = score, list(lines), 0, set()
    while time.time() < deadline:
        r = rng.randrange(len(lines))
        _, top, cands = best_reinsert((lines, r, True))
        cands = sorted((c for c in cands if c != lines[r]), key=size)[:3]
        if top >= score and cands:
            lines = lines[:r] + [rng.choice(cands)] + lines[r + 1:]
            score = top
            steps += 1
            visited.add(frozenset(lines))
            if score > best or (score == best and max(map(size, lines)) < max(map(size, best_lines))):
                best, best_lines = score, list(lines)
        if max(map(size, lines)) > 10**120:
            lines, score = list(start), hill_count(start)
    return best, best_lines, steps, len(visited)


def pair_worker(args):
    """Remove lines r1, r2; re-insert the K best first lines, then the best second line for each."""
    lines, r1, r2, k = args
    rest = [l for t, l in enumerate(lines) if t not in (r1, r2)]
    f16 = Fixed(rest)
    first = sorted(((f16.count_with(c), c) for c in f16.candidates()), key=lambda x: (-x[0], size(x[1])))[:k]
    first += [(None, lines[r1]), (None, lines[r2])]  # so this move contains every single-line move
    best, best_lines = -1, None
    for _, c in first:
        f17 = Fixed(rest + [c])
        for c2 in f17.candidates():
            s = f17.count_with(c2)
            if s > best:
                best, best_lines = s, rest + [c, c2]
    return best, (r1, r2), best_lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["check", "pass", "walk", "pair"])
    parser.add_argument("solution")
    parser.add_argument("out", nargs="?")
    parser.add_argument("seconds", nargs="?", type=float, default=0)
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()
    lines = load(args.solution)
    if args.mode == "check":
        rng = random.Random(1)
        for r in range(len(lines)):
            fixed = Fixed(lines[:r] + lines[r + 1:])
            cands = list(fixed.candidates())
            for cand in [lines[r]] + rng.sample(cands, 5):
                if cand in fixed.line_set:
                    continue
                full = lines[:r] + [cand] + lines[r + 1:]
                fast, slow = fixed.count_with(cand), hill_count(full)
                assert fast == slow, (r, cand, fast, slow)
        print("incremental counter matches the hill's counter on", len(lines) * 6, "cases")
        return
    if args.mode == "pass":
        with Pool(args.workers) as pool:
            results = pool.map(best_reinsert, [(lines, r, True) for r in range(len(lines))])
        results.sort(key=lambda x: -x[1])
        print("DEV (exact, unofficial) best re-insert per removed line:", [(r, top, len(c)) for r, top, c in results])
        r, top, cands = results[0]
        pick = min(cands, key=lambda l: max(abs(v) for v in l))
        new = lines[:r] + [pick] + lines[r + 1:]
        print("chosen: remove", r, "->", top, "max |coef| digits", len(str(max(abs(v) for v in pick))))
        write(args.out, new, {"dev_exact_count": top, "removed": r, "mode": "pass"})
        return
    if args.mode == "pair":
        jobs = [(lines, r1, r2, 6) for r1, r2 in combinations(range(len(lines)), 2)]
        with Pool(args.workers) as pool:
            results = pool.map(pair_worker, jobs, chunksize=1)
        results.sort(key=lambda x: -x[0])
        tally = {}
        for b, _, _ in results:
            tally[b] = tally.get(b, 0) + 1
        print("DEV (exact, unofficial) best two-line replacement, count of line pairs per score:", sorted(tally.items(), reverse=True))
        best, pair, best_lines = results[0]
        print("best", best, "removing", pair, "max |coef| digits", len(str(max(map(size, best_lines)))))
        write(args.out, best_lines, {"dev_exact_count": best, "mode": "pair", "removed": pair})
        return
    with Pool(args.workers) as pool:
        results = pool.map(walk_worker, [(lines, args.seconds, s) for s in range(args.workers)])
    results.sort(key=lambda x: (-x[0], max(map(size, x[1]))))
    print("DEV (exact, unofficial) walk (best, steps, distinct arrangements) per worker:",
          [(b, s, v) for b, _, s, v in results])
    best, best_lines, _, _ = results[0]
    print("best", best, "max |coef| digits", len(str(max(map(size, best_lines)))))
    write(args.out, best_lines, {"dev_exact_count": best, "mode": "walk", "seconds": args.seconds})


if __name__ == "__main__":
    main()

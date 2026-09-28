"""Referee (AUDIT_k5L, Q1): the layer_mut_test checks on exact REAL line arrangements with many triple points
(lines through pairs of points of a small integer grid, plus the referee's explicit bent example with 4 bridge
ends, work/referee4/c7_bent_example.py).  Lines are relabelled by slope and swept left to right into a wiring word.
    uv run --no-project --with python-sat python work/referee4/k5L/layer_real_test.py N_PER_WORKER SEED"""
import random, sys
from collections import Counter
from fractions import Fraction
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from layer_mut_test import check, info
from arr import from_int_lines, from_tokens, sweep_from_rows

BENT7 = [[0, 1, 0], [6, -1, -72], [1, -7, 70], [1, 0, 0], [5, -6, 0], [7, -8, -2], [5, 6, -60]]


def to_wiring(lines):
    if any(b == 0 for a, b, c in lines): return None
    sl = [Fraction(-a, b) for a, b, c in lines]
    if len(set(sl)) < len(sl): return None
    order = sorted(range(len(lines)), key=lambda i: sl[i])
    L = [lines[i] for i in order]
    try: R = from_int_lines(L)
    except ValueError: return None
    rr = [[R.ev[e] - {l} for e in R.rows[l]] for l in range(R.n)]
    try: toks = sweep_from_rows(R.n, rr)
    except ValueError: return None
    A = from_tokens(toks, R.n)
    assert A.T == R.T and sorted(map(len, A.ev)) == sorted(map(len, R.ev))
    return A


def rand_arr(rng, n, grid):
    pts = [(x, y) for x in range(grid) for y in range(grid)]
    lines = set()
    while len(lines) < n:
        (x1, y1), (x2, y2) = rng.sample(pts, 2)
        a, b = y2 - y1, x1 - x2
        c = -(a * x1 + b * y1)
        from math import gcd
        g = gcd(gcd(abs(a), abs(b)), abs(c)) or 1
        a, b, c = a // g, b // g, c // g
        if b < 0 or (b == 0 and a < 0): a, b, c = -a, -b, -c
        lines.add((a, b, c))
    # tiny generic tilt of the whole plane so that no line is vertical
    return [[a + 97 * b, b * 1, c] if False else [a, b, c] for a, b, c in lines]


def worker(args):
    wid, N, seed = args
    rng = random.Random(seed * 1009 + wid); st = Counter()
    if wid == 0:
        A = to_wiring([[7 * a, 7 * b - a, 7 * c] for a, b, c in BENT7])
        if A is not None:
            st['bent7 built'] += 1; check(A, st)
    tries = 0
    while st['arrangements'] < N and tries < 200 * N:
        tries += 1
        n = rng.choice([7, 8, 9, 10, 11])
        lines = rand_arr(rng, n, rng.choice([4, 5, 6]))
        # shear x -> x + y/7 to break verticals: line a x + b y + c = 0 becomes 7a x + (7b - a) y + 7c = 0
        lines = [[7 * a, 7 * b - a, 7 * c] for a, b, c in lines]
        A = to_wiring(lines)
        if A is None or any(m > 3 for m in A.mult) or not (3 <= len(A.triples) <= 7): continue
        if not any(info(A, P)[3] == 'bent' for P in A.triples) and rng.random() < 0.8: continue
        try: check(A, st)
        except (AssertionError, ValueError, IndexError) as ex: st['exception ' + repr(ex)[:80]] += 1
    return st


if __name__ == '__main__':
    N, seed = int(sys.argv[1]), int(sys.argv[2])
    st = Counter()
    with Pool(4) as pool:
        for s in pool.imap_unordered(worker, [(w, N, seed) for w in range(4)]): st.update(s)
    for k_ in sorted(st, key=str): print(k_, st[k_])
    fail = [k_ for k_ in st if any(x in str(k_) for x in ('MISMATCH', 'UNSOUND', 'UNSAT', 'FAIL', 'capok False', 'TRI MISMATCH', 'exception'))]
    print('FAIL' if fail else 'PASS', fail)

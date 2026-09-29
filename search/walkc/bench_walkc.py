"""Per-call time of the walkc primitives against the Python originals (n = 18 gallery words, one core).

    uv run --no-project --with python-sat --with numpy python search/walkc/bench_walkc.py
"""
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.insert(1, str(ROOT / "search" / "walkc"))
sys.path.insert(2, str(ROOT / "search" / "dp1fast"))
sys.path.append(str(ROOT / "work" / "t3"))
sys.path.insert(3, str(ROOT / "work" / "research2"))
sys.path.insert(4, str(ROOT / "tools/external/kobon-solutions"))
import numpy as np  # noqa: E402
import walkc  # noqa: E402
import extend_dp  # noqa: E402
import dpwalk  # noqa: E402
import coverage  # noqa: E402
from arr import Arr  # noqa: E402
from verification.quick_check import count_triangles  # noqa: E402

rnd = random.Random(2)
fs = sorted((ROOT / "tools/external/kobon-solutions/gallery/data/18").glob("*.json"))
W = [extend_dp.parse_tokens(json.load(open(f))["gens"]) for f in rnd.sample(fs, 40)]
n = 18


def timeit(fn, args_list, reps=1):
    t = time.perf_counter()
    for _ in range(reps):
        for a in args_list:
            fn(*a)
    return (time.perf_counter() - t) / (reps * len(args_list)) * 1e6


rows = [dpwalk.rows_from_tokens(w, n) for w in W]
B = [walkc.to_word(w) for w in W]
res = []


def row(name, py, c):
    res.append((name, py, c))
    print(f"{name:34s} python {py:10.1f} us   walkc {c:8.2f} us   x{py / c:7.1f}")


row("delete_line", timeit(lambda w: extend_dp.delete_wire(w, n, 5), [(w,) for w in W], 20),
    timeit(lambda w: walkc.delete_line(w, 5, n), [(w,) for w in B], 200))
row("count (T only; py = quick_check)", timeit(lambda r: count_triangles(r), [(r,) for r in rows], 3),
    timeit(lambda w: walkc.count(w, n), [(w,) for w in B], 200))
row("count (T,k,b,Z,D; py = Arr+bridges)", timeit(lambda w: Arr(dpwalk.tokens_to_gens(w), n).T(), [(w,) for w in W], 2),
    timeit(lambda w: walkc.count(w, n), [(w,) for w in B], 200))
gens = [dpwalk.tokens_to_gens(w) for w in W]


def py_canon(g):
    chi = coverage.chi_from_word(g, n)
    trip, _, _ = coverage.tables(n)
    return coverage.canon(np.array([chi[t] for t in trip], dtype=np.int8), n)


py_canon(gens[0])
walkc.canon_hash(B[0], n)
row("canon (chi + 8n images + min)", timeit(py_canon, [(g,) for g in gens], 2),
    timeit(lambda w: walkc.canon_hash(w, n), [(w,) for w in B], 100))
row("rows hash (py = hash(rows))", timeit(lambda w: hash(dpwalk.rows_from_tokens(w, n)), [(w,) for w in W], 5),
    timeit(lambda w: walkc.rows_hash(w, n), [(w,) for w in B], 200))
row("rows->word sweep (incl. mask conv.)", timeit(lambda r: dpwalk.sweep(r, list(range(n))), [(r,) for r in rows], 3),
    timeit(lambda r: walkc.rows_to_word(r, None, 0), [(r,) for r in rows], 3))
# rebuild of a DP path: python Base.word_of vs walkc Base.eval (rebuild + count + hash)
cases = []
for w in W[:20]:
    bt, bn = dpwalk.delete_lines(w, n, [rnd.randrange(n)])
    pb = dpwalk.Base(bt, bn)
    r = pb.best()
    cnt, ps = pb.paths(r["T"] - 1, 100)
    cb = walkc.Base(bt, bn)
    cb.solve_max()
    cases.append((pb, ps[0], cb, r["T"] - 1))
t_py = time.perf_counter()
for pb, (seq, fid), cb, _ in cases:
    for _ in range(3):
        nt = pb.word_of(seq, fid)
        count_triangles(dpwalk.rows_from_tokens(nt, bn + 1))
        hash(dpwalk.rows_from_tokens(nt, bn + 1))
t_py = (time.perf_counter() - t_py) / (3 * len(cases)) * 1e6
t_c = time.perf_counter()
for pb, _, cb, thr in cases:
    cb.enum(thr, 100)
    for _ in range(50):
        cb.eval(0)
t_c = (time.perf_counter() - t_c) / (50 * len(cases)) * 1e6
row("path -> word + T + hash (per cand.)", t_py, t_c)
json.dump(res, open(ROOT / "work/eng/T10/bench_walkc.json", "w"))

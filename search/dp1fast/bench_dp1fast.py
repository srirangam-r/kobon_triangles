"""Benchmark: Python extend_dp.solve vs compiled solve on gallery arrangements (n = 14..18).
    uv run --no-project --with python-sat --with numpy python search/dp1fast/bench_dp1fast.py"""
import json, random, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from dp1fast import Dp1, extend_dp

G = Path(__file__).resolve().parent.parent.parent / "tools/external/kobon-solutions/gallery/data"
rnd = random.Random(3)
for n in (14, 16, 17, 18):
    fs = sorted((G / str(n)).glob("*.json"))
    fs = rnd.sample(fs, min(20, len(fs)))
    ws = [(extend_dp.parse_tokens(json.load(open(f))["gens"]), n) for f in fs]
    t = time.time()
    for tk, n_ in ws:
        st = extend_dp.build(tk, n_); extend_dp.solve(st, n_)
    tp = (time.time() - t) / len(ws)
    t = time.time(); ds = [Dp1(tk, n_) for tk, n_ in ws]; tb = (time.time() - t) / len(ws)
    t = time.time()
    for _ in range(20):
        for d in ds: d.solve()
    tc = (time.time() - t) / (20 * len(ws))
    t = time.time()
    for tk, n_ in ws:
        st = extend_dp.build(tk, n_)
    tpb = (time.time() - t) / len(ws)
    print(f"n={n}: python build+solve {tp*1e3:.1f} ms (build alone {tpb*1e3:.1f}) | C solve only {tc*1e3:.3f} ms, "
          f"python-side build+flatten {tb*1e3:.1f} ms | solve speedup x{(tp-tpb)/tc:.0f}, end-to-end x{tp/(tb+tc):.1f}")

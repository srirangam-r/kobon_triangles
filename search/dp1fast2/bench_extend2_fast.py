"""Benchmark of extend2_fast (compiled) vs extend2_dp (pure Python) on the n0 = 16 bridge cores.
    uv run --no-project --with python-sat --with numpy python search/dp1fast2/bench_extend2_fast.py [--py K]
Prints, per core: target-94 all-153-rank-pairs time of the compiled solver (Kx computation reported separately), and
for the first K cores also the time of extend2_dp on this machine (default K = 3).  Then exact-max times of
five rank pairs of core 0."""
import json
import sys
import time
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.insert(1, str(ROOT / "search/dp1fast2"))
sys.path.insert(2, str(ROOT / "work/research2"))
import extend2_dp as E2  # noqa: E402
import extend2_fast as F  # noqa: E402

K = int(sys.argv[sys.argv.index("--py") + 1]) if "--py" in sys.argv else 3
seeds = json.load(open(ROOT / "work/eng/T1/bridge_seeds.json"))
pairs = list(combinations(range(18), 2))
tc = []
tpy = []
for i, s in enumerate(seeds):
    t = time.time()
    B = F.FastBase(s["gens"])
    tk = time.time() - t
    t = time.time()
    for r1, r2 in pairs:
        assert B.pair(r1, r2, target=94)[0] is None
    dt = time.time() - t
    tc.append((tk, dt))
    line = f"{s['name']}: compiled target-94 x153 pairs: {dt:.2f}s (+ {tk:.2f}s base setup incl. Kx)"
    if i < K:
        t = time.time()
        P = E2.Base(s["gens"])
        for r1, r2 in pairs:
            assert E2.pair_search(P, r1, r2, target=94)[0] is None
        tp = time.time() - t
        tpy.append((tp, dt + tk))
        line += f" | extend2_dp {tp:.1f}s -> x{tp / (dt + tk):.0f} end to end, x{tp / dt:.0f} on the search"
    print(line, flush=True)
print(f"17 cores: compiled search total {sum(d for _, d in tc):.1f}s (mean {sum(d for _, d in tc) / len(tc):.2f}s per core), "
      f"setup total {sum(k for k, _ in tc):.1f}s")
if tpy:
    print(f"first {len(tpy)} cores: python {sum(a for a, _ in tpy):.1f}s vs compiled {sum(b for _, b in tpy):.1f}s "
          f"-> x{sum(a for a, _ in tpy) / sum(b for _, b in tpy):.0f}")
B = F.FastBase(seeds[0]["gens"])
for r in [(5, 8), (3, 9), (0, 1), (7, 16), (2, 17)]:
    t = time.time()
    T, _ = B.pair(*r)
    print(f"exact max of ranks {r} on core 0: {T} in {time.time() - t:.2f}s")

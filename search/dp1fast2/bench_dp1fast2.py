"""Benchmark: dp1fast (Python build + C DP) vs dp1fast2 (C build + C DP), end to end from a gens string.
    uv run --no-project --with python-sat --with numpy python search/dp1fast2/bench_dp1fast2.py"""
import json, random, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(1, str(HERE.parent / "dp1fast"))
import dp1fast, dp1fast2, extend_dp

G = HERE.parent.parent / "tools/external/kobon-solutions/gallery/data"
rnd = random.Random(3)
for n in (14, 16, 17, 18):
    fs = sorted((G / str(n)).glob("*.json"))
    gens = [json.load(open(f))["gens"] for f in rnd.sample(fs, min(20, len(fs)))]
    res = {}
    for name, mod in (("py", None), ("dp1fast", dp1fast), ("dp1fast2", dp1fast2)):
        reps = 3
        t = time.time()
        for _ in range(reps):
            for g in gens:
                if mod is None:
                    toks = extend_dp.parse_tokens(g); nn = max(a + w for a, w in toks)
                    st = extend_dp.build(toks, nn); extend_dp.solve(st, nn)
                else:
                    mod.Dp1.from_gens(g).best_by_rank()
        res[name] = (time.time() - t) / (reps * len(gens))
    print(f"n={n}: python {res['py']*1e3:.2f} ms | dp1fast {res['dp1fast']*1e3:.2f} ms | dp1fast2 {res['dp1fast2']*1e3:.3f} ms "
          f"| speedup vs dp1fast x{res['dp1fast']/res['dp1fast2']:.1f}, vs python x{res['py']/res['dp1fast2']:.0f}")

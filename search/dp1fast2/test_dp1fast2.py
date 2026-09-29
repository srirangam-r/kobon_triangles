"""Validation of dp1fast2 (C face-graph builder + DP) against dp1fast (Python build + C DP).

    uv run --no-project --with python-sat --with numpy python search/dp1fast2/test_dp1fast2.py [--nfiles 600]
Per gallery word (n = 10..18, stratified over the gallery directories, so many words have triple points):
  * the flattened face-graph arrays (foff, flen, kind, mask, nxt, below, starts) and T0 are identical,
  * solve(allow4) for allow4 in (False, True): by_k dict, T, per-start bests (start_best, start_best_k) identical,
  * canonical solve and best_by_rank() identical,
  * the argmax path recounts (count_triangles of the extended rows) to T.
Plus: enumeration (thr = max-1) path multisets identical on 40 small words.
"""
import collections
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(1, str(ROOT / "search/dp1fast"))
import numpy as np  # noqa: E402
import dp1fast  # noqa: E402
import dp1fast2  # noqa: E402
import extend_dp  # noqa: E402

G = ROOT / "tools/external/kobon-solutions/gallery/data"


def sample(nfiles, seed=5):
    by = collections.defaultdict(list)
    for d in sorted(G.iterdir()):
        if d.is_dir() and d.name.split("-")[0].isdigit() and 10 <= int(d.name.split("-")[0]) <= 18:
            by[d.name] = sorted(d.glob("*.json"))
    rnd = random.Random(seed)
    per = max(1, nfiles // len(by))
    out = []
    for k, v in by.items():
        out += rnd.sample(v, min(per, len(v)))
    rest = [f for v in by.values() for f in v if f not in set(out)]
    rnd.shuffle(rest)
    return (out + rest)[:nfiles]


def main():
    nfiles = int(sys.argv[sys.argv.index("--nfiles") + 1]) if "--nfiles" in sys.argv else 600
    files = sample(nfiles)
    fails = 0
    cnt = collections.Counter()
    t_old = t_new = 0.0
    for fn in files:
        j = json.load(open(fn))
        toks = extend_dp.parse_tokens(j["gens"])
        n = len(j["lines"])
        ntrip = sum(1 for g, w in toks if w == 3)
        t = time.time(); a = dp1fast.Dp1(toks, n); t_old += time.time() - t
        t = time.time(); b = dp1fast2.Dp1(toks, n); t_new += time.time() - t
        ok = a.T0 == b.T0
        for nm in ("foff", "flen", "kind_", "mask_", "nxt_", "below_", "starts"):
            ok = ok and np.array_equal(getattr(a, nm), getattr(b, nm))
        for allow4 in (False, True):
            t = time.time(); ra = a.solve(allow4); t_old += time.time() - t
            t = time.time(); rb = b.solve(allow4); t_new += time.time() - t
            ok = ok and ra["by_k"] == rb["by_k"] and ra["T"] == rb["T"] and ra["gain"] == rb["gain"]
            ok = ok and np.array_equal(ra["start_best"], rb["start_best"]) and np.array_equal(ra["start_best_k"], rb["start_best_k"])
            ok = ok and ra["path"] == rb["path"]
            ok = ok and extend_dp.count_triangles(b.rows(rb["path"])) == rb["T"]
            v, sb = b._start_best(allow4, False)
            ok = ok and v == rb["gain"] and np.array_equal(sb, ra["start_best"])
            ca, cb = a.solve(allow4, canonical=True), b.solve(allow4, canonical=True)
            ok = ok and np.array_equal(b._start_best(allow4, True)[1], ca["start_best"])
            ok = ok and ca["T"] == cb["T"] and np.array_equal(ca["start_best"], cb["start_best"])
            ok = ok and a.best_by_rank(allow4) == b.best_by_rank(allow4)
        cnt[(n, "triple" if ntrip else "simple", ok)] += 1
        if not ok:
            fails += 1
            print("FAIL", fn)
    print(f"{len(files)} words ({sum(v for k, v in cnt.items() if k[1] == 'triple')} with triple points):")
    for k in sorted(cnt):
        print("  ", k, cnt[k])
    print(f"mismatches: {fails}   time: dp1fast build+solve {t_old:.1f}s, dp1fast2 {t_new:.1f}s")

    bad = tested = 0
    small = [f for f in sample(300, seed=9) if len(json.load(open(f))["lines"]) <= 11][:40]
    for fn in small:
        j = json.load(open(fn)); toks = extend_dp.parse_tokens(j["gens"]); n = len(j["lines"])
        a, b = dp1fast.Dp1(toks, n), dp1fast2.Dp1(toks, n)
        T = a.max_T()
        for canon in (False, True):
            ca, pa = a.enum(T - 1, canonical=canon, cap=200000)
            cb, pb = b.enum(T - 1, canonical=canon, cap=200000)
            good = ca == cb and collections.Counter(map(tuple, pa)) == collections.Counter(map(tuple, pb))
            tested += 1
            if not good:
                bad += 1
                print("ENUM FAIL", fn, canon, ca, cb)
    print(f"enumeration comparisons: {tested}, failures {bad}")
    # completion is a no-op on words in which every pair crosses; n=17 ground truth (work/ext): max 93, never 94
    import glob
    comp_bad = 0
    for fn in files[:200]:
        g = json.load(open(fn))["gens"]
        toks = extend_dp.parse_tokens(g)
        nn = max(a + w for a, w in toks)
        if dp1fast2.parallel_pairs(toks, nn):
            continue
        comp_bad += dp1fast2.complete_tokens(toks, nn) != toks
    print("complete_tokens changed a word without parallel pairs:", comp_bad)
    gt = sorted(glob.glob(str(G / "17" / "*.json")))
    mx = []
    for fn in gt:
        d = dp1fast2.Dp1.from_gens(json.load(open(fn))["gens"], 17)
        br = d.best_by_rank()
        mx.append((d.T0, d.max_T(), d.max_T(True), sorted(set(br.values()))))
    print("n=17 records (T0, maxT, maxT allow4, distinct per-rank bests):", sorted(set(map(str, mx))))
    assert all(m[1] == 93 and m[2] == 93 for m in mx), "94 or missing 93 at n=17?!"
    return fails + bad + comp_bad


if __name__ == "__main__":
    sys.exit(1 if main() else 0)

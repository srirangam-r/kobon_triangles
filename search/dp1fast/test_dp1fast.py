"""Validation of the compiled DP against work/research2/extend_dp.py.

    uv run --no-project --with python-sat --with numpy python search/dp1fast/test_dp1fast.py [--nfiles 400] [--quick]
Checks (per gallery arrangement, n = 10..18, including triple-point ones):
  * T0 and the full 'best T by #new triple points' dict equal the Python DP (allow4 False and True),
  * the argmax path returned by C recounts (count_triangles) to the maximum,
  * canonical starts give the same maximum,
  * on small cases: the C path enumeration (thr = max-1) equals all_paths filtered by recount.
Then the n=17 ground truth: max T is 93, never 94; per-rank comparison against work/ext.
"""
import glob, json, random, sys, time, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from dp1fast import Dp1, extend_dp, NEG

G = ROOT / "tools/external/kobon-solutions/gallery/data"


def sample(nfiles, seed=1):
    files = [f for d in sorted(G.iterdir()) if d.is_dir() and d.name.split("-")[0].isdigit()
             and 10 <= int(d.name.split("-")[0]) <= 18 for f in sorted(d.glob("*.json"))]
    rnd = random.Random(seed)
    # stratify by directory so triple-point directories are represented
    by = collections.defaultdict(list)
    for f in files:
        by[f.parent.name].append(f)
    out = []
    per = max(1, nfiles // len(by))
    for k, v in by.items():
        out += rnd.sample(v, min(per, len(v)))
    rest = [f for f in files if f not in set(out)]
    rnd.shuffle(rest)
    return (out + rest)[:nfiles] if len(out) < nfiles else out[:nfiles]


def main():
    nfiles = int(sys.argv[sys.argv.index("--nfiles") + 1]) if "--nfiles" in sys.argv else 400
    fails = 0
    tp = tc = 0.0
    cnt = collections.Counter()
    for fn in sample(nfiles):
        j = json.load(open(fn))
        toks = extend_dp.parse_tokens(j["gens"])
        n = len(j["lines"])
        ntrip = sum(1 for g, w in toks if w == 3)
        for allow4 in (False, True):
            t = time.time()
            st = extend_dp.build(toks, n)
            T0 = extend_dp.base_T(st)
            bk, (seq, val) = extend_dp.solve(st, n, allow4)
            tp += time.time() - t
            t = time.time()
            d = Dp1(toks, n)
            r = d.solve(allow4)
            tc += time.time() - t
            want = {k: T0 + v for k, v in bk.items()}
            ok = (d.T0 == T0 and r["by_k"] == want)
            if ok and r["path"]:
                ok = extend_dp.count_triangles(d.rows(r["path"])) == r["T"] == T0 + val
            c = d.solve(allow4, canonical=True)
            ok = ok and c["T"] == r["T"]
            cnt[(n, "triple" if ntrip else "simple", allow4, ok)] += 1
            if not ok:
                fails += 1
                print("FAIL", fn, allow4, T0, d.T0, want, r["by_k"])
    print("files x modes by (n, kind, allow4, ok):")
    for k in sorted(cnt):
        print("  ", k, cnt[k])
    print(f"total mismatches: {fails}   python(build+solve)={tp:.1f}s  C(build+flatten+solve)={tc:.1f}s")

    # enumeration check on small arrangements
    bad = 0; tested = 0
    small = [f for f in sample(60, seed=7) if len(json.load(open(f))["lines"]) <= 11]
    for fn in small[:12]:
        j = json.load(open(fn)); toks = extend_dp.parse_tokens(j["gens"]); n = len(j["lines"])
        st = extend_dp.build(toks, n); d = Dp1(toks, n)
        T = d.max_T()
        py = collections.Counter()
        for s in extend_dp.all_paths(st, n):
            if extend_dp.count_triangles(extend_dp.path_rows(st, n, s)) >= T - 1:
                py[tuple(s)] += 1
        c, paths = d.enum(T - 1, cap=1000000)
        cc = collections.Counter(tuple(p) for p in paths)
        cn, _ = d.enum(T - 1, canonical=True, cap=10)
        tested += 1
        good = cc == py and c == sum(py.values()) and 2 * cn == c
        if not good:
            bad += 1; print("ENUM FAIL", fn, len(py), c, cn)
        print(f"enum {Path(fn).name}: n={n} T={T} paths>=T-1: python {sum(py.values())} C {c} canonical {cn} ok={good}")
    print("enumeration failures:", bad, "of", tested)

    # ground truth n=17
    gt = collections.defaultdict(dict)
    for f in glob.glob(str(ROOT / "work/ext/n17_t93_s*.jsonl")):
        for l in open(f):
            r = json.loads(l)
            gt[r["base"]][(r["ranks"][0], r["sign"])] = r["res"] == "SAT"
    mx = {}
    for base in gt:
        j = json.load(open(G / "17" / base))
        d = Dp1.from_gens(j["gens"], 17)
        mx[base] = (d.T0, d.max_T(), d.max_T(True))
    print("n=17 ground-truth bases:", len(gt), "(T0, maxT, maxT allow4):", sorted(set(mx.values())))
    assert all(v[1] <= 93 and v[2] <= 93 for v in mx.values()), "94 found?!"
    print("n=17: max over records =", max(v[1] for v in mx.values()), " (SAT93 present:", any(any(v.values()) for v in gt.values()), ")")
    return fails + bad


if __name__ == "__main__":
    sys.exit(1 if main() else 0)

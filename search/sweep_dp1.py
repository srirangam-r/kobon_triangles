"""Exact one-line completion sweep: for every n-line sample (jsonl rows with "gens"), the compiled DP
(search/dp1fast) gives the maximum T after adding one pseudoline (triple points allowed, no 4-fold point).
Prints the distribution of the maximum and writes every row reaching >= --flag to <out>.

    python search/sweep_dp1.py <out.jsonl> <in.jsonl> [<in.jsonl> ...] [--workers 6] [--flag 94] [--min-T 82]
"""
import argparse
import collections
import json
import sys
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search" / "dp1fast"))
sys.path.insert(0, str(ROOT / "search"))
sys.path.append(str(ROOT / "work/research2"))


def work(args):
    from dp1fast import Dp1
    rows, flag = args
    out = []
    for r in rows:
        try:
            res = Dp1.from_gens(r["gens"]).solve(False, True)
        except Exception as e:  # report, never hide
            out.append((r, None, repr(e)[:200]))
            continue
        best = res["T"]
        out.append((r, best, None))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--flag", type=int, default=94)
    ap.add_argument("--min-T", type=int, default=0)
    a = ap.parse_args()
    seen, rows = set(), []
    for f in a.inputs:
        for l in open(f):
            try:
                r = json.loads(l)
            except json.JSONDecodeError:
                continue
            key = r.get("h") or r["gens"]
            if key in seen or r.get("T", 99) < a.min_T:
                continue
            seen.add(key)
            rows.append(r)
    chunks = [rows[i:i + 200] for i in range(0, len(rows), 200)]
    dist, errs, hits = collections.Counter(), 0, 0
    fo = open(a.out, "a")
    with Pool(a.workers) as p:
        for out in p.imap_unordered(work, [(c, a.flag) for c in chunks]):
            for r, best, err in out:
                if err:
                    errs += 1
                    if errs <= 3:
                        print("ERR", err, flush=True)
                    continue
                dist[(r.get("T"), best)] += 1
                if best is not None and best >= a.flag:
                    hits += 1
                    fo.write(json.dumps({**r, "best18": best}) + "\n")
                    fo.flush()
                    print(f"HIT base T={r.get('T')} k={r.get('k')} bridges={r.get('bridges')} -> {best}", flush=True)
    print(f"{len(rows)} distinct bases; errors {errs}; hits >= {a.flag}: {hits}")
    by_best = collections.Counter()
    for (T, best), c in dist.items():
        by_best[best] += c
    print("max T after one added line:", dict(sorted(by_best.items())))
    print("(base T, best):", dict(sorted(dist.items(), reverse=True)[:12]))


if __name__ == "__main__":
    main()

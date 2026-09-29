"""Independent recount of every class record (cls_w*.jsonl) of a dpwalk_c / dpwalk2 run.

    uv run --no-project --with python-sat --with numpy python search/walkc/recount_records.py RUN_DIR [--procs 3]
Per record: T == quick_check.count_triangles(replay_word(gens).rows) (the record's T), k == number of multiple points
of replay_word, and for every record with k > 0 (or a sample of the others): (k, bridges, Z, D) == the work/t3 Arr
values (Arr.Z / Arr.D, bridge = doubly used segment between two triple points), plus the canon id
sha1(coverage.canon(chi))[:16] == the record's canon id.  Also T via kobon_sat.count_general on a sample.
"""
import argparse
import glob
import hashlib
import json
import random
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.insert(1, str(ROOT / "work/lns/push"))
sys.path.append(str(ROOT / "work/t3"))
sys.path.insert(2, str(ROOT / "tools/external/kobon-solutions"))
from verification.quick_check import count_triangles, replay_word  # noqa: E402


def check(args):
    line, deep = args
    import numpy as np
    r = json.loads(line)
    n, gens = r["n"], r["gens"]
    st = replay_word(gens, n)
    bad = []
    T = count_triangles(st.rows)
    if T != r["T"]:
        bad.append(("T", T, r["T"]))
    if len(st.multiple_points) != r["k"]:
        bad.append(("k", len(st.multiple_points), r["k"]))
    if deep:
        from arr import Arr
        a = Arr(gens, n)
        ev = a.events
        br = set()
        for x in range(n):
            row = a.rows[x]
            for e in range(len(row) - 1):
                if len(a.t[x][e]) == 2 and len(ev[row[e]]) == 3 and len(ev[row[e + 1]]) == 3:
                    br.add(frozenset((row[e], row[e + 1])))
        if (a.T(), len(a.triples), len(br), a.Z(), a.D()) != (r["T"], r["k"], r["b"], r["Z"], r["D"]):
            bad.append(("arr", (a.T(), len(a.triples), len(br), a.Z(), a.D()), (r["T"], r["k"], r["b"], r["Z"], r["D"])))
        import coverage
        trip, _, _ = coverage.tables(n)
        chi = coverage.chi_from_word(gens, n)
        v = np.array([chi[t] for t in trip], dtype=np.int8)
        if hashlib.sha1(coverage.canon(v, n)).hexdigest()[:16] != r["canon"]:
            bad.append(("canon",))
        from kobon_sat import count_general
        if len(count_general(n, chi)) != r["T"]:
            bad.append(("count_general",))
    return bad, r["T"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--procs", type=int, default=3)
    ap.add_argument("--sample", type=int, default=1500, help="deep-checked records without triple points")
    a = ap.parse_args()
    lines = [ln for f in sorted(glob.glob(str(Path(a.dir) / "cls_w*.jsonl"))) for ln in open(f) if ln.strip()]
    rnd = random.Random(0)
    flat = [json.loads(ln) for ln in lines]
    deep_idx = {i for i, r in enumerate(flat) if r["k"] > 0 and (r["b"] >= 1 or rnd.random() < 0.05)}
    deep_idx |= set(rnd.sample(range(len(flat)), min(a.sample, len(flat))))
    with Pool(a.procs) as p:
        res = p.map(check, [(ln, i in deep_idx) for i, ln in enumerate(lines)], chunksize=200)
    bad = [b for b, _ in res if b]
    print(f"{len(lines)} records recounted with quick_check (T, k); {len(deep_idx)} deep-checked "
          f"(Arr T/k/bridges/Z/D, canon id, count_general); T histogram {dict(sorted(Counter(t for _, t in res).items()))}")
    print("records with k > 0:", sum(1 for r in flat if r["k"] > 0), "; with bridges >= 1:", sum(1 for r in flat if r["b"] >= 1),
          "; max k", max(r["k"] for r in flat), "max bridges", max(r["b"] for r in flat))
    print("MISMATCHES:", len(bad), bad[:5])
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

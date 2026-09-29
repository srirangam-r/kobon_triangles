"""Frontier of generator samples: best T at each number of doubly used bridges, distinct classes per (T, bridges)
cell, and a spot check of the sample's own bridge count against the independent checker (test_k5L_layer.geometry).

    python search/frontier.py <samples.jsonl> [...] [--check 200]
"""
import argparse
import collections
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.insert(1, str(ROOT / "work/lns/push"))
sys.path.append(str(ROOT / "work/t3"))
import numpy as np  # noqa: E402
from coverage import canon, tables  # noqa: E402
from run_lns import chi_from_word  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--check", type=int, default=200)
    a = ap.parse_args()
    rows = []
    for f in a.files:
        for l in open(f):
            try:
                rows.append(json.loads(l))
            except json.JSONDecodeError:
                pass
    n = rows[0]["n"]
    trip, _, _ = tables(n)
    cells = collections.defaultdict(set)
    for r in rows:
        chi = chi_from_word(r["gens"], n)
        cells[(r["T"], r.get("bridges", 0))].add(canon(np.array([chi[t] for t in trip], dtype=np.int8), n))
    front = {}
    for (T, b), s in cells.items():
        front[b] = max(front.get(b, 0), T)
    print(f"n={n}: {len(rows)} samples")
    print("frontier (bridges -> best T):", dict(sorted(front.items())))
    Ts = sorted({T for T, _ in cells}, reverse=True)[:4]
    for T in Ts:
        print(f"  T={T}: distinct classes by bridges", {b: len(cells[(T, b)]) for (T2, b) in sorted(cells) if T2 == T})
    from arr import Arr
    from test_k5L_layer import geometry
    sample = random.Random(0).sample(rows, min(a.check, len(rows)))
    bad = 0
    for r in sample:
        ar = Arr(r["gens"])
        b = len(geometry(ar)[1])
        if b != r.get("bridges", 0) or ar.T() != r["T"]:
            bad += 1
    print(f"spot check vs independent checker: {len(sample) - bad}/{len(sample)} agree on (T, bridges)")


if __name__ == "__main__":
    main()

"""Reach of a generator: fraction of held-out real cores (canonical classes) that its samples rediscover, per T,
and the implied detection probability for a 94 whose best 17-line core follows the non-perfect 93-core mix.

    python search/reach.py work/pls/cores93_heldout.json <samples.jsonl> [...]
"""
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.insert(1, str(ROOT / "work/lns/push"))
import numpy as np  # noqa: E402
from coverage import canon, tables  # noqa: E402
from run_lns import chi_from_word  # noqa: E402

# best-core mix of the 995 non-perfect gallery 93s (T17 = 79..84); perfect 85 cores are excluded by the DP
MIX = {84: 153, 83: 187, 82: 292, 81: 247, 80: 111, 79: 5}


def cls(row):
    n = row["n"]
    trip, _, _ = tables(n)
    chi = chi_from_word(row["gens"], n)
    return canon(np.array([chi[t] for t in trip], dtype=np.int8), n)


def main():
    held = json.load(open(sys.argv[1]))
    hc = collections.defaultdict(set)
    for r in held:
        hc[r["T"]].add(cls(r))
    seen = set()
    nsamp = 0
    for f in sys.argv[2:]:
        for l in open(f):
            try:
                r = json.loads(l)
            except json.JSONDecodeError:
                continue
            if r.get("T", 0) >= 79:
                seen.add(cls(r))
                nsamp += 1
    print(f"{nsamp} samples, {len(seen)} distinct classes (T >= 79)")
    tot = sum(MIX.values())
    pdet = 0.0
    for T in sorted(hc, reverse=True):
        got = len(hc[T] & seen)
        frac = got / len(hc[T])
        pdet += MIX.get(T, 0) / tot * frac
        print(f"  held-out real cores T17={T}: {got}/{len(hc[T])} rediscovered ({frac:.1%})")
    print(f"implied P(detect a 94 | its best core follows the 93 mix, one-line completion exact) ~ {pdet:.1%}")


if __name__ == "__main__":
    main()

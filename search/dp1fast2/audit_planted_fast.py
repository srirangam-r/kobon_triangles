"""Planted-solution audit of the compiled exact extension tools (0 false negatives at the real scale).

Random gallery 93s (n = 18):
  one   delete 1 line d -> dp1fast2's exact one-line DP, started at the deleted line's slope rank d, must reach >= 93
        (also the overall maximum, canonical starts, must be >= 93);
  two   delete 2 lines D = (d1 < d2) -> extend2_fast at ranks (d1, d2) in target mode 93 must reach >= 93 (and in
        max mode the exact maximum must be >= 93; its witness recounts).
The original arrangement is a witness, so any "< 93" would be a false negative.

    uv run --no-project --with python-sat --with numpy python search/dp1fast2/audit_planted_fast.py one 300
    uv run --no-project --with python-sat --with numpy python search/dp1fast2/audit_planted_fast.py two 30
"""
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.insert(1, str(ROOT / "search/dp1fast2"))
import numpy as np  # noqa: E402
import audit_planted as AP  # noqa: E402
import dp1fast2  # noqa: E402
import extend2_fast as F  # noqa: E402
import extend_dp as X  # noqa: E402


def main():
    mode, N = sys.argv[1], int(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 777
    rng = random.Random(seed)
    fails = 0
    t0 = time.time()
    if mode == "one":
        at_rank = 0
        for i in range(N):
            name, D, w = AP.planted(1, rng)
            d = D[0]
            dp = dp1fast2.Dp1.from_gens(w)
            n0 = dp.n
            T = dp.max_T()
            # best over the start at left gap d (non-canonical, left-inf start of the face with d lines below)
            face = 0 if d == 0 else (1 if d == n0 else d + 1)
            s0 = int(dp.foff[face])
            _, sb = dp._start_best(False, False)
            idx = int(np.nonzero(dp.starts == s0)[0][0])
            Td = dp.T0 + int(sb[idx])
            ok = T >= 93 and Td >= 93
            at_rank += Td >= 93
            if not ok:
                fails += 1
                print("FALSE NEGATIVE", name, D, "overall", T, "at rank", Td, flush=True)
        print(f"one-line DP (dp1fast2): {N} planted cases, {at_rank} reach >= 93 at the deleted rank, "
              f"{fails} false negatives  [{time.time() - t0:.1f}s]")
    else:
        for i in range(N):
            name, D, w = AP.planted(2, rng)
            B = F.FastBase(w)
            T, best = B.pair(D[0], D[1], target=93)
            Tm, bm = B.pair(D[0], D[1])
            ok = T is not None and T >= 93 and Tm is not None and Tm >= 93 and Tm >= T
            if bm is not None:
                ok = ok and X.count_triangles(B.witness_rows(D[0], D[1], bm)) == Tm
            if not ok:
                fails += 1
            print(f"case {i}: {name} deleted {D}: n0={B.n} T0={B.T0} target-93 -> {T}, exact max -> {Tm} "
                  f"{'ok' if ok else 'FALSE NEGATIVE'}", flush=True)
        print(f"two-line (extend2_fast): {N} planted cases, {fails} false negatives  [{time.time() - t0:.1f}s]")
    return fails


if __name__ == "__main__":
    sys.exit(1 if main() else 0)

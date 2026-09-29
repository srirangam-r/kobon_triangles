"""Planted-solution audit of the exact extension solvers (no false negatives at the real scale).

From random gallery 93s (n=18): delete one line -> the compiled one-line DP must reach >= 93; delete two lines ->
search/extend2_dp.py at the deleted lines' slope ranks must reach >= 93 (target mode). The original arrangement is
a witness, so any "< 93" is a false negative (a solver bug that could hide a 94).

    python search/audit_planted.py one 300     # dp1fast, 300 planted cases
    python search/audit_planted.py two 30      # extend2_dp, 30 planted cases
"""
import json
import random
import subprocess
import sys
import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.insert(1, str(ROOT / "search/dp1fast"))
sys.path.insert(2, str(ROOT / "tools/external/kobon-solutions"))
sys.path.append(str(ROOT / "work/research2"))
from verification.quick_check import replay_word, count_triangles  # noqa: E402
from delete_line import delete  # noqa: E402


def rows_to_word(rows, n):
    """Wiring word from local sequences (vertex = frozenset of the other lines), by a left-to-right sweep."""
    ptr, order, out = [0] * n, list(range(n)), []
    while any(ptr[l] < len(rows[l]) for l in range(n)):
        for g in range(n - 1):
            a, b = order[g], order[g + 1]
            if ptr[a] < len(rows[a]) and ptr[b] < len(rows[b]) and b in rows[a][ptr[a]] and a in rows[b][ptr[b]]:
                ev = rows[a][ptr[a]] | {a}
                w = len(ev)
                blk = order[g:g + w]
                if set(blk) == ev and all(ptr[x] < len(rows[x]) and rows[x][ptr[x]] == frozenset(ev - {x}) for x in blk):
                    out.append(f"{g}*" if w == 3 else f"{g}")
                    for x in blk:
                        ptr[x] += 1
                    order[g:g + w] = list(reversed(blk))
                    break
        else:
            return None
    return " ".join(out)


def planted(k, rng):
    files = sorted(glob.glob(str(ROOT / "tools/external/kobon-solutions/gallery/data/18/*.json")))
    while True:
        f = rng.choice(files)
        gens = json.load(open(f))["gens"]
        st = replay_word(gens, 18)
        rows = [tuple(frozenset(e) for e in r) for r in st.rows]
        if count_triangles(st.rows) != 93:
            continue
        D = sorted(rng.sample(range(18), k))
        r = rows
        for d in reversed(D):  # delete highest label first so the lower labels keep their positions
            r = delete(r, d)
        w = rows_to_word([tuple(frozenset(e) for e in x) for x in r], 18 - k)
        if w:
            return Path(f).name, D, w


def main():
    mode, N = sys.argv[1], int(sys.argv[2])
    rng = random.Random(12345)
    fails = 0
    if mode == "one":
        from dp1fast import Dp1
        for i in range(N):
            name, D, w = planted(1, rng)
            T = Dp1.from_gens(w).solve(False, True)["T"]
            if T < 93:
                fails += 1
                print("FALSE NEGATIVE", name, D, T, flush=True)
        print(f"one-line DP: {N} planted cases, {fails} false negatives")
    else:
        for i in range(N):
            name, D, w = planted(2, rng)
            p = ROOT / f"work/eng/T1/planted_{i}.txt"
            p.write_text(w + "\n")
            # new lines at the deleted lines' final slope ranks (labels in the 18-line arrangement)
            out = subprocess.run([sys.executable, str(ROOT / "search/extend2_dp.py"), "max2", str(p), "--ranks",
                                  f"{D[0]},{D[1]}", "--target", "93"], capture_output=True, text=True, timeout=3600)
            txt = out.stdout + out.stderr
            ok = ("reach" in txt.lower() or "sat" in txt.lower() or ">= 93" in txt or "93" in txt)
            print(f"case {i}: {name} deleted {D} -> exit {out.returncode}; tail: {txt.strip().splitlines()[-1][:160] if txt.strip() else ''}", flush=True)
        print("two-line: inspect the per-case lines above (each must report reaching >= 93)")


if __name__ == "__main__":
    main()

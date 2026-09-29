"""Validation of search/extend2_fast.py against search/extend2_dp.py (the pure-Python exact two-line solver).

    uv run --no-project --with python-sat --with numpy python search/dp1fast2/test_extend2_fast.py [A] [B] [C] [D]
  D  base + L1 rebuild: the C partner gain (build_ext + exact second-line DP) equals Base.partner_gain for random
     first-line paths at n0 = 8..16 (including triple-point bases and paths through vertices), and the (G, D) tables,
     MG / MN and count_ge agree with the Python Dp.
  A  exact maximum on >= 40 (base, rank pair) cases at n0 = 8..12 (incl. triple-point bases and edge pairs):
     max mode == extend2_dp.pair_search; the witness recounts; target mode at max / max+1 agrees; a few cases are
     also checked against SAT (fastext.Ext: SAT at max, UNSAT at max+1).
  B  target-94 on work/eng/T1/bridge_seeds.json (17 n0=16 seeds x 153 rank pairs): every pair unreached, and the
     partner-eval / pruned counters equal those of the extend2_dp run in work/eng/T1/bench94.log (same search tree);
     plus the exact maxima quoted in work/eng/T1/REPORT.md (SAT-validated there).
  E  exact max C vs Python at n0 = 13..15 (simple and triple-point bases).
Bases with parallel pairs are compared uncompleted (parity with extend2_dp) and, against SAT, completed.
"""
import glob
import json
import random
import re
import sys
import time
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.insert(1, str(ROOT / "search/dp1fast2"))
sys.path.insert(2, str(ROOT / "work/research2"))
import ctypes  # noqa: E402
import numpy as np  # noqa: E402
import extend_dp as X  # noqa: E402
import extend2_dp as E2  # noqa: E402
import extend2_fast as F  # noqa: E402
import dp1fast2 as D2  # noqa: E402

G = ROOT / "tools/external/kobon-solutions/gallery/data"


def words(n0, k, rnd, triple=None):
    dirs = [d for d in sorted(G.iterdir()) if d.is_dir() and d.name.split("-")[0] == str(n0)]
    fs = [f for d in dirs for f in sorted(d.glob("*.json"))]
    out = []
    for f in rnd.sample(fs, len(fs)):
        g = json.load(open(f))["gens"]
        has = "*" in g
        if triple is None or has == triple:
            out.append((f.name, g))
        if len(out) == k:
            break
    return out


def part_D():
    rnd = random.Random(11)
    tot = bad = 0
    for n0, k in ((8, 3), (10, 3), (12, 3), (14, 3), (16, 4)):
        for name, gens in words(n0, k, rnd) + words(n0, 2, rnd, triple=True):
            P = E2.Base(gens)
            Fb = F.FastBase(gens, kx=P.Kx)
            L = Fb.L
            d1 = Fb.dp1
            foff = d1.foff
            # (G, D) tables, MG / MN, count_ge
            for gap in range(n0 + 1):
                mg, mn = ctypes.c_int(), ctypes.c_int()
                L.ext2_mgmn(Fb.h, gap, ctypes.byref(mg), ctypes.byref(mn))
                ok = mg.value == P.dp(gap, "G").val and mn.value == P.dp(gap, "N").val
                out = np.zeros(64, dtype=np.int32)
                dc = L.ext2_bydn(Fb.h, gap, D2._ptr(out))
                py = P.by_d(gap)
                ok = ok and {k: int(out[k]) for k in range(dc) if out[k] > -99} == py
                for mode, name_ in ((0, "G"), (1, "N")):
                    dp = P.dp(gap, name_)
                    for thr in (dp.val - 3, dp.val - 1, dp.val):
                        ok = ok and L.ext2_count_ge(Fb.h, gap, mode, thr) == dp.count_ge(thr)
                tot += 1
                bad += not ok
                if not ok:
                    print("TABLE MISMATCH", name, gap)
            # partner gains along random first-line paths
            for _ in range(6):
                gap = rnd.randrange(n0 + 1)
                dp = P.dp(gap, "G")
                paths = list(dp.paths(dp.val - 6))
                if not paths:
                    continue
                for w, g1, seq, fs in rnd.sample(paths, min(25, len(paths))):
                    st = [int(foff[f]) + P.G.index(f)[x] for f, x in zip(fs, seq)]
                    pg = rnd.randrange(n0 + 2)
                    want = P.partner_gain(gap, seq, pg)
                    got = L.ext2_partner(Fb.h, gap, D2._ptr(np.ascontiguousarray(st, dtype=np.int32)), len(st), pg)
                    tot += 1
                    if got != want:
                        bad += 1
                        print("PARTNER MISMATCH", name, gap, pg, got, want)
        print(f"  D: n0={n0} done, {tot} comparisons, {bad} mismatches", flush=True)
    return bad


def part_A():
    from fastext import Ext
    sys.path.insert(0, str(ROOT / "work/lns/push"))
    from run_lns import chi_from_word
    rnd = random.Random(21)
    bad = cases = sat_checked = par_cases = 0
    for n0, k, kt in ((8, 4, 2), (9, 4, 1), (10, 5, 3), (11, 4, 1), (12, 3, 3)):
        for name, gens in words(n0, k, rnd) + words(n0, kt, rnd, triple=True):
            P = E2.Base(gens)
            Fb = F.FastBase(gens, kx=P.Kx)
            par = bool(Fb.parallel)
            Fc = F.FastBase(gens, complete=True) if par else None
            pairs = [(0, 1), (0, n0 + 1), (n0, n0 + 1)] + rnd.sample(list(combinations(range(n0 + 2), 2)), 4)
            chi0 = None
            for r1, r2 in pairs:
                t = time.time()
                a, _ = E2.pair_search(P, r1, r2)
                tp = time.time() - t
                t = time.time()
                b, w = Fb.pair(r1, r2)
                tc = time.time() - t
                ok = a == b
                if b is not None:
                    ok = ok and X.count_triangles(Fb.witness_rows(r1, r2, w)) == b
                for tt in ((a or 0) + 1, a or 0):
                    ok = ok and ((E2.pair_search(P, r1, r2, target=tt)[0] is not None) == (Fb.pair(r1, r2, target=tt)[0] is not None))
                if n0 <= 10 and b is not None and (par or rnd.random() < 0.5):
                    # SAT models see the completed base (every pair crosses); identical for words without parallel pairs
                    chi0 = chi0 or chi_from_word(gens, n0)
                    sat = lambda tt: any(Ext(chi0, n0, (r1, r2), s, tt, n=n0 + 2).solve() is not None for s in (1, -1))
                    bc = Fc.pair(r1, r2)[0] if par else b
                    ok = ok and sat(bc) and not sat(bc + 1)
                    sat_checked += 1
                    par_cases += par
                cases += 1
                bad += not ok
                if not ok:
                    print("MISMATCH", name, n0, r1, r2, a, b)
            print(f"  A: n0={n0} {name}: cases so far {cases}, mismatches {bad} (last: py {tp:.2f}s, C {tc*1e3:.1f} ms)", flush=True)
    print(f"  A: {cases} (base, rank pair) cases, {sat_checked} also SAT-checked ({par_cases} of them on a base with "
          f"parallel pairs, via complete=True), mismatches {bad}")
    return bad


def part_B():
    seeds = json.load(open(ROOT / "work/eng/T1/bridge_seeds.json"))
    log = {}
    for ln in open(ROOT / "work/eng/T1/bench94.log"):
        m = re.match(r"(\S+): n0=16 .*exact partner evals (\d+), pruned 0\+(\d+)", ln)
        if m:
            log[m.group(1)] = (int(m.group(2)), int(m.group(3)))
    recs = {}
    for ln in open(ROOT / "work/eng/T1/bench94.jsonl"):
        r = json.loads(ln)
        recs[(r["name"], r["r1"], r["r2"])] = r["reached"]
    bad = pairs = 0
    tot = 0.0
    for s in seeds:
        t = time.time()
        Fb = F.FastBase(s["gens"])
        for r1, r2 in combinations(range(18), 2):
            T, _ = Fb.pair(r1, r2, target=94)
            pairs += 1
            if (T is not None) != recs[(s["name"], r1, r2)] or T is not None:
                bad += 1
                print("MISMATCH vs bench94.jsonl", s["name"], r1, r2, T)
        st = Fb.stats()
        want = log.get(s["name"])
        dt = time.time() - t
        tot += dt
        if want and (st["evals"], st["pruned2"]) != want:
            bad += 1
            print("COUNTER MISMATCH", s["name"], st, want)
        print(f"  B: {s['name']}: {dt:.2f}s evals {st['evals']} pruned {st['pruned2']} (python log: {want})", flush=True)
    print(f"  B: {pairs} rank pairs, mismatches {bad}, total {tot:.1f}s")
    # exact maxima quoted in T1/REPORT.md for seed 0 (SAT-validated there: SAT at max, UNSAT at max+1)
    Fb = F.FastBase(seeds[0]["gens"])
    for (r1, r2), want in {(5, 8): 88, (3, 9): 88, (0, 1): 89, (7, 16): 88, (2, 17): 88}.items():
        t = time.time()
        T, w = Fb.pair(r1, r2)
        ok = T == want and X.count_triangles(Fb.witness_rows(r1, r2, w)) == T
        bad += not ok
        print(f"  B: exact max ({r1},{r2}) = {T} (T1 report: {want}) {'ok' if ok else 'MISMATCH'} [{time.time()-t:.1f}s]", flush=True)
    return bad


def part_E():
    """Larger bases (n0 = 13..15, simple and triple-point): exact max, C vs Python, plus target mode at max / max+1."""
    rnd = random.Random(31)
    bad = cases = 0
    for n0 in (13, 14, 15):
        for name, gens in words(n0, 2, rnd) + words(n0, 1, rnd, triple=True):
            P = E2.Base(gens)
            Fb = F.FastBase(gens, kx=P.Kx)
            for r1, r2 in rnd.sample(list(combinations(range(n0 + 2), 2)), 3):
                t = time.time()
                a, _ = E2.pair_search(P, r1, r2)
                tp = time.time() - t
                b, w = Fb.pair(r1, r2)
                ok = a == b and (b is None or X.count_triangles(Fb.witness_rows(r1, r2, w)) == b)
                for tt in ((a or 0) + 1, a or 0):
                    ok = ok and ((E2.pair_search(P, r1, r2, target=tt)[0] is not None) == (Fb.pair(r1, r2, target=tt)[0] is not None))
                cases += 1
                bad += not ok
                print(f"  E: n0={n0} {name} ({r1},{r2}): py {a} C {b} {'ok' if ok else 'MISMATCH'} (python {tp:.1f}s)", flush=True)
    print(f"  E: {cases} cases, mismatches {bad}")
    return bad


if __name__ == "__main__":
    parts = [a for a in sys.argv[1:] if a in "ABCDE"] or list("DAB")
    bad = 0
    for p in parts:
        print(f"part {p}", flush=True)
        bad += {"A": part_A, "B": part_B, "D": part_D, "E": part_E}[p]()
    print("TOTAL MISMATCHES:", bad)
    sys.exit(1 if bad else 0)

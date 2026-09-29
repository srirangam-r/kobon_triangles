#!/usr/bin/env python3
"""Compiled exact two-line extension solver (search/dp1fast2/ext2.c): same semantics and CLI as extend2_dp.py.

Exact maximum number of bounded triangles after adding two pseudolines at final slope ranks r1 < r2 to a wiring
word (triple points allowed, no 4-fold point).  The bound / branch-and-bound scheme is that of extend2_dp.py
(see its docstring); the whole pair_search (one-line DPs in modes G/N/S, (G, D)-Pareto tables, plan costs,
pruned enumeration, base+L1 rebuild, exact second-line DP) runs in C.  Python only parses input, computes the
interaction constant Kx (extend2_dp.interaction_bound, once per base) and prints.

CLI:
    extend2_fast.py max2 INPUT [--ranks r1,r2] [--target T] [--limit K] [--verify] [--verbose] [--out F]
    extend2_fast.py selftest
INPUT: a gallery JSON, a seeds JSON list (seeds16.json / bridge_seeds.json format) or a text file with one word per
line.  Library use:
    from extend2_fast import FastBase
    B = FastBase(gens); B.pair(r1, r2, target=None) -> (T, witness) or (None, None)
Bases with parallel pairs: the default is exactly extend2_dp's semantics (a parallel pair never meets).  The SAT
models (fastext / kobon_sat) complete such a base with far crossings; use --complete / FastBase(complete=True) to
match them (work/eng/T8/REPORT.md).  A no-op when every pair of base lines crosses (all gallery n >= 10 words).
"""
import argparse
import ctypes
import json
import sys
import time
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "work/research2"))
sys.path.insert(0, str(ROOT / "search"))
sys.path.insert(0, str(ROOT / "search/dp1fast2"))
import extend_dp as X  # noqa: E402
import extend2_dp as E2  # noqa: E402
import dp1fast2 as D2  # noqa: E402


def _ptr(a):
    return a.ctypes.data_as(ctypes.c_void_p)


class FastBase:
    """A base arrangement with the compiled two-line solver.  Mirrors extend2_dp.Base (pair_search -> pair)."""

    def __init__(self, gens=None, tokens=None, n=None, kx=None, complete=False):
        self.tokens = tokens if tokens is not None else X.parse_tokens(gens)
        self.n = n if n is not None else max(g + w for g, w in self.tokens)
        par = D2.parallel_pairs(self.tokens, self.n)
        self.parallel = par
        if par and complete:
            self.tokens = D2.complete_tokens(self.tokens, self.n)
        elif par:
            print(f"warning: base has {len(par)} parallel pair(s) {par[:4]}; without --complete the search treats them "
                  f"as never crossing and is NOT equivalent to the SAT models (use complete=True / --complete)",
                  file=sys.stderr)
        if kx is None:
            G = E2.Graph(self.tokens, self.n)
            kx, ok = E2.interaction_bound(G)
            assert ok, "interaction bound failed on a base face"
        self.Kx = kx
        tg = np.ascontiguousarray([g for g, _ in self.tokens], dtype=np.int32)
        tw = np.ascontiguousarray([w for _, w in self.tokens], dtype=np.int32)
        self.L = D2.ext2_lib()
        self.h = self.L.ext2_new(self.n, len(self.tokens), _ptr(tg), _ptr(tw), self.Kx)
        if not self.h:
            raise ValueError("ext2_new failed (bad word or n > 30)")
        self.T0 = self.L.ext2_T0(self.h)
        self._d1 = None
        self._pyB = None

    def __del__(self):
        try:
            self.L.ext2_free(self.h)
        except Exception:
            pass

    @property
    def dp1(self):
        """Dp1 (same graph, same state numbering) for converting C paths to x-sequences."""
        if self._d1 is None:
            self._d1 = D2.Dp1(self.tokens, self.n)
        return self._d1

    def pair(self, r1, r2, target=None, warm=True):
        """(T, witness): T = exact max over placements at ranks (r1, r2) (max mode) or the value of the first
        placement with T >= target found (target mode); (None, None) when there is none.  witness = (k, states)."""
        out = np.zeros(80, dtype=np.int32)
        T = self.L.ext2_pair(self.h, r1, r2, -1 if target is None else target, int(warm), _ptr(out))
        if T == -2:
            raise RuntimeError("ext2_pair: internal error (extension graph build failed)")
        if T < 0:
            return None, None
        return T, (int(out[0]), [int(x) for x in out[2:2 + out[1]]])

    def stats(self):
        s = np.zeros(3, dtype=np.int64)
        self.L.ext2_stats(self.h, _ptr(s))
        return {"evals": int(s[0]), "pruned2": int(s[1]), "nodes": int(s[2])}

    def witness_rows(self, r1, r2, best):
        """Event rows of the (n0+2)-line arrangement of a witness (for an independent recount)."""
        if self._pyB is None:
            self._pyB = E2.Base(tokens=self.tokens, n=self.n)
        k, states = best
        return E2.witness_rows(self._pyB, r1, r2, (k, self.dp1._xs(states)))


def cmd_max2(args):
    words = E2.load_words(args.input)[:args.limit]
    out = open(args.out, "w") if args.out else None
    for name, gens in words:
        t0 = time.time()
        B = FastBase(gens, complete=args.complete)
        n0 = B.n
        pairs = list(combinations(range(n0 + 2), 2))
        if args.ranks:
            pairs = [tuple(int(x) for x in args.ranks.split(","))]
        overall = None
        for r1, r2 in pairs:
            t1 = time.time()
            T, best = B.pair(r1, r2, target=args.target)
            if args.verify and best is not None:
                got = X.count_triangles(B.witness_rows(r1, r2, best))
                assert got == T, (name, r1, r2, T, got)
            rec = {"name": name, "n0": n0, "T0": B.T0, "r1": r1, "r2": r2, "max": T,
                   "secs": round(time.time() - t1, 3)}
            if args.target is not None:
                rec["target"] = args.target
                rec["reached"] = T is not None
            if out:
                out.write(json.dumps(rec) + "\n")
                out.flush()
            if args.verbose:
                print(f"{name} ranks=({r1},{r2}) max={T} ({rec['secs']}s)", flush=True)
            if T is not None and (overall is None or T > overall):
                overall = T
        what = f">= {args.target}" if args.target is not None else "max"
        st = B.stats()
        print(f"{name}: n0={n0} T0={B.T0} Kx={B.Kx} pairs={len(pairs)} overall {what}: "
              f"{overall if overall is not None else 'none (all placements below target)'}  "
              f"[{time.time() - t0:.1f}s, exact partner evals {st['evals']}, pruned 0+{st['pruned2']}]", flush=True)
    if out:
        out.close()


def selftest():
    """Compare with extend2_dp on small gallery bases (all rank pairs, max mode and target mode)."""
    import glob
    bad = 0
    for n0, nb in ((6, 2), (8, 2)):
        fs = sorted(glob.glob(str(ROOT / f"tools/external/kobon-solutions/gallery/data/{n0}/*.json")))[:nb]
        for f in fs:
            gens = json.load(open(f))["gens"]
            P = E2.Base(gens)
            F = FastBase(gens, kx=P.Kx)
            for r1, r2 in combinations(range(n0 + 2), 2):
                a, _ = E2.pair_search(P, r1, r2)
                b, w = F.pair(r1, r2)
                ok = a == b
                if b is not None:
                    ok = ok and X.count_triangles(F.witness_rows(r1, r2, w)) == b
                for t in ((a or 0) + 1, a or 0):
                    ok = ok and ((E2.pair_search(P, r1, r2, target=t)[0] is not None) == (F.pair(r1, r2, target=t)[0] is not None))
                bad += not ok
                if not ok:
                    print("MISMATCH", f, r1, r2, a, b)
    print("selftest:", "FAILED %d" % bad if bad else "ok (extend2_fast == extend2_dp)")
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("max2", help="exact two-line extension maximum per rank pair")
    m.add_argument("input")
    m.add_argument("--ranks", help="r1,r2 (final slope ranks 0..n0+1, r1 < r2); default all pairs")
    m.add_argument("--target", type=int, help="only decide whether some placement reaches T (faster)")
    m.add_argument("--limit", type=int, default=10 ** 9, help="use only the first K words of INPUT")
    m.add_argument("--complete", action="store_true",
                   help="append the far crossings of parallel base pairs first (needed for SAT equivalence when the "
                        "base has parallel pairs; no-op otherwise)")
    m.add_argument("--verify", action="store_true", help="recount every witness triangle-by-triangle")
    m.add_argument("--verbose", action="store_true", help="print every rank pair")
    m.add_argument("--out", help="write one JSON line per rank pair")
    sub.add_parser("selftest")
    args = ap.parse_args()
    if args.cmd == "selftest":
        sys.exit(1 if selftest() else 0)
    cmd_max2(args)


if __name__ == "__main__":
    main()

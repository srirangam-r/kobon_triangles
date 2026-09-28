"""Exact structure extractor for the A-stream claims (stdlib only).

For an arrangement of exact integer lines a*x+b*y+c=0 it computes
  - the bounded triangular faces (independent re-implementation, used only to test
    claims about the proof framework -- never to score a submission),
  - Z (unused bounded segments), D (segments used by two triangles),
  - for every multiple point: the cyclic order of its 6 rays, the blocks (doubly used
    first segment with a simple far end, plus its cap line) and the bridges (doubly
    used first segment whose far end is multiple).

Then it checks the A-stream claims:
  A01  every bridge joins two multiple points consecutive on their common line, so a
       line with j multiple points carries at most j-1 bridges and beta <= sigma;
       distinct bridges meet only at shared endpoints (plane bridge graph).
  A02  a bridge on an outer ray of a block has its far (multiple) end on that block's
       cap line, so the pair (P, cap) is counted in x.
plus the framework identity D = sum_P (b(P) + e(P)/2) and the c-count of C34.

    python3 work/t3/a_struct.py --selftest
    python3 work/t3/a_struct.py submission/solution.json ...
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction
from itertools import combinations
from math import gcd
from pathlib import Path


def norm(line):
    a, b, c = (int(v) for v in line)
    g = gcd(gcd(abs(a), abs(b)), abs(c)) or 1
    a, b, c = a // g, b // g, c // g
    for v in (a, b, c):
        if v:
            if v < 0:
                a, b, c = -a, -b, -c
            break
    return a, b, c


def inter(l1, l2):
    (a1, b1, c1), (a2, b2, c2) = l1, l2
    det = a1 * b2 - a2 * b1
    if det == 0:
        return None
    return (Fraction(b1 * c2 - b2 * c1, det), Fraction(a2 * c1 - a1 * c2, det))


def side(line, p):
    a, b, c = line
    return a * p[0] + b * p[1] + c


def cmp_dir(u, v):
    """Angular comparison of two direction vectors (counter-clockwise from +x)."""
    def half(d):
        return 0 if (d[1] > 0 or (d[1] == 0 and d[0] > 0)) else 1
    hu, hv = half(u), half(v)
    if hu != hv:
        return -1 if hu < hv else 1
    cr = u[0] * v[1] - u[1] * v[0]
    return 0 if cr == 0 else (-1 if cr > 0 else 1)


class Arrangement:
    def __init__(self, lines):
        self.lines = [norm(l) for l in lines]
        n = self.n = len(self.lines)
        assert len(set(self.lines)) == n, "duplicate lines"
        pts = {}
        for i, j in combinations(range(n), 2):
            p = inter(self.lines[i], self.lines[j])
            if p is None:
                continue
            pts.setdefault(p, set()).update((i, j))
        self.pts = pts
        self.mult = {p: s for p, s in pts.items() if len(s) >= 3}
        # vertices along each line, in order
        self.order = []
        for i, line in enumerate(self.lines):
            key = 0 if line[1] else 1
            on = [p for p, s in pts.items() if i in s]
            self.order.append(sorted(on, key=lambda p: p[key] if line[1] else p[key]))
        self.pos = [{p: k for k, p in enumerate(o)} for o in self.order]
        self.tris = self._triangles()
        self.use = {}
        for i in range(n):
            for k in range(max(0, len(self.order[i]) - 1)):
                self.use[(i, k)] = 0
        for tri in self.tris:
            for a, b, c in ((tri[0], tri[1], tri[2]), (tri[1], tri[0], tri[2]), (tri[2], tri[0], tri[1])):
                p, q = inter(self.lines[a], self.lines[b]), inter(self.lines[a], self.lines[c])
                ra, rb = self.pos[a][p], self.pos[a][q]
                assert abs(ra - rb) == 1, "triangle side is not a single segment"
                self.use[(a, min(ra, rb))] += 1
        self.Z = sum(1 for v in self.use.values() if v == 0)
        self.D = sum(1 for v in self.use.values() if v == 2)
        self.t = len(self.mult)

    def _triangles(self):
        out = []
        for i, j, k in combinations(range(self.n), 3):
            ps = [inter(self.lines[i], self.lines[j]), inter(self.lines[i], self.lines[k]),
                  inter(self.lines[j], self.lines[k])]
            if any(p is None for p in ps) or len(set(ps)) < 3:
                continue
            ok = True
            for m in range(self.n):
                if m in (i, j, k):
                    continue
                s = [side(self.lines[m], p) for p in ps]
                if min(s) < 0 < max(s):
                    ok = False
                    break
            if ok:
                out.append((i, j, k))
        return out

    def rays(self, P):
        """Cyclically ordered rays at P: list of (line, far vertex or None, segment key)."""
        out = []
        for i in sorted(self.mult[P] if P in self.mult else self.pts[P]):
            k = self.pos[i][P]
            for nb in (k - 1, k + 1):
                if 0 <= nb < len(self.order[i]):
                    V = self.order[i][nb]
                    seg = (i, min(k, nb))
                else:
                    V, seg = None, None
                d = self.lines[i][1], -self.lines[i][0]
                if V is not None:
                    d = (V[0] - P[0], V[1] - P[1])
                elif nb < 0:
                    d = (-d[0], -d[1])
                out.append({"line": i, "far": V, "seg": seg, "dir": d})
        import functools
        out.sort(key=functools.cmp_to_key(lambda u, v: cmp_dir(u["dir"], v["dir"])))
        return out

    def point_data(self, P):
        rs = self.rays(P)
        k = len(rs)
        for idx, r in enumerate(rs):
            r["dbl"] = r["seg"] is not None and self.use[r["seg"]] == 2
            r["bridge"] = bool(r["dbl"] and r["far"] in self.mult)
            r["middle"] = bool(r["dbl"] and not r["bridge"])
            r["cap"] = None
            if r["middle"]:
                other = [m for m in sorted(self.pts[r["far"]]) if m != r["line"]]
                r["cap"] = other[0] if len(other) == 1 else None
        b = sum(1 for r in rs if r["middle"])
        e = sum(1 for r in rs if r["bridge"])
        return {"rays": rs, "b": b, "e": e, "c": Fraction(b) + Fraction(e, 2) - 2, "k": k // 2}

    def report(self):
        data = {P: self.point_data(P) for P in self.mult}
        B = sum(d["b"] for d in data.values())
        E = sum(d["e"] for d in data.values())
        j = [sum(1 for P in self.mult if i in self.pts[P]) for i in range(self.n)]
        m = sum(1 for x in j if x)
        sigma = sum(x - 1 for x in j if x >= 1)
        bridges = set()
        for P, d in data.items():
            for r in d["rays"]:
                if r["bridge"]:
                    bridges.add(r["seg"])
        return {"n": self.n, "T": len(self.tris), "t": self.t, "Z": self.Z, "D": self.D,
                "B": B, "e_total": E, "beta": len(bridges), "m": m, "sigma": sigma,
                "sum_c": sum(d["c"] for d in data.values()),
                "types": sorted((d["b"], d["e"], d["k"]) for d in data.values()),
                "data": data, "bridges": bridges, "j": j}


def check(lines, label="", tally=None):
    A = Arrangement(lines)
    R = A.report()
    fails = []
    # framework identity D = sum (b + e/2)
    if R["D"] != R["B"] + R["beta"]:
        fails.append(f"D={R['D']} != B+beta={R['B']}+{R['beta']}")
    if R["sum_c"] != R["D"] - 2 * R["t"]:
        fails.append("sum_c mismatch")
    # A01: per-line bridge count and beta <= sigma
    per_line = {}
    for (i, k) in R["bridges"]:
        per_line[i] = per_line.get(i, 0) + 1
    for i, cnt in per_line.items():
        if cnt > max(R["j"][i] - 1, 0):
            fails.append(f"A01 line {i}: {cnt} bridges but j={R['j'][i]}")
    if R["beta"] > R["sigma"]:
        fails.append(f"A01 beta={R['beta']} > sigma={R['sigma']}")
    # A01 planarity: two bridges meet only at a shared endpoint
    segs = []
    for (i, k) in R["bridges"]:
        segs.append((i, A.order[i][k], A.order[i][k + 1]))
    for (i, p1, q1), (jj, p2, q2) in combinations(segs, 2):
        if i == jj:
            continue
        X = inter(A.lines[i], A.lines[jj])
        if X is None:
            continue
        if X not in (p1, q1) and X not in (p2, q2):
            def between(X, p, q):
                return min(p[0], q[0]) < X[0] < max(p[0], q[0]) or (
                    p[0] == q[0] and min(p[1], q[1]) < X[1] < max(p[1], q[1]))
            if between(X, p1, q1) and between(X, p2, q2):
                fails.append("A01 two bridges cross")
    # A02: bridge on an outer ray of a block -> far end on that block's cap line
    a02 = 0
    unpaid = 0
    for P, d in R["data"].items():
        rs, k = d["rays"], len(d["rays"])
        for idx, r in enumerate(rs):
            if not r["bridge"]:
                continue
            adj = [rs[(idx - 1) % k], rs[(idx + 1) % k]]
            if not any(s["middle"] for s in adj):
                unpaid += 1
                if d["b"] >= 2 and d["k"] == 3:
                    # at a triple point with two blocks only a bent back ray can be unpaid
                    mids = [i for i, s in enumerate(rs) if s["middle"]]
                    if len(mids) == 2 and (mids[1] - mids[0]) % k == 3:
                        fails.append(f"A03 unpaid bridge at an axis point {P}")
            for s in adj:
                if not s["middle"] or s["cap"] is None:
                    continue
                a02 += 1
                if side(A.lines[s["cap"]], r["far"]) != 0:
                    fails.append(f"A02 bridge far end not on cap line at {P}")
                if r["far"] not in A.mult:
                    fails.append("A02 far end not multiple")
    if tally is not None:
        tally["a02"] = tally.get("a02", 0) + a02
        tally["unpaid_ends"] = tally.get("unpaid_ends", 0) + unpaid
        tally["bridges"] = tally.get("bridges", 0) + R["beta"]
    print(f"{label} n={R['n']} T={R['T']} t={R['t']} Z={R['Z']} D={R['D']} B={R['B']} "
          f"beta={R['beta']} m={R['m']} sigma={R['sigma']} sum_c={R['sum_c']} "
          f"types(b,e,k)={R['types']} A02_instances={a02} unpaid_ends={unpaid} "
          f"{'OK' if not fails else 'FAIL ' + '; '.join(fails)}")
    return fails


# bent point with four doubly used bridge rays (verdicts/C07.md explicit example)
BENT_E4 = [(0, 1, 0), (6, -1, -72), (1, -7, 70), (1, 0, 0),
           (5, -6, 0), (7, -8, -2), (5, 6, -60)]
FAR = [(1, 37, -100000), (2, -41, -120000), (13, 5, 90000), (1, -3, -70000)]


def random_arrangement(n, rng):
    """Random exact arrangement with several multiple points: random lines plus lines
    through pairs of existing crossings (each such line creates triple points)."""
    lines = []
    while len(lines) < n - n // 3:
        a, b, c = rng.randint(-9, 9), rng.randint(-9, 9), rng.randint(-40, 40)
        if (a or b) and norm((a, b, c)) not in [norm(l) for l in lines]:
            lines.append(norm((a, b, c)))
    tries = 0
    while len(lines) < n and tries < 200:
        tries += 1
        pts = [p for p in (inter(l1, l2) for l1, l2 in combinations(lines, 2)) if p]
        if len(pts) < 2:
            break
        p, q = rng.sample(pts, 2)
        if p == q:
            continue
        dx, dy = q[0] - p[0], q[1] - p[1]
        a, b = dy, -dx
        c = -(a * p[0] + b * p[1])
        den = 1
        for v in (a, b, c):
            den = den * Fraction(v).denominator // gcd(den, Fraction(v).denominator)
        cand = norm((int(a * den), int(b * den), int(c * den)))
        if cand[0] == 0 and cand[1] == 0:
            continue
        if cand not in lines:
            lines.append(cand)
    return lines


def selftest():
    import random
    bad = []
    rng = random.Random(20260928)
    stats = {"with_bridges": 0, "t_ge_7": 0, "a02": 0, "arrangements": 0}
    for trial in range(int(sys.argv[2]) if len(sys.argv) > 2 else 60):
        lines = random_arrangement(rng.choice([8, 9, 10, 11]), rng)
        if len(set(lines)) < 8:
            continue
        A = Arrangement(lines)
        R = A.report()
        stats["arrangements"] += 1
        stats["with_bridges"] += R["beta"] > 0
        stats["t_ge_7"] += R["t"] >= 7
        bad += check(lines, f"random#{trial}", stats)
    print("random stats", stats)

    bad += check(BENT_E4, "bent-e4(7 lines)", stats)
    bad += check(BENT_E4 + FAR, "bent-e4+4 far lines", stats)
    for p in sorted(Path("submissions").glob("*/solution.json")) + [Path("submission/solution.json")]:
        lines = json.loads(p.read_text())["lines"]
        if len(lines) > 18:
            continue
        bad += check(lines, str(p), stats)
    print("SELFTEST", "PASS" if not bad else f"FAIL ({len(bad)})")
    return 1 if bad else 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "--selftest":
        sys.exit(selftest())
    for p in args:
        check(json.loads(Path(p).read_text())["lines"], p)

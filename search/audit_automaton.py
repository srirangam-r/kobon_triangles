#!/usr/bin/env python
"""Independent adversarial audit of search/line_automaton.py (task A20).  Does not modify any existing file.

    python search/audit_automaton.py enum N [--out f]        all arrangements of N lines (points of multiplicity <= 3):
                                                             closure of flip / collapse / expand from the bubble-sort word
    python search/audit_automaton.py walk N SEED STEPS       random walks (flip/collapse/expand) from the bubble-sort word
    python search/audit_automaton.py geo ...                 independent geometric oracle (straight lines, exact rationals)
    python search/audit_automaton.py dp                      independent min-plus DP + certificate check

Per arrangement and line it checks: (1) line_automaton.check_line (frames enumerated, edges allowed, ends compatible,
hidden assignment in the domain, exact window sum == reference, parity); (2) the real line is a path of the *graph on
which Bellman-Ford runs* (start node, every edge, terminal), with window weights <= real; (3) M1 and M2 stated directly
with the reference functions.
"""
import collections
import itertools
import json
import random
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.append(str(ROOT / "work/t3"))
import inspect  # noqa: E402,F401  (stdlib first)
import line_automaton as LA  # noqa: E402

LA._imports()
from arr import Arr  # noqa: E402
from bbl_rules import Charge  # noqa: E402
from bbl_hall import values  # noqa: E402
from bbl_adversary import portions  # noqa: E402
import mutate  # noqa: E402


# ----------------------------------------------------------------------------------------------- arrangement sources
def bubble_word(n):
    return " ".join(str(j) for i in range(n - 1, 0, -1) for j in range(i))


def canon(a):
    return mutate.sweep(mutate.local_sequences(a), a.n)


def neighbours(a):
    """flip / collapse of every triangle with 3 simple vertices, expand of every triple point (both orientations)"""
    out = []
    for f in a.tris:
        if any(len(a.events[v]) != 2 for v in mutate.tri_vertices(a, f)):
            continue
        for op in (mutate.flip, mutate.collapse):
            w = op(a, f)
            if w is not None:
                out.append(w)
    for P in a.triples:
        for o in (0, 1):
            w = mutate.expand(a, P, o)
            if w is not None:
                out.append(w)
    return out


def enum_all(n, limit=10 ** 9):
    start = canon(Arr(bubble_word(n), n))
    seen = {start}
    stack = [start]
    while stack:
        w = stack.pop()
        yield w
        if len(seen) >= limit:
            continue
        a = Arr(w, n)
        for w2 in neighbours(a):
            if w2 not in seen and not any(len(e) > 3 for e in Arr(w2, n).events):
                seen.add(w2)
                stack.append(w2)


# ----------------------------------------------------------------------------------------------- the checks
class GraphIndex:
    """the graph exactly as line_automaton builds it for a given objective, indexed for path-membership queries"""

    def __init__(self, obj):
        g = LA.Graph()
        self.nodes, self.starts, self.edges, self.terms = g.objective_weights(obj)
        self.obj = obj
        self.node_id = {x: i for i, x in enumerate(self.nodes)}
        self.start_set = set(self.starts)
        self.emap = {}
        for (a, b, w) in self.edges:
            self.emap.setdefault((a, b), set()).add(w)
        self.tmap = {}
        for (u, w, fl, pr, cq) in self.terms:
            self.tmap.setdefault(u, set()).add(w)

    def path_weight(self, frames):
        """None if frames is not a path of the graph, else the total weight (sum of edge weights + terminal weight)"""
        m = len(frames)
        if m < 2:
            return None
        nodes = []
        par = 1 if frames[0].kind == "S" else 0
        cls = frames[0].ub
        for i, f in enumerate(frames):
            if i > 0:
                par = (par + (f.kind == "S")) % 2
            prev = frames[i - 1].info_prev(i - 1 == 0) if i > 0 else None
            nodes.append((prev, f, par, cls, 0, 1 if i == m - 1 else 0, 0))
        tot = 0
        ids = []
        for x in nodes:
            if x not in self.node_id:
                return "node missing %s" % (x,)
            ids.append(self.node_id[x])
        if ids[0] not in self.start_set:
            return "not a start"
        for i in range(m - 1):
            ws = self.emap.get((ids[i], ids[i + 1]))
            if not ws:
                return "edge missing at %d" % i
            prev = nodes[i][0]
            ni = frames[i + 1].info_next(i + 1 == m - 1)
            w = LA.options(prev, frames[i], ni)
            wm = min(sum(c * x for c, x in zip(self.obj, v)) for v in w)
            if wm not in ws:
                return "edge weight differs"
            tot += wm
        ts = self.tmap.get(ids[-1])
        if not ts:
            return "terminal missing"
        prev = nodes[-1][0]
        wm = min(sum(c * x for c, x in zip(self.obj, v)) for v in LA.options(prev, frames[-1], None))
        if wm not in ts:
            return "terminal weight differs"
        return tot + wm


def check_arrangement(w, n, gi_list, stats, verbose=True):
    """returns list of error strings for the arrangement with word w"""
    errs = []
    try:
        ch = Charge(Arr(w, n))
    except ValueError:
        stats["fourfold"] += 1
        return errs
    a = ch.a
    if any(sum(len(a.events[e]) - 1 for e in a.rows[L]) != a.n - 1 for L in range(a.n)):
        stats["incomplete"] += 1
        return errs
    val, served = values(ch)
    rec = portions(ch)
    stats["arr"] += 1
    stats["arr_n%d" % n] += 1
    for L in range(n):
        stats["lines"] += 1
        try:
            e = LA.check_line(ch, L, val, served, rec)
        except Exception as ex:                                    # extraction asserts count as failures
            e = ["EXC %r" % (ex,)]
        frames, hids = LA.extract(ch, L) if not e else (None, None)
        ref = LA.reference(ch, L, val, served, rec)
        p, v2, nRN, nRR, nT = ref
        vL = Fr(v2, 2) - 1
        comp = vL + Fr(nRN, 2) + Fr(3 * nRR, 2)
        stats["minM2"] = min(stats.get("minM2", 99), comp)
        stats["minV"] = min(stats.get("minV", 99), vL)
        if comp < -1:
            e.append("M2 violated: v_L + comp = %s" % comp)
        # M1: clean line of an even arrangement
        if not ch.onl[L] and not any(b[5] == L for b in ch.blk):
            stats["clean"] += 1
            if n % 2 == 0 and n >= 4 and p < 1:
                e.append("M1 violated: clean line without portion")
            if n % 2 == 1:
                stats["clean_odd_p0"] += (p == 0)
        if frames is not None:
            fr = LA.normalise(frames)
            if COVER_ON and len(fr) >= 2:
                record_cover(frames, hids, "n=%d word=%s L=%d" % (n, w, L))
            for gi in gi_list:
                pw = gi.path_weight(fr)
                if pw is None:                                  # lines with a single vertex (n <= 3) are not paths
                    stats["single_vertex_line"] += 1
                    continue
                if isinstance(pw, str):
                    e.append("not a graph path (%s): %s" % (pw, gi.obj))
                    continue
                real = sum(c * x for c, x in zip(gi.obj, ref))
                if pw > real:
                    e.append("path weight %d > real %d for %s" % (pw, real, gi.obj))
        if e:
            errs.append((L, e))
            if verbose and stats["bad_lines"] < 20:
                print("ERROR n=%d L=%d word=%s\n   %s" % (n, L, w, e[:3]), flush=True)
            stats["bad_lines"] += 1
    return errs


def cmd_enum(args):
    n = int(args[0])
    limit = int(args[1]) if len(args) > 1 else 10 ** 9
    gi_list = [GraphIndex((0, 1, 1, 3, 0)), GraphIndex((1, 0, 0, 0, 0)), GraphIndex((0, 1, 0, 0, 0))]
    stats = collections.Counter()
    t0 = time.time()
    trip_hist = collections.Counter()
    for k, w in enumerate(enum_all(n, limit)):
        check_arrangement(w, n, gi_list, stats)
        trip_hist[Arr(w, n).triples.__len__()] += 1
        if k % 5000 == 0:
            print("  ...", k, dict(stats), "%.0fs" % (time.time() - t0), flush=True)
    print("n=%d arrangements checked %d, lines %d, bad lines %d, min(v+comp)=%s min v=%s time %.0fs" % (
        n, stats["arr"], stats["lines"], stats["bad_lines"], stats.get("minM2"), stats.get("minV"), time.time() - t0))
    print("clean lines", stats["clean"], "odd-n clean lines with p=0:", stats["clean_odd_p0"])
    print("by number of triple points:", dict(sorted(trip_hist.items())))


def cmd_walk(args):
    n, seed, steps = int(args[0]), int(args[1]), int(args[2])
    p_expand = float(args[3]) if len(args) > 3 else 0.2
    p_collapse = float(args[4]) if len(args) > 4 else 0.4
    gi_list = [GraphIndex((0, 1, 1, 3, 0)), GraphIndex((1, 0, 0, 0, 0)), GraphIndex((0, 1, 0, 0, 0))]
    rng = random.Random(seed)
    a = Arr(bubble_word(n), n)
    stats = collections.Counter()
    trip_hist = collections.Counter()
    t0 = time.time()
    seen = set()
    for it in range(steps):
        w = mutate.random_move(a, rng, p_collapse=p_collapse, p_expand=p_expand)
        if w is None:
            continue
        b = Arr(w, n)
        if any(len(e) > 3 for e in b.events):
            continue
        a = b
        if w in seen:
            continue
        seen.add(w)
        trip_hist[len(a.triples)] += 1
        check_arrangement(w, n, gi_list, stats)
    print("walk n=%d seed=%d: distinct arrangements %d, lines %d, bad lines %d, min(v+comp)=%s min v=%s (%.0fs)" % (
        n, seed, stats["arr"], stats["lines"], stats["bad_lines"], stats.get("minM2"), stats.get("minV"), time.time() - t0))
    print("  triple-point histogram:", dict(sorted(trip_hist.items())))



# ----------------------------------------------------------------------------------------------- geometric oracle
# Straight lines with exact rational arithmetic.  Everything below (triangles, ray statuses, blocks, T1, F, portions,
# v_L, frames, hidden variables) is computed from the coordinates and the definitions in search/bbl_hall.py's
# docstring, WITHOUT Arr / Charge / extract.  Arr is only used afterwards to compare the reference.
import functools  # noqa: E402
from math import gcd  # noqa: E402


class Geo:
    def __init__(self, lines):
        """lines: list of (s, c), y = s x + c, pairwise distinct slopes.  Labels are re-sorted by slope (top to bottom at -inf)."""
        self.lines = sorted(lines)
        n = self.n = len(lines)
        pts = {}
        for i in range(n):
            for j in range(i + 1, n):
                s1, c1 = self.lines[i]
                s2, c2 = self.lines[j]
                x = (c2 - c1) / (s1 - s2)
                pts.setdefault((x, s1 * x + c1), set()).update((i, j))
        self.at = {p: frozenset(v) for p, v in pts.items()}
        self.four = any(len(v) > 3 for v in self.at.values())
        self.row = [sorted(p for p, v in self.at.items() if i in v) for i in range(n)]
        self.pos = [{p: k for k, p in enumerate(r)} for r in self.row]
        self.triples = [p for p, v in self.at.items() if len(v) == 3]
        self._tri()

    # -- triangles by the three-line criterion
    def _pt(self, i, j):
        s1, c1 = self.lines[i]
        s2, c2 = self.lines[j]
        x = (c2 - c1) / (s1 - s2)
        return (x, s1 * x + c1)

    def _side(self, i, p):
        s, c = self.lines[i]
        return 1 if p[1] > s * p[0] + c else -1

    def _tri(self):
        n = self.n
        self.tb = [[0] * max(len(r) - 1, 0) for r in self.row]      # triangle above segment e of line i
        self.bb = [[0] * max(len(r) - 1, 0) for r in self.row]
        self.ntri = 0
        for i, j, k in itertools.combinations(range(n), 3):
            A, B, C = self._pt(i, j), self._pt(i, k), self._pt(j, k)
            if len({A, B, C}) < 3:
                continue
            if abs(self.pos[i][A] - self.pos[i][B]) == 1 and abs(self.pos[j][A] - self.pos[j][C]) == 1 \
                    and abs(self.pos[k][B] - self.pos[k][C]) == 1:
                self.ntri += 1
                for (l, P, Q, R) in ((i, A, B, C), (j, A, C, B), (k, B, C, A)):
                    e = min(self.pos[l][P], self.pos[l][Q])
                    (self.tb if self._side(l, R) == 1 else self.bb)[l][e] += 1

    def bits(self, i, e):
        if e < 0 or e >= len(self.row[i]) - 1:
            return (0, 0)
        assert self.tb[i][e] <= 1 and self.bb[i][e] <= 1
        return (self.tb[i][e], self.bb[i][e])

    # -- rays at a multiple point, ccw
    def rays(self, P):
        L = sorted(self.at[P])
        rs = [(l, +1) for l in L] + [(l, -1) for l in L]

        def d(r):
            s = self.lines[r[0]][0]
            return (r[1], r[1] * s)

        def half(v):
            return 0 if (v[1] > 0 or (v[1] == 0 and v[0] > 0)) else 1

        def cmp(r1, r2):
            v1, v2 = d(r1), d(r2)
            h1, h2 = half(v1), half(v2)
            if h1 != h2:
                return h1 - h2
            cr = v1[0] * v2[1] - v1[1] * v2[0]
            return -1 if cr > 0 else 1 if cr < 0 else 0
        return sorted(rs, key=functools.cmp_to_key(cmp))

    def far(self, P, ray):
        l, d = ray
        i = self.pos[l][P] + d
        return self.row[l][i] if 0 <= i < len(self.row[l]) else None

    def first_bits(self, P, ray):
        """bits of the first segment of the ray, None if there is none"""
        l, d = ray
        i = self.pos[l][P]
        e = i if d == 1 else i - 1
        if e < 0 or e >= len(self.row[l]) - 1:
            return None
        return self.bits(l, e)

    def status(self, P, ray):
        b = self.first_bits(P, ray)
        if b is None or b != (1, 1):
            return "N"
        return "B" if len(self.at[self.far(P, ray)]) == 2 else "R"

    def sector(self, P, rs, k):
        """is the sector between rays k and k+1 (ccw) at P a triangle"""
        r1, r2 = rs[k % 6], rs[(k + 1) % 6]
        Q1, Q2 = self.far(P, r1), self.far(P, r2)
        if Q1 is None or Q2 is None:
            return 0
        common = (self.at[Q1] & self.at[Q2]) - {r1[0], r2[0]}
        if not common:
            return 0
        (C,) = common
        return int(abs(self.pos[C][Q1] - self.pos[C][Q2]) == 1)

    def wiring_word(self):
        n = self.n
        order = list(range(n))
        toks = []
        for p in sorted(self.at):
            S = sorted(self.at[p])
            g = order.index(S[0])
            w = len(S)
            assert order[g:g + w] == S, "block not contiguous"
            toks.append(str(g) + "*" * (w - 2))
            order[g:g + w] = order[g:g + w][::-1]
        return " ".join(toks)

    # -- the definitions of bbl_hall.py, transcribed from its docstring
    def oracle(self):
        """returns dict with p[L], v[L] (Fractions), nRN[L], nRR[L], nT[L]; also stores blocks / served"""
        n = self.n
        H = Fr(3, 2)
        p = [0] * n
        unused = []
        for i in range(n):
            for e in range(len(self.row[i]) - 1):
                if self.bits(i, e) == (0, 0):
                    unused.append((i, e))
                    p[i] += 1
        for (i, e) in unused:
            for X in (self.row[i][e], self.row[i][e + 1]):
                if len(self.at[X]) == 2:
                    (o,) = self.at[X] - {i}
                    p[o] += 1
        v = {L: Fr(p[L]) - 1 for L in range(n)}
        RS, ST = {}, {}
        for P in self.triples:
            RS[P] = self.rays(P)
            ST[P] = [self.status(P, r) for r in RS[P]]
            for k, r in enumerate(RS[P]):
                v[r[0]] += H if ST[P][k] == "N" else -H if ST[P][k] == "B" else 0
        blocks = []
        for P in self.triples:
            for k, r in enumerate(RS[P]):
                if ST[P][k] == "B":
                    X = self.far(P, r)
                    (C,) = self.at[X] - {r[0]}
                    blocks.append((P, k, r[0], X, C))
        served = {}
        for b in blocks:
            P, k, l, X, C = b
            F1, F2 = self.far(P, RS[P][(k - 1) % 6]), self.far(P, RS[P][(k + 1) % 6])
            got = Fr(0)
            if F1 is not None and F2 is not None and len(self.at[F1]) == 3 and len(self.at[F2]) == 3:
                for Q in (F1, F2):
                    d = 1 if X[0] > Q[0] else -1
                    kk = RS[Q].index((C, d))
                    if ST[Q][kk] == "N":
                        got += H
            v[C] -= got
            v[l] += got
            served[b] = got > 0
        for b in blocks:
            if served[b]:
                continue
            P, k, l, X, C = b
            for f in ((k - 1) % 6, (k + 1) % 6):
                if ST[P][f] == "N":
                    v[RS[P][f][0]] -= 1
                    v[l] += 1
        nRN, nRR = [0] * n, [0] * n
        for b in blocks:
            P, k, l, X, C = b
            if served[b]:
                continue
            nR = sum(1 for f in ((k - 1) % 6, (k + 1) % 6) if ST[P][f] == "R")
            nRR[l] += nR == 2
            nRN[l] += nR == 1
        nT = [sum(1 for V in self.row[L] if len(self.at[V]) == 3) for L in range(n)]
        self.RS, self.ST, self.blocks, self.served = RS, ST, blocks, served
        return dict(p=p, v=v, nRN=nRN, nRR=nRR, nT=nT)

    # -- frames of line L
    def frames(self, L):
        """returns frames, hids for line L (oriented by increasing x, + = above), from the coordinates only"""
        row = self.row[L]
        sL = self.lines[L][0]
        frames, hids = [], []
        for i, V in enumerate(row):
            bi, bo = self.bits(L, i - 1), self.bits(L, i)
            if len(self.at[V]) == 2:
                (W,) = self.at[V] - {L}
                up = 1 if self.lines[W][0] > sL else -1
                ub = (int(self.far(V, (W, up)) is None), int(self.far(V, (W, -up)) is None))
                frames.append(LA.Frame("S", bi, bo, ub, LA.NONE))
                hids.append(None)
                continue
            rs = self.rays(V)
            j = rs.index((L, 1))
            ring = rs[j:] + rs[:j]                 # E, E+, W+, W, W-, E-
            assert ring[3] == (L, -1)
            E, Ep, Wp, W_, Wm, Em = ring
            hp, hm = self.sector(V, ring, 1), self.sector(V, ring, 4)
            assert self.sector(V, ring, 0) == bo[0] and self.sector(V, ring, 5) == bo[1]
            assert self.sector(V, ring, 2) == bi[0] and self.sector(V, ring, 3) == bi[1]
            sig, ub = [], [0, 0]
            for name, r in (("E+", Ep), ("E-", Em), ("W+", Wp), ("W-", Wm)):
                f = self.far(V, r)
                if f is None:
                    ub[0 if name[1] == "+" else 1] = 1
                sig.append(int(f is not None and len(self.at[f]) == 3))
            g = [0, 0, 0, 0]
            names = ("E+", "E-", "W+", "W-")
            rmap = {"E+": Ep, "E-": Em, "W+": Wp, "W-": Wm}
            for R, Ro in (("E+", "W+"), ("E-", "W-"), ("W+", "E+"), ("W-", "E-")):
                r = rmap[R]
                if self.status(V, r) == "B":
                    X = self.far(V, r)
                    (C,) = self.at[X] - {r[0]}
                    Q = self.far(V, rmap[Ro])
                    if Q is not None and len(self.at[Q]) == 3:
                        d = 1 if X[0] > Q[0] else -1
                        kk = self.RS[Q].index((C, d))
                        g[names.index(Ro)] = int(self.ST[Q][kk] == "N")
            frames.append(LA.Frame("T", bi, bo, tuple(ub), (hp, hm)))
            hids.append((tuple(sig), tuple(g)))
        return frames, hids


def random_lines(rng, n, mode):
    """returns list of (s, c) or None.  Lines through random pairs of a pool of grid points, then a random projective
    map (an invertible linear map of the dual) makes them pairwise non-parallel and non-vertical; concurrency is preserved."""
    if mode == "grid":
        cands = [(a, b, c) for a in range(-2, 3) for b in range(-2, 3) for c in range(-2, 3) if (a, b) != (0, 0)]
        cands = [t for t in cands if gcd(gcd(abs(t[0]), abs(t[1])), abs(t[2])) == 1 and t > (0, 0, 0)]
        rng.shuffle(cands)
        lines = cands[:n]
    else:
        k = rng.choice([4, 5, 6, 7, 8, 9]) if mode == "pool" else rng.choice([2, 3, 4])
        pool = list({(rng.randint(-3, 3), rng.randint(-3, 3)) for _ in range(k)})
        lines = set()
        tries = 0
        while len(lines) < n and tries < 300:
            tries += 1
            if mode == "pool" and len(pool) >= 2:
                p, q = rng.sample(pool, 2)
            else:                                               # "planted": one pool point + random second point
                p = rng.choice(pool)
                q = (rng.randint(-3, 3), rng.randint(-3, 3))
                if p == q:
                    continue
            A, B, C = (p[1] - q[1], q[0] - p[0], p[0] * q[1] - p[1] * q[0])
            gg = gcd(gcd(abs(A), abs(B)), abs(C))
            A, B, C = A // gg, B // gg, C // gg
            if (A, B, C) < (0, 0, 0):
                A, B, C = -A, -B, -C
            lines.add((A, B, C))
        lines = list(lines)
    if len(lines) < n:
        return None
    for _ in range(50):
        M = [[rng.randint(-3, 3) for _ in range(3)] for _ in range(3)]
        det = (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1]) - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
               + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
        if det == 0:
            continue
        out = []
        for (A, B, C) in lines:
            out.append((M[0][0] * A + M[0][1] * B + M[0][2] * C, M[1][0] * A + M[1][1] * B + M[1][2] * C,
                        M[2][0] * A + M[2][1] * B + M[2][2] * C))
        if any(b == 0 for (_, b, _) in out):
            continue
        if len(set(Fr(-a, b) for (a, b, c) in out)) < n:
            continue
        return [(Fr(-a, b), Fr(-c, b)) for (a, b, c) in out]
    return None


def geo_check(g, ref_word=True, gi_list=(), stats=None):
    """full comparison for one Geo arrangement; returns list of error strings"""
    n = g.n
    errs = []
    o = g.oracle()
    if ref_word:
        w = g.wiring_word()
        a = Arr(w, n)
        for L in range(n):
            if [a.events[e] for e in a.rows[L]] != [g.at[p] for p in g.row[L]]:
                errs.append("wiring word does not reproduce the vertex sequences")
                return errs
        ch = Charge(a)
        val, served = values(ch)
        rec = portions(ch)
        for L in range(n):
            if val[L] != o["v"][L] or rec[L] != o["p"][L]:
                errs.append("ORACLE vs REFERENCE: line %d v %s/%s p %s/%s" % (L, o["v"][L], val[L], o["p"][L], rec[L]))
            refv = LA.reference(ch, L, val, served, rec)
            if (refv[2], refv[3]) != (o["nRN"][L], o["nRR"][L]):
                errs.append("ORACLE vs REFERENCE: nRN/nRR line %d %s %s" % (L, refv[2:4], (o["nRN"][L], o["nRR"][L])))
        if a.T() != g.ntri:
            errs.append("triangle count differs %d %d" % (a.T(), g.ntri))
    for L in range(n):
        frames, hids = g.frames(L)
        if COVER_ON and len(frames) >= 2:
            record_cover(frames, hids, "geo n=%d lines=%s L=%d" % (n, [(str(a), str(b)) for a, b in g.lines], L))
        frames = LA.normalise(frames)
        if len(frames) < 2:
            continue
        for f in frames:
            if f not in LA._FRAMESET:
                errs.append("frame not enumerated %s" % (f,))
        for f, h in zip(frames, frames[1:]):
            if not LA.edge_ok(f, h):
                errs.append("edge not allowed")
        if not LA.ends_compatible(frames[0], frames[-1]):
            errs.append("ends incompatible")
        tot = [0] * 5
        for (prev, cur, nxt), hid in zip(LA.line_windows(frames), hids):
            if cur.kind == "T" and hid not in LA._domain(prev, cur, nxt):
                errs.append("hidden outside domain")
            v = LA.exact_vec(prev, cur, nxt, hid)
            for k in range(5):
                tot[k] += v[k]
        want = (o["p"][L], int(2 * (o["v"][L] + 1)), o["nRN"][L], o["nRR"][L], o["nT"][L])
        if tuple(tot) != want:
            errs.append("automaton sum %s vs oracle %s (line %d)" % (tuple(tot), want, L))
        nS = sum(1 for f in frames if f.kind == "S")
        if (nS - (n - 1)) % 2:
            errs.append("parity")
        for gi in gi_list:
            pw = gi.path_weight(frames)
            if isinstance(pw, str):
                errs.append("not a graph path: %s" % pw)
            elif pw > sum(c * x for c, x in zip(gi.obj, want)):
                errs.append("path weight above real value")
        comp = o["v"][L] + Fr(o["nRN"][L], 2) + Fr(3 * o["nRR"][L], 2)
        if comp < -1:
            errs.append("M2 violated")
        clean = (o["nT"][L] == 0) and not any(b[4] == L for b in g.blocks)
        if clean and n % 2 == 0 and n >= 4 and o["p"][L] < 1:
            errs.append("M1 violated")
        if stats is not None:
            stats["lines"] += 1
            stats["minM2"] = min(stats.get("minM2", 99), comp)
            stats["minV"] = min(stats.get("minV", 99), o["v"][L])
            stats["clean"] += clean
    return errs


def cmd_geo(args):
    n_lo, n_hi, seed, count = int(args[0]), int(args[1]), int(args[2]), int(args[3])
    rng = random.Random(seed)
    gi_list = [GraphIndex((0, 1, 1, 3, 0))]
    stats = collections.Counter()
    trip_hist = collections.Counter()
    t0 = time.time()
    for it in range(count):
        n = rng.randint(n_lo, n_hi)
        mode = rng.choice(["pool", "planted", "grid"])
        L = random_lines(rng, n, mode)
        if L is None:
            stats["gen_fail"] += 1
            continue
        g = Geo(L)
        if g.four:
            stats["fourfold"] += 1
            continue
        stats["arr"] += 1
        trip_hist[len(g.triples)] += 1
        errs = geo_check(g, True, gi_list, stats)
        if errs:
            stats["bad_arr"] += 1
            if stats["bad_arr"] <= 10:
                print("ERROR", n, mode, g.lines, errs[:4], flush=True)
    print("geo n=%d..%d seed=%d: arrangements %d (4-fold skipped %d, gen fail %d), lines %d, bad arrangements %d, "
          "min(v+comp)=%s min v=%s (%.0fs)" % (n_lo, n_hi, seed, stats["arr"], stats["fourfold"], stats["gen_fail"],
                                            stats["lines"], stats["bad_arr"], stats.get("minM2"), stats.get("minV"), time.time() - t0))
    print("  triple-point histogram:", dict(sorted(trip_hist.items())))



# ----------------------------------------------------------------------------------------------- independent DP
# A second implementation of the model of work/eng/T20/REPORT.md written from scratch in a block-centric style
# (frames = plain tuples (kind, bin, bout, ub, h); infos = (kind, h, bits-beyond)).  Used for a differential test of every
# window weight and for an independent graph, an independent Bellman-Ford and a checked potential certificate.
NB = ((0, 0), (0, 1), (1, 0), (1, 1))
Z2 = (0, 0)


def ok_frame2(kind, bi, bo, ub, h):
    if kind == "S":
        if ub == (1, 1):
            return False                                           # F7
        for s in (0, 1):
            if ub[s] and (bi[s] or bo[s]):
                return False                                       # F2: triangle next to an unbounded ray
        return True
    for s in (0, 1):
        if ub[s] and (h[s] or (bi[s] and bo[s])):
            return False                                           # F6
    return True


def frame_list2():
    out = []
    for kind in "ST":
        for bi in NB:
            for bo in NB:
                for ub in NB:
                    for h in (NB if kind == "T" else (Z2,)):
                        if ok_frame2(kind, bi, bo, ub, h):
                            out.append((kind, bi, bo, ub, h))
    return out


def domain2(prev, cur, nxt, full_g=False):
    """hidden assignments (sig over E+, E-, W+, W-; g likewise) allowed by F3' and F4"""
    kind, bi, bo, ub, h = cur
    hp, hm = h
    forced = [0, 0, 0, 0]
    for s in (0, 1):
        if nxt is not None and nxt[0] == "S" and bo[s] and nxt[2][s]:
            forced[s] = 1                                          # E+ (s=0), E- (s=1)
        if prev is not None and prev[0] == "S" and bi[s] and prev[2][s]:
            forced[2 + s] = 1                                      # W+, W-
    dbl = [bo[0] and hp, bo[1] and hm, bi[0] and hp, bi[1] and hm]    # E+, E-, W+, W-
    Estat = "N" if bo != (1, 1) else ("B" if (nxt is not None and nxt[0] == "S") else "R")
    Wstat = "N" if bi != (1, 1) else ("B" if (prev is not None and prev[0] == "S") else "R")
    for sig in itertools.product((0, 1), repeat=4):
        if any(forced[k] and not sig[k] for k in range(4)):
            continue
        stat = ["N"] * 6                                           # ring E, E+, W+, W, W-, E-
        stat[0], stat[3] = Estat, Wstat
        for k, pos in ((0, 1), (1, 5), (2, 2), (3, 4)):
            if dbl[k]:
                stat[pos] = "R" if sig[k] else "B"
        if any(stat[i] == "B" and stat[(i + 1) % 6] == "B" for i in range(6)):
            continue
        for g in (itertools.product((0, 1), repeat=4) if full_g else [(0, 0, 0, 0)]):
            yield sig, g


def vec2(prev, cur, nxt, hid=None):
    """(p, v2, nRN, nRR, nT); prev / nxt = (kind, h, bits beyond) or None"""
    kind, bi, bo, ub, h = cur
    p = 0
    if nxt is not None and bo == Z2:
        p += 1
    if kind == "S":
        for s in (0, 1):
            if not ub[s] and bi[s] + bo[s] == 0:
                p += 1
        v2 = 2 * p
        if prev is not None and nxt is not None and prev[0] == "T" and nxt[0] == "T":
            for s in (0, 1):
                if bi[s] and bo[s]:
                    for bits in (bi, bo):                          # segments to the two flankers
                        if bits[1 - s] == 0:
                            v2 -= 3
        return (p, v2, 0, 0, 0)
    sig, g = hid
    hp, hm = h
    v2 = 2 * p
    dbl = [bo == (1, 1), bool(bo[0] and hp), bool(bi[0] and hp), bi == (1, 1), bool(bi[1] and hm), bool(bo[1] and hm)]
    trip = [nxt is not None and nxt[0] == "T", sig[0], sig[2], prev is not None and prev[0] == "T", sig[3], sig[1]]
    stat = ["N" if not dbl[k] else ("R" if trip[k] else "B") for k in range(6)]
    for k in (0, 3):
        v2 += 3 if stat[k] == "N" else -3 if stat[k] == "B" else 0
    nRN = nRR = 0
    for k in range(6):
        if stat[k] != "B":
            continue
        f1, f2 = (k - 1) % 6, (k + 1) % 6
        if k in (0, 3):                                            # L is the axis
            beyond = nxt[2] if k == 0 else prev[2]
            fl = (1, 5) if k == 0 else (2, 4)                      # flank positions; bit side 0 for pos 1,2; side 1 for pos 5,4
            side = {1: 0, 5: 1, 2: 0, 4: 1}
            got = 0
            if trip[fl[0]] and trip[fl[1]]:
                got = sum(3 for q in fl if beyond[side[q]] == 0)
            if got > 0:
                v2 += got
            else:
                v2 += 2 * sum(1 for q in fl if stat[q] == "N")
                nR = sum(1 for q in fl if stat[q] == "R")
                nRR += nR == 2
                nRN += nR == 1
        else:                                                      # axis is another line: block on E+, W+, W-, E-
            # flankers: the L-neighbour (nxt for E+/E-, prev for W+/W-) and the hidden far end of the other flank ray
            nb, hid_pos = ((nxt, 2) if k == 1 else (nxt, 4) if k == 5 else (prev, 1) if k == 2 else (prev, 5))
            hid_sig_idx = {2: 2, 4: 3, 1: 0, 5: 1}[hid_pos]
            side = 0 if k in (1, 2) else 1
            served = nb is not None and nb[0] == "T" and sig[hid_sig_idx] == 1 and (nb[1][side] == 0 or g[hid_sig_idx] == 1)
            if not served:
                for q in (0, 3):
                    if q in (f1, f2) and stat[q] == "N":
                        v2 -= 2
    return (p, v2, nRN, nRR, 1)


def wmin2(obj, prev, cur, nxt):
    if cur[0] == "S":
        return sum(c * x for c, x in zip(obj, vec2(prev, cur, nxt)))
    return min(sum(c * x for c, x in zip(obj, vec2(prev, cur, nxt, hid))) for hid in domain2(prev, cur, nxt))


def build2(obj, allow=lambda f: True, edge_allow=lambda c, n: True, feat=None):
    frames = [f for f in frame_list2() if allow(f)]
    by_bin = collections.defaultdict(list)
    for f in frames:
        by_bin[f[1]].append(f)
    node = {}
    nodes = []

    def nid(x):
        if x not in node:
            node[x] = len(nodes)
            nodes.append(x)
        return node[x]
    starts, terms, edges = [], [], []
    stack = []
    for f in frames:
        if f[1] == Z2:
            x = (None, f, 1 if f[0] == "S" else 0, f[3], 0, False)          # (prev info, frame, parity, first ub, flag, last)
            starts.append(nid(x))
            stack.append(x)
    seen = set(stack)
    while stack:
        x = stack.pop()
        prev, cur, par, cls, fl, last = x
        u = node[x]
        if last:
            if not ((cls[0] and cur[3][1]) or (cls[1] and cur[3][0])):
                fl2 = fl or (feat is not None and feat(prev, cur, None))
                terms.append((u, wmin2(obj, prev, cur, None), par, int(bool(fl2))))
            continue
        for nx in by_bin[cur[2]]:
            if not edge_allow(cur, nx):
                continue
            if cur[2] == (1, 1) and cur[0] == "S" and nx[0] == "S":
                continue                                                       # F3
            for is_last in (False, True):
                if is_last and nx[2] != Z2:
                    continue
                if nx[0] == "T" and nx[3] != Z2 and not is_last:
                    continue
                ni = (nx[0], nx[4], nx[2])
                fl2 = fl or (feat is not None and feat(prev, cur, ni))
                y = ((cur[0], cur[4], cur[1]), nx, (par + (nx[0] == "S")) % 2, cls, int(bool(fl2)), is_last)
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
                nid(y)
                edges.append((u, node[y], wmin2(obj, prev, cur, ni)))
    return nodes, starts, edges, terms


def bellman_ford2(nodes, starts, edges, terms, parity=None, need_flag=False):
    """returns (value or -inf or None, potentials dist) ; certificate verified in verify2"""
    import numpy as np
    N = len(nodes)
    INF = 10 ** 9
    terms = [t for t in terms if (parity is None or t[2] == parity) and (not need_flag or t[3])]
    # keep only nodes that can reach a terminal
    radj = collections.defaultdict(list)
    for (a, b, w) in edges:
        radj[b].append(a)
    co = {t[0] for t in terms}
    st = list(co)
    while st:
        x = st.pop()
        for y in radj[x]:
            if y not in co:
                co.add(y)
                st.append(y)
    E = [(a, b, w) for (a, b, w) in edges if a in co and b in co]
    src = np.array([e[0] for e in E], dtype=np.int64)
    dst = np.array([e[1] for e in E], dtype=np.int64)
    wt = np.array([e[2] for e in E], dtype=np.int64)
    dist = np.full(N, INF, dtype=np.int64)
    for s in starts:
        if s in co:
            dist[s] = 0
    pred = np.full(N, -1, dtype=np.int64)
    converged = False
    for it in range(N + 5):
        ok = dist[src] < INF
        cand = np.where(ok, dist[src] + wt, INF)
        best = dist.copy()
        np.minimum.at(best, dst, cand)
        imp = np.nonzero(best < dist)[0]
        if len(imp) == 0:
            converged = True
            break
        # record a predecessor for improved nodes
        sel = np.nonzero(ok & (cand == best[dst]) & (best[dst] < dist[dst]))[0]
        pred[dst[sel]] = src[sel]
        dist = best
        last_imp = imp
    if not converged:
        # find a cycle in the predecessor graph
        x = int(last_imp[0])
        for _ in range(N + 5):
            x = int(pred[x])
        cyc, y = [x], int(pred[x])
        while y != x:
            cyc.append(y)
            y = int(pred[y])
        cyc.reverse()
        return float("-inf"), (cyc, E, co)
    best_v = None
    for (u, w, par, fl) in terms:
        if dist[u] < INF and (best_v is None or dist[u] + w < best_v):
            best_v = int(dist[u] + w)
    return best_v, (dist, E, co, terms)


def verify2(res, starts, nodes):
    """independent verification of the output of bellman_ford2 (pure python)"""
    val, data = res
    if val == float("-inf"):
        cyc, E, co = data
        w = {}
        for (a, b, ww) in E:
            w[(a, b)] = min(ww, w.get((a, b), 10 ** 9))
        tot = 0
        for i, x in enumerate(cyc):
            y = cyc[(i + 1) % len(cyc)]
            if (x, y) not in w:
                return "cycle edge missing"
            tot += w[(x, y)]
        return "negative cycle OK (length %d, weight %d)" % (len(cyc), tot) if tot < 0 else "cycle not negative"
    if val is None:
        return "no terminal reachable"
    dist, E, co, terms = data
    INF = 10 ** 9
    for s in starts:
        if s in co and dist[s] > 0:
            return "start potential > 0"
    for (a, b, w) in E:
        if dist[a] < INF and dist[b] > dist[a] + w:
            return "potential violated on an edge"
    reach = dist < INF
    lo = min(int(dist[u] + w) for (u, w, par, fl) in terms if reach[u])
    if lo != val:
        return "terminal bound differs"
    return "potential certificate OK (all %d edges, %d start nodes): every path costs >= %d" % (len(E), len(starts), val)


def cmd_dp(args):
    # 1. frames
    f2 = set(frame_list2())
    f1 = set(tuple(f) for f in LA.all_frames())
    print("frame sets equal:", f1 == f2, len(f1), len(f2))

    def conv_info(x):
        return None if x is None else (x[0], x[1], x[2])
    # 2. window-by-window differential test: every window that LA enumerates
    fr = LA.all_frames()
    pi, ni = collections.defaultdict(set), collections.defaultdict(set)
    for f in fr:
        pi[f.bout].add((f.kind, f.h, f.bin, False))
        ni[f.bin].add((f.kind, f.h, f.bout, False))
    nw = ndiff = 0
    t0 = time.time()
    for c in fr:
        for p_ in list(pi[c.bin]) + ([None] if c.bin == Z2 else []):
            for n_ in list(ni[c.bout]) + ([None] if c.bout == Z2 else []):
                if p_ is not None and c.kind == "S" and p_[0] == "S" and c.bin == (1, 1):
                    pass
                nw += 1
                o1 = set(LA.options(p_, c, n_))
                cc = tuple(c)
                # options of LA are sets of distinct vectors (g = 0); compare against the g = 0 vectors of vec2
                if c.kind == "S":
                    o2 = {vec2(conv_info(p_), cc, conv_info(n_))}
                else:
                    o2 = {vec2(conv_info(p_), cc, conv_info(n_), hid) for hid in domain2(conv_info(p_), cc, conv_info(n_))}
                if o1 != o2:
                    ndiff += 1
                    if ndiff <= 5:
                        print("DIFF", p_, c, n_, "LA-only", sorted(o1 - o2)[:3], "vec2-only", sorted(o2 - o1)[:3])
    print("windows compared: %d, differing option sets: %d (%.0fs)" % (nw, ndiff, time.time() - t0))
    # 3. full_g domains and exact_vec on all g
    nd = 0
    t0 = time.time()
    for c in fr:
        if c.kind != "T":
            continue
        for p_ in list(pi[c.bin]) + ([None] if c.bin == Z2 else []):
            for n_ in list(ni[c.bout]) + ([None] if c.bout == Z2 else []):
                d1 = set(LA.sig_domain(p_, c, n_, True))
                d2 = set(domain2(conv_info(p_), tuple(c), conv_info(n_), True))
                if d1 != d2:
                    nd += 1
                    continue
                for hid in d1:
                    if LA.exact_vec(p_, c, n_, hid) != vec2(conv_info(p_), tuple(c), conv_info(n_), hid):
                        nd += 1
    print("full-g domains / exact vectors differing: %d (%.0fs)" % (nd, time.time() - t0))
    # 4. independent graphs, Bellman-Ford and certificates
    clean = lambda f: f[0] == "S" and not (f[1][0] and f[2][0]) and not (f[1][1] and f[2][1])
    xonly = lambda f: f[0] == "S" or (f[1] == (1, 1) and f[2] == (1, 1) and f[4] == Z2 and f[3] == Z2)
    noTT = lambda c, n: not (c[0] == "T" and n[0] == "T")
    jobs = [
        ("M1 clean, n even", (1, 0, 0, 0, 0), dict(allow=clean), 1, None),
        ("M1 clean, n odd", (1, 0, 0, 0, 0), dict(allow=clean), 0, None),
        ("M2 (0,1,1,3,0) all n", (0, 1, 1, 3, 0), {}, None, None),
        ("M2 (0,1,1,3,0) even n", (0, 1, 1, 3, 0), {}, 1, None),
        ("M2 (0,1,1,3,0) odd n", (0, 1, 1, 3, 0), {}, 0, None),
        ("M2 (0,1,1,2,0) [expect -inf]", (0, 1, 1, 2, 0), {}, None, None),
        ("M2 (0,1,0,3,0) [expect -inf]", (0, 1, 0, 3, 0), {}, None, None),
        ("M2 (0,1,2,3,0) all n", (0, 1, 2, 3, 0), {}, None, None),
        ("M2 (0,1,1,3,0) even n, x-only lines", (0, 1, 1, 3, 0), dict(allow=xonly, edge_allow=noTT), 1, None),
    ]
    for name, obj, kw, par, _ in jobs:
        t0 = time.time()
        nodes, starts, edges, terms = build2(obj, **kw)
        res = bellman_ford2(nodes, starts, edges, terms, parity=par)
        chk = verify2(res, starts, nodes)
        # LA's answer
        kw1 = {}
        if "allow" in kw:
            kw1["allow"] = (lambda f, a=kw["allow"]: a(tuple(f)))
        if "edge_allow" in kw:
            kw1["edge_allow"] = (lambda c, n, a=kw["edge_allow"]: a(tuple(c), tuple(n)))
        v1, _ = LA.solve(LA.Graph(**kw1), obj, parity=par)
        print("%-42s  independent DP: %s  | LA.solve: %s | %s  (%d nodes, %d edges, %.0fs)" % (
            name, res[0], v1, chk, len(nodes), len(edges), time.time() - t0), flush=True)



# ----------------------------------------------------------------------------------------------- mutation self-test
# Each mutation makes one imposed fact STRONGER than what is true (or perturbs a window formula).  A sound audit harness
# must reject every one of them on small exhaustive input; this measures the power of the tests used above.
def apply_mutation(name):
    orig_ends = LA.ends_compatible
    orig_cls = LA.ends_compatible_cls
    orig_edge = LA.edge_ok
    orig_dom = LA.sig_domain
    orig_frame_ok = LA.frame_ok
    orig_vec = LA.exact_vec
    if name == "F5_same_side":            # also forbid both ends having an unbounded + ray (false)
        LA.ends_compatible = lambda a, b: orig_ends(a, b) and not (a.ub[0] and b.ub[0])
        LA.ends_compatible_cls = lambda c, l: orig_cls(c, l) and not (c[0] and l.ub[0])
    elif name == "F5_missing":            # drop F5 entirely (weaker: must NOT fail on data, only weaken M1)
        LA.ends_compatible = lambda a, b: True
        LA.ends_compatible_cls = lambda c, l: True
    elif name == "F3_bridges":            # also forbid triple-triple (1,1) segments (false: bridges exist)
        LA.edge_ok = lambda c, n: orig_edge(c, n) and not (c.bout == (1, 1) and c.kind == "T" and n.kind == "T")
    elif name == "F3_simple_triple":      # also forbid simple-triple (1,1) segments (false: blocks exist)
        LA.edge_ok = lambda c, n: orig_edge(c, n) and not (c.bout == (1, 1))
    elif name == "F7_asym":               # forbid S frames whose ub = (0,1) (false)
        LA.frame_ok = lambda f: orig_frame_ok(f) and not (f.kind == "S" and f.ub == (0, 1))
    elif name == "F2_triangle_by_ub":     # F2 with the wrong quantifier: ub forbids only the incoming bit (false for the outgoing)
        def fo(f):
            if f.kind == "S" and f.ub[0] and f.bout[0]:
                return True
            return orig_frame_ok(f)
        # weaker than truth: allows impossible frames (harmless for soundness; harmful for tightness) -- reported as 'weaker'
        LA.frame_ok = fo
    elif name == "F3p_other_side":        # F3' forcing applied with the wrong side bit (false)
        def dom(prev, cur, nxt, full_g=False):
            for sig, g in orig_dom(prev, cur, nxt, full_g):
                if nxt is not None and nxt[0] == "S" and cur.bout[0] and nxt[2][1] and not sig[0]:
                    continue
                yield sig, g
        LA.sig_domain = dom
    elif name == "F4_adjacent_R":         # forbid B next to R as well (false)
        def dom(prev, cur, nxt, full_g=False):
            for sig, g in orig_dom(prev, cur, nxt, full_g):
                dbl = (cur.bout[0] and cur.h[0], cur.bout[1] and cur.h[1], cur.bin[0] and cur.h[0], cur.bin[1] and cur.h[1])
                st = {}
                for k, R in enumerate(LA.ER):
                    st[R] = ("B" if sig[k] == 0 else "R") if dbl[k] else "N"
                st["E"] = LA.ray_status_L(cur.bout, nxt)
                st["W"] = LA.ray_status_L(cur.bin, prev)
                if any((st[LA.RING[i]] == "B" and st[LA.RING[(i + 1) % 6]] == "R") or (st[LA.RING[i]] == "R" and st[LA.RING[(i + 1) % 6]] == "B")
                       for i in range(6)):
                    continue
                yield sig, g
        LA.sig_domain = dom
    elif name == "F4_opposite":           # forbid opposite blocks (false: X points)
        def dom(prev, cur, nxt, full_g=False):
            for sig, g in orig_dom(prev, cur, nxt, full_g):
                dbl = (cur.bout[0] and cur.h[0], cur.bout[1] and cur.h[1], cur.bin[0] and cur.h[0], cur.bin[1] and cur.h[1])
                st = {}
                for k, R in enumerate(LA.ER):
                    st[R] = ("B" if sig[k] == 0 else "R") if dbl[k] else "N"
                st["E"] = LA.ray_status_L(cur.bout, nxt)
                st["W"] = LA.ray_status_L(cur.bin, prev)
                if any(st[LA.RING[i]] == "B" and st[LA.RING[(i + 3) % 6]] == "B" for i in range(3)):
                    continue
                yield sig, g
        LA.sig_domain = dom
    elif name == "g_always_1":            # fix g = 1 instead of 0 in the DP (unsound direction for the min: weights go up)
        def dom(prev, cur, nxt, full_g=False):
            for sig, g in orig_dom(prev, cur, nxt, full_g):
                yield sig, ((1, 1, 1, 1) if not full_g else g)
        LA.sig_domain = dom
    elif name == "touch_side0":           # touches only counted on side +
        def vec(prev, cur, nxt, hid=None):
            r = list(orig_vec(prev, cur, nxt, hid))
            if cur.kind == "S" and not cur.ub[1] and cur.bin[1] + cur.bout[1] == 0:
                r[0] -= 1
                r[1] -= 2
            return tuple(r)
        LA.exact_vec = vec
    elif name == "cap_pay_2":             # T1 with L the cap pays 2 instead of 3
        def vec(prev, cur, nxt, hid=None):
            r = list(orig_vec(prev, cur, nxt, hid))
            if cur.kind == "S" and prev is not None and nxt is not None and prev[0] == "T" and nxt[0] == "T":
                for k in (0, 1):
                    if cur.bin[k] and cur.bout[k]:
                        r[1] += (cur.bin[1 - k] == 0) + (cur.bout[1 - k] == 0)
            return tuple(r)
        LA.exact_vec = vec
    elif name == "parity_flip":
        pass                              # handled by the caller
    else:
        raise SystemExit("unknown mutation " + name)
    LA._FRAMESET = frozenset(LA.all_frames())
    LA._opt_cache.clear()
    LA._dom_cache.clear()
    real_options = LA.options

    def safe_options(prev, cur, nxt):                       # a mutated domain may be empty: treat as +infinity weight
        r = real_options(prev, cur, nxt)
        return r if r else frozenset([(10 ** 6, 10 ** 6, 10 ** 6, 10 ** 6, 0)])
    LA.options = safe_options


def cmd_mut(args):
    name, n = args[0], int(args[1])
    apply_mutation(name)
    gi_list = [GraphIndex((0, 1, 1, 3, 0)), GraphIndex((1, 0, 0, 0, 0))]
    stats = collections.Counter()
    kinds = collections.Counter()
    for w in enum_all(n):
        errs = check_arrangement(w, n, gi_list, stats, verbose=False)
        for (L, e) in errs:
            kinds[e[0].split(":")[0][:60]] += 1
    print("MUTATION %-18s n=%d: arrangements %d, failing lines %d %s" % (name, n, stats["arr"], stats["bad_lines"],
                                                                        dict(kinds.most_common(3))))



# ----------------------------------------------------------------------------------------------- feature coverage
# Which branches of the window formulas / which local facts are actually exercised by real lines?
COVER = collections.Counter()
COVER_ON = False
COVER_EX = {}


def window_features(prev, cur, nxt, hid):
    """set of feature labels of a real window (prev / nxt = LA Info tuples)"""
    F = set()
    kind, bi, bo, ub, h = tuple(cur)
    pi = None if prev is None else (prev[0], prev[1], prev[2])
    ni = None if nxt is None else (nxt[0], nxt[1], nxt[2])
    if kind == "S":
        F.add("S")
        if ni is not None and bo == Z2:
            F.add("S:own-unused-seg")
        for s in (0, 1):
            if not ub[s] and bi[s] + bo[s] == 0:
                F.add("S:touch")
        caps = [s for s in (0, 1) if bi[s] and bo[s]]
        if len(caps) == 2:
            F.add("S:caps-both-sides")
        for s in caps:
            if pi is not None and ni is not None:
                key = ("T" if pi[0] == "T" else "S") + ("T" if ni[0] == "T" else "S")
                nN = (bi[1 - s] == 0) + (bo[1 - s] == 0)
                F.add("S:cap[%s]" % key + (":T1 N-gap-ends=%d" % nN if key == "TT" else ""))
            else:
                F.add("S:cap-at-end")
        if bo == (1, 1) and ni is not None:
            F.add("S:(1,1)-out")
        if bi == (1, 1) and pi is not None:
            F.add("S:(1,1)-in")
        return F
    F.add("T")
    sig, g = hid
    hp, hm = h
    dbl = [bo == (1, 1), bool(bo[0] and hp), bool(bi[0] and hp), bi == (1, 1), bool(bi[1] and hm), bool(bo[1] and hm)]
    trip = [ni is not None and ni[0] == "T", sig[0], sig[2], pi is not None and pi[0] == "T", sig[3], sig[1]]
    stat = ["N" if not dbl[k] else ("R" if trip[k] else "B") for k in range(6)]
    F.add("T:Lrays=%s%s" % (stat[0], stat[3]))
    F.add("T:hidden-rays=%s" % "".join(stat[k] for k in (1, 2, 4, 5)))
    # activity of F3' and F4 in this real window
    dom_sigs = {sg for sg, _ in domain2(pi, tuple(cur), ni)}
    forced_only = 16
    fz = [0, 0, 0, 0]
    for s_ in (0, 1):
        if ni is not None and ni[0] == "S" and bo[s_] and ni[2][s_]:
            fz[s_] = 1
        if pi is not None and pi[0] == "S" and bi[s_] and pi[2][s_]:
            fz[2 + s_] = 1
    forced_only = sum(1 for sg in itertools.product((0, 1), repeat=4) if not any(fz[k] and not sg[k] for k in range(4)))
    if forced_only < 16:
        F.add("T:F3'-active (removes %d of 16 hidden assignments)" % (16 - forced_only))
    if len(dom_sigs) < forced_only:
        F.add("T:F4-active (removes %d assignments after F3')" % (forced_only - len(dom_sigs)))
    if sig in dom_sigs or True:
        pass
    # forcing
    for s in (0, 1):
        if ni is not None and ni[0] == "S" and bo[s] and ni[2][s]:
            F.add("T:F3'-forced-next")
        if pi is not None and pi[0] == "S" and bi[s] and pi[2][s]:
            F.add("T:F3'-forced-prev")
    for k in (0, 3):
        if stat[k] != "B":
            continue
        fl = (1, 5) if k == 0 else (2, 4)
        beyond = (ni if k == 0 else pi)[2]
        side = {1: 0, 5: 1, 2: 0, 4: 1}
        both = trip[fl[0]] and trip[fl[1]]
        nN = sum(1 for q in fl if beyond[side[q]] == 0) if both else 0
        if both and nN > 0:
            F.add("T:axis-block[%s] T1-served N-gap-ends=%d" % ("E" if k == 0 else "W", nN))
        else:
            nR = sum(1 for q in fl if stat[q] == "R")
            F.add("T:axis-block F-branch nR=%d%s" % (nR, " (flankers triple, no N gap)" if both else ""))
            if any(stat[q] == "B" for q in fl):
                F.add("T:AXIS-BLOCK WITH B FLANK (F4 violation)")
    for k in (1, 2, 4, 5):
        if stat[k] != "B":
            continue
        nb, hid_pos = ((ni, 2) if k == 1 else (ni, 4) if k == 5 else (pi, 1) if k == 2 else (pi, 5))
        hs = {2: 2, 4: 3, 1: 0, 5: 1}[hid_pos]
        side = 0 if k in (1, 2) else 1
        lray = 0 if k in (1, 5) else 3
        why = None
        if nb is None or nb[0] != "T":
            why = "unserved: L-neighbour not triple"
        elif not sig[hs]:
            why = "unserved: hidden flanker not triple"
        elif nb[1][side] == 0:
            why = "served: gap ray at L-neighbour is N"
        elif g[hs]:
            why = "served ONLY via hidden gap (g=1)"
        else:
            why = "unserved: both flankers triple, no N gap"
        F.add("T:adjacent-block[L-ray %s] %s" % (stat[lray], why))
    return F


def record_cover(frames, hids, tag):
    fr = LA.normalise(frames)
    F = set()
    for (prev, cur, nxt), hid in zip(LA.line_windows(fr), hids):
        for f in window_features(prev, cur, nxt, hid):
            F.add(f)
    f0, f1 = fr[0], fr[-1]
    F.add("ends: first.ub=%s last.ub=%s" % (tuple(f0.ub), tuple(f1.ub)))
    for f in F:
        COVER[f] += 1
        COVER_EX.setdefault(f, tag)



def cmd_cover(args):
    """cover enum N | walk N seed steps pe pc | geo lo hi seed count   -> prints feature counts (with one example each)"""
    global COVER_ON
    COVER_ON = True
    sub = args[0]
    if sub == "enum":
        cmd_enum(args[1:])
    elif sub == "walk":
        cmd_walk(args[1:])
    elif sub == "geo":
        cmd_geo(args[1:])
    elif sub == "sample":
        cmd_sample(args[1:])
    out = {k: [v, COVER_EX[k]] for k, v in COVER.items()}
    fn = ROOT / "work/eng/A20" / ("cover_" + "_".join(args).replace(" ", "") + ".json")
    json.dump(out, open(fn, "w"), indent=0)
    for k in sorted(COVER):
        print("  %8d  %s" % (COVER[k], k))



def cmd_ablate(args):
    """which local facts do M1 and M2 actually depend on?  drop one fact at a time and re-solve"""
    orig_frame_ok, orig_edge, orig_dom = LA.frame_ok, LA.edge_ok, LA.sig_domain

    def frame_ok_v(drop):
        def fo(f):
            (ti, bi_), (to, bo_) = f.bin, f.bout
            if f.kind == "S":
                if "F7" not in drop and f.ub == (1, 1):
                    return False
                if "F2" not in drop and ((f.ub[0] and (ti or to)) or (f.ub[1] and (bi_ or bo_))):
                    return False
                return True
            if "F6" not in drop:
                if f.ub[0] and (f.h[0] or (ti and to)):
                    return False
                if f.ub[1] and (f.h[1] or (bi_ and bo_)):
                    return False
            return True
        return fo

    def dom_v(drop):
        def dom(prev, cur, nxt, full_g=False):
            bi, bo = cur.bin, cur.bout
            hp, hm = cur.h
            Es = LA.ray_status_L(bo, nxt)
            Ws = LA.ray_status_L(bi, prev)
            forced = [0, 0, 0, 0]
            if "F3p" not in drop:
                if nxt is not None and nxt[0] == "S":
                    forced[0] = int(bo[0] and nxt[2][0])
                    forced[1] = int(bo[1] and nxt[2][1])
                if prev is not None and prev[0] == "S":
                    forced[2] = int(bi[0] and prev[2][0])
                    forced[3] = int(bi[1] and prev[2][1])
            dbl = (bo[0] and hp, bo[1] and hm, bi[0] and hp, bi[1] and hm)
            for sig in itertools.product((0, 1), repeat=4):
                if any(forced[k] and not sig[k] for k in range(4)):
                    continue
                st = {"E": Es, "W": Ws}
                for k, R in enumerate(LA.ER):
                    st[R] = ("B" if sig[k] == 0 else "R") if dbl[k] else "N"
                if "F4" not in drop and any(st[LA.RING[i]] == "B" and st[LA.RING[(i + 1) % 6]] == "B" for i in range(6)):
                    continue
                for g in (itertools.product((0, 1), repeat=4) if full_g else [(0, 0, 0, 0)]):
                    yield sig, g
        return dom

    def run(drop):
        LA.frame_ok = frame_ok_v(drop)
        LA.edge_ok = (lambda c, n: c.bout == n.bin) if "F3" in drop else orig_edge
        LA.sig_domain = dom_v(drop)
        LA._opt_cache.clear()
        res = []
        for name, obj, allow, par in (("M1 even", (1, 0, 0, 0, 0), LA.clean_frame, 1), ("M2 all n", (0, 1, 1, 3, 0), lambda f: True, None)):
            g = LA.Graph(allow=allow, compat=("F5" not in drop))
            v, _ = LA.solve(g, obj, parity=par)
            res.append("%s: %s" % (name, v if v != float("-inf") else "-inf"))
        print("drop %-12s -> %s" % (",".join(sorted(drop)) or "(nothing)", " | ".join(res)), flush=True)
    sets = ([[], ["F2"], ["F3"], ["F3p"], ["F4"], ["F5"], ["F6"], ["F7"], ["F3", "F3p", "F4"]] if not args
            else [a.split(",") if a != "-" else [] for a in args])
    for drop in sets:
        run(set(drop))



def energy(w, n):
    """(min over lines of v_L + comp, number of lines attaining it, M1 slack = min p over clean lines (99 if none))"""
    ch = Charge(Arr(w, n))
    val, served = values(ch)
    rec = portions(ch)
    best, cnt, m1 = Fr(99), 0, 99
    for L in range(n):
        p, v2, nRN, nRR, nT = LA.reference(ch, L, val, served, rec)
        comp = Fr(v2, 2) - 1 + Fr(nRN, 2) + Fr(3 * nRR, 2)
        if comp < best:
            best, cnt = comp, 0
        cnt += comp == best
        if not ch.onl[L] and not any(b[5] == L for b in ch.blk):
            m1 = min(m1, p)
    return best, cnt, m1


def cmd_anneal(args):
    """simulated annealing that tries to FALSIFY M2 (min_L v_L + comp < -1) and M1 (clean line with p = 0, n even)"""
    n, seed, steps = int(args[0]), int(args[1]), int(args[2])
    temp = float(args[3]) if len(args) > 3 else 0.3
    rng = random.Random(seed)
    a = Arr(bubble_word(n), n)
    cur = energy(bubble_word(n), n)
    best = cur
    found = []
    seen = set()
    t0 = time.time()
    for it in range(steps):
        w = mutate.random_move(a, rng, p_collapse=0.4, p_expand=0.15)
        if w is None:
            continue
        b = Arr(w, n)
        if any(len(e) > 3 for e in b.events):
            continue
        e = energy(w, n)
        seen.add(w)
        # lower min-comp is better; more lines at the minimum is better
        key_new, key_cur = (float(e[0]), -e[1]), (float(cur[0]), -cur[1])
        if key_new <= key_cur or rng.random() < pow(2.718, -(float(e[0]) - float(cur[0])) / temp):
            a, cur = b, e
        if e[0] < -1 or (n % 2 == 0 and e[2] == 0):
            found.append(w)
            print("!!! FALSIFIED n=%d word=%s energy=%s" % (n, w, e), flush=True)
        if key_new < (float(best[0]), -best[1]):
            best = e
    print("anneal n=%d seed=%d steps=%d: distinct %d, best min(v+comp)=%s (attained by %d lines), falsifications %d (%.0fs)" % (
        n, seed, steps, len(seen), best[0], best[1], len(found), time.time() - t0))



def random_reduced_word(n, rng):
    """random maximal chain of adjacent transpositions (a random simple arrangement of n pseudolines)"""
    perm = list(range(n))
    toks = []
    while True:
        cand = [g for g in range(n - 1) if perm[g] < perm[g + 1]]
        if not cand:
            return " ".join(toks)
        g = rng.choice(cand)
        perm[g], perm[g + 1] = perm[g + 1], perm[g]
        toks.append(str(g))


def cmd_sample(args):
    """sample n count seed [collapse_bias]: independent random simple arrangements, then a random number of collapses/flips/expands"""
    n, count, seed = int(args[0]), int(args[1]), int(args[2])
    gi_list = [GraphIndex((0, 1, 1, 3, 0)), GraphIndex((1, 0, 0, 0, 0))]
    rng = random.Random(seed)
    stats = collections.Counter()
    trip_hist = collections.Counter()
    t0 = time.time()
    seen = set()
    for it in range(count):
        w = random_reduced_word(n, rng)
        a = Arr(w, n)
        w = canon(a)
        a = Arr(w, n)
        for _ in range(rng.randint(0, 3 * n)):
            w2 = mutate.random_move(a, rng, p_collapse=rng.choice([0.2, 0.5, 0.7]), p_expand=rng.choice([0.05, 0.2]))
            if w2 is None:
                continue
            b = Arr(w2, n)
            if any(len(e) > 3 for e in b.events):
                continue
            a, w = b, w2
        if w in seen:
            continue
        seen.add(w)
        trip_hist[len(a.triples)] += 1
        check_arrangement(w, n, gi_list, stats)
    print("sample n=%d seed=%d: distinct arrangements %d, lines %d, bad lines %d, min(v+comp)=%s min v=%s (%.0fs)" % (
        n, seed, stats["arr"], stats["lines"], stats["bad_lines"], stats.get("minM2"), stats.get("minV"), time.time() - t0))
    print("  triple-point histogram:", dict(sorted(trip_hist.items())))



def smooth_energy(w, n, beta=2.0):
    import math
    ch = Charge(Arr(w, n))
    val, served = values(ch)
    rec = portions(ch)
    E, low, m1p = 0.0, Fr(99), 99
    for L in range(n):
        p, v2, nRN, nRR, nT = LA.reference(ch, L, val, served, rec)
        comp = Fr(v2, 2) - 1 + Fr(nRN, 2) + Fr(3 * nRR, 2)
        low = min(low, comp)
        E += math.exp(-beta * float(comp))
        if not ch.onl[L] and not any(b[5] == L for b in ch.blk):
            m1p = min(m1p, p)
            if n % 2 == 0:
                E += math.exp(-beta * (p - 1))            # a clean line with p = 0 would contribute e^{beta}
    return E, low, m1p


def cmd_anneal2(args):
    """Metropolis walk on the smooth energy sum_L exp(-beta * (v_L + comp)) (+ clean-line term): drives towards many
    near-violating lines; reports any real violation of M1 / M2."""
    import math
    n, seed, steps = int(args[0]), int(args[1]), int(args[2])
    T = float(args[3]) if len(args) > 3 else 1.0
    rng = random.Random(seed)
    w = canon(Arr(random_reduced_word(n, rng), n))
    a = Arr(w, n)
    cur = smooth_energy(w, n)
    best_low = cur[1]
    viol = 0
    seen = set()
    t0 = time.time()
    hist = collections.Counter()
    for it in range(steps):
        w2 = mutate.random_move(a, rng, p_collapse=0.35, p_expand=0.2)
        if w2 is None:
            continue
        b = Arr(w2, n)
        if any(len(e) > 3 for e in b.events):
            continue
        e = smooth_energy(w2, n)
        seen.add(w2)
        hist[len(b.triples)] += 1
        if e[1] < -1 or (n % 2 == 0 and e[2] == 0):
            viol += 1
            print("!!! FALSIFIED n=%d word=%s low=%s m1=%s" % (n, w2, e[1], e[2]), flush=True)
        if e[0] >= cur[0] or rng.random() < math.exp((e[0] - cur[0]) / (T * max(cur[0], 1))) :
            a, cur = b, e
            best_low = min(best_low, e[1])
    print("anneal2 n=%d seed=%d steps=%d distinct=%d lowest v+comp seen=%s violations=%d triple-hist=%s (%.0fs)" % (
        n, seed, steps, len(seen), best_low, viol, dict(sorted(hist.items())), time.time() - t0))



def cmd_data(args):
    """data <mod> <part> <limit> <files...>: the graph-path membership check on the previous worker's data sets"""
    mod, part, limit = int(args[0]), int(args[1]), int(args[2])
    files = args[3:]
    gi_list = [GraphIndex((0, 1, 1, 3, 0)), GraphIndex((1, 0, 0, 0, 0))]
    stats = collections.Counter()
    t0 = time.time()
    for g, ch in LA.iter_arrangements(files, even_only=False, limit=limit, mod=mod, part=part):
        n = ch.a.n
        check_arrangement(g, n, gi_list, stats)
    print("data mod=%d part=%d: arrangements %d, lines %d, bad lines %d, min(v+comp)=%s, min v=%s, incomplete skipped %d (%.0fs)" % (
        mod, part, stats["arr"], stats["lines"], stats["bad_lines"], stats.get("minM2"), stats.get("minV"),
        LA.SKIPPED_INCOMPLETE[0], time.time() - t0))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "enum":
        cmd_enum(sys.argv[2:])
    elif cmd == "walk":
        cmd_walk(sys.argv[2:])
    elif cmd == "geo":
        cmd_geo(sys.argv[2:])
    elif cmd == "dp":
        cmd_dp(sys.argv[2:])
    elif cmd == "mut":
        cmd_mut(sys.argv[2:])
    elif cmd == "cover":
        cmd_cover(sys.argv[2:])
    elif cmd == "ablate":
        cmd_ablate(sys.argv[2:])
    elif cmd == "anneal":
        cmd_anneal(sys.argv[2:])
    elif cmd == "sample":
        cmd_sample(sys.argv[2:])
    elif cmd == "anneal2":
        cmd_anneal2(sys.argv[2:])
    elif cmd == "data":
        cmd_data(sys.argv[2:])
    else:
        import importlib
        raise SystemExit("unknown command")

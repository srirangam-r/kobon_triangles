#!/usr/bin/env python3
"""Exact maximum number of bounded triangles after adding TWO pseudolines to a fixed arrangement.

Base: a wiring word (gallery 'gens'; triple points 'g*' allowed).  The new lines L1 < L2 sit at final slope ranks
r1 < r2 in 0..n0+1 (C(n0+2, 2) rank pairs: 153 for n0 = 16); they may pass through simple base vertices (triple
points, also L1 x L2 on a base line) but never through a triple point (no 4-fold point).  Same semantics as
fastext.Ext.

Model.  A new line is a path in the face graph (work/research2/extend_dp.py); its gain over the base is
G = -(base triangles cut) + (new triangles created) = sum of per-face gains.  For two lines
    T = T0 + G1 + G2 + I,        I = sum over base faces cut by both lines of a local interaction term,
and only base triangles cut by both lines (each cut once, not twice: +1 each) and the crossing L1 x L2 (at most
one face pair) can make I positive (proved by brute force per face in `interaction_bound`).  So
    I <= Kx + min(D1, D2)  <= Ib,     D = number of base triangles cut by the line.
Search (rank pair (r1, r2), incumbent T_best, need T >= T*):
    X = T* - T0 - Ib.  Some optimal line has G >= ...: every pair with T >= T* has G1 >= ta (case A: enumerate L1
    at base gap r1 with G1 >= ta, exact best L2 by the one-line DP on the explicit arrangement base + L1) or
    G1 < ta and hence G2 >= X + 1 - ta (case B: enumerate L2 at base gap r2 - 1, exact best L1 on base + L2).
    Enumeration is DFS over the DP with the exact best-suffix bound, so only paths with G >= threshold are visited.
    The incumbent is raised during the search, which tightens the thresholds (the thresholds are re-derived from
    the current incumbent at every node).

CLI:
    extend2_dp.py max2 INPUT [--ranks r1,r2] [--target T] [--limit K]
INPUT: a gallery JSON ({"gens": ...}), a seeds JSON list (seeds16.json format) or a text file with one word per
line.  Without --target the exact maximum of every rank pair is printed (finding a larger value raises the bar
for the following searches).  With --target T only "is there a placement with >= T triangles" is decided per
rank pair (much faster when T is above the maximum).
    extend2_dp.py selftest      # validation against fastext.Ext (SAT) and brute force
"""
import argparse
import json
import sys
import time
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "work/research2"))
sys.path.insert(0, str(ROOT / "search"))
import extend_dp as X  # noqa: E402

NEG = -99


def piece_tri(kinds, i, j):
    """Is the piece of a face on the boundary arc i -> j (cut by the chord i-j) a bounded triangle?
    kinds: element kinds 'e' / 'v' / 'inf' around the face."""
    if kinds[i] == 'inf' or kinds[j] == 'inf':
        return False
    m = len(kinds)
    c = (kinds[i] == 'e') + (kinds[j] == 'e')
    k = (i + 1) % m
    while k != j:
        if kinds[k] == 'inf':
            return False
        c += kinds[k] == 'e'
        k = (k + 1) % m
    return c == 2


_PIECES = {}


def piece_table(kinds):
    """t[i][j] = number of triangular pieces when the face is cut by the chord between elements i and j."""
    t = _PIECES.get(kinds)
    if t is None:
        m = len(kinds)
        t = _PIECES[kinds] = [[piece_tri(kinds, i, j) + piece_tri(kinds, j, i) if i != j else 0
                               for j in range(m)] for i in range(m)]
    return t


class Graph:
    """Face graph of a wiring word with precomputed one-line transitions."""

    def __init__(self, tokens, n):
        self.n = n
        self.tokens = tokens
        self.struct = X.build(tokens, n)
        faces, edges, verts, rows, vpos = self.struct
        self.faces = faces
        self.full = (1 << n) - 1
        self.bmask = [sum(1 << w for w in f['below']) for f in faces]
        self.by_below = {m: i for i, m in enumerate(self.bmask)}
        self._index = [None] * len(faces)
        self._tr = [None] * len(faces)
        self.tri_face = [f['bounded'] and f['nedges'] == 3 for f in faces]
        self._T0 = None

    @property
    def T0(self):
        if self._T0 is None:
            self._T0 = X.base_T(self.struct)
        return self._T0

    def index(self, fid):
        ix = self._index[fid]
        if ix is None:
            ix = self._index[fid] = {x: i for i, x in enumerate(self.faces[fid]['cyc'])}
        return ix

    def tr(self, fid):
        """(transitions, ends) of a face; transitions[ei] = [(nf, nei, gain, lines mask, xj, element)],
        ends[ei] = best gain of ending the line at an infinity of the face entered at ei."""
        t = self._tr[fid]
        if t is not None:
            return t
        faces, edges, verts = self.struct[0], self.struct[1], self.struct[2]
        cyc = faces[fid]['cyc']
        pt = piece_table(tuple(x[0] for x in cyc))
        g0 = -1 if self.tri_face[fid] else 0
        masks = []
        for x in cyc:
            if x[0] == 'inf':
                masks.append(None)
            elif x[0] == 'e':
                masks.append(1 << edges[x[1]][0])
            else:
                masks.append(sum(1 << w for w in verts[x[1]][0]))
        nxt = []
        for xj, x in enumerate(cyc):
            if x[0] == 'inf' or bin(masks[xj]).count('1') > 2:
                nxt.append(None)
            elif x[0] == 'e':
                w, bel, abv = edges[x[1]]
                nxt.append(abv if bel == fid else bel)
            else:
                nxt.append(verts[x[1]][1][fid])
        tf, ef = [], []
        for ei in range(len(cyc)):
            tl, best_end = [], NEG
            for xj, x in enumerate(cyc):
                if xj == ei:
                    continue
                g = g0 + pt[ei][xj]
                if x[0] == 'inf':
                    best_end = max(best_end, g)
                elif nxt[xj] is not None:
                    nf = nxt[xj]
                    tl.append((nf, self.index(nf)[x], g, masks[xj], xj, x))
            tf.append(tl)
            ef.append(best_end)
        t = self._tr[fid] = (tf, ef)
        return t

    def start_face(self, gap):
        """Face of the left end at `gap` (number of wires below), entry index 0 = its left infinity."""
        return 0 if gap == 0 else (1 if gap == self.n else gap + 1)

    def dp(self, gap):
        return Dp(self, self.start_face(gap), 0)


class Dp:
    """Best path values from (face, entry) to the antipodal face for one start.

    mode 'G': weight of a path = gain G (new triangles - base triangles cut); mode 'N': weight = G + D = number
    of triangles with a side on the new line (D = number of base triangles cut)."""

    def __init__(self, G, F, ei0, mode='G', bset=None):
        self.G, self.F, self.ei0 = G, F, ei0
        self.s0 = G.bmask[F]
        self.memo = {}
        self._byd = {}
        self._cnt = {}
        # per-face bonus: every triangle face (mode 'N'), or the faces of `bset`
        self.bonus = G.tri_face if mode == 'N' else [False] * len(G.faces)
        if bset is not None:
            self.bonus = [f in bset for f in range(len(G.faces))]
        self.val = self.best(F, ei0)

    def best(self, fid, ei):
        key = (fid, ei)
        m = self.memo.get(key)
        if m is not None:
            return m
        G = self.G
        C = self.s0 ^ G.bmask[fid]
        b = NEG
        tf, ef = G.tr(fid)
        bo = self.bonus[fid]
        if C == G.full and ef[ei] > NEG:
            b = ef[ei] + bo
        for nf, nei, g, lm, xj, x in tf[ei]:
            if lm & C:
                continue
            v = self.best(nf, nei)
            if v > NEG and v + g + bo > b:
                b = v + g + bo
        self.memo[key] = b
        return b

    def paths(self, thr):
        """Yield (weight, G, element sequence) of every path with weight >= thr (thr may be a callable, re-read at
        every node so that an improving incumbent prunes the running enumeration)."""
        G = self.G
        seq = []
        cb = thr if callable(thr) else (lambda: thr)

        fs = [self.F]

        def rec(fid, ei, acc, accg):
            C = self.s0 ^ G.bmask[fid]
            tf, ef = G.tr(fid)
            bo = self.bonus[fid]
            if C == G.full:
                e = ef[ei]
                if e > NEG and acc + e + bo >= cb():
                    yield acc + e + bo, accg + e, list(seq), list(fs)
            for nf, nei, g, lm, xj, x in tf[ei]:
                if lm & C:
                    continue
                v = self.best(nf, nei)
                if v > NEG and acc + g + bo + v >= cb():
                    seq.append(x)
                    fs.append(nf)
                    yield from rec(nf, nei, acc + g + bo, accg + g)
                    fs.pop()
                    seq.pop()
        yield from rec(self.F, self.ei0, 0, 0)

    def byd(self, fid, ei):
        """{D: best gain G of a completion from (fid, ei) that cuts exactly D base triangles from fid on}."""
        key = (fid, ei)
        r = self._byd.get(key)
        if r is not None:
            return r
        G = self.G
        C = self.s0 ^ G.bmask[fid]
        tf, ef = G.tr(fid)
        d0 = 1 if G.tri_face[fid] else 0
        r = {}
        if C == G.full and ef[ei] > NEG:
            r[d0] = ef[ei]
        for nf, nei, g, lm, xj, x in tf[ei]:
            if lm & C:
                continue
            for d, v in self.byd(nf, nei).items():
                if r.get(d + d0, NEG) < v + g:
                    r[d + d0] = v + g
        self._byd[key] = r
        return r

    def by_d(self):
        """{D: best gain G among paths cutting exactly D base triangles}."""
        return self.byd(self.F, self.ei0)

    def paths_gd(self, cond):
        """Yield (G, D, element sequence, faces) of every path whose (G, D) satisfies cond(G, D) (cond must be
        nondecreasing in G).  A node is expanded only if some completion satisfies cond, so no dead leaves."""
        G = self.G
        seq = []
        fs = [self.F]

        def rec(fid, ei, accg, accd):
            C = self.s0 ^ G.bmask[fid]
            tf, ef = G.tr(fid)
            d0 = 1 if G.tri_face[fid] else 0
            if C == G.full and ef[ei] > NEG and cond(accg + ef[ei], accd + d0):
                yield accg + ef[ei], accd + d0, list(seq), list(fs)
            for nf, nei, g, lm, xj, x in tf[ei]:
                if lm & C:
                    continue
                sub = self.byd(nf, nei)
                a2, d2 = accg + g, accd + d0
                if any(cond(a2 + v, d2 + d) for d, v in sub.items()):
                    seq.append(x)
                    fs.append(nf)
                    yield from rec(nf, nei, a2, d2)
                    fs.pop()
                    seq.pop()
        yield from rec(self.F, self.ei0, 0, 0)

    def count_ge(self, thr):
        """Number of paths with gain >= thr (DP over (state, remaining needed))."""
        G = self.G
        memo = self._cnt

        def cnt(fid, ei, need):
            key = (fid, ei, need)
            r = memo.get(key)
            if r is not None:
                return r
            C = self.s0 ^ G.bmask[fid]
            r = 0
            tf, ef = G.tr(fid)
            bo = self.bonus[fid]
            if C == G.full:
                e = ef[ei]
                if e > NEG and e + bo >= need:
                    r += 1
            for nf, nei, g, lm, xj, x in tf[ei]:
                if lm & C:
                    continue
                v = self.best(nf, nei)
                if v > NEG and g + bo + v >= need:
                    r += cnt(nf, nei, need - g - bo)
            memo[key] = r
            return r
        return cnt(self.F, self.ei0, thr)


# ---- interaction bound: brute force over chord pairs inside one face ------------------------------------------
def _arc_edges(cyc, u, w):
    """Edge sides on the boundary arc from point u to point w (points are (element, offset); increasing index);
    None when the arc meets infinity (the piece is unbounded)."""
    m = len(cyc)
    eu, ew = u[0], w[0]
    if cyc[eu][0] == 'inf' or cyc[ew][0] == 'inf':
        return None
    if eu == ew and u[1] < w[1]:
        return 1 if cyc[eu][0] == 'e' else 0
    c = (cyc[eu][0] == 'e') + (cyc[ew][0] == 'e')
    k = (eu + 1) % m
    while k != ew:
        if cyc[k][0] == 'inf':
            return None
        c += cyc[k][0] == 'e'
        k = (k + 1) % m
    return c


def _piece(cyc, chord_sides, arcs):
    tot = chord_sides
    for u, w in arcs:
        e = _arc_edges(cyc, u, w)
        if e is None:
            return 0
        tot += e
    return 1 if tot == 3 else 0


def _tau1(cyc, p, q):
    return _piece(cyc, 1, [(p, q)]) + _piece(cyc, 1, [(q, p)])


def _tau2(cyc, c, d):
    """Triangular pieces of a face cut by chords c=(p,q), d=(r,s) (points (element, offset)); kind of the pair."""
    shared = [(i, j) for i in range(2) for j in range(2) if c[i] == d[j]]
    if shared:                                           # the chords end at a common point of an edge
        i, j = shared[0]
        x, a, b = c[i], c[1 - i], d[1 - j]
        cp = lambda t: ((t[0] - x[0]) % len(cyc), t[1])
        if cp(a) > cp(b):
            a, b = b, a
        return _piece(cyc, 1, [(x, a)]) + _piece(cyc, 2, [(a, b)]) + _piece(cyc, 1, [(b, x)]), 'touch'
    pts = [c[0], c[1], d[0], d[1]]
    P = sorted(range(4), key=lambda i: pts[i])
    order = ['c' if i < 2 else 'd' for i in P]
    seq = [pts[i] for i in P]
    if order in (['c', 'd', 'c', 'd'], ['d', 'c', 'd', 'c']):
        return sum(_piece(cyc, 2, [(seq[k], seq[(k + 1) % 4])]) for k in range(4)), 'cross'
    for r in range(4):
        rot = [order[(r + k) % 4] for k in range(4)]
        if rot[0] == rot[1] and rot[2] == rot[3]:
            s_ = [seq[(r + k) % 4] for k in range(4)]
            return (_piece(cyc, 1, [(s_[0], s_[1])]) + _piece(cyc, 1, [(s_[2], s_[3])])
                    + _piece(cyc, 2, [(s_[1], s_[2]), (s_[3], s_[0])])), 'none'
    raise AssertionError


def face_interaction(cyc, tri_f, masks):
    """Max over valid chord pairs (c, d) in one face of I_f = tau(c, d) - tau(c) - tau(d) + [f is a triangle], per
    kind: 'cross' (chords cross inside), 'touch' (share an endpoint on an edge = the crossing L1 x L2), 'none'.
    masks[k]: line mask of element k (0 for infinity; elements of a triple point are not usable as endpoints)."""
    m = len(cyc)
    elems = [k for k in range(m) if cyc[k][0] == 'inf' or bin(masks[k]).count('1') <= 2]
    chords = [(a, b) for a in elems for b in elems if a < b and not (masks[a] & masks[b])]
    best = {'cross': NEG, 'touch': NEG, 'none': NEG}
    for c in chords:
        for d in chords:
            share = sorted(set(c) & set(d))
            if any(cyc[e][0] == 'v' for e in share):     # both new lines through one base vertex: 4-fold
                continue
            opts = [(-1, 0, 1) if cyc[e][0] == 'e' else (-1, 1) for e in share]
            for offs in product(*opts):
                od = dict(zip(share, offs))
                cc = ((c[0], 0), (c[1], 0))
                dd = ((d[0], od.get(d[0], 0)), (d[1], od.get(d[1], 0)))
                if set(cc) == set(dd):
                    continue
                t, kind = _tau2(cyc, cc, dd)
                val = t - _tau1(cyc, *cc) - _tau1(cyc, *dd) + (1 if tri_f else 0)
                if val > best[kind]:
                    best[kind] = val
    return best


_INTER_CACHE = {}


def interaction_bound(G):
    """(Kx, ok): I <= Kx + (number of base triangles cut by both lines), proved for every face of G by brute force:
    'none'-kind pairs give at most [f triangle] (checked: ok), the single crossing point L1 x L2 gives at most
    Kx = max(max cross, 2 * max touch) (a touching point lies on an edge, hence in two faces)."""
    faces, edges, verts = G.struct[0], G.struct[1], G.struct[2]
    cross = touch = 0
    ok = True
    for fid, f in enumerate(faces):
        cyc = f['cyc']
        masks = []
        for x in cyc:
            masks.append(0 if x[0] == 'inf' else (1 << edges[x[1]][0] if x[0] == 'e'
                                                   else sum(1 << w for w in verts[x[1]][0])))
        canon = {}
        key = (G.tri_face[fid], tuple(
            (x[0], tuple(sorted(canon.setdefault(w, len(canon)) for w in range(G.n) if masks[k] >> w & 1)))
            for k, x in enumerate(cyc)))
        r = _INTER_CACHE.get(key)
        if r is None:
            r = _INTER_CACHE[key] = face_interaction(cyc, G.tri_face[fid], masks)
        cross, touch = max(cross, r['cross']), max(touch, r['touch'])
        ok = ok and r['none'] <= (1 if G.tri_face[fid] else 0)
    return max(cross, 2 * touch), ok


def rows_to_tokens(rows, init):
    """Wiring word (tokens (slot, width)) of an arrangement given by event rows and its left-to-right start order."""
    N = len(rows)
    order = list(init)
    pos = [0] * N
    left = sum(len(r) for r in rows)
    tokens = []
    nxt = lambda w: rows[w][pos[w]] if pos[w] < len(rows[w]) else None
    s = 0
    while left:
        progressed = False
        for s in range(N - 1):
            u, v = order[s], order[s + 1]
            ru = nxt(u)
            if ru is None or v not in ru:
                continue
            if len(ru) == 1:
                if nxt(v) == frozenset([u]):
                    order[s], order[s + 1] = v, u
                    pos[u] += 1
                    pos[v] += 1
                    left -= 2
                    tokens.append((s, 2))
                    progressed = True
                    break
            elif len(ru) == 2 and s + 2 < N:
                w = order[s + 2]
                if ru == frozenset([v, w]) and nxt(v) == frozenset([u, w]) and nxt(w) == frozenset([u, v]):
                    order[s], order[s + 2] = w, u
                    for x in (u, v, w):
                        pos[x] += 1
                    left -= 3
                    tokens.append((s, 3))
                    progressed = True
                    break
        assert progressed, "rows do not form a wiring diagram"
    return tokens


def extend_graph(G, seq, gap):
    """Graph of base + one new line following `seq` from left gap `gap` (new line label n)."""
    n = G.n
    rows = X.path_rows(G.struct, n, seq)
    init = list(range(gap)) + [n] + list(range(gap, n))
    return Graph(rows_to_tokens(rows, init), n + 1), rows


def word_tokens(gens):
    return X.parse_tokens(gens)


def word_n(tokens):
    return max(g + w for g, w in tokens)


# ---- two-line search ------------------------------------------------------------------------------------------
class Base:
    """A base arrangement with cached one-line DPs and its interaction constant."""

    def __init__(self, gens=None, tokens=None, n=None):
        self.tokens = tokens if tokens is not None else word_tokens(gens)
        self.n = n if n is not None else word_n(self.tokens)
        self.G = Graph(self.tokens, self.n)
        self.T0 = self.G.T0
        self.Kx, ok = interaction_bound(self.G)
        assert ok, "interaction bound failed on a base face"
        self._dp = {}
        self._f2 = {}
        self.evals = self.pruned1 = self.pruned2 = 0

    def dp(self, gap, mode):
        d = self._dp.get((gap, mode))
        if d is None:
            d = self._dp[gap, mode] = Dp(self.G, self.G.start_face(gap), 0, mode)
        return d

    def by_d(self, gap):
        d = self._dp.get((gap, 'D'))
        if d is None:
            d = self._dp[gap, 'D'] = self.dp(gap, 'G').by_d()
        return d

    def partner_gain(self, gap, seq, partner_gap):
        """Best gain of one more line (left gap `partner_gap` of base + new line) after new line `seq`."""
        self.evals += 1
        G1, _ = extend_graph(self.G, seq, gap)
        return Dp(G1, G1.start_face(partner_gap), 0).val


def pair_search(B, r1, r2, target=None, warm=True):
    """Best T over placements of two lines at final ranks r1 < r2.  With `target`: returns (T, witness) for the
    best placement found with T >= target, or (None, None) when every placement has T < target.

    Bound used (proved in the module docstring): T <= T0 + Kx + G1 + G2 + min(D1, D2).  Hence, with X = T* - T0 - Kx
    (T* = incumbent + 1), any improving pair has  N1 + G2 >= X  and  G1 + N2 >= X  (N = G + D), and for the
    enumerated line e:  G_e + max_d(bestG_f[d] + min(D_e, d)) >= X.  Every improving pair either has N_e >= a
    (pass A: enumerate line e in the base) or G_f >= X - a + 1 (pass B: enumerate line f); each enumerated line is
    completed by the exact one-line DP on base + that line."""
    T0, Kx = B.T0, B.Kx
    gaps = {1: r1, 2: r2 - 1}                     # base gap of each line if it is enumerated in the base
    pgap = {1: r2, 2: r1}                         # gap of the other line in base + the enumerated one
    MG = {k: B.dp(gaps[k], 'G').val for k in (1, 2)}
    MN = {k: B.dp(gaps[k], 'N').val for k in (1, 2)}
    st = {'inc': (target - 1) if target is not None else -1, 'best': None}

    def X():
        return st['inc'] + 1 - T0 - Kx

    def ub():
        return T0 + Kx + min(MN[1] + MG[2], MG[1] + MN[2])

    def f2(o):
        """f2[D] = max_d (bestG_o[d] + min(D, d)): best G_o + shared triangles when the other line cuts D."""
        t = B._f2.get(gaps[o])
        if t is None:
            bd = B.by_d(gaps[o])
            t = B._f2[gaps[o]] = [max(v + min(D, d) for d, v in bd.items()) for D in range(max(bd) + 1)]
        return lambda D: t[min(D, len(t) - 1)]

    def evaluate(k, g, seq, fs):
        tri_faces = frozenset(f for f in fs if B.G.tri_face[f])
        need = st['inc'] + 1 - T0 - Kx - g                     # the other line must reach G_o + S >= need
        if Dp(B.G, B.G.start_face(gaps[3 - k]), 0, 'S', tri_faces).val < need:
            B.pruned2 += 1
            return
        v = B.partner_gain(gaps[k], seq, pgap[k])
        if v > NEG and T0 + g + v > st['inc']:
            st['inc'], st['best'] = T0 + g + v, (k, seq)

    def result():
        return (st['inc'], st['best']) if st['best'] is not None else (None, None)
    if ub() < st['inc'] + 1:
        return None, None
    if warm and target is None:
        for k in (1, 2):
            for i, (w, g, seq, fs) in enumerate(B.dp(gaps[k], 'G').paths(MG[k] - 1)):
                evaluate(k, g, seq, fs)
                if i >= 300:
                    break
        if ub() < st['inc'] + 1:
            return result()
    plan = None
    x = X()
    for e, f in ((1, 2), (2, 1)):
        dN, dG = B.dp(gaps[e], 'N'), B.dp(gaps[f], 'G')
        for a in range(max(1, (x + 1) // 2 - 2), (x + 1) // 2 + 3):
            lo_a, lo_b = max(a, x - MG[f]), max(x - a + 1, x - MN[e])
            cost = (dN.count_ge(lo_a) if lo_a <= MN[e] else 0) + (dG.count_ge(lo_b) if lo_b <= MG[f] else 0)
            if plan is None or cost < plan[0]:
                plan = (cost, e, f, a)
    cost, e, f, a = plan
    f2f, f2e = f2(f), f2(e)
    condA = lambda g, d: g + d >= max(a, X() - MG[f]) and g + f2f(d) >= X()
    condB = lambda g, d: g >= max(X() - a + 1, X() - MN[e]) and g + f2e(d) >= X()
    for g, d, seq, fs in B.dp(gaps[e], 'G').paths_gd(condA):
        evaluate(e, g, seq, fs)
        if target is not None and st['best'] is not None:
            return result()
    for g, d, seq, fs in B.dp(gaps[f], 'G').paths_gd(condB):
        evaluate(f, g, seq, fs)
        if target is not None and st['best'] is not None:
            return result()
    return result()


def witness_rows(B, r1, r2, best):
    """Event rows of the (n0+2)-line arrangement of a `pair_search` witness (for an independent recount)."""
    k, seq = best
    gap = r1 if k == 1 else r2 - 1
    pg = r2 if k == 1 else r1
    G1, _ = extend_graph(B.G, seq, gap)
    d = Dp(G1, G1.start_face(pg), 0)
    seq2 = next(iter(d.paths(d.val)))[2]
    return X.path_rows(G1.struct, B.n + 1, seq2)


def load_words(path):
    """[(name, gens)] from a gallery JSON, a JSON list of such records, or a text file with one word per line."""
    txt = Path(path).read_text()
    try:
        j = json.loads(txt)
    except ValueError:
        return [(f"{Path(path).name}:{i}", ln) for i, ln in enumerate(txt.splitlines()) if ln.strip()]
    recs = j if isinstance(j, list) else [j]
    return [(r.get("name", f"{Path(path).name}:{i}"), r["gens"]) for i, r in enumerate(recs)]


def cmd_max2(args):
    words = load_words(args.input)[:args.limit]
    out = open(args.out, "w") if args.out else None
    for name, gens in words:
        t0 = time.time()
        B = Base(gens)
        n0 = B.n
        pairs = list(combinations(range(n0 + 2), 2))
        if args.ranks:
            pairs = [tuple(int(x) for x in args.ranks.split(","))]
        overall = None
        for r1, r2 in pairs:
            t1 = time.time()
            T, best = pair_search(B, r1, r2, target=args.target)
            if args.verify and best is not None:
                got = X.count_triangles(witness_rows(B, r1, r2, best))
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
        print(f"{name}: n0={n0} T0={B.T0} Kx={B.Kx} pairs={len(pairs)} overall {what}: "
              f"{overall if overall is not None else 'none (all placements below target)'}  "
              f"[{time.time() - t0:.1f}s, exact partner evals {B.evals}, pruned {B.pruned1}+{B.pruned2}]", flush=True)
    if out:
        out.close()


def selftest():
    """Brute force (all first-line paths x exact second line) vs pruned search on small gallery bases, and vs SAT."""
    import glob
    sys.path.insert(0, str(ROOT / "work/lns/push"))
    from run_lns import chi_from_word
    from fastext import Ext
    bad = 0
    for n0, nb in ((6, 2), (8, 1)):
        fs = sorted(glob.glob(str(ROOT / f"tools/external/kobon-solutions/gallery/data/{n0}/*.json")))[:nb]
        for f in fs:
            gens = json.load(open(f))["gens"]
            B = Base(gens)
            chi0 = chi_from_word(gens, n0)
            for r1, r2 in combinations(range(n0 + 2), 2):
                T, _ = pair_search(B, r1, r2)
                d = B.dp(r1, 'G')
                brute = -1
                for w, g1, seq, fs_ in d.paths(-99):
                    G1, _ = extend_graph(B.G, seq, r1)
                    v = Dp(G1, G1.start_face(r2), 0).val
                    if v > NEG:
                        brute = max(brute, B.T0 + g1 + v)
                ok = T == brute
                if n0 == 6:
                    sat = lambda t: any(Ext(chi0, n0, (r1, r2), s, t, n=n0 + 2).solve() is not None for s in (1, -1))
                    ok = ok and sat(T) and not sat(T + 1)
                bad += not ok
                if not ok:
                    print("MISMATCH", n0, f, r1, r2, T, brute)
    print("selftest:", "FAILED %d" % bad if bad else "ok (pruned == brute force; n0=6 also == SAT max, UNSAT at max+1)")
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("max2", help="exact two-line extension maximum per rank pair")
    m.add_argument("input")
    m.add_argument("--ranks", help="r1,r2 (final slope ranks 0..n0+1, r1 < r2); default all pairs")
    m.add_argument("--target", type=int, help="only decide whether some placement reaches T (faster)")
    m.add_argument("--limit", type=int, default=10 ** 9, help="use only the first K words of INPUT")
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

"""T28: pinned SAT for the flower cases of a hypothetical 94 (n = 18, multiplicity <= 3).

Structure being encoded (work/bbl/THEORY.md section 21 and work/eng/T28_flower_sat.md):
  * Z = 0 (every bounded segment is a side of some triangle), so D = 3t - 6.
  * bridge components are flowers: centre O on lines m0,m1,m2 and corners P_i (i = 0..5)
    on m_{i mod 3}, l_{i-1}, l_i.  Triangles: inner (m_i, m_{i+1}, l_i), outer (l_{i-1}, l_i, l_{i+1})
    (star tip Y_i = l_{i-1} n l_{i+1}), and per corner exactly one "corner triangle":
        variant 1 (ring RRRNNB, ext l_{i-1} is the block):  (m_i, l_{i-1}, l_{i+1})
        variant 2 (ring RRRBNN, ext l_i is the block):      (m_i, l_i,     l_{i-2})
    (derivation: Z=0 forces ray 4 = ext m_i to be singly used, rays 3 / 5 lie on the outer triangles.)
  * case A: two flowers, 14 triple points.  case B: one flower + 3 X points (10 triple points).

Lines are *named* (0..17); the slope position of a name is a free permutation pi (variables X[a][p]),
so interleavings of the flowers at infinity are decided by the solver (or cubed by --fix name:pos).

    uv run --no-project --with python-sat python search/flower_sat.py --case A --chir1 000 --chir2 000 --dimacs out.cnf
"""
import argparse
import itertools
import json
import sys
import time
from itertools import combinations, permutations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "search"))
from kobon_sat import build_defect, count_general  # noqa: E402
from pysat.card import CardEnc, EncType  # noqa: E402

S = lambda *x: tuple(sorted(x))


# ------------------------------------------------------------------------------------------ words
def chi_from_word(gens, n):
    wires = list(range(n))
    slot_of = list(range(n))
    chi = {}
    for tok in gens.split():
        g = int(tok.rstrip("*"))
        w = 2 + tok.count("*")
        block = wires[g:g + w]
        for i, k in combinations(sorted(block), 2):
            for j in range(i + 1, k):
                chi[i, j, k] = 0 if j in block else (1 if g > slot_of[j] else -1)
        block.reverse()
        wires[g:g + w] = block
        for s in range(g, g + w):
            slot_of[wires[s]] = s
    return chi


def chi_to_word(n, chi):
    """Wiring-diagram word of the arrangement with chirotope chi (values -1/0/1, sorted triples).

    Along line r, i's crossing precedes j's iff chi(sorted r,i,j) == -1 for i < j (+1 for i > j) in the SAT convention;
    the wiring word built here satisfies chi_from_word(word) == chi, which is the negation of that reading (both are
    the same arrangement up to a 180-degree rotation).
    Returns the gens string (tokens 'g', 'g*' for a triple point) or None when the sweep gets stuck.
    """
    def before(r, i, j):  # i's crossing strictly before j's on r
        v = chi[tuple(sorted((r, i, j)))]
        return v == (1 if i < j else -1)

    pts = {}
    seq = []
    for r in range(n):
        others = [x for x in range(n) if x != r]
        rank = {i: sum(1 for j in others if j != i and before(r, j, i)) for i in others}
        groups = {}
        for i in others:
            groups.setdefault(rank[i], []).append(i)
        order = []
        for k in sorted(groups):
            g = groups[k]
            if len(g) == 1:
                order.append(frozenset((r, g[0])))
            elif len(g) == 2:
                order.append(frozenset((r, g[0], g[1])))
            else:
                return None
        seq.append(order)
    idx = [0] * n
    wires = list(range(n))
    toks = []
    while True:
        progressed = False
        for g in range(n - 1):
            a = wires[g]
            if idx[a] >= len(seq[a]):
                continue
            pt = seq[a][idx[a]]
            w = len(pt)
            if g + w > n:
                continue
            block = wires[g:g + w]
            if set(block) != set(pt):
                continue
            if any(idx[x] >= len(seq[x]) or seq[x][idx[x]] != pt for x in block):
                continue
            toks.append(str(g) + "*" * (w - 2))
            wires[g:g + w] = block[::-1]
            for x in block:
                idx[x] += 1
            progressed = True
            break
        if not progressed:
            break
    if any(idx[r] != len(seq[r]) for r in range(n)):
        return None
    return " ".join(toks)


# ------------------------------------------------------------------------------------------ flowers
class Flower:
    """Names of one flower: m[0..2], l[0..5] are integer line names."""

    def __init__(self, base):
        self.m = [base + i for i in range(3)]
        self.l = [base + 3 + i for i in range(6)]

    @property
    def lines(self):
        return self.m + self.l

    def M(self, i):
        return self.m[i % 3]

    def L(self, i):
        return self.l[i % 6]

    def O(self):
        return S(*self.m)

    def P(self, i):
        return S(self.M(i), self.L(i - 1), self.L(i))

    def points(self):
        return [self.O()] + [self.P(i) for i in range(6)]

    def inner(self, i):
        return S(self.M(i), self.M(i + 1), self.L(i))

    def outer(self, i):
        return S(self.L(i - 1), self.L(i), self.L(i + 1))

    def corner(self, i, v):
        """corner triangle at P_i; v = 1: block on ext l_{i-1}; v = 2: block on ext l_i"""
        return S(self.M(i), self.L(i - 1), self.L(i + 1)) if v == 1 else S(self.M(i), self.L(i), self.L(i - 2))

    def fixed_triangles(self):
        return [self.inner(i) for i in range(6)] + [self.outer(i) for i in range(6)]


def chir_bits(s):
    """'011' -> per-corner variants (1 or 2) for corners 0..5 (antipodal corners equal)."""
    b = [1 + int(c) for c in s]
    return b + b


# ------------------------------------------------------------------------------------------ model
def build_light(n, k):
    """Skeleton model: signotope axioms with concurrency (no 4-fold points), tri variables with the 'no other line separates
    the vertices' definition, exactly k triple points.  No adjacency / Z / count machinery (about 5x smaller)."""
    from itertools import product
    from kobon_sat import allowed4
    from pysat.formula import CNF, IDPool
    pool = IDPool()
    trip = list(combinations(range(n), 3))
    z = {t: pool.id(("zero",) + t) for t in trip}
    pz = {t: pool.id(("pos",) + t) for t in trip}
    ng = {t: pool.id(("neg",) + t) for t in trip}
    tri = {t: pool.id(("tri",) + t) for t in trip}
    cnf = CNF()
    for t in trip:
        cnf.extend([[z[t], pz[t], ng[t]], [-z[t], -pz[t]], [-z[t], -ng[t]], [-pz[t], -ng[t]]])
    is_val = lambda t, v: {0: z, 1: pz, -1: ng}[v][t]
    allowed = allowed4()
    for a, b, c, d in combinations(range(n), 4):
        ts = [(b, c, d), (a, c, d), (a, b, d), (a, b, c)]
        for v in product((-1, 0, 1), repeat=4):
            if v in allowed and v != (0, 0, 0, 0):
                continue
            cnf.append([-is_val(t, val) for t, val in zip(ts, v)])
    for (i, j, k3), tv in tri.items():
        cnf.append([-tv, -z[i, j, k3]])
        for l in range(n):
            if l in (i, j, k3):
                continue
            verts = [(i, j), (i, k3), (j, k3)]
            for (u1, u2), (w1, w2) in product(verts, verts):
                if (u1, u2) == (w1, w2):
                    continue
                clause = [-tv]
                for (x1, x2), want in (((u1, u2), 1), ((w1, w2), -1)):
                    a3, b3, c3 = sorted((x1, x2, l))
                    val = want if l == b3 else -want
                    clause.append(-is_val((a3, b3, c3), val))
                cnf.append(clause)
    if k is not None:
        cnf.extend(CardEnc.equals(lits=list(z.values()), bound=k, vpool=pool, encoding=EncType.cardnetwrk).clauses)
    cnf.append([-ng[0, 1, 2]])
    cnf.pool = pool
    return cnf, z, pz, ng, tri, 0


class Model:
    def __init__(self, n=18, k=14, target=94, z0=True, card="cardnetwrk", alternate=True, light=False):
        self.n = n
        if light:
            cnf, z, pz, ng, tri, budget = build_light(n, k)
            z0 = False
        else:
            cnf, z, pz, ng, tri, budget = build_defect(n, target, k, alternate=alternate, card=card, exact_triple=True, blanc=False)
        self.cnf, self.z, self.pz, self.ng, self.tri, self.budget = cnf, z, pz, ng, tri, budget
        self.pool = cnf.pool
        self.trip = list(z)
        self.A = lambda r, i, j: self.pool.id(("adj", r, i, j))
        self.X = None
        self.loc_cache = {}
        if z0:
            self.add_z0()

    def add_z0(self):
        """Z = 0: every consecutive pair (i, j) on r is a side of a triangle through its endpoints.

        H(r,i,y) = exists x: z(r,i,x) and tri(r,x,y)  (segment from i's point toward y, seen from i's end);
        used(r,i,j) = tri(r,i,j) or H(r,i,j) or H(r,j,i) or exists y: z(r,j,y) and H(r,i,y).
        Same semantics as the usedvia_* clauses of search/build_k6z.py (C14), with fewer auxiliaries."""
        cnf, pool, z, tri, A, n = self.cnf, self.pool, self.z, self.tri, self.A, self.n
        H = {}
        for r, i, y in permutations(range(n), 3):
            h = pool.id(("H", r, i, y))
            H[r, i, y] = h
            ors = [-h]
            for x in range(n):
                if x in (r, i, y):
                    continue
                w = pool.id(("W", r, i, x, y))
                cnf.extend([[-w, z[S(r, i, x)]], [-w, tri[S(r, x, y)]]])
                ors.append(w)
            cnf.append(ors)
        for r, i, j in permutations(range(n), 3):
            lits = [-A(r, i, j), tri[S(r, i, j)], H[r, i, j], H[r, j, i]]
            for y in range(n):
                if y in (r, i, j):
                    continue
                v = pool.id(("V", r, i, j, y))
                cnf.extend([[-v, z[S(r, j, y)]], [-v, H[r, i, y]]])
                lits.append(v)
            cnf.append(lits)

    # ---- permutation variables
    def add_pi(self):
        n, cnf, pool = self.n, self.cnf, self.pool
        self.X = [[pool.id(("X", a, p)) for p in range(n)] for a in range(n)]
        for a in range(n):
            cnf.append(list(self.X[a]))
            for p, q in combinations(range(n), 2):
                cnf.append([-self.X[a][p], -self.X[a][q]])
        for p in range(n):
            cnf.append([self.X[a][p] for a in range(n)])
            for a, b in combinations(range(n), 2):
                cnf.append([-self.X[a][p], -self.X[b][p]])

    def loc(self, T):
        """loc[t] for a named triple T: implied by the positions of T's lines."""
        T = S(*T)
        if T in self.loc_cache:
            return self.loc_cache[T]
        a, b, c = T
        X, cnf, pool = self.X, self.cnf, self.pool
        d = {t: pool.id(("loc",) + T + t) for t in self.trip}
        for p, q, r in permutations(range(self.n), 3):
            cnf.append([-X[a][p], -X[b][q], -X[c][r], d[S(p, q, r)]])
        self.loc_cache[T] = d
        return d

    def pin_point(self, T):
        d = self.loc(T)
        for t, v in d.items():
            self.cnf.append([-v, self.z[t]])

    def pin_tri_lit(self, T):
        """aux literal nt with nt -> tri at the positions of T"""
        d = self.loc(T)
        nt = self.pool.id(("nt",) + S(*T))
        # nt & loc[t] -> tri[t]; loc is one-directional, so use X directly for soundness
        a, b, c = S(*T)
        X = self.X
        for p, q, r in permutations(range(self.n), 3):
            self.cnf.append([-nt, -X[a][p], -X[b][q], -X[c][r], self.tri[S(p, q, r)]])
        return nt

    def add_flower(self, fl, chir=None, rays=True, tips=True, tip_exclude=()):
        """chir: list of 6 per-corner variants (1/2), or None = free (solver chooses)."""
        cnf = self.cnf
        for P in fl.points():
            self.pin_point(P)
        for T in fl.fixed_triangles():
            cnf.append([self.pin_tri_lit(T)])
        self.corner_vars = getattr(self, "corner_vars", {})
        for i in range(6):
            t1, t2 = self.pin_tri_lit(fl.corner(i, 1)), self.pin_tri_lit(fl.corner(i, 2))
            if chir is None:
                cnf.append([t1, t2])
            else:
                cnf.append([t1 if chir[i] == 1 else t2])
        if rays:
            for i in range(6):
                P = fl.P(i)
                self.forbid_double(P, fl.M(i), (fl.M(i + 1), fl.M(i + 2)))
                if chir is not None:
                    if chir[i] == 1:   # block on ext l_{i-1}; ext l_i is a plain ray
                        self.forbid_double(P, fl.L(i), (fl.M(i + 1), fl.L(i + 1)))
                    else:              # block on ext l_i
                        self.forbid_double(P, fl.L(i - 1), (fl.M(i - 1), fl.L(i - 2)))
        if tips and chir is not None and rays:
            self.add_tips(fl, chir, tips=[j for j in range(6) if j not in tip_exclude])
        return

    def dbl(self, r, i, i2, w):
        """var <-> tri(r,i,w) and tri(r,i2,w): both triangles on the segment of r from the point r n i (= r n i2, when
        concurrent) to the crossing of w (a doubly used segment when this is true and the segment is adjacent)."""
        if i > i2:
            i, i2 = i2, i
        key = (r, i, i2, w)
        d = self.__dict__.setdefault("dblv", {})
        if key not in d:
            v = self.pool.id(("dbl",) + key)
            t1, t2 = self.tri[S(r, i, w)], self.tri[S(r, i2, w)]
            self.cnf.extend([[-v, t1], [-v, t2], [v, -t1, -t2]])
            d[key] = v
        return d[key]

    def forbid_double(self, T, a, exempt=(), extra=()):
        """At the named triple point T, the two segments of line a leaving T are not both sides of two triangles,
        except toward a next line in `exempt` (the bridge partners).  Sound for a 94: with Z = 0 and D = 3t - 6, the
        doubly used segments are exactly the designated ones."""
        T = S(*T)
        loc = self.loc(T)
        X, n = self.X, self.n
        for t in self.trip:
            for r in t:
                i, i2 = [x for x in t if x != r]
                for w in range(n):
                    if w in t:
                        continue
                    self.cnf.append([-loc[t], -X[a][r], -self.dbl(r, i, i2, w)] + [X[e][w] for e in exempt] + list(extra))

    def two_caps(self, r, i, i2):
        """shared guard var g: g -> at least two cap lines w with tri(r,i,w) and tri(r,i2,w)"""
        key = ("g2", r, i, i2)
        d = self.__dict__.setdefault("g2v", {})
        if key not in d:
            g = self.pool.id(key)
            caps = [self.dbl(r, i, i2, w) for w in range(self.n) if w not in (r, i, i2)]
            for cl in CardEnc.atleast(lits=caps, bound=2, vpool=self.pool, encoding=EncType.seqcounter).clauses:
                self.cnf.append([-g] + cl)
            d[key] = g
        return d[key]

    def add_xpoint(self, axis, b, c, rays=True):
        """X point (ring NNBNNB) on names axis, b, c with a given axis (both rays of the axis are blocks: two cap lines w
        with tri(axis,b,w), tri(axis,c,w); the other four rays are plain)."""
        sel = self.add_xpoint_free((axis, b, c), rays=rays)
        self.cnf.append([sel[axis]])
        return sel

    def add_xpoint_free(self, T, rays=True):
        T = S(*T)
        self.pin_point(T)
        n, cnf, pool, X = self.n, self.cnf, self.pool, self.X
        sel = {a: pool.id(("xsel",) + T + (a,)) for a in T}
        cnf.append(list(sel.values()))
        for u, v in combinations(T, 2):
            cnf.append([-sel[u], -sel[v]])
        self.__dict__.setdefault("xsel", {})[T] = sel
        for a in T:
            b, c = [x for x in T if x != a]
            for r in range(n):
                for i, i2 in combinations([x for x in range(n) if x != r], 2):
                    for bb, cc in ((i, i2), (i2, i)):
                        cnf.append([-sel[a], -X[a][r], -X[b][bb], -X[c][cc], self.two_caps(r, i, i2)])
            if rays:
                for x in (b, c):
                    self.forbid_double(T, x, (), extra=[sel[x]])
        return sel

    def before(self, r, i, j):
        """literal: on line r, the crossing with i is strictly before the crossing with j (kobon_sat convention)"""
        t = S(r, i, j)
        return self.ng[t] if i < j else self.pz[t]

    def ext_var(self, kind, L, R):
        """kind 'F': var -> L n R is the first vertex of L (no crossing before it); 'G': last vertex."""
        key = (kind, L, R)
        d = self.__dict__.setdefault("extv", {})
        if key not in d:
            v = self.pool.id(("ext",) + key)
            for M in range(self.n):
                if M in (L, R):
                    continue
                self.cnf.append([-v, -(self.before(L, M, R) if kind == "F" else self.before(L, R, M))])
            d[key] = v
        return d[key]

    def unbounded_at(self, a, b):
        """clause helper: literal list meaning 'the crossing of names a and b is an extreme vertex of line a'"""
        raise NotImplementedError

    def add_tips(self, fl, chir, tips=range(6)):
        """Star-tip constraints (Z = 0, single-use rays), tip Y_j = l_{j-1} n l_{j+1}, corner variants (v_j, v_{j+1}):
          (1,2): nothing;  (1,1): Y_j is an extreme vertex of l_{j-1};  (2,2): extreme vertex of l_{j+1};
          (2,1): extreme on both lines, or an 'opposite' triangle (l_{j-1}, l_{j+1}, w), w != l_j."""
        n, X, cnf = self.n, self.X, self.cnf
        for j in tips:
            a, b, mid = fl.L(j - 1), fl.L(j + 1), fl.L(j)
            v0, v1 = chir[j % 6], chir[(j + 1) % 6]
            for r in range(n):
                for q in range(n):
                    if r == q:
                        continue
                    pre = [-X[a][r], -X[b][q]]
                    ext_a = [self.ext_var("F", r, q), self.ext_var("G", r, q)]     # Y is extreme on a (a at r, b at q)
                    ext_b = [self.ext_var("F", q, r), self.ext_var("G", q, r)]
                    if (v0, v1) == (1, 1):
                        cnf.append(pre + ext_a)
                    elif (v0, v1) == (2, 2):
                        cnf.append(pre + ext_b)
                    elif (v0, v1) == (2, 1):
                        ov = self.pool.id(("otri", a, b, r, q))
                        opts = [tri for w, tri in ((w, self.tri[S(r, q, w)]) for w in range(n) if w not in (r, q))]
                        # ov -> exists w (not the position of the middle line l_j) with tri(r,q,w)
                        for w in range(n):
                            if w in (r, q):
                                continue
                        cnf.append(pre + ext_a + [ov])
                        cnf.append(pre + ext_b + [ov])
                        # ov: opposite triangle exists and the middle line is not w
                        cnf.append([-ov] + [self.opp_lit(r, q, w, mid) for w in range(n) if w not in (r, q)])

    def opp_lit(self, r, q, w, mid):
        """aux: tri(r,q,w) and line `mid` is not at position w"""
        key = ("opp", r, q, w, mid)
        d = self.__dict__.setdefault("oppv", {})
        if key not in d:
            v = self.pool.id(key)
            self.cnf.extend([[-v, self.tri[S(r, q, w)]], [-v, -self.X[mid][w]]])
            d[key] = v
        return d[key]

    def zp(self, u, v):
        """var -> the crossing of names/positions u, v is a triple point (positions)"""
        key = ("zp", min(u, v), max(u, v))
        d = self.__dict__.setdefault("zpv", {})
        if key not in d:
            x = self.pool.id(key)
            self.cnf.append([-x] + [self.z[S(u, v, w)] for w in range(self.n) if w not in (u, v)])
            for w in range(self.n):
                if w not in (u, v):
                    self.cnf.append([x, -self.z[S(u, v, w)]])
            d[key] = x
        return d[key]

    def add_block_lemma(self):
        """Z = 0 lemma for every block (segment of r from a triple point (r,i,i2) to a simple point Y = r n w, both
        triangles (r,i,w), (r,i2,w)): the segment of r beyond Y is absent (Y extreme on r) or a triangle uses it, and that
        triangle has the w-side [Y, i n w] or [Y, i2 n w] whose far end must then be a triple point.  So
        Y is extreme on r, or Y is a triple point (not simple), or i n w / i2 n w is a triple point."""
        n = self.n
        for t in self.trip:
            for r in t:
                i, i2 = [x for x in t if x != r]
                for w in range(n):
                    if w in t:
                        continue
                    self.cnf.append([-self.z[t], -self.dbl(r, i, i2, w), self.ext_var("F", r, w), self.ext_var("G", r, w),
                                     self.zp(r, w), self.zp(i, w), self.zp(i2, w)])

    def blk(self, r, s):
        """var -> a block on line r (triple point (r,i,i2), z true) whose far end is r n s and whose cap is s"""
        key = ("blk", r, s)
        d = self.__dict__.setdefault("blkv", {})
        if key not in d:
            v = self.pool.id(key)
            opts = []
            for t in self.trip:
                if r not in t or s in t:
                    continue
                i, i2 = [x for x in t if x != r]
                o = self.pool.id(("blko", r, s) + t)
                self.cnf.extend([[-o, self.z[t]], [-o, self.dbl(r, i, i2, s)]])
                opts.append(o)
            self.cnf.append([-v] + opts)
            d[key] = v
        return d[key]

    def add_end_lemmas(self):
        """Z = 0 facts about line ends for arrangements whose triple points are all type X (no ray is unbounded at a triple point):
          E5  an end vertex (first/last vertex of a line) is a simple point;
          E3  if r ends at Y = r n s and s does not end there, the segment of r before Y is a block (previous vertex is a triple
              point with axis r and cap s): 'I block';
          E2  the cap of such a block passes through Y (does not end there): 'exactly one line ends';
          E4  if both r and s end at Y (wedge), the bounded sector there is a triangle (r, s, w)."""
        n = self.n
        for r in range(n):
            for s in range(n):
                if r == s:
                    continue
                for kind in ("F", "G"):
                    e = self.ext_var(kind, r, s)
                    self.cnf.append([-e, -self.zp(r, s)])                                   # E5
                    o1, o2 = self.ext_var("F", s, r), self.ext_var("G", s, r)
                    self.cnf.append([-e, o1, o2, self.blk(r, s)])                           # E3
                    # wedge: triangle (r,s,w)
                    wlits = [self.tri[S(r, s, w)] for w in range(n) if w not in (r, s)]
                    self.cnf.append([-e, -o1] + wlits)
                    self.cnf.append([-e, -o2] + wlits)
        for t in self.trip:                                                                 # E2
            for r in t:
                i, i2 = [x for x in t if x != r]
                for w in range(n):
                    if w in t:
                        continue
                    d = self.dbl(r, i, i2, w)
                    for kind in ("F", "G"):
                        for kind2 in ("F", "G"):
                            self.cnf.append([-self.z[t], -d, -self.ext_var(kind, r, w), -self.ext_var(kind2, w, r)])

    def less(self, a, b):
        """clauses: position of name a < position of name b"""
        n, X = self.n, self.X
        for p in range(n):
            for q in range(p + 1):
                self.cnf.append([-X[a][p], -X[b][q]])

    def add_symbreak(self, chir1, chir2):
        """Naming automorphisms of the pinned structure (they do not change the arrangement):
        rotation by 3 (P_i -> P_{i+3}: l_i <-> l_{i+3}, m_j fixed) preserves every chirality vector;
        rotation by 1 (m_j -> m_{j+1}) also does when the vector is constant (000 / 111).
        Flower 1 is anchored by X[m_0][0] (its m_0 is the smallest-slope line), flower 2 has no anchor."""
        fls = self.flowers
        for k, fl in enumerate(fls):
            chir = (chir1, chir2)[k]
            self.less(fl.l[0], fl.l[3])
            if k == 1 and chir in ("000", "111"):
                self.less(fl.m[0], fl.m[1])
                self.less(fl.m[0], fl.m[2])

    def chi_from_model(self, model):
        ms = set(l for l in model if l > 0)
        return {t: (0 if self.z[t] in ms else (1 if self.pz[t] in ms else -1)) for t in self.z}

    def names_from_model(self, model):
        ms = set(l for l in model if l > 0)
        return {a: next(p for p in range(self.n) if self.X[a][p] in ms) for a in range(self.n)}


def build_case(case, chir1, chir2=None, k=None, free_chir=False, symmetry=True, z0=True, target=94, rays=True, symbreak=True, light=False):
    """case 'A': two flowers on names 0-8 / 9-17.  case 'B1': flower on 0-8 and X points {9,10,11},{12,13,14},{15,16,17}
    with axes 9, 12, 15 (disjoint from the flower)."""
    if case == "A":
        M = Model(18, 14 if k is None else k, target, z0=z0, light=light)
        M.add_pi()
        f1, f2 = Flower(0), Flower(9)
        M.add_flower(f1, None if free_chir else chir_bits(chir1), rays=rays)
        M.add_flower(f2, None if free_chir else chir_bits(chir2), rays=rays)
        M.flowers = [f1, f2]
    elif case == "B1":
        M = Model(18, 10 if k is None else k, target, z0=z0, light=light)
        M.add_pi()
        f1 = Flower(0)
        M.add_flower(f1, None if free_chir else chir_bits(chir1), rays=rays)
        M.flowers = [f1]
        M.xpoints = [(9, 10, 11), (12, 13, 14), (15, 16, 17)]
        for T in M.xpoints:
            M.add_xpoint(T[0], T[1], T[2], rays=rays)
    elif case == "B":
        raise ValueError("use build_B")
    else:
        raise ValueError(case)
    if symmetry:
        M.cnf.append([M.X[M.flowers[0].m[0]][0]])  # rotate so that m_0 of the first flower has the smallest slope
    if symbreak and not free_chir:
        M.add_symbreak(chir1, chir2)
    return M


def verify_model(M, model, out=None):
    chi = M.chi_from_model(model)
    found = count_general(M.n, chi)
    word = chi_to_word(M.n, chi)
    res = {"recount": len(found), "zeros": sum(1 for v in chi.values() if v == 0), "word": word}
    if word is not None:
        sys.path.append(str(ROOT / "work" / "t3"))
        from arr import Arr
        a = Arr(word, M.n)
        res["arr_T"] = a.T()
        res["word_chi_ok"] = chi_from_word(word, M.n) == chi
    res["names"] = M.names_from_model(model)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default="A", choices=["A", "B1"])
    ap.add_argument("--chir1", default="000")
    ap.add_argument("--chir2", default="000")
    ap.add_argument("--free-chir", action="store_true")
    ap.add_argument("--fix", default="", help="name:pos,... unit clauses on the permutation")
    ap.add_argument("--no-sym", action="store_true")
    ap.add_argument("--no-z0", action="store_true")
    ap.add_argument("--no-rays", action="store_true", help="omit the single-use constraints on the plain rays")
    ap.add_argument("--dimacs")
    ap.add_argument("--solver", default="cadical195")
    a = ap.parse_args()
    t0 = time.time()
    M = build_case(a.case, a.chir1, a.chir2, free_chir=a.free_chir, symmetry=not a.no_sym, z0=not a.no_z0, rays=not a.no_rays)
    for item in filter(None, a.fix.split(",")):
        nm, pos = item.split(":")
        M.cnf.append([M.X[int(nm)][int(pos)]])
    print(f"built {a.case} chir {a.chir1}/{a.chir2}: {M.cnf.nv} vars, {len(M.cnf.clauses)} clauses, {time.time()-t0:.1f}s", flush=True)
    if a.dimacs:
        M.cnf.to_file(a.dimacs)
        print("wrote", a.dimacs)
        return
    from pysat.solvers import Solver
    t1 = time.time()
    with Solver(name=a.solver, bootstrap_with=M.cnf.clauses) as s:
        sat = s.solve()
        el = time.time() - t1
        if not sat:
            print(json.dumps({"case": a.case, "chir1": a.chir1, "chir2": a.chir2, "fix": a.fix, "status": "UNSAT", "solve_s": round(el, 1)}))
            return
        res = verify_model(M, s.get_model())
        res.update({"case": a.case, "chir1": a.chir1, "chir2": a.chir2, "fix": a.fix, "status": "SAT", "solve_s": round(el, 1)})
        print(json.dumps(res))


if __name__ == "__main__":
    main()


def build_X6(z0=True, strong=True, anchor=True, target=94, light=False, k=6, triples=None, anchor_name=None, ends=True, flip_break=True):
    """Positional model (no line names) for k triple points that are ALL type X (ring NNBNNB), Z = 0, D = 3k - 6 = 12:
      * every triple point t has an axis (selector ax[t][r]): two cap lines (both rays of the axis are blocks with simple
        far ends); the two flank lines have both rays singly used (no bridges at all);
      * block lemma (strong form): for a block (r; i,i2; w) the segment beyond its far end Y is absent, or Y is triple, or
        i n w / i2 n w is a triple point V carrying a block on w toward Y (a 'mutual' pair);
      * line 0 avoids all triple points (some line does: every axis needs a non-extreme end, so two X points share a line).
    All are necessary for k = 6 (Sum c = 6, all X), Z = 0, D = 12."""
    M = Model(18, k, target, z0=z0, light=light)
    n, cnf, pool, z = M.n, M.cnf, M.pool, M.z
    if not flip_break:   # drop chi(0,1,2) != -1 (the 180-degree rotation break); needed when cubes are canonical under rotation
        brk = [-M.ng[0, 1, 2]]
        cnf.clauses.remove(brk)
    if triples is not None:
        M.add_pi()
        for T in triples:
            M.pin_point(T)
        if anchor_name is not None:
            cnf.append([M.X[anchor_name][0]])      # rotate so that this line has the smallest slope
        anchor = False
    ax = {}
    for t in M.trip:
        for r in t:
            ax[t, r] = pool.id(("ax",) + t + (r,))
        cnf.append([-z[t]] + [ax[t, r] for r in t])
        for r, r2 in combinations(t, 2):
            cnf.append([-ax[t, r], -ax[t, r2]])
        for r in t:
            i, i2 = [x for x in t if x != r]
            cnf.append([-ax[t, r], M.two_caps(r, i, i2)])
            for w in range(n):
                if w in t:
                    continue
                d = M.dbl(r, i, i2, w)
                cnf.append([-z[t], ax[t, r], -d])                       # flank rays are singly used
                cnf.append([-ax[t, r], -d, -M.zp(r, w)])                # axis rays: blocks have simple far ends
    # strong block lemma
    for t in M.trip:
        for r in t:
            i, i2 = [x for x in t if x != r]
            for w in range(n):
                if w in t:
                    continue
                lits = [-z[t], -M.dbl(r, i, i2, w), M.ext_var("F", r, w), M.ext_var("G", r, w), M.zp(r, w)]
                if strong:
                    for j, j2 in ((i, i2), (i2, i)):
                        # V = j n w is a triple point {w, j, u} and the ray of w from V toward Y is a block (caps r)
                        m = pool.id(("mut", r, j, w))
                        if ("mutdef", r, j, w) not in M.__dict__.setdefault("_mut", set()):
                            M._mut.add(("mutdef", r, j, w))
                            opts = []
                            for u in range(n):
                                if u in (r, j, w):
                                    continue
                                o = pool.id(("mutu", r, j, w, u))
                                cnf.extend([[-o, z[S(w, j, u)]], [-o, M.dbl(w, j, u, r)]])
                                opts.append(o)
                            cnf.append([-m] + opts)
                        lits.append(m)
                else:
                    lits += [M.zp(i, w), M.zp(i2, w)]
                cnf.append(lits)
    if anchor:
        for t in M.trip:
            if 0 in t:
                cnf.append([-z[t]])
    if ends:
        M.add_end_lemmas()
    return M


def build_B(chir1, xpoints, axes=None, symmetry=True, z0=True, rays=True, target=94, symbreak=False, light=False, tips=True, blocklemma=True):
    """Case B: the flower on names 0-8 plus the X points (list of 3 triples of names); axes: list of names or None (free)."""
    M = Model(18, 10, target, z0=z0, light=light)
    M.add_pi()
    f1 = Flower(0)
    used = {l for x in xpoints for l in x if l < 9}
    tip_exclude = {j for j in range(6) if f1.L(j - 1) in used or f1.L(j + 1) in used}
    M.add_flower(f1, chir_bits(chir1), rays=rays, tips=tips, tip_exclude=tip_exclude)
    M.flowers = [f1]
    M.xpoints = [tuple(x) for x in xpoints]
    for k, T in enumerate(M.xpoints):
        sel = M.add_xpoint_free(T, rays=rays)
        if axes is not None and axes[k] is not None:
            M.cnf.append([sel[axes[k]]])
    if blocklemma:
        M.add_block_lemma()
    if symmetry:
        M.cnf.append([M.X[f1.m[0]][0]])
    if symbreak:
        M.less(f1.l[0], f1.l[3])
    return M

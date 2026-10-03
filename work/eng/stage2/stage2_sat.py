#!/usr/bin/env python3
"""Stage-2 zero-credit-corner SAT builder (K(18), T=94, all-8 present, pi=6, E=0).

Builds the class model (classsat + patsat_m + ends_probe.augment) and adds the E=0 consequences
c1..c9 of the zero-credit corner (work/eng/stage2/RESULT.md).  Every added constraint is controlled by a guard literal
(guard=True) so that the SAME clauses used in production can be validated against exact
arrangement computations by solving under assumptions.  In production (guard=False) the clauses
are added unguarded.

Segment-use variables are exact (functional) definitions:
  Top[r,i,j] / Bot[r,i,j]  (i<j): a triangular face lies on that side of the segment of line r between
                            the vertices r^i and r^j (any representatives i', j' of those vertices)
  Use = Top|Bot, Use2 = Top&Bot.
"""
from pathlib import Path
from itertools import combinations
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'work/bbl/all8_work/pydeps'), str(ROOT / 'work/bbl/all8_work'),
                str(ROOT / 'work/bbl')]
import global_sat as G
import ends_probe as E
from pysat.card import CardEnc, EncType

C = G.C
P = C.P
key3 = P.key3
N = 18


def base_class(K=N, target=94, all8=True, ring_selector=True, tcard='equals_seq'):
    """class model (same as global_sat.build) with optional T cardinality and optional all-8 selector"""
    B = P.Base(K)
    C.add_class(B)
    selectors = []
    for quad in combinations(range(K), 4):
        zq = [B.z[key3(*t)] for t in combinations(quad, 3)]
        ring = C.quad_ring(B, quad)
        for i in range(8):                                  # no 6-type points (11101110 excluded)
            B.cl.append([-x for x in zq] + [ring[i], ring[(i + 4) % 8]])
        selectors.append(B.AND(zq + ring))
    B.selectors = selectors
    if all8:
        B.cl.append(selectors)
    if target is not None:
        from pysat.card import CardEnc
        kind, enc = tcard.split('_')
        encT = {'seq': EncType.seqcounter, 'tot': EncType.totalizer, 'card': EncType.cardnetwrk, 'mtot': EncType.mtotalizer}[enc]
        fn = CardEnc.equals if kind == 'equals' else CardEnc.atleast
        card = fn(list(B.tri.values()), target, top_id=B.nv, encoding=encT)
        B.nv = card.nv
        B.cl.extend(card.clauses)
    return B


class Stage2:
    def __init__(self, B, guard=True):
        self.B = B
        self.guard = guard
        self.g = {}                                         # constraint name -> guard literal
        self.stat = {}

    # ---- helpers
    def gl(self, name):
        if not self.guard:
            return None
        if name not in self.g:
            self.g[name] = self.B.new()
        return self.g[name]

    def add(self, name, clause):
        g = self.gl(name)
        self.B.cl.append(list(clause) + ([-g] if g else []))
        self.stat[name] = self.stat.get(name, 0) + 1

    # ---- segment use variables
    def build_use(self):
        B = self.B
        R = range(B.K)
        TR = {}                                             # (side, r, i, j) i<j
        for t in B.trip:
            T = B.tri[t]
            for r in t:
                i, j = [x for x in t if x != r]
                TR[0, r, i, j] = B.AND([T, B.up(i, j, r)])
                TR[1, r, i, j] = B.AND([T, B.dn(i, j, r)])

        def tr(side, r, i, j):
            return TR[side, r, min(i, j), max(i, j)]
        Mv = {}
        for side in (0, 1):
            for r in R:
                oth = [x for x in R if x != r]
                for i in oth:
                    for j in oth:
                        if i == j:
                            continue
                        terms = []
                        for i2 in oth:
                            if i2 == j:
                                continue
                            if i2 == i:
                                terms.append(tr(side, r, i, j))
                            else:
                                terms.append(B.AND([B.z[key3(r, i, i2)], tr(side, r, i2, j)]))
                        Mv[side, r, i, j] = B.OR(terms)
        Sd = {}
        for side in (0, 1):
            for r in R:
                oth = [x for x in R if x != r]
                for i, j in combinations(oth, 2):
                    terms = []
                    for j2 in oth:
                        if j2 == i:
                            continue
                        if j2 == j:
                            terms.append(Mv[side, r, i, j])
                        else:
                            terms.append(B.AND([B.z[key3(r, j, j2)], Mv[side, r, i, j2]]))
                    Sd[side, r, i, j] = B.OR(terms)
        self.Top = {(r, i, j): Sd[0, r, i, j] for (s, r, i, j) in Sd if s == 0}
        self.Bot = {(r, i, j): Sd[1, r, i, j] for (s, r, i, j) in Sd if s == 1}
        self.Use = {}
        self.Use2 = {}
        for k in self.Top:
            self.Use[k] = B.OR([self.Top[k], self.Bot[k]])
            self.Use2[k] = B.AND([self.Top[k], self.Bot[k]])

    def use(self, r, i, j):
        return self.Use[r, min(i, j), max(i, j)]

    def use2(self, r, i, j):
        return self.Use2[r, min(i, j), max(i, j)]

    # ---- kites, corners
    def build_kites(self):
        B = self.B
        R = range(B.K)
        S = B.S
        self.sec = {}
        self.kite = {}
        self.cq = {}
        self.D = {}
        types = ['pp', 'qp', 'mm', 'pq']
        for p, q in combinations(R, 2):
            for c in R:
                if c in (p, q):
                    continue
                t = B.tri3(p, q, c)
                self.sec[p, q, 'pp', c] = B.AND([t, B.before(p, q, c), B.before(q, p, c)])
                self.sec[p, q, 'mm', c] = B.AND([t, B.before(p, c, q), B.before(q, c, p)])
                self.sec[p, q, 'qp', c] = B.AND([t, B.before(q, p, c), B.before(p, c, q)])
                self.sec[p, q, 'pq', c] = B.AND([t, B.before(q, c, p), B.before(p, q, c)])
            self.kite[p, q] = B.AND([-B.zp[p, q]] + [S[p, q, k] for k in types])
            oth = [c for c in R if c not in (p, q)]
            self.cq[p, q] = [
                B.OR([B.AND([B.A[p, q, c], B.zp2[p, c]]) for c in oth]),    # ray p+
                B.OR([B.AND([B.A[p, c, q], B.zp2[p, c]]) for c in oth]),    # ray p-
                B.OR([B.AND([B.A[q, p, c], B.zp2[q, c]]) for c in oth]),    # ray q+
                B.OR([B.AND([B.A[q, c, p], B.zp2[q, c]]) for c in oth])]    # ray q-
            self.D[p, q] = {k: B.OR([B.AND([self.sec[p, q, k, c], self.use2(c, p, q)]) for c in oth])
                            for k in types}

    # ---- constraints
    def c1_wedges(self, W=12):
        B = self.B
        self.wedges = E.augment(B, 0)           # triple optimality (+ builds wedge literals), no minimum yet
        if W is None:
            return
        card = CardEnc.equals(self.wedges, bound=W, top_id=B.nv, encoding=EncType.seqcounter)
        B.cl.extend(card.clauses)
        B.nv = card.nv

    def c2_no_touch(self):
        B = self.B
        R = range(B.K)
        nuF, nuB = {}, {}
        for L in R:
            oth = [x for x in R if x != L]
            for m in oth:
                nuF[L, m] = B.OR([B.AND([B.A[L, m, j], -self.use(L, m, j)]) for j in oth if j != m])
                nuB[L, m] = B.OR([B.AND([B.A[L, j, m], -self.use(L, m, j)]) for j in oth if j != m])
        for L in R:
            oth = [x for x in R if x != L]
            for i in oth:
                for m in oth:
                    if i == m:
                        continue
                    # P = L^i multiple, X = L^m simple, first segment P->X doubly used
                    # (i before m): forward block, the segment beyond X is the one after X
                    self.add('c2', [-B.A[L, i, m], -B.zp[L, i], B.zp[L, m], -self.use2(L, i, m), -nuF[L, m]])
                    self.add('c2', [-B.A[L, m, i], -B.zp[L, i], B.zp[L, m], -self.use2(L, i, m), -nuB[L, m]])
        self.nuF, self.nuB = nuF, nuB

    def c3_kites_quad_corners(self):
        for (p, q), cs in self.cq.items():
            for a, b, c in combinations(range(4), 3):
                self.add('c3', [-self.kite[p, q], -cs[a], -cs[b], -cs[c]])

    def c4_blocks_to_kites(self):
        B = self.B
        for L in range(B.K):
            oth = [x for x in range(B.K) if x != L]
            for i in oth:
                for m in oth:
                    if i == m:
                        continue
                    self.add('c4', [-B.AD[L, i, m], -B.zp2[L, i], B.zp[L, m], -self.use2(L, i, m),
                                    self.kite[min(L, m), max(L, m)]])

    def c5_no_empty_ray(self):
        B = self.B
        for L in range(B.K):
            oth = [x for x in range(B.K) if x != L]
            for i, m in combinations(oth, 2):
                u = self.use(L, i, m)
                self.add('c5', [-B.AD[L, i, m], -B.zp[L, i], u])
                self.add('c5', [-B.AD[L, i, m], -B.zp[L, m], u])

    def c6_emix(self):
        B = self.B
        self.E2 = {}
        for (p, q), cs in self.cq.items():
            e2 = B.OR([B.AND([cs[a], cs[b]]) for a, b in combinations(range(4), 2)])
            self.E2[p, q] = e2
            for k in ['pp', 'qp', 'mm', 'pq']:
                for c in range(B.K):
                    if c in (p, q):
                        continue
                    self.add('c6', [-self.kite[p, q], -e2, -self.sec[p, q, k, c], self.use2(c, p, q)])

    def c7_allmult_triangles(self):
        B = self.B
        for t in B.trip:
            a, b, c = t
            hyp = [-B.tri[t], -B.zp[a, b], -B.zp[b, c], -B.zp[a, c]]
            for r in t:
                i, j = [x for x in t if x != r]
                self.add('c7', hyp + [self.use2(r, i, j)])

    def c89_kite_caps(self, c8=True, c9=True):
        B = self.B
        self.nq1, self.dall = {}, {}
        for (p, q), cs in self.cq.items():
            D = [self.D[p, q][k] for k in ['pp', 'qp', 'mm', 'pq']]
            nq0 = B.AND([-x for x in cs])
            nq1 = B.OR([B.AND([cs[a]] + [-cs[b] for b in range(4) if b != a]) for a in range(4)])
            self.nq1[p, q] = nq1
            self.dall[p, q] = B.AND(D)
            if c8:
                # exactly two of the four caps are double
                for a, b, c in combinations(range(4), 3):
                    self.add('c8', [-self.kite[p, q], -nq0, D[a], D[b], D[c]])
                    self.add('c8', [-self.kite[p, q], -nq0, -D[a], -D[b], -D[c]])
            if c9:
                for a, b in combinations(range(4), 2):
                    self.add('c9', [-self.kite[p, q], -nq1, D[a], D[b]])

    def c10_zero_slack(self):
        """S_P^circ = 0 at every 4-fold point P together with c4 (all blocks are kite blocks, D_P = k_P):
        k_P + c_B(P) = 4, k_P = #rays of P whose far end is a kite centre, c_B(P) = #case-B kites at P
        (kite with exactly one 4-fold corner, namely P, and all four cap edges double).
        Per-quad guard in guard mode (self.gq[Q])."""
        B = self.B
        R = range(B.K)
        kr, cb = {}, {}
        for L in R:
            for x in R:
                if x == L:
                    continue
                for d in (1, -1):
                    ks, cs_ = [], []
                    for c in R:
                        if c in (L, x):
                            continue
                        adj = B.A[L, x, c] if d == 1 else B.A[L, c, x]
                        pr = (min(L, c), max(L, c))
                        ks.append(B.AND([adj, self.kite[pr]]))
                        cs_.append(B.AND([adj, self.kite[pr], self.nq1[pr], self.dall[pr]]))
                    kr[L, x, d] = B.OR(ks)
                    cb[L, x, d] = B.OR(cs_)
        self.kr, self.cb = kr, cb
        self.gq = {}
        for Q in combinations(R, 4):
            conc = B.AND([B.z[key3(*t)] for t in combinations(Q, 3)])
            lits = []
            for L in Q:
                x = min(y for y in Q if y != L)
                for d in (1, -1):
                    lits.append(kr[L, x, d])
                    lits.append(cb[L, x, d])
            card = CardEnc.equals(lits, bound=4, top_id=B.nv, encoding=EncType.seqcounter)
            B.nv = card.nv
            g = None
            if self.guard:
                g = self.gq[Q] = B.new()
            for cl in card.clauses:
                B.cl.append(list(cl) + [-conc] + ([-g] if g else []))
            self.stat['c10'] = self.stat.get('c10', 0) + len(card.clauses)

    def build_all(self, W=12, c8=True, c9=True, c10=True):
        self.c1_wedges(W)
        self.build_use()
        self.build_kites()
        self.c2_no_touch()
        self.c3_kites_quad_corners()
        self.c4_blocks_to_kites()
        self.c5_no_empty_ray()
        self.c6_emix()
        self.c7_allmult_triangles()
        self.c89_kite_caps(c8, c9)
        if c10:
            self.c10_zero_slack()
        return self


def build_stage2(target=94, all8=True, guard=False, W=12, c8=True, c9=True, c10=True):
    B = base_class(N, target, all8)
    S2 = Stage2(B, guard=guard).build_all(W, c8, c9, c10)
    return B, S2


def dump_cnf(B, path):
    with open(path, 'w') as f:
        f.write(f'p cnf {B.nv} {len(B.cl)}\n')
        for cl in B.cl:
            f.write(' '.join(map(str, cl)) + ' 0\n')


if __name__ == '__main__':
    import time
    t0 = time.time()
    B, S2 = build_stage2(94, True, guard=False)
    print('built', time.time() - t0, 'vars', B.nv, 'clauses', len(B.cl), S2.stat, flush=True)

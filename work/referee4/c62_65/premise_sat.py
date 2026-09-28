"""Referee SAT for C62/C64/C65: does the lemma's (positive) premise occur in ANY pseudoline arrangement of
n lines (any number of triple points, no 4-fold point, no triangle target, no counting)?

Independent of c62_local_sat / k5L_layer: own witness encoding, only the signotope base (allowed4) and the
before() convention of search/kobon_sat.py are shared.  Encodings are one-directional (premise -> witnesses),
which is all a counterexample search needs; every SAT model is decoded and re-checked by struct_.py.

Why UNSAT at the premise's line count n0 is a proof: the premise of C62/C64/C65 is a conjunction of positive
facts (triple points, triangular faces, doubly used first segments with simple/triple far ends) about at most
n0 lines (C65: 6, C62: 7, C64: 8).  Deleting all other lines keeps every such fact; adding a far pseudoline
(crossings beyond all vertices) keeps them too.  So a counterexample anywhere gives one with exactly n0 lines.

    uv run --no-project --with python-sat python premise_sat.py N TEST [TEST ...]
TEST in C65, C65ctl, C62, C62ctl, C64, C64ctl
"""
import sys
import time
from itertools import combinations, permutations, product
from collections import Counter

from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

sys.path.insert(0, '/home/nail/stuff/sundai_math/search')
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee4/c62_65')
from kobon_sat import allowed4  # noqa: E402
from struct_ import Arr, check  # noqa: E402


def S(*x):
    return tuple(sorted(x))


class Model:
    def __init__(self, n):
        self.n = n
        self.pool, self.cnf = IDPool(), CNF()
        P, C = self.pool, self.cnf
        trip = list(combinations(range(n), 3))
        self.z = {t: P.id(('z',) + t) for t in trip}
        self.pz = {t: P.id(('p',) + t) for t in trip}
        self.ng = {t: P.id(('m',) + t) for t in trip}
        for t in trip:
            C.extend([[self.z[t], self.pz[t], self.ng[t]], [-self.z[t], -self.pz[t]], [-self.z[t], -self.ng[t]],
                      [-self.pz[t], -self.ng[t]]])
        val = lambda t, v: {0: self.z, 1: self.pz, -1: self.ng}[v][t]
        ok = {v for v in allowed4() if v != (0, 0, 0, 0)}
        for a, b, c, d in combinations(range(n), 4):
            ts = [(b, c, d), (a, c, d), (a, b, d), (a, b, c)]
            for v in product((-1, 0, 1), repeat=4):
                if v not in ok:
                    C.append([-val(t, x) for t, x in zip(ts, v)])
        bf = lambda r, i, j: self.ng[S(r, i, j)] if i < j else self.pz[S(r, i, j)]
        self.bf = bf
        # adjacency: A(r,i,j) -> i strictly before j on r and nothing strictly between
        A = {}
        for r in range(n):
            oth = [x for x in range(n) if x != r]
            for i, j in permutations(oth, 2):
                a = P.id(('A', r, i, j))
                A[r, i, j] = a
                C.append([-a, bf(r, i, j)])
                for l in oth:
                    if l not in (i, j):
                        C.append([-a, -bf(r, i, l), -bf(r, l, j)])
        # tri(a,b,c) -> not concurrent and the three vertex pairs consecutive (the exact face condition)
        self.tri = {}
        for t in trip:
            a, b, c = t
            v = P.id(('tri',) + t)
            self.tri[t] = v
            C.append([-v, -self.z[t]])
            for r, i, j in ((a, b, c), (b, a, c), (c, a, b)):
                C.append([-v, A[r, i, j], A[r, j, i]])

    def T(self, *x):
        return self.tri[S(*x)]

    def Z(self, *x):
        return self.z[S(*x)]

    def node_or(self, key, branches):
        """v -> OR_k AND(branches[k]); returns v (False-constant if no branch)."""
        v = self.pool.id(key)
        ws = []
        for k, lits in enumerate(branches):
            w = self.pool.id(key + ('w', k))
            self.cnf.extend([[-w, x] for x in lits])
            ws.append(w)
        self.cnf.append([-v] + ws)
        return v

    # P = l1 ∩ l2 (∩ c) has a block (middle on c, cap C) one of whose cap triangles has the vertex
    # l1 ∩ u (= l1 ∩ u ∩ l3); cap C through that vertex, C in {u, l3}.
    def cov(self, l1, l2, u, l3):
        u, l3 = min(u, l3), max(u, l3)
        key = ('cov', l1, l2, u, l3)
        if key in self._cov:
            return self._cov[key]
        br = []
        for c in range(self.n):
            if c in (l1, l2, u, l3):
                continue
            for Cc in (u, l3):
                br.append([self.Z(l1, l2, c), self.T(c, l1, Cc), self.T(c, l2, Cc)])
        v = self.node_or(key, br)
        self._cov[key] = v
        return v

    _cov = {}

    def partner(self, Q):
        """some triple point V is bent towards the triple point Q (lines of Q: a3, C1, C2)"""
        br = []
        for a3 in Q:
            C1, C2 = [x for x in Q if x != a3]
            for a1, a2 in permutations([x for x in range(self.n) if x not in Q], 2):
                br.append([self.Z(a1, a2, a3), self.T(a1, a2, C1), self.T(a1, a3, C1), self.T(a2, a1, C2),
                           self.T(a2, a3, C2)])
        return self.node_or(('partner',) + Q, br)

    def sigma(self, model):
        pos = set(x for x in model if x > 0)
        return {t: (0 if self.z[t] in pos else 1 if self.pz[t] in pos else -1) for t in self.z}


def premise(M, test):
    n = M.n
    outer = []
    if test in ('C65', 'C65ctl'):
        for Q in combinations(range(n), 3):
            for q3 in Q:
                x, y = [v for v in Q if v != q3]
                for w in range(n):
                    if w in Q:
                        continue
                    lits = [M.Z(*Q), M.T(x, y, w), M.cov(y, w, x, q3)]
                    if test == 'C65':
                        lits.append(M.cov(x, w, y, q3))
                    else:   # control: R = x∩w must still be a triple point (all-multiple face)
                        lits.append(M.node_or(('Rtrip', x, w), [[M.Z(x, w, r)] for r in range(n) if r not in (x, w)]))
                    outer.append(lits)
    elif test in ('C62', 'C62ctl'):
        for u, a1, a2, b1, b2 in permutations(range(n), 5):
            lits = [M.Z(u, a1, a2), M.Z(u, b1, b2), M.T(u, a1, b1), M.T(u, a2, b2),
                    M.cov(a1, b1, u, a2)]                     # P1 covers P1 -> a
            if test == 'C62':
                lits.append(M.cov(b2, a2, u, b1))              # P2 covers P2 -> b (crossed)
            else:
                lits.append(M.cov(a2, b2, u, a1))              # P2 covers P2 -> a (parallel control)
            outer.append(lits)
    elif test in ('C64', 'C64ctl'):
        for Q in combinations(range(n), 3):
            pv = M.partner(Q)
            for q3 in Q:
                for x, y in permutations([v for v in Q if v != q3]):
                    for w in range(n):
                        if w in Q:
                            continue
                        for p, r in permutations([v for v in range(n) if v not in Q and v != w], 2):
                            # P = y∩w∩p, R = x∩w∩r; [Q,P] on y doubly: other triangle {y, x', w'}
                            dQP = [M.T(y, xx, ww) for xx in (x, q3) for ww in (w, p) if (xx, ww) != (x, w)]
                            dQR = [M.T(x, yy, ww) for yy in (y, q3) for ww in (w, r) if (yy, ww) != (y, w)]
                            a = M.node_or(('dQP', Q, y, w, p, x), [[l] for l in dQP])
                            b = M.node_or(('dQR', Q, x, w, r, y), [[l] for l in dQR])
                            lits = [M.Z(*Q), pv, M.T(x, y, w), M.Z(y, w, p), M.Z(x, w, r), a]
                            if test == 'C64':
                                lits.append(b)
                            outer.append(lits)
    else:
        raise SystemExit(test)
    top = M.node_or(('top', test), outer)
    return top


def main():
    n = int(sys.argv[1])
    for test in sys.argv[2:]:
        M = Model(n)
        M._cov = {}
        t0 = time.time()
        top = premise(M, test)
        M.cnf.append([top])
        with Solver(name='cadical153', bootstrap_with=M.cnf.clauses) as sv:
            r = sv.solve()
            line = f'n={n} {test}: {"SAT" if r else "UNSAT"} ({time.time() - t0:.1f}s, {len(M.cnf.clauses)} clauses)'
            if r:
                A = Arr(n, M.sigma(sv.get_model()))
                st, bad = Counter(), []
                check(A, st, bad)
                line += f' | decoded: triples {len(A.triples)}, allmult faces {st["allmult faces"]}, ' \
                        f'twin pairs {st["T twin pairs"]}, parallel-cap pairs {st["T parallel caps (control)"]}, ' \
                        f'CC cover=1 {st["CC #covering toward a vertex = 1"]}, bent {st["BP bent"]}, ' \
                        f'BP one-side {st["BP partner face with one side doubly used"]}, violations {len(bad)}'
            print(line, flush=True)


if __name__ == '__main__':
    main()

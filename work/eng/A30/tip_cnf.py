"""A30: independent CNF for the minimal tip lemma (written without reading T28's encoding).

Model.  9 labelled pseudolines ("roles") in the Euclidean plane (wiring diagram view).  Variables:
  sl[x][y] (x<y)   : True iff role x has the LOWER slope than role y (total order, transitivity clauses).
  lt[r][b][c], gt[r][b][c]  (r, b<c distinct): on line r the crossing with b is strictly before / strictly after the
                     crossing with c (x-coordinate); neither = the two crossings coincide (triple point r,b,c).
Axioms (all of them hold in every Euclidean pseudoline arrangement; nothing else is used):
  (W) for every line r and every three other lines b,c,d the three pairwise relations form a weak order, and not all
      three are ties (no point of multiplicity 4; every 18-line arrangement considered has multiplicity <= 3).
  (T) for every triple a<b<c the three local comparisons are the same after normalising by slope order: with
      N_a = "b before c on a, read in increasing slope order of (b,c)" etc, N_a = N_b = N_c  (all '<', all '=', all '>').
      (For slopes u<v<w: x_uv < x_uw < x_vw, or the reverse, or all equal.)
Statement-specific constraints (usage of roles: m0,m1,m2 = 0,1,2 ; l_0..l_5 = 3..8).
"""
import itertools, sys
from pysat.formula import CNF

N = 9
M = lambda i: i % 3            # spokes m_i, m_{i+3} = m_i
L = lambda i: 3 + (i % 6)      # hexagon lines

class Enc:
    def __init__(self, no4fold=True):
        self.no4fold = no4fold
        self.nv = 0
        self.cnf = CNF()
        self.sl = {}
        self.lt = {}
        self.gt = {}
        for x, y in itertools.combinations(range(N), 2):
            self.sl[x, y] = self.new()
        for r in range(N):
            oth = [i for i in range(N) if i != r]
            for b, c in itertools.combinations(oth, 2):
                self.lt[r, b, c] = self.new()
                self.gt[r, b, c] = self.new()
                self.cnf.append([-self.lt[r, b, c], -self.gt[r, b, c]])
        self._axioms()

    def new(self):
        self.nv += 1
        return self.nv

    # literal "a has lower slope than b"
    def low(self, a, b):
        return self.sl[a, b] if a < b else -self.sl[b, a]

    # literals for relations on line r between the crossings with b and c
    def LT(self, r, b, c):   # crossing with b strictly before crossing with c (b != c)
        return self.lt[r, b, c] if b < c else self.gt[r, c, b]

    def GT(self, r, b, c):
        return self.LT(r, c, b)

    def EQ(self, r, b, c):  # as list of "negated-literal pair": EQ holds iff both lt,gt false
        return (-self.LT(r, b, c), -self.GT(r, b, c))

    def eq(self, r, b, c):
        """add unit clauses asserting crossing(r,b) == crossing(r,c)"""
        x, y = self.EQ(r, b, c)
        self.cnf.append([x]); self.cnf.append([y])

    def neq_clause(self, r, b, c):
        """clause asserting crossing(r,b) != crossing(r,c)"""
        return [self.LT(r, b, c), self.GT(r, b, c)]

    def _val_not(self, r, b, c, v):
        """literals whose disjunction says: relation(r;b,c) != v, v in '<','=','>' """
        if v == '<':
            return [-self.LT(r, b, c)]
        if v == '>':
            return [-self.GT(r, b, c)]
        return [self.LT(r, b, c), self.GT(r, b, c)]

    def _axioms(self):
        cnf = self.cnf
        # slope order transitivity
        for x, y, z in itertools.permutations(range(N), 3):
            # low(x,y) & low(y,z) -> low(x,z)
            cnf.append([-self.low(x, y), -self.low(y, z), self.low(x, z)])
        # (W) weak order on every line, no 4-fold
        rel_vals = '<=>'
        def cmp(p, q):
            return '<' if p < q else ('>' if p > q else '=')
        allowed = set()
        for pos in itertools.product(range(3), repeat=3):   # positions of b,c,d on the line
            allowed.add((cmp(pos[0], pos[1]), cmp(pos[0], pos[2]), cmp(pos[1], pos[2])))
        if self.no4fold:
            allowed.discard(('=', '=', '='))
        for r in range(N):
            oth = [i for i in range(N) if i != r]
            for b, c, d in itertools.combinations(oth, 3):
                for combo in itertools.product(rel_vals, repeat=3):
                    if combo in allowed:
                        continue
                    cl = self._val_not(r, b, c, combo[0]) + self._val_not(r, b, d, combo[1]) + self._val_not(r, c, d, combo[2])
                    cnf.append(cl)
        # (T) triple consistency
        for a, b, c in itertools.combinations(range(N), 3):
            # N_a: relation of (b,c) on a, normalised: if low(b,c) then rel else reversed.
            trip = [(a, b, c), (b, a, c), (c, a, b)]   # (line, first, second)   [first<second as roles]
            for bits in itertools.product([0, 1], repeat=3):   # bits: low(first,second) for the three lines
                # slope pattern as literals: low(b,c), low(a,c), low(a,b)
                pat = [self.low(b, c) if bits[0] else -self.low(b, c),
                       self.low(a, c) if bits[1] else -self.low(a, c),
                       self.low(a, b) if bits[2] else -self.low(a, b)]
                for rv in itertools.product(rel_vals, repeat=3):
                    # normalised values
                    nv = []
                    for k in range(3):
                        v = rv[k]
                        if not bits[k]:   # reversed reading
                            v = {'<': '>', '>': '<', '=': '='}[v]
                        nv.append(v)
                    if nv[0] == nv[1] == nv[2]:
                        continue
                    cl = [-p for p in pat]
                    for k in range(3):
                        line, f, s = trip[k]
                        cl += self._val_not(line, f, s, rv[k])
                    cnf.append(cl)

    # ---------------------------------------------------------------- statement constraints
    def concurrent(self, x, y, z):
        self.eq(x, y, z); self.eq(y, x, z); self.eq(z, x, y)

    def not_strictly_between(self, a, x, y, d):
        """on line a, crossing(a,d) is not strictly between crossing(a,x) and crossing(a,y)"""
        self.cnf.append([-self.LT(a, x, d), -self.LT(a, d, y)])
        self.cnf.append([-self.LT(a, y, d), -self.LT(a, d, x)])

    def triangle_face(self, p, q, r):
        """lines p,q,r bound a bounded triangular face: three distinct vertices and no other line cuts an open side"""
        for a, x, y in ((p, q, r), (q, p, r), (r, p, q)):
            self.cnf.append(self.neq_clause(a, x, y))
            for d in range(N):
                if d not in (p, q, r):
                    self.not_strictly_between(a, x, y, d)

    def flower(self):
        self.concurrent(M(0), M(1), M(2))                                   # O
        for i in range(6):
            self.concurrent(M(i), L(i - 1), L(i))                           # P_i
        for i in range(6):
            self.triangle_face(M(i), M(i + 1), L(i))                        # inner triangle O P_i P_{i+1}

    def ends_at_tip(self, j, mirror=False, simple_tip=False):
        """l_{j-1} ends at Y_j = l_{j-1} n l_{j+1}  (mirror: l_{j+1} ends at Y_j), i.e. Y_j is the last vertex beyond P_j.
        simple_tip: additionally no other line passes through Y_j."""
        if not mirror:
            A, Y, Q = L(j - 1), L(j + 1), L(j)      # P_j = A n Q n m_j
        else:
            A, Y, Q = L(j + 1), L(j - 1), L(j)      # P_{j+1} = A n l_j n m_{j+1}
        for d in range(N):
            if d in (A, Y, Q):
                continue
            # if Q before Y then not (Y before d) ; if Y before Q then not (d before Y)
            self.cnf.append([-self.LT(A, Q, Y), -self.LT(A, Y, d)])
            self.cnf.append([-self.LT(A, Y, Q), -self.LT(A, d, Y)])
            if simple_tip:
                self.cnf.append(self.neq_clause(A, d, Y))
        # Q (= the corner point) is distinct from Y (automatic with no 4-fold points, but be explicit)
        self.cnf.append(self.neq_clause(A, Q, Y))


def build(j=0, mirror=False, end1=True, end2=True, simple_tip=False, no4fold=True):
    e = Enc(no4fold)
    e.flower()
    if end1:
        e.ends_at_tip(j, mirror, simple_tip)
    if end2:
        e.ends_at_tip(j + 3, mirror, simple_tip)
    return e


if __name__ == '__main__':
    from pysat.solvers import Solver
    for mirror in (False, True):
        for simple in (False, True):
            for (e1, e2) in ((True, True), (True, False), (False, True), (False, False)):
                e = build(0, mirror, e1, e2, simple)
                with Solver(name='cadical195', bootstrap_with=e.cnf.clauses) as s:
                    r = s.solve()
                print(f'mirror={mirror} simple_tip={simple} end1={e1} end2={e2}: nv={e.nv} ncl={len(e.cnf.clauses)} SAT={r}', flush=True)

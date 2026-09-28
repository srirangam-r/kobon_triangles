"""Independent arrangement structure from a rank-3 signotope with zeros (referee C62-C65).

sigma[(a,b,c)] in {-1,0,1} for a<b<c.  Convention of search/kobon_sat.py:
before(r,i,j) (crossing with i strictly before crossing with j on line r) <=> sigma[sorted] == (-1 if i<j else +1).
Everything is computed combinatorially from per-line vertex orders; circular order at a triple point
{w0<w1<w2} is [(w0,-1),(w1,-1),(w2,-1),(w0,1),(w1,1),(w2,1)] (-1 = towards earlier vertices) and is
VALIDATED: every triangular face at a point must use two circularly adjacent rays.
"""
from itertools import combinations


def S(*x):
    return tuple(sorted(x))


class Arr:
    def __init__(self, n, sigma):
        self.n = n
        self.sigma = sigma
        self.rows = {}
        for r in range(n):
            oth = [x for x in range(n) if x != r]

            def bf(i, j):
                s = sigma[S(r, i, j)]
                return s == (-1 if i < j else 1)
            rank = {i: sum(bf(l, i) for l in oth if l != i) for i in oth}
            for i in oth:
                for j in oth:
                    if i != j:
                        if sigma[S(r, i, j)] == 0:
                            assert rank[i] == rank[j], 'inconsistent zero'
                        else:
                            assert bf(i, j) != bf(j, i) and bf(i, j) == (rank[i] < rank[j]), 'inconsistent'
            groups = {}
            for i in oth:
                groups.setdefault(rank[i], set()).add(i)
            self.rows[r] = [frozenset(groups[k] | {r}) for k in sorted(groups)]
        self.mult = {}
        for r, row in self.rows.items():
            for v in row:
                self.mult[v] = len(v)
        for v in self.mult:
            for L in v:
                assert v in self.rows[L], 'vertex inconsistency'
        self.pos = {(L, v): k for L, row in self.rows.items() for k, v in enumerate(row)}
        # triangular faces: {a,b,c} not concurrent, pairwise vertices consecutive on each line
        self.tris = set()
        for a, b, c in combinations(range(n), 3):
            if sigma[(a, b, c)] == 0:
                continue
            vab, vac, vbc = self.vert(a, b), self.vert(a, c), self.vert(b, c)
            if self.cons(a, vab, vac) and self.cons(b, vab, vbc) and self.cons(c, vac, vbc):
                self.tris.add(frozenset((vab, vac, vbc)))
        self.triples = [v for v in self.mult if len(v) == 3]
        assert all(len(v) <= 3 for v in self.mult)
        # usage of segments: segment = (L, k) between rows[L][k] and rows[L][k+1]
        self.usage = {}
        for t in self.tris:
            for u, w in combinations(t, 2):
                (L,) = tuple(u & w)
                k = min(self.pos[L, u], self.pos[L, w])
                assert abs(self.pos[L, u] - self.pos[L, w]) == 1
                self.usage.setdefault((L, k), []).append(t)
        assert all(len(x) <= 2 for x in self.usage.values())
        self.info = {P: self.point(P) for P in self.triples}

    def vert(self, a, b):
        for v in self.rows[a]:
            if b in v:
                return v
        raise KeyError

    def cons(self, L, u, w):
        return abs(self.pos[L, u] - self.pos[L, w]) == 1

    def first(self, P, L, d):
        k = self.pos[L, P] + d
        row = self.rows[L]
        return row[k] if 0 <= k < len(row) else None

    def seg(self, P, L, d):
        k = self.pos[L, P]
        j = k if d == 1 else k - 1
        if j < 0 or j >= len(self.rows[L]) - 1:
            return None, []
        return (L, j), self.usage.get((L, j), [])

    def point(self, P):
        w = sorted(P)
        R = [(w[0], -1), (w[1], -1), (w[2], -1), (w[0], 1), (w[1], 1), (w[2], 1)]
        F = [self.first(P, L, d) for L, d in R]
        U = [self.seg(P, L, d)[1] for L, d in R]
        # validate circular order: every triangle face at P uses two adjacent rays
        for t in self.tris:
            if P in t:
                o = [v for v in t if v != P]
                idx = [F.index(v) for v in o]
                assert (idx[0] - idx[1]) % 6 in (1, 5), 'circular order'
        blk = [len(U[i]) == 2 and F[i] is not None and len(F[i]) == 2 for i in range(6)]
        brg = [len(U[i]) == 2 and F[i] is not None and len(F[i]) == 3 for i in range(6)]
        mids = [i for i in range(6) if blk[i]]
        lines_of_mids = [R[i][0] for i in mids]
        if len(mids) == 2 and lines_of_mids[0] == lines_of_mids[1]:
            typ = 'X'
        elif len(mids) == 2:
            typ = 'V'
        else:
            typ = {0: 'O0', 1: 'O1', 3: 'C'}.get(len(mids), '?')
        # cap triangles per block: the two faces bordering the first segment
        caps = {i: U[i] for i in mids}
        return dict(R=R, F=F, U=U, blk=blk, brg=brg, mids=mids, typ=typ, e=sum(brg), caps=caps)

    def covers(self, P, Q):
        """P has a block one of whose cap triangles has vertex Q."""
        I = self.info[P]
        return any(Q in t for i in I['mids'] for t in I['caps'][i])

    def doubly(self, P, Q):
        """segment [P,Q] (consecutive on their common line) borders two triangles"""
        (L,) = tuple(P & Q)
        if not self.cons(L, P, Q):
            return False
        k = min(self.pos[L, P], self.pos[L, Q])
        return len(self.usage.get((L, k), [])) == 2

    def allmult_faces(self):
        return [t for t in self.tris if all(len(v) == 3 for v in t)]


def check(A, st, bad, tag=''):
    """C62 (T), C63 (W), C64 (BP), C65 (CC) checks with premise counters."""
    faces = A.allmult_faces()
    info = A.info
    st['arr'] += 1
    st['triples'] += len(A.triples)
    st['allmult faces'] += len(faces)
    for f in faces:
        nx = sum(info[v]['typ'] == 'X' for v in f)
        st[f'CC faces with {nx} X vertices'] += 1
        if nx >= 2:
            bad.append(f'{tag} C65: face with {nx} X vertices')
        for Q in f:
            P, R = [v for v in f if v != Q]
            c = A.covers(P, Q) + A.covers(R, Q)
            st[f'CC #covering toward a vertex = {c}'] += 1
            if c == 2:
                bad.append(f'{tag} C65 violated')
    for f1, f2 in combinations(faces, 2):
        sh = f1 & f2
        if len(sh) != 2:
            continue
        a, b = tuple(sh)
        (P1,) = tuple(f1 - sh)
        (P2,) = tuple(f2 - sh)
        st['T twin pairs'] += 1
        st['T twin types ' + ''.join(sorted((info[P1]['typ'], info[P2]['typ'])))] += 1
        for x, y in ((a, b), (b, a)):
            if A.covers(P1, x) and A.covers(P2, y):
                bad.append(f'{tag} C62 violated')
            if A.covers(P1, x) or A.covers(P2, y):
                st['T one side of the crossed premise'] += 1
            if A.covers(P1, x) and A.covers(P2, x):
                st['T parallel caps (control)'] += 1
    for Q, I in info.items():
        for i in range(6):
            r = [(i + j) % 6 for j in range(6)]
            F = I['F']
            if all(F[r[j]] is not None and len(F[r[j]]) == 3 for j in range(4)) and len(I['U'][r[0]]) == 2 \
                    and len(I['U'][r[3]]) == 2:
                st['W premise'] += 1
                if I['mids']:
                    st['W premise with block'] += 1
                if I['blk'][r[4]] and not I['brg'][r[5]]:
                    bad.append(f'{tag} C63 violated (block at r4, r5 not bridge)')
                if I['blk'][r[5]] and not I['brg'][r[4]]:
                    bad.append(f'{tag} C63 violated (block at r5, r4 not bridge)')
    for V, I in info.items():
        if I['typ'] != 'V':
            continue
        st['BP bent'] += 1
        m0, m1 = I['mids']
        sh = (m0 + 1) % 6 if (m1 - m0) % 6 == 2 else (m1 + 1) % 6
        Q = I['F'][sh]
        # independent: Q must be the common third vertex of both blocks' cap triangles
        c0 = set().union(*[set(t) for t in I['caps'][m0]]) - {V}
        c1 = set().union(*[set(t) for t in I['caps'][m1]]) - {V}
        assert (c0 & c1) == {Q}, 'bent shared apex'
        assert len(Q) == 3, 'bent partner not triple'
        st['BP bent with partner'] += 1
        for f in faces:
            if Q not in f:
                continue
            P, R = [v for v in f if v != Q]
            st['BP partner in all-mult face'] += 1
            if A.doubly(Q, P) and A.doubly(Q, R):
                bad.append(f'{tag} C64 violated')
            elif A.doubly(Q, P) or A.doubly(Q, R):
                st['BP partner face with one side doubly used'] += 1

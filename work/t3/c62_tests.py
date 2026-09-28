"""Empirical tests for the C62-C65 lemmas (k = 5, beta > 0 residue).

Arrangements: gallery wiring words, then random contractions of simple triangles to triple
points (plus a targeted move that makes all-multiple faces) and triangle flips; no 4-fold points.
Local structure per triple point P: 6 rays in circular order (work/t3/arr.py convention), first
vertices F[i], usage of the first segment, sector triangles, blocks (doubly used, simple far end)
and bridges (doubly used, triple far end).

Checks (all must have 0 violations):
  CC (C65) in an all-multiple face PQR, P and R never both have blocks covering P->Q, R->Q.
  T  (C62) two all-multiple faces (P1,a,b), (P2,a,b) sharing the side [a,b]: never P1 has a
     block covering P1->a while P2 has a block covering P2->b ("crossed blocks").
  W  (C63) four consecutive rays with triple first vertices, the outer two doubly used: then P
     has no block unless a fifth ray carries a bridge.
  BP (C64) the partner Q of a bent point is never a face vertex with both its face sides doubly used.
  OB (earlier-draft tool) opposed blocks: two blocks on one line ending at the same simple X from opposite
     sides => both neighbours of X on the cap line are multiple.
  G  (earlier draft; premise never occurs, 2-F faces are impossible by C65) 2-F face PQR (P,R type X, Q one
     block mutual with P): U = first(q4) lies on b_P with
     P, X_PQ, U consecutive; e(Q) >= 3 => q4 is a bridge; then U is not type X; e(Q) = 4 =>
     W = first(q3) on b_R with R, X_RQ, W consecutive and W not type X.
usage: python3 c62_tests.py N_PER_WORKER SEED [WORKERS=4]
"""
import json
import random
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee')
from arr import from_tokens  # noqa: E402
from mutate import simple_tris, contract, flip  # noqa: E402

GAL = Path('/home/nail/stuff/sundai_math/tools/external/kobon-solutions/gallery/data')


class Loc:
    """Local structure of arrangement A (referee Arr, no 4-fold points)."""

    def __init__(self, A):
        self.A = A
        self.tri = set(frozenset(t) for t in A.tris)
        self.T = set(A.triples)
        self.info = {P: self.point(P) for P in A.triples}

    def first(self, P, ray):
        L, d = ray
        k = self.A.idx[L][P] + d
        r = self.A.rows[L]
        return r[k] if 0 <= k < len(r) else None

    def use(self, P, ray):
        L, d = ray
        k = self.A.idx[L][P]
        j = k if d == 1 else k - 1
        if j < 0 or j >= len(self.A.rows[L]) - 1:
            return None
        return len(self.A.usage.get((L, j), ()))

    def point(self, P):
        w0, w1, w2 = sorted(self.A.ev[P])
        R = [(w0, -1), (w1, -1), (w2, -1), (w0, 1), (w1, 1), (w2, 1)]
        F = [self.first(P, r) for r in R]
        U = [self.use(P, r) for r in R]
        S = [F[i] is not None and F[(i + 1) % 6] is not None and frozenset((P, F[i], F[(i + 1) % 6])) in self.tri
             for i in range(6)]
        blk = [U[i] == 2 and F[i] is not None and self.A.mult[F[i]] == 2 for i in range(6)]
        brg = [U[i] == 2 and F[i] is not None and self.A.mult[F[i]] == 3 for i in range(6)]
        mids = [i for i in range(6) if blk[i]]
        if len(mids) == 2 and (mids[1] - mids[0]) % 6 == 3:
            typ = 'X'
        elif len(mids) == 2:
            typ = 'V'
        else:
            typ = {0: 'O0', 1: 'O1', 3: 'C'}.get(len(mids), '?')
        return dict(R=R, F=F, U=U, S=S, blk=blk, brg=brg, mids=mids, typ=typ, e=sum(brg))

    def ray_to(self, P, Q):
        I = self.info[P]
        for i in range(6):
            if I['F'][i] == Q:
                return i
        return None

    def cap(self, P, i):
        """cap line of the block at ray i of P (other line through the far end)."""
        X = self.info[P]['F'][i]
        (C,) = tuple(self.A.ev[X] - {self.info[P]['R'][i][0]})
        return C

    def all_mult_faces(self):
        return [t for t in self.tri if all(self.A.mult[v] == 3 for v in t)]


def consecutive_on(A, L, u, v):
    return L in A.ev[u] and L in A.ev[v] and abs(A.idx[L][u] - A.idx[L][v]) == 1


def check(A, st, bad, tag):
    if any(m > 3 for m in A.mult):
        return
    Lc = Loc(A)
    info = Lc.info
    faces = Lc.all_mult_faces()
    st['arr'] += 1
    st['triples'] += len(A.triples)
    st['allmult faces'] += len(faces)
    # ---- T: twin faces
    for i, f1 in enumerate(faces):
        for f2 in faces[i + 1:]:
            sh = f1 & f2
            if len(sh) != 2:
                continue
            a, b = sorted(sh)
            (P1,) = tuple(f1 - sh)
            (P2,) = tuple(f2 - sh)
            st['T premise (twin faces)'] += 1

            def covers(P, x, y):
                """P has a block covering P->x on the side away from P->y."""
                I = info[P]
                ix, iy = Lc.ray_to(P, x), Lc.ray_to(P, y)
                if ix is None or iy is None:
                    return None
                out = (ix - 1) % 6 if (iy - ix) % 6 == 1 else (ix + 1) % 6
                assert (iy - ix) % 6 in (1, 5)
                return I['blk'][out]
            c1a, c1b = covers(P1, a, b), covers(P1, b, a)
            c2a, c2b = covers(P2, a, b), covers(P2, b, a)
            st[('T types', ''.join(sorted((info[P1]['typ'], info[P2]['typ']))))] += 1
            if (c1a and c2b) or (c1b and c2a):
                bad.append(f'{tag} T violated: faces {sorted(f1)} {sorted(f2)}')
            if info[P1]['typ'] == 'X' and info[P2]['typ'] == 'X':
                bad.append(f'{tag} T: both third vertices type X')
    # ---- W: four consecutive triple-first rays
    for P, I in info.items():
        for i in range(6):
            r = [(i + j) % 6 for j in range(6)]
            if all(I['F'][r[j]] is not None and A.mult[I['F'][r[j]]] == 3 for j in range(4)) \
                    and I['U'][r[0]] == 2 and I['U'][r[3]] == 2:
                st['W premise'] += 1
                if I['mids'] and not (I['brg'][r[4]] or I['brg'][r[5]]):
                    bad.append(f'{tag} W violated at {P}: mids {I["mids"]} brg {I["brg"]}')
                if I['mids']:
                    st['W premise with block (needs 5th bridge)'] += 1
    # ---- BP: bent partner not a face vertex with both face sides doubly used
    for V, I in info.items():
        if I['typ'] != 'V':
            continue
        m0, m1 = I['mids']
        sh = (m0 + 1) % 6 if (m1 - m0) % 6 == 2 else (m1 + 1) % 6
        Q = I['F'][sh]
        st['bent points'] += 1
        if Q is None or A.mult[Q] != 3:
            continue
        st['bent with triple partner'] += 1
        for f in faces:
            if Q not in f:
                continue
            Pp, Rr = [v for v in f if v != Q]
            L1, L2 = A.common_line(Q, Pp), A.common_line(Q, Rr)
            j1 = min(A.idx[L1][Q], A.idx[L1][Pp]); j2 = min(A.idx[L2][Q], A.idx[L2][Rr])
            if len(A.usage.get((L1, j1), ())) == 2 and len(A.usage.get((L2, j2), ())) == 2:
                bad.append(f'{tag} BP violated: bent {V} partner {Q} face {sorted(f)}')
            st['BP partner in all-mult face'] += 1
    # ---- OB: opposed blocks at a simple point
    ends = {}
    for P, I in info.items():
        for i in I['mids']:
            ends.setdefault(I['F'][i], []).append((P, I['R'][i][0]))
    for X, lst in ends.items():
        for x in range(len(lst)):
            for y in range(x + 1, len(lst)):
                (P1, L1), (P2, L2) = lst[x], lst[y]
                if L1 != L2:
                    continue
                st['OB premise'] += 1
                (C,) = tuple(A.ev[X] - {L1})
                k = A.idx[C][X]
                nb = [A.rows[C][k + d] for d in (-1, 1) if 0 <= k + d < len(A.rows[C])]
                if len(nb) < 2 or any(A.mult[v] == 2 for v in nb):
                    bad.append(f'{tag} OB violated at {X}')

    # ---- CC: converging caps: in an all-multiple face PQR, two vertices never both cover their rays toward the third
    for f in faces:
        for Q in f:
            P_, R_ = [v for v in f if v != Q]
            def cov(P, Q, R):
                I = info[P]
                iq, ir = Lc.ray_to(P, Q), Lc.ray_to(P, R)
                out = (iq - 1) % 6 if (ir - iq) % 6 == 1 else (iq + 1) % 6
                return I['blk'][out]
            a, b = cov(P_, Q, R_), cov(R_, P_, Q) if False else cov(R_, Q, P_)
            st[('CC covers toward a vertex', int(a) + int(b))] += 1
            if a and b:
                bad.append(f'{tag} CC violated: face {sorted(f)} both cover toward {Q}')
        nx = sum(info[v]['typ'] == 'X' for v in f)
        st[('CC face #typeX', nx)] += 1
        if nx >= 2:
            bad.append(f'{tag} CC: face {sorted(f)} with {nx} type-X vertices')
    # ---- G: 2-F faces
    for f in faces:
        for Q in f:
            P_, R_ = [v for v in f if v != Q]
            if info[P_]['typ'] != 'X' or info[R_]['typ'] != 'X' or len(info[Q]['mids']) != 1:
                continue
            st['G premise (2-F face, Q one block)'] += 1
            IQ = info[Q]
            m = IQ['mids'][0]
            C = Lc.cap(Q, m)
            # mutual partner: the face vertex whose line is the cap
            P, R = (P_, R_) if C in A.ev[P_] else (R_, P_) if C in A.ev[R_] else (None, None)
            if P is None:
                bad.append(f'{tag} G: Q block cap through neither face vertex')
                continue
            q0, q1 = Lc.ray_to(Q, P), Lc.ray_to(Q, R)
            orient = 1 if (q1 - q0) % 6 == 1 else -1
            q = lambda j: (q0 + orient * j) % 6
            if m != q(5):
                bad.append(f'{tag} G: Q block not at q5 (m={m}, q5={q(5)})')
                continue
            XPQ = IQ['F'][q(5)]
            U = IQ['F'][q(4)]
            bP = C
            ok = U is not None and bP in A.ev[U] and consecutive_on(A, bP, XPQ, U) and consecutive_on(A, bP, P, XPQ)
            if not ok:
                bad.append(f'{tag} G(a) failed: U={U}')
            st[('G e(Q)', IQ['e'])] += 1
            if IQ['e'] >= 3:
                if not IQ['brg'][q(4)]:
                    bad.append(f'{tag} G: e(Q)>=3 but q4 not a bridge')
                elif info[U]['typ'] == 'X':
                    bad.append(f'{tag} G: U type X')
                st[('G U type', info[U]['typ'] if U in info else 'simple')] += 1
            if IQ['e'] == 4:
                W = IQ['F'][q(3)]
                XRQ = IQ['F'][q(2)]
                (bR,) = tuple(A.ev[XRQ] - {IQ['R'][q(2)][0]})
                if not (consecutive_on(A, bR, R, XRQ) and consecutive_on(A, bR, XRQ, W)):
                    bad.append(f'{tag} G(c) W not on b_R')
                if info[W]['typ'] == 'X':
                    bad.append(f'{tag} G(c) W type X')
                st['G e(Q)=4 checked'] += 1


def make_face(A, rng):
    """Targeted move: pick a simple triangular face D and, for each vertex u of D, contract the
    simple triangle vertically opposite D at u (if it exists); this tends to create
    all-multiple faces."""
    s = simple_tris(A)
    rng.shuffle(s)
    for D in s[:40]:
        opp = []
        for u in D:
            Ls = sorted(A.ev[u])
            # faces at u other than D: triangles containing u that share no line-segment with D
            cand = [t for t in simple_tris(A) if u in t and len(set(t) & set(D)) == 1]
            # vertically opposite: uses both lines through u, lies on the other side of both
            cand = [t for t in cand if all(any(L in A.ev[v] for v in t if v != u) for L in Ls)]
            if cand:
                opp.append(rng.choice(cand))
        if len(opp) >= 2 and len({v for t in opp for v in t}) == 3 * len(opp):
            try:
                B = A
                for t in opp:
                    tt = [e for e in B.tris if set(e) == set(t)]
                    if not tt:
                        break
                    B = contract(B, tt[0])
                return B
            except (ValueError, AssertionError, IndexError):
                continue
    return A


def worker(args):
    wid, N, seed = args
    rng = random.Random(seed * 7919 + wid)
    st, bad = Counter(), []
    files = [f for s in ('10', '12', '14', '16', '18', '18-1', '18-4', '18-6', '18-9', '20', '20-6', '20-9')
             for f in sorted((GAL / s).glob('*.json'))]
    for it in range(N):
        f = rng.choice(files)
        n = int(f.parent.name.split('-')[0])
        try:
            A = from_tokens(json.load(open(f))['gens'].split(), n)
            for _ in range(rng.choice([0, 1, 2, 3])):
                A = make_face(A, rng)
            for _ in range(rng.choice([0, 2, 5, 10, 16])):
                s = simple_tris(A)
                if s:
                    A = contract(A, rng.choice(s))
            for _ in range(rng.choice([0, 0, 2, 6])):
                s = simple_tris(A)
                if s:
                    A = flip(A, rng.choice(s))
            if rng.random() < 0.5:
                A = make_face(A, rng)
            A = from_tokens(A.tokens, n, complete=False)
        except (ValueError, AssertionError, IndexError):
            continue
        try:
            check(A, st, bad, f'w{wid}i{it}')
        except (AssertionError, ValueError, IndexError) as ex:
            bad.append(f'assert {ex!r}')
    return st, bad


if __name__ == '__main__':
    N, seed = int(sys.argv[1]), int(sys.argv[2])
    W = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    st, bad = Counter(), []
    with Pool(W) as pool:
        for s, b in pool.imap_unordered(worker, [(w, N, seed) for w in range(W)]):
            st.update(s)
            bad += b
    for k_ in sorted(st, key=str):
        print(st[k_], k_)
    print('FAILS', len(bad))
    for b in bad[:20]:
        print('  ', b[:200])

"""Order-free BBL parity and end lemmas, added as redundant (proven) clauses to T14's UnitModel.

CDCL cannot find BBL's alternation argument when the crossing order along a line is a variable (search/l3_sat.py:
L3 costs ~9x per two lines, but ~0.1 s once line 0's order is fixed). These lemmas state the argument without any
positions. They hold in every arrangement (proofs in work/bbl/THEORY.md section 12), so adding them is sound.

For a line L with no multiple point on it (so all its vertices are simple and no segment of L is doubly used, L1):
  P1 (parity)  if no bounded segment of L is unused, then the triangles on its first and last segments satisfy
               side_first XOR side_last = (n - 3) XOR (XOR over j of [L caps a block at L n j])       (mod 2).
  P2 (ends)    if the end segment at an end vertex V = L n N carries a triangle on side s only, then the first
               segment of N from V on side -s is unused (a touch on L) or unbounded.
Side convention (P1/P2 for simple lines below): only XORs / paired flips of the side are used, so a global swap of
"above" and "below" leaves them valid. side_rays() uses the true convention: T14's before(r, i, j) runs against the
sweep, and the point i n j lies above L iff [i < L] == before(i, L, j).
"""
from itertools import combinations


def add_parity_lemmas(m, lines=None, p1=True, p2=True):
    f, n = m.f, m.n
    R = range(n)
    lines = list(R) if lines is None else lines
    cnt = 0
    for L in lines:
        oth = [i for i in R if i != L]
        simple = -m.zl[L]
        first = {M: f.AND([m.before(L, M, j) for j in oth if j != M]) for M in oth}
        last = {N: f.AND([m.before(L, j, N) for j in oth if j != N]) for N in oth}

        def above(i, j):                        # literal: point i n j above L
            b = m.before(i, L, j)
            return -b if i < L else b

        up_f, any_f, up_l, any_l = [], [], [], []
        for M in oth:
            for M2 in oth:
                if M2 == M:
                    continue
                t = m.tri3(L, M, M2)
                ab = above(M, M2)
                up_f.append(f.AND([first[M], m.A[L, M, M2], t, ab]))
                any_f.append(f.AND([first[M], m.A[L, M, M2], t]))
                up_l.append(f.AND([last[M], m.A[L, M2, M], t, ab]))
                any_l.append(f.AND([last[M], m.A[L, M2, M], t]))
        sf, uf, sl, ul = f.OR(up_f), f.OR(any_f), f.OR(up_l), f.OR(any_l)
        if p1:
            nounused = f.AND([-m.usg[L, i, j] for i in oth for j in oth if i != j])
            caps = [f.OR([m.Bk[j, L, 1], m.Bk[j, L, -1]]) for j in oth]
            x = f.new()                          # x <-> sf xor sl
            f.add([-x, sf, sl]); f.add([-x, -sf, -sl]); f.add([x, -sf, sl]); f.add([x, sf, -sl])
            for c in caps:
                y = f.new()
                f.add([-y, x, c]); f.add([-y, -x, -c]); f.add([y, -x, c]); f.add([y, x, -c])
                x = y
            want = (n - 3) % 2                   # x must equal want when L is simple and has no unused segment
            f.add([-simple, -nounused, -uf, -ul, x if want else -x])
            cnt += 1
        if p2:
            for (endv, used, s_up) in ((last, ul, sl), (first, uf, sf)):
                for N in oth:
                    for s in (1, -1):            # s = +1: the end triangle is above L
                        # the other side is -s; along N, direction +1 from V lies above L iff N > L
                        other_above = (s == -1)
                        dirn = 1 if (N > L) == other_above else -1
                        f.add([-simple, -endv[N], -used, (-s_up if s == 1 else s_up),
                               m.uout[N, L, dirn], m.last[N, L, dirn]])
                        cnt += 1
    return cnt


def side_rays(m):
    """up[L, j, d] / dn[L, j, d]: the face above / below the first segment of L from the point of j (class expanded)
    in direction d is a triangle. Built from t3(L, x, y) with the apex side read off the labels (see module doc)."""
    if hasattr(m, "_side_rays"):
        return m._side_rays
    f, n = m.f, m.n
    R = range(n)
    z3 = lambda a, b, c: m.z[tuple(sorted((a, b, c)))]  # noqa: E731
    upF, dnF = {}, {}
    for L in R:
        oth = [i for i in R if i != L]
        for x in oth:
            for d in (1, -1):
                us, ds = [], []
                for y in oth:
                    if y == x:
                        continue
                    t = m.tri3(L, x, y)
                    dirl = m.before(L, x, y) if d == 1 else m.before(L, y, x)
                    b = m.before(x, L, y)
                    # T14's before(r, i, j) runs against the sweep. So before(x, L, y) means y's point comes before L's
                    # in the sweep on x, i.e. on x's starting side of L: above L iff x < L.
                    ab = b if x < L else -b          # apex x n y above L
                    us.append(f.AND([t, dirl, ab]))
                    ds.append(f.AND([t, dirl, -ab]))
                upF[L, x, d] = f.OR(us)
                dnF[L, x, d] = f.OR(ds)
    up, dn = {}, {}
    for L in R:
        oth = [i for i in R if i != L]
        for j in oth:
            for d in (1, -1):
                up[L, j, d] = f.OR([upF[L, j, d]] + [f.AND([z3(L, j, k), upF[L, k, d]]) for k in oth if k != j])
                dn[L, j, d] = f.OR([dnF[L, j, d]] + [f.AND([z3(L, j, k), dnF[L, k, d]]) for k in oth if k != j])
    m._side_rays = (up, dn)
    return up, dn


def _xor2(f, a, b):
    x = f.new()
    f.add([-x, a, b]); f.add([-x, -a, -b]); f.add([x, -a, b]); f.add([x, a, -b])
    return x


def add_general_parity(m, lines=None):
    """P1g (a tautology, valid for every line of every arrangement): with sigma(L, V, d) = [the first segment of L from
    vertex V in direction d carries a triangle above L and none below], the XOR over the vertices V of L of
    sigma(L, V, -1) XOR sigma(L, V, +1) is 0 (each bounded segment is counted at both ends, unbounded rays give 0).
    Vertices are represented by their canonical (smallest-label) line, repl[L, j]."""
    f, n = m.f, m.n
    up, dn = side_rays(m)
    cnt = 0
    for L in (range(n) if lines is None else lines):
        acc = None
        for j in range(n):
            if j == L:
                continue
            sm = f.AND([up[L, j, -1], -dn[L, j, -1]])
            sp = f.AND([up[L, j, 1], -dn[L, j, 1]])
            term = f.AND([m.repl[L, j], _xor2(f, sm, sp)])
            acc = term if acc is None else _xor2(f, acc, term)
        f.add([-acc])
        cnt += 1
    return cnt


def add_general_ends(m, lines=None):
    """P2g: at a simple end vertex V = L n N of L, if the end segment of L carries a triangle on one side only, then
    the first segment of N from V on the other side is unused (a touch on L) or unbounded."""
    f, n = m.f, m.n
    up, dn = side_rays(m)
    cnt = 0
    for L in (range(n) if lines is None else lines):
        oth = [i for i in range(n) if i != L]
        for N in oth:
            last = f.AND([m.before(L, j, N) for j in oth if j != N])
            first = f.AND([m.before(L, N, j) for j in oth if j != N])
            # T14 direction +1 along N from V goes back to N's starting side of L: above L iff N < L
            below = -1 if N < L else 1            # direction along N from V that lies below L
            for endv, inward in ((last, -1), (first, 1)):
                only_up = f.AND([up[L, N, inward], -dn[L, N, inward]])
                only_dn = f.AND([dn[L, N, inward], -up[L, N, inward]])
                f.add([-endv, -only_up, m.uout[N, L, below], m.last[N, L, below]])
                f.add([-endv, -only_dn, m.uout[N, L, -below], m.last[N, L, -below]])
                cnt += 2
    return cnt

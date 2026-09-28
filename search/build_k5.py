"""Build the k5 instance (C32 spec): 18 lines, 94 triangles, exactly 5 triple points, no bridge (beta = 0),
B = 10, exactly one unused segment u0 (Z = 1).

Claim tags (work/loop/ledger.md): C5, C10, C14, C17 (Statement 1; Statement 2 weakened at u0), C30, C31, C32.
  * segment-used clause with one slack s(r,i,j) per ordered consecutive pair, sum s = 1 (C30: Z = 0 impossible),
    s -> adjacency, both endpoints simple, u0 not an end segment, not a triangle side (C30);
  * every triple point is type X (>= 4 triangles at it) and no line end (C30);
  * lines avoiding all triple points are caps, except clean lines cl(L), sum cl <= 1 (C30/C31: clean = 2 dead);
  * 11 <= #triple lines <= 13 (sigma in [2, 4]);
  * some line carries two triple points (Theorem H); line 0 avoids every triple point (C32 (a) 7).

    uv run --no-project --with python-sat python search/build_k5.py <out.cnf>
Writes <out>.ids.json (pz, ng, z, tri, s, F/G first/last, tl, cl, top) for the cube generator.
"""
import argparse
import json
import sys
from itertools import combinations, permutations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kobon_sat import build_defect  # noqa: E402
from pysat.card import CardEnc, EncType  # noqa: E402

n, k = 18, 5
S = lambda *x: tuple(sorted(x))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    a = ap.parse_args()
    cnf, z, pz, ng, tri, budget = build_defect(n, 94, k, alternate=True, card="cardnetwrk", exact_triple=True, blanc=True)
    pool = cnf.pool
    trip = list(z)
    A = lambda r, i, j: pool.id(("adj", r, i, j))
    before = lambda r, i, j: ng[S(r, i, j)] if i < j else pz[S(r, i, j)]  # i's crossing precedes j's on r
    # C10 (Lemma A local clause)
    for t in trip:
        for x in t:
            b, c = [y for y in t if y != x]
            for C in range(n):
                if C in t:
                    continue
                for N in range(n):
                    if N in t or N == C:
                        continue
                    cnf.append([-z[t], -tri[S(x, b, C)], -tri[S(x, c, C)], -tri[S(x, C, N)], z[S(b, C, N)], z[S(c, C, N)]])
    # C14/C30: every consecutive pair is a side of a triangle through its endpoints, except the one slack s = u0
    s = {}
    for r, i, j in permutations(range(n), 3):
        lits = [-A(r, i, j), tri[S(r, i, j)]]
        for x in range(n):
            if x in (r, i, j):
                continue
            w = pool.id(("usedvia_i", r, i, j, x))
            cnf.extend([[-w, z[S(r, i, x)]], [-w, tri[S(r, x, j)]]])
            lits.append(w)
            w2 = pool.id(("usedvia_j", r, i, j, x))
            cnf.extend([[-w2, z[S(r, j, x)]], [-w2, tri[S(r, i, x)]]])
            lits.append(w2)
        for x in range(n):
            for y in range(n):
                if len({r, i, j, x, y}) < 5:
                    continue
                w3 = pool.id(("usedvia_ij", r, i, j, x, y))
                cnf.extend([[-w3, z[S(r, i, x)]], [-w3, z[S(r, j, y)]], [-w3, tri[S(r, x, y)]]])
                lits.append(w3)
        v = pool.id(("slack", r, i, j))
        s[r, i, j] = v
        cnf.append(lits + [v])
        # u0 = [r∩i, r∩j]: consecutive, both endpoints simple, not an end segment of r, not a triangle side
        cnf.append([-v, A(r, i, j)])
        cnf.append([-v, -tri[S(r, i, j)]])
        for x in range(n):
            if x not in (r, i, j):
                cnf.extend([[-v, -z[S(r, i, x)]], [-v, -z[S(r, j, x)]]])
        cnf.append([-v] + [before(r, M, i) for M in range(n) if M not in (r, i, j)])
        cnf.append([-v] + [before(r, j, M) for M in range(n) if M not in (r, i, j)])
    for cl in CardEnc.equals(lits=list(s.values()), bound=1, vpool=pool, encoding=EncType.seqcounter).clauses:
        cnf.append(cl)
    # beta = 0: a segment between two triple points is a side of at most one triangle
    for r in range(n):
        for i, i2 in combinations([x for x in range(n) if x != r], 2):
            for j, j2 in combinations([x for x in range(n) if x not in (r, i, i2)], 2):
                reps = [(i, j), (i, j2), (i2, j), (i2, j2)]
                base = [-z[S(r, i, i2)], -z[S(r, j, j2)]]
                for (x1, y1), (x2, y2) in combinations(reps, 2):
                    for adj in (A(r, i, j), A(r, j, i)):
                        cnf.append(base + [-adj, -tri[S(r, x1, y1)], -tri[S(r, x2, y2)]])
    # C30: every triple point is type X (its 4 cap triangles) and is no line end
    for t in trip:
        lits = [tri[S(x, y, L)] for x, y in combinations(t, 2) for L in range(n) if L not in t]
        for cl in CardEnc.atleast(lits=lits, bound=4, vpool=pool, encoding=EncType.seqcounter).clauses:
            cnf.append([-z[t]] + cl)
        for L in t:
            for a_ in t:
                if a_ == L:
                    continue
                cnf.append([-z[t]] + [before(L, M, a_) for M in range(n) if M not in t])
                cnf.append([-z[t]] + [before(L, a_, M) for M in range(n) if M not in t])
    # C30/C31: a line avoiding all triple points is a cap line or one of at most one clean line
    cls = []
    for L in range(n):
        c_ = pool.id(("clean", L))
        cls.append(c_)
        cnf.append([z[t] for t in trip if L in t] + [pool.id(("cap", L) + t) for t in trip if L not in t] + [c_])
        cnf.extend([[-c_, -z[t]] for t in trip if L in t])  # a clean line avoids the triple points
    for cl in CardEnc.atmost(lits=cls, bound=1, vpool=pool, encoding=EncType.seqcounter).clauses:
        cnf.append(cl)
    # triple-line indicators, 11 <= tau <= 13
    tl = []
    for L in range(n):
        v = pool.id(("tl", L))
        on = [z[t] for t in trip if L in t]
        cnf.extend([[-x, v] for x in on])
        cnf.append([-v] + on)
        tl.append(v)
    for cl in CardEnc.atleast(lits=tl, bound=11, vpool=pool, encoding=EncType.seqcounter).clauses + \
            CardEnc.atmost(lits=tl, bound=13, vpool=pool, encoding=EncType.seqcounter).clauses:
        cnf.append(cl)
    # C5 (Theorem H): some line carries two triple points; WLOG line 0 avoids every triple point
    shared = []
    for L in range(n):
        lits = [z[t] for t in trip if L in t]
        sh = pool.id(("shared2", L))
        for cl in CardEnc.atleast(lits=lits, bound=2, vpool=pool, encoding=EncType.seqcounter).clauses:
            cnf.append([-sh] + cl)
        shared.append(sh)
    cnf.append(shared)
    for t in trip:
        if 0 in t:
            cnf.append([-z[t]])
    # C17 Statement 1 (unconditional) and Statement 2 weakened at u0 (C32 (b))
    first = lambda L, R: [x for M in range(n) if M not in (L, R) for x in (-before(L, M, R), -z[S(L, R, M)])]
    last = lambda L, R: [x for M in range(n) if M not in (L, R) for x in (-before(L, R, M), -z[S(L, R, M)])]
    forbid = lambda c1, c2: cnf.append(sorted({-x for x in c1 + c2}))
    for L, R in combinations(range(n), 2):
        if {L, R} == {0, n - 1}:
            combos = [(first(L, R), first(R, L)), (last(L, R), last(R, L))]
        elif R - L == 1:
            combos = [(first(L, R), last(R, L)), (last(L, R), first(R, L))]
        else:
            combos = [(first(L, R), first(R, L)), (last(L, R), last(R, L)), (first(L, R), last(R, L)), (last(L, R), first(R, L))]
        for c1, c2 in combos:
            forbid(c1, c2)

    def conj(name, lits):  # v <-> AND(lits)
        v = pool.id(name)
        cnf.extend([[-v, x] for x in lits])
        cnf.append([v] + [-x for x in lits])
        return v
    F = {(L, R): conj(("c17f", L, R), first(L, R)) for L, R in permutations(range(n), 2)}
    G = {(L, R): conj(("c17l", L, R), last(L, R)) for L, R in permutations(range(n), 2)}
    for L, R in permutations(range(n), 2):
        both = []
        for s1, s2 in combinations([x for x in range(n) if x not in (L, R)], 2):
            w = pool.id(("c17both", L, R, s1, s2))
            cnf.extend([[-w, z[S(L, s1, s2)]], [-w, tri[S(L, R, s1)]], [-w, tri[S(L, R, s2)]]])
            both.append(w)
        touch = [s[R, L, x] for x in range(n) if x not in (L, R)] + [s[R, x, L] for x in range(n) if x not in (L, R)]
        for end in (F, G):
            cnf.append([-end[L, R], F[R, L], G[R, L]] + both + touch)
    cnf.to_file(a.out)
    key = lambda t: ",".join(map(str, t))
    json.dump({"top": pool.top, "pz": {key(t): v for t, v in pz.items()}, "ng": {key(t): v for t, v in ng.items()},
               "z": {key(t): v for t, v in z.items()}, "tri": {key(t): v for t, v in tri.items()},
               "s": {key(t): v for t, v in s.items()}, "c17f": {key(t): v for t, v in F.items()},
               "c17l": {key(t): v for t, v in G.items()}, "tl": tl, "clean": cls},
              open(Path(a.out).with_suffix(".ids.json"), "w"))
    print(f"{a.out}: vars {pool.top}, clauses {len(cnf.clauses)}")


if __name__ == "__main__":
    main()

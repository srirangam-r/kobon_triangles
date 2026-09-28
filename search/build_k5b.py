"""k5b instance (C36 spec, sections 1-2): 18 lines, 94 triangles, exactly 5 triple points, at least one doubly used
bridge (beta >= 1). Tags: C5 (shared line; line 0 off triple points), C10, C17 Statement 1, C35 (sector classes,
valid since k <= 4 is closed by C25), C36 section 2 (beta >= 1). C36 sections 3-4 are not encoded.

    uv run --no-project --with python-sat python search/build_k5b.py <out.cnf>
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


def at_least(cnf, pool, lits, jmax, name):
    """One-directional counter: returns g[j] (j = 1..jmax) with g[j] -> at least j of lits are true."""
    prev = [None] * (jmax + 1)  # prev[j]: "at least j among the first i lits"; None = false
    for i, x in enumerate(lits):
        cur = [None] * (jmax + 1)
        for j in range(1, jmax + 1):
            v = pool.id((name, i, j))
            # v -> prev[j] or (x and prev[j-1])
            a_ = prev[j]
            b_ = prev[j - 1] if j > 1 else True
            cnf.append([-v] + ([a_] if a_ else []) + [x])
            if b_ is not True:
                cnf.append([-v] + ([a_] if a_ else []) + ([b_] if b_ else []))
            cur[j] = v
        prev = cur
    return prev


def add_dz(cnf, pool, z, tri, trip, bf, brs):
    """C36 section 3: D - Z >= 9 (sound weakened form). D >= blocks + doubly used bridges, Z >= unused segments
    with two simple endpoints; each count is one-directional, so a real 94 satisfies it with the true values."""
    A = lambda r, i, j: pool.id(("adj", r, i, j))
    us = []
    for r, i, j in permutations(range(n), 3):  # u forced when (r: i,j) is consecutive, not a triangle side, both ends simple
        lits = [-A(r, i, j), tri[S(r, i, j)]]
        for x in range(n):
            if x not in (r, i, j):
                lits += [z[S(r, i, x)], z[S(r, j, x)]]
        u = pool.id(("unused", r, i, j))
        cnf.append(lits + [u])
        us.append(u)
    blk_counts = []
    for t in trip:  # blk(t, a, C) -> z[t] and the two cap triangles on a's first segment towards C
        bl = []
        for a_ in t:
            b_, c_ = [y for y in t if y != a_]
            for C in range(n):
                if C in t:
                    continue
                v = pool.id(("blk", t, a_, C))
                cnf.extend([[-v, z[t]], [-v, tri[S(a_, b_, C)]], [-v, tri[S(a_, c_, C)]]])
                bl.append(v)
        g = at_least(cnf, pool, bl, 3, ("cb", t))
        blk_counts += [g[j] for j in (1, 2, 3)]
    by_line = {}
    for v in brs:
        by_line.setdefault(pool.obj(v)[1], []).append(v)
    br_counts = []
    for r, vs in by_line.items():
        g = at_least(cnf, pool, vs, 4, ("cr", r))
        br_counts += [g[j] for j in (1, 2, 3, 4)]
    M = 8
    G = at_least(cnf, pool, blk_counts + br_counts, 9 + M, "cg")
    # forward counter on u: s[m] is forced true when at least m of the u are true
    s_prev = [None] * (M + 1)
    for i, x in enumerate(us):
        s_cur = [None] * (M + 1)
        for m in range(1, min(i + 1, M) + 1):
            v = pool.id(("cu", i, m))
            if s_prev[m]:
                cnf.append([-s_prev[m], v])
            if m == 1:
                cnf.append([-x, v])
            elif s_prev[m - 1]:
                cnf.append([-x, -s_prev[m - 1], v])
            s_cur[m] = v
        s_prev = s_cur
    cnf.append([G[9]])  # D >= 9 + Z_simple, applied for Z_simple = 0..M (weaker, still sound, beyond M)
    for m in range(1, M + 1):
        cnf.append([-s_prev[m], G[9 + m]])


def build(dz=False):
    """The k5b base (see module docstring); returns (cnf, pool, z, tri, pz, ng, trip, bf, brs)."""
    cnf, z, pz, ng, tri, budget = build_defect(n, 94, k, alternate=True, card="cardnetwrk", exact_triple=True, blanc=True)
    pool = cnf.pool
    trip = list(z)
    bf = lambda r, i, j: ng[S(r, i, j)] if i < j else pz[S(r, i, j)]  # on r, i's crossing precedes j's
    for t in trip:  # C10
        for x in t:
            b, c = [y for y in t if y != x]
            for C in range(n):
                if C in t:
                    continue
                for N in range(n):
                    if N not in t and N != C:
                        cnf.append([-z[t], -tri[S(x, b, C)], -tri[S(x, c, C)], -tri[S(x, C, N)], z[S(b, C, N)], z[S(c, C, N)]])
    # C35 sector classes: z[t] -> at least 2 of the 3 sectors of each alternating class carry a triangle
    for t in trip:
        A_, B_, C_ = t
        rows = {"k1": [(A_, B_, lambda L: (bf(A_, B_, L), bf(B_, A_, L))), (B_, C_, lambda L: (bf(B_, L, C_), bf(C_, L, B_))),
                       (A_, C_, lambda L: (bf(A_, L, C_), bf(C_, A_, L)))],
                "k2": [(A_, B_, lambda L: (bf(A_, L, B_), bf(B_, L, A_))), (B_, C_, lambda L: (bf(B_, C_, L), bf(C_, B_, L))),
                       (A_, C_, lambda L: (bf(A_, C_, L), bf(C_, L, A_)))]}
        for cls, rs in rows.items():
            secs = []
            for idx, (x, y, dirs) in enumerate(rs):
                sec = pool.id(("sec", t, cls, idx))
                ws = []
                for L in range(n):
                    if L in t:
                        continue
                    w = pool.id(("secw", t, cls, idx, L))
                    d1, d2 = dirs(L)
                    cnf.extend([[-w, tri[S(x, y, L)]], [-w, d1], [-w, d2]])
                    ws.append(w)
                cnf.append([-sec] + ws)
                secs.append(sec)
            for p, q in combinations(secs, 2):
                cnf.append([-z[t], p, q])
    # beta >= 1: some segment between two triple points on a line r is a side of two triangles
    brs = []
    for r in range(n):
        ts = [t for t in trip if r in t]
        for t1, t2 in combinations(ts, 2):
            o1, o2 = [x for x in t1 if x != r], [y for y in t2 if y != r]
            if set(o1) & set(o2):
                continue
            (x, x2), (y, y2) = o1, o2
            for (p1, q1), (p2, q2) in (((x, y), (x2, y2)), ((x, y2), (x2, y))):
                v = pool.id(("br", r, t1, t2, p1, q1))
                cnf.extend([[-v, z[t1]], [-v, z[t2]], [-v, tri[S(r, p1, q1)]], [-v, tri[S(r, p2, q2)]]])
                brs.append(v)
    cnf.append(brs)
    if dz:
        add_dz(cnf, pool, z, tri, trip, bf, brs)
    # C5: some line carries two triple points; line 0 avoids every triple point
    shared = []
    for L in range(n):
        lits = [z[t] for t in trip if L in t]
        sh = pool.id(("shared2", L))
        for cl in CardEnc.atleast(lits=lits, bound=2, vpool=pool, encoding=EncType.seqcounter).clauses:
            cnf.append([-sh] + cl)
        shared.append(sh)
    cnf.append(shared)
    cnf.extend([[-z[t]] for t in trip if 0 in t])
    # C17 Statement 1 (unconditional)
    first = lambda L, R: [x for M in range(n) if M not in (L, R) for x in (-bf(L, M, R), -z[S(L, R, M)])]
    last = lambda L, R: [x for M in range(n) if M not in (L, R) for x in (-bf(L, R, M), -z[S(L, R, M)])]
    for L, R in combinations(range(n), 2):
        if {L, R} == {0, n - 1}:
            combos = [(first(L, R), first(R, L)), (last(L, R), last(R, L))]
        elif R - L == 1:
            combos = [(first(L, R), last(R, L)), (last(L, R), first(R, L))]
        else:
            combos = [(first(L, R), first(R, L)), (last(L, R), last(R, L)), (first(L, R), last(R, L)), (last(L, R), first(R, L))]
        for c1, c2 in combos:
            cnf.append(sorted({-x for x in c1 + c2}))
    return cnf, pool, z, tri, pz, ng, trip, bf, brs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--dz", action="store_true", help="C36 section 3: D - Z >= 9 with aggregated counters")
    a = ap.parse_args()
    cnf, pool, z, tri, pz, ng, trip, bf, brs = build(a.dz)
    cnf.to_file(a.out)
    json.dump({"n": n, "pz": {f"{x},{y},{w}": v for (x, y, w), v in pz.items() if x == 0},
               "ng": {f"{x},{y},{w}": v for (x, y, w), v in ng.items() if x == 0}}, open(Path(a.out).with_suffix(".spec.json"), "w"))
    print(f"{a.out}: vars {pool.top}, clauses {len(cnf.clauses)}, bridge options {len(brs)}")


if __name__ == "__main__":
    main()

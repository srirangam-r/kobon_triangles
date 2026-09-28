"""k5b instance (C36 spec, sections 1-2): 18 lines, 94 triangles, exactly 5 triple points, at least one doubly used
bridge (beta >= 1). Tags: C5 (shared line; line 0 off triple points), C10, C17 Statement 1, C35 (sector classes,
valid since k <= 4 is closed by C25), C36 section 2 (beta >= 1). C36 sections 3-4 are not encoded.

    uv run --no-project --with python-sat python search/build_k5b.py <out.cnf>
"""
import argparse
import json
import sys
from itertools import combinations
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
    cnf.to_file(a.out)
    json.dump({"n": n, "pz": {f"{x},{y},{w}": v for (x, y, w), v in pz.items() if x == 0},
               "ng": {f"{x},{y},{w}": v for (x, y, w), v in ng.items() if x == 0}}, open(Path(a.out).with_suffix(".spec.json"), "w"))
    print(f"{a.out}: vars {pool.top}, clauses {len(cnf.clauses)}, bridge options {len(brs)}")


if __name__ == "__main__":
    main()

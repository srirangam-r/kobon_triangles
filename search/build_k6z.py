"""Build the k6z instance: 18 lines, 94 triangles, exactly 6 triple points, no bridge (beta = 0).

Encodes (claim tags from work/loop/ledger.md):
  C10  Lemma A as a local clause
  C14  k=6, beta=0 => Z = 0 (every segment is a side of some triangle), non-triple lines are caps
  C5   not general position: some line carries two triple points; line 0 avoids them all
  C17  (--c17) mutual ends are slope-adjacent, and under Z = 0 a simple first/last vertex whose
       first segment is singly used is a mutual end
  C16  (--c16) triple-line indicators tl[L] and guarded counts: sel_u4 => exactly 14 triple lines,
       sel_u6 => 12..15 (sigma = 18 - tau, with sigma = 4 for u = 4 and 3 <= sigma <= 6 for u = 6).
       Cubes set sel_u4 or sel_u6 and tl[L] for the line of every cap-point end (an axis).

    uv run --no-project --with python-sat python search/build_k6z.py <out.cnf> [--c17]
"""
import argparse
import json
import sys
from itertools import combinations, permutations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kobon_sat import build_defect  # noqa: E402
from pysat.card import CardEnc, EncType  # noqa: E402

n, k = 18, 6
S = lambda *x: tuple(sorted(x))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--c17", action="store_true")
    ap.add_argument("--c16", action="store_true")
    ap.add_argument("--dump-ids", action="store_true", help="write <out>.ids.json with pz, ng, z, tri for all triples")
    a = ap.parse_args()
    cnf, z, pz, ng, tri, budget = build_defect(n, 94, k, alternate=True, card="cardnetwrk", exact_triple=True, blanc=True)
    pool = cnf.pool
    trip = list(z)
    A = lambda r, i, j: pool.id(("adj", r, i, j))
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
    # C14: Z = 0. Every consecutive pair (i, j) on r is a side of a triangle through its endpoints;
    # the endpoint of i on r is shared with i' iff z(r, i, i').
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
        cnf.append(lits)
    # beta = 0: a segment between two triple points is a side of at most one triangle
    for r in range(n):
        for i, i2 in combinations([x for x in range(n) if x != r], 2):
            for j, j2 in combinations([x for x in range(n) if x not in (r, i, i2)], 2):
                reps = [(i, j), (i, j2), (i2, j), (i2, j2)]
                base = [-z[S(r, i, i2)], -z[S(r, j, j2)]]
                for (x1, y1), (x2, y2) in combinations(reps, 2):
                    for adj in (A(r, i, j), A(r, j, i)):
                        cnf.append(base + [-adj, -tri[S(r, x1, y1)], -tri[S(r, x2, y2)]])
    # C14: every line avoiding all triple points is a cap line
    for L in range(n):
        cnf.append([z[t] for t in trip if L in t] + [pool.id(("cap", L) + t) for t in trip if L not in t])
    # C5 (Theorem H): not general position; WLOG line 0 avoids every triple point
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
    n17 = 0
    if a.c17:
        before = lambda r, i, j: ng[S(r, i, j)] if i < j else pz[S(r, i, j)]  # i's crossing precedes j's on r
        # first(L,R) = L∩R is L's first vertex and simple; each conjunct listed as a literal
        first = lambda L, R: [x for M in range(n) if M not in (L, R) for x in (-before(L, M, R), -z[S(L, R, M)])]
        last = lambda L, R: [x for M in range(n) if M not in (L, R) for x in (-before(L, R, M), -z[S(L, R, M)])]
        forbid = lambda c1, c2: cnf.append(sorted({-x for x in c1 + c2}))
        # Statement 1: a mutual end is a wedge at infinity, so its two rays are adjacent in the circular order
        for L, R in combinations(range(n), 2):
            if {L, R} == {0, n - 1}:
                combos = [(first(L, R), first(R, L)), (last(L, R), last(R, L))]
            elif R - L == 1:
                combos = [(first(L, R), last(R, L)), (last(L, R), first(R, L))]
            else:
                combos = [(first(L, R), first(R, L)), (last(L, R), last(R, L)), (first(L, R), last(R, L)), (last(L, R), first(R, L))]
            for c1, c2 in combos:
                forbid(c1, c2)
                n17 += 1
        # Statement 2 (Z = 0): if L∩R is L's first (last) vertex, simple, and not an end of R, then the first
        # (last) segment of L is doubly used, so the next vertex is a triple point L,S,S' with tri(L,R,S), tri(L,R,S')
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
            for end in (F, G):
                cnf.append([-end[L, R], F[R, L], G[R, L]] + both)
                n17 += 1
    extra16 = {}
    if a.c16:
        tl = []
        for L in range(n):
            v = pool.id(("c16tl", L))  # v <-> L passes through a triple point
            on = [z[t] for t in trip if L in t]
            cnf.extend([[-z_, v] for z_ in on])
            cnf.append([-v] + on)
            tl.append(v)
        s4, s6 = pool.id(("c16sel", 4)), pool.id(("c16sel", 6))
        for sel, lo, hi in ((s4, 14, 14), (s6, 12, 15)):
            for cl in CardEnc.atleast(lits=tl, bound=lo, vpool=pool, encoding=EncType.seqcounter).clauses:
                cnf.append([-sel] + cl)
            for cl in CardEnc.atmost(lits=tl, bound=hi, vpool=pool, encoding=EncType.seqcounter).clauses:
                cnf.append([-sel] + cl)
        extra16 = {"tl": tl, "sel": {"4": s4, "6": s6}}
    cnf.to_file(a.out)
    spec = Path(a.out).with_suffix(".spec.json")
    extra = {}
    if a.c17:  # variable ids of first/last(L,R), for cubes on the structure at infinity
        extra = {"c17f": {f"{L},{R}": v for (L, R), v in F.items()}, "c17l": {f"{L},{R}": v for (L, R), v in G.items()}}
    json.dump({"n": n, "pz": {f"{x},{y},{w}": v for (x, y, w), v in pz.items() if x == 0},
               "ng": {f"{x},{y},{w}": v for (x, y, w), v in ng.items() if x == 0}} | extra | extra16, open(spec, "w"))
    if a.dump_ids:
        key = lambda t: ",".join(map(str, t))
        json.dump({"top": pool.top, "pz": {key(t): v for t, v in pz.items()}, "ng": {key(t): v for t, v in ng.items()},
                   "z": {key(t): v for t, v in z.items()}, "tri": {key(t): v for t, v in tri.items()}},
                  open(Path(a.out).with_suffix(".ids.json"), "w"))
    print(f"{a.out}: vars {pool.top}, clauses {len(cnf.clauses)}, C17 clauses {n17}")


if __name__ == "__main__":
    main()

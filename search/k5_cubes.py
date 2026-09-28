"""Cubes for k5 (C32 (c)): one per row of work/t3/k5_patterns.jsonl (clean <= 1, K = 4).

Row: N (6 non-wedge end positions), t (touch end), s0 (U0's singleton), match (two mutual pairs of the other 4
singletons), wedges. Position p: line p % 18, left end if p < 18 ("from p" = left to right), else right end.
Per row:
  * wedges (p, q): end(p, line q) and end(q, line p) (c17f / c17l units);
  * every singleton p: 2nd vertex from p is a triple point l∩b∩c with at most one line before it, with blocks
    at the 1st and 3rd vertices (tri(l,b,x), tri(l,c,x) on each side)  [C26 (a)/(b) shape, C30];
  * match (p, p'): line p meets line p' at the 3rd vertex from each singleton end (exactly 3 lines before, simple),
    with P's block there: tri(l,b,l'), tri(l,c,l')  [C26 (c)];
  * s0 / t (a = line s0, L = line t): L∩a is L's end at t and a's 4th vertex from s0 (exactly 4 lines before);
    the slack u0 sits on a's consecutive pair (D, L) oriented from s0  [C30, C31, C32 (c)].

    uv run --no-project --with python-sat python search/k5_cubes.py <k5.ids.json> <patterns.jsonl> <out.jsonl> <k5.cnf>
New variables start after max(ids top, the base CNF's declared nv).
"""
import json
import sys
from itertools import combinations

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool


def main(ids_path, pat_path, out, base_cnf):
    ids = json.load(open(ids_path))
    with open(base_cnf) as fh:
        top0 = max(ids["top"], int(fh.readline().split()[2]))
    key = lambda *t: ",".join(map(str, t))
    S3 = lambda *t: key(*sorted(t))
    pz, ng, z, tri, sl, F, G = ids["pz"], ids["ng"], ids["z"], ids["tri"], ids["s"], ids["c17f"], ids["c17l"]
    before = lambda r, i, j: ng[S3(r, i, j)] if i < j else pz[S3(r, i, j)]
    end = lambda p, other: (F if p < 18 else G)[key(p % 18, other)]
    n = 0
    with open(out, "w") as fh:
        for row in map(json.loads, open(pat_path)):
            pool = IDPool(start_from=top0 + 1)
            units, clauses = [], []
            for p, q in row["wedges"]:
                units += [end(p, q % 18), end(q, p % 18)]
            singles = [p for p in row["N"] if p != row["t"]]
            for p in singles:  # C26 (a)/(b) shape at a singleton end
                L, left = p % 18, p < 18
                bef = lambda x, y, L=L, left=left: before(L, x, y) if left else before(L, y, x)
                ws = []
                for b, c in combinations([x for x in range(18) if x != L], 2):
                    w = pool.id(("w", p, b, c))
                    ws.append(w)
                    rest = [x for x in range(18) if x not in (L, b, c)]
                    clauses.append([-w, z[S3(L, b, c)]])
                    for cl in CardEnc.atmost(lits=[bef(x, b) for x in rest], bound=1, vpool=pool, encoding=EncType.seqcounter).clauses:
                        clauses.append([-w] + cl)
                    v1s, v2s = [], []
                    for x in rest:
                        v1, v2 = pool.id(("v1", p, b, c, x)), pool.id(("v2", p, b, c, x))
                        clauses += [[-v1, bef(x, b)], [-v1, tri[S3(L, b, x)]], [-v1, tri[S3(L, c, x)]],
                                    [-v2, bef(b, x)], [-v2, tri[S3(L, b, x)]], [-v2, tri[S3(L, c, x)]]]
                        v1s.append(v1)
                        v2s.append(v2)
                    clauses += [[-w] + v1s, [-w] + v2s]
                clauses.append(ws)

            def nth_vertex(p, L2, count, block):  # line p%18 meets L2 after exactly `count` lines, from end p
                L, left = p % 18, p < 18
                others = [x for x in range(18) if x not in (L, L2)]
                bef = {x: (before(L, x, L2) if left else before(L, L2, x)) for x in others}
                units.extend(-z[S3(L, L2, x)] for x in others)  # that vertex is simple
                clauses.extend(CardEnc.equals(lits=list(bef.values()), bound=count, vpool=pool, encoding=EncType.seqcounter).clauses)
                if block:  # the 2nd vertex's triple point L∩b∩c lies before L2, with P's block at L∩L2
                    wit = []
                    for b, c in combinations(others, 2):
                        w = pool.id(("m", p, L2, b, c))
                        clauses.extend([[-w, z[S3(L, b, c)]], [-w, bef[b]], [-w, bef[c]], [-w, tri[S3(L, b, L2)]], [-w, tri[S3(L, c, L2)]]])
                        wit.append(w)
                    clauses.append(wit)
            for p, q in row["match"]:
                nth_vertex(p, q % 18, 3, True)
                nth_vertex(q, p % 18, 3, True)
            s0, t = row["s0"], row["t"]
            a, L = s0 % 18, t % 18
            units.append(end(t, a))
            nth_vertex(s0, L, 4, False)
            if s0 < 18:  # left to right on a: (D, L) consecutive, u0 = [a∩D, a∩L]
                clauses.append([sl[key(a, D, L)] for D in range(18) if D not in (a, L)])
            else:
                clauses.append([sl[key(a, L, D)] for D in range(18) if D not in (a, L)])
            tag = "N%s_t%d_s%d" % ("_".join(map(str, row["N"])), t, s0)
            fh.write(json.dumps({"tag": tag, "units": units, "clauses": clauses, "top": pool.top}) + "\n")
            n += 1
    print(f"{n} cubes -> {out}")


if __name__ == "__main__":
    main(*sys.argv[1:5])

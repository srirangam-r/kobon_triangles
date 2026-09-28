"""Sub-cubes for C16 (B) (or any wedge cube): add the C26 (a)/(b) shape at every singleton end, without knowing
the matching. All ingredients are refereed-correct (C14, C16, C17, C26).

For a singleton end (l, e), counting vertices of l from e: X_1 = l∩C is simple, X_2 = l∩b∩c is a triple point
with axis l, P's blocks sit at X_1 (capped by C) and at X_3 = l∩D (capped by D), and X_3 is simple. Encoded as
    OR_{b<c} w(b,c),   w(b,c) -> z(l,b,c) ∧ AtMost1{x : x crosses l before b from e} ∧ OR_x v1 ∧ OR_x v2,
    v1(x) -> x before b from e ∧ tri(l,b,x) ∧ tri(l,c,x)          (the block at X_1, cap C = x)
    v2(x) -> b before x from e ∧ tri(l,b,x) ∧ tri(l,c,x)          (the block at X_3, cap D = x)
For u = 4 cubes on the k6z3 base, also the unit sel_u4 (C16 (B): sigma = 4, so exactly 14 triple lines) and
tl[l] for every singleton line (an axis passes through its point).

    uv run --no-project --with python-sat python search/wedge_cubes_single.py <ids.json> <spec3.json> <cubes.jsonl> <out.jsonl>
"""
import json
import sys
from itertools import combinations

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool


def main(ids_path, spec3_path, cubes_path, out):
    ids = json.load(open(ids_path))
    spec3 = json.load(open(spec3_path))
    top0 = max(ids["top"], max(spec3["tl"]), max(spec3["sel"].values()))
    S3 = lambda *t: ",".join(map(str, sorted(t)))
    pz, ng, z, tri = ids["pz"], ids["ng"], ids["z"], ids["tri"]
    before = lambda r, i, j: ng[S3(r, i, j)] if i < j else pz[S3(r, i, j)]
    n = 0
    with open(out, "w") as fh:
        for c in map(json.loads, open(cubes_path)):
            pool = IDPool(start_from=top0 + 1)
            units = list(c["units"]) + [spec3["sel"][str(c["u"])]] + sorted({spec3["tl"][p % 18] for p in c["S"]})
            clauses = []
            for p in c["S"]:
                L, left = p % 18, p < 18
                bef = lambda x, y: before(L, x, y) if left else before(L, y, x)  # x crosses L before y, from the end
                ws = []
                for b, cc in combinations([x for x in range(18) if x != L], 2):
                    w = pool.id(("w", p, b, cc))
                    ws.append(w)
                    rest = [x for x in range(18) if x not in (L, b, cc)]
                    clauses.append([-w, z[S3(L, b, cc)]])
                    for cl in CardEnc.atmost(lits=[bef(x, b) for x in rest], bound=1, vpool=pool, encoding=EncType.seqcounter).clauses:
                        clauses.append([-w] + cl)
                    v1s, v2s = [], []
                    for x in rest:
                        v1, v2 = pool.id(("v1", p, b, cc, x)), pool.id(("v2", p, b, cc, x))
                        clauses += [[-v1, bef(x, b)], [-v1, tri[S3(L, b, x)]], [-v1, tri[S3(L, cc, x)]],
                                    [-v2, bef(b, x)], [-v2, tri[S3(L, b, x)]], [-v2, tri[S3(L, cc, x)]]]
                        v1s.append(v1)
                        v2s.append(v2)
                    clauses += [[-w] + v1s, [-w] + v2s]
                clauses.append(ws)
            tag = "u%d_%s_single" % (c["u"], "_".join(map(str, c["S"])))
            fh.write(json.dumps({"tag": tag, "units": units, "clauses": clauses, "top": pool.top}) + "\n")
            n += 1
    print(f"{n} sub-cubes -> {out}")


if __name__ == "__main__":
    main(*sys.argv[1:5])

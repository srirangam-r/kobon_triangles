"""C16 (A) sub-cubes: a C27-admissible singleton set S plus one perfect matching of its singletons, with the
C26 (c) structure as extra clauses (all refereed-correct: C16, C17, C26, C27).

For a matched pair of singleton ends (l, e) <-> (l', e'), counting from the singleton end:
  * l meets l' at its 3rd vertex, which is simple: exactly 3 lines cross l strictly before l' (from e), and none
    passes through l∩l'; the same holds on l' from e';
  * the 2nd vertex from e is a triple point l∩b∩c with b, c among those 3 lines, and P's other block sits at the
    3rd vertex: tri(l, b, l') and tri(l, c, l')  [C26 (a), (b), (c)].
Matched singletons are at cyclic distance <= 5 and on different lines (C27, C26 (c)).

    uv run --no-project --with python-sat python search/wedge_cubes_c26.py <ids.json> <cubes.jsonl> <out.jsonl>
"""
import json
import sys
from itertools import combinations

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

dist = lambda a, b: min((a - b) % 36, (b - a) % 36)


def matchings(S):
    if not S:
        yield []
        return
    a = S[0]
    for b in S[1:]:
        if b % 18 != a % 18 and dist(a, b) <= 5:
            for m in matchings([x for x in S if x not in (a, b)]):
                yield [(a, b)] + m


def main(ids_path, cubes_path, out):
    ids = json.load(open(ids_path))
    S3 = lambda *t: ",".join(map(str, sorted(t)))
    pz, ng, z, tri = ids["pz"], ids["ng"], ids["z"], ids["tri"]
    before = lambda r, i, j: ng[S3(r, i, j)] if i < j else pz[S3(r, i, j)]
    n = 0
    with open(out, "w") as fh:
        for c in map(json.loads, open(cubes_path)):
            for M in matchings(sorted(c["S"])):
                pool = IDPool(start_from=ids["top"] + 1)
                units, clauses = list(c["units"]), []
                for p, q in M:
                    for (pa, pb) in ((p, q), (q, p)):
                        L, L2, left = pa % 18, pb % 18, pa < 18
                        others = [x for x in range(18) if x not in (L, L2)]
                        # "x crosses L strictly before L2, counted from L's singleton end"
                        bef = {x: (before(L, x, L2) if left else before(L, L2, x)) for x in others}
                        units += [-z[S3(L, L2, x)] for x in others]  # the 3rd vertex is simple
                        clauses += CardEnc.equals(lits=list(bef.values()), bound=3, vpool=pool, encoding=EncType.seqcounter).clauses
                        wit = []
                        for b, cc in combinations(others, 2):  # the 2nd vertex: triple point L∩b∩cc, P's block at the 3rd
                            w = pool.id(("w", L, L2, b, cc))
                            clauses += [[-w, z[S3(L, b, cc)]], [-w, bef[b]], [-w, bef[cc]],
                                        [-w, tri[S3(L, b, L2)]], [-w, tri[S3(L, cc, L2)]]]
                            wit.append(w)
                        clauses.append(wit)
                tag = "u6_%s_m%s" % ("_".join(map(str, c["S"])), "_".join(f"{a}-{b}" for a, b in M))
                fh.write(json.dumps({"tag": tag, "units": units, "clauses": clauses, "top": pool.top}) + "\n")
                n += 1
    print(f"{n} sub-cubes -> {out}")


if __name__ == "__main__":
    main(*sys.argv[1:4])

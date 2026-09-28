"""k5g: the k5b2 base (C10, C35 sectors, beta >= 1, D - Z >= 9, Theorem-H shared line, line 0 off triple points,
C17 Statement 1) plus generic constraints valid on every graph of the refereed k=5, beta>0 residue (C37-C50,
work/t3/k5_exceptions.jsonl: 28 graphs, B in [7,8], Z <= B + beta - 9 <= 5, each graph needs >= 1 exception):

  * segment-used clause with a slack s(r,i,j) on canonical representatives (smallest label at each endpoint),
    sum s <= 5  (Z <= 5);
  * C17 Statement 2 weakened at unused segments: a simple end vertex L∩R whose first segment is singly used is an
    end of R or lies on an unused segment of R (touch);
  * exact block indicators blk(t,a,C) <-> z[t] ∧ tri(a,b,C) ∧ tri(a,c,C); 7 <= B <= 8; no 3-block point;
  * at least one exception (C43 E2, C50 (ii), C50 (i)) in the necessary form:
      cap-point end  OR_{t,a,C} blk(t,a,C) ∧ (first(a,C) ∨ last(a,C))     [E2, (ii)]
      axis-cap line  OR_a (a is a block axis ∧ a caps a block)             [(i)]
Writes <out>.ids.json with the literal ids the cube generator needs.

    uv run --no-project --with python-sat python search/build_k5g.py <out.cnf>
"""
import argparse
import json
import sys
from itertools import combinations, permutations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_k5b import build, S, n  # noqa: E402
from pysat.card import CardEnc, EncType  # noqa: E402


def build_g(zmax=5):
    """The k5g instance; returns (cnf, pool, g) with g holding the named literals (see main for ids.json)."""
    cnf, pool, z, tri, pz, ng, trip, bf, brs = build(dz=True)
    A = lambda r, i, j: pool.id(("adj", r, i, j))
    # canonical slack: the clause for (r,i,j) is exempt unless i and j are the smallest lines at their endpoints
    s = {}
    for r, i, j in permutations(range(n), 3):
        lits = [-A(r, i, j), tri[S(r, i, j)]]
        for x in range(n):
            if x in (r, i, j):
                continue
            w = pool.id(("gvi", r, i, j, x)); cnf.extend([[-w, z[S(r, i, x)]], [-w, tri[S(r, x, j)]]]); lits.append(w)
            w2 = pool.id(("gvj", r, i, j, x)); cnf.extend([[-w2, z[S(r, j, x)]], [-w2, tri[S(r, i, x)]]]); lits.append(w2)
            if x < i:
                lits.append(z[S(r, i, x)])  # not canonical at i's endpoint
            if x < j:
                lits.append(z[S(r, j, x)])
        for x in range(n):
            for y in range(n):
                if len({r, i, j, x, y}) == 5:
                    w3 = pool.id(("gvij", r, i, j, x, y))
                    cnf.extend([[-w3, z[S(r, i, x)]], [-w3, z[S(r, j, y)]], [-w3, tri[S(r, x, y)]]]); lits.append(w3)
        v = pool.id(("gslack", r, i, j))
        s[r, i, j] = v
        cnf.append(lits + [v])
        cnf.append([-v, A(r, i, j)])
    for cl in CardEnc.atmost(lits=list(s.values()), bound=zmax, vpool=pool, encoding=EncType.seqcounter).clauses:
        cnf.append(cl)
    # first/last conjunctions (C17) and Statement 2 weakened with touches
    first = lambda L, R: [x for M in range(n) if M not in (L, R) for x in (-bf(L, M, R), -z[S(L, R, M)])]
    last = lambda L, R: [x for M in range(n) if M not in (L, R) for x in (-bf(L, R, M), -z[S(L, R, M)])]

    def conj(name, lits):
        v = pool.id(name)
        cnf.extend([[-v, x] for x in lits])
        cnf.append([v] + [-x for x in lits])
        return v
    F = {(L, R): conj(("gF", L, R), first(L, R)) for L, R in permutations(range(n), 2)}
    G = {(L, R): conj(("gG", L, R), last(L, R)) for L, R in permutations(range(n), 2)}
    for L, R in permutations(range(n), 2):
        both = []
        for s1, s2 in combinations([x for x in range(n) if x not in (L, R)], 2):
            w = pool.id(("gboth", L, R, s1, s2))
            cnf.extend([[-w, z[S(L, s1, s2)]], [-w, tri[S(L, R, s1)]], [-w, tri[S(L, R, s2)]]])
            both.append(w)
        # the touched unused segment of R contains L's crossing; its canonical representative may use any x
        touch = [s[R, L, x] for x in range(n) if x not in (L, R)] + [s[R, x, L] for x in range(n) if x not in (L, R)]
        for end in (F, G):
            cnf.append([-end[L, R], F[R, L], G[R, L]] + both + touch)
    # exact block indicators; 7 <= B <= 8; at most 2 blocks per point
    blk = {}
    for t in trip:
        per = []
        for a_ in t:
            b_, c_ = [y for y in t if y != a_]
            for C in range(n):
                if C in t:
                    continue
                v = pool.id(("blk", t, a_, C))  # defined one-directionally by add_dz; add the converse
                cnf.append([-z[t], -tri[S(a_, b_, C)], -tri[S(a_, c_, C)], v])
                blk[t, a_, C] = v
                per.append(v)
        for cl in CardEnc.atmost(lits=per, bound=2, vpool=pool, encoding=EncType.seqcounter).clauses:
            cnf.append(cl)
    bl = list(blk.values())
    for cl in CardEnc.atmost(lits=bl, bound=8, vpool=pool, encoding=EncType.seqcounter).clauses + \
            CardEnc.atleast(lits=bl, bound=7, vpool=pool, encoding=EncType.seqcounter).clauses:
        cnf.append(cl)
    # at least one exception
    cpe = {}  # cap-point end at line a towards cap C: blk(t,a,C) and C's crossing is a's first or last vertex
    for (t, a_, C), v in blk.items():
        w = pool.id(("gcpe", t, a_, C))
        cnf.extend([[-w, v], [-w, F[a_, C], G[a_, C]]])
        cpe[t, a_, C] = w
    axcap = []
    for a_ in range(n):
        ax, cp = pool.id(("gax", a_)), pool.id(("gcap", a_))
        cnf.append([-ax] + [v for (t, x, C), v in blk.items() if x == a_])
        cnf.append([-cp] + [v for (t, x, C), v in blk.items() if C == a_])
        w = pool.id(("gaxcap", a_))
        cnf.extend([[-w, ax], [-w, cp]])
        axcap.append(w)
    exc_any = list(cpe.values()) + axcap
    cnf.append(exc_any)
    g = dict(z=z, tri=tri, pz=pz, ng=ng, trip=trip, bf=bf, brs=brs, s=s, F=F, G=G, blk=blk, cpe=cpe, axcap=axcap)
    return cnf, pool, g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--zmax", type=int, default=5)
    a = ap.parse_args()
    cnf, pool, g = build_g(a.zmax)
    F, G, blk, cpe, axcap, pz, ng = (g[x] for x in ("F", "G", "blk", "cpe", "axcap", "pz", "ng"))
    cnf.to_file(a.out)
    key = lambda t: ",".join(map(str, t))
    json.dump({"top": pool.top, "F": {key(k): v for k, v in F.items()}, "G": {key(k): v for k, v in G.items()},
               "blk": {key((*t, a_, C)): v for (t, a_, C), v in blk.items()}, "cpe": {key((*t, a_, C)): v for (t, a_, C), v in cpe.items()},
               "axcap": axcap, "pz0": {f"{x},{y},{w}": v for (x, y, w), v in pz.items() if x == 0},
               "ng0": {f"{x},{y},{w}": v for (x, y, w), v in ng.items() if x == 0}},
              open(Path(a.out).with_suffix(".ids.json"), "w"))
    print(f"{a.out}: vars {pool.top}, clauses {len(cnf.clauses)}")


if __name__ == "__main__":
    main()

"""Diagnostic (not a proof instance): the k5L label layer on the bare pseudoline model with exactly 5 triple points
and NO triangle-count constraint (no 94 target, no D-count, no slack). Used to see whether per-graph cubes are
locally consistent and how fast locally impossible cubes die. Same variable names as kobon_sat.build_defect.

    uv run --no-project --with python-sat python search/build_k5L_local.py work/k5L/local.cnf
"""
import json
import sys
from itertools import combinations, permutations, product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kobon_sat import allowed4  # noqa: E402
from k5L_layer import add_labels, upper, S  # noqa: E402
from pysat.card import CardEnc, EncType  # noqa: E402
from pysat.formula import CNF, IDPool  # noqa: E402

n, k = 18, 5


def main():
    out = sys.argv[1]
    pool, cnf = IDPool(), CNF()
    trip = list(combinations(range(n), 3))
    z = {t: pool.id(("zero",) + t) for t in trip}
    pz = {t: pool.id(("pos",) + t) for t in trip}
    ng = {t: pool.id(("neg",) + t) for t in trip}
    tri = {t: pool.id(("tri",) + t) for t in trip}
    for t in trip:
        cnf.extend([[z[t], pz[t], ng[t]], [-z[t], -pz[t]], [-z[t], -ng[t]], [-pz[t], -ng[t]]])
    val = lambda t, v: {0: z, 1: pz, -1: ng}[v][t]
    allowed = allowed4()
    for a, b, c, d in combinations(range(n), 4):
        ts = [(b, c, d), (a, c, d), (a, b, d), (a, b, c)]
        for v in product((-1, 0, 1), repeat=4):
            if v in allowed and v != (0, 0, 0, 0):
                continue
            cnf.append([-val(t, x) for t, x in zip(ts, v)])
    bf = lambda r, i, j: ng[S(r, i, j)] if i < j else pz[S(r, i, j)]
    A = {}
    for r in range(n):
        others = [x for x in range(n) if x != r]
        for i, j in permutations(others, 2):
            A[r, i, j] = pool.id(("adj", r, i, j))
            cnf.append([-A[r, i, j], bf(r, i, j)])
            bet = []
            for l in others:
                if l in (i, j):
                    continue
                w = pool.id(("btw", r, i, l, j))
                cnf.extend([[-w, bf(r, i, l)], [-w, bf(r, l, j)], [-A[r, i, j], -w], [w, -bf(r, i, l), -bf(r, l, j)]])
                bet.append(w)
            cnf.append([-bf(r, i, j)] + bet + [A[r, i, j]])
    if "--succ" in sys.argv:  # redundant: a crossing has one successor and one predecessor point on r
        for r in range(n):
            others = [x for x in range(n) if x != r]
            for i in others:
                for j, l in combinations([x for x in others if x != i], 2):
                    cnf.append([-A[r, i, j], -A[r, i, l], z[S(r, j, l)]])
                    cnf.append([-A[r, j, i], -A[r, l, i], z[S(r, j, l)]])
    for (a, b, c), tv in tri.items():  # tri <-> three consecutive pairs, not concurrent (hill rule)
        cnf.append([-tv, -z[a, b, c]])
        pairs = []
        for r, i, j in ((a, b, c), (b, a, c), (c, a, b)):
            cnf.append([-tv, A[r, i, j], A[r, j, i]])
            pairs.append((A[r, i, j], A[r, j, i]))
        for pick in product(*pairs):
            cnf.append([z[a, b, c]] + [-x for x in pick] + [tv])
    cnf.extend(CardEnc.equals(lits=list(z.values()), bound=k, vpool=pool, encoding=EncType.seqcounter).clauses)
    cnf.extend([[-z[t]] for t in trip if 0 in t])
    cnf.append([-ng[0, 1, 2]])
    blk = {}
    for t in trip:
        for a_ in t:
            b_, c_ = [y for y in t if y != a_]
            for C in range(n):
                if C in t:
                    continue
                v = pool.id(("blk", t, a_, C))
                cnf.extend([[-v, z[t]], [-v, tri[S(a_, b_, C)]], [-v, tri[S(a_, c_, C)]],
                            [-z[t], -tri[S(a_, b_, C)], -tri[S(a_, c_, C)], v]])
                blk[t, a_, C] = v
        cnf.extend(CardEnc.atmost(lits=[blk[t, a_, C] for a_ in t for C in range(n) if C not in t], bound=2,
                                  vpool=pool, encoding=EncType.seqcounter).clauses)
    first = lambda L, R: [x for M in range(n) if M not in (L, R) for x in (-bf(L, M, R), -z[S(L, R, M)])]
    last = lambda L, R: [x for M in range(n) if M not in (L, R) for x in (-bf(L, R, M), -z[S(L, R, M)])]

    def conj(name, lits):
        v = pool.id(name)
        cnf.extend([[-v, x] for x in lits])
        cnf.append([v] + [-x for x in lits])
        return v
    F = {(L, R): conj(("gF", L, R), first(L, R)) for L, R in permutations(range(n), 2)}
    G = {(L, R): conj(("gG", L, R), last(L, R)) for L, R in permutations(range(n), 2)}
    ids = add_labels(cnf, pool, n, z, tri, blk, F, G, nlab=5)
    zr = [pool.id(("LZr_dummy", j)) for j in range(7)]  # no slack counter here: ZR units become free literals
    ids["ZR"] = {str(j): zr[j] for j in range(1, 7)}
    ids["top"] = pool.top
    cnf.to_file(out)
    json.dump(ids, open(Path(out).with_suffix(".ids.json"), "w"))
    print(f"{out}: vars {pool.top}, clauses {len(cnf.clauses)}")


if __name__ == "__main__":
    main()

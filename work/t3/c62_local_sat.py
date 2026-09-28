"""Small-n local SAT check of the C62-C65 structural kills of the k=5, beta>0 residue.

Instance (n lines, pseudolines, exact semantics, NO triangle target, NO counting):
  signotope axioms (search/kobon_sat.allowed4, no 4-fold point), exactly 5 triple points,
  exact adjacency A(r,i,j) and exact triangles tri <-> (three pairs consecutive and not concurrent),
  blocks / first / last as in search/test_k5L_layer.py, the label layer search/k5L_layer.add_labels,
  and for one residue graph the structural units of search/k5L_cubes.py (types, exact bridge graph,
  listed faces), without exception or D-count units.
The kills C62 (twin faces), C63 (fan of 4 bridge rays), C64 (bent partner in a face) and C65 (b)/(c)
(type-X third vertex beyond a 2-F face) are local and n-independent: every such graph must be UNSAT
at every n. The C65 (a) sigma-gap graphs (0, 11, 13, 15, 17) are killed only by counting at n = 18
and may be SAT here; their models are decoded and fed to c62_tests.check (lemma G on real data).

    uv run --no-project --with python-sat python work/t3/c62_local_sat.py N [graph ...]
"""
import json
import sys
import time
from itertools import combinations, permutations, product
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

ROOT = Path('/home/nail/stuff/sundai_math')
sys.path.insert(0, str(ROOT / 'search'))
from kobon_sat import allowed4  # noqa: E402
from k5L_layer import add_labels, S  # noqa: E402

NBLK = {"X": 2, "F": 2, "V": 2, "O1": 1, "O1b": 1, "O0": 0}


def base(n):
    pool, cnf = IDPool(), CNF()
    trip = list(combinations(range(n), 3))
    z = {t: pool.id(("zero",) + t) for t in trip}
    pz = {t: pool.id(("pos",) + t) for t in trip}
    ng = {t: pool.id(("neg",) + t) for t in trip}
    tri = {t: pool.id(("tri",) + t) for t in trip}
    for t in trip:
        cnf.extend([[z[t], pz[t], ng[t]], [-z[t], -pz[t]], [-z[t], -ng[t]], [-pz[t], -ng[t]]])
    val = lambda t, v: {0: z, 1: pz, -1: ng}[v][t]
    ok = allowed4()
    for a, b, c, d in combinations(range(n), 4):
        ts = [(b, c, d), (a, c, d), (a, b, d), (a, b, c)]
        for v in product((-1, 0, 1), repeat=4):
            if v in ok and v != (0, 0, 0, 0):
                continue
            cnf.append([-val(t, x) for t, x in zip(ts, v)])
    bf = lambda r, i, j: ng[S(r, i, j)] if i < j else pz[S(r, i, j)]
    A = {}
    for r in range(n):
        oth = [x for x in range(n) if x != r]
        for i, j in permutations(oth, 2):
            a = pool.id(("adj", r, i, j))
            A[r, i, j] = a
            cnf.append([-a, bf(r, i, j)])
            btw = []
            for l in oth:
                if l in (i, j):
                    continue
                w = pool.id(("btw", r, i, l, j))
                cnf.extend([[-w, bf(r, i, l)], [-w, bf(r, l, j)], [w, -bf(r, i, l), -bf(r, l, j)], [-a, -w]])
                btw.append(w)
            cnf.append([-bf(r, i, j)] + btw + [a])
    for (a, b, c), tv in tri.items():
        cnf.append([-tv, -z[a, b, c]])
        pairs = []
        for r, i, j in ((a, b, c), (b, a, c), (c, a, b)):
            cnf.append([-tv, A[r, i, j], A[r, j, i]])
            q = pool.id(("cons", r, i, j))
            cnf.extend([[-q, A[r, i, j], A[r, j, i]], [q, -A[r, i, j]], [q, -A[r, j, i]]])
            pairs.append(q)
        cnf.append([tv, z[a, b, c]] + [-q for q in pairs])       # exact triangles
    cnf.extend(CardEnc.equals(lits=list(z.values()), bound=5, vpool=pool, encoding=EncType.seqcounter).clauses)
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

    def conj(name, lits):
        v = pool.id(name)
        cnf.extend([[-v, x] for x in lits])
        cnf.append([v] + [-x for x in lits])
        return v
    first = lambda L, R: [x for M in range(n) if M not in (L, R) for x in (-bf(L, M, R), -z[S(L, R, M)])]
    last = lambda L, R: [x for M in range(n) if M not in (L, R) for x in (-bf(L, R, M), -z[S(L, R, M)])]
    F = {(L, R): conj(("gF", L, R), first(L, R)) for L, R in permutations(range(n), 2)}
    G = {(L, R): conj(("gG", L, R), last(L, R)) for L, R in permutations(range(n), 2)}
    cnf.append([-ng[0, 1, 2]])   # 180-degree rotation symmetry (flips every sign)
    return cnf, pool, dict(z=z, pz=pz, ng=ng, tri=tri, blk=blk, F=F, G=G, bf=bf)


def graph_units(ids, r):
    I = lambda name, *k: ids[name][",".join(map(str, k))]
    t = r["types"]
    units = []
    for i, x in enumerate(t):
        if x in ("X", "F"):
            units += [I("GE2", i), I("AX", i)]
        elif x == "V":
            units += [I("GE2", i), -I("AX", i)]
        else:
            units += [I("GE1", i), -I("GE2", i), I("TB", i) if x == "O1b" else -I("TB", i)]
    edges = {tuple(sorted(e)) for e in r["bridges"]}
    for i, j in combinations(range(5), 2):
        units.append(I("BR", i, j) if (i, j) in edges else -I("BR", i, j))
    for f in r["faces"]:
        units.append(I("FC", *sorted(f)))
    return units


def decode(n, model, g):
    """model -> sweep word via per-line vertex orders (referee sweep_from_rows)."""
    sys.path.insert(0, str(ROOT / 'work/referee'))
    from arr import sweep_from_rows
    pos = set(x for x in model if x > 0)
    zt = lambda *x: g['z'][S(*x)] in pos
    rr = []
    for r in range(n):
        oth = [x for x in range(n) if x != r]
        groups = []
        for x in oth:
            for grp in groups:
                if zt(r, x, grp[0]):
                    grp.append(x)
                    break
            else:
                groups.append([x])
        before = lambda i, j: g['bf'](r, i, j) in pos
        import functools
        groups.sort(key=functools.cmp_to_key(lambda p, q: -1 if before(p[0], q[0]) else 1))
        rr.append([frozenset(gp) for gp in groups])
    return sweep_from_rows(n, rr)


def main():
    n = int(sys.argv[1])
    rows = [json.loads(l) for l in open(ROOT / 'work/t3/k5_exceptions.jsonl')]
    gis = [int(x) for x in sys.argv[2:]] or list(range(len(rows)))
    t0 = time.time()
    cnf, pool, g = base(n)
    ids = add_labels(cnf, pool, n, g['z'], g['tri'], g['blk'], g['F'], g['G'], nlab=5)
    print(f'n={n}: vars {pool.top} clauses {len(cnf.clauses)} built in {time.time() - t0:.1f}s', flush=True)
    with Solver(name='cadical153', bootstrap_with=cnf.clauses) as sv:
        for gi in gis:
            t1 = time.time()
            res = sv.solve(assumptions=graph_units(ids, rows[gi]))
            line = f'graph {gi:2d} {rows[gi]["types"]} need {rows[gi]["need"]}: {"SAT" if res else "UNSAT"} ({time.time() - t1:.1f}s)'
            if res:
                try:
                    toks = decode(n, sv.get_model(), g)
                    line += ' word: ' + ' '.join(toks)
                except Exception as ex:  # noqa: BLE001
                    line += f' (decode failed: {ex!r})'
            print(line, flush=True)


if __name__ == '__main__':
    main()

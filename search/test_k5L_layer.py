"""Check the k5L label layer against real arrangements (gallery wiring words, no 4-fold point, no parallels).
Model literals are fixed from chi (z/pz/ng) and the true triangle set; blk and F/G are defined exactly as in
build_k5g; labels are assigned to the triple points. Then, per indicator:
  two-directional (GE1, GE2, AX, TB, BR): the formula forces exactly the geometric value;
  one-directional (FC, CPE, MUT, E2, E1): geometric truth => satisfiable with the indicator true (soundness);
  we also count how often a false property is still satisfiable (looseness, not an error).
Geometry is computed independently from arr.py (vertex orders, doubly used segments, faces).

    uv run --no-project --with python-sat python search/test_k5L_layer.py [max_per_bucket]
"""
import collections
import glob
import json
import sys
from itertools import combinations, permutations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.insert(0, str(ROOT / "work/t3"))
from arr import Arr  # noqa: E402
from base2 import chi_from_word  # noqa: E402
from kobon_sat import count_general  # noqa: E402
from k5L_layer import add_labels, S  # noqa: E402
from pysat.formula import CNF, IDPool  # noqa: E402
from pysat.solvers import Solver  # noqa: E402

GAL = ROOT / "tools/external/kobon-solutions/gallery/data"


def geometry(a):
    """Ground truth from the wiring diagram: per triple point its blocks (a, C, X), bridges, faces."""
    ev, rows, n = a.events, a.rows, a.n
    trip = a.triples
    blocks = {P: [] for P in trip}
    bridges = set()
    for x in range(n):
        for e in range(len(rows[x]) - 1):
            u, v = rows[x][e], rows[x][e + 1]
            if len(a.t[x][e]) != 2:
                continue
            if len(ev[u]) == 3 and len(ev[v]) == 3:
                bridges.add(frozenset((u, v)))
            elif len(ev[u]) == 3:
                blocks[u].append((x, next(iter(ev[v] - {x})), v))
            elif len(ev[v]) == 3:
                blocks[v].append((x, next(iter(ev[u] - {x})), u))
    faces = set()
    for f in a.tris:
        vs = set()
        for (x, e, _) in f:
            vs |= {rows[x][e], rows[x][e + 1]}
        if len(vs) == 3 and all(len(ev[v]) == 3 for v in vs):
            faces.add(frozenset(vs))
    return blocks, bridges, faces


def point_of(a, x, y):
    for eid in a.rows[x]:
        if y in a.events[eid]:
            return eid


def check(gens, st):
    a = Arr(gens)
    n = a.n
    if any(len(e) > 3 for e in a.events) or len(a.events) + 2 * len(a.triples) != n * (n - 1) // 2:
        return
    k = len(a.triples)
    chi = chi_from_word(gens, n)
    tris = set(tuple(sorted(t)) for t in count_general(n, chi))
    pool, cnf = IDPool(), CNF()
    trip = list(combinations(range(n), 3))
    z = {t: pool.id(("zero",) + t) for t in trip}
    pz = {t: pool.id(("pos",) + t) for t in trip}
    ng = {t: pool.id(("neg",) + t) for t in trip}
    tri = {t: pool.id(("tri",) + t) for t in trip}
    for t in trip:
        v = chi[t]
        cnf.extend([[z[t] if v == 0 else -z[t]], [pz[t] if v == 1 else -pz[t]], [ng[t] if v == -1 else -ng[t]],
                    [tri[t] if t in tris else -tri[t]]])
    bf = lambda r, i, j: ng[S(r, i, j)] if i < j else pz[S(r, i, j)]
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
    first = lambda L, R: [x for M in range(n) if M not in (L, R) for x in (-bf(L, M, R), -z[S(L, R, M)])]
    last = lambda L, R: [x for M in range(n) if M not in (L, R) for x in (-bf(L, R, M), -z[S(L, R, M)])]

    def conj(name, lits):
        v = pool.id(name)
        cnf.extend([[-v, x] for x in lits])
        cnf.append([v] + [-x for x in lits])
        return v
    F = {(L, R): conj(("gF", L, R), first(L, R)) for L, R in permutations(range(n), 2)}
    G = {(L, R): conj(("gG", L, R), last(L, R)) for L, R in permutations(range(n), 2)}
    ids = add_labels(cnf, pool, n, z, tri, blk, F, G, nlab=k)
    P = a.triples  # label i <-> event P[i]
    for i, eid in enumerate(P):
        cnf.append([ids["p"][",".join(map(str, (i, *sorted(a.events[eid]))))]])
    blocks, bridges, faces = geometry(a)
    ends = {x: {a.rows[x][0], a.rows[x][-1]} for x in range(n)}
    lines = [set(a.events[e]) for e in P]
    truth = {}
    for i, e in enumerate(P):
        bs = blocks[e]
        truth["GE1", (i,)] = len(bs) >= 1
        truth["GE2", (i,)] = len(bs) >= 2
        truth["AX", (i,)] = any(b1[0] == b2[0] for b1, b2 in combinations(bs, 2))
        truth["TB", (i,)] = any(len(a.events[point_of(a, b, C)]) == 3 for (x, C, X) in bs for b in lines[i] - {x})
        truth["CPE", (i,)] = any(X in ends[x] for (x, C, X) in bs)
        truth["MUT", (i,)] = any((C, x) in {(y, D) for j, e2 in enumerate(P) if j != i for (y, D, _) in blocks[e2]}
                                 for (x, C, X) in bs)
    for i, j in combinations(range(k), 2):
        truth["BR", (i, j)] = frozenset((P[i], P[j])) in bridges
    for i, j, l in combinations(range(k), 3):
        truth["FC", (i, j, l)] = frozenset((P[i], P[j], P[l])) in faces
    for W, Q in permutations(range(k), 2):
        mids_Q = {x for (x, _, _) in blocks[P[Q]]}
        truth["E2", (W, Q)] = any(X in ends[x] and C in mids_Q for (x, C, X) in blocks[P[W]])
    for Pp, R in combinations(range(k), 2):
        for Q in range(k):
            for s in range(k):
                if len({Pp, R, Q, s}) < 4:
                    continue
                mids_Q = {x for (x, _, _) in blocks[P[Q]]}
                m = lines[Pp] & lines[R]
                truth["E1", (Pp, R, Q, s)] = bool(m & lines[s]) and bool(lines[s] & mids_Q - m)
    for i in range(k):
        g2, ax, g1 = truth["GE2", (i,)], truth["AX", (i,)], truth["GE1", (i,)]
        st["type " + ("X/F" if g2 and ax else "V" if g2 else ("O1b" if truth["TB", (i,)] else "O1a") if g1 else "O0")] += 1
    two = {"GE1", "GE2", "AX", "TB", "BR"}
    with Solver(name="cadical153", bootstrap_with=cnf.clauses) as sv:
        if not sv.solve():
            st["BASE UNSAT"] += 1
            return
        for (name, key), val in truth.items():
            v = ids[name][",".join(map(str, key))]
            pos, neg = sv.solve(assumptions=[v]), sv.solve(assumptions=[-v])
            if name in two:
                st[f"{name} {'ok' if (pos, neg) == (val, not val) else 'MISMATCH'}"] += 1
            else:
                if val:
                    st[f"{name} {'sound' if pos else 'UNSOUND'}"] += 1
                else:
                    st[f"{name} {'loose' if pos else 'tight'}"] += 1
                    # all one-directional indicators may be set false freely
                    assert neg
    st["arrangements"] += 1
    st[f"k={k}"] += 1


def main():
    cap = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    st = collections.Counter()
    seen = collections.Counter()
    for f in sorted(glob.glob(str(GAL / "*" / "*.json"))):
        d = json.load(open(f))
        a = Arr(d["gens"])
        k = len(a.triples)
        if not (3 <= k <= 7) or a.n > 18 or seen[a.n, k] >= cap:
            continue
        before = st["arrangements"]
        check(d["gens"], st)
        if st["arrangements"] > before:
            seen[a.n, k] += 1
    for key in sorted(st):
        print(f"{key}: {st[key]}")
    bad = [key for key in st if "MISMATCH" in key or "UNSOUND" in key or "UNSAT" in key]
    print("FAIL" if bad else "PASS")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

"""SAT model: is there a simple arrangement of n pseudolines with >= T triangles?

Lines are labelled 0..n-1 by slope. A variable chi(i,j,k), i<j<k, says whether
the crossing of i and k lies above j. Signotope axiom: for every a<b<c<d the
sequence chi(bcd), chi(acd), chi(abd), chi(abc) changes sign at most once. Those
are exactly the simple Euclidean pseudoline arrangements with no parallels.

Triangle rule (derived in search/signotope4.py from real line arrangements):
with s1 = [bcd != acd], s2 = [acd != abd], s3 = [abd != abc] (at most one true),
the fourth line of {a,b,c,d} leaves
    abc uncut iff not s1 and not s2      bcd uncut iff not s2 and not s3
    abd uncut iff s2 or s3               acd uncut iff s1 or s2
and a triple is a triangle face iff every other line leaves it uncut.

UNSAT for T proves no simple pseudoline arrangement (hence no simple line
arrangement) of n lines has T triangles. SAT gives a pseudoline candidate that
still has to be straightened.

    python3 search/kobon_sat.py <n> <T> [--solver cadical195] [--symmetry]
    python3 search/kobon_sat.py check <solution.json>   # rule-based count on a real arrangement
"""
import argparse
import json
import sys
import time
from fractions import Fraction
from itertools import combinations
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


def uncut_rule(pattern_bits):
    """pattern_bits = (s1, s2, s3); returns which omitted index leaves its triangle uncut."""
    s1, s2, s3 = pattern_bits
    return {"d": not s1 and not s2, "a": not s2 and not s3, "c": s2 or s3, "b": s1 or s2}


def count_from_chi(n, chi):
    """Triangles of a simple arrangement given chi[(i,j,k)] in {+1,-1}."""
    total = []
    for t in combinations(range(n), 3):
        ok = True
        for l in range(n):
            if l in t:
                continue
            a, b, c, d = sorted(t + (l,))
            v = (chi[b, c, d], chi[a, c, d], chi[a, b, d], chi[a, b, c])
            rule = uncut_rule((v[0] != v[1], v[1] != v[2], v[2] != v[3]))
            omitted = "abcd"[(a, b, c, d).index(l)]
            if not rule[omitted]:
                ok = False
                break
        if ok:
            total.append(t)
    return total


def vertex_side(chi, i, j, l):
    """Side (+1 above, 0 on, -1 below) of the crossing of i and j relative to line l."""
    a, b, c = sorted((i, j, l))
    v = chi[a, b, c]
    return v if l == b else -v


def count_general(n, chi):
    """Triangles from 3-valued chi (zeros = concurrent triples): three distinct vertices and
    no other line with vertices strictly on both sides."""
    found = []
    for i, j, k in combinations(range(n), 3):
        if chi[i, j, k] == 0:
            continue
        ok = True
        for l in range(n):
            if l in (i, j, k):
                continue
            sides = {vertex_side(chi, i, j, l), vertex_side(chi, i, k, l), vertex_side(chi, j, k, l)}
            if 1 in sides and -1 in sides:
                ok = False
                break
        if ok:
            found.append((i, j, k))
    return found


def chi3_from_lines(lines):
    """Like chi_from_lines but allows concurrent triples (chi = 0); None only for parallels/verticals."""
    if any(b == 0 for _, b, _ in lines):
        return None, None
    slopes = [(Fraction(-a, b), Fraction(-c, b)) for a, b, c in lines]
    order = sorted(range(len(lines)), key=lambda i: slopes[i][0])
    ms = [slopes[i] for i in order]
    if len({m for m, _ in ms}) < len(ms):
        return None, None
    chi = {}
    for i, j, k in combinations(range(len(ms)), 3):
        (mi, qi), (mj, qj), (mk, qk) = ms[i], ms[j], ms[k]
        x = (qk - qi) / (mi - mk)
        y, yj = mi * x + qi, mj * x + qj
        chi[i, j, k] = (y > yj) - (y < yj)
    return order, chi


ALLOWED4 = None  # filled below: the 17 realizable (bcd, acd, abd, abc) patterns


def allowed4():
    pats = set()
    from itertools import product
    for v in product((-1, 0, 1), repeat=4):
        zeros = v.count(0)
        if zeros == 4:
            pats.add(v)
        elif zeros == 0 and sum(v[t] != v[t + 1] for t in range(3)) <= 1:
            pats.add(v)
        elif zeros == 1 and (list(v) == sorted(v) or list(v) == sorted(v, reverse=True)):
            pats.add(v)
    assert len(pats) == 17
    return pats


def build_general(n, target):
    """Relaxation that allows concurrent triples: every real arrangement with distinct slopes
    satisfies it, so UNSAT here rules out all straight-line arrangements with >= target."""
    from itertools import product
    pool = IDPool()
    z = {t: pool.id(("zero",) + t) for t in combinations(range(n), 3)}
    p = {t: pool.id(("pos",) + t) for t in combinations(range(n), 3)}
    tri = {t: pool.id(("tri",) + t) for t in combinations(range(n), 3)}
    cnf = CNF()
    for t in z:
        cnf.append([-z[t], -p[t]])  # canonical: zero forces pos false

    def lits_equal(t, value):
        """literals whose conjunction says chi[t] == value"""
        if value == 0:
            return [z[t]]
        return [-z[t], p[t] if value == 1 else -p[t]]

    allowed = allowed4()
    for a, b, c, d in combinations(range(n), 4):
        ts = [(b, c, d), (a, c, d), (a, b, d), (a, b, c)]
        for v in product((-1, 0, 1), repeat=4):
            if v in allowed:
                continue
            clause = []
            for t, val in zip(ts, v):
                clause += [-l for l in lits_equal(t, val)]
            cnf.append(clause)
    for (i, j, k), tv in tri.items():
        cnf.append([-tv, -z[i, j, k]])
        for l in range(n):
            if l in (i, j, k):
                continue
            verts = [(i, j), (i, k), (j, k)]
            for (u1, u2), (w1, w2) in product(verts, verts):
                if (u1, u2) == (w1, w2):
                    continue
                # forbid: vertex u strictly above l and vertex w strictly below l
                clause = [-tv]
                for (x1, x2), want in (((u1, u2), 1), ((w1, w2), -1)):
                    a3, b3, c3 = sorted((x1, x2, l))
                    val = want if l == b3 else -want  # needed chi value for that side
                    clause += [-q for q in lits_equal((a3, b3, c3), val)]
                cnf.append(clause)
    card = CardEnc.atleast(lits=list(tri.values()), bound=target, vpool=pool, encoding=EncType.seqcounter)
    cnf.extend(card.clauses)
    cnf.append([z[0, 1, 2], p[0, 1, 2]])  # 180-degree rotation flips every sign: forbid chi(0,1,2) = -1
    return cnf, z, p, tri


def build_defect(n, target, max_triple, allow_fourfold=False, uncut=True, alternate=False, card="seqcounter", exact_triple=False, blanc=False, k2_18=False, case2=None):
    """Defect-budget model for arrangements with at most `max_triple` triple points.

    Along line r, the crossing with i comes strictly before the crossing with j (i < j)
    iff chi(sorted r,i,j) = -1 (derived empirically, like the triangle rule). A(r;i,j):
    those two points are distinct and consecutive on r. A triple is a triangle iff its
    three pairs are consecutive on the three lines (the hill's rule). Accounting: with at
    most k triple points and no 4-fold point, (number of consecutive pairs) - 3T <= 6 + 6k
    at T >= 94-style targets, i.e. defects = A and not triangle are at most
    n(n-2) + 6k - 3*target. Every real arrangement in that class satisfies this CNF.
    """
    from itertools import permutations, product
    pool = IDPool()
    trip = list(combinations(range(n), 3))
    z = {t: pool.id(("zero",) + t) for t in trip}
    pz = {t: pool.id(("pos",) + t) for t in trip}
    ng = {t: pool.id(("neg",) + t) for t in trip}
    tri = {t: pool.id(("tri",) + t) for t in trip}
    cnf = CNF()
    for t in trip:  # exactly one of zero / pos / neg
        cnf.extend([[z[t], pz[t], ng[t]], [-z[t], -pz[t]], [-z[t], -ng[t]], [-pz[t], -ng[t]]])

    def is_val(t, v):
        return {0: z, 1: pz, -1: ng}[v][t]

    allowed = allowed4()
    for a, b, c, d in combinations(range(n), 4):
        ts = [(b, c, d), (a, c, d), (a, b, d), (a, b, c)]
        for v in product((-1, 0, 1), repeat=4):
            if v in allowed and (allow_fourfold or v != (0, 0, 0, 0)):
                continue
            cnf.append([-is_val(t, val) for t, val in zip(ts, v)])

    def before(r, i, j):  # literal: point of i strictly before point of j on line r
        t = tuple(sorted((r, i, j)))
        return ng[t] if i < j else pz[t]

    A = {}
    for r in range(n):
        others = [x for x in range(n) if x != r]
        for i, j in permutations(others, 2):
            A[r, i, j] = pool.id(("adj", r, i, j))
            cnf.append([-A[r, i, j], before(r, i, j)])
            betweens = []
            for l in others:
                if l in (i, j):
                    continue
                w = pool.id(("btw", r, i, l, j))
                cnf.extend([[-w, before(r, i, l)], [-w, before(r, l, j)], [-A[r, i, j], -w]])
                # w must be true whenever l really is between (so A can be forced)
                cnf.append([w, -before(r, i, l), -before(r, l, j)])
                betweens.append(w)
            cnf.append([-before(r, i, j)] + betweens + [A[r, i, j]])
    defects = []
    for (a, b, c), tv in tri.items():
        cnf.append([-tv, -z[a, b, c]])
        for r, i, j in ((a, b, c), (b, a, c), (c, a, b)):
            cnf.append([-tv, A[r, i, j], A[r, j, i]])
    for (r, i, j), av in A.items():
        d = pool.id(("defect", r, i, j))
        cnf.append([-av, tri[tuple(sorted((r, i, j)))], d])
        defects.append(d)
    if uncut:  # redundant but sound: no other line separates a triangle's vertices
        for (i, j, k), tv in tri.items():
            for l in range(n):
                if l in (i, j, k):
                    continue
                verts = [(i, j), (i, k), (j, k)]
                for (u1, u2), (w1, w2) in product(verts, verts):
                    if (u1, u2) == (w1, w2):
                        continue
                    clause = [-tv]
                    for (x1, x2), want in (((u1, u2), 1), ((w1, w2), -1)):
                        a3, b3, c3 = sorted((x1, x2, l))
                        val = want if l == b3 else -want
                        clause.append(-is_val((a3, b3, c3), val))
                    cnf.append(clause)
    if alternate:
        # Two triangles on consecutive segments [P_i,P_j], [P_j,P_l] of line r both have a side
        # on line j starting at P_j. If they were on the same side of r, both sides would be the
        # first segment of j's ray from P_j, so their apexes would coincide: i, j, l concurrent.
        # Hence: same side => chi(i,j,l) = 0. (Holds for every real arrangement.)
        def side_is(i, j, r, sgn):
            a3, b3, c3 = sorted((i, j, r))
            return is_val((a3, b3, c3), sgn if r == b3 else -sgn)
        for r in range(n):
            others = [x for x in range(n) if x != r]
            for i, j, l in permutations(others, 3):
                t1, t2 = tri[tuple(sorted((r, i, j)))], tri[tuple(sorted((r, j, l)))]
                for sgn in (1, -1):
                    cnf.append([-A[r, i, j], -A[r, j, l], -t1, -t2, -side_is(i, j, r, sgn),
                                -side_is(j, l, r, sgn), z[tuple(sorted((i, j, l)))]])
    if blanc:
        # Generalized Blanc lemma (Prop. 2.0.4 of arXiv 0801.2845, n even, extended): a line L
        # that avoids every multiple point and is not a "cap line" (two of its triples with
        # the lines of some triple point are triangles) meets, at its crossing X with some
        # line M, a piece of M that is bounded on that side and is a side of no triangle.
        # U(L,M,d): on M, the piece from X in direction d (+1 after, -1 before) is bounded and
        # unused; unused <=> no triangle (L,M,N) with N crossing M on that side of X.
        assert not allow_fourfold
        for L in range(n):
            claim = []
            for M in range(n):
                if M == L:
                    continue
                for d in (1, -1):
                    u = pool.id(("U", L, M, d))
                    side_lits = []
                    for N in range(n):
                        if N in (L, M):
                            continue
                        pos = before(M, L, N) if d == 1 else before(M, N, L)
                        side_lits.append(pos)
                        cnf.append([-u, -pos, -tri[tuple(sorted((L, M, N)))]])
                    cnf.append([-u] + side_lits)
                    claim.append(u)
            exempt = [z[t] for t in trip if L in t]
            for t in trip:
                if L in t:
                    continue
                a3, b3, c3 = t
                cp = pool.id(("cap", L) + t)
                t1, t2, t3 = (tri[tuple(sorted((L, x, y)))] for x, y in ((a3, b3), (a3, c3), (b3, c3)))
                cnf.extend([[-cp, z[t]], [-cp, t1, t2], [-cp, t1, t3], [-cp, t2, t3]])
                exempt.append(cp)
            e = pool.id(("exempt", L))
            cnf.append([-e] + exempt)          # e_L -> L is exempt
            cnf.append([e] + claim)            # not exempt -> claims an unused piece
    enc = {"seqcounter": EncType.seqcounter, "totalizer": EncType.totalizer, "mtotalizer": EncType.mtotalizer,
           "kmtotalizer": EncType.kmtotalizer, "sortnetwrk": EncType.sortnetwrk, "cardnetwrk": EncType.cardnetwrk}[card]
    # consecutive pairs on line r = 16 + tau_r + a_r at most (tau_r triple points on r, a_r of
    # them consecutive); two triple points share at most one line, so sum a_r <= C(k,2)
    k = max_triple
    budget = n * (n - 2) + 3 * k + k * (k - 1) // 2 - 3 * target
    if case2:
        # n=18, T=94, exactly 2 triple points, split by case (all deductions from 3T = 282 - Z + D,
        # D <= 2 cap-type segments per triple point (+1 for PQ in case B), Z >= ceil(clean/2)):
        #   both: >= 4 triangles have each triple point as a vertex (2 disjoint cap blocks);
        #         line 0 can be taken defect-free AND off both triple points (>= 8 such lines,
        #         since defects lie on unused segments or on lines through a triple point).
        #   A: the triple points share no line; budget 12; >= 10 exempt lines (4 cap lines).
        #   B: they share a line; budget 13 (default); >= 8 exempt lines (>= 3 cap lines).
        assert n == 18 and target == 94 and max_triple == 2 and exact_triple and blanc and case2 in ("A", "B")
        for t in trip:
            if 0 in t:
                cnf.append([-z[t]])
        for t in trip:
            a3, b3, c3 = t
            at_p = [tri[tuple(sorted((x, y, L)))] for x, y in ((a3, b3), (a3, c3), (b3, c3))
                    for L in range(n) if L not in t]
            # A: 2 disjoint cap blocks -> 4 triangles at P. B: only 4 are forced (the referee found
            # arrangements where P's two blocks overlap on the ray toward Q, so "5" was false).
            card4 = CardEnc.atleast(lits=at_p, bound=4, vpool=pool, encoding=EncType.seqcounter)
            for cl in card4.clauses:
                cnf.append([-z[t]] + cl)  # only when t is a triple point
        per_line = [[z[t] for t in trip if L in t] for L in range(n)]
        if case2 == "A":
            budget -= 1
            for lits in per_line:
                cnf.extend(CardEnc.atmost(lits=lits, bound=1, vpool=pool, encoding=EncType.seqcounter).clauses)
            need_exempt = 10
        else:
            shared = [pool.id(("shared", L)) for L in range(n)]
            for L in range(n):  # shared_L -> line L carries both triple points
                cnf.extend([[-shared[L]] + cl for cl in CardEnc.atleast(lits=per_line[L], bound=2, vpool=pool,
                                                                        encoding=EncType.seqcounter).clauses])
            cnf.append(shared)
            need_exempt = 8
        cnf.extend(CardEnc.atleast(lits=[pool.id(("exempt", L)) for L in range(n)], bound=need_exempt, vpool=pool,
                                   encoding=EncType.seqcounter).clauses)
        # every segment at a triple point is a triangle side, so every unused segment has two
        # simple endpoints and is claimable from exactly those two: sum of U <= 2Z (Z = 4 / 5)
        # Only in case A are all segments at a triple point used (blocks cannot overlap there),
        # so unused segments have simple endpoints and sum U <= 2Z = 8. In case B the overlap
        # sub-case can leave an unused segment at P, so no such bound is added.
        if case2 == "A":
            u_all = [pool.id(("U", L, M, d)) for L in range(n) for M in range(n) if M != L for d in (1, -1)]
            cnf.extend(CardEnc.atmost(lits=u_all, bound=8, vpool=pool, encoding=EncType.seqcounter).clauses)
    if k2_18:
        # CASE A ONLY (the two triple points share no line). Case B, where they are consecutive
        # on a common line and the segment between them is a side of two triangles
        # (D = Z = 5, 9 clean lines), is NOT covered, so an UNSAT here settles case A alone.
        # Case A deductions for n=18, T=94 (3T = 282 - Z + D, D <= 4, Z >= ceil(clean/2)):
        # no line carries both triple points; the budget drops by C(2,2)=1; exactly 10 exempt lines.
        assert n == 18 and target == 94 and max_triple == 2 and exact_triple and blanc
        budget -= 1
        for L in range(n):
            cnf.extend(CardEnc.atmost(lits=[z[t] for t in trip if L in t], bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)
        cnf.extend(CardEnc.atleast(lits=[pool.id(("exempt", L)) for L in range(n)], bound=10, vpool=pool,
                                   encoding=EncType.seqcounter).clauses)
    if budget < 0:
        cnf.append([])  # counting alone rules it out
    else:
        cnf.extend(CardEnc.atmost(lits=defects, bound=budget, vpool=pool, encoding=enc).clauses)
        # Rotation symmetry: rotating the plane only changes which line has the smallest slope,
        # so any line can be made line 0. At most `budget` lines carry a defect, so if
        # budget < n some line has none: take it as line 0.
        if budget < n:
            for (r, i, j), av in A.items():
                if r == 0:
                    cnf.append([-pool.id(("defect", r, i, j))])
            # and if enough lines remain, line 0 also avoids every triple point
            if n - budget - 3 * k > 0:
                for t in trip:
                    if 0 in t:
                        cnf.append([-z[t]])
    if exact_triple:  # exactly max_triple concurrent triples (the case with fewer is covered separately)
        cnf.extend(CardEnc.equals(lits=list(z.values()), bound=max_triple, vpool=pool, encoding=enc).clauses)
    else:
        cnf.extend(CardEnc.atmost(lits=list(z.values()), bound=max_triple, vpool=pool, encoding=enc).clauses)
    cnf.extend(CardEnc.atleast(lits=list(tri.values()), bound=target, vpool=pool, encoding=enc).clauses)
    cnf.append([-ng[0, 1, 2]])  # 180-degree rotation flips every sign
    cnf.pool = pool  # exposed so callers can add constraints on named variables
    return cnf, z, pz, ng, tri, budget


def chi_from_lines(lines):
    """Lines [a,b,c] (a x + b y + c = 0, b != 0) -> slope order and chi; None if not simple."""
    slopes = [(Fraction(-a, b), Fraction(-c, b)) for a, b, c in lines]
    order = sorted(range(len(lines)), key=lambda i: slopes[i][0])
    ms = [slopes[i] for i in order]
    chi = {}
    for i, j, k in combinations(range(len(ms)), 3):
        (mi, qi), (mj, qj), (mk, qk) = ms[i], ms[j], ms[k]
        if mi == mk or mi == mj or mj == mk:
            return None, None
        x = (qk - qi) / (mi - mk)
        y, yj = mi * x + qi, mj * x + qj
        if y == yj:
            return None, None
        chi[i, j, k] = 1 if y > yj else -1
    return order, chi


def build(n, target, symmetry=False):
    pool = IDPool()
    x = {t: pool.id(("chi",) + t) for t in combinations(range(n), 3)}  # true = +1
    tri = {t: pool.id(("tri",) + t) for t in combinations(range(n), 3)}
    cnf = CNF()
    for a, b, c, d in combinations(range(n), 4):
        v = [x[b, c, d], x[a, c, d], x[a, b, d], x[a, b, c]]
        # at most one sign change: forbid +-+ and -+- on any 3 of the 4 positions in order
        for p, q, r in combinations(range(4), 3):
            cnf.append([-v[p], v[q], -v[r]])
            cnf.append([v[p], -v[q], v[r]])
        # sign-change indicators s1, s2, s3 as xors of neighbours
        s = []
        for k in range(3):
            y = pool.id(("s", a, b, c, d, k))
            p, q = v[k], v[k + 1]
            cnf.extend([[-y, p, q], [-y, -p, -q], [y, -p, q], [y, p, -q]])
            s.append(y)
        s1, s2, s3 = s
        # triangle abc needs d to leave it uncut: not s1 and not s2
        cnf.extend([[-tri[a, b, c], -s1], [-tri[a, b, c], -s2]])
        # bcd needs a: not s2 and not s3
        cnf.extend([[-tri[b, c, d], -s2], [-tri[b, c, d], -s3]])
        # abd needs c: s2 or s3
        cnf.append([-tri[a, b, d], s2, s3])
        # acd needs b: s1 or s2
        cnf.append([-tri[a, c, d], s1, s2])
    card = CardEnc.atleast(lits=list(tri.values()), bound=target, vpool=pool, encoding=EncType.seqcounter)
    cnf.extend(card.clauses)
    if symmetry:
        # reflecting the plane (x -> -x) reverses the slope order and flips every chi;
        # breaking just that one symmetry: fix chi(0,1,2) = +1
        cnf.append([x[0, 1, 2]])
    return cnf, x, tri


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        lines = json.loads(Path(sys.argv[2]).read_text())["lines"]
        order, chi = chi_from_lines(lines)
        if chi is not None:
            print("simple arrangement; rule-based triangle count:", len(count_from_chi(len(lines), chi)))
        order, chi3 = chi3_from_lines(lines)
        if chi3 is None:
            print("has parallel or vertical lines; general count not applicable")
            return
        zeros = sum(1 for v in chi3.values() if v == 0)
        print(f"general rule-based count: {len(count_general(len(lines), chi3))} (concurrent triples: {zeros})")
        return
    parser = argparse.ArgumentParser()
    parser.add_argument("n", type=int)
    parser.add_argument("target", type=int)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--symmetry", action="store_true")
    parser.add_argument("--dimacs", help="write the CNF here instead of solving")
    parser.add_argument("--nonsimple", action="store_true", help="allow concurrent triples (relaxation)")
    parser.add_argument("--defect", type=int, metavar="K", help="defect-budget model with at most K triple points")
    parser.add_argument("--alternate", action="store_true", help="add the opposite-sides rule for consecutive triangles")
    parser.add_argument("--exact", action="store_true", help="exactly K triple points instead of at most K")
    parser.add_argument("--blanc", action="store_true", help="add the generalized Blanc lemma (even n)")
    parser.add_argument("--case2", choices=["A", "B"], help="n=18/T=94/exactly-2 case A or B deductions")
    parser.add_argument("--k2-18", action="store_true", help="n=18/T=94/exactly-2, CASE A only: the two triple points share no line (needs --exact --blanc)")
    parser.add_argument("--card", default="seqcounter", help="cardinality encoding (seqcounter, totalizer, mtotalizer, kmtotalizer, sortnetwrk, cardnetwrk)")
    args = parser.parse_args()
    started = time.time()
    if args.defect is not None:
        cnf, z, pz, ng, tri, budget = build_defect(args.n, args.target, args.defect, alternate=args.alternate, card=args.card, exact_triple=args.exact, blanc=args.blanc, k2_18=args.k2_18, case2=args.case2)
        if args.dimacs:
            cnf.to_file(args.dimacs)
            print(f"wrote {args.dimacs}: {cnf.nv} vars, {len(cnf.clauses)} clauses, defect budget {budget}")
            return
        with Solver(name=args.solver, bootstrap_with=cnf.clauses) as solver:
            sat = solver.solve()
            elapsed = time.time() - started
            tag = f"n={args.n} T={args.target} (<= {args.defect} triple points, defect budget {budget})"
            if not sat:
                print(f"{tag}: UNSAT ({elapsed:.1f}s, {cnf.nv} vars, {len(cnf.clauses)} clauses)")
                return
            model = set(l for l in solver.get_model() if l > 0)
            chi = {t: (0 if z[t] in model else (1 if pz[t] in model else -1)) for t in z}
            found = count_general(args.n, chi)
            zeros = sum(1 for v in chi.values() if v == 0)
            print(f"{tag}: SAT ({elapsed:.1f}s); recount {len(found)} triangles, {zeros} triple points")
        return
    if args.nonsimple:
        cnf, z, p, tri = build_general(args.n, args.target)
        if args.dimacs:
            cnf.to_file(args.dimacs)
            print(f"wrote {args.dimacs}: {cnf.nv} vars, {len(cnf.clauses)} clauses")
            return
        with Solver(name=args.solver, bootstrap_with=cnf.clauses) as solver:
            sat = solver.solve()
            elapsed = time.time() - started
            if not sat:
                print(f"n={args.n} T={args.target} (concurrency allowed): UNSAT ({elapsed:.1f}s, {cnf.nv} vars, {len(cnf.clauses)} clauses)")
                return
            model = set(l for l in solver.get_model() if l > 0)
            chi = {t: (0 if z[t] in model else (1 if p[t] in model else -1)) for t in z}
            found = count_general(args.n, chi)
            zeros = sum(1 for v in chi.values() if v == 0)
            print(f"n={args.n} T={args.target} (concurrency allowed): SAT ({elapsed:.1f}s); recount {len(found)} triangles, {zeros} concurrent triples")
        return
    cnf, x, tri = build(args.n, args.target, args.symmetry)
    if args.dimacs:
        cnf.to_file(args.dimacs)
        print(f"wrote {args.dimacs}: {cnf.nv} vars, {len(cnf.clauses)} clauses")
        return
    with Solver(name=args.solver, bootstrap_with=cnf.clauses) as solver:
        sat = solver.solve()
        elapsed = time.time() - started
        if not sat:
            print(f"n={args.n} T={args.target}: UNSAT ({elapsed:.1f}s, {cnf.nv} vars, {len(cnf.clauses)} clauses)")
            return
        model = set(l for l in solver.get_model() if l > 0)
        chi = {t: (1 if v in model else -1) for t, v in x.items()}
        found = count_from_chi(args.n, chi)
        print(f"n={args.n} T={args.target}: SAT ({elapsed:.1f}s); rule-based recount = {len(found)} triangles")


if __name__ == "__main__":
    main()

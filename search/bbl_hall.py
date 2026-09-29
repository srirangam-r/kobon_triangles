"""Reference implementation of the two-hop Hall lemma for the generalized BBL bound (spec for the SAT verifier).

Setting: an arrangement of n pseudolines, triple points allowed, no point of multiplicity >= 4. Units are thirds of a
triangle slot; all values below are exact rationals with denominator 2.

Rays and blocks (as in search/bbl_rules.py). At a triple point P each of its 6 rays is
  N  no first segment, or the first segment is not a side of two triangles;
  B  (block) doubly used first segment [P, X] with X simple; cap = the other line through X;
  R  (bridge) doubly used first segment whose far end is a triple point.
Flank rays of a block on ray i at P: the rays i-1 and i+1 at P (never blocks). Flankers: their far ends.
Portions p_L: own unused bounded segments of L + touches on L (an unused segment of another line with a simple endpoint
on L).

Line values v_L, for every line L:
  v_L = p_L - 1 + sum over triple points P on L of [ 3/2 (#N rays of P along L) - 3/2 (#B rays of P along L) ]
        + (T1 and F transfers below).
  T1 (cap gap). For a block b = [P, X] (axis l, cap C) whose two flankers F1, F2 are triple points (then F1, X, F2 are
     consecutive on C): for each Fi whose ray along C toward X is N, C gives 3/2 to l. b is *served* if it received > 0.
  F  (flank). Every unserved block takes 1 from the line of each of its flank rays that is N.
Identity (exact):  3 Lambda - n = sum_L v_L + waste,  waste = portions lost at multiple endpoints >= 0,
  Lambda = n(n - 2) - 3T.

Relations (1 hop) between distinct lines L, M:
  (a) L and M pass through a common triple point;
  (b) one is the axis and the other the cap of some block;
  (c) M is a pure cap (a cap through no triple point) of a block at P, and L passes through P.
Two-hop neighbourhood N2(L) = lines at distance 1 or 2 in this relation graph.

Two-hop Hall lemma HL(eps): with demands d_L = v_L - eps [L passes through a triple point], every set S of lines with
d < 0 satisfies   sum_{L in S} d_L + sum_{M in N2(S), d_M > 0} d_M >= 0,   N2(S) = union of N2(L), L in S.
Equivalently (max-flow/min-cut), the positive lines can cover all negative lines by transfers to lines within 2 hops.
Consequences: HL(0) => sum_L v_L >= 0 => Lambda >= n/3 (T <= 94 at n = 18). HL(eps), eps > 0 => if there is a triple
point then 3 Lambda - n > 0, and at n = 18 (Lambda = 0 mod 3) Lambda >= 9, i.e. T <= 93. Simple arrangements: T <= 93
by Theorem H.

    python search/bbl_hall.py <in>... [--eps 1/6] [--hops 2] [--noF]
"""
import argparse
import collections
import inspect  # noqa: F401  (stdlib module first: work/t3/inspect.py shadows it)
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.append(str(ROOT / "work/t3"))
from arr import Arr, rays, far_end  # noqa: E402
from cluster import records  # noqa: E402
from bbl_rules import Charge  # noqa: E402
from bbl_adversary import portions  # noqa: E402

H = F(3, 2)


def values(ch, noF=False):
    """line values after T1 and F (every line of the arrangement); also returns served flags.
    noF=True drops rule F (a deliberately weakened scheme, used as a planted test for the SAT verifier)"""
    a, trip = ch.a, ch.trip
    rec = portions(ch)
    val = {L: F(rec[L]) - 1 for L in range(a.n)}
    for P in a.triples:
        for i, r in enumerate(rays(a, P)):
            s = ch.st[P][i]
            val[r[0]] += H if s == "N" else -H if s == "B" else 0
    served = {}
    for b in ch.blk:
        (P, i, l, d, X, C) = b
        rs = rays(a, P)
        F1, F2 = far_end(a, P, rs[(i - 1) % 6]), far_end(a, P, rs[(i + 1) % 6])
        got = F(0)
        if F1 in trip and F2 in trip:
            for Q in (F1, F2):
                dq = 1 if a.pos[C][X] > a.pos[C][Q] else -1
                k = rays(a, Q).index((C, dq))
                if ch.st[Q][k] == "N":
                    got += H
        val[C] -= got
        val[l] += got
        served[b] = got > 0
    for b in ch.blk:
        if served[b] or noF:
            continue
        (P, i, l, d, X, C) = b
        rs = rays(a, P)
        for f in ((i - 1) % 6, (i + 1) % 6):
            if ch.st[P][f] == "N":
                val[rs[f][0]] -= 1
                val[l] += 1
    return val, served


def relation(ch, hops=2):
    a = ch.a
    rel = collections.defaultdict(set)
    for P in a.triples:
        for L in a.events[P]:
            rel[L] |= set(a.events[P]) - {L}
    for b in ch.blk:
        rel[b[2]].add(b[5])
        rel[b[5]].add(b[2])
        if not ch.onl[b[5]]:
            for L in a.events[b[0]]:
                if L != b[5]:
                    rel[b[5]].add(L)
                    rel[L].add(b[5])
    if hops == 2:
        rel = {L: set().union(rel[L], *(rel[M] for M in rel[L])) - {L} for L in range(a.n)}
    return {L: rel.get(L, set()) for L in range(a.n)}


def hall_deficit(ch, eps=F(0), hops=2, noF=False):
    """max over sets S of negative lines of -(sum_S d + sum_{N2(S), d>0} d)  (0 if HL holds), via max-flow"""
    import networkx as nx
    val, served = values(ch, noF)
    rel = relation(ch, hops)
    d = {L: val[L] - (eps if ch.onl[L] else 0) for L in val}
    G = nx.DiGraph()
    need = F(0)
    G.add_node("s")
    G.add_node("t")
    for L, x in d.items():
        if x > 0:
            G.add_edge("s", L, capacity=x)
        elif x < 0:
            G.add_edge(L, "t", capacity=-x)
            need += -x
            for M in rel[L]:
                if d[M] > 0:
                    G.add_edge(M, L)          # infinite capacity
    if need == 0:
        return F(0), val, d
    fv = nx.maximum_flow_value(G, "s", "t")
    return need - F(fv).limit_denominator(10 ** 6), val, d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--eps", default="0")
    ap.add_argument("--hops", type=int, default=2)
    ap.add_argument("--limit", type=int, default=10 ** 9)
    ap.add_argument("--noF", action="store_true", help="weakened scheme without rule F (planted test)")
    o = ap.parse_args()
    eps = F(o.eps)
    tot = bad = 0
    dist = collections.Counter()
    for inp in o.inputs:
        seen = set()
        for r in records(inp):
            g = r["gens"] if isinstance(r["gens"], str) else " ".join(r["gens"])
            if g in seen:
                continue
            seen.add(g)
            try:
                ch = Charge(Arr(g, r.get("n")))
            except ValueError:
                continue
            tot += 1
            dfc, val, d = hall_deficit(ch, eps, o.hops, o.noF)
            lam = ch.lam
            assert 3 * lam - ch.a.n >= sum(val.values()), (g, lam, sum(val.values()))
            for L in val:
                dist[min(val[L], 4)] += 1
            if dfc > 0:
                bad += 1
                print("VIOLATION", ch.a.n, ch.a.T(), str(dfc), g, flush=True)
            if tot >= o.limit:
                break
    print(f"{tot} arrangements, eps={eps}, hops={o.hops}: Hall violations {bad}")
    print("line values after T1+F:", {str(k): c for k, c in sorted(dist.items())})


if __name__ == "__main__":
    main()

"""Per-point cost for the unit lemma (integer form, budget 6 per triple point):
  cost(P) = sum_{blocks b at P} [3 + pc(b) - uown(b) - upc(b)] + sum_{bridges at P} 3/2 - sum_{links at P} 1/2
  pc(b)   = 1/(#blocks capped by that pure cap)   if cap(b) avoids all triple points, else 0
  uown(b) = 1/(#U-blocks sharing u_b)             if status U, else 0
  upc(b)  = 1                                     if status U and cap(b) pure, else 0
Unit lemma  <=>  sum_{P in K} cost(P) <= 6|K| for every line-connected unit K.
Prints the distribution of cost(P) - 6 by point signature, the statuses 'O' (used, not mutual: should never occur by
Lemma A), and neighbourhoods of points with cost > 6.
"""
import collections
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.append(str(ROOT / "work/t3"))
from arr import Arr, rays  # noqa: E402
from cluster import records  # noqa: E402
from bbl_rules import Charge  # noqa: E402
from bbl_charge import point_type  # noqa: E402


def costs(ch):
    a = ch.a
    st = ch.side_status()
    capcnt = collections.Counter(b[5] for b in ch.blk if not ch.onl[b[5]])
    ukey, ucnt = {}, collections.Counter()
    for b, s in st.items():
        if s == "U":
            (P, i, l, d, X, C) = b
            ix = a.pos[l][X]
            ukey[b] = (l, ix if d == 1 else ix - 1)
            ucnt[ukey[b]] += 1
    cost = collections.defaultdict(F)
    sig = collections.defaultdict(list)
    for b, s in st.items():
        P, C = b[0], b[5]
        pure = not ch.onl[C]
        c = 3 + (F(1, capcnt[C]) if pure else 0)
        if s == "U":
            c -= F(1, ucnt[ukey[b]]) + (1 if pure else 0)
        cost[P] += c
        sig[P].append(s + ("p" if pure else "t"))
    trip = ch.trip
    for L in range(a.n):
        r = a.rows[L]
        ps = [i for i, v in enumerate(r) if v in trip]
        for x, y in zip(ps, ps[1:]):
            P, Q = r[x], r[y]
            bridge = (y == x + 1) and len(a.t[L][x]) == 2
            # a bridge costs 3/2 at each end but is also a link (-1/2): net +1 at each end; a plain link -1/2
            w = F(1) if bridge else F(-1, 2)
            cost[P] += w
            cost[Q] += w
    return cost, sig, st


def main():
    dist = collections.Counter()
    ostat = 0
    over = collections.Counter()
    for inp in sys.argv[1:]:
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
            cost, sig, st = costs(ch)
            ostat += sum(1 for s in st.values() if s == "O")
            for P in ch.a.triples:
                key = ("".join(point_type(ch.st[P])), "".join(sorted(sig[P])))
                dist[cost[P] - 6 > 0] += 1
                if cost[P] > 6:
                    over[(key, str(cost[P] - 6))] += 1
    print("points with cost > 6:", dist[True], "of", dist[True] + dist[False], "; statuses O (should be 0):", ostat)
    for k, v in over.most_common(20):
        print(f"  {v:7d}  {k}")


if __name__ == "__main__":
    main()

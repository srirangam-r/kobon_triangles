"""Principled per-line scheme S1 for the generalized BBL bound (extended portions), in thirds of a triangle-slot.

Initial values (exact: sum over all lines = 3 Lambda - n - waste):
  line L gets 3/2 per N ray, -3/2 per block ray, 0 per bridge ray along L at its triple points, plus p_L portions, minus 1.
Rules:
  T1 (cap gap)  block b = [P, X] (axis l, cap C) whose two flank rays end at triple points F1, F2 (so F1, X, F2 are
                consecutive on C): for each of the rays of C at F1, F2 pointing to X that is N, C gives 3/2 to l.
                A gap (C, X) serves one block only.
  F  (flank)    a block not served by T1 takes x from the line of each of its N flank rays.
  R  (rescue)   a pure cap C still below 0 takes from the axes of the blocks it caps, up to y per block, only from what
                the axis holds above 0 after T1 and F.   (y = 0 disables)
Target: every line ends >= 0.

    python search/bbl_s1.py <in>... [--x 1] [--y 1] [--show 20] [--examples]
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


def s1(ch, x=F(1), y=F(1)):
    a, trip = ch.a, ch.trip
    st = ch.side_status()
    rec = portions(ch)
    val = collections.defaultdict(F)
    lines = set(L for L in range(a.n) if ch.onl[L]) | set(b[5] for b in ch.blk)
    for L in lines:
        val[L] = F(rec[L]) - 1
    for P in a.triples:
        for i, r in enumerate(rays(a, P)):
            s = ch.st[P][i]
            val[r[0]] += H if s == "N" else -H if s == "B" else 0
    log = collections.defaultdict(list)
    claimed = set()
    served = {}
    for b in ch.blk:
        (P, i, l, d, X, C) = b
        rs = rays(a, P)
        f1, f2 = rs[(i - 1) % 6], rs[(i + 1) % 6]
        F1, F2 = far_end(a, P, f1), far_end(a, P, f2)
        served[b] = False
        if F1 in trip and F2 in trip and (C, X) not in claimed:
            claimed.add((C, X))
            served[b] = True
            for Q in (F1, F2):
                rq = rays(a, Q)
                dq = 1 if a.pos[C][X] > a.pos[C][Q] else -1
                k = rq.index((C, dq))
                if ch.st[Q][k] == "N":
                    val[C] -= H
                    val[l] += H
                    log[l].append("+T1")
    # T2 (mutual pair): b = [P, X] and b' = [Q, X] mutual; the common triangle P X Q has its third side [P, Q] on a line m.
    # If [P, Q] is not a bridge, P's ray toward Q is N: b takes 3/2 from it (and b' symmetrically from Q's ray).
    if T2:
        for b in ch.blk:
            if served[b] or st[b] != "M":
                continue
            (P, i, l, d, X, C) = b
            rs = rays(a, P)
            for f in ((i - 1) % 6, (i + 1) % 6):
                Q = far_end(a, P, rs[f])
                if ch.st[P][f] == "N" and Q in trip and any(
                        b2[0] == Q and b2[4] == X and b2[2] == C for b2 in ch.blk):
                    val[rs[f][0]] -= H
                    val[l] += H
                    log[l].append("+T2")
                    served[b] = "T2"
                    break
    for b in ch.blk:
        if served[b]:
            continue
        (P, i, l, d, X, C) = b
        rs = rays(a, P)
        for f in ((i - 1) % 6, (i + 1) % 6):
            if ch.st[P][f] == "N":
                val[rs[f][0]] -= x
                val[l] += x
                log[l].append("+F")
    if y and not NORESCUE:
        for b in ch.blk:
            (P, i, l, d, X, C) = b
            if ch.onl[C] or val[C] >= 0:
                continue
            # rescue from the lines through P: the axis first, then the others by decreasing value
            donors = [l] + sorted((L for L in a.events[P] if L != l), key=lambda L: -val[L])
            for dn in donors:
                w = min(y, -val[C], max(val[dn], F(0)))
                if w > 0:
                    val[dn] -= w
                    val[C] += w
                    log[C].append("+R")
                if val[C] >= 0:
                    break
    for rnd in range(FAIR):
        # canonical sharing: snapshot the values; every line M with v(M) > 0 splits v(M) equally among its related lines
        # that are negative in the snapshot (related: common triple point; axis <-> cap; pure cap -> lines through the
        # points of the blocks it caps)
        rel = collections.defaultdict(set)
        for P in a.triples:
            for L in a.events[P]:
                rel[L] |= set(a.events[P]) - {L}
        for b in ch.blk:
            rel[b[2]].add(b[5])
            rel[b[5]].add(b[2])
            if not ch.onl[b[5]]:
                for L in a.events[b[0]]:
                    rel[b[5]].add(L)
                    rel[L].add(b[5])
        if HOPS == 2:
            rel = {L: set().union(rel[L], *(rel[M] for M in rel[L])) - {L} for L in list(rel)}
        snap = dict(val)
        neg = {L for L in snap if snap[L] < 0}
        for M in sorted(snap):
            if snap[M] <= 0:
                continue
            req = [L for L in rel[M] if L in neg]
            if not req:
                continue
            w = snap[M] / len(req)
            for L in req:
                val[M] -= w
                val[L] += w
                log[L].append(f"+S{rnd}")
    for rnd in range(POOL):
        rel = collections.defaultdict(set)
        for P in a.triples:
            for L in a.events[P]:
                rel[L] |= set(a.events[P]) - {L}
        for b in ch.blk:
            rel[b[2]].add(b[5])
            rel[b[5]].add(b[2])
        for L in sorted(val):
            if val[L] >= 0:
                continue
            for dn in sorted(rel[L], key=lambda M: (-val[M], M)):
                w = min(-val[L], max(val[dn], F(0)))
                if w > 0:
                    val[dn] -= w
                    val[L] += w
                    log[L].append(f"+P{rnd}")
                if val[L] >= 0:
                    break
    return val, st, served, rec, log


HOPS = 1
if "--hops2" in sys.argv:
    HOPS = 2
    sys.argv.remove("--hops2")
FAIR = 0
if "--fair" in sys.argv:
    k = sys.argv.index("--fair")
    FAIR = int(sys.argv[k + 1])
    del sys.argv[k:k + 2]
NORESCUE = "--norescue" in sys.argv
if NORESCUE:
    sys.argv.remove("--norescue")
POOL = 0
if "--pool" in sys.argv:
    k = sys.argv.index("--pool")
    POOL = int(sys.argv[k + 1])
    del sys.argv[k:k + 2]
T2 = "--t2" in sys.argv
if T2:
    sys.argv.remove("--t2")


def sig(ch, L, st, served, rec, log):
    a = ch.a
    seq = []
    for P in ch.onl[L]:
        rs = rays(a, P)
        s = ""
        for d in (-1, +1):
            i = rs.index((L, d))
            t = ch.st[P][i]
            if t == "B":
                b = next(b for b in ch.blk if b[0] == P and b[1] == i)
                t = ("t" if served[b] == "T2" else "b" if served[b] else "B") + st[b]
            s += t
        seq.append(s)
    capped = sorted(("c" if served[b] else "u") + st[b] for b in ch.blk if b[5] == L)
    return f"{' '.join(seq) or '-'} | caps {','.join(capped)} | p {rec[L]} | {''.join(sorted(log[L]))}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--x", default="1")
    ap.add_argument("--y", default="1")
    ap.add_argument("--show", type=int, default=20)
    ap.add_argument("--limit", type=int, default=10 ** 9)
    ap.add_argument("--examples", action="store_true")
    o = ap.parse_args()
    x, y = F(o.x), F(o.y)
    dist = collections.Counter()
    bad = collections.Counter()
    ex = {}
    narr = nbad = 0
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
            narr += 1
            val, st, served, rec, log = s1(ch, x, y)
            neg = [L for L in val if val[L] < 0]
            nbad += bool(neg)
            for L in val:
                dist[min(val[L], 3)] += 1
            for L in neg:
                k = (str(val[L]), sig(ch, L, st, served, rec, log))
                bad[k] += 1
                ex.setdefault(k, g)
            if narr >= o.limit:
                break
    print(f"{narr} arrangements; {nbad} with a negative line; distribution:",
          {str(k): c for k, c in sorted(dist.items())})
    print(f"negative lines: {sum(bad.values())} in {len(bad)} signatures")
    for k, c in bad.most_common(o.show):
        print(f"  {c:6d} fin={k[0]:>5} {k[1]}")
        if o.examples:
            print("         ex:", ex[k])


if __name__ == "__main__":
    main()

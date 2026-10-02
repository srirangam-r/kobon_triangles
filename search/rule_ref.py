"""Reference (global) evaluation of the SIG rules on real arrangements: final value of every line = v_L (after T1, F) + transfers.

A rule is  (payer label, receiver label, cell)  with cell = canonical block signature (see rule_lp.SigCatalogue):
    sig = (ring5, u, pL, pR, tL, tR, oth)
      ring5  statuses (N/B/R) of the rays i+1 .. i+5 at the apex P of the block b = [P, X] on ray i (R = i+1 side ... L = i-1 side)
      u      the axis ray beyond X is unbounded (status I)
      pL/pR  the face beyond X on the left / right is a triangle, i.e. [F, X] is itself a block (partner) with F the flanker
      tL/tR  the flanker (far end of the flank ray) is a triple point
      oth    (u', pL', pR') of the block on the opposite ray of P (same axis), (9,9,9) if none
    roles: A axis, C cap, L / R the lines of the flank rays i-1 / i+1 ('M' if the signature is mirror symmetric).
For every block and every ordered pair of distinct roles (p, q) the line of p pays w[(p, q, cell)] to the line of q.
"""
import collections
import inspect  # noqa: F401  (stdlib first)
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.append(str(ROOT / "work/t3"))
from arr import Arr, rays, far_end  # noqa: E402
import bbl_rules2 as R2  # noqa: E402

NOOTH = (9, 9, 9)


def mirror_sig(sg):
    ring5, u, pL, pR, tL, tR, oth = sg
    return (tuple(reversed(ring5)), u, pR, pL, tR, tL, (oth[0], oth[2], oth[1]))


def block_sigs(c):
    """{block: (signature in the ray-index orientation, {'A': line, 'C': line, 'L': line, 'R': line})}"""
    a, ch = c.a, c.ch
    byPXC = {(b[0], b[4], b[2]) for b in c.blk}
    byPB = {(b[0], b[1]): b for b in c.blk}
    out = {}

    def flags(b):
        P, i, l, d, X, C = b
        rs = rays(a, P)
        FL = far_end(a, P, rs[(i - 1) % 6])
        FR = far_end(a, P, rs[(i + 1) % 6])
        return (int(c.st[b] == "I"), int((FL, X, C) in byPXC), int((FR, X, C) in byPXC), int(FL in ch.trip), int(FR in ch.trip))

    for b in c.blk:
        P, i, l, d, X, C = b
        rs = rays(a, P)
        st = ch.st[P]
        u, pL, pR, tL, tR = flags(b)
        oth = NOOTH
        ob = byPB.get((P, (i + 3) % 6))
        if ob is not None:
            ou, opL, opR, _, _ = flags(ob)
            oth = (ou, opL, opR)
        ring5 = tuple(st[(i + t) % 6] for t in range(1, 6))
        out[b] = ((ring5, u, pL, pR, tL, tR, oth),
                  {"A": l, "C": C, "R": rs[(i + 1) % 6][0], "L": rs[(i - 1) % 6][0]})
    return out


def transfers(c, W):
    """list of (payer line, receiver line, amount, key) for the weight table W: key -> Fraction"""
    tr = []
    for b, (sg, lines) in block_sigs(c).items():
        sm = mirror_sig(sg)
        lines = dict(lines)
        symm = sm == sg
        if sm < sg:
            sg = sm
            lines["L"], lines["R"] = lines["R"], lines["L"]
        lab = (lambda x: "M" if (symm and x in "LR") else x)
        for p in "ACLR":
            for q in "ACLR":
                if p == q:
                    continue
                key = (lab(p), lab(q), sg)
                w = W.get(key)
                if w:
                    tr.append((lines[p], lines[q], w, key))
    return tr


def finals(c, W):
    v = dict(c.v0)
    for (p, q, w, key) in transfers(c, W):
        v[p] -= w
        v[q] += w
    return v


def is_rfree(c):
    return all("R" not in c.ch.st[P] for P in c.a.triples)


def canon_ring(r):
    r = "".join(r)
    return min(t[k:] + t[:k] for t in (r, r[::-1]) for k in range(6))


def ring_types(c):
    return {canon_ring(c.ch.st[P]) for P in c.a.triples}


def main():
    import argparse
    import pickle
    from cluster import records
    ap = argparse.ArgumentParser()
    ap.add_argument("weights")
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--rings", default=None, help="comma separated ring types of the certified class (default: bridge-free)")
    ap.add_argument("--limit", type=int, default=10 ** 9)
    ap.add_argument("--mod", type=int, default=1)
    ap.add_argument("--part", type=int, default=0)
    o = ap.parse_args()
    W = {k: F(x).limit_denominator(1000) for k, x in pickle.load(open(o.weights, "rb")).items()}
    cls_types = None if o.rings is None else {canon_ring(x) for x in o.rings.split(",")}
    seen = set()
    stats = collections.Counter()
    lo = {"rfree": None, "other": None, "in_class": None}
    k = 0
    for inp in o.inputs:
        for r in records(inp):
            g = r["gens"] if isinstance(r["gens"], str) else " ".join(r["gens"])
            if g in seen:
                continue
            seen.add(g)
            k += 1
            if k % o.mod != o.part:
                continue
            try:
                a = Arr(g, r.get("n"))
                if a.n % 2:
                    continue
                c = R2.Ctx(a)
            except ValueError:
                continue
            if any(sum(len(a.events[e]) - 1 for e in a.rows[L]) != a.n - 1 for L in range(a.n)):
                continue
            cls = ("rfree" if is_rfree(c) else "other") if cls_types is None else ("in_class" if ring_types(c) <= cls_types else "other")
            v = finals(c, W)
            m = min(v.values())
            stats[cls, "arr"] += 1
            if m < 0:
                stats[cls, "neg_arr"] += 1
                if stats[cls, "neg_arr"] <= 3:
                    print("NEGATIVE", cls, a.n, a.T(), str(m), g)
            stats[cls, "neg_lines"] += sum(1 for x in v.values() if x < 0)
            assert sum(v.values()) == sum(c.v0.values()), "not conservative"
            lo[cls] = m if lo[cls] is None else min(lo[cls], m)
            if stats[cls, "arr"] >= o.limit:
                break
    print(dict(stats), "min final per class:", {k_: str(x) for k_, x in lo.items()})


if __name__ == "__main__":
    main()

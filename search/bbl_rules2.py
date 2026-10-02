"""Explicit local transfer rules R1-R3 (+ safety net R4) that replace the two-hop Hall step of search/bbl_hall.py.

Setting and notation (from search/bbl_hall.py / bbl_rules.py; triple points only, no point of multiplicity >= 4;
all values are exact rationals).
  v0[L]     line value after T1 and F (bbl_hall.values, eps = 0): p_L - 1 + 3/2 (#N rays - #B rays along L) + T1/F.
  ray       the 6 rays of a triple point P are numbered 0..5 cyclically, ray k+3 is the opposite ray of ray k (same
            line). Status st[P][k] in {N, B, R}; N rays carry +3/2 and B rays -3/2 in v0 (R rays 0).
  block     b = (P, i, l, d, X, C): apex P, ray i, axis l, simple far end X, cap C. Flank rays: i-1, i+1 (never B).
            status(b) in {U, I, M, O} (bbl_rules.Charge.side_status): beyond X the axis segment is unused (U),
            unbounded (I), the block of a mutual partner (M), or otherwise used (O). served(b): b received T1.
  partner   for status M, b' = [Q, X] with axis C and cap l.  connector(b): the line of the flank ray of b whose far
            end is Q (the line PQ).  free ray: an N ray o at P with st[P][o-1] != B and st[P][o+1] != B.
  p_L       portions (unused own segments + touches) = bbl_adversary.portions.
  rho(M)    = 2 (#N rays of M - #B rays of M) + 2 p_M, counted over the triple points on M: a ray-count proxy of v0[M].
  TAU       = 8.

Rules, applied in this order; every transfer is (donor -> receiver, amount). Requests depend on local structure and on
the requester's own running value; donors are only compared by their own ray counts rho (R3).

  R1  (deficient pure cap)  A pure cap C (no triple point on C) with v0[C] < 0 (that is p_C = 0, v0 = -1) caps k blocks
      b = [P, X] (all of status I). For each of them C receives 1/k from
        (a) if P carries a second block b' with the same axis l (an X point):  l if status(b') = U;  connector(b') if
            status(b') = M;  nobody otherwise;
        (b) if b is the only block at P:  1/(2k) from each of the lines of rays i+2 and i+4 of P (the free rays
            opposite the two flank rays).
  R2  (bridge flank)  For every unserved block b = (P, i, l, ...) and each flank ray f in {i-1, i+1} with
      st[P][f] = R whose opposite ray o = f+3 is a free N ray: the line of ray o gives 1/2 to l.
  R3  (demand driven)  Let v be the values after R1, R2. Every line L with v[L] < 0 collects its deficit -v[L] from
      the donor set D*(L). Candidates D(L) = union over the blocks b with axis L and status I or M of
        connector(b) and cap(b)              (status M),
        cap(b)                               (status I and cap(b) carries a triple point),
        the lines of the N flank rays of b   (both statuses),
      minus L itself, deduplicated. rho* = min(TAU, max_{M in D(L)} rho(M)); D*(L) = {M in D(L): rho(M) >= rho*}
      (the richest candidates; all candidates with rho >= TAU if there are such). Each M in D*(L) gives
      -v[L] / |D*(L)| to L. (No candidate: nothing happens.)
  R4  (safety net; NOT structural, value based)  Let v be the values after R3. Every line M with v[M] > 0 splits v[M]
      equally among the lines L with v[L] < 0 that are related to M by one hop (bbl_hall.relation, hops = 1: common
      triple point; axis <-> cap of a block; pure cap <-> lines through the blocked point). R4 is a fallback for the
      rare situations where the structural donors of R1-R3 are exhausted; it never takes more than a donor has, so only
      requesters can remain negative.

Claim under test: after R1-R3 (or R1-R4) every line of every even-n arrangement has value >= 0.
All rules are transfers, so 3 Lambda - n = sum of the final values + waste still holds.

    python search/bbl_rules2.py <in>... [--no-r4] [--limit N] [--show K]
"""
import inspect  # noqa: F401  (stdlib module first: work/t3/inspect.py shadows it)
import argparse
import collections
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.append(str(ROOT / "work/t3"))
from arr import Arr, rays, far_end  # noqa: E402
from bbl_rules import Charge  # noqa: E402
import bbl_hall  # noqa: E402
from bbl_adversary import portions  # noqa: E402

TAU = 8
HALF = F(1, 2)


class Ctx:
    """structure of one arrangement: blocks, statuses, partners, connectors, T1+F values"""

    def __init__(self, a):
        self.a = a
        self.ch = ch = Charge(a)           # raises ValueError on a point of multiplicity >= 4
        self.v0, self.served = bbl_hall.values(ch)
        self.st = ch.side_status()
        self.p = portions(ch)
        self.blk = ch.blk
        self.byP = collections.defaultdict(list)
        self.capped = collections.defaultdict(list)
        self.axisof = collections.defaultdict(list)
        byX = collections.defaultdict(list)
        for b in self.blk:
            self.byP[b[0]].append(b)
            self.capped[b[5]].append(b)
            self.axisof[b[2]].append(b)
            byX[b[4]].append(b)
        self.partner = {}
        for b in self.blk:
            if self.st[b] == "M":
                for b2 in byX[b[4]]:
                    if b2 is not b and b2[2] == b[5]:
                        self.partner[b] = b2
        self._rho = {}

    def flank(self, b):
        """[(ray index, line, status, far end)] of the two flank rays of block b"""
        a, ch = self.a, self.ch
        P, i = b[0], b[1]
        rs = rays(a, P)
        return [(f, rs[f][0], ch.st[P][f], far_end(a, P, rs[f])) for f in ((i - 1) % 6, (i + 1) % 6)]

    def connector(self, b):
        pb = self.partner.get(b)
        if pb is None:
            return None
        for f, L, s, fe in self.flank(b):
            if fe == pb[0]:
                return L
        return None

    def rho(self, M):
        if M not in self._rho:
            a, ch = self.a, self.ch
            nN = nB = 0
            for P in ch.onl[M]:
                for i, r in enumerate(rays(a, P)):
                    if r[0] == M:
                        nN += ch.st[P][i] == "N"
                        nB += ch.st[P][i] == "B"
            self._rho[M] = 2 * (nN - nB) + 2 * self.p[M]
        return self._rho[M]


def rule_R1(c):
    out = []
    a, ch = c.a, c.ch
    for C in range(a.n):
        if ch.onl[C] or c.v0[C] >= 0:
            continue
        bs = c.capped[C]
        for b in bs:
            P, i, l = b[0], b[1], b[2]
            w = -c.v0[C] / len(bs)
            other = [x for x in c.byP[P] if x is not b]
            if len(other) == 1 and other[0][2] == l:
                s = c.st[other[0]]
                if s == "U":
                    out.append((l, C, w, "R1"))
                elif s == "M":
                    out.append((c.connector(other[0]), C, w, "R1"))
            elif not other:
                rs = rays(a, P)
                for k in (2, 4):
                    out.append((rs[(i + k) % 6][0], C, w / 2, "R1"))
    return out


def rule_R2(c):
    out = []
    a, ch = c.a, c.ch
    for b in c.blk:
        if c.served[b]:
            continue
        P, i, l = b[0], b[1], b[2]
        rs = rays(a, P)
        for f in ((i - 1) % 6, (i + 1) % 6):
            o = (f + 3) % 6
            if ch.st[P][f] == "R" and ch.st[P][o] == "N" and "B" not in (ch.st[P][(o - 1) % 6], ch.st[P][(o + 1) % 6]):
                out.append((rs[o][0], l, HALF, "R2"))
    return out


def candidates(c, L):
    cand = []
    for b in c.axisof[L]:
        if c.st[b] not in ("I", "M"):
            continue
        if c.st[b] == "M":
            cand.append(c.connector(b))
            cand.append(b[5])
        elif c.ch.onl[b[5]]:
            cand.append(b[5])
        cand += [line for f, line, st_, fe in c.flank(b) if st_ == "N"]
    return sorted({d for d in cand if d is not None and d != L})


def rule_R3(c, v):
    out = []
    for L in range(c.a.n):
        if v[L] >= 0:
            continue
        cand = candidates(c, L)
        if not cand:
            continue
        key = min(max(c.rho(d) for d in cand), TAU)
        best = [d for d in cand if c.rho(d) >= key]
        for d in best:
            out.append((d, L, -v[L] / len(best), "R3"))
    return out


def rule_R4(c, v):
    rel = bbl_hall.relation(c.ch, 1)
    out = []
    neg = {L for L in v if v[L] < 0}
    for M in sorted(v):
        if v[M] <= 0:
            continue
        req = [L for L in rel[M] if L in neg]
        for L in req:
            out.append((M, L, v[M] / len(req), "R4"))
    return out


def apply(v, tr):
    for d, r, w, t in tr:
        if d is not None:
            v[d] -= w
            v[r] += w


def final(a, r4=True):
    """(context, final values, list of transfers). r4=False stops after the structural rules R1-R3."""
    c = Ctx(a)
    v = dict(c.v0)
    tr = rule_R1(c)
    apply(v, tr)
    t = rule_R2(c)
    apply(v, t)
    tr += t
    t = rule_R3(c, v)
    apply(v, t)
    tr += t
    if r4 and min(v.values()) < 0:
        t = rule_R4(c, v)
        apply(v, t)
        tr += t
    return c, v, tr


def main():
    from cluster import records
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--no-r4", action="store_true")
    ap.add_argument("--limit", type=int, default=10 ** 9)
    ap.add_argument("--show", type=int, default=5)
    o = ap.parse_args()
    tot = neg = need4 = 0
    lo = None
    for inp in o.inputs:
        seen = set()
        for r in records(inp):
            g = r["gens"] if isinstance(r["gens"], str) else " ".join(r["gens"])
            if g in seen:
                continue
            seen.add(g)
            try:
                a = Arr(g, r.get("n"))
                if a.n % 2:
                    continue
                c3, v3, _ = final(a, r4=False)
                c, v, tr = final(a, r4=not o.no_r4)
            except ValueError:
                continue
            tot += 1
            m = min(v.values())
            lo = m if lo is None else min(lo, m)
            need4 += min(v3.values()) < 0
            if m < 0:
                neg += 1
                if neg <= o.show:
                    print("NEGATIVE", a.n, a.T(), str(m), g)
            if tot >= o.limit:
                break
    print(f"{tot} even-n arrangements: {need4} need R4 (negative after R1-R3), {neg} negative at the end "
          f"({'R1-R3' if o.no_r4 else 'R1-R4'}), smallest final line value {lo}")


if __name__ == "__main__":
    main()

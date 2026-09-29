"""Explicit discharging rules for the generalized BBL bound (every line ends with charge >= 1/3 => Lambda >= n/3).

Base charges (sum <= Lambda = Z + sum_P c_P):
  U  each unused bounded segment u gives 1/3 to its own line and 1/3 to the other line at each simple endpoint (a touch);
  P  each triple point P gives c_P/3 to each of its three lines, c_P = 3 - D_P - beta_P/2.
Rules (applied after the base charges):
  R1 (cap rescue) block [P, X] on the axis l with cap C: if C passes through no triple point and C has no touch at X
     (then the segment of l beyond X is unbounded), l gives 1/3 to C.

    python search/bbl_rules.py <in>... [--rules R1] [--show 12]
Prints the arrangements where some line ends below 1/3, grouped by a descriptive signature of the deficient line.
"""
import argparse
import collections
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.append(str(ROOT / "work/t3"))
from arr import Arr, rays, first_seg, far_end, touches  # noqa: E402
from cluster import records  # noqa: E402
from bbl_charge import point_type, role  # noqa: E402

T3 = F(1, 3)


class Charge:
    def __init__(self, a):
        self.a = a
        n = a.n
        if any(len(e) > 3 for e in a.events):
            raise ValueError("4-fold point")
        trip = self.trip = set(a.triples)
        self.st, self.blk = {}, []                 # blk: (P, ray index, axis line, X, cap line)
        Dp, bp = collections.Counter(), collections.Counter()
        for P in a.triples:
            st = []
            for i, r in enumerate(rays(a, P)):
                fs = first_seg(a, P, r)
                if fs is None or len(a.t[fs[0]][fs[1]]) != 2:
                    st.append("N")
                    continue
                X = far_end(a, P, r)
                if X in trip:
                    st.append("R")
                    bp[P] += 1
                else:
                    st.append("B")
                    Dp[P] += 1
                    self.blk.append((P, i, r[0], r[1], X, a.other(X, r[0])))
            self.st[P] = st
        self.c = {P: 3 - Dp[P] - F(bp[P], 2) for P in a.triples}
        self.touch = collections.defaultdict(list)    # line -> [(u, X)]
        for (u, X, L) in touches(a):
            self.touch[L].append((u, X))
        self.Z = [sum(1 for s in a.t[L] if not s) for L in range(n)]
        self.onl = [[P for P in a.rows[L] if P in trip] for L in range(n)]
        self.q = [F(self.Z[L], 3) + F(len(self.touch[L]), 3) + sum((self.c[P] for P in self.onl[L]), F(0)) / 3
                  for L in range(n)]
        self.log = [[] for _ in range(n)]
        self.lam = n * (n - 2) - 3 * a.T()
        assert sum(self.q) <= self.lam

    def give(self, frm, to, w, why):
        self.q[frm] -= w
        self.q[to] += w
        self.log[frm].append(f"-{w}:{why}")
        self.log[to].append(f"+{w}:{why}")

    def R1(self):
        for (P, i, l, d, X, C) in self.blk:
            if self.onl[C]:
                continue
            if any(x == X for (_, x) in self.touch[C]):
                continue
            self.give(l, C, T3, "R1")

    def side_status(self):
        """for every block: 'U' (segment beyond X unused, bounded), 'M' (mutual pair), 'I' (unbounded), 'O' (used, not mutual)"""
        a = self.a
        out = {}
        byX = collections.defaultdict(list)
        for b in self.blk:
            byX[b[4]].append(b)
        for b in self.blk:
            (P, i, l, d, X, C) = b
            r = a.rows[l]
            ix = a.pos[l][X]
            e = ix if d == 1 else ix - 1
            if e < 0 or e > len(r) - 2:
                out[b] = "I"
            elif not a.t[l][e]:
                out[b] = "U"
            else:
                mutual = any(b2 is not b and b2[2] == C and b2[5] == l for b2 in byX[X])
                out[b] = "M" if mutual else "O"
        return out

    def R2(self):
        """chain rule for X points (two opposite blocks, no bridge): mutual pairs link X points into paths; charge 1/3 is
        passed along the path from a U end to an I end (each I end's axis paid R1)."""
        st = self.side_status()
        xs = {P for P in self.a.triples if "".join(point_type(self.st[P])) == "BNNBNN"}
        sides = collections.defaultdict(list)       # P -> [(block, status)]
        for b, s in st.items():
            if b[0] in xs:
                sides[b[0]].append((b, s))
        # partner via mutual block: block b of P with cap C = axis of Q, same X
        partner = {}
        for b, s in st.items():
            if s == "M" and b[0] in xs:
                for b2, s2 in st.items():
                    if b2 is not b and b2[4] == b[4] and b2[2] == b[5] and b2[0] in xs:
                        partner[b] = b2
        seen = set()
        self.chains = []
        for P in xs:
            if P in seen:
                continue
            # walk to one end
            comp, stack = [], [P]
            seen.add(P)
            while stack:
                q = stack.pop()
                comp.append(q)
                for b, s in sides[q]:
                    if b in partner and partner[b][0] not in seen:
                        seen.add(partner[b][0])
                        stack.append(partner[b][0])
            if len(comp) < 2:
                continue
            ends = [(b, s) for q in comp for b, s in sides[q] if b not in partner]
            self.chains.append(tuple(sorted(s for _, s in ends)))
            U = [b for b, s in ends if s == "U"]
            I = [b for b, s in ends if s == "I"]
            # route: pair each I end with a U end along the path (all axes on a path)
            for bi, bu in zip(I, U):
                # path from bu's point to bi's point through partners
                path = self._path(bu[0], bi[0], sides, partner)
                for x, y in zip(path, path[1:]):
                    self.give(self._axis(x), self._axis(y), T3, "R2")

    def _pool(self, lines, tag):
        """move charge inside a set of lines so that every line reaches 1/3 when the set's total allows it"""
        lines = sorted(set(lines))
        need = [L for L in lines if self.q[L] < T3]
        if not need:
            return
        donors = [L for L in lines if self.q[L] > T3]
        for L in need:
            for dnr in donors:
                if self.q[L] >= T3:
                    break
                w = min(self.q[dnr] - T3, T3 - self.q[L])
                if w > 0:
                    self.give(dnr, L, w, tag)

    def R2g(self):
        """mutual components (points linked by mutual pairs, any type): pool the axes of their blocks"""
        st = self.side_status()
        partner = {}
        for b, s in st.items():
            if s == "M":
                for b2, s2 in st.items():
                    if b2 is not b and b2[4] == b[4] and b2[2] == b[5]:
                        partner[b] = b2
        adj = collections.defaultdict(set)
        for b, b2 in partner.items():
            adj[b[0]].add(b2[0])
            adj[b2[0]].add(b[0])
        seen = set()
        self.mcomp = []
        for P in list(adj):
            if P in seen:
                continue
            comp, stack = set(), [P]
            seen.add(P)
            while stack:
                q = stack.pop()
                comp.add(q)
                for r in adj[q]:
                    if r not in seen:
                        seen.add(r)
                        stack.append(r)
            axes = [b[2] for b in self.blk if b[0] in comp] + [b[5] for b in self.blk if b[0] in comp]
            self.mcomp.append(comp)
            self._pool(axes, "R2g")

    def R3(self):
        """bridge clusters: pool all lines through their points and the caps of their blocks"""
        trip = self.trip
        adj = collections.defaultdict(set)
        a = self.a
        for L in range(a.n):
            r = a.rows[L]
            for e in range(len(r) - 1):
                if len(a.t[L][e]) == 2 and r[e] in trip and r[e + 1] in trip:
                    adj[r[e]].add(r[e + 1])
                    adj[r[e + 1]].add(r[e])
        seen = set()
        for P in list(adj):
            if P in seen:
                continue
            comp, stack = set(), [P]
            seen.add(P)
            while stack:
                q = stack.pop()
                comp.add(q)
                for r2 in adj[q]:
                    if r2 not in seen:
                        seen.add(r2)
                        stack.append(r2)
            lines = [L for q in comp for L in a.events[q]] + [b[5] for b in self.blk if b[0] in comp]
            self._pool(lines, "R3")

    def Rstar(self):
        """one pooling rule: components of the graph on triple points with edges = bridges and mutual pairs; pool all
        lines through the component's points and the caps of its blocks"""
        a = self.a
        trip = self.trip
        adj = collections.defaultdict(set)
        for L in range(a.n):
            r = a.rows[L]
            for e in range(len(r) - 1):
                if len(a.t[L][e]) == 2 and r[e] in trip and r[e + 1] in trip:
                    adj[r[e]].add(r[e + 1])
                    adj[r[e + 1]].add(r[e])
        st = self.side_status()
        for b, s in st.items():
            if s == "M":
                for b2 in self.blk:
                    if b2 is not b and b2[4] == b[4] and b2[2] == b[5]:
                        adj[b[0]].add(b2[0])
                        adj[b2[0]].add(b[0])
        seen = set()
        self.units = []
        for P in a.triples:
            if P in seen:
                continue
            comp, stack = set(), [P]
            seen.add(P)
            while stack:
                q = stack.pop()
                comp.add(q)
                for r2 in adj[q]:
                    if r2 not in seen:
                        seen.add(r2)
                        stack.append(r2)
            lines = set(L for q in comp for L in a.events[q]) | set(b[5] for b in self.blk if b[0] in comp)
            self.units.append((comp, lines))
            self._pool(lines, "R*")

    def _axis(self, P):
        return next(b[2] for b in self.blk if b[0] == P)

    def _path(self, s, t, sides, partner):
        prev = {s: None}
        stack = [s]
        while stack:
            q = stack.pop()
            if q == t:
                break
            for b, _ in sides[q]:
                if b in partner and partner[b][0] not in prev:
                    prev[partner[b][0]] = q
                    stack.append(partner[b][0])
        out = [t]
        while prev[out[-1]] is not None:
            out.append(prev[out[-1]])
        return out[::-1]

    def describe(self, L):
        a = self.a
        cls = "triple" if self.onl[L] else ("cap" if any(b[5] == L for b in self.blk) else "clean")
        pts = tuple(sorted(("".join(point_type(self.st[P])), "".join(role(self.st[P], [i for i, r in enumerate(rays(a, P)[:3]) if r[0] == L][0])), str(self.c[P]))
                           for P in self.onl[L]))
        capd = tuple(sorted("".join(point_type(self.st[b[0]])) for b in self.blk if b[5] == L))
        return (cls, self.Z[L], len(self.touch[L]), pts, capd, tuple(sorted(set(x.split(":")[1] + x[0] for x in self.log[L]))), str(self.q[L]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--rules", default="R1,R2")
    ap.add_argument("--show", type=int, default=12)
    ap.add_argument("--limit", type=int, default=10 ** 9)
    a = ap.parse_args()
    rules = [r for r in a.rules.split(",") if r]
    bad = collections.Counter()
    chains = collections.Counter()
    ex = {}
    cnt = nbad = 0
    for inp in a.inputs:
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
            for rule in rules:
                getattr(ch, rule)()
            cnt += 1
            for c in getattr(ch, "chains", []):
                chains[c] += 1
            low = [L for L in range(ch.a.n) if ch.q[L] < T3]
            if low:
                nbad += 1
            for L in low:
                d = ch.describe(L)
                bad[d] += 1
                ex.setdefault(d, (g, L))
            if cnt >= a.limit:
                break
    print(f"rules {rules}: {cnt} arrangements, {nbad} with a line below 1/3, {sum(bad.values())} deficient lines")
    print("X-chains by end statuses:", dict(chains))
    for d, v in bad.most_common(a.show):
        print(f"  {v:6d}  {d}\n          e.g. line {ex[d][1]} of {ex[d][0][:90]}")


if __name__ == "__main__":
    main()

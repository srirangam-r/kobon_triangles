"""Combinatorial structure of a wiring-diagram arrangement (gallery sweep words).

For each line: ordered vertices; for each bounded segment: which sides carry a triangle
(t-sequence entry: set of sides in {+1,-1}); triple points; cap blocks; axes; clean lines;
claims (unused segment u of M at a simple endpoint X, attributed to the other line through X).

Side convention: +1 = smaller slot index ("above" in the wiring diagram), -1 = below.
"""
import json
import sys
from collections import defaultdict
from itertools import combinations


def build(gens, n):
    wires = list(range(n))
    rows = [[] for _ in range(n)]          # rows[w] = list of event ids on line w
    events = []                            # event id -> frozenset of lines
    c = [0] * n                            # vertices passed so far on each line
    face = {}                              # gap k -> dict(edges=[(line, e, side)], left=bool)
    for k in range(n - 1):
        face[k] = dict(edges=[(wires[k], -1, -1), (wires[k + 1], -1, +1)], left=False)
    faces = []
    for tok in gens.split():
        g = int(tok.rstrip("*"))
        w = 3 if tok.endswith("*") else 2
        W = wires[g:g + w]
        eid = len(events)
        events.append(frozenset(W))
        for x in W:
            rows[x].append(eid)
        for k in range(g, g + w - 1):      # closed gaps
            f = face[k]
            if f["left"]:
                faces.append(f["edges"])
        for x in W:
            c[x] += 1
        wires[g:g + w] = list(reversed(W))
        for k in range(g, g + w - 1):
            face[k] = dict(edges=[(wires[k], c[wires[k]] - 1, -1), (wires[k + 1], c[wires[k + 1]] - 1, +1)], left=True)
        if g - 1 >= 0:
            x = wires[g]
            face[g - 1]["edges"].append((x, c[x] - 1, +1))
        if g + w - 1 <= n - 2:
            x = wires[g + w - 1]
            face[g + w - 1]["edges"].append((x, c[x] - 1, -1))
    return rows, events, faces


class Arr:
    def __init__(self, gens, n=None):
        if n is None:
            n = 1 + max(int(t.rstrip("*")) + (2 if t.endswith("*") else 1) for t in gens.split())
        self.n = n
        self.rows, self.events, faces = build(gens, n)
        self.faces = faces
        self.tris = [f for f in faces if len(f) == 3]
        # t[line][e] = set of sides with a triangle over segment e (0..len-2)
        self.t = [[set() for _ in range(len(r) - 1)] for r in self.rows]
        for f in self.tris:
            for (x, e, side) in f:
                assert 0 <= e < len(self.rows[x]) - 1, (x, e)
                self.t[x][e].add(side)
        self.triples = [eid for eid, ev in enumerate(self.events) if len(ev) == 3]
        self.pos = [{eid: i for i, eid in enumerate(r)} for r in self.rows]
        # side of vertex eid relative to line L (for eid not on L): +1 / -1
        # computed via crossing order: line L at slot... use geometry-free rule:
        # vertex V=(A,B) lies on the + side of L iff on A, V and A∩L ... not needed generally.

    def T(self):
        return len(self.tris)

    def Z(self):
        return sum(1 for r in self.t for s in r if not s)

    def D(self):
        return sum(1 for r in self.t for s in r if len(s) == 2)

    def lines_at(self, eid):
        return self.events[eid]

    def is_simple(self, eid):
        return len(self.events[eid]) == 2

    def other(self, eid, L):
        """unique other line through a simple vertex"""
        (o,) = self.events[eid] - {L}
        return o

    def seg_side_of_piece(self, L, i, R):
        """Crossing X = rows[L][i] with line R. Return (e_before, e_after) pieces on R: the
        segments of R starting/ending at X, and on which side of L each lies."""
        raise NotImplementedError


def load(path):
    d = json.load(open(path))
    return Arr(d["gens"])



# ---------------------------------------------------------------- structure helpers
def side_of(a, V, L):
    """side (+1/-1) of vertex V (event id, not on L) relative to line L."""
    assert L not in a.events[V]
    for R in a.events[V]:
        # find X = R ∩ L on R
        for eid in a.rows[R]:
            if L in a.events[eid]:
                X = eid
                break
        i, j = a.pos[R][V], a.pos[R][X]
        s = +1 if R < L else -1
        return s if i < j else -s


def rays(a, P):
    """6 rays at triple point P in circular (counterclockwise) order: (line, dir)."""
    # recover slot order before the event: sorted labels = top-to-bottom order (block is sorted)
    w0, w1, w2 = sorted(a.events[P])
    return [(w0, -1), (w1, -1), (w2, -1), (w0, +1), (w1, +1), (w2, +1)]


def first_seg(a, P, ray):
    L, d = ray
    i = a.pos[L][P]
    e = i if d == +1 else i - 1
    if e < 0 or e > len(a.rows[L]) - 2:
        return None
    return (L, e)


def far_end(a, P, ray):
    L, d = ray
    i = a.pos[L][P] + d
    if 0 <= i < len(a.rows[L]):
        return a.rows[L][i]
    return None


def seg_ends(a, L, e):
    return a.rows[L][e], a.rows[L][e + 1]


def blocks(a, P):
    """list of (ray index, cap line) for doubly used first segments with simple far end."""
    rs = rays(a, P)
    out = []
    for k, r in enumerate(rs):
        fs = first_seg(a, P, r)
        if fs is None:
            continue
        L, e = fs
        if len(a.t[L][e]) == 2:
            X = far_end(a, P, r)
            if a.is_simple(X):
                out.append((k, a.other(X, L)))
    return out


def unused(a):
    return [(L, e) for L in range(a.n) for e in range(len(a.t[L])) if not a.t[L][e]]


def touches(a):
    """(u, X, toucher) for every unused segment u and simple endpoint X."""
    out = []
    for (L, e) in unused(a):
        for X in seg_ends(a, L, e):
            if a.is_simple(X):
                out.append(((L, e), X, a.other(X, L)))
    return out


if __name__ == "__main__":
    a = load(sys.argv[1])
    print("n", a.n, "T", a.T(), "Z", a.Z(), "D", a.D(), "triples", [sorted(a.events[e]) for e in a.triples])

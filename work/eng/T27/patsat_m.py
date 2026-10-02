"""Pattern SAT: is a local pattern along a line L realizable by SOME pseudoline arrangement (affine, all pairs cross, points of
multiplicity <= 3)?  UNSAT proves the pattern impossible for every n (restriction principle: dropping all lines outside S keeps
the positive part of the pattern).

Model: K lines labelled by slope 0..K-1 (Euclidean pseudoline arrangement, signotope axioms, kobon_sat.allowed4 with 4-fold points
forbidden).  L = label 0 (WLOG: cyclic label shift, search/symmetry.py).  Along L the order of the crossings is
`before(0,i,j)` (verified numerically: increasing x), and 'side +' = above L (verified numerically).  At a triple slot with
lines p < q (labels): p carries the rays E+ and W-, q carries W+ and E-  (p has the smaller slope: its upper ray is the eastmost).

Pattern: consecutive slots (vertices of L), kind S (one line) / T (two lines), segment triangle bits, hidden sector bits h,
apex flags (multiplicity of the third vertex of a segment triangle), sig flags (multiplicity of the far end of a hidden ray).
Only POSITIVE information is used (a triangle exists, a multiplicity is fixed); zeros are dropped.

Every soft element has a selector literal, so an UNSAT core gives a minimal forbidden sub-pattern.
"""
import sys
import time
from array import array
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "search"))
import inspect  # noqa: F401,E402
sys.path.append(str(ROOT / "work/t3"))
from kobon_sat import allowed4  # noqa: E402
from pysat.solvers import Solver  # noqa: E402

_ALLOWED = None
ALLOW4 = [True]       # T27: 4-fold (and higher) points are allowed; apex flag 1 = exactly triple, 2 = simple, 3 = >= 4-fold


def key3(a, b, c):
    return tuple(sorted((a, b, c)))


class Base:
    """chi model of K labelled pseudolines with derived before / adjacency / triangle / multiplicity variables"""

    def __init__(self, K):
        self.K = K
        self.nv = 0
        self.cl = []
        R = range(K)
        self.R = R
        self.TRUE = self.new()
        self.cl.append([self.TRUE])
        trip = self.trip = list(combinations(R, 3))
        z = self.z = {t: self.new() for t in trip}
        pz = self.pz = {t: self.new() for t in trip}
        ng = self.ng = {t: self.new() for t in trip}
        for t in trip:
            self.cl += [[z[t], pz[t], ng[t]], [-z[t], -pz[t]], [-z[t], -ng[t]], [-pz[t], -ng[t]]]
        val = lambda t, v: {0: z, 1: pz, -1: ng}[v][t]  # noqa: E731
        global _ALLOWED
        if _ALLOWED is None:
            _ALLOWED = allowed4()
        for a, b, c, d in combinations(R, 4):
            ts = [(b, c, d), (a, c, d), (a, b, d), (a, b, c)]
            for v in product((-1, 0, 1), repeat=4):
                if v in _ALLOWED and (ALLOW4[0] or v != (0, 0, 0, 0)):
                    continue
                self.cl.append([-val(t, x) for t, x in zip(ts, v)])

        def before(r, i, j):
            t = key3(r, i, j)
            return ng[t] if i < j else pz[t]
        self.before = before
        A = self.A = {}
        for r in R:
            oth = [x for x in R if x != r]
            for i in oth:
                for j in oth:
                    if i != j:
                        A[r, i, j] = self.new()
            for i in oth:
                for j in oth:
                    if i == j:
                        continue
                    ws = []
                    for l in oth:
                        if l in (i, j):
                            continue
                        w = self.AND([before(r, i, l), before(r, l, j)])
                        ws.append(w)
                        self.cl.append([-A[r, i, j], -w])
                    self.cl.append([-A[r, i, j], before(r, i, j)])
                    self.cl.append([-before(r, i, j), A[r, i, j]] + ws)
        AD = {}
        for r in R:
            for i, j in combinations([x for x in R if x != r], 2):
                AD[r, i, j] = AD[r, j, i] = self.OR([A[r, i, j], A[r, j, i]])
        self.AD = AD
        tri = self.tri = {}
        for (a, b, c) in trip:
            tri[a, b, c] = self.AND([-z[a, b, c], AD[a, b, c], AD[b, a, c], AD[c, a, b]])
        zp = self.zp = {}
        for i, j in combinations(R, 2):
            zp[i, j] = zp[j, i] = self.OR([z[key3(i, j, m)] for m in R if m not in (i, j)]) if K > 2 else -self.TRUE
        zp2 = self.zp2 = {}          # at least two further lines through i ^ j (a >= 4-fold point)
        for i, j in combinations(R, 2):
            oth = [m for m in R if m not in (i, j)]
            zp2[i, j] = zp2[j, i] = (self.OR([self.AND([z[key3(i, j, a)], z[key3(i, j, b)]]) for a, b in combinations(oth, 2)])
                                     if len(oth) >= 2 else -self.TRUE)

    def new(self):
        self.nv += 1
        return self.nv

    def AND(self, lits):
        v = self.new()
        for l in lits:
            self.cl.append([-v, l])
        self.cl.append([v] + [-l for l in lits])
        return v

    def OR(self, lits):
        v = self.new()
        for l in lits:
            self.cl.append([-l, v])
        self.cl.append([-v] + list(lits))
        return v

    def tri3(self, a, b, c):
        return self.tri[key3(a, b, c)]

    def up(self, i, j, l):
        """vertex i^j strictly above line l"""
        a, b, c = sorted((i, j, l))
        return self.pz[a, b, c] if l == b else self.ng[a, b, c]

    def dn(self, i, j, l):
        a, b, c = sorted((i, j, l))
        return self.ng[a, b, c] if l == b else self.pz[a, b, c]


class Pattern:
    """slots: list of (kind, h) kind 'S'/'T', h = (h+, h-) hidden sector bits (T only).
    seg[s] = (top, bottom) triangle bits of the segment between slot s and s+1.
    apex[(s, sigma)] = 1 (triple) / 2 (simple) for the apex of the triangle on segment s side sigma (0 = +, 1 = -).
    sig[(s, ray)] = 0/1 far-end multiplicity of hidden ray ray in 'E+','E-','W+','W-' of T slot s."""

    def __init__(self, slots, seg, apex=None, sig=None, name="", neg=None, ub=None):
        self.slots, self.seg, self.apex, self.sig, self.name = list(slots), dict(seg), dict(apex or {}), dict(sig or {}), name
        self.extra = []                   # cell features: ('unb', s, ray) axis ray beyond the far end of ray is unbounded; ('far', s, ray) far-side triangle
        self.neg = list(neg or [])        # exact mode only: elements that must be ABSENT: ('tri', s, sg) / ('hid', s, sg)
        self.ub = dict(ub or {})          # exact mode only: (slot, sg) -> 1: unbounded ray on that side

    def elements(self):
        """soft elements: ('tri', s, sigma), ('apex', s, sigma, flag), ('hid', s, sigma), ('sig', s, ray, value)"""
        el = []
        for s, bits in sorted(self.seg.items()):
            for sg in (0, 1):
                if bits[sg]:
                    el.append(("tri", s, sg))
                    if (s, sg) in self.apex:
                        el.append(("apex", s, sg, self.apex[(s, sg)]))
        for s, (k, h) in enumerate(self.slots):
            if k == "T":
                for sg in (0, 1):
                    if h[sg]:
                        el.append(("hid", s, sg))
            if k == "M":
                for idx in range(4):
                    if h[idx]:
                        el.append(("hidm", s, idx))
        for (s, ray), v in sorted(self.sig.items()):
            el.append(("sig", s, ray, v))
        el += list(getattr(self, "extra", []))
        return el

    def nlines_upper(self):
        n = 1 + sum(1 if k == "S" else 2 if k == "T" else 3 for k, h in self.slots)
        n += sum(1 for s, (k, h) in enumerate(self.slots) if k == "T" for sg in (0, 1) if h[sg])
        n += sum(1 for e in self.elements() if e[0] == "apex" and e[3] == 1)
        n += sum(1 for e in self.elements() if e[0] == "sig" and e[3] == 1)
        n += sum(1 for e in self.elements() if e[0] == "far")
        for e in self.elements():
            if e[0] == "capx":
                n += e[3] + e[4] + sum(1 for x in e[5:8] if x == 1)
        return n


RAYS = {"E+": (0, "a"), "W-": (1, "a"), "W+": (0, "b"), "E-": (1, "b")}   # ray -> (side, line role a/b)


def build(pat, K, elements=None):
    """returns (Base, selector dict element -> literal).  All soft elements are guarded by selectors."""
    B = Base(K)
    f = B
    m = len(pat.slots)
    lines = list(range(1, K))
    pos = [{l: B.new() for l in lines} for _ in range(m)]
    # each line in at most one slot
    for l in lines:
        for s1, s2 in combinations(range(m), 2):
            B.cl.append([-pos[s1][l], -pos[s2][l]])
    for s, (k, h) in enumerate(pat.slots):
        want = 1 if k == "S" else 2 if k == "T" else 3
        # exactly `want` lines in slot s
        for grp in combinations(lines, want + 1):
            B.cl.append([-pos[s][l] for l in grp])
        for grp in combinations(lines, len(lines) - want + 1):
            B.cl.append([pos[s][l] for l in grp])
        if k == "S":
            for l in lines:
                B.cl.append([-pos[s][l], -B.zp[0, l]])
        else:
            for p, q in combinations(lines, 2):
                B.cl.append([-pos[s][p], -pos[s][q], B.z[key3(0, p, q)]])
    # consecutive slots are consecutive vertices of L
    for s in range(m - 1):
        terms = []
        for l in lines:
            for l2 in lines:
                if l != l2:
                    terms.append(B.AND([pos[s][l], pos[s + 1][l2], B.A[0, l, l2]]))
        B.cl.append(terms)
    sel = {}
    el = pat.elements() if elements is None else elements
    # segment triangles
    X = {}
    for e in el:
        if e[0] in ("tri", "apex"):
            s, sg = e[1], e[2]
            if (s, sg) not in X:
                X[(s, sg)] = []
                for l in lines:
                    for l2 in lines:
                        if l == l2:
                            continue
                        t = B.AND([pos[s][l], pos[s + 1][l2], B.tri3(0, l, l2), B.up(l, l2, 0) if sg == 0 else B.dn(l, l2, 0)])
                        X[(s, sg)].append((t, l, l2))
    for e in el:
        v = B.new()
        sel[e] = v
        if e[0] == "tri":
            B.cl.append([-v] + [t for t, l, l2 in X[(e[1], e[2])]])
        elif e[0] == "apex":
            fl = e[3]

            def apex_lit(l, l2, fl=fl):
                if fl == 2:
                    return [-B.zp[l, l2]]
                if fl == 3:
                    return [B.zp2[l, l2]]
                return [B.zp[l, l2], -B.zp2[l, l2]] if ALLOW4[0] else [B.zp[l, l2]]
            terms = [B.AND([t] + apex_lit(l, l2)) for t, l, l2 in X[(e[1], e[2])]]
            B.cl.append([-v] + terms)
    # hidden sectors (need lazily; also serve sig flags)
    H = {}

    def hid_terms(s, sg):
        if (s, sg) not in H:
            H[(s, sg)] = []
            for p, q in combinations(lines, 2):
                for l in lines:
                    if l in (p, q):
                        continue
                    sidelit = B.up(p, l, 0) if sg == 0 else B.dn(p, l, 0)
                    t = B.AND([pos[s][p], pos[s][q], B.tri3(p, q, l), sidelit])
                    H[(s, sg)].append((t, p, q, l))
        return H[(s, sg)]
    HM = {}

    def hidm_terms(s, idx):
        """M slot with lines a < b < c (labels = slopes): ring E, a+, b+, c+, W, a-, b-, c-.  hE+ = (a+,b+), hE- = (b-,c-), hW+ = (b+,c+), hW- = (a-,b-)
        (h = (hE+, hE-, hW+, hW-)).  'lo' pair = (a,b), 'hi' pair = (b,c)."""
        if (s, idx) not in HM:
            sg = (0, 1, 0, 1)[idx]
            which = ("lo", "hi", "hi", "lo")[idx]
            terms = []
            for p, q in combinations(lines, 2):
                rr = [r for r in lines if r not in (p, q) and ((r > q) if which == "lo" else (r < p))]
                if not rr:
                    continue
                third = B.OR([pos[s][r] for r in rr])
                for l in lines:
                    if l in (p, q):
                        continue
                    sidelit = B.up(p, l, 0) if sg == 0 else B.dn(p, l, 0)
                    terms.append(B.AND([pos[s][p], pos[s][q], third, B.tri3(p, q, l), sidelit]))
            HM[(s, idx)] = terms
        return HM[(s, idx)]
    for e in el:
        if e[0] == "hidm":
            B.cl.append([-sel[e]] + hidm_terms(e[1], e[2]))
    for e in el:
        if e[0] == "hid":
            v = sel[e]
            B.cl.append([-v] + [t for t, p, q, l in hid_terms(e[1], e[2])])
        elif e[0] == "sig":
            s, ray, val = e[1], e[2], e[3]
            sg, role = RAYS[ray]
            v = sel[e]
            # the far end of this ray is a vertex of an adjacent triangle: attach to the segment triangle if it exists,
            # else to the hidden triangle
            k, h = pat.slots[s]
            if ray == "E+":
                tri_el = ("tri", s, 0) if s in pat.seg and pat.seg[s][0] else None
                tri_pos = (s, 0, "E")
            elif ray == "E-":
                tri_el = ("tri", s, 1) if s in pat.seg and pat.seg[s][1] else None
                tri_pos = (s, 1, "E")
            elif ray == "W+":
                tri_el = ("tri", s - 1, 0) if (s - 1) in pat.seg and pat.seg[s - 1][0] else None
                tri_pos = (s - 1, 0, "W")
            else:
                tri_el = ("tri", s - 1, 1) if (s - 1) in pat.seg and pat.seg[s - 1][1] else None
                tri_pos = (s - 1, 1, "W")
            if tri_el is not None:
                key = (tri_pos[0], tri_pos[1])
                if key not in X:
                    X[key] = []
                    for l in lines:
                        for l2 in lines:
                            if l != l2:
                                t = B.AND([pos[key[0]][l], pos[key[0] + 1][l2], B.tri3(0, l, l2),
                                           B.up(l, l2, 0) if key[1] == 0 else B.dn(l, l2, 0)])
                                X[key].append((t, l, l2))
                terms = [B.AND([t, B.zp[l, l2] if val == 1 else -B.zp[l, l2]]) for t, l, l2 in X[key]]
                B.cl.append([-v] + terms)
            elif h[sg]:
                terms = []
                for t, p, q, l in hid_terms(s, sg):
                    r = p if role == "a" else q
                    terms.append(B.AND([t, B.zp[r, l] if val == 1 else -B.zp[r, l]]))
                B.cl.append([-v] + terms)
            else:
                pass          # no adjacent triangle: unconstrained (dropped)
    # cell features (T25): 'unb' / 'far' for a block on ray `ray` of the T slot s
    lo_hi = {}

    def role_lits(s):
        if s not in lo_hi:
            lo = {}
            hi = {}
            for l in lines:
                below = [pos[s][l2] for l2 in lines if l2 < l]
                lo[l] = B.AND([pos[s][l]] + [-b for b in below])
                hi[l] = B.AND([pos[s][l], -lo[l]])
            lo_hi[s] = (lo, hi)
        return lo_hi[s]

    def seg_terms(s0, sg):
        key_ = (s0, sg)
        if key_ not in X:
            X[key_] = []
            for l in lines:
                for l2 in lines:
                    if l != l2:
                        t = B.AND([pos[s0][l], pos[s0 + 1][l2], B.tri3(0, l, l2), B.up(l, l2, 0) if sg == 0 else B.dn(l, l2, 0)])
                        X[key_].append((t, l, l2))
        return X[key_]
    for e in el:
        if e[0] not in ("unb", "far"):
            continue
        s_, ray = e[1], e[2]
        sg, role = RAYS[ray]
        east = ray[0] == "E"
        s0 = s_ if east else s_ - 1
        lo, hi = role_lits(s_)
        car_tab = lo if role == "a" else hi
        hl_tab = hi if role == "a" else lo
        v = B.new()
        sel[e] = v
        terms = []
        for t, l, l2 in seg_terms(s0, sg):
            car, c = (l, l2) if east else (l2, l)          # carrier line (at slot s_) and cap line (at the neighbouring slot)
            if e[0] == "unb":
                # no vertex of the carrier beyond X = carrier ^ c (away from P = carrier ^ line 0)
                m_ = [m for m in lines if m not in (car, c)]
                d1 = B.AND([B.before(car, 0, c)] + [-B.before(car, c, m) for m in m_])
                d2 = B.AND([B.before(car, c, 0)] + [-B.before(car, m, c) for m in m_])
                terms.append(B.AND([t, car_tab[car], B.OR([d1, d2])]))
            else:
                for b_ in lines:
                    if b_ in (car, c):
                        continue
                    for D in lines:
                        if D in (car, c, b_):
                            continue
                        terms.append(B.AND([t, car_tab[car], hl_tab[b_], B.z[key3(b_, c, D)], B.tri3(car, c, D)]))
        B.cl.append([-v] + terms)
    # cap-role cell completions (T25): ('capx', c, sigma, s23, s34, x0, x1, x2) at the S slot c that caps a block on side sigma
    for e in el:
        if e[0] != "capx":
            continue
        c_, sg, s23, s34, x0, x1, x2 = e[1:]
        v = sel[e] if e in sel else B.new()
        sel[e] = v
        terms = []
        T1 = seg_terms(c_ - 1, sg)            # (t, wp, A)
        T2 = seg_terms(c_, sg)                # (t, A, wn)
        by2 = {}
        for t2, A2, wn in T2:
            by2.setdefault(A2, []).append((t2, wn))
        for t1, wp, A in T1:
            for t2, wn in by2.get(A, []):
                if wn == wp:
                    continue
                conj = [t1, t2]
                # sectors at P beyond the flank rays
                if s23 or x0 is not None or x1 is not None:
                    alt23 = []
                    for l in lines:
                        if l in (A, wn, wp):
                            continue
                        f23 = [B.tri3(A, wn, l)]
                        if x0 is not None:
                            f23.append(B.zp[wn, l] if x0 == 1 else -B.zp[wn, l])
                        if x1 is not None:
                            f23.append(B.zp[A, l] if x1 == 1 else -B.zp[A, l])
                        alt23.append(B.AND(f23))
                    conj.append(B.OR(alt23))
                if s34 or x2 is not None or x1 is not None:
                    alt34 = []
                    for l in lines:
                        if l in (A, wn, wp):
                            continue
                        f34 = [B.tri3(A, wp, l)]
                        if x2 is not None:
                            f34.append(B.zp[wp, l] if x2 == 1 else -B.zp[wp, l])
                        if x1 is not None:
                            f34.append(B.zp[A, l] if x1 == 1 else -B.zp[A, l])
                        alt34.append(B.AND(f34))
                    conj.append(B.OR(alt34))
                terms.append(B.AND(conj))
        B.cl.append([-v] + terms)
    # exact mode extras (hard clauses)
    for e in getattr(pat, "neg", []):
        if e[0] == "tri":
            key_ = (e[1], e[2])
            if key_ not in X:
                X[key_] = []
                for l in lines:
                    for l2 in lines:
                        if l != l2:
                            t = B.AND([pos[e[1]][l], pos[e[1] + 1][l2], B.tri3(0, l, l2),
                                       B.up(l, l2, 0) if e[2] == 0 else B.dn(l, l2, 0)])
                            X[key_].append((t, l, l2))
            for t, l, l2 in X[key_]:
                B.cl.append([-t])
        elif e[0] == "hid":
            for t, p_, q_, l in hid_terms(e[1], e[2]):
                B.cl.append([-t])
        elif e[0] == "hidm":
            for t in hidm_terms(e[1], e[2]):
                B.cl.append([-t])
    if getattr(pat, "ub", None):
        sidef = lambda l, m, sg: B.up(l, m, 0) if sg == 0 else B.dn(l, m, 0)
        for (s, sg), v in getattr(pat, "ub", {}).items():
            if not v:
                continue
            k = pat.slots[s][0]
            unb = {}
            for l in lines:
                unb[l] = B.AND([-sidef(l, m, sg) for m in lines if m != l])
            if k == "S":
                for l in lines:
                    B.cl.append([-pos[s][l], unb[l]])
            else:
                B.cl.append([B.AND([pos[s][l], unb[l]]) for l in lines])
    return B, sel


def solve(pat, K=None, Kmin=None, elements=None, want_core=False, timeout=None, solver="cadical153"):
    """SAT test.  K = upper bound on |S| (default from the pattern); tries increasing K' from Kmin (SAT is monotone in K').
    Returns (sat: bool, K used, core (list of elements) or None, seconds)."""
    t0 = time.time()
    Kmax = K or pat.nlines_upper()
    Kmin = Kmin or (1 + sum(1 if k == "S" else 2 if k == "T" else 3 for k, h in pat.slots))
    Kmin = min(max(Kmin, 3), Kmax)
    ks = sorted(set([Kmin, min(Kmax, Kmin + 2), Kmax]))
    for Kp in ks:
        B, sel = build(pat, Kp, elements)
        el = pat.elements() if elements is None else elements
        s = Solver(name=solver, bootstrap_with=B.cl)
        ok = s.solve(assumptions=[sel[e] for e in el])
        if ok:
            model = set(x for x in s.get_model() if x > 0)
            s.delete()
            return True, Kp, None, time.time() - t0
        core = None
        if want_core:
            cs = set(s.get_core())
            core = [e for e in el if sel[e] in cs]
        s.delete()
        if Kp == Kmax:
            return False, Kp, core, time.time() - t0
    return False, Kmax, None, time.time() - t0


def minimize_core(pat, K, core):
    """deletion-based minimal UNSAT subset of soft elements"""
    core = list(core)
    i = 0
    while i < len(core):
        trial = core[:i] + core[i + 1:]
        ok, Kp, _, _ = solve(pat, K, elements=trial)
        if ok:
            i += 1
        else:
            core = trial
    return core


# ---------------------------------------------------------------------------------------------- constructors
def pattern_from_window(prev, cur, nxt, sig=None, name=""):
    """(prev Info, cur (E)Frame, next Info) -> Pattern.  sig: optional tuple (E+, E-, W+, W-) of cur (kind T)."""
    slots, seg, apex = [], {}, {}
    idx = {}
    if prev is not None and prev[2] != (0, 0):
        slots.append(("T", (0, 0)) if prev[2] == (1, 1) else ("S", (0, 0)))
    if prev is not None:
        slots.append((prev[0], prev[1] if prev[0] == "T" else (0, 0)))
    idx["cur"] = len(slots)
    slots.append((cur.kind, cur.h if cur.kind == "T" else (0, 0)))
    if nxt is not None:
        slots.append((nxt[0], nxt[1] if nxt[0] == "T" else (0, 0)))
    if nxt is not None and nxt[2] != (0, 0):
        slots.append(("T", (0, 0)) if nxt[2] == (1, 1) else ("S", (0, 0)))
    c = idx["cur"]
    if prev is not None and prev[2] != (0, 0):
        seg[c - 2] = prev[2]
    if prev is not None:
        seg[c - 1] = cur.bin
    if nxt is not None:
        seg[c] = cur.bout
    if nxt is not None and nxt[2] != (0, 0):
        seg[c + 1] = nxt[2]
    if hasattr(cur, "ain"):
        for sg in (0, 1):
            if cur.ain[sg] and prev is not None:
                apex[(c - 1, sg)] = cur.ain[sg]
            if cur.aout[sg] and nxt is not None:
                apex[(c, sg)] = cur.aout[sg]
    sg_ = {}
    if sig is not None and cur.kind == "T":
        for ray, v in zip(("E+", "E-", "W+", "W-"), sig):
            if v is not None:
                sg_[(c, ray)] = v
    return Pattern(slots, seg, apex, sg_, name)


# ---------------------------------------------------------------------------------------------- restriction / symmetry
def restrict(pat, elements):
    """Pattern containing only `elements` (soft), with the minimal range of slots that they touch (re-indexed).
    Returns a Pattern whose soft elements are exactly the re-indexed ones."""
    touched = set()
    for e in elements:
        if e[0] in ("tri", "apex"):
            touched |= {e[1], e[1] + 1}
        elif e[0] == "hid":
            touched.add(e[1])
        elif e[0] == "sig":
            touched.add(e[1])
            ray = e[2]
            # a sig flag of a ray with no hidden triangle attaches to the neighbouring segment triangle
            if ray in ("W+", "W-"):
                touched.add(e[1] - 1)
            else:
                touched.add(e[1] + 1)
    lo, hi = min(touched), max(touched)
    lo = max(lo, 0)
    hi = min(hi, len(pat.slots) - 1)
    slots = [pat.slots[s] for s in range(lo, hi + 1)]
    # hidden bits only where an element uses them; kinds are kept
    hset = set((e[1] - lo, e[2]) for e in elements if e[0] == "hid")
    slots = [(k, (int((s, 0) in hset), int((s, 1) in hset)) if k == "T" else (0, 0)) for s, (k, h) in enumerate(slots)]
    seg, apex, sig = {}, {}, {}
    for e in elements:
        if e[0] == "tri":
            seg.setdefault(e[1] - lo, [0, 0])[e[2]] = 1
        elif e[0] == "apex":
            apex[(e[1] - lo, e[2])] = e[3]
            seg.setdefault(e[1] - lo, [0, 0])[e[2]] = 1          # an apex flag implies the triangle
        elif e[0] == "sig":
            sig[(e[1] - lo, e[2])] = e[3]
    seg = {s: tuple(b) for s, b in seg.items()}
    # relax a T slot to S when all elements use only one of its two lines (dropping the other line is a restriction)
    used = [set() for _ in slots]
    for e in elements:
        if e[0] in ("tri", "apex"):
            s0, sg = e[1] - lo, e[2]
            used[s0].add("p" if sg == 0 else "q")            # east line of side sg
            used[s0 + 1].add("q" if sg == 0 else "p")        # west line of side sg
        elif e[0] == "hid":
            used[e[1] - lo] |= {"p", "q"}
        elif e[0] == "sig":
            s0 = e[1] - lo
            ray = e[2]
            has_h = slots[s0][0] == "T" and slots[s0][1][0 if ray[1] == "+" else 1]
            used[s0] |= {"p", "q"} if has_h else set()
    slots = [("S", (0, 0)) if (k == "T" and len(used[i]) <= 1) else (k, h) for i, (k, h) in enumerate(slots)]
    return Pattern(slots, seg, apex, sig, pat.name)


def flip_sides(pat):
    m = len(pat.slots)
    slots = [(k, (h[1], h[0])) for k, h in pat.slots]
    seg = {s: (b[1], b[0]) for s, b in pat.seg.items()}
    apex = {(s, 1 - sg): v for (s, sg), v in pat.apex.items()}
    rr = {"E+": "E-", "E-": "E+", "W+": "W-", "W-": "W+"}
    sig = {(s, rr[r]): v for (s, r), v in pat.sig.items()}
    return Pattern(slots, seg, apex, sig, pat.name)


def reverse(pat):
    m = len(pat.slots)
    slots = list(reversed(pat.slots))
    seg = {m - 2 - s: b for s, b in pat.seg.items()}
    apex = {(m - 2 - s, sg): v for (s, sg), v in pat.apex.items()}
    rr = {"E+": "W+", "W+": "E+", "E-": "W-", "W-": "E-"}
    sig = {(m - 1 - s, rr[r]): v for (s, r), v in pat.sig.items()}
    return Pattern(slots, seg, apex, sig, pat.name)


def key(pat):
    return (tuple(pat.slots), tuple(sorted(pat.seg.items())), tuple(sorted(pat.apex.items())), tuple(sorted(pat.sig.items())))


def variants(pat):
    a = pat
    b = flip_sides(pat)
    c = reverse(pat)
    d = flip_sides(c)
    return [a, b, c, d]


def canon(pat):
    return min(variants(pat), key=key)


# ---------------------------------------------------------------------------------------------- proof search
class Timeout(Exception):
    pass


def _solve(s, assumptions, limit=None):
    """solve with an optional wall-clock limit (needs an interruptible solver such as glucose4)"""
    if not limit:
        return s.solve(assumptions=assumptions)
    import threading
    tm = threading.Timer(limit, s.interrupt)
    tm.start()
    try:
        r = s.solve_limited(assumptions=assumptions, expect_interrupt=True)
    finally:
        tm.cancel()
    if r is None:
        raise Timeout()
    return r


def _min_core(solver, sel, elements, limit=None):
    """deletion-minimal subset of `elements` that stays UNSAT under the solver (assumption based)"""
    core = list(elements)
    i = 0
    while i < len(core):
        trial = core[:i] + core[i + 1:]
        if _solve(solver, [sel[e] for e in trial], limit):
            i += 1
        else:
            core = trial
    return core


def _order(els):
    """deletion order: multiplicity flags first (they cost witness lines), then hidden triangles, then segment triangles"""
    rank = {"sig": 0, "apex": 1, "hid": 2, "tri": 3}
    return sorted(els, key=lambda e: rank[e[0]])


def restrict_plain(pat, elements):
    """like restrict() but never relaxes T slots to S"""
    sub = restrict(pat, elements)
    lo = None
    touched = set()
    for e in elements:
        if e[0] in ("tri", "apex"):
            touched |= {e[1], e[1] + 1}
        elif e[0] == "hid":
            touched.add(e[1])
        elif e[0] == "sig":
            touched.add(e[1])
            touched.add(e[1] - 1 if e[2] in ("W+", "W-") else e[1] + 1)
    lo = max(min(touched), 0)
    kinds = [pat.slots[lo + i][0] for i in range(len(sub.slots))]
    sub.slots = [(k, h) for k, (k0, h) in zip(kinds, sub.slots)]
    return sub


def prove(pat, k0=8, want_min=True, solver="cadical153", verbose=False, limit=None):
    """Decide the (positive part of the) pattern.  Returns dict(sat=bool, K, core=Pattern|None, secs, ...).
    UNSAT is only reported once a sub-pattern whose |S| bound is <= the tested K' is refuted."""
    t0 = time.time()
    if limit:
        solver = "glucose4"
    try:
        return _prove(pat, k0, want_min, solver, verbose, limit, t0)
    except Timeout:
        return dict(sat=None, K=None, core=None, secs=time.time() - t0)


def _prove(pat, k0, want_min, solver, verbose, limit, t0):
    full = _order(pat.elements())
    if not full:
        return dict(sat=True, K=0, core=None, secs=0.0)
    Kfull = pat.nlines_upper()
    Kp = min(max(k0, 1 + sum(1 if k == "S" else 2 for k, h in pat.slots)), Kfull)
    while True:
        B, sel = build(pat, Kp)
        s = Solver(name=solver, bootstrap_with=B.cl)
        if _solve(s, [sel[e] for e in full], limit):
            s.delete()
            return dict(sat=True, K=Kp, core=None, secs=time.time() - t0)
        core = _min_core(s, sel, full, limit)
        s.delete()
        cands = []
        for mk in (restrict, restrict_plain):
            sub = mk(pat, core)
            if not any(key(sub) == key(c) for c in cands):
                cands.append(sub)
        good = None
        for sub in cands:
            if sub.nlines_upper() <= Kp and _refute(sub, solver):
                good = sub
                break
        if verbose:
            print("   K'", Kp, "core", len(core), "of", len(full), "bounds", [c.nlines_upper() for c in cands], "good", good is not None, flush=True)
        if good is not None:
            break
        if Kp >= Kfull:
            good = restrict_plain(pat, core)
            break
        Kp = min(max(min(c.nlines_upper() for c in cands), Kp + 1), Kfull)
    if want_min:
        good = minimize(good, solver=solver)
    return dict(sat=False, K=Kp, core=good, secs=time.time() - t0)


def minimize(pat, solver="cadical153"):
    """deletion-minimal UNSAT sub-pattern (each test is a refutation at the bound of the sub-pattern)"""
    cur = pat
    changed = True
    while changed:
        changed = False
        els = _order(cur.elements())
        for i in range(len(els)):
            trial = els[:i] + els[i + 1:]
            if not trial:
                continue
            for mk in (restrict, restrict_plain):
                sub = mk(cur, trial)
                if len(sub.elements()) >= len(cur.elements()):
                    continue                       # deleting an element must shrink the pattern (a flag implies its triangle)
                if _refute(sub, solver):
                    cur = sub
                    changed = True
                    break
            if changed:
                break
    return cur


def _refute(pat, solver="cadical153", limit=120):
    """UNSAT at its own bound K(pat)?  (a timeout counts as 'not refuted', which is the conservative answer)"""
    K = pat.nlines_upper()
    B, sel = build(pat, max(K, 3))
    s = Solver(name="glucose4" if limit else solver, bootstrap_with=B.cl)
    try:
        ok = _solve(s, [sel[e] for e in pat.elements()], limit)
    except Timeout:
        s.delete()
        return False
    s.delete()
    return not ok

def _sigvec(hid):
    """hid code (harvest.hid_code) -> (E+, E-, W+, W-)"""
    return tuple((hid >> k) & 1 for k in range(4))


def pattern_from_frames(frames, hids=None, name=""):
    """k consecutive (enriched) frames of a line; hids = their harvest hid codes (true sig) or None.
    Outer segments (bin of the first, bout of the last frame) get an outer slot when they carry a triangle."""
    slots, seg, apex, sig = [], {}, {}, {}
    f0, fl = frames[0], frames[-1]
    if f0.bin != (0, 0):
        slots.append(("T", (0, 0)) if f0.bin == (1, 1) else ("S", (0, 0)))
        seg[0] = f0.bin
    base = len(slots)
    for i, f in enumerate(frames):
        slots.append((f.kind, f.h if f.kind in ("T", "M") else (0, 0)))
    for i, f in enumerate(frames[:-1]):
        seg[base + i] = f.bout
    if fl.bout != (0, 0):
        slots.append(("T", (0, 0)) if fl.bout == (1, 1) else ("S", (0, 0)))
        seg[base + len(frames) - 1] = fl.bout
    for i, f in enumerate(frames):
        if hasattr(f, "ain"):
            s_ = base + i
            for sg in (0, 1):
                if f.ain[sg] and (s_ - 1) in seg:
                    apex[(s_ - 1, sg)] = f.ain[sg]
                if f.aout[sg] and s_ in seg:
                    apex[(s_, sg)] = f.aout[sg]
        if hids is not None and f.kind == "T":
            for ray, v in zip(("E+", "E-", "W+", "W-"), _sigvec(hids[i])):
                sig[(base + i, ray)] = v
    seg = {s_: b for s_, b in seg.items() if b != (0, 0)}
    return Pattern(slots, seg, apex, sig, name)


def pattern_exact(frames, hids=None, name=""):
    """whole line (exact query): every bit, hidden bit, apex flag and ub flag is imposed; no outer slots, no extra lines."""
    m = len(frames)
    slots = [(f.kind, f.h if f.kind in ("T", "M") else (0, 0)) for f in frames]
    seg, apex, sig, neg, ub = {}, {}, {}, [], {}
    for i, f in enumerate(frames):
        if i < m - 1:
            seg[i] = f.bout
        if f.kind == "M":
            for idx in range(4):
                if not f.h[idx]:
                    neg.append(("hidm", i, idx))
        for sg in (0, 1):
            if i < m - 1 and not f.bout[sg]:
                neg.append(("tri", i, sg))
            if f.kind == "T" and not f.h[sg]:
                neg.append(("hid", i, sg))
            if f.ub[sg]:
                ub[(i, sg)] = 1
            if hasattr(f, "aout") and i < m - 1 and f.aout[sg]:
                apex[(i, sg)] = f.aout[sg]
        if hids is not None and f.kind == "T":
            for ray, v in zip(("E+", "E-", "W+", "W-"), _sigvec(hids[i])):
                sig[(i, ray)] = v
    seg = {s: b for s, b in seg.items() if b != (0, 0)}
    return Pattern(slots, seg, apex, sig, name, neg, ub)


def solve_exact(pat, solver="cadical153", limit=None):
    """SAT/UNSAT of the exact whole-line query on K = 1 + #lines-in-slots lines (no free lines).  Returns (sat, secs, model info)"""
    t0 = time.time()
    K = 1 + sum(1 if k == "S" else 2 if k == "T" else 3 for k, h in pat.slots)
    if limit:
        solver = "glucose4"
    B, sel = build(pat, K)
    s = Solver(name=solver, bootstrap_with=B.cl)
    try:
        ok = _solve(s, [sel[e] for e in pat.elements()], limit)
    except Timeout:
        return None, time.time() - t0, None
    res = None
    if ok:
        M = set(x for x in s.get_model() if x > 0)
        res = {t: (0 if B.z[t] in M else (1 if B.pz[t] in M else -1)) for t in B.trip}
    s.delete()
    return ok, time.time() - t0, res

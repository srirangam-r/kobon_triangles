"""Rule design by LP with the line automaton as separation oracle (task T21).

Idea.  A *rule* is (trigger class, payer role, receiver role, weight w >= 0).  Every line L then ends with
    final_L = v_L (after T1, F)  +  sum_r w_r * net_r(L),   net_r(L) = #(times L receives by r) - #(times L pays by r).
The line automaton of search/line_automaton.py (T20) describes every line by a path of windows (prev, cur, next) with
hidden variables (far-end multiplicities) minimised adversarially per window.  We add to every window the signed rule
counts net_r.  Soundness of the coupling comes for free from the min over hidden variables:
  * payer: the adversary picks the hidden assignment with the trigger true (we pay whenever the trigger MAY hold);
  * receiver: the adversary picks the assignment with the trigger false (we count only when it SURELY holds);
provided that the trigger of a rule is a function of features that BOTH roles can represent (visible or hidden
variables of their windows).  The first catalogue (families AC, AM, MM, CM, kept as `Catalogue`) only uses features that both
roles see and is infeasible even for bridge-free arrangements.  The catalogue that works is `SigCatalogue` (families SIG): payer and
receiver are among A (axis), C (cap), L / R (flank lines) of a block, the rule cell is the FULL signature of the block (ring of the
5 other rays, unbounded flag, partner flags, flanker multiplicities, status of the opposite block), and whatever a role cannot see is an
extra adversarial hidden variable of that role's window.  The first catalogue's families were:
  AC  block signature (status U/I/M, served, flank pair) : axis A <-> cap C          (both see it)
  AM  ring seen from the flank line M                    : axis A <-> flank line M   (ring is common to the 3 lines of P)
  MM  ring seen from the payer                           : flank line <-> flank line
  CM  the two flank statuses                             : cap C <-> flank line M
The LP variables are the weights; the constraints are  2*final >= 0  on every path of the automaton with an odd
number of simple vertices (n even).  Separation = min-plus DP (Bellman-Ford) with the current weights; the witness
path (or negative cycle) yields the next constraint.

    uv run --no-project --with numpy --with scipy --with networkx python search/rule_lp.py lp --enriched --f4p --families SIG \
        [--rfree | --rings T1,T2,... | --noRR] [--k1] [--k2] [--k2g] [--k3] [--umax U] --export rules.json --save w.pkl --dump cuts.json

Certificates found (commands and files: work/eng/T21/certificates.json):
  bridge-free class   --rfree                        rules_rfree.json      (15 rules, denominator 12)
  NB0 (no bridge ray next to a block ray)   --rings NNNNNN,BNNNNN,BNNBNN,BNNRNN,NNNNNR,NNNNRR,NNRNNR,NNNRRR,NNRRRR,RRRRRR   rules_nb0_.json
  C2 = NB0 + BNNNNR,BNNNRR,BRNNNR,BNNRRR,BRNNRR, with --k1 --k2      rules_C2_k12.json     (46 rules, denominator 6)
Facts (flags): F4' always on (--f4p); K1* --k1, K2 --k2, K2g --k2g, K3 --k3 (proved by the lead / T23, see work/eng/DIGEST.md).
Plug-in points for further forbidden patterns:
  window filter   SigCatalogue.window_options / Catalogue.window_options (drop hidden assignments, e.g. k1_violation, k2_violation, k2g_force)
  edge filter     WGraph(edge_allow=f) with f(cur_frame, next_frame) -> bool (e.g. f4p_edge_allow)
  k-gram / state  WGraph.__init__ node tuple (prev, cur, parity, cls, role, k3_state): replace k3_step(state, prev, cur, next_info) by any
                  automaton step returning the new state or None
"""
import collections
import itertools
import sys
from fractions import Fraction as F
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
import inspect  # noqa: F401,E402  (stdlib first: work/t3/inspect.py shadows it)
sys.path.append(str(ROOT / "work/t3"))
import numpy as np  # noqa: E402
import line_automaton as LA  # noqa: E402
from line_automaton import NONE, ER, RING  # noqa: E402

TARGET = 2.0        # 2*final = v2 + 2 sum w net - 2  >= 0   (the constant -1 of v_L is not in v2)
SIGI = {"E+": 0, "E-": 1, "W+": 2, "W-": 3}


# ---------------------------------------------------------------------------------------------------- enriched frames
class EFrame(collections.namedtuple("EFrame", "kind bin bout ub h ain aout")):
    """T20 frame + apex flags: for every segment side carrying a triangle, the multiplicity of the apex vertex of that
    triangle (1 = triple point, 2 = simple vertex; 0 = no triangle).  Both end vertices of a segment see the same flags;
    at a triple vertex the flags of E+, E-, W+, W- (the four hidden rays) are the far-end multiplicities of those rays
    whenever the adjacent segment side carries a triangle (the apex of the triangle in sector (E,E+) is the far end of
    E+, etc.).  At a simple vertex the apexes of the incoming/outgoing triangles on one side are both the far end of
    W's ray on that side, so they coincide (and are triple when both triangles exist, fact F3')."""
    __slots__ = ()

    def info_prev(self, first=False):
        return (self.kind, self.h, self.bin, first)

    def info_next(self, last=False):
        return (self.kind, self.h, self.bout, last)


def _taus(bits):
    for a0 in ((0,) if bits[0] == 0 else (1, 2)):
        for a1 in ((0,) if bits[1] == 0 else (1, 2)):
            yield (a0, a1)


def all_eframes():
    out = []
    for f in LA.all_frames():
        for ain in _taus(f.bin):
            for aout in _taus(f.bout):
                if f.kind == "S":
                    if any(f.bin[s] and f.bout[s] and not (ain[s] == 1 and aout[s] == 1) for s in (0, 1)):
                        continue
                    if any(f.bin[s] and not f.bout[s] and False for s in (0, 1)):
                        continue
                out.append(EFrame(f.kind, f.bin, f.bout, f.ub, f.h, ain, aout))
    return out


def tau_compatible(cur, sig):
    """hidden multiplicities must agree with the apex flags of the adjacent segments"""
    for k, a in enumerate((cur.aout[0], cur.aout[1], cur.ain[0], cur.ain[1])):
        if a and sig[k] != (1 if a == 1 else 0):
            return False
    return True


# ---------------------------------------------------------------------------------------------------- rule events
def ring_of(prev, cur, nxt, sig):
    """statuses (N/B/R) of the six rays in RING order (E, E+, W+, W, W-, E-)"""
    bi, bo = cur.bin, cur.bout
    hp, hm = cur.h
    dbl = (bo[0] and hp, bo[1] and hm, bi[0] and hp, bi[1] and hm)      # E+, E-, W+, W-
    st = {"E": LA.ray_status_L(bo, nxt), "W": LA.ray_status_L(bi, prev)}
    for k, R in enumerate(ER):
        st[R] = ("B" if sig[k] == 0 else "R") if dbl[k] else "N"
    return [st[x] for x in RING]


def block_status(other):
    """U / I / M of the block whose far end is the simple vertex described by Info `other` (kind, h, bits beyond, end)"""
    return "I" if other[3] else "U" if other[2] == NONE else "M"


def canon_ring(r):
    """canonical form (rotation/reflection) of a ring given as string/list of statuses"""
    r = "".join(r)
    best = None
    for t in (r, r[::-1]):
        for k in range(6):
            u = t[k:] + t[:k]
            if best is None or u < best:
                best = u
    return best


def k1_violation(prev, cur, nxt, sig):
    """K1* (proved by the lead, see work/eng/T21/REPORT.md): at a triple frame with hidden sector h[s] = 1 on side s, the sector
    triangle's third side c crosses L exactly once, so it cannot be forced to the right (rf) and to the left (lf) at once.
      rf(s) = bout[s] and (sig[E s] == 0  or  (next is simple and its outgoing bit on side s is 1))
      lf(s) = bin[s]  and (sig[W s] == 0  or  (prev is simple and its incoming bit on side s is 1))"""
    for s_ in (0, 1):
        if not cur.h[s_]:
            continue
        rf = cur.bout[s_] and (sig[s_] == 0 or (nxt is not None and nxt[0] == "S" and nxt[2][s_] == 1))
        lf = cur.bin[s_] and (sig[2 + s_] == 0 or (prev is not None and prev[0] == "S" and prev[2][s_] == 1))
        if rf and lf:
            return True
    return False


def k2_violation(prev, cur, nxt):
    """K2 (kite, proved by the lead): at a 4-triangle simple frame X = S[(1,1)(1,1)] with both neighbours triple, the two opposite outer
    triangles of the kite cannot both be triangles: forbid (prev.h[+] and next.h[-]) or (prev.h[-] and next.h[+])."""
    if cur.kind != "S" or cur.bin != (1, 1) or cur.bout != (1, 1) or prev is None or nxt is None:
        return False
    if prev[0] != "T" or nxt[0] != "T":
        return False
    return bool((prev[1][0] and nxt[1][1]) or (prev[1][1] and nxt[1][0]))


def k2g_force(prev, cur, nxt, sig):
    """K2g (proved by the lead from K2): at a triple frame with bin[s] = bout[s] = h[s] = 1,
       E-side: sig[E s] = 0, sig[W s] = 1, next triple with h[s] = 1 and bits[s] = 1  ==> g[W s] = 1  (the block on E s is served)
       W-side: sig[W s] = 0, sig[E s] = 1, prev triple with h[s] = 1 and bits[s] = 1  ==> g[E s] = 1.
    Returns (g, zero_pO): g the forced gap-end flags (default 0), zero_pO the set of ring positions j of blocks whose hidden-flank
    partner flag pO is forced to 0 (the gap-end ray at the hidden flanker is N)."""
    g = [0, 0, 0, 0]
    zero = set()
    for s_ in (0, 1):
        if not (cur.bin[s_] and cur.bout[s_] and cur.h[s_]):
            continue
        if sig[s_] == 0 and sig[2 + s_] == 1 and nxt is not None and nxt[0] == "T" and nxt[1][s_] and nxt[2][s_]:
            g[2 + s_] = 1
            zero.add(1 if s_ == 0 else 5)
        if sig[2 + s_] == 0 and sig[s_] == 1 and prev is not None and prev[0] == "T" and prev[1][s_] and prev[2][s_]:
            g[s_] = 1
            zero.add(2 if s_ == 0 else 4)
    return tuple(g), zero


def k3_step(state, prev, cur, ni):
    """K3 (run form of K1*, proved by the lead): along a maximal run of consecutive triple vertices linked on side s (bout[s] = 1, the
    apex of that triangle is triple, h[s] = 1 at both), the h[s]-triangles share one third-side line f that crosses L left of the run
    or right of it.  lf(s)(v) forces 'left', rf(s)(v) forces 'right'; a run with both is impossible.
      lf(s)(v) = bin[s]  and (ain[s]  == 2 or (prev simple and prev.bits[s]))
      rf(s)(v) = bout[s] and (aout[s] == 2 or (next simple and next.bits[s]))
    state = (a0, a1) with a_s in {0: nothing yet, 1: lf seen, 2: rf seen} for the run that arrives at cur.  Returns the state that
    leaves cur, or None if forbidden.  Needs the enriched frames (ain / aout)."""
    if cur.kind != "T":
        return (0, 0)
    out = [0, 0]
    for s_ in (0, 1):
        if not cur.h[s_]:
            continue
        st = state[s_]
        lf = bool(cur.bin[s_] and (cur.ain[s_] == 2 or (prev is not None and prev[0] == "S" and prev[2][s_])))
        rf = bool(cur.bout[s_] and (cur.aout[s_] == 2 or (ni is not None and ni[0] == "S" and ni[2][s_])))
        if (lf and rf) or (st == 1 and rf) or (st == 2 and lf):
            return None
        new = 1 if (st == 1 or lf) else 2 if (st == 2 or rf) else 0
        link = bool(ni is not None and ni[0] == "T" and cur.bout[s_] and cur.aout[s_] == 1 and ni[1][s_])
        out[s_] = new if link else 0
    return tuple(out)


def has_rr_block(r):
    """ring r (RING order) contains a block whose two flank rays are both bridges"""
    return any(r[j] == "B" and r[(j - 1) % 6] == "R" and r[(j + 1) % 6] == "R" for j in range(6))


def flt_of(a, b):
    return "".join(sorted((a, b)))


class Catalogue:
    """maps rule keys to column indices (assigned on first use) and generates the events of a window"""

    def __init__(self, families, enriched=False, rfree=False, norr=False, k1=False, k2=False, k2g=False):
        self.k2g = k2g
        self.enriched = enriched
        self.norr = norr
        self.k1 = k1
        self.k2 = k2
        self.rfree = rfree          # restricted class: no bridge (R) rays at all
        self.fam = set(families)
        self.idx = {}
        self.keys = []

    def col(self, key):
        i = self.idx.get(key)
        if i is None:
            i = self.idx[key] = len(self.keys)
            self.keys.append(key)
        return i

    def triple_events(self, prev, cur, nxt, sig):
        """list of (column, signed count) contributed by the ring blocks of the triple vertex `cur` to line L"""
        r = ring_of(prev, cur, nxt, sig)
        out = collections.Counter()
        fam = self.fam
        for j in range(6):
            if r[j] != "B":
                continue
            ring = tuple(r[(j + t) % 6] for t in range(6))
            fr, fl = ring[1], ring[5]                       # right / left flank status (N or R)
            if j % 3 == 0:                                  # L is the axis
                if j == 0:
                    other, fls = nxt, (SIGI["E+"], SIGI["E-"])
                else:
                    other, fls = prev, (SIGI["W+"], SIGI["W-"])
                nb = other[2]
                s = block_status(other)
                sv = int(sig[fls[0]] == 1 and sig[fls[1]] == 1 and (nb[0] == 0 or nb[1] == 0))
                flt = flt_of(fr, fl)
                if "AC" in fam:
                    out[self.col(("AC", "A>C", s, sv, flt))] -= 1
                    out[self.col(("AC", "C>A", s, sv, flt))] += 1
                for rk in (ring[1:], ring[:0:-1]):          # M_right, M_left seen from the flank going away
                    if "AM" in fam:
                        out[self.col(("AM", "A>M", rk))] -= 1
                        out[self.col(("AM", "M>A", rk))] += 1
            else:
                # L is a flank line M: flank position j-1 (going away: decreasing) or j+1 (increasing)
                if (j - 1) % 3 == 0:
                    rk = ring[:0:-1]                        # flank at ring[5]; away = decreasing
                    fM, fO = fl, fr
                else:
                    rk = ring[1:]
                    fM, fO = fr, fl
                if "AM" in fam:
                    out[self.col(("AM", "A>M", rk))] += 1
                    out[self.col(("AM", "M>A", rk))] -= 1
                if "CM" in fam:
                    out[self.col(("CM", "C>M", fM, fO))] += 1
                    out[self.col(("CM", "M>C", fM, fO))] -= 1
                if "MM" in fam:
                    # L = M pays / receives the other flank line; key = ring seen from the payer's flank
                    out[self.col(("MM", rk))] -= 1                                  # L pays (L is the payer of its own ring)
                    rk2 = ring[1:] if rk == ring[:0:-1] else ring[:0:-1]              # ring seen from the other flank line
                    out[self.col(("MM", rk2))] += 1                                  # the other flank line pays L
        return [(c, x) for c, x in out.items() if x]

    def simple_events(self, prev, cur, nxt):
        """cap events at a simple vertex: for each side k where L caps a block (bin[k] = bout[k] = 1)"""
        out = collections.Counter()
        if prev is None or nxt is None:
            return []
        fam = self.fam
        for k in (0, 1):
            if not (cur.bin[k] and cur.bout[k]):
                continue
            o = 1 - k
            s = "I" if cur.ub[o] else "U" if cur.bin[o] + cur.bout[o] == 0 else "M"
            fp = "R" if (prev[0] == "T" and prev[1][k]) else "N"
            fn = "R" if (nxt[0] == "T" and nxt[1][k]) else "N"
            sv = int(prev[0] == "T" and nxt[0] == "T" and (cur.bin[o] == 0 or cur.bout[o] == 0))
            if "AC" in fam:
                flt = flt_of(fp, fn)
                out[self.col(("AC", "A>C", s, sv, flt))] += 1
                out[self.col(("AC", "C>A", s, sv, flt))] -= 1
            if "CM" in fam:
                for (fM, fO) in ((fp, fn), (fn, fp)):
                    out[self.col(("CM", "C>M", fM, fO))] -= 1
                    out[self.col(("CM", "M>C", fM, fO))] += 1
        return [(c, x) for c, x in out.items() if x]

    def window_options(self, prev, cur, nxt):
        """set of (v2, p, nRN, nRR, terms) over the hidden assignments of the window; terms = tuple of terms, a term is a tuple
        of alternative event vectors (the adversary picks one; here always a single one)"""
        if cur.kind == "S":
            if self.k2 and k2_violation(prev, cur, nxt):
                return set()
            if self.norr and prev is not None and nxt is not None:
                for k in (0, 1):
                    if cur.bin[k] and cur.bout[k] and prev[0] == "T" and prev[1][k] and nxt[0] == "T" and nxt[1][k]:
                        return set()
            p, v2, nRN, nRR, nT = LA.exact_vec(prev, cur, nxt)
            ev = tuple(sorted(self.simple_events(prev, cur, nxt)))
            return {(v2, p, nRN, nRR, ((ev,),) if ev else ())}
        res = set()
        for (sig, g) in LA.sig_domain(prev, cur, nxt):
            if self.enriched and not tau_compatible(cur, sig):
                continue
            if self.rfree and "R" in ring_of(prev, cur, nxt, sig):
                continue
            if self.norr and has_rr_block(ring_of(prev, cur, nxt, sig)):
                continue
            if self.k1 and k1_violation(prev, cur, nxt, sig):
                continue
            if self.k2g:
                g = k2g_force(prev, cur, nxt, sig)[0]
            p, v2, nRN, nRR, nT = LA.exact_vec(prev, cur, nxt, (sig, g))
            ev = tuple(sorted(self.triple_events(prev, cur, nxt, sig)))
            res.add((v2, p, nRN, nRR, ((ev,),) if ev else ()))
        return res


# ---------------------------------------------------------------------------------------------------- full block signatures
NOOTH = (9, 9, 9)
OTH_STATUSES = ((1, 0, 0), (0, 0, 0), (0, 1, 0), (0, 0, 1), (0, 1, 1))       # I, U, M(left), M(right), M(both)
POS_IDX = {1: 0, 5: 1, 2: 2, 4: 3}      # ring position of a hidden ray -> index in sig (E+, E-, W+, W-)
# flank line M of a block at ring position j (M's own rays are positions 0 and 3):
#   (role side of M, neighbour holding the far end of M's flank ray, side of the block ray relative to M, own flank position,
#    hidden flank position)
M_TABLE = {1: ("L", "nxt", 0, 0, 2), 2: ("R", "prev", 0, 3, 1), 4: ("L", "prev", 1, 3, 5), 5: ("R", "nxt", 1, 0, 4)}


def mirror_sig(sg):
    ring5, u, pL, pR, tL, tR, oth = sg
    return (tuple(reversed(ring5)), u, pR, pL, tR, tL, (oth[0], oth[2], oth[1]))


class SigCatalogue:
    """Rules = (payer role, receiver role, cell) with cell = the FULL local signature of a block b = [P, X] (ring of the 5 other
    rays at P starting at the right flank, unbounded flag u, partner flags pL/pR (the face beyond X on that side is a triangle),
    flanker multiplicities tL/tR, and the status of the opposite block of the axis if there is one).  Roles: A axis, C cap,
    L/R flank lines (M when the signature is mirror symmetric).  Each role evaluates the signature from its own window; the
    parts it cannot see are extra adversarial hidden variables of that role (min over completions in the window).
    Payer: completion with the trigger true costs; receiver: completion with the trigger false is worst."""

    def __init__(self, enriched=True, rfree=False, pairs=None, norr=False, rings=None, k1=False, k2=False, k2g=False):
        self.enriched, self.rfree, self.norr, self.k1, self.k2, self.k2g = enriched, rfree, norr, k1, k2, k2g
        self.rings = None if rings is None else {canon_ring(x) for x in rings}     # allowed canonical ring types (None = all)
        self.idx, self.keys = {}, []
        self.pairs = pairs                      # None = all ordered pairs
        self._rv = {}

    def col(self, key):
        i = self.idx.get(key)
        if i is None:
            i = self.idx[key] = len(self.keys)
            self.keys.append(key)
        return i

    def role_vec(self, role, sg):
        """event vector of a line playing `role` in the block with signature sg (block-frame orientation)"""
        k = (role, sg)
        v = self._rv.get(k)
        if v is not None:
            return v
        sm = mirror_sig(sg)
        swap = sm < sg
        cs = sm if swap else sg
        symm = sm == sg
        r = role
        if swap and r in "LR":
            r = "R" if r == "L" else "L"

        def lab(x):
            return "M" if symm and x in "LR" else x
        out = collections.Counter()
        for q in "ACLR":
            if q == r:
                continue
            if self.pairs is None or (lab(r), lab(q)) in self.pairs:
                out[self.col((lab(r), lab(q), cs))] -= 1
            if self.pairs is None or (lab(q), lab(r)) in self.pairs:
                out[self.col((lab(q), lab(r), cs))] += 1
        v = tuple(sorted((c, x) for c, x in out.items() if x))
        self._rv[k] = v
        return v

    # ---- windows
    def window_options(self, prev, cur, nxt):
        if cur.kind == "S":
            if self.k2 and k2_violation(prev, cur, nxt):
                return set()
            p, v2, nRN, nRR, nT = LA.exact_vec(prev, cur, nxt)
            ct = self.cap_terms(prev, cur, nxt)
            return set() if ct is None else {(v2, p, nRN, nRR, ct)}
        res = set()
        for (sig, g) in LA.sig_domain(prev, cur, nxt):
            if self.enriched and not tau_compatible(cur, sig):
                continue
            r = ring_of(prev, cur, nxt, sig)
            if self.rfree and "R" in r:
                continue
            if self.norr and has_rr_block(r):
                continue
            if self.rings is not None and canon_ring(r) not in self.rings:
                continue
            if self.k1 and k1_violation(prev, cur, nxt, sig):
                continue
            zero = set()
            if self.k2g:
                g, zero = k2g_force(prev, cur, nxt, sig)
            p, v2, nRN, nRR, nT = LA.exact_vec(prev, cur, nxt, (sig, g))
            res.add((v2, p, nRN, nRR, self.triple_terms(prev, cur, nxt, sig, r, zero)))
        return res

    def cap_terms(self, prev, cur, nxt):
        if prev is None or nxt is None:
            return ()
        terms = []
        for k in (0, 1):
            if not (cur.bin[k] and cur.bout[k]):
                continue
            o = 1 - k
            u = int(cur.ub[o])
            pR, pL = cur.bin[o], cur.bout[o]                 # R side = predecessor, L side = successor
            tR, tL = int(prev[0] == "T"), int(nxt[0] == "T")
            fR = "R" if (prev[0] == "T" and prev[1][k]) else "N"
            fL = "R" if (nxt[0] == "T" and nxt[1][k]) else "N"
            s12, s45 = fR == "R", fL == "R"
            if self.norr and s12 and s45:
                return None
            if self.rfree and (s12 or s45):
                return None
            opts = set()
            for s23 in (0, 1):
                for s34 in (0, 1):
                    dbl = (s12 and s23, s23 and s34, s34 and s45)
                    for far in itertools.product(*[(0, 1) if d else (None,) for d in dbl]):
                        x = ["N" if d is None else ("B" if d == 0 else "R") for d in far]
                        if (x[0] == "B" and x[1] == "B") or (x[1] == "B" and x[2] == "B"):
                            continue
                        if self.rfree and "R" in x:
                            continue
                        if self.rings is not None and canon_ring(("B", fR) + tuple(x) + (fL,)) not in self.rings:
                            continue
                        if self.norr and ((x[0] == "B" and (fR == "R" and x[1] == "R")) or (x[1] == "B" and x[0] == "R" and x[2] == "R")
                                          or (x[2] == "B" and x[1] == "R" and fL == "R")):
                            continue
                        ring5 = (fR, x[0], x[1], x[2], fL)
                        for oth in (OTH_STATUSES if x[1] == "B" else (NOOTH,)):
                            opts.add(self.role_vec("C", (ring5, u, pL, pR, tL, tR, oth)))
            if not opts:
                return None                 # no consistent completion of the block's point: the window cannot occur
            terms.append(tuple(sorted(opts)))
        return tuple(sorted(terms))

    def triple_terms(self, prev, cur, nxt, sig, r, zero=()):
        terms = []
        done = set()
        for j in range(6):
            if r[j] != "B" or j in done:
                continue
            ring5 = tuple(r[(j + t) % 6] for t in range(1, 6))
            if j % 3 == 0:
                terms.append((self.role_vec("A", self.sig_axis(prev, nxt, sig, r, j)),))
                continue
            # flank line: joint completions with the opposite block if it is also a block
            jo = (j + 3) % 6
            grp = [j] + ([jo] if r[jo] == "B" else [])
            done.update(grp)
            info = []
            for jj in grp:
                side, ok, sg_, own, hid = M_TABLE[jj]
                other = nxt if ok == "nxt" else prev
                pM = other[1][sg_] if other[0] == "T" else 0
                tOwn = int(other[0] == "T")
                tHid = sig[POS_IDX[hid]]
                info.append((jj, side, pM, tOwn, tHid))
            opts = set()
            for comp in itertools.product(*[self._m_completions(pM, tHid, jj in zero) for (jj, side, pM, tOwn, tHid) in info]):
                vec = collections.Counter()
                sgs = []
                for (jj, side, pM, tOwn, tHid), (u, pO) in zip(info, comp):
                    sgs.append((jj, side, pM, tOwn, tHid, u, pO))
                for idx_, (jj, side, pM, tOwn, tHid, u, pO) in enumerate(sgs):
                    if side == "L":
                        pL, pR, tL, tR = pM, pO, tOwn, tHid
                    else:
                        pR, pL, tR, tL = pM, pO, tOwn, tHid
                    if len(sgs) == 2:
                        jj2, side2, pM2, tOwn2, tHid2, u2, pO2 = sgs[1 - idx_]
                        oth = (u2, pM2, pO2) if side2 == "L" else (u2, pO2, pM2)
                    else:
                        oth = NOOTH
                    r5 = tuple(r[(jj + t) % 6] for t in range(1, 6))
                    for cc, x in self.role_vec(side, (r5, u, pL, pR, tL, tR, oth)):
                        vec[cc] += x
                opts.add(tuple(sorted((c, x) for c, x in vec.items() if x)))
            terms.append(tuple(sorted(opts)))
        return tuple(sorted(terms))

    @staticmethod
    def _m_completions(pM, tHid, zero_pO=False):
        out = []
        for u in (0, 1):
            for pO in (0, 1):
                if u and (pM or pO):
                    continue
                if pO and (not tHid or zero_pO):
                    continue
                out.append((u, pO))
        return out

    def sig_axis(self, prev, nxt, sig, r, j):
        """full signature of the block on the axis's own ray j (0 = E, 3 = W); everything is visible"""
        ring5 = tuple(r[(j + t) % 6] for t in range(1, 6))
        if j == 0:
            other, other2 = nxt, prev
            pR, pL = other[2][0], other[2][1]
            tR, tL = sig[POS_IDX[1]], sig[POS_IDX[5]]
            pR2, pL2 = None, None
        else:
            other, other2 = prev, nxt
            pR, pL = other[2][1], other[2][0]
            tR, tL = sig[POS_IDX[4]], sig[POS_IDX[2]]
        u = int(bool(other[3]))
        oth = NOOTH
        if r[(j + 3) % 6] == "B":
            u2 = int(bool(other2[3]))
            if j == 0:
                pR2, pL2 = other2[2][1], other2[2][0]
            else:
                pR2, pL2 = other2[2][0], other2[2][1]
            oth = (u2, pL2, pR2)
        return (ring5, u, pL, pR, tL, tR, oth)


# ---------------------------------------------------------------------------------------------------- graph
class WGraph:
    """product graph with window-indexed edges.  node = (prev info, frame, parity of #S, first-vertex ub class, is_last)."""

    def __init__(self, cat, allow=lambda f: True, edge_allow=lambda c, n: True, allowed=None, k3=False):
        """allowed: optional set of windows (prev, cur, next); only these may occur (empirical automaton)"""
        self.cat = cat
        frames = [f for f in (all_eframes() if cat.enriched else LA.all_frames()) if allow(f)]
        by_bin = collections.defaultdict(list)
        for f in frames:
            by_bin[f.bin].append(f)
        print(f"frames: {len(frames)}", flush=True)
        self.win_id, self.win_list = {}, []
        node_id, nodes = {}, []

        def nid(x):
            if x not in node_id:
                node_id[x] = len(nodes)
                nodes.append(x)
            return node_id[x]

        def wid(prev, cur, nxt):
            k = (prev, cur, nxt)
            i = self.win_id.get(k)
            if i is None:
                i = self.win_id[k] = len(self.win_list)
                self.win_list.append(k)
            return i

        starts, edges, terms, stack = [], [], [], []
        for f in frames:
            if f.bin == NONE:
                x = (None, f, 1 if f.kind == "S" else 0, f.ub, 0, (0, 0))
                starts.append(nid(x))
                stack.append(x)
        seen = set(stack)
        while stack:
            x = stack.pop()
            prev, cur, par, cls, role, k3s = x
            u = node_id[x]
            if role == 1:
                if k3 and k3_step(k3s, prev, cur, None) is None:
                    continue
                if LA.ends_compatible_cls(cls, cur) and (allowed is None or (prev, cur, None) in allowed):
                    terms.append((u, wid(prev, cur, None), par))
                continue
            for nxt in by_bin[cur.bout]:
                if not LA.edge_ok(cur, nxt) or not edge_allow(cur, nxt):
                    continue
                if cat.enriched and cur.aout != nxt.ain:
                    continue
                for last in (0, 1):
                    if last and nxt.bout != NONE:
                        continue
                    if nxt.kind == "T" and nxt.ub != NONE and not last:
                        continue
                    ni = nxt.info_next(bool(last))
                    if allowed is not None and (prev, cur, ni) not in allowed:
                        continue
                    k3n = (0, 0)
                    if k3:
                        k3n = k3_step(k3s, prev, cur, ni)
                        if k3n is None:
                            continue
                    y = (cur.info_prev(prev is None), nxt, (par + (nxt.kind == "S")) % 2, cls, last, k3n)
                    if y not in seen:
                        seen.add(y)
                        stack.append(y)
                    nid(y)
                    edges.append((u, node_id[y], wid(prev, cur, ni)))
        self.nodes = nodes
        self.N = len(nodes)
        # options per window -> sparse matrices (windows with no admissible hidden assignment are dropped)
        t0 = time.time()
        term_id, term_list = {}, []

        def tid(term):
            i = term_id.get(term)
            if i is None:
                i = term_id[term] = len(term_list)
                term_list.append(term)
            return i

        valid, wopts = {}, []
        for i, (p, c, n_) in enumerate(self.win_list):
            opts = self.cat.window_options(p, c, n_)
            conv = sorted({(o[0], tuple(sorted(tid(t) for t in o[4]))) for o in opts})
            if conv:
                valid[i] = len(valid)
                wopts.append(conv)
        self.win_old = [None] * len(valid)
        for i, j in valid.items():
            self.win_old[j] = i
        ov2, win_of, wo_i, wo_j, wo_v = [], [], [], [], []
        for j, conv in enumerate(wopts):
            for (v2, tids) in conv:
                r = len(ov2)
                ov2.append(v2)
                win_of.append(j)
                for t, c in collections.Counter(tids).items():
                    wo_i.append(r)
                    wo_j.append(t)
                    wo_v.append(c)
        self.win_list = [self.win_list[i] for i in self.win_old]
        edges = [(a, b, valid[w]) for (a, b, w) in edges if w in valid]
        terms = [(u, valid[w], par) for (u, w, par) in terms if w in valid]
        self.K = len(self.cat.keys)
        self.term_list = term_list
        self.ov2 = np.array(ov2, dtype=np.float64)
        self.opt_win = np.array(win_of, dtype=np.int64)
        from scipy.sparse import csr_matrix
        nt = max(len(term_list), 1)
        self.WO = csr_matrix((wo_v, (wo_i, wo_j)), shape=(len(ov2), nt), dtype=np.float64)
        ti, tj, tv_, tstart, trow = [], [], [], [], 0
        for t in term_list:
            tstart.append(trow)
            for opt in t:
                for (c, x) in opt:
                    ti.append(trow)
                    tj.append(c)
                    tv_.append(x)
                trow += 1
        self.TO = csr_matrix((tv_, (ti, tj)), shape=(max(trow, 1), max(self.K, 1)), dtype=np.float64)
        self.term_start = np.array(tstart if tstart else [0], dtype=np.int64)
        self.n_term_opts = trow
        self.win_start = np.searchsorted(self.opt_win, np.arange(len(self.win_list)))
        # trimming: keep nodes that reach a terminal with parity 1 and are reachable from starts (by construction)
        radj = collections.defaultdict(list)
        for (a, b, w) in edges:
            radj[b].append(a)
        co = set(t[0] for t in terms if t[2] == 1)
        st = list(co)
        while st:
            x = st.pop()
            for y in radj[x]:
                if y not in co:
                    co.add(y)
                    st.append(y)
        fwd = collections.defaultdict(list)
        for (a, b, w) in edges:
            if a in co and b in co:
                fwd[a].append(b)
        reach = set(s0 for s0 in starts if s0 in co)
        st = list(reach)
        while st:
            x = st.pop()
            for y in fwd[x]:
                if y not in reach:
                    reach.add(y)
                    st.append(y)
        co = co & reach
        self.edges = [(a, b, w) for (a, b, w) in edges if a in co and b in co]
        self.starts = [s0 for s0 in starts if s0 in co]
        self.terms = [(u, w) for (u, w, par) in terms if par == 1 and u in co]
        self.src = np.array([e[0] for e in self.edges], dtype=np.int64)
        self.dst = np.array([e[1] for e in self.edges], dtype=np.int64)
        self.ew = np.array([e[2] for e in self.edges], dtype=np.int64)
        self.tn = np.array([t[0] for t in self.terms], dtype=np.int64)
        self.tw = np.array([t[1] for t in self.terms], dtype=np.int64)
        print(f"graph: {self.N} nodes, {len(self.edges)} edges (trimmed), {len(self.win_list)} windows, "
              f"{len(ov2)} window options, {len(term_list)} terms ({trow} term options), K={self.K} rule columns, "
              f"options {time.time() - t0:.1f}s", flush=True)

    # ------------------------------------------------------------------------------------ evaluation
    def window_min(self, w, scale=1):
        """window minima of  scale * v2 + 2 * (w . counts)  (with integer w and scale this is exact integer arithmetic)"""
        tov = self.TO @ w if self.n_term_opts else np.zeros(1)
        tval = 2.0 * np.minimum.reduceat(tov, self.term_start) if len(self.term_list) else np.zeros(1)
        val = scale * self.ov2 + self.WO @ tval
        self._tov, self._tval = tov, tval
        return np.minimum.reduceat(val, self.win_start), val

    def solve(self, w, want="path", tol=1e-9, max_iter=None, scale=1):
        """min over all admissible paths of 2*final.  Returns (value, kind, counts) where kind = 'path' | 'cycle'
        and counts = (v2, dict column -> signed count) of the witness, or (None, ...) if unreachable."""
        wmin, val = self.window_min(w, scale)
        ewt = wmin[self.ew]
        N = self.N
        INF = 1e18
        dist = np.full(N, INF)
        par = np.full(N, -1, dtype=np.int64)
        pare = np.full(N, -1, dtype=np.int64)
        dist[self.starts] = 0.0
        src, dst = self.src, self.dst
        for it in range(max_iter or N + 2):
            ok = dist[src] < INF
            cand = np.where(ok, dist[src] + ewt, INF)
            best = dist.copy()
            np.minimum.at(best, dst, cand)
            imp = best < dist - tol
            if not imp.any():
                break
            es = np.nonzero(ok & (cand <= best[dst] + 1e-12) & imp[dst])[0]
            # choose one improving edge per destination (last write wins)
            par[dst[es]] = src[es]
            pare[dst[es]] = es
            dist = np.where(imp, best, dist)
            if it % 10 == 9:
                cyc = self._parent_cycle(par, pare, ewt)
                if cyc is not None and cyc[0] < -tol:
                    return cyc[0], "cycle", self._counts(cyc[1], wmin, val)
        else:
            cyc = self._parent_cycle(par, pare, ewt)
            if cyc is not None:
                return cyc[0], "cycle", self._counts(cyc[1], wmin, val)
        tot = np.where(dist[self.tn] < INF, dist[self.tn] + wmin[self.tw], INF)
        k = int(np.argmin(tot))
        if tot[k] >= INF:
            return None, "none", None
        # path: follow parents
        path_edges = []
        x = int(self.tn[k])
        seen = set()
        while pare[x] >= 0 and x not in seen:
            seen.add(x)
            e = int(pare[x])
            path_edges.append(e)
            x = int(src[e])
        path_edges = path_edges[::-1]
        cnt = self._counts(path_edges, wmin, val, extra_window=int(self.tw[k]))
        return float(tot[k]), "path", cnt

    def solve_bounded(self, w, umax, scale=1):
        """min over admissible paths with n - 1 = #simple + 2 #triple <= umax (n even: odd number of units) of the path value,
        by a layered DP over the consumed units (no cycles are involved).  Returns (value, 'path', counts, units)."""
        wmin, val = self.window_min(w, scale)
        ewt = wmin[self.ew]
        N = self.N
        INF = 1e18
        if not hasattr(self, "_kunits"):
            self._kunits = np.array([2 if self.nodes[i][1].kind == "T" else 1 for i in range(N)])
        ku = self._kunits
        unit_e = ku[self.src]
        F = np.full((umax + 1, N), INF)
        Pe = np.full((umax + 1, N), -1, dtype=np.int64)
        F[0][self.starts] = 0.0
        for c in range(umax + 1):
            fc = F[c]
            ok = fc[self.src] < INF
            for c0 in (1, 2):
                c2 = c + c0
                if c2 > umax:
                    continue
                m = np.nonzero(ok & (unit_e == c0))[0]
                if not len(m):
                    continue
                cand = fc[self.src[m]] + ewt[m]
                best = F[c2].copy()
                np.minimum.at(best, self.dst[m], cand)
                imp = best < F[c2] - 1e-9
                if imp.any():
                    sel = m[cand <= best[self.dst[m]] + 1e-12]
                    sel = sel[imp[self.dst[sel]]]
                    Pe[c2][self.dst[sel]] = sel
                    F[c2] = np.where(imp, best, F[c2])
        bestv, bu, bnode, bc = INF, None, None, None
        for u_, wi in zip(self.tn, self.tw):
            uu = int(ku[u_])
            for c in range(0, umax + 1 - uu):
                v = F[c][u_]
                if v < INF and v + wmin[wi] < bestv:
                    bestv, bnode, bc, bu = v + wmin[wi], int(u_), c, (c + uu, int(wi))
        if bnode is None:
            return None, "none", None, None
        edges = []
        x, c = bnode, bc
        while c > 0:
            e = int(Pe[c][x])
            edges.append(e)
            c -= int(unit_e[e])
            x = int(self.src[e])
        edges = edges[::-1]
        cnt = self._counts(edges, wmin, val, extra_window=bu[1])
        return float(bestv), "path", cnt, bu[0]

    def _parent_cycle(self, par, pare, ewt):
        N = self.N
        state = np.zeros(N, dtype=np.int8)
        for s in range(N):
            if state[s] or par[s] < 0:
                continue
            chain, x = [], s
            while x >= 0 and state[x] == 0:
                state[x] = 1
                chain.append(x)
                x = par[x]
            if x >= 0 and state[x] == 1 and x in chain:
                cyc = chain[chain.index(x):]
                edges = [int(pare[y]) for y in cyc][::-1]
                tot = float(sum(ewt[e] for e in edges))
                for y in chain:
                    state[y] = 2
                return tot, edges
            for y in chain:
                state[y] = 2
        return None

    def _counts(self, edges, wmin, val, extra_window=None):
        """aggregate v2 and signed rule counts of the window sequence (argmin option per window and per term at the current w)"""
        v2 = 0
        cnt = collections.Counter()
        wins = [int(self.ew[e]) for e in edges]
        if extra_window is not None:
            wins.append(extra_window)
        WO = self.WO
        for wi in wins:
            lo = self.win_start[wi]
            hi = self.win_start[wi + 1] if wi + 1 < len(self.win_start) else len(self.opt_win)
            r = lo + int(np.argmin(val[lo:hi]))
            v2 += int(self.ov2[r])
            for k in range(WO.indptr[r], WO.indptr[r + 1]):
                t, mult = int(WO.indices[k]), int(WO.data[k])
                t0_ = self.term_start[t]
                t1_ = self.term_start[t + 1] if t + 1 < len(self.term_start) else self.n_term_opts
                o = t0_ + int(np.argmin(self._tov[t0_:t1_]))
                for (c, x) in self.term_list[t][o - t0_]:
                    cnt[c] += x * mult
        return v2, {c: x for c, x in cnt.items() if x}, wins


# ---------------------------------------------------------------------------------------------------- API for later users
def f4p_edge_allow(c, n):
    """extra fact F4' as an edge filter: two consecutive simple vertices cannot both cap a block on the same side"""
    if c.kind == "S" and n.kind == "S":
        for s_ in (0, 1):
            if c.bin[s_] and c.bout[s_] and n.bout[s_]:
                return False
    return True


def build_graph(rings=None, rfree=False, k1=False, k2=False, f4p=True):
    """the enriched automaton with the SIG rule catalogue (the graph on which the certificates live)"""
    cat = SigCatalogue(enriched=True, rfree=rfree, rings=None if rings is None else list(rings), k1=k1, k2=k2)
    return WGraph(cat, edge_allow=f4p_edge_allow if f4p else (lambda c, n: True))


def load_rules(G, path):
    """weight vector (integers) and denominator from a json written by --export; keys that do not occur in G get weight 0"""
    import json
    d = json.load(open(path))
    D = d["denominator"]
    w = np.zeros(G.K)
    for r in d["rules"]:
        key = (r["payer"], r["receiver"], (tuple(r["ring5"]), r["u"], r["pL"], r["pR"], r["tL"], r["tR"], tuple(r["oth"])))
        if key in G.cat.idx:
            w[G.cat.idx[key]] = F(r["weight"]) * D
    return w, D


# ---------------------------------------------------------------------------------------------------- data side
def apex_flags(ch, L):
    """apex multiplicity flags of every bounded segment of line L: list of (a+, a-), 1 = triple apex, 2 = simple apex, 0 = no
    triangle on that side"""
    a = ch.a
    row = a.rows[L]
    out = [[0, 0] for _ in range(len(row) - 1)]
    for f in a.tris:
        for (x, e, side) in f:
            if x != L:
                continue
            others = [(y, e2) for (y, e2, s2) in f if y != L]
            (y1, e1), (y2, e2) = others
            v1 = {a.rows[y1][e1], a.rows[y1][e1 + 1]}
            v2 = {a.rows[y2][e2], a.rows[y2][e2 + 1]}
            apex = (v1 & v2) - {row[e], row[e + 1]}
            assert len(apex) == 1, (L, e, apex)
            (ap,) = apex
            out[e][0 if side == 1 else 1] = 1 if len(a.events[ap]) == 3 else 2
    return [tuple(x) for x in out]


def eframes_of_line(ch, L):
    """(enriched frames, hidden assignments) of line L; interior triple frames have their ub flags dropped"""
    frames, hids = LA.extract(ch, L)
    frames = LA.normalise(frames)
    ap = apex_flags(ch, L)
    m = len(frames)
    ef = []
    for i, f in enumerate(frames):
        ain = ap[i - 1] if i > 0 else (0, 0)
        aout = ap[i] if i < m - 1 else (0, 0)
        ef.append(EFrame(f.kind, f.bin, f.bout, f.ub, f.h, ain, aout))
    return ef, hids


_EFS = None


def check_eline(ch, L):
    """soundness of the enriched model on a real line: frames enumerated, edges allowed, true hidden assignment admissible"""
    global _EFS
    if _EFS is None:
        _EFS = frozenset(all_eframes())
    errs = []
    ef, hids = eframes_of_line(ch, L)
    if len(ef) < 2:
        return errs, ef, hids
    for f in ef:
        if f not in _EFS:
            errs.append(f"eframe not enumerated {f}")
    for f, g in zip(ef, ef[1:]):
        if not LA.edge_ok(f, g) or f.aout != g.ain:
            errs.append(f"edge {f} -> {g}")
    if not LA.ends_compatible(ef[0], ef[-1]):
        errs.append("ends")
    for (prev, cur, nxt), hid in zip(LA.line_windows(ef), hids):
        if cur.kind == "T":
            sig, g = hid
            if not tau_compatible(cur, sig):
                errs.append(f"sig vs apex flags at {cur} {hid}")
            elif hid not in LA._domain(prev, cur, nxt):
                errs.append(f"hidden outside domain {cur} {hid}")
    return errs, ef, hids


def cmd_windows(args):
    """collect the windows (prev, cur, next) of real lines (enriched frames) and check the enriched model on them"""
    import argparse
    import pickle
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=10 ** 9)
    ap.add_argument("--mod", type=int, default=1)
    ap.add_argument("--part", type=int, default=0)
    o = ap.parse_args(args)
    LA._imports()
    wins = collections.Counter()
    nar = nl = bad = 0
    for g, ch in LA.iter_arrangements(o.inputs, True, o.limit, mod=o.mod, part=o.part):
        nar += 1
        for L in range(ch.a.n):
            errs, ef, hids = check_eline(ch, L)
            nl += 1
            if errs:
                bad += 1
                if bad <= 10:
                    print("ERROR", ch.a.n, L, g[:60], errs[:3], flush=True)
                continue
            if len(ef) < 2:
                continue
            for w in LA.line_windows(ef):
                wins[w] += 1
    print(f"arrangements {nar}, lines {nl}, failing {bad}, distinct windows {len(wins)}")
    pickle.dump(dict(wins), open(o.out, "wb"))


# ---------------------------------------------------------------------------------------------------- LP driver
def lp_loop(G, wmax=3.0, max_it=400, verbose=True, w0=None, extra_cuts=None, umax=None):
    from scipy.optimize import linprog
    K = G.K
    cuts = list(extra_cuts or [])
    w = np.zeros(K) if w0 is None else np.array(w0, dtype=float)
    history = []
    for it in range(max_it):
        t0 = time.time()
        if umax:
            v, kind, cnt, _u = G.solve_bounded(w, umax)
        else:
            v, kind, cnt = G.solve(w)
        if v is None:
            print("no path at all?")
            return w, cuts, history
        history.append((it, v, kind))
        if verbose:
            print(f"it {it:3d} DP min (2*final+2) = {v:9.4f} ({kind}), len {len(cnt[2]) if cnt else 0}, cuts {len(cuts)}, "
                  f"|w|_1 = {w.sum():.3f}, {time.time() - t0:.1f}s", flush=True)
        if v >= TARGET - 1e-9:
            return w, cuts, history
        cuts.append(cnt + (kind,))
        # LP: min sum w  s.t.  v2 + 2 * c . w >= 2 (paths) or >= 0 (cycles: a path may repeat the cycle arbitrarily often)
        A = np.zeros((len(cuts), K))
        b = np.zeros(len(cuts))
        for i, cut in enumerate(cuts):
            v2, d, kd = cut[0], cut[1], cut[3] if len(cut) > 3 else "path"
            for c, x in d.items():
                A[i, c] = -2.0 * x
            b[i] = v2 - (TARGET if kd == "path" else 0.0)
        res = linprog(np.ones(K), A_ub=A, b_ub=b, bounds=[(0, wmax)] * K, method="highs")
        if res.status != 0:
            print("LP infeasible after", len(cuts), "cuts")
            return None, cuts, history
        w = res.x
    return w, cuts, history


def min_by_units(G, wint, D, umax):
    """independent layered DP: min over paths with exactly u units (u <= umax) of D*v2 + 2 w.counts, for every u"""
    wmin, val = G.window_min(wint, D)
    ewt = wmin[G.ew]
    N = G.N
    INF = 1e18
    ku = np.array([2 if G.nodes[i][1].kind == "T" else 1 for i in range(N)])
    F = np.full((umax + 1, N), INF)
    F[0][G.starts] = 0.0
    for c in range(umax + 1):
        for c0 in (1, 2):
            if c + c0 > umax:
                continue
            m = (ku[G.src] == c0) & (F[c][G.src] < INF)
            np.minimum.at(F[c + c0], G.dst[m], F[c][G.src[m]] + ewt[m])
    res = {}
    for u_, wi in zip(G.tn, G.tw):
        uu = int(ku[u_])
        for c in range(0, umax + 1 - uu):
            v = F[c][u_] + wmin[wi]
            if F[c][u_] < INF and v < res.get(c + uu, INF):
                res[c + uu] = float(v)
    return res


def rationalize(G, w, dens=(1, 2, 3, 4, 6, 8, 12, 24, 36, 48, 60, 120), umax=None):
    """smallest common denominator D such that round(D w) is an exact certificate: DP min of  D*v2 + 2 sum wint cnt  >= 2 D
    on all paths and cycles (integer arithmetic in float64, exact below 2^53)"""
    for D in dens:
        wint = np.rint(w * D)
        if umax:
            v, kind, cnt, _u = G.solve_bounded(wint, umax, scale=D)
        else:
            v, kind, cnt = G.solve(wint, scale=D)
        if v is not None and v >= 2 * D - 1e-9:
            return D, wint, v
    return None, None, None


def export_rules(G, wint, D, path):
    """machine-readable rule table: one row per weighted rule, weight = wint/D (exact fraction)"""
    import json
    rows = []
    for i in np.nonzero(wint)[0]:
        pay, rec, cell = G.cat.keys[i]
        ring5, u, pL, pR, tL, tR, oth = cell
        rows.append(dict(payer=pay, receiver=rec, ring5="".join(ring5), u=u, pL=pL, pR=pR, tL=tL, tR=tR, oth=list(oth),
                         weight=str(F(int(wint[i]), D))))
    json.dump(dict(description="rule (payer role, receiver role, block signature cell) with weight; roles A axis, C cap, "
                               "L/R flank lines, M = both flank lines when the signature is mirror symmetric; see search/rule_ref.py",
                   denominator=D, rules=rows), open(path, "w"), indent=1)
    return rows


def verify_cert(G, wint, D, maxlen=90):
    """independent re-verification of a certificate (integer weights wint / denominator D):
    (1) Bellman-Ford minimum over all paths >= 2D and no negative cycle (G.solve, exact integer arithmetic in float64)
    (2) layered DP by exact path length up to maxlen (no parent pointers, no early stop)
    (3) negative-cycle check inside every strongly connected component with scipy's Bellman-Ford"""
    out = {}
    v, kind, _ = G.solve(wint, scale=D)
    out["bf_min"] = v
    out["bf_ok"] = v is not None and v >= 2 * D - 1e-9
    wmin, val = G.window_min(wint, D)
    ewt = wmin[G.ew]
    N = G.N
    INF = 1e18
    dist = np.full(N, INF)
    dist[G.starts] = 0.0
    best = INF
    minlen = None
    for length in range(1, maxlen + 1):
        cand = dist[G.src] + ewt
        nd = np.full(N, INF)
        np.minimum.at(nd, G.dst, cand)
        dist = np.minimum(nd, INF)
        tot = np.where(dist[G.tn] < INF, dist[G.tn] + wmin[G.tw], INF)
        m = tot.min()
        if m < best:
            best, minlen = m, length + 1
    out["layered_min"] = float(best)
    out["layered_ok"] = best >= 2 * D - 1e-9
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import connected_components, bellman_ford
    A = csr_matrix((np.ones(len(G.src)), (G.src, G.dst)), shape=(N, N))
    nc, lab = connected_components(A, directed=True, connection="strong")
    sizes = np.bincount(lab)
    ok = True
    ncyc = 0
    for comp in np.nonzero(sizes > 1)[0]:
        nodes = np.nonzero(lab == comp)[0]
        loc = {int(x): i for i, x in enumerate(nodes)}
        m = np.isin(G.src, nodes) & np.isin(G.dst, nodes)
        if not m.any():
            continue
        ncyc += 1
        ii = np.array([loc[int(x)] for x in G.src[m]])
        jj = np.array([loc[int(x)] for x in G.dst[m]])
        ww = ewt[m]
        # min weight parallel edges; scipy needs positive-or-zero tricks: use dense/sparse with explicit min
        d = {}
        for a_, b_, w_ in zip(ii, jj, ww):
            if (a_, b_) not in d or w_ < d[(a_, b_)]:
                d[(a_, b_)] = w_
        ks = list(d)
        # shift to make explicit zeros representable: scipy treats stored zeros as edges in csr, fine
        M = csr_matrix(([d[k] for k in ks], ([k[0] for k in ks], [k[1] for k in ks])), shape=(len(nodes), len(nodes)))
        try:
            bellman_ford(M, directed=True, indices=0)
        except Exception as e:                       # NegativeCycleError
            if "negative" in str(e).lower():
                ok = False
    out["scc_with_cycles"] = ncyc
    out["scc_ok"] = ok
    return out


def tight_analysis(G, wint, D, units=17):
    """windows lying on some path with final value exactly 0 and exactly `units` = #simple + 2 #triple vertex units (n - 1 = units).
    Layered DP over the consumed units, forward and backward (exact integer arithmetic).  Returns (set of tight window ids,
    number of tight edges)."""
    wmin, val = G.window_min(wint, D)
    ewt = wmin[G.ew]
    N = G.N
    INF = 1e18
    kind_units = np.array([2 if G.nodes[i][1].kind == "T" else 1 for i in range(N)])
    unit_e = kind_units[G.src]
    target = 2.0 * D
    F = np.full((units + 1, N), INF)
    F[0][G.starts] = 0.0
    for c in range(units + 1):
        ok = F[c][G.src] < INF
        cand_c = c + unit_e
        for c2 in np.unique(cand_c[ok]):
            if c2 > units:
                continue
            m = ok & (cand_c == c2)
            np.minimum.at(F[c2], G.dst[m], F[c][G.src[m]] + ewt[m])
    B = np.full((units + 1, N), INF)
    tn_units = kind_units[G.tn]
    for u, w_, un in zip(G.tn, wmin[G.tw], tn_units):
        if un <= units:
            B[un][u] = min(B[un][u], w_)
    for c in range(units + 1):
        # B[c][u] = ewt + B[c - units(u)][v]
        for c0 in (1, 2):
            m = (unit_e == c0) & (c - c0 >= 0)
            if not m.any():
                continue
            cand = B[c - c0][G.dst[m]] + ewt[m]
            np.minimum.at(B[c], G.src[m], cand)
    tight = set()
    nt = 0
    for c in range(units + 1):
        for c0 in (1, 2):
            c1 = units - c - c0
            if c1 < 0:
                continue
            m = (unit_e == c0)
            tot = F[c][G.src] + ewt + B[c1][G.dst]
            hit = m & (np.abs(tot - target) < 1e-6)
            nt += int(hit.sum())
            tight.update(int(x) for x in G.ew[hit])
    # terminal windows
    for u, wi, un in zip(G.tn, G.tw, tn_units):
        c = units - un
        if c >= 0 and abs(F[c][u] + wmin[wi] - target) < 1e-6:
            tight.add(int(wi))
            nt += 1
    return tight, nt


def describe(G, cnt, only_rules=True):
    v2, d, wins = cnt[:3]
    lines = [f"  total v2 = {v2} (= 2*value of the base), rule counts:"]
    for c, x in sorted(d.items(), key=lambda t: t[0]):
        lines.append(f"    {x:+d} x {G.cat.keys[c]}")
    return "\n".join(lines)


def show_path(G, cnt):
    v2, d, wins = cnt[:3]
    out = []
    for wi in wins:
        prev, cur, nxt = G.win_list[wi]
        out.append(LA.show([cur]))
    return " | ".join(out)


def main():
    import argparse
    if len(sys.argv) > 1 and sys.argv[1] == "windows":
        return cmd_windows(sys.argv[2:])
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--families", default="AC,AM,MM,CM")
    ap.add_argument("--wmax", type=float, default=3.0)
    ap.add_argument("--iters", type=int, default=400)
    ap.add_argument("--enriched", action="store_true", help="apex-multiplicity flags shared between adjacent windows")
    ap.add_argument("--windows", default=None, help="comma-separated pickles of windows seen in data: empirical automaton")
    ap.add_argument("--rfree", action="store_true", help="restricted class: no bridge rays")
    ap.add_argument("--f4p", action="store_true", help="extra fact F4': no two adjacent simple vertices cap the same side")
    ap.add_argument("--export", default=None, help="json rule table of the certificate")
    ap.add_argument("--save", default=None, help="pickle of the rule weights (key -> weight)")
    ap.add_argument("--dump", default=None, help="write the infeasibility cuts (with full windows) as json")
    ap.add_argument("--rings", default=None, help="comma separated canonical ring types allowed at triple points (e.g. NNNNNN,BNNNNN)")
    ap.add_argument("--k1", action="store_true", help="extra proven fact K1* (restriction of the hidden domain at triple frames)")
    ap.add_argument("--umax", type=int, default=None, help="only lines with n - 1 <= UMAX (bounded n, no cycles)")
    ap.add_argument("--k2", action="store_true", help="extra proven fact K2 (kite: opposite outer triangles of a 4-triangle vertex)")
    ap.add_argument("--k3", action="store_true", help="extra proven fact K3 (run form of K1*; adds 2 trits of state to the nodes)")
    ap.add_argument("--k2g", action="store_true", help="extra proven fact K2g (forces g = 1: the block is served)")
    ap.add_argument("--noRR", action="store_true", help="exclude blocks with two bridge flanks (restricted class)")
    o = ap.parse_args()
    if o.families == "SIG":
        cat = SigCatalogue(enriched=o.enriched, rfree=o.rfree, norr=o.noRR, rings=None if o.rings is None else o.rings.split(","), k1=o.k1, k2=o.k2, k2g=o.k2g)
    else:
        cat = Catalogue(o.families.split(","), enriched=o.enriched, rfree=o.rfree, norr=o.noRR, k1=o.k1, k2=o.k2, k2g=o.k2g)
    ea = lambda c, n: True
    if o.f4p:
        ea0 = ea

        def ea(c, n, ea0=ea0):
            # F4': two consecutive simple vertices cannot both cap a block on the same side (the apex of the triangle over
            # the segment would carry two adjacent block rays)
            if c.kind == "S" and n.kind == "S":
                for s_ in (0, 1):
                    if c.bin[s_] and c.bout[s_] and n.bout[s_]:
                        return False
            return ea0(c, n)
    allowed = None
    if o.windows:
        import pickle
        allowed = set()
        for f in o.windows.split(","):
            allowed |= set(pickle.load(open(f, "rb")).keys())
        print("empirical windows:", len(allowed))
    G = WGraph(cat, edge_allow=ea, allowed=allowed, k3=o.k3)
    if o.cmd == "base":
        v, kind, cnt = G.solve(np.zeros(G.K))
        print("w=0:", v, kind)
        print(describe(G, cnt))
        print(show_path(G, cnt))
    elif o.cmd == "lp":
        w, cuts, hist = lp_loop(G, o.wmax, o.iters, umax=o.umax)
        if w is None:
            import json
            dump = []
            for i, c in enumerate(cuts):
                print(f"--- cut {i} ({c[3] if len(c) > 3 else 'path'}):", show_path(G, c))
                print(describe(G, c))
                dump.append(dict(kind=c[3] if len(c) > 3 else "path", v2=c[0], counts={repr(G.cat.keys[k]): x for k, x in c[1].items()},
                                 windows=[[repr(t) for t in G.win_list[wi]] for wi in c[2]]))
            if o.dump:
                json.dump(dump, open(o.dump, "w"), indent=1)
        if w is not None:
            D, wint, v = rationalize(G, w, umax=o.umax)
            print("exact certificate:", "denominator", D, "DP min (D*(2*final+2)) =", v, "target", None if D is None else 2 * D)
            if D is not None:
                w = wint / D
            for i in np.argsort(-w):
                if w[i] > 1e-9:
                    print(F(int(round(w[i] * (D or 1))), D or 1), G.cat.keys[i])
            if D is not None and o.umax:
                mb = min_by_units(G, wint, D, o.umax)
                print("verify (bounded): min D*(2*final+2) per n-1:", {u: mb[u] for u in sorted(mb)}, "target", 2 * D)
            elif D is not None:
                print("verify:", verify_cert(G, wint, D))
                if o.export:
                    export_rules(G, wint, D, o.export)
            if o.save:
                import pickle
                pickle.dump({G.cat.keys[i]: float(w[i]) for i in range(len(w)) if w[i] > 1e-9}, open(o.save, "wb"))


if __name__ == "__main__":
    main()

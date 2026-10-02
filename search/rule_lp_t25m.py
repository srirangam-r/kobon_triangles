"""T25: multiplicity >= 4 extension of the exact-weight rule LP (search/rule_lp_t25.py stays untouched).

Adds to the exact-17 automaton the T22 frames of m-fold points (search/line_automaton_m.py):
  * frames M4 / M5 = an m-fold vertex seen from L, m = 4 (3 crossings) and m = 5 (4 crossings); a multiplicity m >= 6 is covered by the class of
    the same parity plus an even number of dummy units (a sound relaxation: the class has the smaller bonus 6(m-3)); the DP handles the dummy
    units as zero-weight 2-unit self loops at M nodes.
  * "triple" in T1 / F / T1'' / sig / flanker flags means MULTIPLE (>= 3), exactly as in search/bbl_hallm.py.
  * apex classes 1 = triple, 2 = simple, 3 = multiplicity >= 4 (enriched S / T frames).  Facts that were proved for exactly triple vertices (K2, K2g,
    K3, the patterns of search/automaton_facts.py) never fire on M vertices / M neighbours / class-3 apexes.
  * no block rules (cap_terms / triple_terms cells) for blocks whose apex is an M point; no PT cells at M points; TRI cells skip every triangle that has
    a vertex of multiplicity >= 4.

    uv run --no-project --with numpy --with scipy --with networkx --with python-sat python search/rule_lp_t25m.py lp --class full --split --alpha \
        --celldom --wr --sv --tri --pt --eps 0 --cleandelta 1/24 ...     (same flags as rule_lp_t25.py, plus --mult, on by default here)
"""
import collections
import itertools
import sys
import time
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
import inspect  # noqa: F401,E402
sys.path.append(str(ROOT / "work/t3"))
import numpy as np  # noqa: E402
import line_automaton as LA  # noqa: E402
import line_automaton_m as LM  # noqa: E402
import rule_lp as RL  # noqa: E402
import rule_lp_t25 as T  # noqa: E402
from line_automaton import NONE, BITS  # noqa: E402

UNITS = {"S": 1, "T": 2, "M4": 3, "M5": 4}
MCLASS = {"M4": 4, "M5": 5}


UNITS_SPLIT = {"S": 1, "T": 2, "MJ": 1, "M": 2, "MP": 3}     # --splitm: junction node (1 unit) + M (2) / MP (3)


def units(f):
    return UNITS_SPLIT[f.kind] if SPLITM[0] else UNITS[f.kind]


def is_m(f):
    return f.kind in MCLASS


def info_is_m(info):
    return info is not None and len(info) == 5


def norm_info(info):
    """neighbour info with M neighbours declared kind 'M' (neither S nor T): for the facts proved for exactly triple vertices"""
    if info is None or len(info) == 4:
        return info
    return ("M",) + tuple(info[1:4])


# ---------------------------------------------------------------------------------------------------- frames
class MF(RL.EFrame):
    """m-fold vertex (kind 'M4' / 'M5'): h = (hE+, hE-, hW+, hW-); no apex flags, no ub flags.  Neighbours see it as a triple vertex (T22) plus a
    5th element that marks it as multiple-of-4+."""
    __slots__ = ()

    def info_prev(self, first=False):
        return ("T", (self.h[0], self.h[1]), self.bin, first, self.kind)

    def info_next(self, last=False):
        return ("T", (self.h[2], self.h[3]), self.bout, last, self.kind)


BADONLY = [True]     # perturbation lemma (THEORY section 24): a max-vertex counterexample has only triple points and BAD 4-fold points (sector words 11101110, 11111110,
                     # 11111111 up to the dihedral group); no M5+ frames.  --allm switches this reduction off.
SPLITM = [False]     # --splitm: M vertices come as exactly 4-fold ("M", 3 units, bonus 6, PT4 cells) and >= 5-fold ("MP", 4 units, bonus 12, dummy units), hW in the node
GIFT = [0]          # experiment: every cap of a block whose apex is a >= 4-fold point receives GIFT[0] (final units) for free
APEX_CLASSES = [(1, 2, 3)]      # --noapex3 sets (1, 2): the enriched frames of rule_lp_t25.py (a triangle apex is never a >= 4-fold point)


def _taus3(bits):
    for a0 in ((0,) if bits[0] == 0 else APEX_CLASSES[0]):
        for a1 in ((0,) if bits[1] == 0 else APEX_CLASSES[0]):
            yield (a0, a1)


def all_eframes_m():
    """enriched S / T frames with apex classes {1 triple, 2 simple, 3 multiple>=4}, plus the M frames"""
    out = []
    import os as _os_t
    triopt = bool(_os_t.environ.get("TRIOPT"))
    for f in LA.all_frames():
        # TRIOPT (lead, sol's ALL8_NOTE2 section 10): in a (T, V)-maximal 94 both alternating sector sums of a triple are >= 2.
        # Cyclic sectors of a T frame: TL = bin[0], TM = h[0], TR = bout[0], BR = bout[1], BM = h[1], BL = bin[1].
        if triopt and f.kind == "T" and (f.bin[0] + f.bout[0] + f.h[1] < 2 or f.h[0] + f.bin[1] + f.bout[1] < 2):
            continue
        for ain in _taus3(f.bin):
            for aout in _taus3(f.bout):
                if f.kind == "S":
                    # a simple vertex capping a block (triangles on both segments on the same side) sees the same apex P twice: multiple
                    if any(f.bin[s] and f.bout[s] and not (ain[s] == aout[s] and ain[s] in (1, 3)) for s in (0, 1)):
                        continue
                out.append(RL.EFrame(f.kind, f.bin, f.bout, f.ub, f.h, ain, aout))
    for kind in ("M4", "M5"):
        for bi, bo, a, c in itertools.product(BITS, BITS, BITS, BITS):
            out.append(MF(kind, bi, bo, NONE, a + c, (0, 0), (0, 0)))
    return out


def tau_compatible_m(cur, sig):
    """the hidden far ends of a triple frame agree with its apex flags: apex triple (1) or >=4 (3) <=> far end multiple"""
    for k, a in enumerate((cur.aout[0], cur.aout[1], cur.ain[0], cur.ain[1])):
        if a and sig[k] != (1 if a in (1, 3) else 0):
            return False
    return True


# ---------------------------------------------------------------------------------------------------- facts for exactly-triple vertices only
_k2 = RL.k2_violation
_k2g = RL.k2g_force
_k3 = RL.k3_step


def k2_violation_m(prev, cur, nxt):
    return _k2(norm_info(prev), cur, norm_info(nxt))


def k2g_force_m(prev, cur, nxt, sig):
    return _k2g(norm_info(prev), cur, norm_info(nxt), sig)


def k3_step_m(state, prev, cur, ni):
    """K3 guarded for multiplicity >= 4 (work/eng/T27/facts_scan.py: the unguarded version is contradicted by real lines with a >= 4-fold apex).
    The 'previous / next vertex is simple with a triangle' disjuncts of lf / rf need the far end Z / Y of the h-triangle to be EXACTLY triple
    (apex class 1); Z / Y simple (class 2) is fine; a >= 4-fold apex (class 3) gives no forcing.  The link between run vertices needs a triple
    apex (aout == 1) and an exactly triple next vertex (norm_info turns M neighbours into kind 'M')."""
    if cur.kind != "T":
        return (0, 0)
    prev, ni = norm_info(prev), norm_info(ni)
    out = [0, 0]
    for s_ in (0, 1):
        if not cur.h[s_]:
            continue
        st = state[s_]
        lf = bool(cur.bin[s_] and (cur.ain[s_] == 2 or (cur.ain[s_] == 1 and prev is not None and prev[0] == "S" and prev[2][s_])))
        rf = bool(cur.bout[s_] and (cur.aout[s_] == 2 or (cur.aout[s_] == 1 and ni is not None and ni[0] == "S" and ni[2][s_])))
        if (lf and rf) or (st == 1 and rf) or (st == 2 and lf):
            return None
        new = 1 if (st == 1 or lf) else 2 if (st == 2 or rf) else 0
        link = bool(ni is not None and ni[0] == "T" and cur.bout[s_] and cur.aout[s_] == 1 and ni[1][s_])
        out[s_] = new if link else 0
    return tuple(out)


HIDSTATE = [False]   # --hidstate (T29): hidden state along the line.  Level 1 (F4 link): the face F4 beyond the simple apex X of a triangle on a segment of L, seen by the flank blocks of BOTH end vertices of that segment, is one face:
                     # its status (triangle or not = the hidden bit pO of the two flank cells) is carried on the edge between two consecutive triple frames and must agree in both windows.
HS0 = (None, None)   # no link tags


def hs_active(cur, nxt):
    """sides s of the segment cur -> nxt where an F4 link is active: both end vertices are exactly triple, the triangle on side s of the segment has a SIMPLE apex X, and both
    end vertices see the ray towards X as doubly used (hidden sector h[s] of both is a triangle): so both have a B ray towards X and both flank cells see the face F4 beyond X"""
    if cur.kind != "T" or nxt.kind != "T":
        return (False, False)
    return tuple(bool(cur.bout[s_] and cur.h[s_] and cur.aout[s_] == 2 and nxt.h[s_] and nxt.bin[s_] and nxt.ain[s_] == 2) for s_ in (0, 1))


UUB = [False]        # --uub (T29): the U-UB lemma (proved, work/eng/T29): if the axis A of a flank block at a T vertex P ends at its simple far end X (completion u = 1, A has no vertex beyond X)
                     # then every line W with no vertex on the side 1-s of L (ub flag on side 1-s) passes through X, i.e. is the cap C, i.e. sits at P itself or at the neighbour Y1 of P on the side of
                     # the triangle P-Y1-X.  The flank completion u is a window label ("u", dir, side) -> token "1" / "0"; the line automaton tracks the ub flags seen so far.


def u_lam_variants(prev, cur, nxt_info):
    """window variants of the u = 1 completions that are possible in this window (T frame, flank ray towards a simple apex whose neighbour Y1 is not a triple/multiple point with the hidden
    sector triangle, i.e. pM = 0): tuples of (("u", dir, side), token) with token "1" (block with u = 1) / "0" (no block or u = 0)"""
    if not UUB[0] or cur.kind != "T":
        return [()]
    cand = []
    for s_ in (0, 1):
        if nxt_info is not None and cur.bout[s_] and cur.h[s_] and cur.aout[s_] == 2:
            if nxt_info[0] == "MENTRY":
                pm = nxt_info[3][s_]
            else:
                pm = 0 if nxt_info[0] == "S" else nxt_info[1][s_]
            if pm == 0:
                cand.append(("u", "out", s_))
        if prev is not None and cur.bin[s_] and cur.h[s_] and cur.ain[s_] == 2:
            pm = 0 if prev[0] == "S" else prev[1][s_]
            if pm == 0:
                cand.append(("u", "in", s_))
    if not cand:
        return [()]
    return [tuple(zip(cand, toks)) for toks in itertools.product("01", repeat=len(cand))]


def merge_lam(a, b):
    return tuple(sorted(a + b)) if (a and b) else (a or b)


def make_uub_step(inner):
    """wrap the combined line-automaton step: extra state element (ubOld, ubPrev, pend, forb) = bit masks over the 2 sides (see UUB)"""
    def step(state, prev, cur, ni):
        if state == (0, 0):
            base, ex = (0, 0), (0, 0, 0, 0)
        else:
            base, ex = state[:7], (state[7] if len(state) > 7 else (0, 0, 0, 0))
        new = inner(base, prev, cur, ni)
        if new is None:
            return None
        ubOld, ubPrev, pend, forb = ex
        ubm = (cur.ub[0] | (cur.ub[1] << 1)) if cur.kind in ("S", "T") else 0
        toks = [(k_[1], k_[2]) for k_, t_ in LAMSTATE[0] if k_[0] == "u" and t_ == "1"]
        if ubm & forb:
            return None
        for (d_, s_) in toks:
            bm = 1 << (1 - s_)
            if ubOld & bm:
                return None
            if d_ == "out" and (ubPrev & bm):
                return None
        forb2, pend2 = forb | pend, 0
        for (d_, s_) in toks:
            bm = 1 << (1 - s_)
            if d_ == "out":
                pend2 |= bm
            else:
                forb2 |= bm
        return tuple(new) + ((ubOld | ubPrev, ubm, pend2, forb2),)
    return step


HIDM = [False]       # --hidm: the F4 link also across T - M adjacencies (exactly 4-fold M): tag pO = 1 forces f2[s] = 1 of the M vertex (L1 on the segment X - Y_r', see hs_edge_choices)


def hs_edge_choices(cur, nxt):
    """edge labels (tags of the sides of the segment cur -> nxt) of a S / T successor edge.
    T -> T: F4 link (hs_active), both tags free.
    M -> T (--hidm): T's flank cell towards the simple apex X of the triangle on side s of the segment, the M sector across the M ray towards X (hE[s]) is a triangle (F3):
        pO = 1 (F4 a triangle) makes the segment X - Y_r' (Y_r' = far end of the M ray s*2) doubly used with the simple end X, hence f2[s] = 1.  So tag 1 needs cur.ain[s] == 1."""
    if cur.kind == "T":
        act = hs_active(cur, nxt)
        return hs_choices(act)
    if HIDM[0] and cur.kind == "M" and nxt.kind == "T":
        opts = []
        for s_ in (0, 1):
            if nxt.bin[s_] and nxt.h[s_] and nxt.ain[s_] == 2 and cur.h[s_]:
                opts.append((0, 1) if cur.ain[s_] == 1 else (0,))
            else:
                opts.append((None,))
        return [(a, b) for a in opts[0] for b in opts[1]]
    return [HS0]


def hs_m_entry_choices(cur, hW):
    """T -> M (junction) edge labels (--hidm): sides s where T's ray towards the simple apex X of the triangle on side s of the segment is doubly used and the M sector hW[s] (F3) is a triangle"""
    if not (HIDM[0] and cur.kind == "T"):
        return [HS0]
    opts = [(0, 1) if (cur.bout[s_] and cur.h[s_] and cur.aout[s_] == 2 and hW[s_]) else (None,) for s_ in (0, 1)]
    return [(a, b) for a in opts[0] for b in opts[1]]


def wrapw(wkey, hin, hout, lab=()):
    """window key with link tags / labels (only when something is set, so that tag-free windows are shared with the plain model)"""
    if hin == HS0 and hout == HS0 and not lab:
        return wkey
    return ("HS", wkey, hin, hout) + ((lab,) if lab else ())


def hs_choices(act):
    """edge labels: tuple (None | pO bit) per side for the active sides"""
    opts = [(None,) if not a else (0, 1) for a in act]
    return [(a, b) for a in opts[0] for b in opts[1]]


GUARD = [False]      # --guarded: K1*, K2, K2g, celldom and the T23 patterns P000-P009 fire only where every apex / vertex they mention is exactly triple or simple


def _side_ok(cur, s_):
    """no >= 4-fold apex (class 3) on a triangle of side s at cur"""
    return not ((cur.bin[s_] and cur.ain[s_] == 3) or (cur.bout[s_] and cur.aout[s_] == 3))


def k1_violation_g(prev, cur, nxt, sig):
    """K1* guarded: only the sides s whose bin / bout triangles have an apex of class 1 or 2"""
    prev, nxt = norm_info(prev), norm_info(nxt)
    for s_ in (0, 1):
        if not cur.h[s_] or not _side_ok(cur, s_):
            continue
        rf = cur.bout[s_] and (sig[s_] == 0 or (nxt is not None and nxt[0] == "S" and nxt[2][s_] == 1))
        lf = cur.bin[s_] and (sig[2 + s_] == 0 or (prev is not None and prev[0] == "S" and prev[2][s_] == 1))
        if rf and lf:
            return True
    return False


def k2_violation_g(prev, cur, nxt):
    """K2 guarded: the kite needs apexes of class 1 or 2 on all four triangles of the 4-triangle simple frame"""
    if any(a == 3 for a in tuple(cur.ain) + tuple(cur.aout)):
        return False
    return _k2(norm_info(prev), cur, norm_info(nxt))


def k2g_force_g(prev, cur, nxt, sig):
    """K2g guarded per side"""
    prev, nxt = norm_info(prev), norm_info(nxt)
    g = [0, 0, 0, 0]
    zero = set()
    for s_ in (0, 1):
        if not (cur.bin[s_] and cur.bout[s_] and cur.h[s_]) or not _side_ok(cur, s_):
            continue
        if sig[s_] == 0 and sig[2 + s_] == 1 and nxt is not None and nxt[0] == "T" and nxt[1][s_] and nxt[2][s_]:
            g[2 + s_] = 1
            zero.add(1 if s_ == 0 else 5)
        if sig[2 + s_] == 0 and sig[s_] == 1 and prev is not None and prev[0] == "T" and prev[1][s_] and prev[2][s_]:
            g[s_] = 1
            zero.add(2 if s_ == 0 else 4)
    return tuple(g), zero


def install_mult():
    """patch rule_lp so that the facts see M neighbours as neither S nor T, and tau_compatible knows apex class 3"""
    RL.k2_violation = k2_violation_g if GUARD[0] else k2_violation_m
    RL.k2g_force = k2g_force_g if GUARD[0] else k2g_force_m
    if GUARD[0]:
        RL.k1_violation = k1_violation_g
    T._K3_ORIG = k3_step_m
    RL.tau_compatible = tau_compatible_m


# ---------------------------------------------------------------------------------------------------- TRI events with vertex classes
def vclass_kind(kind):
    return "S" if kind == "S" else "T" if kind == "T" else "M"


_APEX_LETTER = {1: "T", 2: "S", 3: "M"}


def _tri_emit(out, cl_a, cl_b, ap):
    """one triangle: vertex classes S / T / M of the two endpoints of the visible segment and of its apex; the visible line has the role of the apex"""
    if ap == 0:
        return
    m = [cl_a, cl_b, _APEX_LETTER[ap]]
    if m.count("M") >= 2:
        return                       # the line through two M vertices does not see the apex: no transfer at all in such a triangle
    cell = "".join(sorted(m))
    if len(set(m)) == 1:
        return
    r = m[2]
    for o in "STM":
        n_o = m.count(o)
        if o == r or not n_o:
            continue
        out[("TRI", cell, r + ">" + o)] -= n_o
        out[("TRI", cell, o + ">" + r)] += n_o


def tri_events_m(prev, cur, nxt):
    """TRI transfers with 3 vertex classes {S, T, M}.  The event of a segment is emitted by the S / T frame at one end: the segment after cur
    (any successor), and the segment before cur only when the predecessor is an M vertex.  Triangles with two M vertices carry no transfer."""
    out = collections.Counter()
    if is_m(cur):
        return []
    cc = "T" if cur.kind == "T" else "S"
    if nxt is not None:
        cn = "M" if info_is_m(nxt) else "T" if nxt[0] == "T" else "S"
        for s_ in (0, 1):
            if cur.bout[s_]:
                _tri_emit(out, cc, cn, cur.aout[s_])
    if prev is not None and info_is_m(prev):
        for s_ in (0, 1):
            if cur.bin[s_]:
                _tri_emit(out, "M", cc, cur.ain[s_])
    return [(k, x) for k, x in out.items() if x]


# ---------------------------------------------------------------------------------------------------- MB cells: blocks whose apex is a >= 4-fold point
MB = [False]            # --mb: transfers axis <-> cap for blocks with a >= 4-fold apex, keyed by the number of triangles beyond the cap vertex


def mb_axis_events(prev, cur, nxt):
    """the axis A of a block with an M apex P: the line through P and the simple far end X.  Emitted at the S frame X of that line when the
    neighbour across a doubly used segment (both faces triangles) is an M vertex.  key = number of triangles on the far side of X (the faces
    adjacent to the other segment of A at X, which are the faces beyond X adjacent to the cap C)."""
    out = []
    if cur.kind != "S":
        return out
    if nxt is not None and info_is_m(nxt) and cur.bout == (1, 1):
        kk = cur.bin[0] + cur.bin[1]
        out += [(("MB", kk, "A>C"), -1), (("MB", kk, "C>A"), 1)]
    if prev is not None and info_is_m(prev) and cur.bin == (1, 1):
        kk = cur.bout[0] + cur.bout[1]
        out += [(("MB", kk, "A>C"), -1), (("MB", kk, "C>A"), 1)]
    return out


def mb_cap_events(cur):
    """the cap C of a block whose apex is a >= 4-fold point (S frame, both segments have a triangle on side k with apex class 3)"""
    out = []
    if cur.kind != "S":
        return out
    for k in (0, 1):
        if cur.bin[k] and cur.bout[k] and cur.aout[k] == 3:
            o = 1 - k
            kk = cur.bin[o] + cur.bout[o]
            out += [(("MB", kk, "A>C"), 1), (("MB", kk, "C>A"), -1)]
    return out


# ---------------------------------------------------------------------------------------------------- PT4 cells: exactly 4-fold points (all 8 sectors visible)
_PT4C = {}


def _pt4_map(sec, s_, k):
    new = [0] * 8
    for j in range(8):
        new[(j + k) % 8 if s_ == 1 else (-j - 1 + k) % 8] = sec[j]
    return tuple(new)


def pt4_cell(sec):
    """8 sector bits of a 4-fold point seen from the line whose E ray is ray 0 (ray r lies on line r mod 4, sector j between rays j and j+1).
    Returns (canonical bits under the dihedral group of the 8 rays, role of this line = smallest image line index under the automorphisms of the
    canonical cell, {role: number of lines})."""
    r = _PT4C.get(sec)
    if r is None:
        cands = [(_pt4_map(sec, s_, k), s_, k) for s_ in (1, -1) for k in range(8)]
        canon = min(c[0] for c in cands)
        s0, k0 = min((s_, k) for (c, s_, k) in cands if c == canon)
        aut = [(s_, k) for s_ in (1, -1) for k in range(8) if _pt4_map(canon, s_, k) == canon]

        def orb(i):
            return min((s_ * i + k) % 4 for (s_, k) in aut)
        r = _PT4C[sec] = (canon, orb(k0 % 4), dict(collections.Counter(orb(i) for i in range(4))))
    return r


_BAD4 = []


def bad4_words():
    """canonical forms of the three bad 4-fold sector patterns"""
    if not _BAD4:
        for w in ((1, 1, 1, 0, 1, 1, 1, 0), (1, 1, 1, 1, 1, 1, 1, 0), (1, 1, 1, 1, 1, 1, 1, 1)):
            _BAD4.append(pt4_cell(w)[0])
    return _BAD4


def is_bad4(bout, hE, hW, bin_):
    """sector word of a 4-fold vertex seen from a line through it: (s+0, s+1, s+2, s+3, s-3, s-2, s-1, s-0)
    env BADWORDS (lead, case split): e.g. "67" allows only the 6- and 7-triangle bad words (case: the arrangement has no all-8 point)"""
    import os
    bw = os.environ.get("BADWORDS")
    allowed_ = bad4_words() if not bw else [bad4_words()[{"6": 0, "7": 1, "8": 2}[c]] for c in bw]
    return pt4_cell((bout[0], hE[0], hW[0], bin_[0], bin_[1], hW[1], hE[1], bout[1]))[0] in allowed_


def pt4_events(cur):
    """[(column key, count)] of the PT4 cell at an exactly 4-fold vertex (frame kind 'M'): transfers between the lines of different roles"""
    sec = (cur.bout[0], cur.h[0], cur.h[2], cur.bin[0], cur.bin[1], cur.h[3], cur.h[1], cur.bout[1])
    canon, role, row = pt4_cell(sec)
    out = []
    for other, mult in row.items():
        if other == role:
            continue
        out.append((("PT4", canon, f"{role}>{other}"), -mult))
        out.append((("PT4", canon, f"{other}>{role}"), mult))
    return out


# ---------------------------------------------------------------------------------------------------- star keys at bad 4-fold points (PT4N)
STAR = [None]        # --star LEVEL: None | 'F2' (full triple vs other) | 'F3' (F, H=one non-triangle sector, other) | 'full' (S F H O M)
_STAR_DOM = {}


def star_lvl(c):
    """class of a first vertex: S simple, F full triple (6 triangles), H triple with one non-triangle, O other triple, M >= 4-fold; coarsened by the level"""
    lv = STAR[0]
    if lv == "full":
        return c
    if lv == "F3":
        return c if c in ("F", "H") else "N"
    return "F" if c == "F" else "N"


def class_of_info(info, shared):
    """class of the neighbour described by info = (kind, h, far_bits, flag[, 'M']); `shared` = (bits of the segment between the two vertices) ; None = no neighbour (unbounded ray)"""
    if info is None:
        return star_lvl("S")
    if len(info) == 5:
        return star_lvl("M")
    if info[0] == "S":
        return star_lvl("S")
    z = 6 - (shared[0] + shared[1] + info[1][0] + info[1][1] + info[2][0] + info[2][1])
    return star_lvl("F" if z == 0 else "H" if z == 1 else "O")


def star_domain(sec, r):
    """star classes that the first vertex on ray r of a 4-fold point with sector word `sec` may have (pair lemma restricts the triple classes when PAIRLEM is on)"""
    key = (sec, r, _PAIR, STAR[0])
    d = _STAR_DOM.get(key)
    if d is None:
        out = {star_lvl("S"), star_lvl("M")}
        if not _PAIR:
            out |= {star_lvl("F"), star_lvl("H"), star_lvl("O")}
        else:
            sys.path.append(str(ROOT / "work/eng/T27"))
            import pairlemma as PL
            AL = PL.allowed_set()
            PA = tuple(sec[(r + i) % 8] for i in range(8))
            for Q in itertools.product((0, 1), repeat=6):
                if Q[5] != PA[0] or Q[0] != PA[7]:
                    continue
                x = ("".join(map(str, PA)), "".join(map(str, Q)))
                y = ("".join(map(str, PA[::-1])), "".join(map(str, Q[::-1])))
                if min(x, y) in AL:
                    z = Q.count(0)
                    out.add(star_lvl("F" if z == 0 else "H" if z == 1 else "O"))
        d = _STAR_DOM[key] = tuple(sorted(out))
    return d


_STAR_KEY = {}


def star_key(sec, cvec):
    """canonical (word, classes) star key of a bad 4-fold point seen from the line whose rays are 0 (E) and 4 (W) in the ring numbering of `sec`; returns (key, role, {role: lines})"""
    ck = (sec, cvec)
    r = _STAR_KEY.get(ck)
    if r is not None:
        return r
    canon = pt4_cell(sec)[0]
    best = None
    for s_ in (1, -1):
        for k in range(8):
            if _pt4_map(sec, s_, k) != canon:
                continue
            new = [None] * 8
            for j in range(8):
                new[(j + k) % 8 if s_ == 1 else (-j + k) % 8] = cvec[j]
            t = tuple(new)
            if best is None or t < best[0]:
                best = (t, (s_, k))
    cv, (s0, k0) = best
    aut = [(s_, k) for s_ in (1, -1) for k in range(8) if _pt4_map(canon, s_, k) == canon]

    def mapc(c, s_, k):
        new = [None] * 8
        for j in range(8):
            new[(j + k) % 8 if s_ == 1 else (-j + k) % 8] = c[j]
        return tuple(new)
    stab = [(s_, k) for (s_, k) in aut if mapc(cv, s_, k) == cv]

    def orb(i):
        return min((s_ * i + k) % 4 for (s_, k) in stab)
    role = orb(k0 % 4)
    row = dict(collections.Counter(orb(i) for i in range(4)))
    r = _STAR_KEY[ck] = ((canon, cv), role, row)
    return r


def star_events_of(key, role, row):
    out = []
    for other, mult in row.items():
        if other == role:
            continue
        out.append((("PT4N", key, f"{role}>{other}"), -mult))
        out.append((("PT4N", key, f"{other}>{role}"), mult))
    return out


def star_options(prev, cur):
    """min-term of the self window of a bad 4-fold vertex: one option (event vector) per completion of the hidden star classes; ray 4 (W) is exact (prev), the other seven rays are hidden"""
    sec = (cur.bout[0], cur.h[0], cur.h[2], cur.bin[0], cur.bin[1], cur.h[3], cur.h[1], cur.bout[1])
    cw = class_of_info(prev, cur.bin) if prev is not None else star_lvl("S")
    doms = [star_domain(sec, r) if r != 4 else (cw,) for r in range(8)]
    opts = set()
    for cvec in itertools.product(*doms):
        key, role, row = star_key(sec, cvec)
        opts.add(tuple(sorted(star_events_of(key, role, row))))
    return tuple(sorted(opts))


# ---------------------------------------------------------------------------------------------------- catalogue
class FCatalogueM(T.FCatalogue):
    """T25 catalogue + M windows.  Block rules only at exactly-triple apexes (cap side: apex class 1)."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.stats_m = collections.Counter()

    # ---- M windows: T22 side model, min over the hidden assignments; no rule terms
    def m_options(self, prev, cur, nxt):
        mc = MCLASS[cur.kind]
        res = set()
        for hidE in LM.side_domain(cur.bout, nxt):
            for hidW in LM.side_domain(cur.bin, prev):
                vec = LM.m_vec(prev, cur, nxt, (hidE, hidW))
                v2 = vec[LM.V2] + 6 * (mc - 3)
                res.add(self.finish(prev, cur, nxt, (v2, vec[LM.P_], 0, 0, ())))
        return res

    def window_options(self, prev, cur, nxt):
        if is_m(cur):
            return self.m_options(prev, cur, nxt)
        return super().window_options(prev, cur, nxt)

    # ---- caps: rules only when the block apex is exactly triple (apex class 1); apex class 3 = M point: no rule terms for that side
    def cap_terms(self, prev, cur, nxt):
        if prev is None or nxt is None:
            return ()
        terms = []
        for k in (0, 1):
            if not (cur.bin[k] and cur.bout[k]):
                continue
            if cur.aout[k] == 3:
                continue
            o = 1 - k
            u = int(cur.ub[o])
            pR, pL = cur.bin[o], cur.bout[o]
            tR, tL = int(prev[0] == "T"), int(nxt[0] == "T")
            fR = "R" if (prev[0] == "T" and prev[1][k]) else "N"
            fL = "R" if (nxt[0] == "T" and nxt[1][k]) else "N"
            s12, s45 = fR == "R", fL == "R"
            opts = set()
            for s23 in (0, 1):
                for s34 in (0, 1):
                    dbl = (s12 and s23, s23 and s34, s34 and s45)
                    for far in itertools.product(*[(0, 1) if d else (None,) for d in dbl]):
                        x = ["N" if d is None else ("B" if d == 0 else "R") for d in far]
                        if (x[0] == "B" and x[1] == "B") or (x[1] == "B" and x[2] == "B"):
                            continue
                        if self.rings is not None and RL.canon_ring(("B", fR) + tuple(x) + (fL,)) not in self.rings:
                            continue
                        ring5 = (fR, x[0], x[1], x[2], fL)
                        for oth in (RL.OTH_STATUSES if x[1] == "B" else (RL.NOOTH,)):
                            cell = (ring5, u, pL, pR, tL, tR, oth)
                            if not self.cell_ok(cell):
                                continue
                            opts.add(self.role_vec("C", cell))
            if not opts:
                return None
            terms.append(tuple(sorted(opts)))
        return tuple(sorted(terms))

    def finish(self, prev, cur, nxt, opt):
        v2, p, nRN, nRR, terms = opt
        if not (self.split_a or self.alpha or self.wr or self.sv or self.tri or self.pt):
            return opt
        own = int(nxt is not None and cur.bout == NONE)
        touch = sum(1 for k in (0, 1) if not cur.ub[k] and cur.bin[k] + cur.bout[k] == 0) if cur.kind == "S" else 0
        bits = (cur.bout[0] + cur.bout[1]) if nxt is not None else 0
        ex = []
        v2n = v2
        if self.split_a:
            v2n = v2 - 2 * own + touch
            ca = 3 * own - 1.5 * touch
            if ca:
                ex.append((self.col(("a",)), ca))
        if self.alpha:
            x = (-6 * bits - v2) / 2 + (3 * (self.W - 1) if prev is None else 0)
            if x:
                ex.append((self.col(("alpha",)), x))
        if self.wr and own:
            cw = int(cur.kind != "S") + int(nxt[0] != "S")
            if cw:
                ex.append((self.col(("wr",)), cw))
                _add_xrow(self, "special", ({("wr",): 1.0, ("a",): 1.5, ("alpha",): 1.0}, 1.5))      # exact validity condition of the special columns (A30, THEORY section 23): alpha' + wr + 1.5 a <= 3/2
        if self.sv and cur.kind == "S":
            for key_, x_ in T.sv_events(cur):
                ex.append((self.col(key_), x_))
        if self.tri:
            for key_, x_ in tri_events_m(prev, cur, nxt):
                ex.append((self.col(key_), x_))
        if self.pt and cur.kind == "T":
            for key_, x_ in T.pt_events(cur):
                ex.append((self.col(key_), x_))
        if ex:
            terms = tuple(sorted(tuple(terms) + ((tuple(sorted(ex)),),)))
        return (v2n, p, nRN, nRR, terms)


# ---------------------------------------------------------------------------------------------------- M windows (entry / exit model)
BITS4 = list(BITS)
PREV_M = ("MPREV",)


def _prev_infos():
    """all possible infos of a predecessor as seen by a vertex (used for the lower bound of the W side of an M vertex), None = first vertex"""
    out = {None}
    for f in all_eframes_m():
        out.add(f.info_prev(False))
        out.add(f.info_prev(True))
    return out


_WLB = {}


def w_lower_bound(bin_, hW_fixed=None):
    """min over the unknown W-side data (hW unless fixed, predecessor info, hidden variables) of the W side v2 of an M vertex with incoming bits `bin_`"""
    r = _WLB.get((bin_, hW_fixed))
    if r is None:
        best = None
        for prev in _prev_infos():
            if prev is None and bin_ != NONE:
                continue
            for hW in (BITS4 if hW_fixed is None else [hW_fixed]):
                for hid in LM.side_domain(bin_, prev):
                    v = LM.side_vec(bin_, prev, hW, hid)[LM.V2]
                    if best is None or v < best:
                        best = v
        r = _WLB[(bin_, hW_fixed)] = best
    return r


PROJ_ALL = {
    frozenset(("A", "C")): frozenset(("ring", "oth0")),
    frozenset(("A", "L")): frozenset(("u", "pR")),      # the L flank cannot see u and the far face pR.  Dropping the hidden parts of oth too (tokens othp / othq)
    frozenset(("A", "R")): frozenset(("u", "pL")),      # keeps FC feasible (U7) but makes the exact M rows infeasible (Z11)
    frozenset(("L", "R")): frozenset(("u", "pL", "pR", "oth0")),
    frozenset(("L", "C")): frozenset(("ring", "u", "pR", "oth0")),
    frozenset(("R", "C")): frozenset(("ring", "u", "pL", "oth0")),
}


import os as _os
_TMX = bool(_os.environ.get("TMX"))      # diagnostic: no T vertex directly next to an M vertex (NOT a certificate)
_PAIR = bool(_os.environ.get("PAIRLEM"))    # pair optimality lemma (THEORY section 25): a 4-fold vertex consecutive with a triple vertex only for the ALLOWED sector patterns
_PL = [None]
def _pair_ok(order, Mbin, Mbout, Mh, Tbin, Tbout, Th):
    if _PL[0] is None:
        sys.path.append(str(ROOT / "work/eng/T27"))
        import pairlemma
        _PL[0] = pairlemma
    return _PL[0].pair_ok(order, Mbin, Mbout, Mh, Tbin, Tbout, Th)
if _os.environ.get("PROJ_AL"):
    # experiment: what the axis-flank keys drop (tokens u, far, oth0; far = the face beyond X on the side the flank cannot see)
    _tk = set(_os.environ["PROJ_AL"].split(","))
    PROJ_ALL[frozenset(("A", "L"))] = frozenset(({"u"} if "u" in _tk else set()) | ({"pR"} if "far" in _tk else set()) | ({"oth0"} if "oth0" in _tk else set()) | ({"othp"} if "othv" in _tk else set()))
    PROJ_ALL[frozenset(("A", "R"))] = frozenset(({"u"} if "u" in _tk else set()) | ({"pL"} if "far" in _tk else set()) | ({"oth0"} if "oth0" in _tk else set()) | ({"othq"} if "othv" in _tk else set()))



MCRED = [None]       # --mcredit DELTA: credit columns TAU(word, role) at the M4 vertices (T26-style), see FCatalogueM2.finish
EPS1 = [None]        # --eps1 : None | "var" | fraction: per-M4-incidence relaxation (columns EPS1 with count +1 per M4 frame)
EPS0 = [F(0)]        # epsilon_0 (= -3 * eps)
EPS1MARGIN = [F(0)]
MVAR = [False]       # --mvar: epsilon_0 and delta are LP columns (EPS0, DELTA): path: final + eps0 - sum tau'(word, role) >= 0;  rows sum_roles tau' >= delta per bad word, delta - 18 eps0 >= margin
MVARMARGIN = [F(0)]
OBJ = {}             # column key -> objective coefficient (default 1 for every column): --mvarobj maximises delta - 18 eps0


def _add_xrow(self, name, row):
    names = self.__dict__.setdefault("_xr_names", set())
    if name in names:
        return
    names.add(name)
    if not isinstance(getattr(self, "extra_rows", None), list):
        self.extra_rows = []
    self.extra_rows.append(row)


class FCatalogueM2(T.FCatalogue):
    add_xrow = _add_xrow

    """T25 catalogue + M vertices as entry / exit pairs (see module doc).  Window keys:
       (prev, cur, ("MENTRY", boutM, last))   cur = S/T vertex followed by an M vertex whose hW is unknown (union over hW)
       (PREV_M | None, Mframe, ni)            the E side + lower bound of the W side of an M vertex; ni = info of the next vertex, a MENTRY marker
                                              (next vertex is M too) or None (M is the last vertex)."""

    _hs = None               # (hs_in, hs_out) tags of the window being built (hidden-state mode), see hs_active

    def sig_options(self, prev, cur, nxt):
        out = super().sig_options(prev, cur, nxt)
        hs = self._hs
        if hs is not None and len(hs) > 2 and hs[2]:
            sr = {(k_[1], k_[2]): int(t_) for k_, t_ in hs[2] if k_[0] == "s"}
            if sr:
                out = [o for o in out if all(o[0][SIGIDX[k_]] == v_ for k_, v_ in sr.items())]
        return out

    def window_options(self, prev, cur, nxt):
        if nxt is not None and nxt[0] == "HS":
            # hidden-state window: ("HS", inner next marker, hs_in, hs_out[, labels]); the flank-cell completions of the B rays towards the apex of a link side must carry that tag
            self._hs = (nxt[2], nxt[3], nxt[4] if len(nxt) > 4 else ())
            try:
                return self.window_options(prev, cur, nxt[1])
            finally:
                self._hs = None
        if is_m(cur):
            if SPLITM[0]:
                return self.m_self_options(prev, cur) if nxt == ("MSELF",) else self.m_exit_options_split(prev, cur, nxt)
            return self.m_exit_options(prev, cur, nxt)
        if nxt is not None and nxt[0] == "SIGT":
            # real-row mode: only the options of the TRUE hidden ray multiplicities sig of this triple window
            inner = nxt[1]
            if inner is not None and inner[0] == "MENTRY":
                inner = ("T", inner[3], inner[1], inner[2], "M")
            sg_, g_ = tuple(nxt[2]), tuple(nxt[3])
            r_ = RL.ring_of(prev, cur, inner, sg_)
            p_, v2_, nRN_, nRR_, nT_ = LA.exact_vec(prev, cur, inner, (sg_, g_))
            tt_ = self.triple_terms(prev, cur, inner, sg_, r_, ())
            if tt_ is None:
                return set()
            return {self.finish(prev, cur, inner, (v2_, p_, nRN_, nRR_, tt_))}
        if nxt is not None and nxt[0] == "MENTRY":
            res = set()
            for hW in ([nxt[3]] if len(nxt) > 3 else BITS4):
                res |= super().window_options(prev, cur, ("T", hW, nxt[1], nxt[2], "M"))
            return res
        return super().window_options(prev, cur, nxt)

    @staticmethod
    def _dom(bits, other, Mf, apex=None, side="E"):
        """hidden domain (f1, f2, g) of one side of an M vertex.
          * exactly 4-fold: f2 (rays +-2) is shared by both sides and stored in the frame;
          * apex = (code0, code1): class of the apex of the triangle on the adjacent segment of L (0: no triangle / unknown, 1: multiple, 2: simple);
            that apex IS the far end of the ray s*1 (E side) resp. s*(m-1) (W side), so f1[s] is determined;
          * F4' (T22: a run of consecutive blocks has length <= m - 2) for m = 4: no three consecutive B rays around the ray of L
            (B ray = doubly used with a SIMPLE far end): rays (-1, 0, +1), (0, 1, 2), (0, -1, -2) on the E side, mirrored on the W side."""
        B0 = bits == (1, 1) and other is not None and other[0] == "S"
        true = None
        if Mf.ub != (0, 0):
            # real-row mode (real_lp.py --truehid): the true hidden assignment of this side is encoded in ub as 1 + f1 + 2 f1' + 4 g + 8 g'
            code = Mf.ub[0 if side == "E" else 1] - 1
            true = ((code & 1, (code >> 1) & 1), (code >> 4) & 15)
        if side == "E":
            hn, hf = Mf.h[:2], Mf.h[2:]              # sectors next to the ray of L / two steps away
        else:
            hn, hf = Mf.h[2:], Mf.h[:2]
        for hid in LM.side_domain(bits, other, full_g=(true is not None)):
            f1, f2, g = hid
            if true is not None:
                code = Mf.ub[0 if side == "E" else 1] - 1
                if tuple(f1) != (code & 1, (code >> 1) & 1) or tuple(g) != ((code >> 2) & 1, (code >> 3) & 1) or tuple(f2) != ((code >> 4) & 1, (code >> 5) & 1):
                    continue
            if Mf.kind == "M" and tuple(f2) != tuple(Mf.ain):
                continue
            if apex is not None and any(apex[s_] and f1[s_] != (0 if apex[s_] == 2 else 1) for s_ in (0, 1)):
                continue
            if Mf.kind == "M" and B0:
                blk1 = [bool(bits[s_] and hn[s_] and not f1[s_]) for s_ in (0, 1)]
                blk2 = [bool(hn[s_] and hf[s_] and not f2[s_]) for s_ in (0, 1)]
                if (blk1[0] and blk1[1]) or (blk1[0] and blk2[0]) or (blk1[1] and blk2[1]):
                    continue
            if Mf.kind == "M" and side == "E":
                # run (s*1, s*2, s*3) of three B rays on side s that avoids the rays of L: the far end of the ray s*3 is the apex of the triangle on the
                # segment before the vertex (class stored in Mf.aout when the predecessor is an S / T vertex; 0 = unknown)
                if any(bits[s_] and hn[s_] and not f1[s_] and hn[s_] and hf[s_] and not f2[s_] and hf[s_] and Mf.bin[s_] and Mf.aout[s_] == 2 for s_ in (0, 1)):
                    continue
            yield hid

    def m_self_options(self, prev, Mf):
        """--splitm: the window of the M vertex itself: W side EXACT against the real predecessor info `prev` (junction nodes carry it), bonus of the class,
        PT4 cell.  (junction -> M edge)"""
        apexW = tuple(Mf.aout) if Mf.aout != (0, 0) else None
        vals = [LM.side_vec(Mf.bin, prev, Mf.h[2:], hid)[LM.V2] for hid in self._dom(Mf.bin, prev, Mf, apexW, "W")]
        if not vals:
            return set()
        w = min(vals)
        v2 = w + 6 * (MCLASS[Mf.kind] - 3)
        return {self.finish(prev, Mf, None, (v2, 0, 0, 0, ()), selfwin=True)}

    def m_exit_options_split(self, prev, Mf, ni):
        """--splitm: E side only (the rest is in the self window); finish() is given PREV_M so that the first-vertex constant is added once"""
        res = set()
        apexE = None
        if ni is not None and ni[0] == "MEXIT":
            apexE = ni[2]
            ni = ni[1]
        if ni is not None and ni[0] == "MENTRY":
            infos = [("T", ni[3], ni[1], ni[2], "M")]
        else:
            infos = [ni]
        for nx in infos:
            if nx is None and Mf.bout != NONE:
                continue
            for hidE in self._dom(Mf.bout, nx, Mf, apexE, "E"):
                vE = LM.side_vec(Mf.bout, nx, Mf.h[:2], hidE)
                own = int(nx is not None and Mf.bout == NONE)
                res.add(self.finish(PREV_M, Mf, nx, (vE[LM.V2] + 2 * own, own, 0, 0, ())))
        return res

    def m_exit_options(self, prev, Mf, ni):
        res = set()
        if ni is not None and ni[0] == "MENTRY":
            infos = [("T", hW, ni[1], ni[2], "M") for hW in ([ni[3]] if len(ni) > 3 else BITS4)]
        else:
            infos = [ni]
        if SPLITM[0]:
            wlb = w_lower_bound(Mf.bin, Mf.h[2:])
            bonus = 6 * (MCLASS[Mf.kind] - 3)
        else:
            wlb = w_lower_bound(Mf.bin)
            bonus = 6                                    # bonus 6(m-3) of the class m = 4; dummy units add 6 each in the DP
        for nx in infos:
            if nx is None and Mf.bout != NONE:
                continue
            for hidE in LM.side_domain(Mf.bout, nx):
                vE = LM.side_vec(Mf.bout, nx, Mf.h[:2], hidE)
                own = int(nx is not None and Mf.bout == NONE)
                v2 = vE[LM.V2] + 2 * own + wlb + bonus
                res.add(self.finish(prev, Mf, nx, (v2, own, 0, 0, ())))
        return res

    def project(self, sg):
        """T.FCatalogue.project plus 'oth0': forget whether the axis has an opposite block (hidden to the cap)"""
        sg = super().project(sg)
        if "oth0" in self.proj:
            ring5, u, pL, pR, tL, tR, oth = sg
            sg = (ring5, u, pL, pR, tL, tR, RL.NOOTH)
        return sg

    projall = False
    projc = frozenset()        # --projc: cell features dropped from the keys of the transfers that involve the CAP (role C): the cap cannot see them

    @staticmethod
    def _project(sg, feats):
        ring5, u, pL, pR, tL, tR, oth = sg
        if "u" in feats:
            u = 0
        if "p" in feats:
            pL = pR = 0
        if "pL" in feats:
            pL = 0
        if "pR" in feats:
            pR = 0
        if "t" in feats:
            tL = tR = 0
        if "oth" in feats and oth != RL.NOOTH:
            oth = (0, 0, 0)
        if "othp" in feats and oth != RL.NOOTH:
            oth = (0, oth[1], 0)            # keep only the face bit the L flank sees (pL of the opposite block)
        if "othq" in feats and oth != RL.NOOTH:
            oth = (0, 0, oth[2])            # the R flank sees pR of the opposite block
        if "oth0" in feats:
            oth = RL.NOOTH
        if "ring" in feats:
            ring5 = (ring5[0], "X", "X", "X", ring5[4])
        return (ring5, u, pL, pR, tL, tR, oth)

    @staticmethod
    def _pairname(pair):
        s_ = "".join(sorted(pair))
        return {"AC": "AC", "AL": "AL", "AR": "AL", "LR": "LR", "CL": "LC", "CR": "LC"}[s_]

    def pair_col(self, sg, p, q):
        """LP column of the transfer `p pays q` (roles A C L R) in the block cell sg (block orientation); transfers involving the cap use the
        cap-visible projection of the cell when --projc is set"""
        if self.proj:
            sg = self.project(sg)
        if self.projall:
            # every pair key = the cell features visible to BOTH parties (cap: near ring fR/fL, u, pL, pR, tL, tR; flank L: ring, pL, tL, tR; flank R: ring,
            # pR, tL, tR; axis: all), so that no party has a hidden completion
            pair = frozenset((p, q))
            drop = PROJ_ALL.get(pair) if (self.projall is True or self._pairname(pair) in self.projall) else None
            if drop:
                sg = self._project(sg, drop)
        elif self.projc and "C" in (p, q):
            sg = self._project(sg, self.projc)
        sm = RL.mirror_sig(sg)
        swap = sm < sg
        cs = sm if swap else sg
        symm = sm == sg
        if swap:
            p = {"L": "R", "R": "L"}.get(p, p)
            q = {"L": "R", "R": "L"}.get(q, q)
        return self.col((("M" if (symm and p in "LR") else p), ("M" if (symm and q in "LR") else q), cs))

    def role_vec(self, role, sg):
        k = (role, sg)
        v = self._rv.get(k)
        if v is not None:
            return v
        out = collections.Counter()
        for q in "ACLR":
            if q == role:
                continue
            out[self.pair_col(sg, role, q)] -= 1
            out[self.pair_col(sg, q, role)] += 1
        v = tuple(sorted((c, x) for c, x in out.items() if x))
        self._rv[k] = v
        return v

    noblock = False           # real-row mode with exact block cells: no block terms in the windows (the exact block events are added per line)

    cell_removed = None      # {repr((prev, cur, nxt, sig, j)): {combo}}: joint flank completions refuted by pattern SAT (cells_sweep_m.py)
    _wg = True               # celldom guard of the current window (see _guard_t); the cap windows never use the cell filter when GUARD is on

    def cell_ok(self, cell):
        if not self.celldom:
            return True
        if GUARD[0] and not self._wg:
            return True
        return super().cell_ok(cell)

    @staticmethod
    def _guard_t(prev, cur, nxt, sig):
        """the T23 axis-cell set was derived for exactly-triple arrangements: use it only for a window whose neighbours are not M, whose triangles have no
        class-3 apex and whose multiple far ends are certified exactly triple by the apex flag of the adjacent triangle"""
        if (prev is not None and len(prev) == 5) or (nxt is not None and len(nxt) == 5):
            return False
        if any(a == 3 for a in tuple(cur.ain) + tuple(cur.aout)):
            return False
        for k, a in enumerate((cur.aout[0], cur.aout[1], cur.ain[0], cur.ain[1])):
            if sig[k] == 1 and a != 1:
                return False
        return True

    def triple_terms_hs(self, prev, cur, nxt, sig, r, zero, hs):
        """T.FCatalogue.triple_terms with the hidden-state tags: the (u, pO) completion of the flank block on a link side must have pO == tag"""
        hin, hout = hs[0], hs[1]
        lab = hs[2] if len(hs) > 2 else ()
        labd = {(k_[1], k_[2]): t_ for k_, t_ in lab if k_[0] == "c"}
        ulab = {(k_[1], k_[2]): t_ for k_, t_ in lab if k_[0] == "u"}
        if ulab:
            present_u = {(("out" if RL.M_TABLE[j_][1] == "nxt" else "in"), RL.M_TABLE[j_][2]) for j_ in (1, 2, 4, 5) if r[j_] == "B"}
            for k_, t_ in ulab.items():
                if t_ == "1" and k_ not in present_u:
                    return None              # token 1 needs the flank block on that ray
        if labd:
            present = {(("out" if RL.M_TABLE[j_][1] == "nxt" else "in"), RL.M_TABLE[j_][2]) for j_ in (1, 2, 4, 5) if r[j_] == "B"}
            for k_, t_ in labd.items():
                if (t_ == "X") == (k_ in present):
                    return None              # token X <=> the ray carries no flank block
        terms = []
        done = set()
        for j in range(6):
            if r[j] != "B" or j in done:
                continue
            if j % 3 == 0:
                terms.append((self.role_vec("A", self.sig_axis(prev, nxt, sig, r, j)),))
                continue
            jo = (j + 3) % 6
            grp = [j] + ([jo] if r[jo] == "B" else [])
            done.update(grp)
            info, doms = [], []
            for jj in grp:
                side, ok, sg_, own, hid = RL.M_TABLE[jj]
                other = nxt if ok == "nxt" else prev
                pM = other[1][sg_] if other[0] == "T" else 0
                tOwn = int(other[0] == "T")
                tHid = sig[RL.POS_IDX[hid]]
                info.append((jj, side, pM, tOwn, tHid))
                tag = (hout if ok == "nxt" else hin)[sg_]
                tk = labd.get(("out" if ok == "nxt" else "in", sg_))
                tu = ulab.get(("out" if ok == "nxt" else "in", sg_))
                doms.append([c for c in self._m_completions(pM, tHid, jj in zero) if (tag is None or c[1] == tag) and (tk is None or c == TOKCOMP[tk])
                             and (tu is None or c[0] == int(tu))])
            opts = set()
            for comp in itertools.product(*doms):
                vec = collections.Counter()
                sgs = [(jj, side, pM, tOwn, tHid, u, pO) for (jj, side, pM, tOwn, tHid), (u, pO) in zip(info, comp)]
                cells = []
                bad = False
                for idx_, (jj, side, pM, tOwn, tHid, u, pO) in enumerate(sgs):
                    if side == "L":
                        pL, pR, tL, tR = pM, pO, tOwn, tHid
                    else:
                        pR, pL, tR, tL = pM, pO, tOwn, tHid
                    if len(sgs) == 2:
                        jj2, side2, pM2, tOwn2, tHid2, u2, pO2 = sgs[1 - idx_]
                        oth = (u2, pM2, pO2) if side2 == "L" else (u2, pO2, pM2)
                    else:
                        oth = RL.NOOTH
                    r5 = tuple(r[(jj + t) % 6] for t in range(1, 6))
                    cell = (r5, u, pL, pR, tL, tR, oth)
                    if not self.cell_ok(cell):
                        bad = True
                        break
                    cells.append((side, cell))
                if bad:
                    continue
                for side, cell in cells:
                    for cc, x in self.role_vec(side, cell):
                        vec[cc] += x
                opts.add(tuple(sorted((c, x) for c, x in vec.items() if x)))
            if not opts:
                self.stats["window_no_completion"] += 1
                return None
            terms.append(tuple(sorted(opts)))
        return tuple(sorted(terms))

    def triple_terms(self, prev, cur, nxt, sig, r, zero=()):
        if self.noblock:
            return ()
        self._wg = self._guard_t(prev, cur, nxt, sig) if GUARD[0] else True
        if self._hs is not None:
            return self.triple_terms_hs(prev, cur, nxt, sig, r, zero, self._hs)
        if not self.cell_removed:
            return super().triple_terms(prev, cur, nxt, sig, r, zero)
        terms = []
        done = set()
        for j in range(6):
            if r[j] != "B" or j in done:
                continue
            if j % 3 == 0:
                terms.append((self.role_vec("A", self.sig_axis(prev, nxt, sig, r, j)),))
                continue
            jo = (j + 3) % 6
            grp = [j] + ([jo] if r[jo] == "B" else [])
            done.update(grp)
            info = []
            for jj in grp:
                side, ok, sg_, own, hid = RL.M_TABLE[jj]
                other = nxt if ok == "nxt" else prev
                pM = other[1][sg_] if other[0] == "T" else 0
                tOwn = int(other[0] == "T")
                tHid = sig[RL.POS_IDX[hid]]
                info.append((jj, side, pM, tOwn, tHid))
            rem = None
            if len(grp) == 2:
                rem = self.cell_removed.get(repr((tuple(prev[:4]), cur, tuple(nxt[:4]), tuple(sig), j)))
            opts = set()
            for comp in itertools.product(*[self._m_completions(pM, tHid, jj in zero) for (jj, side, pM, tOwn, tHid) in info]):
                if rem and tuple(tuple(c) for c in comp) in rem:
                    continue
                vec = collections.Counter()
                sgs = [(jj, side, pM, tOwn, tHid, u, pO) for (jj, side, pM, tOwn, tHid), (u, pO) in zip(info, comp)]
                for idx_, (jj, side, pM, tOwn, tHid, u, pO) in enumerate(sgs):
                    if side == "L":
                        pL, pR, tL, tR = pM, pO, tOwn, tHid
                    else:
                        pR, pL, tR, tL = pM, pO, tOwn, tHid
                    if len(sgs) == 2:
                        jj2, side2, pM2, tOwn2, tHid2, u2, pO2 = sgs[1 - idx_]
                        oth = (u2, pM2, pO2) if side2 == "L" else (u2, pO2, pM2)
                    else:
                        oth = RL.NOOTH
                    r5 = tuple(r[(jj + t) % 6] for t in range(1, 6))
                    for cc, x in self.role_vec(side, (r5, u, pL, pR, tL, tR, oth)):
                        vec[cc] += x
                opts.add(tuple(sorted((c, x) for c, x in vec.items() if x)))
            terms.append(tuple(sorted(opts)))
        return tuple(sorted(terms))

    def cap_terms(self, prev, cur, nxt):
        if prev is None or nxt is None:
            return ()
        self._wg = not GUARD[0]
        terms = []
        for k in (0, 1):
            if not (cur.bin[k] and cur.bout[k]):
                continue
            if cur.aout[k] == 3:
                if MB[0]:
                    o = 1 - k
                    kk = cur.bin[o] + cur.bout[o]
                    terms.append((tuple(sorted(((self.col(("MB", kk, "A>C")), 1), (self.col(("MB", kk, "C>A")), -1)))),))
                continue
            if self.noblock:
                continue          # real-row mode: the block cell of a triple-apex block is added exactly (exact_blocks.py)
            o = 1 - k
            u = int(cur.ub[o])
            pR, pL = cur.bin[o], cur.bout[o]
            tR, tL = int(prev[0] == "T"), int(nxt[0] == "T")
            fR = "R" if (prev[0] == "T" and prev[1][k]) else "N"
            fL = "R" if (nxt[0] == "T" and nxt[1][k]) else "N"
            s12, s45 = fR == "R", fL == "R"
            opts = set()
            for s23 in (0, 1):
                for s34 in (0, 1):
                    dbl = (s12 and s23, s23 and s34, s34 and s45)
                    for far in itertools.product(*[(0, 1) if d else (None,) for d in dbl]):
                        x = ["N" if d is None else ("B" if d == 0 else "R") for d in far]
                        if (x[0] == "B" and x[1] == "B") or (x[1] == "B" and x[2] == "B"):
                            continue
                        if self.rings is not None and RL.canon_ring(("B", fR) + tuple(x) + (fL,)) not in self.rings:
                            continue
                        ring5 = (fR, x[0], x[1], x[2], fL)
                        for oth in (RL.OTH_STATUSES if x[1] == "B" else (RL.NOOTH,)):
                            cell = (ring5, u, pL, pR, tL, tR, oth)
                            if not self.cell_ok(cell):
                                continue
                            opts.add(self.role_vec("C", cell))
            if not opts:
                return None
            terms.append(tuple(sorted(opts)))
        return tuple(sorted(terms))

    def finish(self, prev, cur, nxt, opt, selfwin=False):
        v2, p, nRN, nRR, terms = opt
        if GIFT[0] and not is_m(cur):
            v2 = v2 + 2 * GIFT[0] * sum(1 for k in (0, 1) if cur.bin[k] and cur.bout[k] and cur.aout[k] == 3)
        if not (self.split_a or self.alpha or self.wr or self.sv or self.tri or self.pt):
            return opt
        own = int(nxt is not None and cur.bout == NONE)
        touch = sum(1 for k in (0, 1) if not cur.ub[k] and cur.bin[k] + cur.bout[k] == 0) if cur.kind == "S" else 0
        bits = (cur.bout[0] + cur.bout[1]) if nxt is not None else 0
        ex = []
        v2n = v2
        if self.split_a:
            v2n = v2 - 2 * own + touch
            ca = 3 * own - 1.5 * touch
            if ca:
                ex.append((self.col(("a",)), ca))
        if self.alpha:
            x = (-6 * bits - v2) / 2 + (3 * (self.W - 1) if prev is None else 0)
            if x:
                ex.append((self.col(("alpha",)), x))
        if self.wr and own:
            cw = int(cur.kind != "S") + int(nxt[0] != "S")
            if cw:
                ex.append((self.col(("wr",)), cw))
                self.add_xrow("special", ({("wr",): 1.0, ("a",): 1.5, ("alpha",): 1.0}, 1.5))      # exact validity condition of the special columns (A30, THEORY section 23): alpha' + wr + 1.5 a <= 3/2
        if self.sv and cur.kind == "S":
            for key_, x_ in T.sv_events(cur):
                ex.append((self.col(key_), x_))
        if MB[0] and cur.kind == "S":
            for key_, x_ in mb_axis_events(prev, cur, nxt):
                ex.append((self.col(key_), x_))
        if self.tri:
            for key_, x_ in tri_events_m(prev, cur, nxt):
                ex.append((self.col(key_), x_))
        if self.pt and cur.kind == "T":
            for key_, x_ in T.pt_events(cur):
                ex.append((self.col(key_), x_))
        if self.pt and SPLITM[0] and selfwin and cur.kind == "M":
            for key_, x_ in pt4_events(cur):
                ex.append((self.col(key_), x_))
        if MVAR[0] and prev is None:
            ex.append((self.col(("EPS0",)), 1))                             # every path: + eps0 (a path has exactly one first vertex)
            self.add_xrow("eps0max", ({("EPS0",): 1.0}, 0.5))
            if _os.environ.get("EPSX"):
                self.add_xrow("margin", ({("DELTA",): -1.0, ("EPS0",): 18.0, ("EPSM",): 4.0, ("EPSA",): 8.0}, -float(MVARMARGIN[0])))   # delta - 18 eps0 - 4 epsM - 8 epsA >= margin
                self.col(("EPSM",)); self.col(("EPSA",))
            else:
                self.add_xrow("margin", ({("DELTA",): -1.0, ("EPS0",): 18.0}, -float(MVARMARGIN[0])))      # delta - 18 eps0 >= margin
            self.add_xrow("deltamax", ({("DELTA",): 1.0}, float(_os.environ.get("DELTAMAX", "12"))))
            self.col(("DELTA",))
        if _os.environ.get("EPSX"):
            # per-incidence slack (lead): EPSM per M4 vertex of the path, EPSA per side of an outgoing S/T segment whose triangle has a >= 4-fold apex.
            # Sum over the lines: >= sum_P credit - 4 EPSM - 8 EPSA per bad point P (undercounting the flags only makes the bound conservative).
            if SPLITM[0] and selfwin and cur.kind == "M":
                ex.append((self.col(("EPSM",)), 1))
            if cur.kind in ("S", "T") and nxt is not None and getattr(cur, "aout", None):
                na3 = sum(1 for k_ in (0, 1) if cur.aout[k_] == 3)
                if na3:
                    ex.append((self.col(("EPSA",)), na3))
        if (MCRED[0] is not None or MVAR[0]) and SPLITM[0] and selfwin and cur.kind == "M":
            sec = (cur.bout[0], cur.h[0], cur.h[2], cur.bin[0], cur.bin[1], cur.h[3], cur.h[1], cur.bout[1])
            canon_, role_, row_ = pt4_cell(sec)
            _mw = _os.environ.get("MWORD")                                  # per-group credit (lead): credit only at ONE bad word (6 / 7 / 8 triangle sectors)
            _skip = bool(_mw) and canon_ not in [bad4_words()[{"6": 0, "7": 1, "8": 2}[c_]] for c_ in _mw]
            if not _skip:
                ex.append((self.col(("TAU", canon_, role_)), -1))              # path constraint: final >= -eps0 - eps1 * nM + sum tau'(word, role of this line)
                if MVAR[0]:
                    rowd = {("TAU", canon_, r_): -float(c_) for r_, c_ in row_.items()}
                    rowd[("DELTA",)] = 1.0
                    self.add_xrow(("tau", canon_), (rowd, 0.0))                  # sum over the 4 lines of tau' >= delta (variable)
                else:
                    self.add_xrow(("tau", canon_), ({("TAU", canon_, r_): -float(c_) for r_, c_ in row_.items()}, -float(MCRED[0])))      # sum over the 4 lines of tau' >= delta
                if EPS1[0] == "var":
                    ex.append((self.col(("EPS1",)), 1))
                    self.add_xrow("eps1", ({("EPS1",): 4.0}, float(MCRED[0] - 18 * EPS0[0] - EPS1MARGIN[0])))      # 4 eps1 + 18 eps0 <= delta - margin
                elif EPS1[0] is not None:
                    v2n = v2n + 2 * EPS1[0] * 1   # (not used: fixed eps1 would need non-integer v2)
        if STAR[0] is not None and SPLITM[0] and selfwin and cur.kind == "M" and not self.noblock:
            st_opts = star_options(prev, cur)
            st_opts = tuple((tuple((self.col(k_), x_) for k_, x_ in o_)) for o_ in st_opts)
            terms = tuple(sorted(tuple(terms) + (tuple(sorted(st_opts)),)))
        if ex:
            terms = tuple(sorted(tuple(terms) + ((tuple(sorted(ex)),),)))
        return (v2n, p, nRN, nRR, terms)


def apex_code(bits, cls):
    """1 multiple (class 1 or 3), 2 simple, 0 no triangle"""
    return tuple((0 if not bits[s_] else (2 if cls[s_] == 2 else 1)) for s_ in (0, 1))


def hid_code(h):
    """(f1, f2, g) of one side -> 1 + bits (see FCatalogueM2._dom)"""
    f1, f2, g = h
    return 1 + f1[0] + 2 * f1[1] + 4 * g[0] + 8 * g[1] + 16 * f2[0] + 32 * f2[1]


def line_window_keys(fr, mults, hids=None):
    """window keys (splitm model) of a REAL line given as frames (S / T enriched, M kind 'M' = exactly 4-fold with ain = f2, 'MP' = m >= 5).
    Returns (keys, number of dummy units, None) or (None, 0, reason) when the line is not a path of the reduced model (an M vertex that is not a
    bad 4-fold pattern, see THEORY section 24)."""
    m = len(fr)
    ip = [None] + [fr[i].info_prev(i == 0) for i in range(m - 1)]
    inx = [fr[i].info_next(i == m - 1) for i in range(1, m)] + [None]
    keys, nd = [], 0
    for i, f in enumerate(fr):
        ismf = is_m(f)
        prev = None if i == 0 else (PREV_M if ismf else ip[i])
        nxt = inx[i]
        if ismf:
            if f.kind == "MP":
                if BADONLY[0]:
                    return None, 0, "MP"
                nd += mults[i] - 5
            elif BADONLY[0] and not is_bad4(f.bout, f.h[:2], f.h[2:], f.bin):
                return None, 0, "notbad"
            aW = (0, 0) if (i == 0 or is_m(fr[i - 1])) else apex_code(fr[i].bin, fr[i - 1].aout)
            ubc = (hid_code(hids[i][0]), hid_code(hids[i][1])) if (hids is not None and hids[i] is not None) else NONE
            Mf = MF(f.kind, f.bin, f.bout, ubc, f.h, f.ain, aW)
            keys.append((ip[i], Mf, ("MSELF",)))
            if nxt is None:
                ex = None
            elif is_m(fr[i + 1]):
                ex = ("MENTRY", nxt[2], nxt[3], nxt[1])
            else:
                ex = ("MEXIT", nxt, apex_code(fr[i + 1].bin, fr[i + 1].ain))
            keys.append((PREV_M if i > 0 else None, Mf, ex))
        else:
            if nxt is not None and len(nxt) == 5:
                nxt = ("MENTRY", nxt[2], nxt[3], nxt[1])
            if hids is not None and f.kind == "T" and hids[i] is not None:
                nxt = ("SIGT", nxt, tuple(hids[i][0]), tuple(hids[i][1]))
            keys.append((prev, f, nxt))
    return keys, nd, None


# ---------------------------------------------------------------------------------------------------- forbidden frame patterns (SAT cores, 4-fold allowed)
def match_pred_m(pred, f):
    """frame predicate (kind, bin, bout, h(4), ain, aout, exact): positive information only.  kind 'M' matches the exactly 4-fold M frame (h = hE+, hE-, hW+, hW-),
    'S' / 'T' match simple / exactly triple vertices (apex classes ain / aout must be equal when given); MP frames never match."""
    kind, bin_, bout, h, ain, aout, exact = pred[:7]
    if f.kind == "MP" or f.kind == "MJ":
        return False
    if len(pred) > 7 and f.kind in ("S", "T") and (3 in f.ain or 3 in f.aout):
        return False             # guarded fact pattern (T23 P000-P009, proved for multiplicity <= 3): no class-3 apex flag anywhere on a matched frame
    if exact is not None:
        # whole-line word (n = 18 only): (kind, bin, bout, ub, h, ain, aout); M frames compare kind / bits / h only
        if f.kind != exact[0] or tuple(f.bin) != exact[1] or tuple(f.bout) != exact[2]:
            return False
        if f.kind == "M":
            return tuple(f.h) == exact[4]
        return tuple(f.ub) == exact[3] and tuple(f.h) == exact[4] and tuple(f.ain) == exact[5] and tuple(f.aout) == exact[6]
    if kind == "M":
        if f.kind != "M":
            return False
        return all(not (bin_[s_] and not f.bin[s_]) and not (bout[s_] and not f.bout[s_]) for s_ in (0, 1)) and all(not (h[i_] and not f.h[i_]) for i_ in range(4))
    if f.kind not in ("S", "T") or (kind is not None and f.kind != kind):
        return False
    for s_ in (0, 1):
        if bin_[s_] and not f.bin[s_]:
            return False
        if bout[s_] and not f.bout[s_]:
            return False
        if h[s_] and not (f.kind == "T" and f.h[s_]):
            return False
        if ain[s_] and f.ain[s_] != ain[s_]:
            return False
        if aout[s_] and f.aout[s_] != aout[s_]:
            return False
    return True


LAMSTATE = [()]          # labels of the window being stepped: sorted tuple of (key, token), set by the graph builder (T29 hidden labels)
TOKCOMP = {"N": (0, 0), "F": (0, 1), "U": (1, 0), "X": None}      # token -> flank completion (u, pO): N neither, F far face (F4) a triangle, U axis ends at X, X no flank block on the ray
TOKALLOW = {"far": ("F",), "unb": ("U",), "nfar": ("X", "N", "U"), "nunb": ("X", "N", "F")}


class MPatternSet(T.PatternSet):
    """forbidden frame patterns with optional hidden-state parts (T29):
    labs[(j, i)]  = [(key, allowed tokens)]: key ("c", dir, side) = flank-cell completion of the ray (dir in/out, side 0/1) of the i-th frame of pattern j (tokens X N F U),
                    key ("s", dir, side) = the sig bit (far-end multiplicity) of that ray (tokens "0" / "1")
    zeros[(j, i)] = [(field, idx, val)]: exact frame bits (field bin / bout / h with val 0, or ub with val 1) that the positive frame predicate cannot express.
    A predicate matches only if its window variant (LAMSTATE) carries the labels."""
    labs = {}
    zeros = {}

    def _ok(self, j, i, f, ld, check_labs=True):
        ps = self.pats[j][1]
        if not match_pred_m(ps[i], f):
            return False
        for (fld, idx, val) in self.zeros.get((j, i), ()):
            if fld == "bout" and f.bout[idx] != val: return False
            if fld == "bin" and f.bin[idx] != val: return False
            if fld == "h" and (f.h[idx] if idx < len(f.h) else 0) != val: return False
            if fld == "ub" and f.ub[idx] != val: return False
        if check_labs:
            for (k_, allow) in self.labs.get((j, i), ()):
                if ld.get(k_) not in allow:
                    return False
        return True

    def step(self, state, f):
        lam = LAMSTATE[0]
        if lam and any(k_[0] == "u" for k_, t_ in lam):
            lam = tuple(x for x in lam if x[0][0] != "u")        # the u labels belong to the U-UB state, not to the patterns
        key = (state, f, lam)
        r = self._cache.get(key)
        if r is not None:
            return r if r != "BAD" else None
        new = set()
        ld = dict(lam)
        for (j, i) in state:
            if self._ok(j, i, f, ld):
                new.add((j, i + 1))
        for j, (a, ps) in enumerate(self.pats):
            if not a and self._ok(j, 0, f, ld):
                new.add((j, 1))
        if any(i == len(self.pats[j][1]) for (j, i) in new):
            self._cache[key] = "BAD"
            return None
        res = frozenset(new)
        self._cache[key] = res
        return res

    def watch(self, state, f):
        """label keys observed by a predicate that matches the frame f (ignoring labels, honouring the exact bits) and is active in `state` (or can start here)"""
        if not self.labs:
            return ()
        w = set()
        cand = list(state) + [(j, 0) for j, (a, ps) in enumerate(self.pats) if not a]
        for (j, i) in cand:
            if (j, i) in self.labs and self._ok(j, i, f, None, False):
                w |= {k_ for k_, t_ in self.labs[(j, i)]}
        return tuple(sorted(w))


MPSET = [None]
SIGIDX = {("out", 0): 0, ("out", 1): 1, ("in", 0): 2, ("in", 1): 3}      # (dir, side) of a ray -> index in sig = (E+, E-, W+, W-)
RAYDIR = {"E+": ("out", 0), "E-": ("out", 1), "W+": ("in", 0), "W-": ("in", 1)}
TOKEN = {"far": "F", "unb": "U", "none": "N"}


def lam_variants(k3s, cur):
    """window variants of the labels observed by the active patterns: tuples of (key, token); tokens X N F U for completions, 0 1 for sig bits"""
    ps = MPSET[0]
    if ps is None or not ps.labs or cur.kind != "T":
        return [()]
    pst = ps.init if k3s == (0, 0) else k3s[2]
    w = ps.watch(pst, cur)
    if not w:
        return [()]
    return [tuple(zip(w, toks)) for toks in itertools.product(*[("01" if k_[0] == "s" else "XNFU") for k_ in w])]


def _flip_lab(k_):
    return (k_[0], 1 - k_[1])


def _rev_lab(k_):
    return ({"out": "in", "in": "out"}[k_[0]], k_[1])


def _flip(pr):
    k, bi, bo, h, ai, ao = pr
    hh = [h[1], h[0], h[3], h[2]] if k == "M" else [h[1], h[0], 0, 0]
    return [k, [bi[1], bi[0]], [bo[1], bo[0]], hh, [ai[1], ai[0]], [ao[1], ao[0]]]


def _rev(pr):
    k, bi, bo, h, ai, ao = pr
    hh = [h[2], h[3], h[0], h[1]] if k == "M" else list(h)
    return [k, list(bo), list(bi), hh, list(ao), list(ai)]


def load_mpats(path):
    """json list of {"preds": [[kind, bin, bout, h, ain, aout], ...]}: the four symmetric variants (flip sides, reverse direction) are forbidden"""
    import json as _json
    pats, seen = [], set()
    labs_all, zeros_all = {}, {}
    for c in _json.load(open(path)):
        if "word" in c:
            # anchored whole-line word of an 'exact-n only' unrealizable path, both directions and both side flips
            fr = c["word"]        # list of [kind, bin, bout, ub, h, ain, aout]
            def mk(seq):
                return (True, [(x[0], (), (), (), (), (), (x[0], tuple(x[1]), tuple(x[2]), tuple(x[3]), tuple(x[4]), tuple(x[5]), tuple(x[6]))) for x in seq])
            def fl(x):
                k, bi, bo, ub, h, ai, ao = x
                return [k, [bi[1], bi[0]], [bo[1], bo[0]], [ub[1], ub[0]], [h[1], h[0]] if k == "T" else ([h[1], h[0], h[3], h[2]] if k == "M" else list(h)), [ai[1], ai[0]], [ao[1], ao[0]]]
            def rv(x):
                k, bi, bo, ub, h, ai, ao = x
                return [k, list(bo), list(bi), list(ub), ([h[2], h[3], h[0], h[1]] if k == "M" else list(h)), list(ao), list(ai)]
            for flip in (0, 1):
                for rev in (0, 1):
                    seq = [fl(x) if flip else list(x) for x in fr]
                    if rev:
                        seq = [rv(x) for x in reversed(seq)]
                    key = _json.dumps(seq)
                    if key not in seen:
                        seen.add(key)
                        pats.append(mk(seq))
            continue
        base = c["preds"]
        m_ = len(base)
        for flip in (0, 1):
            for rev in (0, 1):
                pp = [_flip(x) if flip else list(x) for x in base]
                lb, zr = {}, {}              # position -> requirements after the symmetry
                items = ([(("c", ) + RAYDIR[r_], a_, set(TOKALLOW[k_])) for (a_, r_, k_) in c.get("labs", [])]
                         + [(("s", ) + RAYDIR[r_], a_, {str(int(v_))}) for (a_, r_, v_) in c.get("sigs", [])])
                for (key, slot, allow) in items:
                    k_ = (key[1], key[2])
                    if flip:
                        k_ = _flip_lab(k_)
                    if rev:
                        k_ = _rev_lab(k_)
                    lb.setdefault(m_ - 1 - slot if rev else slot, []).append(((key[0],) + k_, tuple(sorted(allow))))
                for (slot, fld, idx) in c.get("zeros", []):
                    kind_ = base[slot][0]
                    val = 1 if fld == "ub" else 0
                    if flip:
                        if fld == "h" and kind_ == "M":
                            idx = {0: 1, 1: 0, 2: 3, 3: 2}[idx]
                        else:
                            idx = 1 - idx
                    pos = slot
                    if rev:
                        pos = m_ - 1 - slot
                        if fld == "bout": fld = "bin"
                        elif fld == "bin": fld = "bout"
                        elif fld == "h" and kind_ == "M": idx = {0: 2, 1: 3, 2: 0, 3: 1}[idx]
                    zr.setdefault(pos, []).append((fld, idx, val))
                if rev:
                    pp = [_rev(x) for x in reversed(pp)]
                key = _json.dumps([pp, sorted((i_, sorted(v_)) for i_, v_ in lb.items()), sorted((i_, sorted(v_)) for i_, v_ in zr.items())])
                if key in seen:
                    continue
                seen.add(key)
                for i_, v_ in lb.items():
                    labs_all[(len(pats), i_)] = v_
                for i_, v_ in zr.items():
                    zeros_all[(len(pats), i_)] = v_
                pats.append((bool(c.get("anchored")), [(x[0], tuple(x[1]), tuple(x[2]), tuple(x[3]), tuple(x[4]), tuple(x[5]), None) for x in pp]))
    ps_ = MPatternSet(pats)
    ps_.labs = labs_all
    ps_.zeros = zeros_all
    return ps_


def load_warm_filtered(G, path, pset):
    """cuts of an earlier round (json dump with windows) as initial cuts; cuts without windows (older warm starts) and cuts whose frame sequence matches a
    forbidden pattern are dropped.  Columns must exist in the catalogue."""
    import ast
    import json as _json
    sys.path.append(str(ROOT / "work/eng/T27"))
    sys.path.insert(0, str(ROOT / "work/eng/T23"))
    import classify_cuts as CC
    import sat_path as SP
    out, dropped, nowin = [], 0, 0
    for c in _json.load(open(path)):
        if not c["windows"]:
            nowin += 1
            continue
        if pset is not None and pset.pats and frames_match_pats(SP.parse(CC.notation(c)), pset):
            dropped += 1
            continue
        if _PAIR and frames_pair_bad(SP.parse(CC.notation(c))):
            dropped += 1
            continue
        if _TMX:
            ks = [f.kind for f in SP.parse(CC.notation(c))]
            if any((x == "T" and y == "M") or (x == "M" and y == "T") for x, y in zip(ks, ks[1:])):
                dropped += 1
                continue
        try:
            cnt = {G.cat.idx[ast.literal_eval(k)]: x for k, x in c["counts"].items()}
        except KeyError:
            continue
        out.append((c["v2"], cnt, [], "path", None, c.get("target") or RL.TARGET))
    print(f"warm dump {path}: kept {len(out)}, dropped {dropped} (forbidden pattern), {nowin} without windows", flush=True)
    return out


def frames_pair_bad(frames):
    """cut frame list (one frame per vertex): True if a T-M or M-T adjacency has a disallowed pair pattern"""
    vs = list(frames)        # one frame per vertex in the LP dumps (an M vertex is NOT duplicated)
    for x, y in zip(vs, vs[1:]):
        if x.kind == "M" and y.kind == "T" and not _pair_ok("MT", x.bin, x.bout, x.h, y.bin, y.bout, y.h):
            return True
        if x.kind == "T" and y.kind == "M" and not _pair_ok("TM", y.bin, y.bout, y.h, x.bin, y.bin, x.h):
            return True
    return False


def frames_match_pats(frames, pset):
    """True if the frame sequence (list of frames) contains a forbidden pattern"""
    st = pset.init
    for f in frames:
        st = pset.step(st, f)
        if st is None:
            return True
    return False


# ---------------------------------------------------------------------------------------------------- graph
def canon_arrival(state):
    """arrival state at an M node: the K3 run is dead there; the pattern progress, the F5* union U and the NC flag survive"""
    if state == (0, 0):
        return state
    return ("X", (0, 0), state[2], state[3], state[4], state[5], state[6]) + tuple(state[7:])      # the pattern progress now survives an M arrival (patterns may span T/S -> M)


class WGraphM2(RL.WGraph):
    """RL.WGraph with M vertices as entry / exit pairs; node units S 1, T 2, M 3 (+ dummy 1-unit loops in the DP); no parity bit"""

    def __init__(self, cat, allow=lambda f: True, edge_allow=lambda c, n: True, k3=False, topology_only=False, use_m=True):
        self.cat = cat
        frames = [f for f in all_eframes_m() if not is_m(f) and allow(f)]
        by_bin = collections.defaultdict(list)
        for f in frames:
            by_bin[f.bin].append(f)
        print(f"frames: {len(frames)} (S/T enriched, apex classes 1/2/3)", flush=True)
        self.win_id, self.win_list = {}, []
        node_id, nodes = {}, []
        k3_step = RL.k3_step

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

        def mframes(bin_, bout, hE):
            """(not --splitm) one M frame with hW unknown"""
            return [MF("M", bin_, bout, NONE, hE + (0, 0), (0, 0), (0, 0))]

        def jframe(bin_, bout, hW, apexW=(0, 0)):
            """--splitm: junction node between the predecessor and the M vertex: carries (bin, bout, hW); the window of the predecessor needs exactly these;
            apexW = code of the apex classes of the triangles on the segment to the predecessor (1 multiple, 2 simple, 0 none / unknown): far end of the W-side ray"""
            return MF("MJ", bin_, bout, NONE, (0, 0) + hW, (0, 0), apexW)



        def mkind_frames(J):
            """exactly 4-fold vertex: the far-end multiplicities f2 of the rays +-2 are SHARED by the E and the W side (rays s*2 = s*(m-2) for m = 4), stored in `ain`;
            m >= 5: independent sides"""
            out = [MF("M", J.bin, J.bout, NONE, hE + J.h[2:], f2, J.aout) for hE in BITS4 for f2 in BITS4
                   if not BADONLY[0] or is_bad4(J.bout, hE, J.h[2:], J.bin)]
            if not BADONLY[0]:
                out += [MF("MP", J.bin, J.bout, NONE, hE + J.h[2:], (0, 0), J.aout) for hE in BITS4]
            return out

        starts, edges, terms, stack = [], [], [], []
        for f in frames:
            if f.bin == NONE:
                x = (None, f, 0, f.ub, 0, (0, 0), HS0)
                starts.append(nid(x))
                stack.append(x)
        if use_m and SPLITM[0]:
            for bout, hW in itertools.product(BITS4, BITS4):
                for last in (0, 1):
                    if last and bout != NONE:
                        continue
                    x = (None, jframe(NONE, bout, hW), 0, NONE, last, (0, 0), HS0)
                    starts.append(nid(x))
                    stack.append(x)
        elif use_m:
            for bout, hE in itertools.product(BITS4, BITS4):
                for Mf in mframes(NONE, bout, hE):
                    x = (None, Mf, 0, NONE, 0, (0, 0), HS0)
                    starts.append(nid(x))
                    stack.append(x)
        seen = set(stack)

        def add(u, prev, cur, ni, y_frame, last, cls, k3s, mnext, hs=HS0, lam=()):
            """edge u -> node of y_frame; returns None if forbidden"""
            k3n = (0, 0)
            if k3:
                LAMSTATE[0] = lam
                try:
                    k3n = k3_step(k3s, prev, cur, ni)
                finally:
                    LAMSTATE[0] = ()
                if k3n is None:
                    return
                if mnext:
                    k3n = canon_arrival(k3n)
            y = (PREV_M if is_m(y_frame) else cur.info_prev(prev is None), y_frame, 0, cls, last, k3n, hs)   # junction nodes keep the predecessor's info (exact W side)
            if y not in seen:
                seen.add(y)
                stack.append(y)
            nid(y)
            return y

        while stack:
            x = stack.pop()
            prev, cur, par, cls, role, k3s, hsin = x
            u = node_id[x]
            if cur.kind == "MJ":
                # junction -> M / MP vertex (hE and the class m = 4 or >= 5 are chosen here); the self window of the M vertex sits on this edge
                for Mf in mkind_frames(cur):
                    if any(hsin[s_] == 1 and Mf.ain[s_] != 1 for s_ in (0, 1)):
                        continue                     # --hidm: tag pO = 1 on side s needs f2[s] = 1
                    if _PAIR and prev is not None and len(prev) == 4 and prev[0] == "T" and not _pair_ok("TM", Mf.bin, Mf.bout, Mf.h, prev[2], Mf.bin, prev[1]):
                        continue
                    y = (PREV_M, Mf, 0, cls, role, k3s, HS0)
                    if y not in seen:
                        seen.add(y)
                        stack.append(y)
                    nid(y)
                    edges.append((u, node_id[y], wid(prev, Mf, ("MSELF",))))
                continue
            if role == 1:
                for lam in [merge_lam(l1, l2) for l1 in lam_variants(k3s, cur) for l2 in u_lam_variants(prev, cur, None)]:
                    if k3:
                        LAMSTATE[0] = lam
                        try:
                            k3t = k3_step(k3s, prev, cur, None)
                        finally:
                            LAMSTATE[0] = ()
                        if k3t is None:
                            continue
                    if LA.ends_compatible_cls(cls, cur):
                        terms.append((u, wid(prev, cur, wrapw(None, hsin, HS0, lam)), 1))
                continue
            # ---- successors that are S / T vertices
            for nxt in by_bin[cur.bout]:
                if not LA.edge_ok(cur, nxt) or not edge_allow(cur, nxt):
                    continue
                if _TMX and is_m(cur) and nxt.kind == "T":
                    continue         # DIAGNOSTIC (unsound): T directly after an M vertex forbidden (TMX=1)
                if _PAIR and cur.kind == "M" and nxt.kind == "T" and not _pair_ok("MT", cur.bin, cur.bout, cur.h, nxt.bin, nxt.bout, nxt.h):
                    continue
                if cat.enriched and not is_m(cur) and cur.aout != nxt.ain:
                    continue
                for last in (0, 1):
                    if last and nxt.bout != NONE:
                        continue
                    if nxt.kind == "T" and nxt.ub != NONE and not last:
                        continue
                    ni = nxt.info_next(bool(last))
                    for hso in (hs_edge_choices(cur, nxt) if HIDSTATE[0] else [HS0]):
                        for lam in [merge_lam(l1, l2) for l1 in lam_variants(k3s, cur) for l2 in u_lam_variants(prev, cur, ni)]:
                            y = add(u, prev, cur, ni, nxt, last, cls, k3s, False, hso, lam)
                            if y is not None:
                                wkey = ("MEXIT", ni, apex_code(nxt.bin, nxt.ain)) if (is_m(cur) and SPLITM[0]) else wrapw(ni, hsin, hso, lam)
                                edges.append((u, node_id[y], wid(prev, cur, wkey)))
            # ---- successors that are M vertices (entry / exit)
            if use_m and SPLITM[0]:
                for bout, hW in ([] if (_TMX and cur.kind == "T") else itertools.product(BITS4, BITS4)):
                    for last in (0, 1):
                        if last and bout != NONE:
                            continue
                        J = jframe(cur.bout, bout, hW, (0, 0) if is_m(cur) else apex_code(cur.bout, cur.aout))
                        marker = ("MENTRY", bout, bool(last), hW)
                        ni_state = ("T", hW, bout, bool(last), "M")
                        for hso in (hs_m_entry_choices(cur, hW) if HIDSTATE[0] else [HS0]):
                            for lam in [merge_lam(l1, l2) for l1 in lam_variants(k3s, cur) for l2 in u_lam_variants(prev, cur, marker)]:
                                y = add(u, prev, cur, ni_state, J, last, cls, k3s, True, hso, lam)
                                if y is not None:
                                    edges.append((u, node_id[y], wid(prev, cur, wrapw(marker, hsin, hso, lam))))
            elif use_m:
                for bout, hE in itertools.product(BITS4, BITS4):
                    for last in (0, 1):
                        if last and bout != NONE:
                            continue
                        for Mf in mframes(cur.bout, bout, hE):
                            # edge_ok: F-D for S -> M is not restricted (M is multiple)
                            hW = Mf.h[2:]
                            marker = ("MENTRY", bout, bool(last))
                            ni_state = ("T", hW, bout, bool(last), "M")
                            y = add(u, prev, cur, ni_state, Mf, last, cls, k3s, True)
                            if y is not None:
                                edges.append((u, node_id[y], wid(prev, cur, wrapw(marker, hsin, HS0))))
        self.nodes = nodes
        self.N = len(nodes)
        if topology_only:
            print(f"topology: {self.N} nodes, {len(edges)} raw edges, {len(self.win_list)} windows", flush=True)
            self._edges_raw = edges
            return
        _finish_init2(self, edges, terms, starts)


def _finish_init2(self, edges, terms, starts):
    _finish_common(self, edges, terms, starts)


def _finish_common(self, edges, terms, starts):
    """second half of RL.WGraph.__init__ (window options -> sparse matrices, trimming); units and dummy loops for M nodes"""
    from scipy.sparse import csr_matrix
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
    radj = collections.defaultdict(list)
    for (a, b, w) in edges:
        radj[b].append(a)
    co = set(t[0] for t in terms)
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
    self.terms = [(u, w) for (u, w, par) in terms if u in co]
    self.src = np.array([e[0] for e in self.edges], dtype=np.int64)
    self.dst = np.array([e[1] for e in self.edges], dtype=np.int64)
    self.ew = np.array([e[2] for e in self.edges], dtype=np.int64)
    self.tn = np.array([t[0] for t in self.terms], dtype=np.int64)
    self.tw = np.array([t[1] for t in self.terms], dtype=np.int64)
    self._kunits = np.array([units(self.nodes[i][1]) for i in range(self.N)])
    self.mnodes = np.array([i for i in range(self.N) if is_m(self.nodes[i][1]) and i in co and (not SPLITM[0] or self.nodes[i][1].kind == "MP")], dtype=np.int64)
    print(f"graph: {self.N} nodes, {len(self.edges)} edges (trimmed), {len(self.win_list)} windows, {len(ov2)} window options, "
          f"{len(term_list)} terms ({trow} term options), K={self.K} rule columns, M nodes {len(self.mnodes)}, options {time.time() - t0:.1f}s", flush=True)


UNITS["M"] = 3
MCLASS["M"] = 4
UNITS["MP"] = 4
MCLASS["MP"] = 5


# ---------------------------------------------------------------------------------------------------- exact-weight DP with M nodes
def _fast_struct(G):
    """per unit class c0: edges sorted by destination, for np.minimum.reduceat (much faster than np.minimum.at)"""
    st = getattr(G, "_fast", None)
    if st is None:
        ku = G._kunits
        unit_e = ku[G.src]
        st = {}
        for c0 in (1, 2, 3, 4):
            idx = np.nonzero(unit_e == c0)[0]
            if not len(idx):
                continue
            order = idx[np.argsort(G.dst[idx], kind="stable")]
            d = G.dst[order]
            starts = np.flatnonzero(np.r_[True, d[1:] != d[:-1]])
            st[c0] = (order.astype(np.int64), G.src[order].astype(np.int32), G.ew[order].astype(np.int32), starts, d[starts])
        G._fast = st
        G._mset = np.zeros(G.N, dtype=bool)
        G._mset[G.mnodes] = True
    return st


def dummy_weight(G, w, scale):
    """weight of one dummy unit of an M vertex (multiplicity m -> m + 1): the bonus 6(m-3) grows by 6 halves per unit, so the loop costs 6 in v2
    and -3 * 2 * w_alpha through the alpha' column (its count is -v2/2)."""
    ia = G.cat.idx.get(("alpha",))
    return 6.0 * scale - (6.0 * w[ia] if ia is not None and ia < len(w) else 0.0)


def add_dummy_to_counts(G, cnt, nd):
    """cnt = (v2, {col: count}, windows) of the path without its dummy units: add nd dummy units (v2 += 6 each, alpha count -= 3 each)"""
    if not nd:
        return cnt
    v2, d, wins = cnt
    d = dict(d)
    ia = G.cat.idx.get(("alpha",))
    if ia is not None:
        d[ia] = d.get(ia, 0) - 3 * nd
        if not d[ia]:
            del d[ia]
    return (v2 + 6 * nd, d, wins)


def solve_exactw_m(G, w, W, scale=1, tol=1e-9, noise=None):
    """as rule_lp_t25.solve_exactw, unit lengths 1..3 and dummy 1-unit self loops at M nodes (multiplicities >= 5).
    Layered DP with sorted-by-destination reduceat; the path is recovered by backtracking (no parent arrays)."""
    wmin, val = G.window_min(w, scale)
    wsel = wmin if noise is None else wmin + noise
    N = G.N
    INF = 1e30
    ku = G._kunits
    st = _fast_struct(G)
    ewt_o = {c0: wsel[st[c0][2]] for c0 in st}
    dw = dummy_weight(G, w, scale)
    F_ = np.full((W + 1, N), INF)
    F_[0][G.starts] = 0.0
    mn = G.mnodes
    for c in range(W + 1):
        fc = F_[c]
        for c0 in st:
            c2 = c + c0
            if c2 > W:
                continue
            _, src_o, _, starts, udst = st[c0]
            red = np.minimum.reduceat(fc[src_o] + ewt_o[c0], starts)
            tgt = F_[c2]
            tgt[udst] = np.minimum(tgt[udst], red)
        if len(mn) and c + 1 <= W:
            F_[c + 1][mn] = np.minimum(F_[c + 1][mn], fc[mn] + dw)
    uu = ku[G.tn]
    cc = W - uu
    okt = cc >= 0
    tn_, tw_, cc_ = G.tn[okt], G.tw[okt], cc[okt]
    tot = F_[cc_, tn_] + wsel[tw_]
    k = int(np.argmin(tot))
    if tot[k] >= INF / 2:
        return None, "none", None
    bestv, bnode, bc, bw = float(tot[k]), int(tn_[k]), int(cc_[k]), int(tw_[k])
    edges = []
    x, c = bnode, bc
    nd = 0
    while c > 0:
        fx = F_[c][x]
        if G._mset[x] and F_[c - 1][x] + dw == fx:
            c -= 1
            nd += 1
            continue
        found = None
        for c0 in st:
            if c - c0 < 0:
                continue
            order, src_o, _, starts, udst = st[c0]
            j = np.searchsorted(udst, x)
            if j >= len(udst) or udst[j] != x:
                continue
            lo = starts[j]
            hi = starts[j + 1] if j + 1 < len(starts) else len(order)
            cand = F_[c - c0][src_o[lo:hi]] + ewt_o[c0][lo:hi]
            hit = np.flatnonzero(cand <= fx)
            if len(hit):
                found = (int(order[lo + hit[0]]), c0)
                break
        e, c0 = found
        edges.append(e)
        c -= c0
        x = int(G.src[e])
    edges = edges[::-1]
    cnt = add_dummy_to_counts(G, G._counts(edges, wmin, val, extra_window=bw), nd)
    if noise is not None:
        bestv = float(sum(wmin[i] for i in cnt[2]) + nd * dw)
    return float(bestv), "path", cnt


def solve_exactw_m_slow(G, w, W, scale=1, tol=1e-9, noise=None):
    """as rule_lp_t25.solve_exactw, unit lengths 1..3 and dummy 1-unit self loops at M nodes (multiplicities >= 5)"""
    wmin, val = G.window_min(w, scale)
    wsel = wmin if noise is None else wmin + noise
    ewt = wsel[G.ew]
    N = G.N
    INF = 1e18
    ku = G._kunits
    unit_e = ku[G.src]
    F_ = np.full((W + 1, N), INF)
    Pe = np.full((W + 1, N), -1, dtype=np.int64)
    F_[0][G.starts] = 0.0
    m_by = {c0: np.nonzero(unit_e == c0)[0] for c0 in (1, 2, 3, 4)}
    mn = G.mnodes
    dw = dummy_weight(G, w, scale)
    for c in range(W + 1):
        fc = F_[c]
        for c0 in (1, 2, 3, 4):
            c2 = c + c0
            if c2 > W or len(m_by[c0]) == 0:
                continue
            m = m_by[c0]
            fs = fc[G.src[m]]
            ok = fs < INF
            if not ok.any():
                continue
            m = m[ok]
            cand = fs[ok] + ewt[m]
            best = F_[c2].copy()
            np.minimum.at(best, G.dst[m], cand)
            imp = best < F_[c2] - tol
            if imp.any():
                sel = m[cand <= best[G.dst[m]] + 1e-12]
                sel = sel[imp[G.dst[sel]]]
                Pe[c2][G.dst[sel]] = sel
                F_[c2] = np.where(imp, best, F_[c2])
        if len(mn) and c + 1 <= W:
            cand = fc[mn] + dw
            better = cand < F_[c + 1][mn] - tol
            if better.any():
                idx = mn[better]
                F_[c + 1][idx] = cand[better]
                Pe[c + 1][idx] = -2
    bestv, bnode, bc, bw = INF, None, None, None
    for u_, wi in zip(G.tn, G.tw):
        uu = int(ku[u_])
        c = W - uu
        if c < 0:
            continue
        v = F_[c][u_]
        if v < INF and v + wsel[wi] < bestv:
            bestv, bnode, bc, bw = v + wsel[wi], int(u_), c, int(wi)
    if bnode is None:
        return None, "none", None
    edges = []
    x, c = bnode, bc
    nd = 0
    while c > 0:
        e = int(Pe[c][x])
        if e == -2:
            c -= 1
            nd += 1
            continue
        edges.append(e)
        c -= int(unit_e[e])
        x = int(G.src[e])
    edges = edges[::-1]
    cnt = add_dummy_to_counts(G, G._counts(edges, wmin, val, extra_window=bw), nd)
    if noise is not None:
        bestv = float(sum(wmin[i] for i in cnt[2]) + nd * dw)
    return float(bestv), "path", cnt


def install_all(use_mult=True):
    install_mult()
    T.solve_exactw = lambda *a, **k: solve_exactw_m(*a, **k)


def min_by_units_m(G, wint, D, umax):
    """independent layered DP: min over paths with exactly u units (u <= umax) of D*v2 + 2 w.counts, for every u; dummy 1-unit loops at M nodes"""
    wmin, val = G.window_min(wint, D)
    ewt = wmin[G.ew]
    N = G.N
    INF = 1e18
    ku = G._kunits
    F_ = np.full((umax + 1, N), INF)
    F_[0][G.starts] = 0.0
    dw = dummy_weight(G, wint, D)
    for c in range(umax + 1):
        for c0 in (1, 2, 3, 4):
            if c + c0 > umax:
                continue
            m = (ku[G.src] == c0) & (F_[c][G.src] < INF)
            np.minimum.at(F_[c + c0], G.dst[m], F_[c][G.src[m]] + ewt[m])
        if len(G.mnodes) and c + 1 <= umax:
            F_[c + 1][G.mnodes] = np.minimum(F_[c + 1][G.mnodes], F_[c][G.mnodes] + dw)
    res = {}
    for u_, wi in zip(G.tn, G.tw):
        uu = int(ku[u_])
        for c in range(0, umax + 1 - uu):
            v = F_[c][u_] + wmin[wi]
            if F_[c][u_] < INF and v < res.get(c + uu, INF):
                res[c + uu] = float(v)
    return res


def window_sigsets_m(G, wins, w):
    """T.window_sigsets that understands the hidden-state wrapper ("HS", inner, hs_in, hs_out) of the window key"""
    out = []
    for wi in wins:
        prev, cur, nxt = G.win_list[wi]
        if cur.kind != "T":
            out.append(None)
            continue
        hs = None
        if nxt is not None and nxt[0] == "HS":
            hs, nxt = (nxt[2], nxt[3], nxt[4] if len(nxt) > 4 else ()), nxt[1]
        G.cat._hs = hs
        try:
            if nxt is not None and nxt[0] == "MENTRY":
                opts = []
                for hW in LA.BITS:
                    opts += G.cat.sig_options(prev, cur, ("T", hW, nxt[1], nxt[2], "M"))
            else:
                opts = G.cat.sig_options(prev, cur, nxt)
        finally:
            G.cat._hs = None
        vals = [T.option_value(o_, w) for (_, _, o_) in opts]
        m = min(vals) if vals else 0
        out.append([sg for (sg, _, _), vv in zip(opts, vals) if vv <= m + 1e-7])
    return out


SAVEW = [False]       # --savew: every path cut remembers the weight vector it was found with (hidden choices of the DP can be recomputed: T29 witness CEGAR)


def dump_cuts_m(G, cuts, path):
    """T.dump_cuts plus the per-cut weight vector (key 'w', in the column order of G.cat.keys; 'wkeys' once at the top of the first cut)"""
    dump = T.dump_cuts(G, cuts, None)
    for d, c in zip(dump, cuts):
        if len(c) > 6 and c[6] is not None:
            d["w"] = c[6]
    if dump and SAVEW[0]:
        dump[0]["wkeys"] = [repr(k) for k in G.cat.keys]
    if path:
        import json as _json
        _json.dump(dump, open(path, "w"))
    return dump


# ---------------------------------------------------------------------------------------------------- LP loop with parallel diverse cuts
_PG = {}


def _par_worker(args):
    w, seed, amp, W, tgt = args
    rng = np.random.RandomState(seed)
    G = _PG["G"]
    nz = rng.uniform(0, amp, len(G.win_list))
    v, kind, cnt = solve_exactw_m(G, w, W, noise=nz)
    if v is None or v >= tgt - 1e-9:
        return None
    return v, cnt


def lp_loop_par(G, W, wmax=100.0, max_it=3000, extra_cuts=None, time_limit=None, target=2.0, G2=None, target2=None, npar=6, tag="", center=False):
    """rule_lp_t25.lp_loop_exactw + npar noisy DPs per iteration in worker processes (fork; the graph is shared copy-on-write); every violated
    diverse path becomes an extra cut (same LP rows, the cut list is deduplicated by window sequence)"""
    import multiprocessing as mp
    from scipy.optimize import linprog
    K = G.K
    cuts = list(extra_cuts or [])
    seen = set()
    w = np.zeros(K)
    bounds = T.col_bounds(G, wmax)
    rrows = T.ring_rows_matrix(G, K)
    xrows = []
    for (coefs, rhs) in getattr(G.cat, "extra_rows", []):
        xr = {G.cat.idx[k]: x for k, x in coefs.items() if k in G.cat.idx}
        xrows.append((xr, rhs))
    _fast_struct(G)
    _PG["G"] = G
    pool = mp.get_context("fork").Pool(npar) if npar > 0 else None
    amps = [0.25, 0.5, 1.0, 2.0, 3.0, 0.75, 1.5, 4.0]
    t_start = time.time()
    seed = 0
    try:
        for it in range(max_it):
            t0 = time.time()
            v, kind, cnt = solve_exactw_m(G, w, W)
            v2_, kind2, cnt2 = (solve_exactw_m(G2, w, W) if G2 is not None else (None, None, None))
            if v is None:
                print("no path of that weight")
                return w, cuts
            viol1 = v < target - 1e-9
            viol2 = G2 is not None and v2_ is not None and v2_ < target2 - 1e-9
            if it % 5 == 0 or not (viol1 or viol2):
                print(f"{tag}it {it:3d} DP min (2*final+2) = {v:9.4f}" + (f" clean {v2_:9.4f}" if v2_ is not None else "") +
                      f", len {len(cnt[2])}, cuts {len(cuts)}, |w|_1 = {w.sum():.3f}, {time.time() - t0:.1f}s", flush=True)
                if it % 25 == 0 and it:
                    top = np.argsort(-w)[:8]
                    print("      top columns:", "; ".join(f"{str(G.cat.keys[i])[:60]}={w[i]:.2f}" for i in top if w[i] > 1e-9), flush=True)
            if not (viol1 or viol2) and (it > 0 or not rrows):
                return w, cuts
            if viol1:
                cuts.append(cnt + ("path", window_sigsets_m(G, cnt[2], w), target, [round(float(x), 6) for x in w] if SAVEW[0] else None))
                seen.add(tuple(cnt[2]))
                if pool is not None:
                    tasks = []
                    for j in range(npar):
                        seed += 1
                        tasks.append((w, seed, amps[j % len(amps)], W, target))
                    for r in pool.map(_par_worker, tasks):
                        if r is None:
                            continue
                        key = tuple(r[1][2])
                        if key in seen:
                            continue
                        seen.add(key)
                        cuts.append(r[1] + ("path", window_sigsets_m(G, r[1][2], w), target, [round(float(x), 6) for x in w] if SAVEW[0] else None))
            if viol2:
                cnt2 = (cnt2[0], cnt2[1], [G2.win_list[wi] for wi in cnt2[2]])
                cuts.append(cnt2 + ("path", None, target2))
            A = np.zeros((len(cuts) + len(rrows) + len(xrows), K))
            b = np.zeros(len(cuts) + len(rrows) + len(xrows))
            for i, cut in enumerate(cuts):
                v2, d = cut[0], cut[1]
                for c, x in d.items():
                    A[i, c] = -2.0 * x
                b[i] = v2 - (cut[5] if len(cut) > 5 else target)
            for j, r in enumerate(rrows):
                for c, x in r.items():
                    A[len(cuts) + j, c] = x
            for j, (xr, rhs) in enumerate(xrows):
                for c, x in xr.items():
                    A[len(cuts) + len(rrows) + j, c] = x
                b[len(cuts) + len(rrows) + j] = rhs
            if center:
                # Chebyshev-type centre: maximise the margin t of the cut rows (t <= 1), tiny penalty on sum w; infeasible iff t* < 0
                nrm = np.linalg.norm(A, axis=1)
                A2 = np.hstack([A, nrm[:, None]])
                c2 = np.concatenate([1e-3 * np.ones(K), [-1.0]])
                res = linprog(c2, A_ub=A2, b_ub=b, bounds=list(bounds) + [(-50.0, 1.0)], method="highs")
                if res.status != 0 or res.x[-1] < -1e-9:
                    print(f"{tag}LP infeasible after {len(cuts)} cuts (margin {None if res.status != 0 else res.x[-1]})")
                    return None, cuts
                w = res.x[:K]
                if it % 5 == 0:
                    print(f"      margin t = {res.x[-1]:.4f}", flush=True)
            else:
                cvec = np.ones(K)
                for k_, c_ in OBJ.items():
                    if k_ in G.cat.idx: cvec[G.cat.idx[k_]] = c_
                res = linprog(cvec, A_ub=A, b_ub=b, bounds=bounds, method="highs")
                if res.status != 0:
                    print(f"{tag}LP infeasible after {len(cuts)} cuts")
                    return None, cuts
                w = res.x
            if time_limit and time.time() - t_start > time_limit:
                print(f"{tag}time limit")
                return "timeout", cuts
        return w, cuts
    finally:
        if pool is not None:
            pool.terminate()



# ---------------------------------------------------------------------------------------------------- driver
def f4p_edge_allow_m(c, n):
    """F4' only when the apex of the capped triangle is EXACTLY triple (apex class 1); a multiplicity >= 4 apex (class 3) is allowed"""
    if c.kind == "S" and n.kind == "S":
        for s_ in (0, 1):
            if c.bin[s_] and c.bout[s_] and n.bout[s_] and c.aout[s_] != 3:
                return False
    return True


def build_graph_m(o, cat=None, onlyclean=None, tmode=None, mpath=False):
    T.enable_t1pp(True)
    install_all()
    rings = None
    if o.cls == "C2":
        rings = T.C2_RINGS.split(",")
    elif o.cls != "full":
        rings = o.cls.split(",")
    pset = T.facts_pattern_set() if o.facts else None
    if getattr(o, "pats", None):
        pset = load_mpats(o.pats)
        print(f"forbidden patterns: {len(pset.pats)} (with symmetric variants)", flush=True)
    if GUARD[0]:
        fp = [(a, tuple(tuple(q) + ("G",) for q in ps)) for a, ps in T.facts_pattern_set().pats]
        old_ps = pset
        pset = MPatternSet(list(fp) + (list(pset.pats) if pset is not None else []))
        if old_ps is not None and (old_ps.labs or old_ps.zeros):
            pset.labs = {(j_ + len(fp), i_): v_ for (j_, i_), v_ in old_ps.labs.items()}
            pset.zeros = {(j_ + len(fp), i_): v_ for (j_, i_), v_ in old_ps.zeros.items()}
        print(f"guarded patterns: {len(fp)} T23 facts + {len(pset.pats) - len(fp)} CEGAR patterns", flush=True)
    cat = cat if cat is not None else FCatalogueM2(
        enriched=True, rings=rings, k1=not o.nok1, k2=not o.nok2, k2g=(o.k2g and not o.nok2g), celldom=o.celldom, split_a=o.split, alpha=o.alpha,
        W=o.exactw, afix=None if o.afix is None else float(F(o.afix)), proj=[x for x in o.proj.split(",") if x], wr=o.wr, sv=o.sv, tri=o.tri, pt=o.pt)
    if getattr(o, "cellrm", None):
        import json as _json
        rm = {}
        for fn in o.cellrm.split(","):
            for line in open(fn):
                row = _json.loads(line)
                if row["removed"]:
                    rm.setdefault(row["key"], set()).update(tuple(tuple(c) for c in combo) for combo in row["removed"])
        cat.cell_removed = rm
        print(f"cell filter: {sum(len(v) for v in rm.values())} joint completions removed in {len(rm)} groups", flush=True)
    if getattr(o, "projall", None):
        cat.projall = True if o.projall == "all" else frozenset(o.projall.split(","))
    if getattr(o, "projc", None):
        cat.projc = frozenset(x for x in o.projc.split(",") if x)
    if getattr(o, "axisfile", None):
        import pickle as _pk
        cat.celldom = True
        cat.axis_cells = _pk.load(open(o.axisfile, "rb"))
        print(f"celldom with the multiplicity axis-cell set ({len(cat.axis_cells)} cells)", flush=True)
    MPSET[0] = pset if (pset is not None and getattr(pset, 'labs', None)) else None
    T.install_combined_step(not o.nok3, pset, f5=(o.f5 and not o.nof5), noclean=o.noclean, onlyclean=(o.onlyclean if onlyclean is None else onlyclean),
                            tmode=(o.tmode if tmode is None else tmode))
    if mpath:
        # only paths with at least one M frame: flag kept in the last component of the combined-step state (unused otherwise)
        step0 = RL.k3_step

        def step_m(state, prev, cur, ni):
            new = step0(state, prev, cur, ni)
            if new is None:
                return None
            fl = (0 if state == (0, 0) else state[6]) or int(is_m(cur))
            if ni is None and not fl:
                return None
            return new[:6] + (fl,)
        RL.k3_step = step_m
    if UUB[0]:
        RL.k3_step = make_uub_step(RL.k3_step)
    ea = f4p_edge_allow_m if not o.nof4p else (lambda c, n: True)
    G = WGraphM2(cat, edge_allow=ea, k3=True, use_m=not (o.nomult or onlyclean or o.onlyclean))   # clean paths (FD graph) never contain an M vertex
    print("catalogue stats:", dict(cat.stats), flush=True)
    return G


def add_m_args(ap):
    """T.add_args + the multiplicity options; defaults: all facts on (as rule_lp_t25.py)"""
    ap = T.add_args(ap)
    ap.add_argument("--nomult", action="store_true", help="no M vertices on L (apex classes 1/2/3 kept unless --noapex3)")
    ap.add_argument("--par", type=int, default=0, help="extra noisy DPs per iteration in worker processes (fork)")
    ap.add_argument("--gift", type=float, default=0.0, help="experiment: free credit to the caps of blocks with a >=4-fold apex (NOT a certificate)")
    ap.add_argument("--mb", action="store_true", help="MB cells: axis <-> cap transfers for blocks with a >= 4-fold apex")
    ap.add_argument("--splitm", action="store_true", help="exactly 4-fold (M) and >= 5-fold (MP) vertices apart, hW in the node, PT4 cells at M")
    ap.add_argument("--center", action="store_true", help="LP: maximise the margin of the cuts (Chebyshev centre) instead of minimising sum w (fewer cutting-plane rounds)")
    ap.add_argument("--mcredit", default=None, help="T26-style credits at the bad 4-fold points: columns TAU(word, role) >= 0 with sum over the 4 lines >= DELTA (fraction); path: final >= -eps0 - eps1*nM + sum tau")
    ap.add_argument("--eps1", default=None, help="'var': per-M4-incidence relaxation eps1 as an LP column, 4 eps1 + 18 eps0 <= delta - margin (needs --mcredit)")
    ap.add_argument("--eps1margin", default="0", help="margin in 4 eps1 + 18 eps0 <= delta - margin (fraction)")
    ap.add_argument("--mvar", action="store_true", help="eps0 and delta as LP columns (credit version, T <= 93 via sum final >= delta - 18 eps0 > 0)")
    ap.add_argument("--mvarmargin", default="0", help="row delta - 18 eps0 >= margin (fraction)")
    ap.add_argument("--mvarobj", type=float, default=0.0, help="objective: minimise sum w - OBJ*(delta - 18 eps0) (maximise the margin)")
    ap.add_argument("--guarded", action="store_true", help="guarded K1*, K2, K2g, celldom (T windows only) and the T23 patterns P000-P009: each fires only where every apex / vertex it mentions is exactly triple or simple")
    ap.add_argument("--star", default=None, choices=["F2", "F3", "full"], help="star keys at the bad 4-fold points (PT4N): classes of the first vertices on the 8 rays (F = full triple, H = one non-triangle sector, S simple, O other triple, M 4-fold); F2 keeps F / other, F3 F / H / other")
    ap.add_argument("--mstrict", default=None, help="require final >= this fraction on every path with at least one M4 frame (second DP, same columns)")
    ap.add_argument("--pats", default=None, help="json of forbidden frame patterns (SAT cores, work/eng/T27/cegar_m.py)")
    ap.add_argument("--warmdump", default=None, help="json cut dump (with windows) used as initial cuts; cuts whose frames match a forbidden pattern are dropped")
    ap.add_argument("--cellrm", default=None, help="jsonl files of cells_sweep_m.py: joint flank completions refuted by pattern SAT are removed")
    ap.add_argument("--projall", nargs="?", const="all", default=None, help="block-rule pairs use only the cell features visible to both parties: 'all' or a list of pair types AC,AL,LR,LC (AL = axis-flank, LC = flank-cap)")
    ap.add_argument("--projc", default=None, help="cell features dropped from the keys of the transfers involving the cap (ring, oth0, u, p, t): the cap sees its key exactly")
    ap.add_argument("--axisfile", default=None, help="pickle of the axis-visible cells over all multiplicity windows (axis_cells_m.py): turns celldom on soundly")
    ap.add_argument("--savew", action="store_true", help="remember the weight vector of every path cut in the dump (key w)")
    ap.add_argument("--hidm", action="store_true", help="(needs --hidstate) the F4 tag across T - M adjacencies: pO = 1 forces f2[s] = 1 of the exactly 4-fold neighbour")
    ap.add_argument("--uub", action="store_true", help="T29 U-UB lemma: a flank completion u = 1 (axis ends at X) forbids ub flags on the opposite side except at the cap neighbour Y1")
    ap.add_argument("--dumpall", action="store_true", help="also dump the cuts when the LP is feasible (for dual analysis)")
    ap.add_argument("--hidstate", action="store_true", help="T29 hidden state along the line: F4 link (the far face of the simple apex of a segment triangle, seen by the flank cells of both end vertices, is one bit carried on the edge)")
    ap.add_argument("--allm", action="store_true", help="do NOT apply the perturbation reduction (keep every M4 pattern and the m >= 5 frames)")
    ap.add_argument("--noapex3", action="store_true", help="no >= 4-fold triangle apexes either: with --nomult this must reproduce FC exactly")
    ap.add_argument("--usef5", action="store_true", help="switch F5* on (multiplicity-free proof; needed for the clean-path target FD24)")
    ap.add_argument("--unsafe-facts", action="store_true", help="switch K1*, K2, K2g and F5* back on (they are NOT valid with >= 4-fold points: work/eng/T27/facts_scan.py)")
    ap.set_defaults(nok1=True, nok2=True, nok2g=True, nof4p=False, nof5=True)
    return ap


def apply_m_opts(o):
    if getattr(o, "guarded", False):
        GUARD[0] = True
        o.nok1 = o.nok2 = False
        o.nok2g = True           # K2g needs the apex flags of the NEXT triple vertex's triangles, invisible in the window: 4 real lines of 543k contradict it
        o.celldom = not _os.environ.get("NOCELLDOM")     # env NOCELLDOM=1 (lead): guarded facts without the SAT-derived cell domains
        o.nof5 = False           # F5* (Blanc step 5, multiplicity-free): 0 violations on 543k real lines incl. dirty
    if o.usef5:
        o.nof5 = False
    if o.unsafe_facts:
        o.nok1 = o.nok2 = o.nok2g = o.nof5 = False
    if o.noapex3:
        APEX_CLASSES[0] = (1, 2)
    GIFT[0] = o.gift
    HIDM[0] = bool(getattr(o, "hidm", False)) or bool(_os.environ.get("HIDM"))
    UUB[0] = bool(getattr(o, "uub", False)) or bool(_os.environ.get("UUB"))
    SAVEW[0] = bool(getattr(o, "savew", False))
    HIDSTATE[0] = bool(getattr(o, "hidstate", False)) or bool(_os.environ.get("HIDSTATE"))
    MB[0] = o.mb
    SPLITM[0] = o.splitm
    BADONLY[0] = not o.allm
    if getattr(o, "star", None):
        STAR[0] = o.star
    if getattr(o, "mvar", False):
        MVAR[0] = True
        MVARMARGIN[0] = F(o.mvarmargin)
        if o.mvarobj:
            OBJ[("DELTA",)] = -o.mvarobj
            OBJ[("EPS0",)] = 18 * o.mvarobj
            if _os.environ.get("EPSX") and _os.environ.get("MARGINOBJ"):
                OBJ[("EPSM",)] = 4 * o.mvarobj      # T29: objective = exact margin delta - 18 eps0 - 4 epsM - 8 epsA (env MARGINOBJ=1)
                OBJ[("EPSA",)] = 8 * o.mvarobj
    if getattr(o, "mcredit", None) is not None:
        MCRED[0] = F(o.mcredit)
        EPS0[0] = -3 * F(o.eps)
        EPS1MARGIN[0] = F(o.eps1margin)
        if o.eps1 == "var":
            EPS1[0] = "var"


def warm_cuts(G, o):
    cuts = []
    if o.warm:
        cuts += T.load_warm_cuts(G, o.warm)
    if getattr(o, "warmdump", None):
        cuts += load_warm_filtered(G, o.warmdump, load_mpats(o.pats) if o.pats else None)
    return cuts or None


def main():
    import argparse
    ap = add_m_args(argparse.ArgumentParser())
    o = ap.parse_args()
    apply_m_opts(o)
    G = build_graph_m(o, tmode=("lt2" if o.tcredit is not None else None))
    target = T.target_of(o)
    if o.cmd == "base":
        v, kind, cnt = solve_exactw_m(G, np.zeros(G.K), o.exactw)
        print("w=0:", v, kind)
        print(RL.show_path(G, cnt))
    elif o.cmd == "lp":
        E = float(3 * F(o.eps)) if o.tau else 0.0
        G2 = target2 = None
        if o.mstrict is not None:
            G2 = build_graph_m(o, cat=G.cat, mpath=True)
            target2 = float(2 + 2 * F(o.mstrict))
        if o.cleandelta is not None:
            G2 = build_graph_m(o, cat=G.cat, onlyclean=True)
            target2 = float(2 + 2 * F(o.cleandelta))
        if o.tcredit is not None:
            G2 = build_graph_m(o, cat=G.cat, tmode="ge2")
            target2 = float(2 + 6 * F(o.tcredit))
        if G2 is not None:
            Km = len(G.cat.keys)
            T.pad_K(G, Km)
            T.pad_K(G2, Km)
        if o.par:
            w, cuts = lp_loop_par(G, o.exactw, o.wmax, o.iters, extra_cuts=warm_cuts(G, o), time_limit=o.time_limit,
                                  target=target + o.margin, G2=G2, target2=target2, npar=o.par, center=o.center)
        else:
            w, cuts = T.lp_loop_exactw(G, o.exactw, o.wmax, o.iters, time_limit=o.time_limit, target=target + o.margin, E=E, G2=G2, target2=target2,
                                        extra_cuts=(T.load_warm_cuts(G, o.warm) if o.warm else None))
        if w is None:
            dump = dump_cuts_m(G, cuts, o.dump)
            if o.core:
                xr = [({repr(k): x for k, x in coefs.items()}, rhs) for coefs, rhs in getattr(G.cat, "extra_rows", [])]
                idx = T.min_core(dump, o.wmax, target, xr)
                print("core size", len(idx), "of", len(dump), "cuts:", idx)
        elif isinstance(w, str):
            print("timeout")
            T.dump_cuts(G, cuts, o.dump)
        else:
            if getattr(o, "dumpall", False) and o.dump:
                dump_cuts_m(G, cuts, o.dump)
            T.col_bounds.__defaults__ = (float(o.wmax),)          # T29: the rationalisation must accept weights up to --wmax (the default box of col_bounds is 100)
            _dens = tuple(int(x) for x in _os.environ["DENS"].split(",")) if _os.environ.get("DENS") else (1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 36, 48, 60, 72, 96, 120, 144, 180, 240, 288, 360, 480, 720, 960, 1440, 2880)
            D, wint, v = T.rationalize_exactw(G, w, o.exactw, target, E=(3 * F(o.eps) if o.tau else 0), dens=_dens)
            print("exact certificate:", "denominator", D, "DP min (D*(2*final+2)) =", v, "target", None if D is None else target * D)
            if D is not None:
                w = wint / D
                mb = min_by_units_m(G, wint, D, o.exactw)
                print("verify (bounded): min D*(2*final+2) per n-1:", {u: mb[u] for u in sorted(mb)}, "target", target * D)
                if G2 is not None:
                    v2_, _, _ = solve_exactw_m(G2, wint, o.exactw, scale=D)
                    print("second graph DP min", v2_, "target", target2 * D)
                if o.export:
                    T.export_rules_t25(G, wint, D, o.export)
            if o.save:
                import pickle
                pickle.dump({G.cat.keys[i]: float(w[i]) for i in range(len(w)) if w[i] > 1e-9}, open(o.save, "wb"))


if __name__ == "__main__":
    main()

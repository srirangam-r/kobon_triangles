"""Line automaton for arrangements with points of ANY multiplicity m >= 3 (task T22; extends search/line_automaton.py).

Everything of T20 is kept (frames S = simple vertex, T = triple point, window weights, adversarial hidden variables,
min-plus DP with negative-cycle detection); a new frame kind M is added for m-fold points, m >= 4.  Reference values:
search/bbl_hallm.py (`Multi`, `values`): an m-fold point has 2m rays, N / B / R statuses as before, ray split +-3/2,
bonus 3(m-3) to each of its m lines, T1 (3/2 per N gap ray) and F (1 per N flank ray) with "triple" read as "multiple".

Frame M (m-fold vertex seen from L, m >= 4).  Ring of the 2m rays:  E, +1, ..., +(m-1), W, -(m-1), ..., -1.  Sector s^sigma_j
lies between the rays sigma*j and sigma*(j+1) (sigma = +-, j = 0..m-1, sigma*0 = E, sigma*m = W).  The frame is
    (bin, bout, hE, hW):  bout = (s+_0, s-_0), bin = (s+_{m-1}, s-_{m-1}),  hE = (s+_1, s-_1),  hW = (s+_{m-2}, s-_{m-2}).
Only these bits are visible to the window; the middle sectors and the middle rays are hidden.  A neighbour sees only
(kind, adjacent hidden sector bits, bits beyond) exactly as for triple points, so the multiplicity of the neighbour is
irrelevant.  The E side (bout, next vertex, hE, hidden far ends of the rays +-1 and +-2) and the W side (bin, previous
vertex, hW, rays +-(m-1) and +-(m-2)) are relaxed to be INDEPENDENT (a sound over-approximation, see REPORT.md); the
multiplicity m enters only through the bonus 6(m-3) (in halves) and the parity of m-1, so m >= 6 is dominated by m-2 and
the classes m = 4, 5 (and, as a check, 6, 7) cover every multiplicity.

    python search/line_automaton_m.py gen <base.jsonl>... --out F   # arrangements with 4-, 5-, 6-fold points (push_through + flips)
    python search/line_automaton_m.py genrand --out F               # random wiring words with multiple points of every multiplicity
    python search/line_automaton_m.py validate <in>... [--odd] [--minmult 4]   # every line is an automaton path; quantities == bbl_hallm
    python search/line_automaton_m.py sidecheck <in>...             # M side model applied to TRIPLE vertices == T20 exact vectors
    python search/line_automaton_m.py mutants <in>...               # planted errors must be detected by validate
    python search/line_automaton_m.py m1 | m2 | crosscheck | datamin <in>...
Logs of the runs reported in work/eng/T22/REPORT.md are in work/eng/T22/.
"""
import collections
import itertools
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import line_automaton as LA  # noqa: E402
from line_automaton import BITS, NONE  # noqa: E402

# ---------------------------------------------------------------------------------------------- vector layout
# vec = (p, v2, RN3, RR3, RNM, BNM, RRM, RBM, BBM, nT, nM)
#   p    portions of L;  v2 = 2 (v_L + 1)  (halves; includes the bonus 6(m-3) of every m-fold vertex)
#   unserved blocks with axis L, by the apex multiplicity (3 or >= 4) and by the flank types (N / R / B):
#   RN3 / RR3 : apex triple, exactly one / two flanks non-N (flanks are R: B flanks are impossible at a triple point)
#   RNM = (R,N), BNM = (B,N), RRM = (R,R), RBM = (R,B), BBM = (B,B) : apex of multiplicity >= 4
P_, V2, RN3, RR3, RNM, BNM, RRM, RBM, BBM, NT3, NMF = range(11)
NV = 11
VNAMES = ["p", "v2", "RN3", "RR3", "RNM", "BNM", "RRM", "RBM", "BBM", "nT", "nM"]


def objective(v2=1, a3=0, b3=0, aM=0, bM=0, p=0, nT=0, nM=0):
    """objective in halves: v2 + a3*#RN3 + b3*#RR3 + aM*#(M block, one non-N flank) + bM*#(M block, two non-N flanks)"""
    o = [0] * NV
    o[P_], o[V2], o[RN3], o[RR3] = p, v2, a3, b3
    o[RNM] = o[BNM] = aM
    o[RRM] = o[RBM] = o[BBM] = bM
    o[NT3], o[NMF] = nT, nM
    return tuple(o)


class MFrame(collections.namedtuple("MFrame", "kind bin bout ub h")):
    """m-fold vertex (m >= 4): h = (s+_1, s-_1, s+_{m-2}, s-_{m-2}) = (hE+, hE-, hW+, hW-); ub is always NONE"""
    __slots__ = ()

    def info_prev(self, first=False):     # what the NEXT vertex needs about this predecessor: sectors adjacent to E, bits before
        return ("T", (self.h[0], self.h[1]), self.bin, first)

    def info_next(self, last=False):      # what the PREVIOUS vertex needs about this successor: sectors adjacent to W, bits after
        return ("T", (self.h[2], self.h[3]), self.bout, last)


def all_frames_m(m_frames=True, t3_frames=True):
    """S frames and triple frames of T20 (triple frames without ub flags) plus the M frames"""
    out = [f for f in LA.all_frames() if f.kind == "S" or (t3_frames and f.ub == NONE)]
    if m_frames:
        for bi, bo, a, c in itertools.product(BITS, BITS, BITS, BITS):
            out.append(MFrame("M", bi, bo, NONE, a + c))
    return out


def mult_of(f):
    return 2 if f.kind == "S" else 3 if f.kind == "T" else 4


def parity_of(f, mc):
    """parity of (m - 1): the number of other lines at the vertex, so that sum over L = n - 1"""
    return 1 if f.kind == "S" else 0 if f.kind == "T" else (mc - 1) % 2


# ---------------------------------------------------------------------------------------------- side model of an M vertex
MUT = None      # name of a planted mutation (tests only): `python line_automaton_m.py mutants <in>...`


def ray_stat(bits, other):
    if bits != (1, 1):
        return "N"
    return "B" if other[0] == "S" else "R"


def side_domain(bits, other, full_g=False):
    """hidden assignments (f1, f2, g) of one side of an M vertex.  f1[s] : the far end of the ray s*1 (resp. s*(m-1) on the
    W side) is a multiple point, f2[s] : the same for the ray s*2 (s*(m-2)), g[s] : the gap ray at that far end is N.
    F3': the triangle above the segment next to L (bit bits[s]) has apex Y = far end of the ray s*1; if the next vertex X is
    simple and the face beyond C at X is a triangle too (other[2][s]), the segment [X,Y] is doubly used with a simple end X,
    so Y is multiple."""
    forced = [0, 0]
    if other is not None and other[0] == "S":
        for s in (0, 1):
            if (bits[s] or MUT == "forced_always") and other[2][s]:
                forced[s] = 1
    for f1 in itertools.product((0, 1), repeat=2):
        if any(forced[s] and not f1[s] for s in (0, 1)):
            continue
        for f2 in itertools.product((0, 1), repeat=2):
            for g in (itertools.product((0, 1), repeat=2) if full_g else [(0, 0)]):
                yield f1, f2, g


def side_vec(bits, other, a, hid):
    """contribution to the vector of ONE side (ray E with bits=bout, other=next; or ray W with bits=bin, other=prev)"""
    f1, f2, g = hid
    v = [0] * NV
    st = ray_stat(bits, other)
    if MUT == "R_costs" and st == "R":
        v[V2] -= 3
    if st == "N":
        v[V2] += 3
        for s in (0, 1):
            if bits[s] and a[s] and (not f1[s] or MUT == "count_R_as_block"):   # ray s*1 is a block; this N ray flanks it, pays 1 unless served
                served = other is not None and other[0] == "T" and (f2[s] == 1 or MUT == "served_ignores_f2") and ((not other[1][s]) or g[s])
                if not served:
                    v[V2] -= 1 if MUT == "flank_pay_1" else 2
    elif st == "B":
        v[V2] -= 3
        nb = other[2]
        if MUT == "T1_one_flanker":
            got = 3 * ((nb[0] == 0) + (nb[1] == 0)) if (f1[0] or f1[1]) else 0
        elif MUT == "T1_gain_2":
            got = 2 * ((nb[0] == 0) + (nb[1] == 0)) if (f1[0] and f1[1]) else 0
        else:
            got = 3 * ((nb[0] == 0) + (nb[1] == 0)) if (f1[0] and f1[1]) else 0
        if got > 0:
            v[V2] += got                                # T1: served, no F
        else:                                           # F: 1 per N flank ray; unserved block
            v[V2] += (1 if MUT == "F_gain_1" else 2) * ((not a[0]) + (not a[1]))
            ty = sorted("N" if not a[s] else ("B" if not f1[s] else "R") for s in (0, 1))
            key = "".join(ty)
            idx = {"NN": None, "NR": RNM, "BN": BNM, "RR": RRM, "BR": RBM, "BB": BBM}[key]
            if MUT == "swap_RN_BN" and idx in (RNM, BNM):
                idx = BNM if idx == RNM else RNM
            if idx is not None:
                v[idx] += 1
    return v


def side_event(bits, other, a, hid):
    """label of what happens on one side of an M vertex (coverage statistics of the validation)"""
    f1, f2, g = hid
    st = ray_stat(bits, other)
    if st == "R":
        return "R"
    if st == "N":
        ev = []
        for s in (0, 1):
            if bits[s] and a[s] and not f1[s]:
                served = other is not None and other[0] == "T" and f2[s] == 1 and ((not other[1][s]) or g[s])
                ev.append("svd" if served else "pay")
        return "N" + ("".join(":" + e for e in sorted(ev)))
    nb = other[2]
    if f1[0] and f1[1] and (nb[0] == 0 or nb[1] == 0):
        return "B:T1"
    ty = "".join(sorted("N" if not a[s] else ("B" if not f1[s] else "R") for s in (0, 1)))
    return "B:F:" + ty + (":bothmult" if (f1[0] and f1[1]) else "")


def m_vec(prev, cur, nxt, hid):
    """exact vector of an M window (without the bonus of the vertex); hid = (hidE, hidW)"""
    v = [0] * NV
    v[NMF] = 1
    if nxt is not None and cur.bout == NONE:
        v[P_] += 1
        v[V2] += 2
    sE = side_vec(cur.bout, nxt, cur.h[2:] if MUT == "swap_hE_hW" else cur.h[:2], hid[0])
    sW = side_vec(cur.bin, prev, cur.h[:2] if MUT == "swap_hE_hW" else cur.h[2:], hid[1])
    return [x + y + z for x, y, z in zip(v, sE, sW)]


def bonus(mc):
    """bonus 3(m-3) per line = 6(m-3) halves for the m-fold class mc"""
    v = [0] * NV
    v[V2] = 6 * (mc - 3) - (2 if MUT == "bonus_minus_2" else 0)
    return v


def map5(v5):
    """T20 vector (p, v2, nRN, nRR, nT) -> our 11-vector"""
    v = [0] * NV
    v[P_], v[V2], v[RN3], v[RR3], v[NT3] = v5
    return v


def window_vec(prev, cur, nxt, hid):
    """exact vector of a window with the true hidden assignment (S, T: T20 code; M: this file)"""
    if cur.kind == "M":
        return m_vec(prev, cur, nxt, hid)
    return map5(LA.exact_vec(prev, cur, nxt, hid))


def dot(obj, v):
    return sum(c * x for c, x in zip(obj, v))


BONUS_MODE = "actual"
F4PRIME4 = False        # robustness check only, valid for m = 4 ONLY: no run of three blocks (F4') => flanks of a block ray are not (B, B)


class Weigher:
    """window minima for one objective (memoised).  The g variables are fixed to 0: sound for objectives with v2 coefficient >= 0"""

    def __init__(self, obj):
        assert obj[V2] >= 0
        self.obj = obj
        self.side_cache, self.win_cache = {}, {}

    def side(self, bits, other, a):
        key = (bits, other, a)
        r = self.side_cache.get(key)
        if r is None:
            r = min(dot(self.obj, side_vec(bits, other, a, h)) for h in side_domain(bits, other)
                    if not (F4PRIME4 and bits == (1, 1) and a == (1, 1) and other[0] == "S" and h[0] == (0, 0)))
            self.side_cache[key] = r
        return r

    def window(self, prev, cur, nxt):
        key = (prev, cur, nxt)
        r = self.win_cache.get(key)
        if r is None:
            o = self.obj
            if cur.kind == "M":
                r = o[NMF]
                if nxt is not None and cur.bout == NONE:
                    r += o[P_] + 2 * o[V2]
                r += self.side(cur.bout, nxt, cur.h[:2]) + self.side(cur.bin, prev, cur.h[2:])
            else:
                r = min(dot(o, map5(v)) for v in LA.options(prev, cur, nxt))
            self.win_cache[key] = r
        return r

    def bonus(self, mc):
        if BONUS_MODE == "const6":          # every m-fold vertex gets the bonus of m = 4 only (the surplus 6(m-4) is dropped)
            return self.obj[V2] * 6
        return self.obj[V2] * 6 * (mc - 3)


# ---------------------------------------------------------------------------------------------- graph
class MGraph:
    """Product graph.  node = (prevInfo | None, frame, parity of n-1, first-vertex ub class, feature flag, cnt parity).
    A virtual source node 0 carries the bonus of the first vertex.  Edge (u -> y): the window of u's vertex (with the next
    vertex known) plus the bonus of the M class chosen for the vertex of y.  terminals: any node with bout = NONE and a
    predecessor.  Topology is built once; weights are recomputed per objective.
    compat=True enforces the end fact F5 at simple end vertices (T and M ends carry no ub flags: sound coarsening)."""

    def __init__(self, allow=lambda f: True, edge_allow=lambda c, n: True, feat=None, cnt=None, compat=False,
                 mclasses=(4, 5), m_frames=True, t3_frames=True):
        self.allow, self.edge_allow, self.feat, self.cnt, self.compat = allow, edge_allow, feat, cnt, compat
        self.mclasses = mclasses
        self.frames = [f for f in all_frames_m(m_frames, t3_frames) if allow(f)]
        by_bin = collections.defaultdict(list)
        for f in self.frames:
            by_bin[f.bin].append(f)
        self.by_bin = by_bin
        self._build()

    def mcs(self, f):
        return self.mclasses if f.kind == "M" else (0,)

    def _build(self):
        import numpy as np
        node_id, nodes = {}, []

        def nid(x):
            r = node_id.get(x)
            if r is None:
                r = node_id[x] = len(nodes)
                nodes.append(x)
            return r

        wid, wins = {}, []

        def win(k):
            r = wid.get(k)
            if r is None:
                r = wid[k] = len(wins)
                wins.append(k)
            return r

        def upd(prev, cur, nxt, flag, cp):
            if self.feat and self.feat(prev, cur, nxt):
                flag = 1
            if self.cnt:
                cp = (cp + self.cnt(prev, cur, nxt)) % 2
            return flag, cp

        nid((None, None, 0, NONE, 0, 0))               # source
        E_s, E_d, E_w, E_m = [], [], [], []
        terms = []
        stack, seen = [], set()
        for f in self.frames:
            if f.bin == NONE:
                for mc in self.mcs(f):
                    x = (None, f, parity_of(f, mc), f.ub if self.compat else NONE, 0, 0)
                    E_s.append(0), E_d.append(nid(x)), E_w.append(-1), E_m.append(mc)
                    if x not in seen:
                        seen.add(x)
                        stack.append(x)
        while stack:
            x = stack.pop()
            prev, cur, par, cls, flag, cp = x
            u = node_id[x]
            if cur.bout == NONE and prev is not None and (not self.compat or LA.ends_compatible_cls(cls, cur)):
                fl2, cp2 = upd(prev, cur, None, flag, cp)
                terms.append((u, win((prev, cur, None)), fl2, par, cp2))
            for nxt in self.by_bin[cur.bout]:
                if not LA.edge_ok(cur, nxt) or not self.edge_allow(cur, nxt):
                    continue
                ni = nxt.info_next()
                fl2, cp2 = upd(prev, cur, ni, flag, cp)
                w = win((prev, cur, ni))
                for mc in self.mcs(nxt):
                    y = (cur.info_prev(), nxt, (par + parity_of(nxt, mc)) % 2, cls, fl2, cp2)
                    E_s.append(u), E_d.append(nid(y)), E_w.append(w), E_m.append(mc)
                    if y not in seen:
                        seen.add(y)
                        stack.append(y)
        self.nodes, self.wins = nodes, wins
        self.E_s = np.array(E_s, dtype=np.int64)
        self.E_d = np.array(E_d, dtype=np.int64)
        self.E_w = np.array(E_w, dtype=np.int64)
        self.E_m = np.array(E_m, dtype=np.int64)
        self.terms = terms

    def weights(self, obj):
        """edge weights and terminal weights for the objective"""
        import numpy as np
        W = Weigher(obj)
        wt = np.array([W.window(*k) for k in self.wins], dtype=np.int64)
        bt = np.zeros(max(self.mclasses + (0,)) + 1, dtype=np.int64)
        for mc in self.mclasses:
            bt[mc] = W.bonus(mc)
        ew = np.where(self.E_w >= 0, wt[np.maximum(self.E_w, 0)], 0) + bt[self.E_m]
        tw = np.array([wt[t[1]] for t in self.terms], dtype=np.int64)
        return ew, tw


INF = 10 ** 9
NEG = float("-inf")


def solve_m(g, obj, parity=None, need_flag=False, cnt_parity=None, witness=True):
    """min over all paths (>= 2 vertices) of the objective; returns (value | -inf | None, witness frames)"""
    import numpy as np
    ew, tw = g.weights(obj)
    N = len(g.nodes)
    sel = [i for i, t in enumerate(g.terms)
           if (parity is None or t[3] == parity) and (not need_flag or t[2]) and (cnt_parity is None or t[4] == cnt_parity)]
    if not sel:
        return None, None
    tnode = np.array([g.terms[i][0] for i in sel], dtype=np.int64)
    tweight = tw[sel]
    # co-reachability of the selected terminals (vectorised reverse BFS)
    co = np.zeros(N, dtype=bool)
    co[tnode] = True
    src, dst = g.E_s, g.E_d
    while True:
        new = co[dst] & ~co[src]
        if not new.any():
            break
        co[src[new]] = True
    keep = co[src] & co[dst]
    src, dst, w = src[keep], dst[keep], ew[keep]
    if len(src) == 0 or not co[0]:
        return None, None
    order = np.argsort(dst, kind="stable")
    src, dst, w = src[order], dst[order], w[order]
    uniq, start, cnts = np.unique(dst, return_index=True, return_counts=True)
    dist = np.full(N, INF, dtype=np.int64)
    dist[0] = 0
    par = np.full(N, -1, dtype=np.int64)
    parw = np.zeros(N, dtype=np.int64)
    for it in range(N + 3):
        ds = dist[src]
        cand = np.where(ds < INF, ds + w, INF)
        best = np.minimum.reduceat(cand, start)
        imp = best < dist[uniq]
        if not imp.any():
            break
        rep = np.repeat(best, cnts)
        ok = (cand == rep) & np.repeat(imp, cnts)
        ei = np.nonzero(ok)[0]
        dd = dst[ei]
        # one parent per improved node (the last matching edge wins)
        par[dd] = src[ei]
        parw[dd] = w[ei]
        dist[uniq[imp]] = best[imp]
        if it % 10 == 9:
            cyc = _cycle(par, parw, N)
            if cyc is not None and cyc[0] < 0:
                return NEG, [g.nodes[x][1] for x in cyc[1] if g.nodes[x][1] is not None]
    else:
        return NEG, []
    tot = np.where(dist[tnode] < INF, dist[tnode] + tweight, INF)
    j = int(np.argmin(tot))
    if tot[j] >= INF:
        return None, None
    val = int(tot[j])
    if not witness:
        return val, None
    return val, _witness_m(g, src, dst, w, dist, int(tnode[j]))


def _cycle(par, parw, N):
    """(weight, nodes) of some cycle of the parent graph, None if it is a forest"""
    import numpy as np
    jump = np.where(par >= 0, par, np.arange(N))
    j = jump.copy()
    for _ in range(int(np.ceil(np.log2(max(N, 2)))) + 2):
        j = j[j]
    onc = np.nonzero(par[j] >= 0)[0]               # j[x] is a root (par < 0) iff x's chain ends; otherwise j[x] is on a cycle
    if len(onc) == 0:
        return None
    y = int(j[onc[0]])
    tot, z, cyc = 0, y, []
    while True:
        tot += int(parw[z])
        cyc.append(z)
        z = int(par[z])
        if z == y:
            return tot, cyc[::-1]


def _witness_m(g, src, dst, w, dist, target):
    import numpy as np
    ds = dist[src]
    tight = (ds < INF) & (ds + w == dist[dst])
    ts, td = src[tight], dst[tight]
    adj = collections.defaultdict(list)
    for a_, b_ in zip(ts.tolist(), td.tolist()):
        adj[a_].append(b_)
    prev = {0: None}
    q = collections.deque([0])
    while q:
        x = q.popleft()
        if x == target:
            break
        for y in adj[x]:
            if y not in prev:
                prev[y] = x
                q.append(y)
    path, x = [], target
    while x is not None:
        if x != 0:
            path.append(g.nodes[x][1])
        x = prev.get(x)
    return path[::-1]


def show(path):
    def one(f):
        if f.kind == "M":
            return f"M[{f.bin}{f.bout}h{f.h}]"
        return f"{f.kind}[{f.bin}{f.bout}{'u' + str(f.ub) if f.ub != NONE else ''}{'h' + str(f.h) if f.kind == 'T' else ''}]"
    return " | ".join(one(f) for f in path)


def fmt(v, const=-1.0):
    if v is None:
        return "  n/a"
    if v == NEG:
        return " -inf"
    return f"{v / 2 + const:5.1f}"


# ---------------------------------------------------------------------------------------------- data side
def _imports():
    sys.path.append(str(ROOT / "work/t3"))
    global Arr, rays, far_end, first_seg, Multi, values, records
    import inspect  # noqa: F401  (stdlib module first)
    from arr import Arr, rays, far_end, first_seg
    from bbl_hallm import Multi, values
    from cluster import records


def _side_rel(L, ray):
    """side (+1 / -1) of the ray (w, d) of a line w != L at a common point, relative to L (+1 = smaller slot index)"""
    w, d = ray
    return 1 if ((w < L and d == -1) or (w > L and d == 1)) else -1


def _sector(a, V, rs, i):
    """is the sector between the rays i and i+1 (mod 2m) at the multiple point V a triangle (checked from both bounding rays)"""
    k = len(rs)
    out = []
    for (r, r2) in ((rs[i % k], rs[(i + 1) % k]), (rs[(i + 1) % k], rs[i % k])):
        fs = first_seg(a, V, r)
        if fs is None:
            out.append(False)
        else:
            out.append(_side_rel(r[0], r2) in a.t[fs[0]][fs[1]])
    assert out[0] == out[1], "sector asymmetry"
    return out[0]


def _hid_side(a, V, mult, ch, ringpos, mm, j1, j2):
    """hidden data of one side of an M vertex: rays s*j1 (adjacent to L's ray) and s*j2 (the other flanker), s = +,-"""
    f1, f2, g = [0, 0], [0, 0], [0, 0]
    rs = rays(a, V)
    for s in (0, 1):
        sgn = 1 if s == 0 else -1
        r1, r2 = ringpos(sgn, j1), ringpos(sgn, j2)
        f1[s] = int(far_end(a, V, rs[r1]) in mult)
        f2[s] = int(far_end(a, V, rs[r2]) in mult)
        if ch.st[V][r1] == "B":
            b = next(b for b in ch.blk if b[0] == V and b[1] == r1)
            (_, _, l, d, X, C) = b
            Q = far_end(a, V, rs[r2])
            if Q in mult:
                dq = 1 if a.pos[C][X] > a.pos[C][Q] else -1
                kq = rays(a, Q).index((C, dq))
                g[s] = int(ch.st[Q][kq] == "N")
    return tuple(f1), tuple(f2), tuple(g)


def extract(ch, L):
    """frames of line L (S, T3 as LA.Frame, M as MFrame) with the TRUE hidden assignments"""
    a, mult = ch.a, ch.mult
    row = a.rows[L]
    m = len(row)

    def bits(e):
        if e < 0 or e > m - 2:
            return NONE
        s = a.t[L][e]
        return (int(1 in s), int(-1 in s))

    frames, hids = [], []
    for i, V in enumerate(row):
        bi, bo = bits(i - 1), bits(i)
        if V not in mult:
            W = a.other(V, L)
            ub = [0, 0]
            for d in (-1, 1):
                if far_end(a, V, (W, d)) is None:
                    ub[0 if _side_rel(L, (W, d)) == 1 else 1] = 1
            frames.append(LA.Frame("S", bi, bo, tuple(ub), NONE))
            hids.append(None)
            continue
        mm = len(a.events[V])
        rs = rays(a, V)
        k = 2 * mm
        assert len(rs) == k
        iE = rs.index((L, 1))
        assert rs[(iE + mm) % k] == (L, -1)
        s0 = _side_rel(L, rs[(iE + 1) % k])

        def ringpos(sgn, j, iE=iE, s0=s0, mm=mm, k=k):
            if j == 0:
                return iE
            if j == mm:
                return (iE + mm) % k
            return (iE + j) % k if sgn == s0 else (iE - j) % k

        def sector(sgn, j, ringpos=ringpos, k=k, a=a, V=V, rs=rs):
            r1, r2 = ringpos(sgn, j), ringpos(sgn, j + 1)
            if (r2 - r1) % k == 1:
                return _sector(a, V, rs, r1)
            assert (r1 - r2) % k == 1
            return _sector(a, V, rs, r2)

        # sector bits agree with the segment bits (validates the side conventions)
        assert (int(sector(1, 0)), int(sector(-1, 0))) == bo, (bo, sector(1, 0), sector(-1, 0))
        assert (int(sector(1, mm - 1)), int(sector(-1, mm - 1))) == bi
        hE = (int(sector(1, 1)), int(sector(-1, 1)))
        hW = (int(sector(1, mm - 2)), int(sector(-1, mm - 2)))
        if mm == 3:
            assert hE == hW
            fr = LA.Frame("T", bi, bo, NONE, hE)
            sig = [0] * 4
            g = [0] * 4
            # LA convention: ER = (E+, E-, W+, W-) = rays (+1, -1, +2, -2)
            ringidx = {"E+": ringpos(1, 1), "E-": ringpos(-1, 1), "W+": ringpos(1, 2), "W-": ringpos(-1, 2)}
            for kk, R in enumerate(LA.ER):
                sig[kk] = int(far_end(a, V, rs[ringidx[R]]) in mult)
            for R, Rother in (("E+", "W+"), ("E-", "W-"), ("W+", "E+"), ("W-", "E-")):
                if ch.st[V][ringidx[R]] == "B":
                    b = next(b for b in ch.blk if b[0] == V and b[1] == ringidx[R])
                    (_, _, l, d, X, C) = b
                    Q = far_end(a, V, rs[ringidx[Rother]])
                    if Q in mult:
                        dq = 1 if a.pos[C][X] > a.pos[C][Q] else -1
                        kq = rays(a, Q).index((C, dq))
                        g[LA.ER.index(Rother)] = int(ch.st[Q][kq] == "N")
            frames.append(fr)
            hids.append((tuple(sig), tuple(g)))
        else:
            fr = MFrame("M", bi, bo, NONE, hE + hW)
            hidE = _hid_side(a, V, mult, ch, ringpos, mm, 1, 2)
            hidW = _hid_side(a, V, mult, ch, ringpos, mm, mm - 1, mm - 2)
            frames.append(fr)
            hids.append((hidE, hidW))
    mults = [len(a.events[V]) for V in row]
    return frames, hids, mults


def line_windows(frames):
    m = len(frames)
    out = []
    for i, f in enumerate(frames):
        prev = frames[i - 1].info_prev(False) if i > 0 else None
        nxt = frames[i + 1].info_next(False) if i < m - 1 else None
        out.append((prev, f, nxt))
    return out


def reference(ch, L, val, served):
    """reference 11-vector of line L from bbl_hallm.values() and Multi.rec"""
    a = ch.a
    v = [0] * NV
    v[P_] = ch.rec[L]
    v[V2] = int(2 * (val[L] + 1))
    for b in ch.blk:
        (P, i, l, d, X, C) = b
        if l != L or served[b]:
            continue
        k = 2 * ch.mult[P]
        ty = sorted(ch.st[P][f] for f in ((i - 1) % k, (i + 1) % k))
        nn = sum(1 for t in ty if t != "N")
        if ch.mult[P] == 3:
            assert "B" not in ty, "B flank at a triple point (F4 violated)"
            if nn == 1:
                v[RN3] += 1
            elif nn == 2:
                v[RR3] += 1
        else:
            key = "".join(ty)
            idx = {"NN": None, "NR": RNM, "BN": BNM, "RR": RRM, "BR": RBM, "BB": BBM}[key]
            if idx is not None:
                v[idx] += 1
    for V in a.rows[L]:
        if V in ch.mult:
            v[NT3 if ch.mult[V] == 3 else NMF] += 1
    return tuple(v)


_FRAMESET = None


def frameset():
    global _FRAMESET
    if _FRAMESET is None:
        _FRAMESET = frozenset(all_frames_m())
    return _FRAMESET


_dom_cache = {}


def hid_in_domain(prev, cur, nxt, hid):
    if cur.kind == "T":
        key = (prev, cur, nxt)
        if key not in _dom_cache:
            _dom_cache[key] = set(LA.sig_domain(prev, cur, nxt, True))
        return hid in _dom_cache[key]
    (hE, hW) = hid
    return hE in set(side_domain(cur.bout, nxt, True)) and hW in set(side_domain(cur.bin, prev, True))


def check_line(ch, L, val, served, stats=None, events=None):
    """errors (empty = the line is a path of the automaton, hidden values are in the domains, quantities equal the reference)"""
    errs = []
    frames, hids, mults = extract(ch, L)
    m = len(frames)
    if m < 2:
        return errs
    fset = frameset()
    for f in frames:
        if f not in fset:
            errs.append(f"frame not enumerated: {f}")
    if frames[0].bin != NONE or frames[-1].bout != NONE:
        errs.append("end bits")
    for f, gg in zip(frames, frames[1:]):
        if not LA.edge_ok(f, gg):
            errs.append(f"edge not allowed: {f} -> {gg}")
    if not LA.ends_compatible(frames[0], frames[-1]):
        errs.append("end compatibility violated")
    tot = [0] * NV
    for idx_, ((prev, cur, nxt), hid, mm) in enumerate(zip(line_windows(frames), hids, mults)):
        if cur.kind != "S" and not hid_in_domain(prev, cur, nxt, hid):
            errs.append(f"hidden assignment outside domain at {cur} {hid}")
        v = window_vec(prev, cur, nxt, hid)
        if cur.kind == "M":
            v = [x + y for x, y in zip(v, bonus(mm))]
        for k in range(NV):
            tot[k] += v[k]
        if stats is not None:
            stats[(prev, cur, nxt)] += 1
        if events is not None and cur.kind == "S" and prev is not None and nxt is not None and prev[0] == "T" and nxt[0] == "T":
            for k in (0, 1):
                if cur.bin[k] and cur.bout[k]:      # L caps a block with both flankers multiple (T1 cap payment)
                    npay = (cur.bin[1 - k] == 0) + (cur.bout[1 - k] == 0)
                    events[("Scap", min(mults[idx_ - 1], 5), min(mults[idx_ + 1], 5), f"pays{npay}")] += 1
        if events is not None and cur.kind == "M":
            events[(mm, "E", side_event(cur.bout, nxt, cur.h[:2], hid[0]))] += 1
            events[(mm, "W", side_event(cur.bin, prev, cur.h[2:], hid[1]))] += 1
    ref = reference(ch, L, val, served)
    if tuple(tot) != ref:
        errs.append(f"mismatch automaton {tuple(tot)} vs reference {ref}")
    nS = sum(1 for mm in mults if mm == 2)
    if (sum(mm - 1 for mm in mults) - (ch.a.n - 1)) or ((nS + sum((mm - 1) % 2 for mm in mults if mm > 2) - (ch.a.n - 1)) % 2):
        errs.append("parity")
    return errs


def iter_arrangements(paths, even_only=True, limit=10 ** 9, mod=1, part=0, minmult=2):
    seen = set()
    k = 0
    skipped = 0
    for inp in paths:
        for r in records(inp):
            g = r["gens"] if isinstance(r["gens"], str) else " ".join(r["gens"])
            if g in seen:
                continue
            seen.add(g)
            k += 1
            if k % mod != part:
                continue
            a = Arr(g, r.get("n"))
            if even_only and a.n % 2:
                continue
            if any(sum(len(a.events[e]) - 1 for e in a.rows[L]) != a.n - 1 for L in range(a.n)):
                skipped += 1
                continue
            if max(len(e) for e in a.events) < minmult:
                continue
            yield g, Multi(a)
            limit -= 1
            if limit <= 0:
                return
    iter_arrangements.skipped = skipped




# ---------------------------------------------------------------------------------------------- generator of test data
def cmd_gen(args):
    """arrangements with 4-, 5-, 6-fold points.  Chains of push_through moves (a line moved through a multiple point),
    interleaved with random triangle flips that create the fans a push through a 4-fold point needs (5-fold points are
    rare otherwise).  Every intermediate arrangement with a point of multiplicity >= 4 is written (deduplicated)."""
    import argparse
    import json
    import random
    ap = argparse.ArgumentParser()
    ap.add_argument("bases", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--steps", type=int, default=8)
    ap.add_argument("--flips", type=int, default=120)
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--max-per-base", type=int, default=100)
    ap.add_argument("--skip", type=int, default=0)
    o = ap.parse_args(args)
    _imports()
    from mutate import push_through, flip, tri_vertices
    rng = random.Random(o.seed)
    seen, cnt = set(), collections.Counter()
    fo = open(o.out, "w")

    def try_push(cur, minm):
        cands = [(P, w) for P, ev in enumerate(cur.events) if len(ev) >= minm for w in range(cur.n) if w not in ev]
        rng.shuffle(cands)
        cands.sort(key=lambda pw: -len(cur.events[pw[0]]))
        for P, w in cands[:200]:
            wd = push_through(cur, P, w)
            if wd is not None:
                return wd, Arr(wd, cur.n)
        return None

    for base in o.bases:
        k = 0
        for r in records(base):
            k += 1
            if k <= o.skip:
                continue
            if k > o.skip + o.max_per_base:
                break
            g = r["gens"] if isinstance(r["gens"], str) else " ".join(r["gens"])
            a = Arr(g, r.get("n"))
            for rep in range(o.reps):
                cur = a
                for step in range(o.steps):
                    mx = max(len(e) for e in cur.events)
                    res = try_push(cur, 4) if mx >= 4 else None
                    if res is None and mx >= 4:
                        for _ in range(o.flips):              # flip triangles until a fan appears at a >= 4-fold point
                            tris = [f for f in cur.tris if all(len(cur.events[v]) == 2 for v in tri_vertices(cur, f))]
                            if not tris:
                                break
                            wd = flip(cur, rng.choice(tris))
                            if wd is None:
                                continue
                            cur = Arr(wd, cur.n)
                            res = try_push(cur, 4)
                            if res is not None:
                                break
                    if res is None:
                        res = try_push(cur, 3)
                    if res is None:
                        break
                    wd, cur = res
                    if wd not in seen:
                        seen.add(wd)
                        mm = max(len(e) for e in cur.events)
                        cnt[mm] += 1
                        fo.write(json.dumps({"n": cur.n, "gens": wd, "maxm": mm, "src": Path(base).name}) + "\n")
                        fo.flush()
    fo.close()
    print("generated arrangements by max multiplicity:", dict(sorted(cnt.items())))


def cmd_genrand(args):
    """random arrangements with multiple points of every multiplicity: repeatedly reverse a random block of consecutive
    wires that pairwise have not crossed yet, until the permutation is fully reversed.  Few triangles, but stresses the frames
    at multiplicities 5..8."""
    import argparse
    import json
    import random
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--count", type=int, default=2000)
    ap.add_argument("--n", type=int, nargs="+", default=[8, 10, 12, 14])
    ap.add_argument("--wmax", type=int, default=8)
    o = ap.parse_args(args)
    rng = random.Random(o.seed)
    fo = open(o.out, "w")
    for _ in range(o.count):
        n = rng.choice(o.n)
        wires = list(range(n))
        toks = []
        big = rng.choice([0.0, 0.15, 0.4])
        while True:
            moves = []
            for g in range(n - 1):
                # maximal increasing run starting at g
                w = 2
                if wires[g] < wires[g + 1]:
                    moves.append((g, 2))
                    while g + w < n and wires[g + w - 1] < wires[g + w] and w < o.wmax:
                        w += 1
                        moves.append((g, w))
            if not moves:
                break
            if rng.random() < big:
                cand = [mv for mv in moves if mv[1] >= 4] or moves
            else:
                cand = [mv for mv in moves if mv[1] == 2] or moves
            g, w = rng.choice(cand)
            wires[g:g + w] = wires[g:g + w][::-1]
            toks.append(str(g) + "*" * (w - 2))
        if wires != sorted(wires, reverse=True):
            continue
        fo.write(json.dumps({"n": n, "gens": " ".join(toks)}) + "\n")
    fo.close()


# ---------------------------------------------------------------------------------------------- commands
def cmd_validate(args):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--limit", type=int, default=10 ** 9)
    ap.add_argument("--mod", type=int, default=1)
    ap.add_argument("--part", type=int, default=0)
    ap.add_argument("--odd", action="store_true")
    ap.add_argument("--minmult", type=int, default=2)
    ap.add_argument("--out", default=None)
    o = ap.parse_args(args)
    _imports()
    tot_arr = tot_lines = bad = lines_m = 0
    windows = collections.Counter()
    frames_seen = collections.Counter()
    bym = collections.Counter()
    lines_by_m = collections.Counter()
    events = collections.Counter()
    for g, ch in iter_arrangements(o.inputs, not o.odd, o.limit, o.mod, o.part, o.minmult):
        val, served = bbl_values(ch)
        tot_arr += 1
        bym[max(ch.mult.values(), default=2)] += 1
        for L in range(ch.a.n):
            tot_lines += 1
            errs = check_line(ch, L, val, served, windows, events)
            fr, _, mults = extract(ch, L)
            for f in fr:
                frames_seen[f] += 1
            for mm in set(mults):
                lines_by_m[mm] += 1
            if errs:
                bad += 1
                if bad <= 20:
                    print("ERROR", ch.a.n, L, g[:60], errs[:3], flush=True)
    print(f"skipped incomplete words: {getattr(iter_arrangements, 'skipped', 0)}")
    print(f"arrangements {tot_arr} (by max multiplicity {dict(sorted(bym.items()))}), lines {tot_lines}, failing lines {bad}")
    print(f"lines through a point of multiplicity m: {dict(sorted(lines_by_m.items()))}")
    print(f"distinct frames in data {len(frames_seen)} of {len(frameset())} enumerated; distinct windows {len(windows)}")
    by_kind = collections.Counter(f.kind for f in frames_seen)
    print(f"frames seen by kind: {dict(by_kind)}")
    print("M-side events (multiplicity, side, event): count")
    for k in sorted(events, key=str):
        print("   ", k, events[k])
    if o.out:
        import pickle
        pickle.dump((dict(frames_seen), dict(windows), tot_arr, tot_lines, bad, dict(lines_by_m), dict(events)), open(o.out, "wb"))


def cmd_sidecheck(args):
    """the side model of the M vertex, applied to TRIPLE vertices, must reproduce T20's exact vector (which is validated on
    2.16M lines).  For a triple point hE = hW = h, E side: f1 = (sig E+, sig E-), f2 = (sig W+, sig W-), g = (g W+, g W-);
    W side: f1 = (sig W+, sig W-), f2 = (sig E+, sig E-), g = (g E+, g E-).  All counters must agree, and the true hidden values
    must lie in the side domains (this tests forced / F3' independently of the F4 ring rule)."""
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--limit", type=int, default=10 ** 9)
    ap.add_argument("--mod", type=int, default=1)
    ap.add_argument("--part", type=int, default=0)
    o = ap.parse_args(args)
    _imports()
    nv = bad = narr = 0
    ev = collections.Counter()
    for g, ch in iter_arrangements(o.inputs, True, o.limit, o.mod, o.part, minmult=3):
        narr += 1
        for L in range(ch.a.n):
            frames, hids, mults = extract(ch, L)
            for (prev, cur, nxt), hid in zip(line_windows(frames), hids):
                if cur.kind != "T":
                    continue
                sig, gg = hid
                h = cur.h
                hidE = ((sig[0], sig[1]), (sig[2], sig[3]), (gg[2], gg[3]))
                hidW = ((sig[2], sig[3]), (sig[0], sig[1]), (gg[0], gg[1]))
                sE = side_vec(cur.bout, nxt, h, hidE)
                sW = side_vec(cur.bin, prev, h, hidW)
                base = map5(LA.exact_vec(prev, cur, nxt, hid))
                v = [x + y for x, y in zip(sE, sW)]
                v[P_] = 1 if (nxt is not None and cur.bout == NONE) else 0
                v[V2] += 2 * v[P_]
                v[RN3], v[RR3] = v[RNM] + v[BNM], v[RRM] + v[RBM] + v[BBM]
                v[RNM] = v[BNM] = v[RRM] = v[RBM] = v[BBM] = 0
                v[NT3] = 1
                nv += 1
                ev[(side_event(cur.bout, nxt, h, hidE), side_event(cur.bin, prev, h, hidW))] += 0
                if v != base or hidE not in set(side_domain(cur.bout, nxt, True)) or hidW not in set(side_domain(cur.bin, prev, True)):
                    bad += 1
                    if bad <= 10:
                        print("SIDECHECK FAIL", cur, prev, nxt, hid, v, base)
                for sd in ((cur.bout, nxt, h, hidE), (cur.bin, prev, h, hidW)):
                    ev[side_event(*sd)] += 1
    print(f"arrangements {narr}, triple-point windows {nv}, mismatches {bad}")
    for k in sorted(k for k in ev if isinstance(k, str)):
        print("   ", k, ev[k])


MUTATIONS = ["bonus_minus_2", "F_gain_1", "T1_gain_2", "flank_pay_1", "served_ignores_f2", "forced_always", "swap_RN_BN",
             "swap_hE_hW", "count_R_as_block", "T1_one_flanker", "R_costs"]


def cmd_mutants(args):
    """planted errors in the M window model: the validation must fail on them (detection power of the check)"""
    import argparse
    global MUT
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--limit", type=int, default=10 ** 9)
    ap.add_argument("--minmult", type=int, default=4)
    o = ap.parse_args(args)
    _imports()
    data = [(ch, bbl_values(ch)) for g, ch in iter_arrangements(o.inputs, True, o.limit, minmult=o.minmult)]
    nl = sum(ch.a.n for ch, _ in data)
    for mut in [None] + MUTATIONS:
        MUT = mut
        bad = 0
        for ch, (val, served) in data:
            for L in range(ch.a.n):
                if check_line(ch, L, val, served):
                    bad += 1
        print(f"mutation {str(mut):20s}: failing lines {bad} / {nl}", flush=True)
    MUT = None


def bbl_values(ch):
    return values(ch)


def cmd_datamin(args):
    """minimum over data of v_L and of v_L + comp3 (a3 = 1, b3 = 3 on triple-point blocks), by line feature: shows how tight the
    certified bounds are"""
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--limit", type=int, default=10 ** 9)
    ap.add_argument("--mod", type=int, default=1)
    ap.add_argument("--part", type=int, default=0)
    ap.add_argument("--minmult", type=int, default=2)
    o = ap.parse_args(args)
    _imports()
    best = {}
    narr = 0
    for g, ch in iter_arrangements(o.inputs, True, o.limit, o.mod, o.part, o.minmult):
        val, served = bbl_values(ch)
        narr += 1
        for L in range(ch.a.n):
            ref = reference(ch, L, val, served)
            v = ref[V2] / 2 - 1
            c3 = v + ref[RN3] / 2 + 1.5 * ref[RR3]
            cM = c3 + (ref[RNM] + ref[BNM]) / 2 + 1.5 * (ref[RRM] + ref[RBM] + ref[BBM])
            ms = sorted(set(ch.mult[V] for V in ch.a.rows[L] if V in ch.mult))
            surplus = sum(ch.mult[V] - 4 for V in ch.a.rows[L] if V in ch.mult and ch.mult[V] >= 4)
            cS = c3 - 3 * surplus
            feats = ["all", "pure" if not ms else "mult"]
            if ms and ms[-1] >= 4:
                feats.append("has m>=4")
                feats.append(f"max m = {min(ms[-1], 6)}{'+' if ms[-1] >= 6 else ''}")
                if 3 not in ms:
                    feats.append("m>=4, no triple")
            if 3 in ms:
                feats.append("has triple")
            for f in feats:
                b = best.setdefault(f, [10 ** 9, 10 ** 9, 10 ** 9, 0, 10 ** 9])
                b[0], b[1], b[2] = min(b[0], v), min(b[1], c3), min(b[2], cM)
                b[3] += 1
                b[4] = min(b[4], cS)
    print(f"{narr} arrangements")
    for f, b in sorted(best.items()):
        print(f"  {f:18s} lines {b[3]:8d}  min v_L = {b[0]:5.1f}   min v_L+comp3 = {b[1]:5.1f}   min v_L+comp3+compM(1,3) = {b[2]:5.1f}   min v_L+comp3-3*sum(m-4) = {b[4]:5.1f}")


def clean_frame(f):
    return f.kind == "S" and not (f.bin[0] and f.bout[0]) and not (f.bin[1] and f.bout[1])


def cmd_m1(args):
    """L3: a clean line has a portion iff n is even (m = n-1 odd).  A clean line has only simple vertices, so the multiplicities
    of the other lines are irrelevant; re-derived inside the multiplicity-aware graph (T and M frames excluded by `allow`)."""
    for name, kw in (("S frames only", dict(m_frames=False, t3_frames=False)),
                     ("full frame set, restricted to clean S frames", dict())):
        g = MGraph(allow=clean_frame, compat=True, **kw)
        for par, nm in ((1, "n even (m = n-1 odd)"), (0, "n odd  (m = n-1 even)")):
            v, path = solve_m(g, objective(v2=0, p=1), parity=par)
            print(f"[{name}] clean lines, {nm}: min portions = {v}   witness: {show(path) if path else ''}")
    v, path = solve_m(MGraph(allow=clean_frame, compat=False), objective(v2=0, p=1), parity=1)
    print("ablation without F5 (end compatibility): even n min portions =", v)
    print("(lines through a multiple point can have 0 portions: e.g. M[(0,0)(1,1)] | T[(1,1)(0,0)] , so L3 is a statement about clean lines only)")


def layered_min_m(obj, parity, maxlen, allow=lambda f: True, mclasses=(4, 5), compat=False):
    """independent implementation: forward DP by exact path length (no graph, no Bellman-Ford), lengths 2..maxlen"""
    frames = [f for f in all_frames_m() if allow(f)]
    by_bin = collections.defaultdict(list)
    for f in frames:
        by_bin[f.bin].append(f)
    W = Weigher(obj)
    mcs = lambda f: mclasses if f.kind == "M" else (0,)
    layer = {}
    for f in frames:
        if f.bin == NONE:
            for mc in mcs(f):
                key = (None, f, parity_of(f, mc), f.ub if compat else NONE)
                c = W.bonus(mc) if f.kind == "M" else 0
                if key not in layer or c < layer[key]:
                    layer[key] = c
    best = None
    for length in range(1, maxlen):
        nxt_layer = {}
        for (prev, cur, par, cls), cost in layer.items():
            for nx in by_bin[cur.bout]:
                if not LA.edge_ok(cur, nx):
                    continue
                ni = nx.info_next()
                w = W.window(prev, cur, ni)
                for mc in mcs(nx):
                    key = (cur.info_prev(), nx, (par + parity_of(nx, mc)) % 2, cls)
                    val = cost + w + (W.bonus(mc) if nx.kind == "M" else 0)
                    if key not in nxt_layer or val < nxt_layer[key]:
                        nxt_layer[key] = val
        layer = nxt_layer
        for (prev, cur, par, cls), cost in layer.items():
            if cur.bout != NONE or (parity is not None and par != parity) or (compat and not LA.ends_compatible_cls(cls, cur)):
                continue
            tot = cost + W.window(prev, cur, None)
            if best is None or tot < best[0]:
                best = (tot, length + 1)
    return best


def cmd_crosscheck(args):
    """Bellman-Ford results versus the independent layered DP (exact for finite minima attained by short paths; for -inf the
    layered value keeps falling with the length)"""
    maxlen = int(args[0]) if args else 12
    tests = [
        ("M1 even n", dict(obj=objective(v2=0, p=1), parity=1, allow=clean_frame, compat=True)),
        ("M1 odd n", dict(obj=objective(v2=0, p=1), parity=0, allow=clean_frame, compat=True)),
        ("M2 (a3,b3)=(1,3), classes 4,5", dict(obj=objective(a3=1, b3=3), parity=None)),
        ("M2 (1,3) even n", dict(obj=objective(a3=1, b3=3), parity=1)),
        ("S+M lines only, raw v_L, even n", dict(obj=objective(), parity=1, allow=lambda f: f.kind != "T")),
        ("M2 (1,2) (-inf expected)", dict(obj=objective(a3=1, b3=2), parity=None)),
        ("M2 (0,3) (-inf expected)", dict(obj=objective(a3=0, b3=3), parity=None)),
    ]
    for name, kw in tests:
        gk = {k: v for k, v in kw.items() if k in ("allow", "compat")}
        v, _ = solve_m(MGraph(**gk), kw["obj"], parity=kw["parity"], witness=False)
        lm = [layered_min_m(maxlen=L, **kw) for L in (6, 9, maxlen)]
        print(f"{name}: BF = {fmt(v, 0.0).strip() if v is not None else v} (halves {v});  layered min over lengths <= 6/9/{maxlen}: "
              f"{[x[0] if x else None for x in lm]}", flush=True)


def cmd_m2(args):
    """certified bounds; all values are bounds on v_L (= v2/2 - 1) plus the stated compensation"""
    hasM = lambda prev, cur, nxt: cur.kind == "M"
    print("== M2a: v_L + (a3/2)*#RN3 + (b3/2)*#RR3 + (aM/2)*#(unserved M-block, 1 non-N flank) + (bM/2)*#(... 2 non-N flanks) >= bound")
    g = MGraph()
    print(f"   graph: {len(g.frames)} frames, {len(g.nodes)} nodes, {len(g.E_s)} edges, m classes {g.mclasses}")
    for (a3, b3) in ((1, 3), (1, 2), (0, 3), (0, 0)):
        for par, nm in ((None, "all n"), (1, "even n")):
            row = []
            for (aM, bM) in ((0, 0), (1, 3), (-1, -3)):
                v, path = solve_m(g, objective(a3=a3, b3=b3, aM=aM, bM=bM), parity=par)
                row.append(fmt(v))
                if v == NEG and (aM, bM) == (0, 0) and par is None:
                    cyc = show(path)
            print(f"   (a3,b3)=({a3},{b3}) {nm:7s} (aM,bM)=(0,0) | (1,3) | (-1,-3): {' | '.join(row)}"
                  + (f"   negative cycle: {cyc}" if row[0].strip() == '-inf' and par is None else ""), flush=True)
    print("== M2g: admissible compensation coefficients for unserved blocks at m-fold points (halves), (a3,b3) = (1,3) fixed")
    for (aM, bM) in ((0, 0), (-1, 0), (-2, 0), (-3, 0), (0, -1), (-2, -1), (3, 9)):
        v, path = solve_m(g, objective(a3=1, b3=3, aM=aM, bM=bM))
        print(f"   (aM,bM)=({aM},{bM}): bound {fmt(v)}" + (f"   negative cycle: {show(path)}" if v == NEG else ""), flush=True)
    print("== M2b: window lemma. Minimum over ALL windows of an m-fold vertex (all neighbours, all hidden values) of its v2 contribution")
    for mc in (4, 5, 6, 7):
        W = Weigher(objective(a3=0, b3=0))
        gg = MGraph(mclasses=(mc,), t3_frames=False)
        mn = min(W.window(k[0], k[1], k[2]) + W.bonus(mc) for k in gg.wins if k[1].kind == "M")
        print(f"   m = {mc}: min v2 contribution of an m-fold vertex = {mn}   (6(m-4) = {6 * (mc - 4)})")
    print("== M2c: lines through at least one m-fold vertex (v_L + comp3, a3=1 b3=3), by allowed multiplicity classes")
    for mcs in ((4,), (5,), (6,), (7,), (4, 5), (4, 5, 6, 7, 8, 9)):
        gm = MGraph(feat=hasM, mclasses=mcs)
        out = []
        for par in (None, 1):
            v, path = solve_m(gm, objective(a3=1, b3=3), parity=par, need_flag=True)
            out.append(fmt(v))
        print(f"   classes {mcs}: all n {out[0]}, even n {out[1]}   (witness, even n: {show(path) if path else ''})", flush=True)
    print("== M2e: surplus form.  Give every m-fold vertex only the bonus of m = 4 (drop 6(m-4) halves): the bound stays -1, i.e.")
    print("   v_L + comp3 >= -1 + 3 * sum over the m-fold vertices (m >= 4) on L of (m - 4)")
    global BONUS_MODE
    BONUS_MODE = "const6"
    try:
        gk = MGraph()
        for par, nm in ((None, "all n"), (1, "even n")):
            v, path = solve_m(gk, objective(a3=1, b3=3), parity=par)
            print(f"   [{nm}] min of v_L + comp3 - 3*sum(m-4) = {fmt(v)}", flush=True)
    finally:
        BONUS_MODE = "actual"
    print("== M2f: robustness, m = 4 only, with the extra fact F4' (a run of blocks at a 4-fold point has length <= 2, so the flanks of")
    print("   a block ray E are never (B,B)).  The bound for lines through a 4-fold point does not move:")
    global F4PRIME4
    F4PRIME4 = True
    try:
        g4 = MGraph(feat=hasM, mclasses=(4,))
        for par, nm in ((None, "all n"), (1, "even n")):
            v, path = solve_m(g4, objective(a3=1, b3=3), parity=par, need_flag=True)
            print(f"   [{nm}] lines with a 4-fold vertex, with F4': min v_L + comp3 = {fmt(v)}   {show(path) if path else ''}", flush=True)
    finally:
        F4PRIME4 = False
    print("== M2d: lines with NO triple point (simple and m-fold vertices only): raw v_L, no compensation at all")
    gs = MGraph(allow=lambda f: f.kind != "T", feat=hasM)
    for par, nm in ((None, "all n"), (1, "even n")):
        v, path = solve_m(gs, objective(), parity=par, need_flag=False)
        v2, path2 = solve_m(gs, objective(), parity=par, need_flag=True)
        print(f"   [{nm}] any such line: min v_L = {fmt(v)}; with an m-fold vertex: min v_L = {fmt(v2)}   {show(path2) if path2 else ''}", flush=True)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd, args = sys.argv[1], sys.argv[2:]
    fn = {"gen": cmd_gen, "genrand": cmd_genrand, "validate": cmd_validate, "m1": cmd_m1, "m2": cmd_m2, "mutants": cmd_mutants, "sidecheck": cmd_sidecheck, "datamin": cmd_datamin, "crosscheck": cmd_crosscheck}.get(cmd)
    if fn is None:
        print("unknown command")
        return
    fn(args)


if __name__ == "__main__":
    main()

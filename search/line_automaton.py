"""Line automaton: n-independent verification of per-line lemmas (task T20).

A line L of a pseudoline arrangement (points of multiplicity <= 3) is a sequence of vertices V_1..V_m with bounded
segments s_1..s_{m-1} between them and unbounded rays s_0, s_m.  Every bounded segment carries two face bits
(tb, bb) = (face on side +, face on side -) is a triangle; unbounded rays carry (0, 0).  A *frame* is the local
configuration of one vertex seen from L:
  kind 'S' (simple vertex L∩W):  bin, bout = bits of the segments before/after, ub = (W's ray on side + / - is unbounded)
  kind 'T' (triple L∩a∩b):        bin, bout, h = (hidden sector a+b on side +/- is a triangle), ub = end flags.
Consecutive frames must agree on the segment bits (bout of one = bin of the next).  Everything that
search/bbl_hall.py `values()` attributes to L is a sum of window weights over (prev, cur, next) plus the
information of "hidden" variables (multiplicities of far ends of the other rays at a triple point).  The hidden
variables are chosen adversarially (min) inside each window, which is sound because the automaton does not
correlate windows.  Every local fact imposed is listed (with proofs) in work/eng/T20/REPORT.md.

    python search/line_automaton.py validate <in>...     # soundness check against the Python reference
    python search/line_automaton.py m1                   # milestone 1 (L3)
    python search/line_automaton.py m2                   # milestone 2 (value bounds)
"""
import collections
import itertools
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BITS = [(0, 0), (0, 1), (1, 0), (1, 1)]
NONE = (0, 0)
ER = ("E+", "E-", "W+", "W-")          # the four non-L rays at a triple point
RING = ("E", "E+", "W+", "W", "W-", "E-")   # cyclic order of the six rays


class Frame(collections.namedtuple("Frame", "kind bin bout ub h")):
    __slots__ = ()

    def info_prev(self, first=False):  # what the *next* vertex needs to know about its predecessor (+ is it the first vertex)
        return (self.kind, self.h, self.bin, first)

    def info_next(self, last=False):   # what the *previous* vertex needs to know about its successor (+ is it the last vertex)
        return (self.kind, self.h, self.bout, last)


def all_frames():
    out = []
    for kind in "ST":
        for bi in BITS:
            for bo in BITS:
                for ub in BITS:
                    for h in (BITS if kind == "T" else [NONE]):
                        f = Frame(kind, bi, bo, ub, h)
                        if frame_ok(f):
                            out.append(f)
    return out


def frame_ok(f):
    """local consistency of one frame (facts F-C, F-S1, F-T1 of the report)"""
    (ti, bi_), (to, bo_) = f.bin, f.bout
    if f.kind == "S":
        # F-C: a triangle adjacent to W's ray u needs u bounded;  F-S3: W crosses the other n-2 >= 1 lines, so it has a vertex
        # on at least one side of L
        return not (f.ub[0] and (ti or to)) and not (f.ub[1] and (bi_ or bo_)) and f.ub != (1, 1)
    # triple: 'any hidden ray on that side unbounded' forces the hidden sector and one adjacent sector to be non-triangles
    if f.ub[0] and (f.h[0] or (ti and to)):
        return False
    if f.ub[1] and (f.h[1] or (bi_ and bo_)):
        return False
    return True


def sig_domain(prev, cur, nxt, full_g=False):
    """allowed hidden assignments (sig[4], g[4]) at a triple frame; sig[R] = 1 iff the far end of ray R is triple.
    g (gap-end ray N at the hidden flanker) is unconstrained; it only enters 'served', and served=False is never
    better for the value, so the optimisation windows use g = 0 (sound for objectives with a nonnegative v2
    coefficient).  full_g=True enumerates all g (used for the membership check on data)."""
    bi, bo = cur.bin, cur.bout
    hp, hm = cur.h
    Es = ray_status_L(cur.bout, nxt)
    Ws = ray_status_L(cur.bin, prev)
    forced = [0, 0, 0, 0]
    # F-T2: triangle above s_i with apex Y = far end of the ray E+; if the next vertex is simple and also has a triangle
    # above its own outgoing segment, C+ is doubly used with a simple end, so Y is triple.
    if nxt is not None and nxt[0] == "S":
        if bo[0] and nxt[2][0]:
            forced[0] = 1
        if bo[1] and nxt[2][1]:
            forced[1] = 1
    if prev is not None and prev[0] == "S":
        if bi[0] and prev[2][0]:
            forced[2] = 1
        if bi[1] and prev[2][1]:
            forced[3] = 1
    dbl = (bo[0] and hp, bo[1] and hm, bi[0] and hp, bi[1] and hm)
    for sig in itertools.product((0, 1), repeat=4):
        if any(forced[k] and not sig[k] for k in range(4)):
            continue
        st = {"E": Es, "W": Ws}
        for k, R in enumerate(ER):
            st[R] = ("B" if sig[k] == 0 else "R") if dbl[k] else "N"
        # F-T3: two blocks at a triple point are never adjacent
        if any(st[RING[i]] == "B" and st[RING[(i + 1) % 6]] == "B" for i in range(6)):
            continue
        for g in (itertools.product((0, 1), repeat=4) if full_g else [(0, 0, 0, 0)]):
            yield sig, g


def ray_status_L(bits, other):
    """status of L's own ray at a triple point: 'N', 'B' (doubly used, simple far end) or 'R'"""
    if bits != (1, 1):
        return "N"
    return "B" if other[0] == "S" else "R"


def exact_vec(prev, cur, nxt, hid=None):
    """(p, v2, nRN, nRR, nT) contribution of vertex `cur` (and of the segment after it): p portions, v2 = 2 * value,
    nRN / nRR = number of unserved blocks with axis L whose flank rays are (R, N) / (R, R).  prev/nxt are Info tuples
    (kind, h, bits, end flag) or None; hid = (sig, g) at triple vertices."""
    p = v2 = nRN = nRR = 0
    nT = int(cur.kind == "T")
    bi, bo = cur.bin, cur.bout
    if nxt is not None and bo == NONE:
        p += 1
        v2 += 2                                  # own unused bounded segment
    if cur.kind == "S":
        for k in (0, 1):                         # touches: bounded unused segments of W at this vertex
            if not cur.ub[k] and bi[k] + bo[k] == 0:
                p += 1
                v2 += 2
        if prev is not None and nxt is not None and prev[0] == "T" and nxt[0] == "T":
            for k in (0, 1):                     # T1 with L the cap: L pays 3/2 per N gap-end ray
                if bi[k] and bo[k]:
                    v2 -= 3 * ((bi[1 - k] == 0) + (bo[1 - k] == 0))
        return p, v2, nRN, nRR, nT
    sig, g = hid
    hp, hm = cur.h
    dbl = (bo[0] and hp, bo[1] and hm, bi[0] and hp, bi[1] and hm)
    S = {R: k for k, R in enumerate(ER)}
    for Lray, (bits, other, fl, gapbits) in (("E", (bo, nxt, (S["E+"], S["E-"]), None)),
                                            ("W", (bi, prev, (S["W+"], S["W-"]), None))):
        stat = ray_status_L(bits, other)
        if stat == "N":
            v2 += 3
        elif stat == "B":
            v2 -= 3
        if stat == "B":                          # L is the axis of a block: T1 gains / F gains
            nb = other[2]                        # bits of the segment beyond X
            f1, f2 = sig[fl[0]], sig[fl[1]]
            got2 = 3 * ((nb[0] == 0) + (nb[1] == 0)) if (f1 and f2) else 0
            if got2 > 0:
                v2 += got2
            else:
                v2 += 2 * ((not hp) + (not hm))
                nRR += 1 if (hp and hm) else 0
                nRN += 1 if (hp != hm) else 0
        elif stat == "N":                        # L's N ray may flank an unserved block on an adjacent ray
            if Lray == "E":
                cands = ((bo[0] and hp and sig[S["E+"]] == 0, S["W+"], 0), (bo[1] and hm and sig[S["E-"]] == 0, S["W-"], 1))
            else:
                cands = ((bi[0] and hp and sig[S["W+"]] == 0, S["E+"], 0), (bi[1] and hm and sig[S["W-"]] == 0, S["E-"], 1))
            for (blk, other_k, side) in cands:
                if not blk:
                    continue
                served = other is not None and other[0] == "T" and sig[other_k] == 1 and (not other[1][side] or g[other_k])
                if not served:
                    v2 -= 2
    return p, v2, nRN, nRR, nT


_opt_cache = {}


def options(prev, cur, nxt):
    """set of distinct component vectors of the window over all allowed hidden assignments"""
    key = (prev, cur, nxt)
    r = _opt_cache.get(key)
    if r is None:
        if cur.kind == "S":
            r = frozenset([exact_vec(prev, cur, nxt)])
        else:
            r = frozenset(exact_vec(prev, cur, nxt, h) for h in sig_domain(prev, cur, nxt))
        _opt_cache[key] = r
    return r


def edge_ok(cur, nxt):
    """segment between cur and nxt"""
    if cur.bout != nxt.bin:
        return False
    if cur.bout == (1, 1) and cur.kind == "S" and nxt.kind == "S":      # F-D: doubly used segment has a multiple end
        return False
    return True


def ends_compatible(first, last):
    """F-F: end lines cannot have unbounded rays on opposite sides of L"""
    return not ((first.ub[0] and last.ub[1]) or (first.ub[1] and last.ub[0]))


# ---------------------------------------------------------------------------------------------------- the graph
class Graph:
    """Product graph.  node = (prevInfo | None, frame, parity of #simple vertices, first-vertex ub class, feature flag,
    role (1 = this is the last vertex), parity of `cnt`).
    feat(prev, cur, nxt) -> bool marks windows that set the feature flag; cnt(prev, cur, nxt) -> int is a counter kept
    mod 2; allow(frame) filters frames; compat=False drops the end-compatibility fact F-F (ablation)."""

    def __init__(self, allow=lambda f: True, feat=None, cnt=None, edge_allow=lambda c, n: True, compat=True):
        self.allow, self.feat, self.cnt, self.edge_allow, self.compat = allow, feat, cnt, edge_allow, compat
        self.frames = [f for f in all_frames() if allow(f)]
        self.by_bin = collections.defaultdict(list)
        for f in self.frames:
            self.by_bin[f.bin].append(f)

    def objective_weights(self, obj):
        """returns nodes, start ids, edges (src, dst, w) and terminals (node, w, flag, parity, cnt parity)"""
        node_id, nodes = {}, []

        def nid(x):
            if x not in node_id:
                node_id[x] = len(nodes)
                nodes.append(x)
            return node_id[x]

        def wmin(prev, cur, nxt):
            return min(sum(c * x for c, x in zip(obj, v)) for v in options(prev, cur, nxt))

        def upd(prev, cur, nxt, flag, cp):
            if self.feat and self.feat(prev, cur, nxt):
                flag = 1
            if self.cnt:
                cp = (cp + self.cnt(prev, cur, nxt)) % 2
            return flag, cp

        starts, edges, terms, stack = [], [], [], []
        for f in self.frames:
            if f.bin == NONE:
                x = (None, f, 1 if f.kind == "S" else 0, f.ub, 0, 0, 0)
                starts.append(nid(x))
                stack.append(x)
        seen = set(stack)
        while stack:
            x = stack.pop()
            prev, cur, par, cls, flag, role, cp = x
            u = node_id[x]
            if role == 1:
                if not self.compat or ends_compatible_cls(cls, cur):
                    fl2, cp2 = upd(prev, cur, None, flag, cp)
                    terms.append((u, wmin(prev, cur, None), fl2, par, cp2))
                continue
            for nxt in self.by_bin[cur.bout]:
                if not edge_ok(cur, nxt) or not self.edge_allow(cur, nxt):
                    continue
                for last in (0, 1):
                    if last and nxt.bout != NONE:
                        continue
                    if nxt.kind == "T" and nxt.ub != NONE and not last:
                        continue                    # interior triple frames carry no ub flag (only the two end vertices do)
                    ni = nxt.info_next(bool(last))
                    fl2, cp2 = upd(prev, cur, ni, flag, cp)
                    y = (cur.info_prev(prev is None), nxt, (par + (nxt.kind == "S")) % 2, cls, fl2, last, cp2)
                    if y not in seen:
                        seen.add(y)
                        stack.append(y)
                    nid(y)
                    edges.append((u, node_id[y], wmin(prev, cur, ni)))
        return nodes, starts, edges, terms


def ends_compatible_cls(cls, last):
    return not ((cls[0] and last.ub[1]) or (cls[1] and last.ub[0]))


def solve(graph, obj, parity=None, need_flag=False, cnt_parity=None):
    """min over all paths (>= 2 vertices) of the objective; returns (value | -inf, witness path of frames)"""
    import numpy as np
    nodes, starts, edges, terms = graph.objective_weights(obj)
    N = len(nodes)
    INF = 10 ** 9
    terms = [t for t in terms if (parity is None or t[3] == parity) and (not need_flag or t[2])
             and (cnt_parity is None or t[4] == cnt_parity)]
    # trim: reachable from starts (by construction) and co-reachable to a terminal
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
    edges = [(a, b, w) for (a, b, w) in edges if a in co and b in co]
    if not any(s in co for s in starts):
        return None, None
    src = np.array([e[0] for e in edges], dtype=np.int64)
    dst = np.array([e[1] for e in edges], dtype=np.int64)
    wt = np.array([e[2] for e in edges], dtype=np.int64)
    dist = np.full(N, INF, dtype=np.int64)
    par = np.full(N, -1, dtype=np.int64)
    parw = np.zeros(N, dtype=np.int64)
    for s in starts:
        if s in co:
            dist[s] = 0
    ar = np.arange(N)
    for it in range(N + 2):
        if len(src) == 0:
            break
        ok = dist[src] < INF
        cand = np.where(ok, dist[src] + wt, INF)
        best = dist.copy()
        np.minimum.at(best, dst, cand)
        imp = best < dist
        if not imp.any():
            break
        es = np.nonzero(ok & (cand == best[dst]) & imp[dst])[0]
        par[dst[es]] = src[es]
        parw[dst[es]] = wt[es]
        dist = best
        if it % 20 == 19:                     # negative cycle <=> the parent graph acquires a cycle of negative weight
            cyc = _parent_cycle(par, parw, N)
            if cyc is not None and cyc[0] < 0:
                return float("-inf"), [nodes[x][1] for x in cyc[1]]         # the negative cycle (frames)
    else:
        return float("-inf"), []
    bestv, bt = None, None
    for (u, w, fl, pr, cq) in terms:
        if dist[u] < INF and (bestv is None or dist[u] + w < bestv):
            bestv, bt = int(dist[u] + w), u
    if bestv is None:
        return None, None
    return bestv, _witness(nodes, starts, edges, dist, bt)


def _parent_cycle(par, parw, N):
    """weight of some cycle of the parent graph (None if it is a forest)"""
    import numpy as np
    jump = np.where(par >= 0, par, np.arange(N))
    hasp = par >= 0
    j = jump.copy()
    for _ in range(int(np.ceil(np.log2(max(N, 2)))) + 1):
        j = j[j]
    # nodes whose parent chain never terminates: those with j on a cycle (par[j] >= 0 and chain stays)
    cand = np.nonzero(hasp)[0]
    for x in cand[:2000]:
        y = x
        for _ in range(N + 1):
            if par[y] < 0:
                y = -1
                break
            y = par[y]
        if y == -1:
            continue
        # y is on a cycle
        tot, z, cyc = 0, y, []
        while True:
            tot += int(parw[z])
            cyc.append(int(z))
            z = par[z]
            if z == y:
                return tot, cyc[::-1]
    return None


def _witness(nodes, starts, edges, dist, target):
    """shortest path (fewest steps among tight edges) from a start node to `target`"""
    tight = collections.defaultdict(list)
    for (a, b, w) in edges:
        if dist[a] < 10 ** 9 and dist[a] + w == dist[b]:
            tight[a].append(b)
    prev = {s: None for s in starts if dist[s] == 0}
    q = collections.deque(prev)
    while q:
        x = q.popleft()
        if x == target:
            break
        for y in tight[x]:
            if y not in prev:
                prev[y] = x
                q.append(y)
    path, x = [], target
    while x is not None:
        path.append(nodes[x][1])
        x = prev.get(x)
    return path[::-1]


# ---------------------------------------------------------------------------------------------------- data side
def _imports():
    sys.path.insert(0, str(ROOT / "search"))
    sys.path.append(str(ROOT / "work/t3"))
    global Arr, rays, far_end, first_seg, Charge, values, portions, records
    import inspect  # noqa: F401  (stdlib first)
    from arr import Arr, rays, far_end, first_seg
    from bbl_rules import Charge
    from bbl_hall import values
    from bbl_adversary import portions
    from cluster import records


def _side_rel(L, ray):
    """side (+1/-1) of the ray (w, d) of a line w != L at a common point, relative to L (+1 = smaller slot index)"""
    w, d = ray
    return 1 if ((w < L and d == -1) or (w > L and d == 1)) else -1


def _sector(a, V, rs, i):
    """is the sector between rays i and i+1 at the multiple point V a triangle (seen from both bounding rays)"""
    out = []
    for (r, r2) in ((rs[i % 6], rs[(i + 1) % 6]), (rs[(i + 1) % 6], rs[i % 6])):
        fs = first_seg(a, V, r)
        if fs is None:
            out.append(False)
        else:
            out.append(_side_rel(r[0], r2) in a.t[fs[0]][fs[1]])
    assert out[0] == out[1], "sector asymmetry"
    return out[0]


def extract(ch, L):
    """frames of line L and, for triple vertices, the true hidden assignment; also the reference values"""
    a, trip = ch.a, ch.trip
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
        if V not in trip:
            W = a.other(V, L)
            ub = [0, 0]
            for d in (-1, 1):
                if far_end(a, V, (W, d)) is None:
                    ub[0 if _side_rel(L, (W, d)) == 1 else 1] = 1
            frames.append(Frame("S", bi, bo, tuple(ub), NONE))
            hids.append(None)
            continue
        rs = rays(a, V)
        iE = rs.index((L, 1))
        assert rs[(iE + 3) % 6] == (L, -1)
        s0 = _side_rel(L, rs[(iE + 1) % 6])
        idx = {"E": iE, "W": (iE + 3) % 6}
        if s0 == 1:
            idx.update({"E+": iE + 1, "W+": iE + 2, "W-": iE + 4, "E-": iE + 5})
            hp, hm = _sector(a, V, rs, iE + 1), _sector(a, V, rs, iE + 4)
        else:
            idx.update({"E-": iE + 1, "W-": iE + 2, "W+": iE + 4, "E+": iE + 5})
            hm, hp = _sector(a, V, rs, iE + 1), _sector(a, V, rs, iE + 4)
        idx = {k: v % 6 for k, v in idx.items()}
        # sector bits agree with the segment bits
        pl = 0 if s0 == 1 else 1
        assert _sector(a, V, rs, iE) == bool(bo[pl]) and _sector(a, V, rs, iE + 5 if s0 == 1 else iE + 5) is not None
        ub = [0, 0]
        sig = []
        for R in ER:
            fe = far_end(a, V, rs[idx[R]])
            if fe is None:
                ub[0 if R[1] == "+" else 1] = 1
            sig.append(1 if fe in trip else 0)
        # status consistency with the reference classification
        fr = Frame("T", bi, bo, tuple(ub), (int(hp), int(hm)))
        # L's own unbounded rays never count
        g = [0, 0, 0, 0]
        for R, Rother in (("E+", "W+"), ("E-", "W-"), ("W+", "E+"), ("W-", "E-")):
            k = idx[R]
            if ch.st[V][k] == "B":
                b = next(b for b in ch.blk if b[0] == V and b[1] == k)
                (_, _, l, d, X, C) = b
                Q = far_end(a, V, rs[idx[Rother]])
                if Q in trip:
                    dq = 1 if a.pos[C][X] > a.pos[C][Q] else -1
                    kq = rays(a, Q).index((C, dq))
                    g[ER.index(Rother)] = int(ch.st[Q][kq] == "N")
        frames.append(fr)
        hids.append((tuple(sig), tuple(g)))
    return frames, hids


def line_windows(frames):
    """(prev, cur, nxt) Info triples for every vertex; interior triple frames drop their ub flags (end vertices keep them)"""
    m = len(frames)
    out = []
    for i, f in enumerate(frames):
        prev = frames[i - 1].info_prev(i - 1 == 0) if i > 0 else None
        nxt = frames[i + 1].info_next(i + 1 == m - 1) if i < m - 1 else None
        out.append((prev, f, nxt))
    return out


def normalise(frames):
    m = len(frames)
    return [f if (f.kind == "S" or i in (0, m - 1)) else f._replace(ub=NONE) for i, f in enumerate(frames)]


def reference(ch, L, val, served, rec):
    """reference (p, v2, nRN, nRR, nT) of line L from bbl_hall.values() / portions()"""
    a = ch.a
    nRN = nRR = 0
    for b in ch.blk:
        (P, i, l, d, X, C) = b
        if l != L or served[b]:
            continue
        nR = sum(1 for f in ((i - 1) % 6, (i + 1) % 6) if ch.st[P][f] == "R")
        nRR += nR == 2
        nRN += nR == 1
    return rec[L], int(2 * (val[L] + 1)), nRN, nRR, sum(1 for V in ch.a.rows[L] if V in ch.trip)


def check_line(ch, L, val, served, rec, dom_stats=None):
    """returns a list of error strings (empty = the line is a path of the automaton and the quantities agree)"""
    errs = []
    frames, hids = extract(ch, L)
    frames = normalise(frames)
    m = len(frames)
    if m < 2:
        return errs
    fset = _FRAMESET
    for f in frames:
        if f not in fset:
            errs.append(f"frame not enumerated: {f}")
    if frames[0].bin != NONE or frames[-1].bout != NONE:
        errs.append("end bits")
    for f, g in zip(frames, frames[1:]):
        if not edge_ok(f, g):
            errs.append(f"edge not allowed: {f} -> {g}")
    if not ends_compatible(frames[0], frames[-1]):
        errs.append("end compatibility violated")
    tot = [0, 0, 0, 0, 0]
    for (prev, cur, nxt), hid in zip(line_windows(frames), hids):
        if cur.kind == "T" and hid not in _domain(prev, cur, nxt):
            errs.append(f"hidden assignment outside domain at {cur} {hid}")
        v = exact_vec(prev, cur, nxt, hid)
        for k in range(5):
            tot[k] += v[k]
        if dom_stats is not None:
            dom_stats[(prev, cur, nxt)] += 1
    ref = reference(ch, L, val, served, rec)
    if tuple(tot) != ref:
        errs.append(f"mismatch automaton {tuple(tot)} vs reference {ref}")
    nS = sum(1 for f in frames if f.kind == "S")
    if (nS - (ch.a.n - 1)) % 2:
        errs.append("parity")
    return errs


_dom_cache = {}


def _domain(prev, cur, nxt):
    key = (prev, cur, nxt)
    if key not in _dom_cache:
        _dom_cache[key] = set(sig_domain(prev, cur, nxt, True))
    return _dom_cache[key]


_FRAMESET = frozenset(all_frames())


SKIPPED_INCOMPLETE = [0]


def iter_arrangements(paths, even_only=True, limit=10 ** 9, skip=0, mod=1, part=0):
    seen = set()
    k = 0
    for inp in paths:
        for r in records(inp):
            g = r["gens"] if isinstance(r["gens"], str) else " ".join(r["gens"])
            if g in seen:
                continue
            seen.add(g)
            k += 1
            if k % mod != part:
                continue
            try:
                ch = Charge(Arr(g, r.get("n")))
            except ValueError:
                continue
            if even_only and ch.a.n % 2:
                continue
            a = ch.a
            if any(sum(len(a.events[e]) - 1 for e in a.rows[L]) != a.n - 1 for L in range(a.n)):
                SKIPPED_INCOMPLETE[0] += 1      # some pair of lines never crosses: not a pseudoline arrangement
                continue
            yield g, ch
            limit -= 1
            if limit <= 0:
                return


def cmd_validate(args):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--limit", type=int, default=10 ** 9)
    ap.add_argument("--mod", type=int, default=1)
    ap.add_argument("--part", type=int, default=0)
    ap.add_argument("--odd", action="store_true", help="also accept odd n")
    ap.add_argument("--out", default=None)
    o = ap.parse_args(args)
    _imports()
    tot_arr = tot_lines = bad = 0
    windows = collections.Counter()
    frames_seen = collections.Counter()
    nclass = collections.Counter()
    for g, ch in iter_arrangements(o.inputs, not o.odd, o.limit, mod=o.mod, part=o.part):
        val, served = values(ch)
        rec = portions(ch)
        tot_arr += 1
        for L in range(ch.a.n):
            tot_lines += 1
            errs = check_line(ch, L, val, served, rec, windows)
            fr, _ = extract(ch, L)
            for f in normalise(fr):
                frames_seen[f] += 1
            if errs:
                bad += 1
                if bad <= 20:
                    print("ERROR", ch.a.n, L, g[:60], errs[:3], flush=True)
    print(f"skipped (incomplete words: some pair never crosses): {SKIPPED_INCOMPLETE[0]}")
    print(f"arrangements {tot_arr}, lines {tot_lines}, failing lines {bad}")
    print(f"distinct frames in data {len(frames_seen)} of {len(_FRAMESET)} enumerated; distinct windows {len(windows)}")
    if o.out:
        import pickle
        pickle.dump((dict(frames_seen), dict(windows), tot_arr, tot_lines, bad), open(o.out, "wb"))


def show(path):
    return " | ".join(f"{f.kind}[{f.bin}{f.bout}{'u' + str(f.ub) if f.ub != NONE else ''}{'h' + str(f.h) if f.kind == 'T' else ''}]"
                      for f in path)


def clean_frame(f):
    """clean line: no multiple point, caps no block"""
    return f.kind == "S" and not (f.bin[0] and f.bout[0]) and not (f.bin[1] and f.bout[1])


def cmd_m1(args):
    """L3: a clean line has a portion iff n is even (m = n-1 odd): min portions over locally consistent clean lines"""
    g = Graph(allow=clean_frame)
    for par, name in ((1, "n even (m = n-1 odd)"), (0, "n odd  (m = n-1 even)")):
        v, path = solve(g, (1, 0, 0), parity=par)
        print(f"clean lines, {name}: min portions = {v}")
        if path:
            print("   witness:", show(path))
    # ablation: without the end-compatibility fact F-F the parity argument alone gives nothing
    v, path = solve(Graph(allow=clean_frame, compat=False), (1, 0, 0), parity=1)
    print("ablation without F-F (end compatibility): even n min portions =", v, "|", show(path) if path else "")


INF_ = float("-inf")


def fmt(v, const=-1.0):
    """value of the objective (in halves) -> the bound on v_L"""
    if v is None:
        return "  n/a"
    if v == INF_:
        return " -inf"
    return f"{v / 2 + const:5.1f}"


def status(info, side):
    """U / I / M status of the block whose far end is the simple vertex described by `info` (kind, h, bits beyond, end flag)"""
    return "I" if info[3] else "U" if info[2] == NONE else "M"


def x_point(prev, cur, nxt):
    """cur is an isolated-X-point vertex on its axis L: both L-rays are blocks, the four other rays are N"""
    return (cur.kind == "T" and cur.bin == (1, 1) and cur.bout == (1, 1) and cur.h == NONE
            and prev is not None and nxt is not None and prev[0] == "S" and nxt[0] == "S")


def cap_count(prev, cur, nxt):
    return int(cur.kind == "S") * ((cur.bin[0] and cur.bout[0]) + (cur.bin[1] and cur.bout[1]))


def cmd_m2(args):
    g = Graph()
    print("== M2a: certified lower bounds  v_L + (a/2)*#(unserved RN) + (b/2)*#(unserved RR)  >=  bound   (all lines, all n)")
    print("   rows: a, columns: b = 0..6;  first table all n, second table even n (#simple vertices odd)")
    for par, name in ((None, "all n"), (1, "even n")):
        print(f"   [{name}]")
        print("   a\\b " + "".join(f"{b:6d}" for b in range(7)))
        for a in range(4):
            row = []
            for b in range(7):
                v, _ = solve(g, (0, 1, a, b, 0), parity=par)
                row.append(fmt(v))
            print(f"   {a:3d}  " + " ".join(row), flush=True)
    print("== M2b: X-point axes.  Bound on v_L + comp (a=1, b=3) over lines containing an X point with block statuses (W side, E side)")
    for par, name in ((None, "all n"), (1, "even n")):
        for sW in "UIM":
            for sE in "UIM":
                if sW > sE:
                    continue

                def feat(prev, cur, nxt, sW=sW, sE=sE):
                    if not x_point(prev, cur, nxt):
                        return False
                    return {status(prev, 0), status(nxt, 1)} == {sW, sE} and (sW == sE) == (status(prev, 0) == status(nxt, 1))
                v, path = solve(Graph(feat=feat), (0, 1, 1, 3, 0), parity=par, need_flag=True)
                print(f"   [{name}] X point with statuses ({sW},{sE}): min (v_L+comp) = {fmt(v)}", flush=True)
    print("== M2c: lines whose only triple points are isolated X points (any two triple points separated by simple vertices)")
    xonly = lambda f: f.kind == "S" or (f.bin == (1, 1) and f.bout == (1, 1) and f.h == NONE and f.ub == NONE)
    noTT = lambda c, n: not (c.kind == "T" and n.kind == "T")
    gx = Graph(allow=xonly, edge_allow=noTT)
    for par, name in ((None, "all n"), (1, "even n")):
        v, path = solve(gx, (0, 1, 0, 0, 0), parity=par)
        print(f"   [{name}] min v_L (raw, no compensation) = {fmt(v)}   witness {show(path) if path else ''}")
        for gamma in (1, 2, 3, 4):
            v, path = solve(gx, (0, 1, 0, 0, -gamma), parity=par)
            print(f"   [{name}] min (v_L - {gamma}/2 * #X) = {fmt(v)}", flush=True)
    print("== M2e: lines with at least one triple point and NO unserved RN/RR block (penalties a=b=50): bound on v_L")
    hasT = lambda prev, cur, nxt: cur.kind == "T"
    for par, name in ((None, "all n"), (1, "even n")):
        v, path = solve(Graph(feat=hasT), (0, 1, 50, 50, 0), parity=par, need_flag=True)
        print(f"   [{name}] min v_L = {fmt(v)}   {show(path) if path else ''}", flush=True)
    print("== M2f: what the relaxation allows without / with too little compensation: negative cycles (frames)")
    for (a, b) in ((0, 0), (1, 2), (0, 3)):
        v, cyc = solve(g, (0, 1, a, b, 0))
        print(f"   a={a} b={b}: {fmt(v)}   cycle: {show(cyc) if cyc else ''}", flush=True)
    print("== M2d: pure lines (no multiple point), even n")
    gp = Graph(allow=lambda f: f.kind == "S", cnt=cap_count)
    for cp in (0, 1):
        v, path = solve(gp, (1, 0, 0, 0, 0), parity=1, cnt_parity=cp)
        print(f"   #capped blocks {'odd' if cp else 'even'}: min portions = {v}   {show(path) if path else ''}")

    def bad_cap(prev, cur, nxt):
        return cur.kind == "S" and ((cur.bin[0] and cur.bout[0] and not cur.ub[1]) or (cur.bin[1] and cur.bout[1] and not cur.ub[0]))
    v, path = solve(Graph(allow=lambda f: f.kind == "S", feat=bad_cap), (1, 0, 0, 0, 0), parity=1, need_flag=True)
    print(f"   pure line, n even, capping a block whose axis has a bounded segment beyond X (status U/M): min portions = {v}")


def layered_min(obj, parity, maxlen, allow=lambda f: True, edge_allow=lambda c, n: True, cnt=None, cnt_parity=None,
                feat=None, need_flag=False, compat=True):
    """independent implementation: forward DP by exact path length (no graph, no Bellman-Ford), lengths 2..maxlen"""
    frames = [f for f in all_frames() if allow(f)]
    by_bin = collections.defaultdict(list)
    for f in frames:
        by_bin[f.bin].append(f)

    def w(prev, cur, nxt):
        return min(sum(c * x for c, x in zip(obj, v)) for v in options(prev, cur, nxt))

    best = None
    # state: (prevInfo, cur, role, par, cls, flag, cp) -> min cost so far (cost of all windows before cur)
    layer = {}
    for f in frames:
        if f.bin == NONE:
            layer[(None, f, 0, 1 if f.kind == "S" else 0, f.ub, 0, 0)] = 0
    for length in range(1, maxlen):
        nxt_layer = {}
        for (prev, cur, role, par, cls, flag, cp), cost in layer.items():
            if role:
                continue
            for nx in by_bin[cur.bout]:
                if not edge_ok(cur, nx) or not edge_allow(cur, nx):
                    continue
                for last in (0, 1):
                    if last and nx.bout != NONE:
                        continue
                    if nx.kind == "T" and nx.ub != NONE and not last:
                        continue
                    ni = nx.info_next(bool(last))
                    fl, c2 = flag, cp
                    if feat and feat(prev, cur, ni):
                        fl = 1
                    if cnt:
                        c2 = (cp + cnt(prev, cur, ni)) % 2
                    key = (cur.info_prev(prev is None), nx, last, (par + (nx.kind == "S")) % 2, cls, fl, c2)
                    val = cost + w(prev, cur, ni)
                    if key not in nxt_layer or val < nxt_layer[key]:
                        nxt_layer[key] = val
        layer = nxt_layer
        for (prev, cur, role, par, cls, flag, cp), cost in layer.items():
            if not role or (compat and not ends_compatible_cls(cls, cur)):
                continue
            fl, c2 = flag, cp
            if feat and feat(prev, cur, None):
                fl = 1
            if cnt:
                c2 = (cp + cnt(prev, cur, None)) % 2
            if (parity is not None and par != parity) or (need_flag and not fl) or (cnt_parity is not None and c2 != cnt_parity):
                continue
            tot = cost + w(prev, cur, None)
            if best is None or tot < best[0]:
                best = (tot, length + 1)
    return best


def cmd_crosscheck(args):
    """compare Bellman-Ford results with the independent layered DP (exact for finite minima attained by short paths)"""
    maxlen = int(args[0]) if args else 14
    tests = [
        ("M1 even n", dict(obj=(1, 0, 0, 0, 0), parity=1, allow=clean_frame)),
        ("M1 odd n", dict(obj=(1, 0, 0, 0, 0), parity=0, allow=clean_frame)),
        ("M2a a=1 b=3", dict(obj=(0, 1, 1, 3, 0), parity=None)),
        ("M2a a=1 b=3 even", dict(obj=(0, 1, 1, 3, 0), parity=1)),
        ("M2a a=0 b=6 (-inf expected: layered value keeps falling)", dict(obj=(0, 1, 0, 6, 0), parity=None)),
        ("M2a a=1 b=2 (-inf expected)", dict(obj=(0, 1, 1, 2, 0), parity=None)),
        ("X-only raw", dict(obj=(0, 1, 0, 0, 0), parity=1,
                            allow=lambda f: f.kind == "S" or (f.bin == (1, 1) and f.bout == (1, 1) and f.h == NONE and f.ub == NONE),
                            edge_allow=lambda c, n: not (c.kind == "T" and n.kind == "T"))),
    ]
    for name, kw in tests:
        kw2 = {k: v for k, v in kw.items() if k in ("allow", "edge_allow")}
        v, _ = solve(Graph(**kw2), kw["obj"], parity=kw["parity"])
        lm = [layered_min(maxlen=L, **kw) for L in (6, 10, maxlen)]
        print(f"{name}: BF = {v};  layered min over lengths <= 6/10/{maxlen}: {[x[0] if x else None for x in lm]}", flush=True)


def cmd_datamin(args):
    """minimum over data of v_L (+comp) per X-point feature: shows how tight the certified bounds are"""
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--limit", type=int, default=10 ** 9)
    ap.add_argument("--mod", type=int, default=1)
    ap.add_argument("--part", type=int, default=0)
    o = ap.parse_args(args)
    _imports()
    best = {}
    n_arr = 0
    for g, ch in iter_arrangements(o.inputs, True, o.limit, mod=o.mod, part=o.part):
        val, served = values(ch)
        rec = portions(ch)
        n_arr += 1
        for L in range(ch.a.n):
            frames, hids = extract(ch, L)
            frames = normalise(frames)
            if len(frames) < 2:
                continue
            ref = reference(ch, L, val, served, rec)
            v = ref[1] / 2 - 1
            comp = v + ref[2] / 2 + 1.5 * ref[3]
            feats = ["all"]
            if ref[4] == 0:
                feats.append("pure")
            for (prev, cur, nxt) in line_windows(frames):
                if x_point(prev, cur, nxt):
                    feats.append("X(%s,%s)" % tuple(sorted((status(prev, 0), status(nxt, 1)))))
            for f in set(feats):
                b = best.setdefault(f, [10 ** 9, 10 ** 9, 0])
                b[0] = min(b[0], v)
                b[1] = min(b[1], comp)
                b[2] += 1
    print(f"{n_arr} arrangements")
    for f, b in sorted(best.items()):
        print(f"  {f:10s} lines {b[2]:9d}  min v_L = {b[0]:5.1f}   min (v_L + comp) = {b[1]:5.1f}")


def cmd_coverage(args):
    """enumerated frames / windows versus those seen in the validation runs (pickles written by `validate --out`)"""
    import pickle
    frames_seen, windows_seen = collections.Counter(), collections.Counter()
    for f in args:
        fs, ws, *_ = pickle.load(open(f, "rb"))
        frames_seen.update(fs)
        windows_seen.update(ws)
    fr = all_frames()
    pi, ni = collections.defaultdict(set), collections.defaultdict(set)
    for f in fr:
        pi[f.bout].add((f.kind, f.h, f.bin, False))
        ni[f.bin].add((f.kind, f.h, f.bout, False))
    print(f"frames: enumerated {len(fr)} (S {sum(f.kind == 'S' for f in fr)}, T {sum(f.kind == 'T' for f in fr)}), "
          f"seen in data {len(frames_seen)}")
    nw = set()
    for c in fr:
        if c.kind == "T" and c.ub != NONE and c.bin != NONE and c.bout != NONE:
            continue
        for p_ in list(pi[c.bin]) + ([None] if c.bin == NONE else []):
            for n_ in list(ni[c.bout]) + ([None] if c.bout == NONE else []):
                nw.add((p_, c, n_))
    print(f"windows: bounded enumeration {len(nw)} (interior/ends, end flags ignored), distinct windows seen {len(windows_seen)}")
    unseen = [f for f in fr if f not in frames_seen]
    print(f"unseen frames ({len(unseen)}):")
    for f in unseen:
        print("   ", show([f]))
    return frames_seen


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "validate":
        cmd_validate(args)
    elif cmd == "m1":
        cmd_m1(args)
    elif cmd == "m2":
        cmd_m2(args)
    elif cmd == "crosscheck":
        cmd_crosscheck(args)
    elif cmd == "datamin":
        cmd_datamin(args)
    elif cmd == "coverage":
        cmd_coverage(args)
    else:
        print("unknown command")


if __name__ == "__main__":
    main()

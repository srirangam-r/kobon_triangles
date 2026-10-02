"""Extra PROVEN local facts for the line automaton (task T23).  Pure Python, no SAT dependency at run time.

A *fact* is a forbidden positive pattern along a line L:
    slots   consecutive vertices of L, kind 'S' (simple) or 'T' (triple); T slots may carry hidden-sector bits h = (h+, h-)
    seg     triangle bits (top, bottom) of the segments between consecutive slots
    apex    multiplicity of the third vertex of a segment triangle (1 = triple point, 2 = simple)
    sig     multiplicity of the far end of a hidden ray (E+, E-, W+, W-) of a T slot (1 = triple)
Every fact was refuted by a SAT search over pseudoline arrangements (work/eng/T23/patsat.py):  the pattern's witness lines
(L, the lines through its vertices, the sides of its triangles, the lines through its far ends; at most K of them) form a
restriction of any arrangement containing the pattern that still contains the pattern (dropping lines keeps triangles,
multiplicities, consecutiveness), and no arrangement of K' <= K pseudolines does.  Hence the pattern occurs in NO arrangement,
for every n.  Only positive information (triangle exists, multiplicity) is used, so a fact also kills every frame sequence
that contains the pattern, whatever its other bits are.  Each fact is invariant under the two mirror symmetries
(reverse the direction of L; swap the sides +/-), so all four images are matched.

Interface
    window_forbidden(prev, cur, nxt, sig=None) -> fact name | None   (prev/nxt are Info tuples of line_automaton, cur a (E)Frame;
                                                                      sig = (E+, E-, W+, W-) of a T frame, or None for 'any')
    sig_allowed(prev, cur, nxt)            -> list of the sig tuples of `cur` not excluded by any fact  (T frames)
    edge_forbidden(cur, nxt)               -> fact name | None                (two enriched frames)
    kgram_forbidden(frames, hids=None)     -> fact name | None                (consecutive frames; hids = harvest sig codes or None)
    line_forbidden(frames, hids=None)      -> fact name | None                (a whole line)
    edge_allow(cur, nxt)                   -> bool     plug into line_automaton.Graph(edge_allow=...) / rule_lp.WGraph(edge_allow=...)
    install(LA)                            monkey-patches LA.sig_domain (drops hidden assignments) and LA.options (drops windows)
    FactGraph(LA)                          subclass of LA.Graph that removes forbidden windows and edges

Frames must carry `ain`/`aout` (rule_lp.EFrame) for the apex-flag facts to apply; plain line_automaton.Frame works too (facts
that need apex flags then simply do not fire).
"""
import itertools

FACTS = []            # filled from FACT_TABLE below
RAYS = ("E+", "E-", "W+", "W-")


class Pat:
    __slots__ = ("slots", "seg", "apex", "sig")

    def __init__(self, slots, seg, apex=None, sig=None):
        self.slots = [(k, tuple(h)) for k, h in slots]
        self.seg = {int(s): tuple(b) for s, b in dict(seg).items() if tuple(b) != (0, 0)}
        self.apex = {(int(s), int(sg)): int(v) for (s, sg), v in dict(apex or {}).items()}
        self.sig = {(int(s), r): int(v) for (s, r), v in dict(sig or {}).items()}


def flip_sides(p):
    rr = {"E+": "E-", "E-": "E+", "W+": "W-", "W-": "W+"}
    return Pat([(k, (h[1], h[0])) for k, h in p.slots], {s: (b[1], b[0]) for s, b in p.seg.items()},
               {(s, 1 - sg): v for (s, sg), v in p.apex.items()}, {(s, rr[r]): v for (s, r), v in p.sig.items()})


def reverse(p):
    m = len(p.slots)
    rr = {"E+": "W+", "W+": "E+", "E-": "W-", "W-": "E-"}
    return Pat(list(reversed(p.slots)), {m - 2 - s: b for s, b in p.seg.items()},
               {(m - 2 - s, sg): v for (s, sg), v in p.apex.items()}, {(m - 1 - s, rr[r]): v for (s, r), v in p.sig.items()})


def variants(p):
    c = reverse(p)
    return [p, flip_sides(p), c, flip_sides(c)]


def used_lines(p):
    """for each slot the set of its lines ('p' = E+/W- carrier, 'q' = W+/E- carrier) used by the elements of the pattern"""
    used = [set() for _ in p.slots]
    for s, b in p.seg.items():
        for sg in (0, 1):
            if b[sg]:
                used[s].add("p" if sg == 0 else "q")
                used[s + 1].add("q" if sg == 0 else "p")
    for s, (k, h) in enumerate(p.slots):
        if k == "T" and (h[0] or h[1]):
            used[s] |= {"p", "q"}
    for (s, r), v in p.sig.items():
        k, h = p.slots[s]
        if k == "T" and h[0 if r[1] == "+" else 1]:
            used[s] |= {"p", "q"}
    return used


class Fact:
    def __init__(self, name, slots, seg, apex=None, sig=None, note="", lines=None, span=None):
        self.name = name
        self.pat = Pat(slots, seg, apex, sig)
        self.note, self.lines = note, lines
        self.vars = variants(self.pat)
        self.relax = [[len(u) <= 1 for u in used_lines(v)] for v in self.vars]
        self.span = len(self.pat.slots)
        self.has_sig = bool(self.pat.sig)

    def matches(self, w, use_sig=True):
        """does the positive pattern `w` (Pat) contain this fact (in some orientation)?"""
        for v, rel in zip(self.vars, self.relax):
            m, n = len(v.slots), len(w.slots)
            if m > n:
                continue
            if v.sig and not use_sig:
                continue
            for o in range(n - m + 1):
                if _contains(v, rel, w, o):
                    return True
        return False


def _contains(v, rel, w, o):
    for i, (k, h) in enumerate(v.slots):
        wk, wh = w.slots[o + i]
        if k == "T":
            if wk != "T" or (h[0] and not wh[0]) or (h[1] and not wh[1]):
                return False
        elif wk == "T" and not rel[i]:
            return False
    for s, b in v.seg.items():
        wb = w.seg.get(o + s)
        if wb is None or (b[0] and not wb[0]) or (b[1] and not wb[1]):
            return False
    for (s, sg), a in v.apex.items():
        if w.apex.get((o + s, sg)) != a:
            return False
    for (s, r), a in v.sig.items():
        if w.sig.get((o + s, r)) != a:
            return False
    return True


# ---------------------------------------------------------------------------------------------- pattern constructors
def pat_from_window(prev, cur, nxt, sig=None):
    slots, seg, apex = [], {}, {}
    if prev is not None and prev[2] != (0, 0):
        slots.append(("T", (0, 0)) if prev[2] == (1, 1) else ("S", (0, 0)))
    if prev is not None:
        slots.append((prev[0], prev[1] if prev[0] == "T" else (0, 0)))
    c = len(slots)
    slots.append((cur.kind, cur.h if cur.kind == "T" else (0, 0)))
    if nxt is not None:
        slots.append((nxt[0], nxt[1] if nxt[0] == "T" else (0, 0)))
    if nxt is not None and nxt[2] != (0, 0):
        slots.append(("T", (0, 0)) if nxt[2] == (1, 1) else ("S", (0, 0)))
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
        for r, v in zip(RAYS, sig):
            if v is not None:
                sg_[(c, r)] = v
    return Pat(slots, seg, apex, sg_)


def pat_from_frames(frames, hids=None):
    slots, seg, apex, sig = [], {}, {}, {}
    f0, fl = frames[0], frames[-1]
    if f0.bin != (0, 0):
        slots.append(("T", (0, 0)) if f0.bin == (1, 1) else ("S", (0, 0)))
        seg[0] = f0.bin
    base = len(slots)
    for f in frames:
        slots.append((f.kind, f.h if f.kind == "T" else (0, 0)))
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
        if hids is not None and hids[i] is not None and f.kind == "T":
            h = hids[i]
            for k, r in enumerate(RAYS):
                sig[(base + i, r)] = (h >> k) & 1 if isinstance(h, int) else h[0][k]
    return Pat(slots, seg, apex, sig)


# ---------------------------------------------------------------------------------------------- queries
def _first(w, use_sig=True, span=None):
    for f in FACTS:
        if span is not None and f.span > span:
            continue
        if f.matches(w, use_sig):
            return f.name
    return None


_wcache = {}


def window_forbidden(prev, cur, nxt, sig=None):
    key = (prev[:3] if prev else None, cur, nxt[:3] if nxt else None, sig)
    r = _wcache.get(key, 0)
    if r == 0:
        r = _wcache[key] = _first(pat_from_window(prev, cur, nxt, sig), use_sig=sig is not None)
    return r


def sig_allowed(prev, cur, nxt):
    """sig tuples of the T frame `cur` that are not excluded (sig-conditioned facts) -- assuming the window itself is allowed"""
    if cur.kind != "T":
        return [()]
    return [s for s in itertools.product((0, 1), repeat=4) if window_forbidden(prev, cur, nxt, s) is None]


def edge_forbidden(cur, nxt):
    return _first(pat_from_frames([cur, nxt]))


def kgram_forbidden(frames, hids=None):
    return _first(pat_from_frames(list(frames), hids), use_sig=hids is not None)


line_forbidden = kgram_forbidden


def edge_allow(cur, nxt):
    return edge_forbidden(cur, nxt) is None


# ---------------------------------------------------------------------------------------------- plugging into T20
def install(LA):
    """monkey-patch line_automaton: hidden assignments contradicting a fact are dropped (sig_domain); windows contradicting a
    sig-free fact get NO option (options() returns an empty frozenset, which Graph must skip: use FactGraph)."""
    orig_sig = LA.sig_domain

    def sig_domain(prev, cur, nxt, full_g=False):
        for sig, g in orig_sig(prev, cur, nxt, full_g):
            if window_forbidden(prev, cur, nxt, tuple(sig)) is None:
                yield sig, g
    LA.sig_domain = sig_domain
    LA._opt_cache.clear()
    LA._dom_cache.clear()


def make_fact_graph(LA):
    """returns FactGraph, a subclass of LA.Graph whose product graph omits every edge / terminal whose window (prev, cur, next)
    is forbidden by a sig-free fact and every edge (cur, next) forbidden as a pair.  Windows whose facts involve a sig are
    handled by install() (they restrict sig_domain).  Facts spanning more than the window need a k-gram state (see kgram_forbidden)."""
    NONE = LA.NONE

    class FactGraph(LA.Graph):
        def objective_weights(self, obj):
            node_id, nodes = {}, []

            def nid(x):
                if x not in node_id:
                    node_id[x] = len(nodes)
                    nodes.append(x)
                return node_id[x]

            def wmin(prev, cur, nxt):
                return min(sum(c * x for c, x in zip(obj, v)) for v in LA.options(prev, cur, nxt))

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
                    if (not self.compat or LA.ends_compatible_cls(cls, cur)) and window_forbidden(prev, cur, None) is None \
                            and LA.options(prev, cur, None):
                        fl2, cp2 = upd(prev, cur, None, flag, cp)
                        terms.append((u, wmin(prev, cur, None), fl2, par, cp2))
                    continue
                for nxt in self.by_bin[cur.bout]:
                    if not LA.edge_ok(cur, nxt) or not self.edge_allow(cur, nxt) or edge_forbidden(cur, nxt) is not None:
                        continue
                    for last in (0, 1):
                        if last and nxt.bout != NONE:
                            continue
                        if nxt.kind == "T" and nxt.ub != NONE and not last:
                            continue
                        ni = nxt.info_next(bool(last))
                        if window_forbidden(prev, cur, ni) is not None or not LA.options(prev, cur, ni):
                            continue
                        fl2, cp2 = upd(prev, cur, ni, flag, cp)
                        y = (cur.info_prev(prev is None), nxt, (par + (nxt.kind == "S")) % 2, cls, fl2, last, cp2)
                        if y not in seen:
                            seen.add(y)
                            stack.append(y)
                        nid(y)
                        edges.append((u, node_id[y], wmin(prev, cur, ni)))
            return nodes, starts, edges, terms
    return FactGraph




# ---- FACT_TABLE begin (generated by work/eng/T23/gen_facts.py)
FACT_TABLE = [
    {'name': 'P000', 'slots': [('T', (0, 1)), ('T', (1, 0))], 'seg': [(0, (1, 1))], 'apex': [(0, 0, 2), (0, 1, 2)], 'sig': [], 'lines': 7},
    {'name': 'P001', 'slots': [('S', (0, 0)), ('T', (0, 1))], 'seg': [(0, (1, 1))], 'apex': [(0, 1, 2)], 'sig': [], 'lines': 5},
    {'name': 'P002', 'slots': [('S', (0, 0)), ('T', (0, 1)), ('S', (0, 0))], 'seg': [(0, (0, 1)), (1, (0, 1))], 'apex': [(0, 1, 2), (1, 1, 2)], 'sig': [], 'lines': 6},
    {'name': 'P003', 'slots': [('T', (0, 1)), ('T', (1, 1)), ('T', (1, 0))], 'seg': [(0, (1, 1)), (1, (1, 1))], 'apex': [(0, 0, 2), (1, 1, 2)], 'sig': [], 'lines': 11},
    {'name': 'P004', 'slots': [('T', (0, 1)), ('S', (0, 0)), ('T', (1, 0))], 'seg': [(0, (1, 1)), (1, (1, 1))], 'apex': [], 'sig': [], 'lines': 8},
    {'name': 'P005', 'slots': [('S', (0, 0)), ('T', (0, 1)), ('T', (0, 1)), ('S', (0, 0))], 'seg': [(0, (0, 1)), (1, (0, 1)), (2, (0, 1))], 'apex': [(0, 1, 2), (2, 1, 2)], 'sig': [], 'lines': 9},
    {'name': 'P006', 'slots': [('S', (0, 0)), ('S', (0, 0)), ('T', (0, 1)), ('S', (0, 0))], 'seg': [(0, (0, 1)), (1, (0, 1)), (2, (0, 1))], 'apex': [(2, 1, 2)], 'sig': [], 'lines': 7},
    {'name': 'P007', 'slots': [('S', (0, 0)), ('S', (0, 0)), ('S', (0, 0)), ('S', (0, 0))], 'seg': [(0, (0, 1)), (1, (0, 1)), (2, (0, 1))], 'apex': [], 'sig': [], 'lines': 5},
    {'name': 'P008', 'slots': [('S', (0, 0)), ('S', (0, 0)), ('T', (0, 1)), ('T', (0, 1)), ('S', (0, 0))], 'seg': [(0, (0, 1)), (1, (0, 1)), (2, (0, 1)), (3, (0, 1))], 'apex': [(3, 1, 2)], 'sig': [], 'lines': 10},
    {'name': 'P009', 'slots': [('S', (0, 0)), ('S', (0, 0)), ('T', (0, 1)), ('S', (0, 0)), ('S', (0, 0))], 'seg': [(0, (0, 1)), (1, (0, 1)), (2, (0, 1)), (3, (0, 1))], 'apex': [], 'sig': [], 'lines': 8},
]
# ---- FACT_TABLE end

for _t in FACT_TABLE:
    FACTS.append(Fact(_t['name'], _t['slots'], dict(_t['seg']), {(s, sg): v for s, sg, v in _t['apex']}, {(s, r): v for s, r, v in _t['sig']}, lines=_t['lines']))

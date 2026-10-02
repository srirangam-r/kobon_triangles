# For an arrangement with an all-8 point P: try windows = P plus subsets of its neighbour events (made contiguous by
# commuting, closing under blocking tokens), enumerate every redrawing with the same crossing set (wdpw), splice the
# representative words back and recompute T, V exactly.  Report the best (dT, dV).
import sys, json, itertools
sys.path[:0] = ["/home/nail/stuff/sundai_math/work/t3", "/home/nail/stuff/sundai_math/work/eng/pert2", "/home/nail/stuff/sundai_math/work/eng/star", "/home/nail/stuff/sundai_math/work/eng/comp"]
from arr import Arr, rays, far_end
from window import crossing_set
from wdpw import outcomes_w
from bad_comp import tri_sectors

def tok_span(tok):
    g = int(tok.rstrip("*")); return g, g + 1 + tok.count("*")

def event_tokens(gens, n):
    """map token index -> event index of Arr (Arr numbers events in token order)"""
    return list(range(len(gens)))

def make_adjacent(toks, idxs):
    toks = list(toks); pos = sorted(idxs)
    for t in range(1, len(pos)):
        while pos[t] > pos[t - 1] + 1:
            j = pos[t]; a0, a1 = tok_span(toks[j]); b0, b1 = tok_span(toks[j - 1])
            if a1 < b0 or b1 < a0:
                toks[j - 1], toks[j] = toks[j], toks[j - 1]; pos[t] -= 1
            else:
                return None, j - 1
    return toks, pos[0]

def closure_window(toks, idxs, maxk):
    """indices (in the ORIGINAL token list) of a contiguous-able set containing idxs; None if span exceeds maxk"""
    S = set(idxs)
    while True:
        lo = min(tok_span(toks[i])[0] for i in S); hi = max(tok_span(toks[i])[1] for i in S)
        if hi - lo + 1 > maxk: return None
        # tokens strictly between min(S) and max(S) that overlap the track span [lo, hi] must be in the window
        add = {i for i in range(min(S), max(S) + 1) if i not in S and not (tok_span(toks[i])[1] < lo or tok_span(toks[i])[0] > hi)}
        if not add: return sorted(S)
        S |= add

def try_window(gens, n, idxs, T0, V0, maxk=9, cache={}):
    toks = gens.split()
    W = closure_window(toks, idxs, maxk)
    if W is None: return None
    # move tokens outside the span that lie between out of the way: they commute with the window (disjoint tracks)
    lo = min(tok_span(toks[i])[0] for i in W); hi = max(tok_span(toks[i])[1] for i in W)
    inner = [i for i in range(W[0], W[-1] + 1) if i not in W]
    new = toks[:W[0]] + [toks[i] for i in inner] + [toks[i] for i in W] + toks[W[-1] + 1:]
    s = W[0] + len(inner); blk = [toks[i] for i in W]
    k = hi - lo + 1
    w0 = [(tok_span(t)[0] - lo, tok_span(t)[1] - lo) for t in blk]
    req, _ = crossing_set(k, w0)
    key = (k, req)
    if key not in cache: cache[key] = outcomes_w(k, req)
    best = (-99, 0, None)
    for (vec, tl, nv), w in cache[key].items():
        cand = new[:s] + [str(lo + i) + "*" * (j - i - 1) for (i, j) in w] + new[s + len(blk):]
        b = Arr(" ".join(cand), n); dT = b.T() - T0; dV = len(b.events) - V0
        if (dT, dV) > best[:2]: best = (dT, dV, " ".join(cand))
    return k, len(W), best

if __name__ == "__main__":
    for line in sys.stdin:
        d = json.loads(line); g = d["gens"]; n = d["n"]
        a = Arr(g, n); T0, V0 = a.T(), len(a.events)
        for P, ev in enumerate(a.events):
            if len(ev) != 4 or sum(tri_sectors(a, P)) != 8: continue
            nb = sorted({far_end(a, P, r) for r in rays(a, P) if far_end(a, P, r) is not None})
            res = []
            for m in range(1, 4):
                for sub in itertools.combinations(nb, m):
                    r = try_window(g, n, [P] + list(sub), T0, V0)
                    if r: res.append((r[2][0], r[2][1], r[0], sub))
            res.sort(reverse=True)
            print(n, "T", T0, "P", P, "windows tried", len(res), "best", res[:3])

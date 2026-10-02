# Direct reducibility test on a real arrangement: rearrange a set of events that are consecutive tokens of
# the gens word (after commuting moves), over the tracks they span; recompute T and V for every reduced word.
import sys, itertools
sys.path.insert(0, __import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/work/t3"); sys.path.insert(0, __import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/work/eng/pert2")
from arr import Arr
from window import crossing_set, all_words

def tok_span(tok):
    g = int(tok.rstrip("*")); return g, g + 1 + tok.count("*")

def make_adjacent(gens, idxs):
    """move the tokens idxs (sorted) together by commuting past disjoint-track tokens; return (newgens, start)"""
    toks = list(gens); idxs = sorted(idxs)
    # bubble each later chosen token leftwards to follow the previous one
    pos = list(idxs)
    for t in range(1, len(pos)):
        while pos[t] > pos[t-1] + 1:
            j = pos[t]; a0, a1 = tok_span(toks[j]); b0, b1 = tok_span(toks[j-1])
            if a1 < b0 or b1 < a0:          # disjoint tracks -> commute
                toks[j-1], toks[j] = toks[j], toks[j-1]; pos[t] -= 1
            else:
                return None
    return toks, pos[0]

def test(gens, idxs, n=None):
    gens = gens.split(); a = Arr(" ".join(gens), n); T0 = a.T(); V0 = len(a.events)
    r = make_adjacent(gens, idxs)
    if r is None: return None
    toks, s = r; blk = toks[s:s+len(idxs)]
    lo = min(tok_span(t)[0] for t in blk); hi = max(tok_span(t)[1] for t in blk)
    k = hi - lo + 1
    w0 = [(tok_span(t)[0] - lo, tok_span(t)[1] - lo) for t in blk]
    req, _ = crossing_set(k, w0)
    best = []
    for w in all_words(k, req):
        if list(w) == w0: continue
        new = toks[:s] + [str(lo + i) + "*" * (j - i - 1) for (i, j) in w] + toks[s+len(idxs):]
        b = Arr(" ".join(new), a.n); dT = b.T() - T0; dV = len(b.events) - V0
        best.append((dT, dV, w))
    best.sort(reverse=True)
    return T0, best[:5]

if __name__ == "__main__":
    import json
    gens = sys.argv[1]; idxs = [int(x) for x in sys.argv[2].split(",")]
    print(test(gens, idxs))

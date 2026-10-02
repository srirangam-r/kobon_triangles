"""pair optimality lemma (THEORY section 25, work/eng/pert2/pair_PQ_all.json): a 4-fold vertex P consecutive on a line with a triple vertex Q is allowed only if the canonical
(P sectors, Q sectors) pattern is in the 'allowed' list.  Frame fields -> canonical pattern.
P (M frame): bin, bout, h = (hE+, hE-, hW+, hW-); Q (T frame): bin, bout, h = (middle sector on side +, side -).
Listing convention: sectors in one rotational sense starting right after the ray P->Q (resp. Q->P)."""
import json
_AL = None
def allowed_set():
    global _AL
    if _AL is None:
        d = json.load(open(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/work/eng/pert2/pair_PQ_all.json"))
        _AL = {tuple(x) for x in d["allowed"]}
        import os
        if os.environ.get("PAIRDROP"):       # diagnostic (NOT a sound filter): remove patterns "P:Q;P:Q" from the allowed list
            _AL -= {tuple(t.split(":")) for t in os.environ["PAIRDROP"].split(";")}
        if os.environ.get("PAIRONLY"):       # diagnostic: allow only these patterns
            _AL &= {tuple(t.split(":")) for t in os.environ["PAIRONLY"].split(";")}
        ex = {tuple(x) for x in d["excluded"]}
        assert not (_AL & ex)
        _AL_FULL = None
        globals()["_EX"] = ex
    return _AL
def _s(bits): return "".join(str(int(b)) for b in bits)
def canon_frames(order, Mbin, Mbout, Mh, Tbin, Tbout, Th):
    """order 'MT': M first along the line direction of the bits (P=M, Q=T); 'TM': T first"""
    if order == "MT":
        PA = (Mbout[0], Mh[0], Mh[2], Mbin[0], Mbin[1], Mh[3], Mh[1], Mbout[1])
        QA = (Tbin[1], Th[1], Tbout[1], Tbout[0], Th[0], Tbin[0])
        PB = tuple(reversed(PA))
        QB = (Tbin[0], Th[0], Tbout[0], Tbout[1], Th[1], Tbin[1])
    else:
        PA = (Mbin[1], Mh[3], Mh[1], Mbout[1], Mbout[0], Mh[0], Mh[2], Mbin[0])
        QA = (Tbout[0], Th[0], Tbin[0], Tbin[1], Th[1], Tbout[1])
        PB = tuple(reversed(PA))
        QB = (Tbout[1], Th[1], Tbin[1], Tbin[0], Th[0], Tbout[0])
    return min((_s(PA), _s(QA)), (_s(PB), _s(QB)))
_cache = {}
def pair_ok(order, Mbin, Mbout, Mh, Tbin, Tbout, Th):
    k = (order, tuple(Mbin), tuple(Mbout), tuple(Mh), tuple(Tbin), tuple(Tbout), tuple(Th))
    r = _cache.get(k)
    if r is None:
        r = _cache[k] = canon_frames(*k) in allowed_set()
    return r

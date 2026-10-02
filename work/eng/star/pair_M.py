# Pair lemmas for a BAD 4-fold point P consecutive on a line with (a) a simple vertex X (k=5), (b) a bad 4-fold Q (k=7).
# Exclusion criterion as in work/eng/pert2/pair_PQ_all.py; options enumerated by the validated DP (wdp.outcomes).
import itertools, json, sys
import numpy as np
sys.path[:0] = ["/home/nail/stuff/sundai_math/work/eng/pert2", "/home/nail/stuff/sundai_math/work/eng/star"]
from window import crossing_set, faces
from wdp import outcomes
BAD = {"11111111", "11111110"}          # all-8, 7-type (6-type excluded by certificate; not needed here)
def rotations(w): return {w[i:] + w[:i] for i in range(len(w))} | {(w[::-1])[i:] + (w[::-1])[:i] for i in range(len(w))}
BADW = set().union(*[rotations(w) for w in BAD])

def run(k, w0, Pccw, Qccw, Pcw, Qcw, qbad, name):
    req, _ = crossing_set(k, w0)
    vec0, t0, nv0, inc = faces(k, w0)
    assert sorted(inc[0]) == sorted(Pccw) and sorted(inc[1]) == sorted(Qccw), (inc, Pccw, Qccw)
    vec0c = tuple(min(x, 4) for x in vec0)
    opts = [o for o in outcomes(k, req) if not (o[0] == vec0c and o[1] == t0 and o[2] == nv0)]
    V = np.array([q[0] for q in opts]); TL = np.array([q[1] for q in opts]); NV = np.array([q[2] for q in opts])
    nf = len(vec0); status = {}
    for bits in itertools.product((0, 1), repeat=nf):
        pw = "".join(str(bits[f]) for f in Pccw)
        if pw not in BADW: continue
        qw = "".join(str(bits[f]) for f in Qccw)
        if qbad and qw not in BADW: continue
        choices = []
        for f in range(nf):
            if bits[f]:
                o = 3 - vec0[f]
                if o < 0: choices = None; break
                choices.append([o])
            else:
                choices.append([o for o in (0, 1, 2, 3) if (o == 3 or vec0[f] + o >= 3) and vec0[f] + o != 3])
        if choices is None: continue
        key = min(("".join(str(bits[f]) for f in Pccw), "".join(str(bits[f]) for f in Qccw)),
                  ("".join(str(bits[f]) for f in Pcw), "".join(str(bits[f]) for f in Qcw)))
        tri0 = np.array(bits, dtype=bool); irr = False
        for outs in itertools.product(*choices):
            o = np.array(outs); tri1 = (V + o[None] == 3) & (o[None] < 3)
            dT = tri1.sum(1) - tri0.sum() + TL - t0
            if not ((dT > 0) | ((dT == 0) & (NV > nv0))).any():
                irr = True; break
        status[key] = status.get(key, False) or irr
    ex = sorted(k_ for k_, v in status.items() if not v); al = sorted(k_ for k_, v in status.items() if v)
    print(name, "vec0", vec0, "options", len(opts), "patterns", len(status), "excluded", len(ex), "allowed", len(al), flush=True)
    for p in al: print("   allowed", p)
    json.dump({"excluded": ex, "allowed": al, "convention": "P sectors then Q sectors, same rotational sense, starting right after the ray P->Q / Q->P; canonical = min over both senses"}, open(f"pair_{name}.json", "w"), indent=0)

# (a) 4-fold P (tracks 1..4) then simple X (tracks 0,1); shared wire 4.  Faces: top0 bottom1 left_g=1+g right_g=5+g.
run(5, [(1, 4), (0, 1)], [2, 3, 4, 5, 1, 9, 8, 7], [7, 6, 0, 2], [7, 8, 9, 1, 5, 4, 3, 2], [2, 0, 6, 7], False, "MS")
# (b) 4-fold P (tracks 3..6) then 4-fold Q (tracks 0..3); shared wire 6.  Faces: top0 bottom1 left_g=1+g right_g=7+g.
run(7, [(3, 6), (0, 3)], [4, 5, 6, 7, 1, 13, 12, 11], [11, 10, 9, 8, 0, 2, 3, 4], [11, 12, 13, 1, 7, 6, 5, 4], [4, 3, 2, 0, 8, 9, 10, 11], True, "MM")

# Pair lemma for two TRIPLE points P, Q consecutive on a line (window k=5, w0 = [(2,4),(0,2)]; shared wire 4).
# Same exclusion criterion as work/eng/pert2/pair_PQ_all.py: a (P bits, Q bits) pattern is EXCLUDED iff every
# outside-degree completion compatible with the triangle bits admits a rearrangement with dT > 0, or dT = 0 and more vertices.
# Boundary faces: [top, bottom, left_1..left_4, right_1..right_4] = indices 0..9.
# P sectors ccw from ray P->Q: left_2, left_3, left_4, bottom, right_4, right_3 = [3,4,5,1,9,8]; Q ccw from Q->P: [8,7,6,0,2,3].
import itertools, numpy as np, json, sys
sys.path.insert(0, "/home/nail/stuff/sundai_math/work/eng/pert2")
from window import crossing_set, all_words, faces
k = 5; w0 = [(2, 4), (0, 2)]
req, _ = crossing_set(k, w0)
vec0, t0, nv0, inc = faces(k, w0)
assert sorted(inc[0]) == sorted([3, 4, 5, 1, 9, 8]) and sorted(inc[1]) == sorted([8, 7, 6, 0, 2, 3]), inc
opts = {}
for w in all_words(k, req):
    if list(w) == w0: continue
    v, t, nv, _ = faces(k, w); opts[(v, t, nv)] = w
V = np.array([q[0] for q in opts]); TL = np.array([q[1] for q in opts]); NV = np.array([q[2] for q in opts])
Pccw = [3, 4, 5, 1, 9, 8]; Qccw = [8, 7, 6, 0, 2, 3]
Pcw = [8, 9, 1, 5, 4, 3]; Qcw = [3, 2, 0, 6, 7, 8]
def canon(tri):
    a = ("".join('1' if tri[f] else '0' for f in Pccw), "".join('1' if tri[f] else '0' for f in Qccw))
    b = ("".join('1' if tri[f] else '0' for f in Pcw), "".join('1' if tri[f] else '0' for f in Qcw))
    return min(a, b)
status = {}
nf = len(vec0)
for bits in itertools.product((0, 1), repeat=nf):
    choices = []
    for f in range(nf):
        if bits[f]:
            o = 3 - vec0[f]
            if o < 0: choices = None; break
            choices.append([o])
        else:
            choices.append([o for o in (0, 1, 2, 3) if (o == 3 or vec0[f] + o >= 3) and vec0[f] + o != 3])
    if choices is None: continue
    key = canon(bits); tri0 = np.array(bits, dtype=bool); irr = False
    for outs in itertools.product(*choices):
        o = np.array(outs); tri1 = (V + o[None] == 3) & (o[None] < 3)
        dT = tri1.sum(1) - tri0.sum() + TL - t0
        if not ((dT > 0) | ((dT == 0) & (NV > nv0))).any():
            irr = True; break
    status[key] = status.get(key, False) or irr
ex = sorted(k_ for k_, v in status.items() if not v); al = sorted(k_ for k_, v in status.items() if v)
print("vec0", vec0, "options", len(opts), "canonical patterns", len(status), "excluded", len(ex), "allowed", len(al))
json.dump({"excluded": ex, "allowed": al, "convention": "P sectors then Q sectors, one rotational sense, starting right after the ray P->Q / Q->P; canonical = min over both senses"}, open("pair_TT_all.json", "w"), indent=0)
# how many allowed patterns satisfy single-triple optimality for both points
alt = lambda s: int(s[0]) + int(s[2]) + int(s[4]) >= 2 and int(s[1]) + int(s[3]) + int(s[5]) >= 2
print("allowed with both triples optimal:", sum(1 for p, q in al if alt(p) and alt(q)), "; all pairs of optimal words consistent:",
      sum(1 for p, q in list(status) if alt(p) and alt(q)))

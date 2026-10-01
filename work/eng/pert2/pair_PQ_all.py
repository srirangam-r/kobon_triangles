# Pair lemma, all 4-fold patterns: P (4-fold) adjacent on line a to triple Q.  For every canonical
# (P bits, Q bits) pattern decide EXCLUDED (every compatible face-degree assignment has a rearrangement with
# dT > 0, or dT = 0 and more vertices) or ALLOWED.  Canonical listing: sectors in one rotational sense starting
# right after the ray P->Q (resp. Q->P); canonical = min over the two senses.
import itertools, numpy as np, json
from window import crossing_set, all_words, faces
k = 6; w0 = [(2, 5), (0, 2)]
req, _ = crossing_set(k, w0)
vec0, t0, nv0, _ = faces(k, w0)
opts = {}
for w in all_words(k, req):
    if list(w) == w0: continue
    v, t, nv, _ = faces(k, w); opts[(v, t, nv)] = w
V = np.array([q[0] for q in opts]); TL = np.array([q[1] for q in opts]); NV = np.array([q[2] for q in opts])
Pcw = [9, 10, 11, 1, 6, 5, 4, 3]; Qcw = [3, 2, 0, 7, 8, 9]
Pccw = [3, 4, 5, 6, 1, 11, 10, 9]; Qccw = [9, 8, 7, 0, 2, 3]
def canon(tri):
    a = ("".join('1' if tri[f] else '0' for f in Pcw), "".join('1' if tri[f] else '0' for f in Qcw))
    b = ("".join('1' if tri[f] else '0' for f in Pccw), "".join('1' if tri[f] else '0' for f in Qccw))
    return min(a, b)
status = {}
nf = len(vec0)
for bits in itertools.product((0, 1), repeat=nf):
    # out choices consistent with the triangle bits
    choices = []
    for f in range(nf):
        if bits[f]:
            o = 3 - vec0[f]
            if o < 0: choices = None; break
            choices.append([o])
        else:
            choices.append([o for o in (0, 1, 2, 3) if (o == 3 or vec0[f] + o >= 3) and vec0[f] + o != 3])
    if choices is None: continue
    key = canon(bits)
    tri0 = np.array(bits, dtype=bool)
    irr = False
    for outs in itertools.product(*choices):
        o = np.array(outs); tri1 = (V + o[None] == 3) & (o[None] < 3)
        dT = tri1.sum(1) - tri0.sum() + TL - t0
        if not ((dT > 0) | ((dT == 0) & (NV > nv0))).any():
            irr = True; break
    status[key] = status.get(key, False) or irr
ex = sorted(k_ for k_, v in status.items() if not v); al = sorted(k_ for k_, v in status.items() if v)
print("canonical patterns", len(status), "excluded", len(ex), "allowed", len(al))
json.dump({"excluded": ex, "allowed": al, "convention": "P sectors then Q sectors, one rotational sense, starting right after the ray P->Q / Q->P; canonical = min over both senses"}, open("pair_PQ_all.json", "w"), indent=0)

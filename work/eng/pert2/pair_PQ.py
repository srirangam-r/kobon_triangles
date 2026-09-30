# Bad 4-fold P adjacent (consecutive on line a) to a triple point Q; window k=6, w0 = P(2..5), Q(0..2).
import itertools, numpy as np, sys
from window import crossing_set, all_words, faces
k = 6; w0 = [(2, 5), (0, 2)]
req, _ = crossing_set(k, w0)
W = [w for w in all_words(k, req)]
vec0, t0, nv0, inc0 = faces(k, w0)
opts = {}
for w in W:
    if list(w) == w0: continue
    v, t, nv, inc = faces(k, w)
    key = (v, t, nv)
    opts[key] = w
print("words", len(W), "distinct options", len(opts), "vec0", vec0)
Pc = [3, 9, 10, 11, 1, 6, 5, 4]; Qc = [0, 7, 8, 9, 3, 2]
nf = len(vec0)
V = np.array([k_[0] for k_ in opts], dtype=np.int8)            # options x faces
TL = np.array([k_[1] for k_ in opts]); NV = np.array([k_[2] for k_ in opts])
def bad_pattern(bits):
    z = [i for i in range(8) if not bits[i]]
    return len(z) == 0 or len(z) == 1 or (len(z) == 2 and (z[1] - z[0]) == 4)
irreducible = []
vals = [0, 1, 2, 3]
rng = [ [o for o in vals if o == 3 or vec0[f] + o >= 3] for f in range(nf)]
count = 0
for outs in itertools.product(*rng):
    tri0 = [o < 3 and vec0[f] + o == 3 for f, o in enumerate(outs)]
    if not bad_pattern([tri0[f] for f in Pc]): continue
    count += 1
    o = np.array(outs)
    tri1 = (V + o[None, :] == 3) & (o[None, :] < 3)
    dT = tri1.sum(1) - sum(tri0) + TL - t0
    ok = ((dT > 0) | ((dT == 0) & (NV > nv0))).any()
    if not ok:
        irreducible.append((outs, int(dT.max())))
print("assignments with P bad:", count, "irreducible:", len(irreducible))
from collections import Counter
def ring_bits(outs, cyc):
    return "".join("1" if (outs[f] < 3 and vec0[f] + outs[f] == 3) else "0" for f in cyc)
C = Counter((ring_bits(o, Pc), ring_bits(o, Qc), b) for o, b in irreducible)
for key, c in sorted(C.items(), key=lambda x: -x[1])[:30]:
    print("  P", key[0], "Q", key[1], "bestdT", key[2], "count", c)

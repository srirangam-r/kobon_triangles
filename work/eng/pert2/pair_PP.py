# Two 4-fold points P (tracks 3..6) and P' (tracks 0..3) adjacent on line a; window k=7, w0 = [(3,6),(0,3)].
import itertools, numpy as np, time
from window import crossing_set, all_words, faces
k = 7; w0 = [(3, 6), (0, 3)]
t = time.time()
req, _ = crossing_set(k, w0)
W = all_words(k, req)
vec0, t0, nv0, inc0 = faces(k, w0)
opts = {}
for w in W:
    if list(w) == w0: continue
    v, tl, nv, inc = faces(k, w); opts[(v, tl, nv)] = w
print("words", len(W), "options", len(opts), "vec0", vec0, f"{time.time()-t:.0f}s")
# faces: top0 bot1 left1..6 = 2..7, right1..6 = 8..13
# P = (3,6): top at P = left3 (4) [closes at P'], right4..6 = 11,12,13, bottom 1, left6,5,4 = 7,6,5
Pc = [4, 11, 12, 13, 1, 7, 6, 5]
# P' = (0,3): top 0, right1..3 = 8,9,10, bottom at P' = gap4 face started at P = right4 (11), left3,2,1 = 4,3,2
Qc = [0, 8, 9, 10, 11, 4, 3, 2]
V = np.array([q[0] for q in opts]); TL = np.array([q[1] for q in opts]); NV = np.array([q[2] for q in opts])
def bad(bits):
    z = [i for i in range(8) if not bits[i]]
    return len(z) <= 1 or (len(z) == 2 and z[1] - z[0] == 4)
rng = [[o for o in (0, 1, 2, 3) if o == 3 or vec0[f] + o >= 3] for f in range(len(vec0))]
tot = irr = 0; from collections import Counter; C = Counter()
for outs in itertools.product(*rng):
    tri0 = [o < 3 and vec0[f] + o == 3 for f, o in enumerate(outs)]
    if not bad([tri0[f] for f in Pc]) or not bad([tri0[f] for f in Qc]): continue
    tot += 1
    o = np.array(outs); tri1 = (V + o[None] == 3) & (o[None] < 3)
    dT = tri1.sum(1) - sum(tri0) + TL - t0
    if not ((dT > 0) | ((dT == 0) & (NV > nv0))).any():
        irr += 1; C[("".join('1' if tri0[f] else '0' for f in Pc), "".join('1' if tri0[f] else '0' for f in Qc), int(dT.max()))] += 1
print("both-bad assignments", tot, "irreducible", irr)
for kk, c in sorted(C.items()): print("  P", kk[0], "P'", kk[1], "best", kk[2], c)

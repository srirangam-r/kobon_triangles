# Bad 4-fold P and the simple far end S of one of its rays (line a), with the other line c at S.
# window k=5: tracks 0..4; c at track 0, P-block tracks 1..4 with a at track 4 -> after P, a at track 1; S=(0,1).
import itertools, numpy as np
from window import crossing_set, all_words, faces
k = 5; w0 = [(1, 4), (0, 1)]
req, _ = crossing_set(k, w0)
vec0, t0, nv0, inc0 = faces(k, w0)
opts = {}
for w in all_words(k, req):
    if list(w) == w0: continue
    v, t, nv, inc = faces(k, w); opts[(v, t, nv)] = w
# face order: top0, bot1, left1..4 = 2..5, right1..4 = 6..9
# P sectors cyclic: top at P = left1 (gap1 closes at S) , right2, right3, right4, bottom, left4, left3, left2
Pc = [2, 7, 8, 9, 1, 5, 4, 3]
# S sectors: top at S = top(0), right1 (6), bottom at S = gap2 face started at P = right2 (7), left1 (2)
Sc = [0, 6, 7, 2]
print("options", len(opts), "vec0", vec0)
V = np.array([q[0] for q in opts]); TL = np.array([q[1] for q in opts]); NV = np.array([q[2] for q in opts])
def bad(bits):
    z = [i for i in range(8) if not bits[i]]
    return len(z) <= 1 or (len(z) == 2 and z[1] - z[0] == 4)
rng = [[o for o in (0, 1, 2, 3) if o == 3 or vec0[f] + o >= 3] for f in range(len(vec0))]
tot = irr = 0; from collections import Counter; C = Counter()
for outs in itertools.product(*rng):
    tri0 = [o < 3 and vec0[f] + o == 3 for f, o in enumerate(outs)]
    if not bad([tri0[f] for f in Pc]): continue
    # the ray P->S is doubly used (both P-sectors adjacent to it are triangles): sectors 7 (left1) and 0? ray a->S
    tot += 1
    o = np.array(outs); tri1 = (V + o[None] == 3) & (o[None] < 3)
    dT = tri1.sum(1) - sum(tri0) + TL - t0
    if not ((dT > 0) | ((dT == 0) & (NV > nv0))).any():
        irr += 1
        C[("".join('1' if tri0[f] else '0' for f in Pc), "".join('1' if tri0[f] else '0' for f in Sc))] += 1
print("P bad assignments", tot, "irreducible", irr)
for kk, c in sorted(C.items()): print("  P", kk[0], "S", kk[1], c)

"""Referee4, C7: explicit bent triple point P with 4 bridge ends (c(P) = 2 > 3/2).
Quadrilateral V0=(0,0), Q=(12,0), V4=(14,12), V5=(0,10); P=(6,5) on diagonal Q-V5;
lines: C1=V0Q, C2=QV4, M1=V4V5, M2=V5V0, l0=V0P, l1=V4P, l2=QV5."""
import sys
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee')
from arr import from_int_lines
lines = [[0, 1, 0],        # C1: y = 0
         [6, -1, -72],     # C2
         [1, -7, 70],      # M1
         [1, 0, 0],        # M2: x = 0
         [5, -6, 0],       # l0
         [7, -8, -2],      # l1
         [5, 6, -60]]      # l2
names = ['C1', 'C2', 'M1', 'M2', 'l0', 'l1', 'l2']
A = from_int_lines(lines)
print('T', A.T, 'Z', A.Z, 'D', A.D, 'triple points', [sorted(names[l] for l in A.ev[e]) for e in A.triples])
for P in A.triples:
    cr, bl = A.blocks(P)
    e = 0
    for (w, d, edge, far) in cr:
        if edge is not None and len(A.usage.get(edge, ())) == 2 and A.mult[far] >= 3:
            e += 1
    mids = sorted(b['i'] for b in bl)
    typ = {0: 'b0', 1: 'b1', 3: 'centroid'}.get(len(bl))
    if len(bl) == 2:
        typ = 'axis' if (mids[1] - mids[0]) % 6 == 3 else 'bent'
    print(sorted(names[l] for l in A.ev[P]), 'type', typ, 'b', len(bl), 'e', e, 'c', len(bl) + e / 2 - 2,
          'caps', [names[b['cap']] for b in bl])

# embed in an 18-line exact arrangement: 11 extra lines far from the quadrilateral
import random
rng = random.Random(3)
ext = list(lines)
while len(ext) < 18:
    a, b = rng.randint(-40, 40), rng.randint(-40, 40)
    if a == 0 and b == 0:
        continue
    c = rng.choice([-1, 1]) * rng.randint(3000, 9000)
    cand = ext + [[a, b, c]]
    try:
        B = from_int_lines(cand)
    except ValueError:
        continue
    if any(B.mult[e] > 2 for e in range(len(B.ev)) if (len(B.ev[e]) > 2 and any(l >= 7 for l in B.ev[e]))):
        continue
    ext = cand
B = from_int_lines(ext)
for P in B.triples:
    cr, bl = B.blocks(P)
    if sorted(B.ev[P]) == [4, 5, 6]:
        e = sum(1 for (w, d, edge, far) in cr if edge is not None and len(B.usage.get(edge, ())) == 2 and B.mult[far] >= 3)
        mids = sorted(b['i'] for b in bl)
        print('18-line embedding: T', B.T, 'P blocks', len(bl), 'middles', mids, 'e', e, 'c', len(bl) + e / 2 - 2)
print('extra lines', ext[7:])

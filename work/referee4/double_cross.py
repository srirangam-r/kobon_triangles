"""Referee4: 'double cross' - one block lying in two mutual pairs.
Quadrilateral P=(-2,0), V+=(0,2), P'=(3,0), V-=(0,-1); diagonals a (y=0) and C (x=0) meet at the
simple point X=(0,0).  All four points get a block with middle toward X; each such block is
killed on BOTH sides, i.e. lies in two mutual pairs.  Used in the C16/C18 verdicts."""
import sys
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee')
from arr import from_int_lines
L = {'a': [0, 1, 0], 'C': [1, 0, 0], 'b': [1, 2, 2], 'c': [1, -1, 2], "b'": [1, -3, -3], "c'": [2, 3, -6]}
names = list(L)
A = from_int_lines([L[k] for k in names])
print('T', A.T, 'D', A.D, 'triple points', [sorted(names[l] for l in A.ev[e]) for e in A.triples])
X = A.pe(0, 1)
print('X simple:', A.mult[X] == 2)
for P in A.triples:
    cr, bl = A.blocks(P)
    for b in bl:
        if b['X'] != X:
            continue
        w = b['ray'][0]; C = b['cap']
        kx, kp = A.idx[w][X], A.idx[w][P]
        j = kx if kx > kp else kx - 1
        use = A.usage.get((w, j), [])
        kc = A.idx[C][X]; rc = A.rows[C]
        apex = [rc[u] for u in (kc - 1, kc + 1) if 0 <= u < len(rc)]
        print(sorted(names[l] for l in A.ev[P]), 'block toward X, cap', names[C],
              '| segment beyond X used on sides', sorted(use), '| apexes', [sorted(names[l] for l in A.ev[v]) for v in apex])

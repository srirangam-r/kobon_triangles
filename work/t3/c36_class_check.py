"""Mechanical check of the C36 sector-class formula in model literals.
chi from chi_from_word (search/base2.py); before(r,i,j) := chi(sorted r,i,j) == -1 if i<j else == +1
(i's crossing strictly precedes j's on r).  For each concurrent sorted triple (A,B,C) and each
triangle (x,y,L) with x,y in {A,B,C}: class via the formula, compared with the geometric class
from arr.py (rays r0..r5 = A-,B-,C-,A+,B+,C+; sectors s_i=(r_i,r_{i+1}); even = s0,s2,s4)."""
import glob, sys, json, collections
sys.path.insert(0, '.'); sys.path.insert(0, '../../search')
from arr import Arr, rays
from base2 import chi_from_word
from kobon_sat import count_general
R = '../../tools/external/kobon-solutions/gallery/data'

def before(chi, r, i, j):
    t = tuple(sorted((r, i, j)))
    return chi[t] == (-1 if i < j else 1)

def formula_class(chi, A, B, C, x, y, L):
    l = lambda u, v: before(chi, u, L, v)      # L's crossing on u is before P (= u ∩ v)
    pair = tuple(sorted((x, y)))
    if pair == (A, B):
        if l(A, B) and l(B, A): return 'even'   # (A-left, B-left) = s0
        if not l(A, B) and not l(B, A): return 'odd'   # (A-right, B-right) = s3
    if pair == (B, C):
        if l(B, C) and l(C, B): return 'odd'    # (B-left, C-left) = s1
        if not l(B, C) and not l(C, B): return 'even'  # (B-right, C-right) = s4
    if pair == (A, C):
        if not l(A, C) and l(C, A): return 'even'  # (C-left, A-right) = s2
        if l(A, C) and not l(C, A): return 'odd'   # (C-right, A-left) = s5
    return 'impossible'

st = collections.Counter()
for s in sys.argv[1:]:
    for f in sorted(glob.glob(f'{R}/{s}/*.json'))[:200]:
        d = json.load(open(f)); a = Arr(d['gens'])
        if any(len(e) > 3 for e in a.events): continue
        n = a.n
        if len(a.events) + 2 * len(a.triples) != n * (n - 1) // 2: continue   # skip parallels
        chi = chi_from_word(d['gens'], n)
        tris = set(count_general(n, chi))
        for P in a.triples:
            A, B, C = sorted(a.events[P])
            rs = rays(a, P)
            # geometric classes of faces at P
            geo = {}
            for fc in a.tris:
                at = [(x, +1 if a.rows[x][e] == P else -1) for (x, e, _) in fc if P in (a.rows[x][e], a.rows[x][e + 1])]
                if len(at) != 2: continue
                i, j = sorted(rs.index(r) for r in at)
                sidx = i if j - i == 1 else 5
                lines = frozenset(x for (x, _, _) in fc)
                geo[lines] = 'even' if sidx % 2 == 0 else 'odd'
            for (x, y) in ((A, B), (B, C), (A, C)):
                for L in range(n):
                    if L in (A, B, C): continue
                    t = tuple(sorted((x, y, L)))
                    if t not in tris: continue
                    fcl = {'even': 'odd', 'odd': 'even'}.get(formula_class(chi, A, B, C, x, y, L), 'impossible')  # model before() = sweep-reversed
                    g = geo.get(frozenset((x, y, L)))
                    st['match' if fcl == g else f'MISMATCH {fcl} vs {g}'] += 1
print(dict(st))

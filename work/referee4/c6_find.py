"""Find explicit n=18 counterexamples to the stated C6 rule and print full detail."""
import json, random, sys
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee4')
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee')
from c6_parity import line_data, GAL
from arr import from_tokens
from mutate import simple_tris, flip, contract
rng = random.Random(int(sys.argv[1]))
files = sorted((GAL / '18').glob('*.json'))
found = {}
def show(A, d, why):
    L = d['L']; t = A.tseq(L)
    s = ''.join({frozenset(): '0', frozenset([1]): '+', frozenset([-1]): '-'}.get(x, 'B') for x in t)
    verts = ''.join('T' if A.mult[e] == 3 else '.' for e in A.rows[L])
    print(why, 'T', A.T, 'Z', A.Z, 'D', A.D, 'triples', len(A.triples), 'L', L, 'j', d['j'], 'K', d['K'], 'pats', d['pats'])
    print('   t-seq (t_0..t_r):', s)
    print('   vertices on L   : ', verts)
    print('   tokens:', ' '.join(A.tokens))
for it in range(20000):
    f = rng.choice(files)
    toks = json.load(open(f))['gens'].split()
    A = from_tokens(toks, 18, complete=True)
    try:
        for _ in range(rng.choice([0, 1, 2, 3])):
            s = simple_tris(A)
            if s: A = contract(A, rng.choice(s))
    except (ValueError, AssertionError):
        continue
    if any(m > 3 for m in A.mult): continue
    for d in line_data(A):
        if d['hasBoth'] or not d['strong'] or (d['j'] + d['K']) % 2: continue
        kind = 'end' if 'end' in d['pats'] else 'same'
        if kind not in found:
            found[kind] = 1; show(A, d, f'[{kind}] from {f.name}')
    if len(found) == 2: break

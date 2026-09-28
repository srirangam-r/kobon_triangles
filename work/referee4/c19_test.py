"""Referee4, C19: at a bent point P (toward Q) with a further doubly used bridge [P,R]:
(a) R is the first vertex of ray 0, 4 or 5; (b) Q and R are consecutive on no line.
Also: bridge-graph triangles through bent points (claimed impossible 'in particular').
Runs on the explicit 7-line example of C07 and on random arrangements."""
import json, random, sys
from collections import Counter
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee'); sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee4')
from arr import from_tokens, from_int_lines
from mutate import simple_tris, flip, contract
from c7_lemmaC import point_info
GAL = Path('/home/nail/stuff/sundai_math/tools/external/kobon-solutions/gallery/data')

def cons(A, U, W):
    return any(abs(A.idx[m][U] - A.idx[m][W]) == 1 for m in A.ev[U] & A.ev[W])

def check(A, st, bad, tag):
    if any(m > 3 for m in A.mult): return
    bridges = set()
    for (L, j), s in A.usage.items():
        u, w = A.rows[L][j], A.rows[L][j + 1]
        if len(s) == 2 and A.mult[u] >= 3 and A.mult[w] >= 3:
            bridges.add(frozenset((u, w)))
    for P in A.triples:
        cr, bl, br, typ = point_info(A, P)
        if typ != 'bent': continue
        st['bent'] += 1
        mids = sorted(b['i'] for b in bl)
        i1 = mids[0] if (mids[1] - mids[0]) % 6 == 2 else mids[1]  # middle '1'; shared = i1+1
        sh = (i1 + 1) % 6
        Q = cr[sh][3]
        rel = {(sh - 2) % 6: 'V0', (sh + 2) % 6: 'V4', (sh + 3) % 6: 'V5'}
        for i, R in br:
            if R == Q: continue
            st['bent_extra_bridge'] += 1
            if i not in rel: bad.append(f'{tag} (a) FAIL ray {i}')
            else: st[('extra at', rel[i])] += 1
            if cons(A, Q, R): bad.append(f'{tag} (b) FAIL Q,R consecutive')
        nb = [W for W in A.triples if frozenset((P, W)) in bridges]
        for U, W in combinations(nb, 2):
            if frozenset((U, W)) in bridges:
                st[('bridge triangle through bent P', 'k', len(A.triples))] += 1
                if st['ex'] < 1:
                    st['ex'] += 1
                    bad.append(f'INFO triangle through bent P with k={len(A.triples)} n={A.n} tokens={" ".join(A.tokens) if A.tokens else "(exact)"}')

def worker(args):
    wid, N, files = args
    rng = random.Random(100 + wid); st = Counter(); bad = []
    for it in range(N):
        f = rng.choice(files); n = int(Path(f).parent.name.split('-')[0])
        try:
            A = from_tokens(json.load(open(f))['gens'].split(), n)
            for _ in range(rng.choice([4, 8, 12, 16, 24])):
                s = simple_tris(A)
                if not s: break
                tl = set(L for P in A.triples for L in A.ev[P])
                s2 = [x for x in s if sum(1 for L in set().union(*(A.ev[e] for e in x)) if L in tl) >= 2]
                A = contract(A, rng.choice(s2 if s2 and rng.random() < 0.9 else s))
        except (ValueError, AssertionError, IndexError):
            continue
        st['arr'] += 1; check(A, st, bad, f'w{wid}i{it}')
    return st, bad

if __name__ == '__main__':
    st = Counter(); bad = []
    lines = [[0, 1, 0], [6, -1, -72], [1, -7, 70], [1, 0, 0], [5, -6, 0], [7, -8, -2], [5, 6, -60]]
    A = from_int_lines(lines)
    check(A, st, bad, 'C07-example')
    print('C07 7-line example:', dict(st), [b[:120] for b in bad])
    files = [str(f) for s in ('10', '12', '14', '16', '18') for f in sorted((GAL / s).glob('*.json'))]
    with Pool(4) as pool:
        for s, b in pool.imap_unordered(worker, [(w, int(sys.argv[1]), files) for w in range(4)]):
            st.update(s); bad += b
    for k in sorted(st, key=str): print(st[k], k)
    real = [b for b in bad if not b.startswith('INFO')]
    print('FAILS', len(real))
    for b in real[:10]: print('  ', b[:200])
    for b in bad:
        if b.startswith('INFO'): print('  ', b[:600])

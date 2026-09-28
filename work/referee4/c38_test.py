"""Referee4: C38 multi-split lemma with the C35/C36 class table in the solver's before() semantics.
(1) learn which resolution ('g g+1 g' = R1, 'g+1 g g+1' = R2) destroys which class (EVEN/ODD);
(2) for random S (2-4 triple points) and random resolutions, check
    T' == T + |S| - |union of the chosen-class triangle sets|  (triangles as vertex triples)."""
import json, random, sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee'); sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee4')
from arr import from_tokens
from mutate import simple_tris, contract, flip
from c17_test import chi_from_arr, sat_before
from c35_test import EVEN, ODD
GAL = Path('/home/nail/stuff/sundai_math/tools/external/kobon-solutions/gallery/data')

def classes(A, chi, P):
    before = lambda r, i, j: sat_before(chi, r, i, j)
    a_, b_, c_ = sorted(A.ev[P]); name = {a_: 'A', b_: 'B', c_: 'C'}
    ev, od = set(), set()
    for t in A.tris:
        if P not in t: continue
        o = [v for v in t if v != P]
        x = A.common_line(P, o[0]); y = A.common_line(P, o[1]); L = A.common_line(o[0], o[1])
        yx = [w for w in A.ev[P] if w != x][0]; xy = [w for w in A.ev[P] if w != y][0]
        key = frozenset([(name[x], 'L' if before(x, L, yx) else 'R'), (name[y], 'L' if before(y, L, xy) else 'R')])
        (ev if key in EVEN else od).add(frozenset(t))
    return ev, od

def res(tok, which):
    g = int(tok[:-1])
    return [str(g), str(g + 1), str(g)] if which == 1 else [str(g + 1), str(g), str(g + 1)]

def worker(args):
    wid, N, seed = args
    rng = random.Random(seed * 7919 + wid); st = Counter(); bad = []
    files = [f for s in ('12', '14', '16', '18', '18-1', '20') for f in sorted((GAL / s).glob('*.json'))]
    for it in range(N):
        f = rng.choice(files); n = int(f.parent.name.split('-')[0])
        try:
            A = from_tokens(json.load(open(f))['gens'].split(), n)
            for _ in range(rng.choice([0, 2, 5, 8])):
                s = simple_tris(A)
                if s: A = contract(A, rng.choice(s))
            A = from_tokens(A.tokens, n, complete=False)
        except (ValueError, AssertionError, IndexError):
            continue
        if any(m > 3 for m in A.mult) or len(A.triples) < 2: continue
        chi = chi_from_arr(A); toks = A.tokens
        cl = {P: classes(A, chi, P) for P in A.triples}
        # (1) mapping: single splits
        for P in A.triples:
            T1 = from_tokens(toks[:P] + res(toks[P], 1) + toks[P + 1:], n, complete=False).T
            ev, od = cl[P]
            if len(ev) != len(od):
                if T1 == A.T + 1 - len(ev): st['R1=EVEN'] += 1
                elif T1 == A.T + 1 - len(od): st['R1=ODD'] += 1
                else: bad.append('single split mismatch')
        # (2) multi-split with the learned rule R1 <-> ODD (4498/4498 single splits)
        for rep in range(4):
            S = rng.sample(A.triples, min(len(A.triples), rng.choice([2, 3, 4])))
            choice = {P: rng.choice([1, 2]) for P in S}
            new = []
            for ti, tk in enumerate(toks):
                new += res(tk, choice[ti]) if ti in choice else [tk]
            Tn = from_tokens(new, n, complete=False).T
            U = set()
            for P in S:
                U |= cl[P][1] if choice[P] == 1 else cl[P][0]
            st['multi'] += 1
            if Tn != A.T + len(S) - len(U): bad.append(f'multi FAIL |S|={len(S)}')
    return st, bad

if __name__ == '__main__':
    st = Counter(); bad = []
    with Pool(4) as pool:
        for s, b in pool.imap_unordered(worker, [(w, int(sys.argv[1]), 5) for w in range(4)]):
            st.update(s); bad += b
    print(dict(st), 'FAILS', len(bad), Counter(bad).most_common(3))

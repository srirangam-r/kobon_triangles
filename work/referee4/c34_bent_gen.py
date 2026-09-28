"""Referee4: bent-seeking generator for C34 tests.  Greedy contractions that create bent points / bridges,
then run c34_test.check on every intermediate arrangement with k >= 4."""
import json, random, sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee'); sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee4')
from arr import from_tokens
from mutate import simple_tris, contract, flip
from c7_lemmaC import point_info
from c34_test import check
GAL = Path('/home/nail/stuff/sundai_math/tools/external/kobon-solutions/gallery/data')

def score(A):
    if any(m > 3 for m in A.mult): return -1
    nb = 0; ebr = 0
    for P in A.triples:
        cr, bl, br, typ = point_info(A, P)
        nb += typ == 'bent'; ebr += len(br)
    return 10 * nb + ebr

def worker(args):
    wid, N, seed = args
    rng = random.Random(seed * 7919 + wid); st = Counter(); bad = []
    files = [f for s in ('10', '12', '14', '16', '18') for f in sorted((GAL / s).glob('*.json'))]
    for it in range(N):
        f = rng.choice(files); n = int(f.parent.name.split('-')[0])
        try:
            A = from_tokens(json.load(open(f))['gens'].split(), n)
            for _ in range(rng.choice([0, 2, 6])):
                s = simple_tris(A)
                if s: A = flip(A, rng.choice(s))
            for step in range(rng.choice([6, 9, 12, 16])):
                s = simple_tris(A)
                if not s: break
                cands = rng.sample(s, min(12, len(s)))
                best, bs = None, -2
                for t in cands:
                    try:
                        B = contract(A, t)
                    except (ValueError, AssertionError, IndexError):
                        continue
                    sc = score(B) + rng.random()
                    if sc > bs: best, bs = B, sc
                if best is None: break
                A = best
                if len(A.triples) >= 4:
                    st['arr'] += 1
                    st[('k', min(len(A.triples), 10))] += 1
                    try:
                        check(A, st, bad, f'w{wid}i{it}s{step}')
                    except (AssertionError, ValueError, IndexError) as ex:
                        bad.append(f'assert {ex!r}')
        except (ValueError, AssertionError, IndexError):
            continue
    return st, bad

if __name__ == '__main__':
    N, seed = int(sys.argv[1]), int(sys.argv[2])
    st = Counter(); bad = []
    with Pool(4) as pool:
        for s, b in pool.imap_unordered(worker, [(w, N, seed) for w in range(4)]):
            st.update(s); bad += b
    for k_ in sorted(st, key=str):
        print(st[k_], k_)
    print('FAILS', len(bad))
    for b in bad[:15]: print('  ', b[:200])

"""Referee test of C62-C65 on gallery arrangements and mutations, using the independent structure code
struct_.py (signotope -> vertex orders -> faces/blocks/bridges).  Mutations: work/referee/mutate.py
(contract simple triangles to triple points, triangle flips) plus a greedy premise-seeking contraction
(score = all-multiple faces, twin pairs, fan premises, bent points with a face partner).
    uv run --no-project --with python-sat python gallery_test.py MODE N SEED WORKERS
MODE: gallery (every gallery file as is) | mutate
"""
import json
import random
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee')
sys.path.insert(0, '/home/nail/stuff/sundai_math/search')
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee4/c62_65')
from arr import from_tokens  # noqa: E402
from mutate import simple_tris, contract, flip  # noqa: E402
from base2 import chi_from_word  # noqa: E402
from struct_ import Arr, check  # noqa: E402

GAL = Path('/home/nail/stuff/sundai_math/tools/external/kobon-solutions/gallery/data')


def to_struct(tokens, n):
    chi = chi_from_word(' '.join(tokens), n)
    from itertools import combinations
    sig = {t: chi[t] for t in combinations(range(n), 3)}
    return Arr(n, sig)


def score(B):
    st, bad = Counter(), []
    check(B, st, bad)
    return (3 * st['allmult faces'] + 5 * st['T twin pairs'] + 8 * st['W premise'] + 4 * st['BP bent']
            + 8 * st['BP partner in all-mult face'] + 6 * st['CC faces with 1 X vertices']), bad


def worker(args):
    wid, N, seed, mode = args
    rng = random.Random(seed * 7919 + wid)
    st, bad = Counter(), []
    files = [f for s in ('10', '12', '14', '16', '18', '18-1', '18-4', '18-6', '18-9', '20', '20-6', '20-9')
             for f in sorted((GAL / s).glob('*.json'))]
    if mode == 'gallery':
        allf = sorted(GAL.glob('*/*.json'))
        mine = allf[wid::N]
        for f in mine:
            n = int(f.parent.name.split('-')[0])
            try:
                A = from_tokens(json.load(open(f))['gens'].split(), n)
                if any(m > 3 for m in A.mult):
                    st['skipped 4-fold'] += 1
                    continue
                S_ = to_struct(A.tokens, n)
            except (ValueError, AssertionError, IndexError, KeyError) as ex:
                st['parse fail'] += 1
                continue
            check(S_, st, bad, str(f))
        return st, bad
    for it in range(N):
        f = rng.choice(files)
        n = int(f.parent.name.split('-')[0])
        try:
            A = from_tokens(json.load(open(f))['gens'].split(), n)
            for _ in range(rng.choice([0, 0, 2, 6])):
                s = simple_tris(A)
                if s:
                    A = flip(A, rng.choice(s))
            steps = rng.choice([4, 8, 12, 16, 20])
            greedy = rng.random() < 0.7
            for step in range(steps):
                s = simple_tris(A)
                if not s:
                    break
                if greedy:
                    best, bs = None, -1
                    for t in rng.sample(s, min(8, len(s))):
                        try:
                            B = contract(A, t)
                            if any(m > 3 for m in B.mult):
                                continue
                            sc, _ = score(to_struct(B.tokens, n))
                        except (ValueError, AssertionError, IndexError, KeyError):
                            continue
                        sc += rng.random()
                        if sc > bs:
                            best, bs = B, sc
                    if best is None:
                        break
                    A = best
                else:
                    A = contract(A, rng.choice(s))
                    if any(m > 3 for m in A.mult):
                        break
                if step % 2 == 1 or step == steps - 1:
                    S_ = to_struct(A.tokens, n)
                    check(S_, st, bad, f'w{wid}i{it}s{step} {f.name}')
                    if len(bad) > 50:
                        return st, bad
        except (ValueError, AssertionError, IndexError, KeyError) as ex:
            st['exception ' + type(ex).__name__ + ' ' + str(ex)[:40]] += 1
            continue
    return st, bad


if __name__ == '__main__':
    mode, N, seed, W = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    st, bad = Counter(), []
    jobs = [(w, N if mode != 'gallery' else W, seed, mode) for w in range(W)]
    with Pool(W) as pool:
        for s, b in pool.imap_unordered(worker, jobs):
            st.update(s)
            bad += b
    for k_ in sorted(st, key=str):
        print(f'{st[k_]:9d} {k_}')
    print('FAILS', len(bad))
    for b in bad[:20]:
        print('  ', b[:200])

"""Referee4, C9: test D <= 2k + sigma (the only non-identity step of the C9 budgets),
with k triple points, no 4-fold points, sigma = 3k - l (l = #lines through triple points),
plus the derived budget forms at T: Z + l <= 2k + 288 - 3T (n=18), 2Z - Ztr + 2l <= 2(...).
Also B <= 2k fails exactly at centroid points; report them.  usage: c9_budget.py N SEED sizes"""
import json, random, sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee')
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee4')
from arr import from_tokens, from_int_lines
from mutate import simple_tris, flip, contract
from c7_lemmaC import point_info
GAL = Path('/home/nail/stuff/sundai_math/tools/external/kobon-solutions/gallery/data')

def check(A, st, bad, tag):
    if any(m > 3 for m in A.mult):
        return
    k = len(A.triples)
    lines_tp = set(L for P in A.triples for L in A.ev[P])
    ell = len(lines_tp); sigma = 3 * k - ell
    B = 0; cent = 0
    for P in A.triples:
        cr, bl, br, typ = point_info(A, P)
        B += len(bl); cent += typ == 'centroid'
    st['arr'] += 1; st['centroid_pts'] += cent
    if B > 2 * k:
        st['B>2k'] += 1
    if A.D > 2 * k + sigma:
        bad.append(f'{tag} D={A.D} > 2k+sigma={2*k+sigma} k={k} centroids={cent} tokens={" ".join(A.tokens) if A.tokens else ""}')
    st['min_slack_D'] = min(st.get('min_slack_D', 99), 2 * k + sigma - A.D)
    if A.n == 18:
        ztr = sum(1 for L in range(18) for j in range(len(A.rows[L]) - 1) if not A.usage.get((L, j))
                  for e in (A.rows[L][j], A.rows[L][j + 1]) if A.mult[e] >= 3)
        kap = 2 * A.Z - ztr
        us = sum(1 for L in range(18) for j in range(len(A.rows[L]) - 1) if not A.usage.get((L, j))
                 and A.mult[A.rows[L][j]] == 2 and A.mult[A.rows[L][j + 1]] == 2)
        # budgets hold at T>=94 iff these generalized forms hold with 3T:
        if us + ell > 2 * k + 288 - 3 * A.T:
            bad.append(f'{tag} budget1 fail')
        if kap + 2 * ell > 2 * (2 * k + 288 - 3 * A.T):
            bad.append(f'{tag} budget2 fail')
        st['min_budget1_slack'] = min(st.get('min_budget1_slack', 99), 2 * k + 288 - 3 * A.T - us - ell)

def worker(args):
    wid, N, seed, files = args
    rng = random.Random(seed * 7919 + wid)
    st = Counter(); bad = []
    toks_all = [(int(Path(f).parent.name.split('-')[0]), json.load(open(f))['gens'].split()) for f in files]
    for it in range(N):
        n, toks = rng.choice(toks_all)
        try:
            A = from_tokens(toks, n, complete=True)
            for _ in range(rng.choice([0, 2, 4, 8, 12, 16, 20])):
                s = simple_tris(A)
                if not s: break
                tl = set(L for P in A.triples for L in A.ev[P])
                s2 = [x for x in s if sum(1 for L in set().union(*(A.ev[e] for e in x)) if L in tl) >= 2]
                A = contract(A, rng.choice(s2 if s2 and rng.random() < 0.8 else s))
            for _ in range(rng.choice([0, 1, 3])):
                s = simple_tris(A)
                if s: A = flip(A, rng.choice(s))
        except (ValueError, AssertionError, IndexError):
            st['gen_error'] += 1; continue
        check(A, st, bad, f'w{wid}i{it}')
    return st, bad

if __name__ == '__main__':
    st = Counter(); bad = []
    # centroid example: triangle Q=(0,0), R=(6,0), S=(0,6), cevians through P=(2,2) + far lines
    lines = [[0, 1, 0], [1, 0, 0], [1, 1, -6], [1, -1, 0], [1, 2, -6], [2, 1, -6]]
    rng = random.Random(5)
    while len(lines) < 18:
        cand = lines + [[rng.randint(-30, 30), rng.randint(-30, 30), rng.choice([-1, 1]) * rng.randint(2000, 6000)]]
        try:
            B = from_int_lines(cand)
        except ValueError:
            continue
        if any(len(B.ev[e]) > 2 and any(l >= 6 for l in B.ev[e]) for e in range(len(B.ev))):
            continue
        lines = cand
    A = from_int_lines(lines)
    check(A, st, bad, 'centroid-example')
    print('centroid example: k', len(A.triples), 'D', A.D, [point_info(A, P)[3] for P in A.triples])
    N, seed = int(sys.argv[1]), int(sys.argv[2]); sizes = sys.argv[3:]
    files = [str(f) for s in sizes for f in sorted((GAL / s).glob('*.json'))]
    with Pool(4) as pool:
        for s, b in pool.imap_unordered(worker, [(w, N, seed, files) for w in range(4)]):
            for kk, v in s.items():
                if isinstance(kk, str) and kk.startswith('min'):
                    st[kk] = min(st.get(kk, 99), v)
                else:
                    st[kk] += v
            bad += b
    for kk in sorted(st, key=str):
        print(st[kk], kk)
    print('FAILS', len(bad))
    for b in bad[:10]:
        print('  ', b[:300])

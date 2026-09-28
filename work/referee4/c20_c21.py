"""Referee4: C20 (a) 1-block point, no doubly used bridge on r1,r3,r5 => r2/r3/r4 first segment
unused or ray; (a') the SAT form as written applied to type-X points (premise 'a block on a toward C'
+ no dblbridge on r1,r3,r5) -- expected to be violated; (b) bent point with V0,V4 simple => back
ray 5 unused or ray.  C21 claim 1: two bent points toward one Q are opposite, Q 0-block."""
import json, random, sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee'); sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee4')
from arr import from_tokens
from mutate import simple_tris, contract, flip
from c7_lemmaC import point_info
GAL = Path('/home/nail/stuff/sundai_math/tools/external/kobon-solutions/gallery/data')

def dbl(A, seg): return seg is not None and len(A.usage.get(seg, ())) == 2
def unused_or_ray(A, seg): return seg is None or not A.usage.get(seg)

def check(A, st, bad, tag):
    if any(m > 3 for m in A.mult): return
    bent_to = defaultdict(list)
    for P in A.triples:
        cr, bl, br, typ = point_info(A, P)
        brays = {i for i, _ in br}
        for b in bl:
            i = b['i']
            r = lambda d: (i + d) % 6
            if not ({r(1), r(3), r(5)} & brays):
                concl = any(unused_or_ray(A, cr[r(d)][2]) for d in (2, 3, 4))
                if typ == 'b1':
                    st['C20a_cases'] += 1
                    if not concl: bad.append(f'{tag} C20a FAIL')
                if typ == 'axis':
                    st['C20a_SATform_premise_at_typeX'] += 1
                    if not concl: st['C20a_SATform_VIOLATED_at_typeX'] += 1
        if typ == 'bent':
            mids = sorted(b['i'] for b in bl)
            i1 = mids[0] if (mids[1] - mids[0]) % 6 == 2 else mids[1]
            sh = (i1 + 1) % 6
            Q = cr[sh][3]
            bent_to[Q].append((P, sh))
            V0, V4 = cr[(sh - 2) % 6][3], cr[(sh + 2) % 6][3]
            if V0 is not None and V4 is not None and A.mult[V0] == 2 and A.mult[V4] == 2:
                st['C20b_cases'] += 1
                if not unused_or_ray(A, cr[(sh + 3) % 6][2]): bad.append(f'{tag} C20b FAIL')
    for Q, lst in bent_to.items():
        st[('bent toward same Q', len(lst))] += 1
        if len(lst) > 2: bad.append(f'{tag} C21 >2 bent toward Q')
        if len(lst) == 2:
            (P1, _), (P2, _) = lst
            m = A.ev[P1] & A.ev[P2] & A.ev[Q]
            ok = bool(m) and point_info(A, Q)[3] == 'b0'
            if m:
                (mm,) = tuple(m); ok = ok and (A.idx[mm][P1] - A.idx[mm][Q]) * (A.idx[mm][P2] - A.idx[mm][Q]) < 0
            if not ok: bad.append(f'{tag} C21 claim1 FAIL')
            else: st['C21_pairs_ok'] += 1

def worker(args):
    wid, N, files = args
    rng = random.Random(500 + wid); st = Counter(); bad = []
    for it in range(N):
        f = rng.choice(files); n = int(Path(f).parent.name.split('-')[0])
        try:
            A = from_tokens(json.load(open(f))['gens'].split(), n)
            for _ in range(rng.choice([0, 2, 4, 8, 12, 16, 24])):
                s = simple_tris(A)
                if not s: break
                tl = set(L for P in A.triples for L in A.ev[P])
                s2 = [x for x in s if sum(1 for L in set().union(*(A.ev[e] for e in x)) if L in tl) >= 2]
                A = contract(A, rng.choice(s2 if s2 and rng.random() < 0.9 else s))
            for _ in range(rng.choice([0, 0, 1, 3])):
                s = simple_tris(A)
                if s: A = flip(A, rng.choice(s))
        except (ValueError, AssertionError, IndexError):
            continue
        st['arr'] += 1; check(A, st, bad, f'w{wid}i{it}')
    return st, bad

if __name__ == '__main__':
    files = [str(f) for s in ('10', '12', '14', '16', '18', '18-1', '20') for f in sorted((GAL / s).glob('*.json'))]
    st = Counter(); bad = []
    with Pool(4) as pool:
        for s, b in pool.imap_unordered(worker, [(w, int(sys.argv[1]), files) for w in range(4)]):
            st.update(s); bad += b
    for k in sorted(st, key=str): print(st[k], k)
    print('FAILS', len(bad))
    for b in bad[:10]: print('  ', b[:200])

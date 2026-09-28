"""Referee4: empirical checks for the k = 4 chain C19-C25.
(1) Lemma K4: no 4 multiple points pairwise consecutive (any arrangement).
(2) C22 (general form): bent P with a doubly used back-ray bridge => V0, V4, V5 all multiple;
    bridges to both V0 and V4 => V5 multiple.  At k = 4: no back-ray bridge, e(bent) <= 2.
(3) C24 F1: X vertex P of an all-multiple face PQR: middles on the third line b_P, caps = b_Q, b_R
    (the third lines of Q, R); both face sides at P doubly used.
    F3: non-X face vertex R whose two face neighbours are X: every block of R has its middle on b_R
    and a triple cap; R is not bent.
(4) Accounting at k = 4 (even n): 2*Lambda - n >= sigma - 2*beta + sum m_lb(P) with
    m_lb = X: -1 if sigma-isolated or in an all-multiple face, else -2; bent -1; 1-block: x_P;
    0-block 3; centroid -3.  (Lambda = Z - D + 3k.)
usage: python3 k4_chain.py N SEED"""
import json, random, sys
from collections import Counter
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee'); sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee4')
from arr import from_tokens
from mutate import simple_tris, contract, flip
from c7_lemmaC import point_info
GAL = Path('/home/nail/stuff/sundai_math/tools/external/kobon-solutions/gallery/data')


def cons(A, U, W):
    return any(abs(A.idx[m][U] - A.idx[m][W]) == 1 for m in A.ev[U] & A.ev[W])


def check(A, st, bad, tag):
    if any(m > 3 for m in A.mult):
        return
    T3 = A.triples; k = len(T3)
    # (1) Lemma K4
    for quad in combinations(T3, 4):
        if all(cons(A, u, w) for u, w in combinations(quad, 2)):
            bad.append(f'{tag} K4 FAIL')
    st['K4_quads'] += len(T3) * (len(T3) - 1) * (len(T3) - 2) * (len(T3) - 3) // 24
    info = {P: point_info(A, P) for P in T3}
    tris = set(frozenset(t) for t in A.tris)
    allmult = [t for t in tris if all(A.mult[e] >= 3 for e in t)]
    in_face = set(e for t in allmult for e in t)
    # (2) C22
    for P in T3:
        cr, bl, br, typ = info[P]
        if typ != 'bent':
            continue
        mids = sorted(b['i'] for b in bl)
        i1 = mids[0] if (mids[1] - mids[0]) % 6 == 2 else mids[1]
        sh = (i1 + 1) % 6
        V = {name: cr[(sh + d) % 6][3] for name, d in (('V0', -2), ('V4', 2), ('V5', 3))}
        mult = {nm: v is not None and A.mult[v] >= 3 for nm, v in V.items()}
        brr = {i for i, _ in br}
        if (sh + 3) % 6 in brr and not all(mult.values()):
            bad.append(f'{tag} C22 back-ray bridge without V0,V4,V5 multiple')
        if (sh - 2) % 6 in brr and (sh + 2) % 6 in brr and not mult['V5']:
            bad.append(f'{tag} C22 bridges to V0 and V4 without V5 multiple')
        if k == 4:
            st['k4_bent'] += 1
            if len(br) > 2:
                bad.append(f'{tag} C22 k=4 bent with e>2')
    # (3) C24 F1/F3
    for t in allmult:
        types = {e: info[e][3] for e in t}
        nx = sum(1 for e in t if types[e] == 'axis')
        st[('allmult face', 'k', min(k, 9), 'X vertices', nx)] += 1
        if nx == 3:
            bad.append(f'{tag} F2 FAIL three X face vertices')
        third = {}
        for e in t:
            others = [f for f in t if f != e]
            face_lines = set(A.common_line(e, f) for f in others)
            (b,) = tuple(A.ev[e] - face_lines)
            third[e] = b
        for P in t:
            cr, bl, br, typ = info[P]
            Q, R = [f for f in t if f != P]
            if typ == 'axis':
                if bl[0]['ray'][0] != third[P]:
                    bad.append(f'{tag} F1 axis is not the third line')
                if {b['cap'] for b in bl} != {third[Q], third[R]}:
                    bad.append(f'{tag} F1 caps are not b_Q, b_R')
                for f in (Q, R):
                    L = A.common_line(P, f)
                    j = min(A.idx[L][P], A.idx[L][f])
                    if len(A.usage.get((L, j), ())) != 2:
                        bad.append(f'{tag} F1 face side not doubly used')
                if k == 4 and len(br) != 2:
                    bad.append(f'{tag} F1 k=4 e != 2')
                st['F1_checked'] += 1
        for R in t:
            Q, P = [f for f in t if f != R]
            if types[P] == 'axis' and types[Q] == 'axis' and types[R] != 'axis':
                cr, bl, br, typ = info[R]
                st['F3_checked'] += 1
                if typ == 'bent':
                    bad.append(f'{tag} F3 R bent')
                trip_lines = set(L for X in T3 for L in A.ev[X])
                for b in bl:
                    if b['ray'][0] != third[R] or b['cap'] not in trip_lines:
                        bad.append(f'{tag} F3 block off b_R or non-triple cap')
    # (4) accounting at k = 4
    if k == 4 and A.n % 2 == 0:
        tl = Counter(L for P in T3 for L in A.ev[P])
        sigma = sum(v - 1 for v in tl.values())
        beta = sum(1 for (L, j), s in A.usage.items() if len(s) == 2 and A.mult[A.rows[L][j]] >= 3
                   and A.mult[A.rows[L][j + 1]] >= 3)
        caps_x = {}
        for P in T3:
            cr, bl, br, typ = info[P]
            caps_x[P] = sum(1 for b in bl if sum(1 for v in A.rows[b['cap']] if A.mult[v] >= 3) >= 1)
        msum = 0
        for P in T3:
            typ = info[P][3]
            iso = all(tl[L] == 1 for L in A.ev[P])
            if typ == 'axis':
                msum += -1 if (iso or P in in_face) else -2
            elif typ == 'bent':
                msum += -1
            elif typ == 'b1':
                msum += caps_x[P]
            elif typ == 'b0':
                msum += 3
            else:
                msum += -3
        Lam = A.Z - A.D + 12
        lhs = 2 * Lam - A.n
        rhs = sigma - 2 * beta + msum
        st['k4_arr'] += 1
        st[('k4', 'beta>0', beta > 0)] += 1
        if lhs < rhs:
            bad.append(f'{tag} ACCOUNTING FAIL lhs={lhs} rhs={rhs} n={A.n} tokens={" ".join(A.tokens)}')
        st['k4_min_slack'] = min(st.get('k4_min_slack', 99), lhs - rhs)
        st['k4_min_rhs'] = min(st.get('k4_min_rhs', 99), rhs)


def worker(args):
    wid, N, seed, files = args
    rng = random.Random(seed * 7919 + wid)
    st = Counter(); bad = []
    toks_all = [(int(Path(f).parent.name.split('-')[0]), json.load(open(f))['gens'].split()) for f in files]
    for it in range(N):
        n, toks = rng.choice(toks_all)
        try:
            # start simple-ish: resolve all triple points, then contract 4 triangles near each other
            new = []
            for t in toks:
                if t.endswith('*') and rng.random() < 0.8:
                    g = int(t[:-1])
                    new += [str(g), str(g + 1), str(g)] if rng.random() < 0.5 else [str(g + 1), str(g), str(g + 1)]
                else:
                    new.append(t)
            A = from_tokens(new, n, complete=True)
            for _ in range(rng.choice([0, 1, 3, 6])):
                s = simple_tris(A)
                if s:
                    A = flip(A, rng.choice(s))
            target = rng.choice([4, 4, 4, 5, 6, 8])
            guard = 0
            while len(A.triples) < target and guard < 30:
                guard += 1
                s = simple_tris(A)
                if not s:
                    break
                tl = set(L for P in A.triples for L in A.ev[P])
                s2 = [x for x in s if sum(1 for L in set().union(*(A.ev[e] for e in x)) if L in tl) >= 2]
                A = contract(A, rng.choice(s2 if s2 and rng.random() < 0.9 else s))
        except (ValueError, AssertionError, IndexError):
            st['gen_error'] += 1; continue
        st['arr'] += 1
        try:
            check(A, st, bad, f'w{wid}i{it}')
        except (AssertionError, ValueError, IndexError) as ex:
            bad.append(f'assert {ex!r}')
    return st, bad


if __name__ == '__main__':
    N, seed = int(sys.argv[1]), int(sys.argv[2])
    files = [str(f) for s in ('10', '12', '14', '16', '18', '18-1', '20') for f in sorted((GAL / s).glob('*.json'))]
    st = Counter(); bad = []
    with Pool(4) as pool:
        for s, b in pool.imap_unordered(worker, [(w, N, seed, files) for w in range(4)]):
            for kk, v in s.items():
                if isinstance(kk, str) and kk.startswith('k4_min'):
                    st[kk] = min(st.get(kk, 99), v)
                else:
                    st[kk] += v
            bad += b
    for kk in sorted(st, key=str):
        print(st[kk], kk)
    print('FAILS', len(bad))
    for b in bad[:15]:
        print('  ', b[:300])

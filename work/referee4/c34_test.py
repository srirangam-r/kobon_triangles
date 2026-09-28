"""Referee4: C34 (b), (c) at k >= 5 on contracted/flipped pseudoline arrangements.
(b) type X: bridges only on the two rays bounding a non-cap sector that holds an all-multiple face;
    e in {0,2,4}; faces have <= 2 X vertices; with 2 X vertices the third has <= 1 block, middle on its
    third line, triple cap.  bent: extra-bridge set in {{}, {0}, {4}, {0,4,5}} (C19 labels), c in {1/2,1,2}.
    1-block / 0-block / centroid values.  D = sum(b + e/2).
(c) bent P -> Q: Q has <= 1 block, its middle on line PQ beyond Q; <= 2 bent toward Q, opposite, Q blockless.
usage: python3 c34_test.py N SEED"""
import json, random, sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee'); sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee4')
from arr import from_tokens
from mutate import simple_tris, contract, flip
from c7_lemmaC import point_info
GAL = Path('/home/nail/stuff/sundai_math/tools/external/kobon-solutions/gallery/data')


def check(A, st, bad, tag):
    if any(m > 3 for m in A.mult):
        return
    k = len(A.triples)
    info = {P: point_info(A, P) for P in A.triples}
    tris = set(frozenset(t) for t in A.tris)
    allmult = [t for t in tris if all(A.mult[e] >= 3 for e in t)]
    Dsum = 0.0
    kk = min(k, 9)
    for P in A.triples:
        cr, bl, br, typ = info[P]
        b, e = len(bl), len(br)
        c = b + e / 2 - 2
        Dsum += b + e / 2
        st[('type', typ, 'k>=5', k >= 5)] += 1
        if c > 0:
            st[('c>0', typ, c)] += 1
        if typ == 'axis':
            if e not in (0, 2, 4):
                bad.append(f'{tag} X e={e}')
            capsect = set()
            for bb in bl:
                i = bb['i']; capsect |= {frozenset(((i - 1) % 6, i)), frozenset((i, (i + 1) % 6))}
            noncap = [s for s in (frozenset((j, (j + 1) % 6)) for j in range(6)) if s not in capsect]
            brays = {i for i, _ in br}
            for s_ in noncap:
                i, j = sorted(s_)
                if (i, j) == (0, 5):
                    i, j = 5, 0
                face = cr[i][3] is not None and cr[j][3] is not None and frozenset((P, cr[i][3], cr[j][3])) in tris \
                    and A.mult[cr[i][3]] >= 3 and A.mult[cr[j][3]] >= 3
                on = {i, j} & brays
                if face and on != {i, j}:
                    bad.append(f'{tag} X face in non-cap sector but not both rays bridges')
                if on and not face:
                    bad.append(f'{tag} X bridge without all-multiple face')
            if brays - set().union(*[set(s_) for s_ in noncap]):
                bad.append(f'{tag} X bridge on a middle/cap-only ray')
            if e and k >= 5:
                st[('X e at k>=5', e)] += 1
        if typ == 'bent':
            mids = sorted(bb['i'] for bb in bl)
            i1 = mids[0] if (mids[1] - mids[0]) % 6 == 2 else mids[1]
            sh = (i1 + 1) % 6
            rel = {(sh - 2) % 6: '0', (sh + 2) % 6: '4', (sh + 3) % 6: '5'}
            extra = frozenset(rel[i] for i, _ in br if i != sh)
            if sh not in {i for i, _ in br}:
                bad.append(f'{tag} bent without bridge to Q')
            if extra not in (frozenset(), frozenset('0'), frozenset('4'), frozenset('045')):
                bad.append(f'{tag} bent extra set {sorted(extra)}')
            st[('bent extra', ''.join(sorted(extra)), 'k', kk)] += 1
        if typ == 'centroid' and e != 3:
            bad.append(f'{tag} centroid e={e}')
    if abs(Dsum - A.D) > 1e-9:
        bad.append(f'{tag} D != sum(b+e/2)')
    # faces
    for t in allmult:
        types = {e: info[e][3] for e in t}
        nx = sum(1 for v in types.values() if v == 'axis')
        if nx == 3:
            bad.append(f'{tag} face with 3 X vertices')
        if nx == 2:
            (R,) = [e for e in t if types[e] != 'axis']
            others = [f for f in t if f != R]
            face_lines = {A.common_line(R, f) for f in others}
            (bR,) = tuple(A.ev[R] - face_lines)
            cr, bl, br, typ = info[R]
            trip_lines = set(L for X in A.triples for L in A.ev[X])
            st['F3 (2 X vertices) checked'] += 1
            if len(bl) > 1 or any(bb['ray'][0] != bR or bb['cap'] not in trip_lines for bb in bl):
                bad.append(f'{tag} F3 fail (k={k})')
    # (c) bent partners
    bent_to = defaultdict(list)
    for P in A.triples:
        cr, bl, br, typ = info[P]
        if typ != 'bent':
            continue
        mids = sorted(bb['i'] for bb in bl)
        i1 = mids[0] if (mids[1] - mids[0]) % 6 == 2 else mids[1]
        sh = (i1 + 1) % 6
        Q = cr[sh][3]
        bent_to[Q].append(P)
        crQ, blQ, brQ, typQ = info[Q]
        if len(blQ) > 1:
            bad.append(f'{tag} bent partner has {len(blQ)} blocks ({typQ})')
        m = cr[sh][0]  # line PQ
        for bb in blQ:
            w, d = bb['ray'][0], bb['ray'][1]
            # middle must lie on PQ, pointing away from P
            kq, kp = A.idx[m][Q], A.idx[m][P]
            away = 1 if kq > kp else -1
            if w != m or d != away:
                bad.append(f'{tag} partner block middle not on PQ beyond Q')
        st[('bent partner type', typQ, 'k', kk)] += 1
    for Q, lst in bent_to.items():
        st[('#bent toward Q', len(lst))] += 1
        if len(lst) > 2:
            bad.append(f'{tag} >2 bent toward Q')
        if len(lst) == 2:
            P1, P2 = lst
            m = A.ev[P1] & A.ev[P2] & A.ev[Q]
            ok = bool(m) and info[Q][3] == 'b0'
            if m:
                (mm,) = tuple(m)
                ok = ok and (A.idx[mm][P1] - A.idx[mm][Q]) * (A.idx[mm][P2] - A.idx[mm][Q]) < 0
            if not ok:
                bad.append(f'{tag} two bent toward Q not opposite / Q not blockless')


def worker(args):
    wid, N, seed = args
    rng = random.Random(seed * 7919 + wid); st = Counter(); bad = []
    files = [f for s in ('10', '12', '14', '16', '18', '18-1') for f in sorted((GAL / s).glob('*.json'))]
    for it in range(N):
        f = rng.choice(files); n = int(f.parent.name.split('-')[0])
        try:
            A = from_tokens(json.load(open(f))['gens'].split(), n)
            for _ in range(rng.choice([2, 4, 6, 10, 16, 24])):
                s = simple_tris(A)
                if not s: break
                # bias strongly toward triangles sharing two lines with existing triple points (bridges, bent)
                tl = set(L for P in A.triples for L in A.ev[P])
                s2 = [x for x in s if sum(1 for L in set().union(*(A.ev[e] for e in x)) if L in tl) >= 2]
                s3 = [x for x in s2 if any(A.mult[v] >= 3 for e in x for L in A.ev[e] for v in A.rows[L]
                                           if abs(A.idx[L][v] - A.idx[L][e]) == 1)]
                pool_ = s3 if s3 and rng.random() < 0.6 else (s2 if s2 and rng.random() < 0.8 else s)
                A = contract(A, rng.choice(pool_))
            for _ in range(rng.choice([0, 0, 1, 3])):
                s = simple_tris(A)
                if s: A = flip(A, rng.choice(s))
        except (ValueError, AssertionError, IndexError):
            continue
        st['arr'] += 1
        st[('k>=5', len(A.triples) >= 5)] += 1
        try:
            check(A, st, bad, f'w{wid}i{it}')
        except (AssertionError, ValueError, IndexError) as ex:
            bad.append(f'assert {ex!r}')
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
    for b in bad[:15]:
        print('  ', b[:200])

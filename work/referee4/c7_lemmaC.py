"""Referee4: empirical test of Lemma C (work/t3/shared.md) on pseudoline arrangements with
many triple points on shared lines (gallery + contractions of simple triangles + flips).
Per triple point: b = #blocks, e = #doubly used bridges at P, c = b + e/2 - 2, type.
Checks: D = sum(b + e/2); b <= 3; axis: e>0 => P in an all-multiple triangular face lying in a
non-cap sector; bent: e>=1, e>1 => a cap line through Q and another multiple point;
records max c per type.  usage: python3 c7_lemmaC.py N SEED sizes..."""
import json, random, sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee')
from arr import from_tokens  # noqa
from mutate import simple_tris, flip, contract  # noqa
GAL = Path('/home/nail/stuff/sundai_math/tools/external/kobon-solutions/gallery/data')


def point_info(A, P):
    cr, bl = A.blocks(P)
    bridges = []
    for i, (w, d, edge, far) in enumerate(cr):
        if edge is not None and len(A.usage.get(edge, ())) == 2 and A.mult[far] >= 3:
            bridges.append((i, far))
    mids = sorted(b['i'] for b in bl)
    if len(bl) == 2:
        dd = (mids[1] - mids[0]) % 6
        typ = 'axis' if dd == 3 else ('bent' if dd in (2, 4) else 'adjacent')
    else:
        typ = {0: 'b0', 1: 'b1', 3: 'centroid'}.get(len(bl), 'b%d' % len(bl))
    return cr, bl, bridges, typ


def check(A, st, bad, tag):
    if any(m > 3 for m in A.mult):
        st['skip4'] += 1
        return
    t = len(A.triples)
    st['arr'] += 1
    st[f't{min(t, 12)}'] += 1
    tris = set(frozenset(x) for x in A.tris)
    Dsum = 0.0
    for P in A.triples:
        cr, bl, br, typ = point_info(A, P)
        b, e = len(bl), len(br)
        c = b + e / 2 - 2
        Dsum += b + e / 2
        st[('type', typ)] += 1
        key = ('maxc', typ)
        st[key] = max(st.get(key, -9), c)
        if typ in ('adjacent',) or b > 3:
            bad.append(f'{tag} impossible type {typ}')
        if typ == 'centroid' and e != 3:
            bad.append(f'{tag} centroid e={e}')
        if typ == 'axis' and e > 0:
            # each bridge ray i: the non-cap sector next to it must hold an all-multiple face
            capsect = set()
            for bb in bl:
                i = bb['i']; capsect |= {frozenset(((i - 1) % 6, i)), frozenset((i, (i + 1) % 6))}
            for i, far in br:
                ok = False
                for j in ((i - 1) % 6, (i + 1) % 6):
                    if frozenset((i, j)) in capsect:
                        continue
                    other = cr[j][3]
                    if other is not None and A.mult[other] >= 3 and frozenset((P, far, other)) in tris:
                        ok = True
                if not ok:
                    bad.append(f'{tag} axis bridge without all-multiple face in non-cap sector')
            st['axis_with_bridge'] += 1
            st[('axis_e', e)] += 1
        if typ == 'bent':
            mids = sorted(bb['i'] for bb in bl)
            shared = (mids[0] + 1) % 6 if (mids[1] - mids[0]) % 6 == 2 else (mids[1] + 1) % 6
            Q = cr[shared][3]
            if not any(i == shared for i, _ in br):
                bad.append(f'{tag} bent without bridge to Q')
            others = [far for i, far in br if i != shared]
            for far in others:
                if not any(Q in A.rows[bb['cap']] and far in A.rows[bb['cap']] for bb in bl):
                    st['bent_extra_bridge_far_not_on_cap'] += 1
            ncapmulti = sum(1 for bb in bl if sum(1 for v in A.rows[bb['cap']] if A.mult[v] >= 3) >= 2)
            st[('bent_e', e, 'caps_with_2mult', ncapmulti)] += 1
            if e > 1 and ncapmulti == 0:
                bad.append(f'{tag} bent e>1 without cap line through Q and another multiple point')
            if c > 1.5:
                st['BENT_c_gt_1.5'] += 1
                if st['BENT_c_gt_1.5'] <= 3:
                    bad.append(f'INFO bent c={c} e={e} {tag} tokens={" ".join(A.tokens)}')
        if typ == 'b1' and c > 0:
            st['b1_c_pos'] += 1
        if typ == 'b0' and c > 0:
            st['b0_c_pos'] += 1
    beta = sum(1 for (L, j), s in A.usage.items() if len(s) == 2 and A.mult[A.rows[L][j]] >= 3
               and A.mult[A.rows[L][j + 1]] >= 3)
    if abs(Dsum - A.D) > 1e-9:
        bad.append(f'{tag} D != sum(b+e/2): {A.D} {Dsum}')
    st[('beta>0', beta > 0)] += 1
    if A.n == 18:
        lhs = Dsum - 2 * t
        st['max_sum_c_minus_(t-6+Z)'] = max(st.get('max_sum_c_minus_(t-6+Z)', -99), lhs - (t - 6 + A.Z))
        st['maxT18'] = max(st.get('maxT18', 0), A.T)


def worker(args):
    wid, N, seed, files = args
    rng = random.Random(seed * 7919 + wid)
    st = Counter(); bad = []
    toks_all = [(int(Path(f).parent.name.split('-')[0]), json.load(open(f))['gens'].split()) for f in files]
    for it in range(N):
        n, toks = rng.choice(toks_all)
        try:
            A = from_tokens(toks, n, complete=True)
            for _ in range(rng.choice([2, 4, 6, 8, 12, 16])):
                s = simple_tris(A)
                if not s:
                    break
                # prefer triangles touching existing triple points' lines (shared lines, bridges)
                trip_lines = set(L for P in A.triples for L in A.ev[P])
                s2 = [x for x in s if sum(1 for L in set().union(*(A.ev[e] for e in x)) if L in trip_lines) >= 2]
                A = contract(A, rng.choice(s2 if s2 and rng.random() < 0.7 else s))
            for _ in range(rng.choice([0, 0, 1, 3])):
                s = simple_tris(A)
                if s:
                    A = flip(A, rng.choice(s))
        except (ValueError, AssertionError, IndexError):
            st['gen_error'] += 1; continue
        try:
            check(A, st, bad, f'w{wid}i{it}')
        except AssertionError as ex:
            bad.append(f'assert {ex!r}')
    return st, bad


if __name__ == '__main__':
    N, seed = int(sys.argv[1]), int(sys.argv[2]); sizes = sys.argv[3:]
    files = [str(f) for s in sizes for f in sorted((GAL / s).glob('*.json'))]
    st = Counter(); bad = []
    with Pool(4) as pool:
        for s, b in pool.imap_unordered(worker, [(w, N, seed, files) for w in range(4)]):
            for k, v in s.items():
                if isinstance(k, tuple) and k[0] == 'maxc' or (isinstance(k, str) and k.startswith('max')):
                    st[k] = max(st.get(k, -99), v)
                else:
                    st[k] += v
            bad += b
    for k in sorted(st, key=str):
        print(st[k], k)
    real = [b for b in bad if not b.startswith('INFO')]
    print('FAILS', len(real))
    for b in real[:20]:
        print('  ', b[:300])
    for b in bad:
        if b.startswith('INFO'):
            print('  ', b[:2000])

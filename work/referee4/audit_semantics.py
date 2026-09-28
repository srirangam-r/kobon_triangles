"""Referee4 k6z audit: evaluate the per-end constraints of search/wedge_cubes_c26.py and
search/wedge_cubes_single.py on REAL pseudoline arrangements, using the solver's own literal
semantics (chi from the wiring, before() exactly as in build_defect, tri = triangular face).
For every line end (L, e) whose 2nd vertex (from e) is a type-X triple point P with axis L and whose
1st vertex is simple, the C26 (a)/(b) shape holds in any arrangement, so both encodings must be
satisfied (the c26 one with L2 := the cap line at the 3rd vertex).  Also checks the wedge units:
for a mutual end at position p (left end if p < 18), c17f/c17l semantics = the real first/last vertex."""
import json, random, sys
from collections import Counter
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee'); sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee4')
from arr import from_tokens
from mutate import simple_tris, contract, flip
from c7_lemmaC import point_info
from c17_test import chi_from_arr, sat_before
GAL = Path('/home/nail/stuff/sundai_math/tools/external/kobon-solutions/gallery/data')


def check(A, st, bad, tag):
    n = A.n
    if any(m > 3 for m in A.mult):
        return
    chi = chi_from_arr(A)
    z = lambda a, b, c: chi[tuple(sorted((a, b, c)))] == 0
    TL = set()
    for t in A.tris:
        TL.add(frozenset(A.common_line(u, v) for u, v in ((t[0], t[1]), (t[1], t[2]), (t[0], t[2]))))
    tri = lambda a, b, c: frozenset((a, b, c)) in TL
    before = lambda r, i, j: sat_before(chi, r, i, j)
    info = {P: point_info(A, P) for P in A.triples}
    for L in range(n):
        for left in (True, False):
            r = A.rows[L] if left else A.rows[L][::-1]
            if len(r) < 3 or A.mult[r[0]] != 2 or r[1] not in info:
                continue
            P = r[1]
            cr, bl, br, typ = info[P]
            if typ != 'axis' or bl[0]['ray'][0] != L:
                continue
            X3 = r[2]
            if A.mult[X3] != 2:
                bad.append(f'{tag} X3 not simple'); continue
            (L2,) = tuple(A.ev[X3] - {L})
            st['ends'] += 1
            # ---- wedge_cubes_c26 per-direction constraints
            others = [x for x in range(n) if x not in (L, L2)]
            bef = {x: (before(L, x, L2) if left else before(L, L2, x)) for x in others}
            if any(z(L, L2, x) for x in others):
                bad.append(f'{tag} c26: 3rd vertex not simple')
            if sum(bef.values()) != 3:
                bad.append(f'{tag} c26: #before != 3 ({sum(bef.values())})')
            if not any(z(L, b, c) and bef[b] and bef[c] and tri(L, b, L2) and tri(L, c, L2)
                       for b, c in combinations(others, 2)):
                bad.append(f'{tag} c26: no witness')
            # ---- wedge_cubes_single constraints
            bf = lambda x, y: before(L, x, y) if left else before(L, y, x)
            ok = False
            for b, c in combinations([x for x in range(n) if x != L], 2):
                if not z(L, b, c):
                    continue
                rest = [x for x in range(n) if x not in (L, b, c)]
                if sum(bf(x, b) for x in rest) > 1:
                    continue
                v1 = any(bf(x, b) and tri(L, b, x) and tri(L, c, x) for x in rest)
                v2 = any(bf(b, x) and tri(L, b, x) and tri(L, c, x) for x in rest)
                if v1 and v2:
                    ok = True
            if not ok:
                bad.append(f'{tag} single: no w(b,c)')
    # ---- wedge units: mutual end semantics per position
    for L in range(n):
        for end in (0, -1):
            X = A.rows[L][end]
            if A.mult[X] != 2:
                continue
            (R,) = tuple(A.ev[X] - {L})
            first = all(not before(L, M, R) and not z(L, R, M) for M in range(n) if M not in (L, R))
            last = all(not before(L, R, M) and not z(L, R, M) for M in range(n) if M not in (L, R))
            st['end_units'] += 1
            if (end == 0 and not first) or (end == -1 and not last):
                bad.append(f'{tag} unit semantics: c17f/c17l mismatch')


def worker(args):
    wid, N = args
    rng = random.Random(900 + wid); st = Counter(); bad = []
    files = [f for s in ('10', '12', '14', '16', '18', '18-1', '20') for f in sorted((GAL / s).glob('*.json'))]
    for it in range(N):
        f = rng.choice(files); n = int(f.parent.name.split('-')[0])
        try:
            A = from_tokens(json.load(open(f))['gens'].split(), n)
            for _ in range(rng.choice([0, 1, 3, 6])):
                s = simple_tris(A)
                if s: A = contract(A, rng.choice(s))
            for _ in range(rng.choice([0, 0, 2, 8])):
                s = simple_tris(A)
                if s: A = flip(A, rng.choice(s))
        except (ValueError, AssertionError, IndexError):
            continue
        st['arr'] += 1
        check(A, st, bad, f'w{wid}i{it}')
    return st, bad


if __name__ == '__main__':
    st = Counter(); bad = []
    with Pool(4) as pool:
        for s, b in pool.imap_unordered(worker, [(w, int(sys.argv[1])) for w in range(4)]):
            st.update(s); bad += b
    print(dict(st), 'FAILS', len(bad))
    for b in bad[:10]:
        print('  ', b[:200])

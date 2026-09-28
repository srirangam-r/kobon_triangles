"""Referee4 k5 audit: on real pseudoline arrangements, for every line end (a, e) whose 2nd vertex is a
type-X point U with axis a, 1st vertex simple, 3rd vertex X simple (other line D) and 4th vertex Y simple
(other line L): check with the solver's literal semantics that
  (i) exactly 4 lines cross a strictly before L counted from e, and none passes through a∩L;
  (ii) the slack orientation of k5_cubes: from a left end, before(a, D, L); from a right end, before(a, L, D);
  (iii) if Y is also an end vertex of L, then end(t, a) (c17f for L's left end, c17l for its right end) holds."""
import json, random, sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee'); sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee4')
from arr import from_tokens
from mutate import simple_tris, contract, flip
from c7_lemmaC import point_info
from c17_test import chi_from_arr, sat_before
GAL = Path('/home/nail/stuff/sundai_math/tools/external/kobon-solutions/gallery/data')

def check(A, st, bad):
    n = A.n
    if any(m > 3 for m in A.mult): return
    chi = chi_from_arr(A)
    z = lambda a, b, c: chi[tuple(sorted((a, b, c)))] == 0
    before = lambda r, i, j: sat_before(chi, r, i, j)
    info = {P: point_info(A, P) for P in A.triples}
    for a in range(n):
        for left in (True, False):
            r = A.rows[a] if left else A.rows[a][::-1]
            if len(r) < 4 or A.mult[r[0]] != 2 or r[1] not in info: continue
            cr, bl, br, typ = info[r[1]]
            if typ != 'axis' or bl[0]['ray'][0] != a: continue
            if A.mult[r[2]] != 2 or A.mult[r[3]] != 2: continue
            (D,) = tuple(A.ev[r[2]] - {a}); (L,) = tuple(A.ev[r[3]] - {a})
            st['cases'] += 1
            others = [x for x in range(n) if x not in (a, L)]
            cnt = sum(before(a, x, L) if left else before(a, L, x) for x in others)
            if cnt != 4 or any(z(a, L, x) for x in others): bad.append('count')
            if not (before(a, D, L) if left else before(a, L, D)): bad.append('orientation')
            Y = r[3]
            for end_i, is_first in ((0, True), (-1, False)):
                if A.rows[L][end_i] == Y:
                    st['Y_is_end_of_L'] += 1
                    ok = all(not (before(L, M, a) if is_first else before(L, a, M)) and not z(L, a, M) for M in range(n) if M not in (L, a))
                    if not ok: bad.append('end(t,a)')

def worker(args):
    wid, N = args
    rng = random.Random(1300 + wid); st = Counter(); bad = []
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
        st['arr'] += 1; check(A, st, bad)
    return st, bad

if __name__ == '__main__':
    st = Counter(); bad = []
    with Pool(4) as pool:
        for s, b in pool.imap_unordered(worker, [(w, int(sys.argv[1])) for w in range(4)]):
            st.update(s); bad += b
    print(dict(st), 'FAILS', len(bad), Counter(bad))

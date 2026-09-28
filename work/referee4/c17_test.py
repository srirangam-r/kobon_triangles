"""Referee4, C17 Statement 1 and its SAT form.
(1) geometric check: wiring labels (left order top->bottom = slope order), first = leftmost vertex.
(2) SAT-literal check: chi from the wiring (chi(i,j,k) = +1 iff crossing of i,k is above j,
    0 if concurrent), before(r,i,j) exactly as kobon_sat.build_defect defines it,
    first(L,R) := AND_M !before(L,M,R) AND AND_M !z(L,R,M);  last(L,R) := AND_M !before(L,R,M) AND ...
    then every forbidden combination of the SAT form must be false.
(3) the same on exact integer certificates via kobon_sat.chi3_from_lines (real slopes).
Also C17 Statement 2 (Z = 0 context does not occur in data; checked in the form
'X_1 simple, t_1 single, R_1's piece on side -t_1 is unused or a ray; if a ray, then X_1 is an end of R_1').
usage: python3 c17_test.py N SEED sizes..."""
import json, random, sys, glob
from collections import Counter
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee')
sys.path.insert(0, '/home/nail/stuff/sundai_math/search')
from arr import from_tokens, from_int_lines  # noqa
from mutate import simple_tris, flip, contract  # noqa
GAL = Path('/home/nail/stuff/sundai_math/tools/external/kobon-solutions/gallery/data')


def chi_from_arr(A):
    n = A.n
    chi = {}
    for i, j, k in combinations(range(n), 3):
        e = A.pe(i, k)
        if j in A.ev[e]:
            chi[i, j, k] = 0
        else:
            chi[i, j, k] = -A.side(e, j)
    return chi


def sat_before(chi, r, i, j):
    t = tuple(sorted((r, i, j)))
    return chi[t] == -1 if i < j else chi[t] == 1


def sat_checks(n, chi, st, bad, tag, A=None):
    def z(a, b, c):
        return chi[tuple(sorted((a, b, c)))] == 0

    def first(L, R):
        return all(not sat_before(chi, L, M, R) and not z(L, R, M) for M in range(n) if M not in (L, R))

    def last(L, R):
        return all(not sat_before(chi, L, R, M) and not z(L, R, M) for M in range(n) if M not in (L, R))
    F = {(L, R): first(L, R) for L in range(n) for R in range(n) if L != R}
    Ls = {(L, R): last(L, R) for L in range(n) for R in range(n) if L != R}
    for L in range(n):
        assert sum(F[L, R] for R in range(n) if R != L) <= 1
        assert sum(Ls[L, R] for R in range(n) if R != L) <= 1
    for L, R in combinations(range(n), 2):
        ff, ll = F[L, R] and F[R, L], Ls[L, R] and Ls[R, L]
        fl, lf = F[L, R] and Ls[R, L], Ls[L, R] and F[R, L]
        if ff or ll or fl or lf:
            st['sat_mutual_end'] += 1
        adj = R - L == 1
        wrap = (L, R) == (0, n - 1)
        if (ff or ll) and not adj:
            bad.append(f'{tag} SAT first/first or last/last with L={L} R={R}')
        if (fl or lf) and not wrap:
            bad.append(f'{tag} SAT mixed with L={L} R={R}')
    if A is not None:
        # SAT 'before' must equal the real order along each line, in one global direction
        dirs = Counter()
        for r in range(n):
            for i, j in combinations([x for x in range(n) if x != r], 2):
                ei, ej = A.pe(r, i), A.pe(r, j)
                if ei == ej:
                    continue
                real = A.idx[r][ei] < A.idx[r][ej]
                dirs[sat_before(chi, r, i, j) == real] += 1
        st[('sat_before==left_to_right', tuple(sorted(dirs)))] += 1


def geo_checks(A, st, bad, tag):
    n = A.n
    for L in range(n):
        for end in (0, -1):
            X = A.rows[L][end]
            if A.mult[X] != 2:
                continue
            (R,) = tuple(A.ev[X] - {L})
            if A.rows[R][0] == X:
                e2 = 0
            elif A.rows[R][-1] == X:
                e2 = -1
            else:
                continue
            st['geo_mutual_end'] += 1
            lo, hi = sorted((L, R))
            ok = (hi - lo == 1) if end == e2 else ((lo, hi) == (0, n - 1))
            if not ok:
                bad.append(f'{tag} GEO FAIL L={L} R={R} ends {end},{e2}')
    # Statement 2 core (valid without Z=0): X_1 simple, t_1 single = s  =>  R_1's piece on side -s unused
    for L in range(n):
        t = A.tseq(L)
        for end, ti in ((0, 1), (-1, len(t) - 2)):
            X = A.rows[L][end]
            if A.mult[X] != 2 or len(t[ti]) != 1:
                continue
            (s,) = tuple(t[ti])
            R, pcs = A.pieces(L, X)
            key = pcs[-s]
            st['st2_cases'] += 1
            if key is not None and A.usage.get(key):
                bad.append(f'{tag} ST2 FAIL piece on side -t used')
            if key is None:
                st['st2_ray'] += 1
                if not (A.rows[R][0] == X or A.rows[R][-1] == X):
                    bad.append(f'{tag} ST2 FAIL ray but X not an end of R')
                # the triangle over the end segment uses R's bounded piece at X
                if pcs[s] is None or not A.usage.get(pcs[s]):
                    bad.append(f'{tag} ST2 FAIL corner face not using R piece')


def worker(args):
    wid, N, seed, files = args
    rng = random.Random(seed * 7919 + wid)
    st = Counter(); bad = []
    toks_all = [(int(Path(f).parent.name.split('-')[0]), json.load(open(f))['gens'].split()) for f in files]
    for it in range(N):
        n, toks = rng.choice(toks_all)
        try:
            A = from_tokens(toks, n, complete=True)
            for _ in range(rng.choice([0, 1, 3, 6, 10])):
                s = simple_tris(A)
                if s:
                    A = contract(A, rng.choice(s))
            for _ in range(rng.choice([0, 1, 3, 10, 30])):
                s = simple_tris(A)
                if s:
                    A = flip(A, rng.choice(s))
        except (ValueError, AssertionError, IndexError):
            st['gen_error'] += 1; continue
        if any(m > 3 for m in A.mult):
            continue
        st['arr'] += 1
        tag = f'w{wid}i{it}'
        geo_checks(A, st, bad, tag)
        sat_checks(n, chi_from_arr(A), st, bad, tag, A)
    return st, bad



def chi3_from_lines(lines):
    """Copied verbatim in logic from search/kobon_sat.py (pysat not needed)."""
    from fractions import Fraction
    if any(b == 0 for _, b, _ in lines):
        return None, None
    slopes = [(Fraction(-a, b), Fraction(-c, b)) for a, b, c in lines]
    order = sorted(range(len(lines)), key=lambda i: slopes[i][0])
    ms = [slopes[i] for i in order]
    if len({m for m, _ in ms}) < len(ms):
        return None, None
    chi = {}
    for i, j, k in combinations(range(len(ms)), 3):
        (mi, qi), (mj, qj), (mk, qk) = ms[i], ms[j], ms[k]
        x = (qk - qi) / (mi - mk)
        y, yj = mi * x + qi, mj * x + qj
        chi[i, j, k] = (y > yj) - (y < yj)
    return order, chi


def cert(f):
    st = Counter(); bad = []
    d = json.load(open(f))
    lines = d['lines'] if isinstance(d, dict) else d
    order, chi = chi3_from_lines(lines)
    if chi is None:
        st['cert_skipped'] += 1
        return st, bad
    n = len(lines)
    st['cert'] += 1
    sat_checks(n, chi, st, bad, f)
    # geometric check with real slope labels
    A = from_int_lines([lines[i] for i in order])
    # relabel: from_int_lines keeps given order = slope order; first = smallest x
    for L in range(n):
        a, b, c = lines[order[L]]
        key = lambda e: None
    geo_ok = 0
    from fractions import Fraction
    def xcoord(e):
        ls = sorted(A.ev[e])[:2]
        (a1, b1, c1), (a2, b2, c2) = lines[order[ls[0]]], lines[order[ls[1]]]
        return Fraction(b1 * c2 - c1 * b2, a1 * b2 - b1 * a2)
    for L in range(n):
        vs = sorted(A.rows[L], key=xcoord)
        for pos in (0, -1):
            X = vs[pos]
            if A.mult[X] != 2:
                continue
            (R,) = tuple(A.ev[X] - {L})
            vr = sorted(A.rows[R], key=xcoord)
            if vr[0] == X: e2 = 0
            elif vr[-1] == X: e2 = -1
            else: continue
            lo, hi = sorted((L, R))
            ok = (hi - lo == 1) if pos == e2 else ((lo, hi) == (0, n - 1))
            st['cert_geo_mutual_end'] += 1
            if not ok:
                bad.append(f'{f} CERT GEO FAIL')
    return st, bad


if __name__ == '__main__':
    N, seed = int(sys.argv[1]), int(sys.argv[2]); sizes = sys.argv[3:]
    st = Counter(); bad = []
    certs = sorted(glob.glob('/home/nail/stuff/sundai_math/work/certs/*/solution.json'))
    for f in certs:
        try:
            s, b = cert(f)
        except Exception as ex:  # report, do not hide
            s, b = Counter(cert_error=1), [f'{f} cert error {ex!r}']
        st.update(s); bad += b
    files = [str(f) for s in sizes for f in sorted((GAL / s).glob('*.json'))]
    with Pool(4) as pool:
        for s, b in pool.imap_unordered(worker, [(w, N, seed, files) for w in range(4)]):
            st.update(s); bad += b
    for k in sorted(st, key=str):
        print(st[k], k)
    print('FAILS', len(bad))
    for b in bad[:20]:
        print('  ', b[:300])

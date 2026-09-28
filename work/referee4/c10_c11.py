"""Referee4: C10 (Lemma A clause) and C11 (Lemma D parity through triple points).
C10: z(abc) & tri(abC) & tri(acC) & tri(aCN) => C^N in {C^b, C^c}   (tri = face with those 3 side lines)
     + consequence: if C^b, C^c simple and X=a^C simple, segment of a beyond X unused (if bounded).
C11: L not a cap line (no doubly used piece of another line at a simple crossing of L), no 4-fold
     point on L, every triple point P on L has single entries on both sides; j + q even => kappa(L) >= 1.
usage: python3 c10_c11.py N SEED sizes...   (plus the whole gallery once)"""
import json, random, sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee')
from arr import from_tokens  # noqa
from mutate import simple_tris, flip, contract  # noqa
GAL = Path('/home/nail/stuff/sundai_math/tools/external/kobon-solutions/gallery/data')


def tri_lines(A, t):
    out = set()
    for u, v in ((t[0], t[1]), (t[1], t[2]), (t[0], t[2])):
        out.add(A.common_line(u, v))
    return frozenset(out)


def check(A, st, bad, tag):
    n = A.n
    TL = set(tri_lines(A, t) for t in A.tris)
    # ---- C10
    for P in A.triples:
        if A.mult[P] != 3:
            continue
        ls = sorted(A.ev[P])
        for a in ls:
            b, c = [x for x in ls if x != a]
            for C in range(n):
                if C in ls:
                    continue
                if frozenset((a, b, C)) not in TL or frozenset((a, c, C)) not in TL:
                    continue
                st['C10_premise'] += 1
                Cb, Cc = A.pe(b, C), A.pe(c, C)
                for N in range(n):
                    if N in ls or N == C:
                        continue
                    if frozenset((a, C, N)) in TL:
                        st['C10_triCN'] += 1
                        if A.pe(C, N) not in (Cb, Cc):
                            bad.append(f'{tag} C10 FAIL P={ls} a={a} C={C} N={N}')
                X = A.pe(a, C)
                if A.mult[Cb] == 2 and A.mult[Cc] == 2 and A.mult[X] == 2:
                    kx, kp = A.idx[a][X], A.idx[a][P]
                    if abs(kx - kp) != 1:
                        bad.append(f'{tag} C10 P,X not consecutive')
                        continue
                    j = kx if kx > kp else kx - 1  # segment beyond X
                    if 0 <= j < len(A.rows[a]) - 1:
                        st['C10_cons_checked'] += 1
                        if A.usage.get((a, j)):
                            bad.append(f'{tag} C10 consequence FAIL')
    # ---- C11
    for L in range(n):
        r = A.rows[L]
        if any(A.mult[e] > 3 for e in r):
            continue
        t = A.tseq(L)
        simple = [A.mult[e] == 2 for e in r]
        # (i) not a cap line
        capline = False
        for i, e in enumerate(r):
            if not simple[i]:
                continue
            R, pcs = A.pieces(L, e)
            for s, key in pcs.items():
                if key is not None and len(A.usage.get(key, ())) == 2:
                    capline = True
        if capline:
            continue
        ok = True; j = 0; q = 0
        for i, e in enumerate(r):
            if simple[i]:
                continue
            j += 1
            a, b = t[i], t[i + 1]
            if i == 0 or i == len(r) - 1 or len(a) != 1 or len(b) != 1:
                ok = False; break
            q += a == b
        if not ok:
            continue
        # (single entries also between simple crossings are automatic by L1)
        st['C11_lines'] += 1
        claims = any(A.claims_at(L, e) for i, e in enumerate(r) if simple[i])
        if (j + q) % 2 == 0:
            st['C11_even'] += 1
            st[('C11_even_j', j, 'q', q)] += 1
            if not claims:
                bad.append(f'{tag} C11 FAIL L={L} j={j} q={q}')
        else:
            st['C11_odd'] += 1
            st['C11_odd_noclaim'] += not claims


def gal(f):
    n = int(Path(f).parent.name.split('-')[0])
    st = Counter(); bad = []
    if n % 2:
        return st, bad
    A = from_tokens(json.loads(Path(f).read_text())['gens'].split(), n)
    check(A, st, bad, f)
    st['arr'] += 1
    return st, bad


def worker(args):
    wid, N, seed, files = args
    rng = random.Random(seed * 7919 + wid)
    st = Counter(); bad = []
    toks_all = [(int(Path(f).parent.name.split('-')[0]), json.load(open(f))['gens'].split()) for f in files]
    for it in range(N):
        n, toks = rng.choice(toks_all)
        try:
            A = from_tokens(toks, n, complete=True)
            for _ in range(rng.choice([0, 1, 2, 4, 8, 12])):
                s = simple_tris(A)
                if s:
                    A = contract(A, rng.choice(s))
            for _ in range(rng.choice([0, 0, 1, 3, 6])):
                s = simple_tris(A)
                if s:
                    A = flip(A, rng.choice(s))
        except (ValueError, AssertionError, IndexError):
            st['gen_error'] += 1; continue
        st['arr'] += 1
        check(A, st, bad, f'w{wid}i{it}')
    return st, bad


if __name__ == '__main__':
    N, seed = int(sys.argv[1]), int(sys.argv[2]); sizes = sys.argv[3:]
    st = Counter(); bad = []
    gfiles = [str(f) for d in sorted(GAL.iterdir()) if d.is_dir() for f in sorted(d.glob('*.json'))]
    files = [str(f) for s in sizes for f in sorted((GAL / s).glob('*.json'))]
    with Pool(4) as pool:
        for s, b in pool.imap_unordered(gal, gfiles, chunksize=8):
            st.update(s); bad += b
        for s, b in pool.imap_unordered(worker, [(w, N, seed, files) for w in range(4)]):
            st.update(s); bad += b
    for k in sorted(st, key=str):
        print(st[k], k)
    print('FAILS', len(bad))
    for b in bad[:20]:
        print('  ', b[:300])

"""Referee4: C13 (axis parity through other triple points) and C15 (mutual-pair shape, and the
parity statement on the mutual line).  usage: python3 c13_c15.py N SEED sizes..."""
import json, random, sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee')
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee4')
from arr import from_tokens  # noqa
from mutate import simple_tris, flip, contract  # noqa
from c7_lemmaC import point_info  # noqa
GAL = Path('/home/nail/stuff/sundai_math/tools/external/kobon-solutions/gallery/data')


def check(A, st, bad, tag):
    if any(m > 3 for m in A.mult) or A.n % 2:
        return
    info = {P: point_info(A, P) for P in A.triples}
    caps = set(b['cap'] for P in info for b in info[P][1])
    beta = sum(1 for (L, j), s in A.usage.items() if len(s) == 2 and A.mult[A.rows[L][j]] >= 3
               and A.mult[A.rows[L][j + 1]] >= 3)
    axis_of = {}
    for P, (cr, bl, br, typ) in info.items():
        if typ == 'axis':
            axis_of[P] = bl[0]['ray'][0]
    # ---------------- C13
    for P, a in axis_of.items():
        r = A.rows[a]; t = A.tseq(a)
        if a in caps:
            continue
        p = r.index(P) + 1  # X_p
        # (ii)
        if not (p - 2 >= 0 and not t[p - 2]) or not (p + 1 <= len(r) and not t[p + 1]):
            continue
        others = [i for i, e in enumerate(r) if A.mult[e] >= 3 and e != P]
        ok = True; q = 0
        for i in others:
            x, y = t[i], t[i + 1]
            if i == 0 or i == len(r) - 1 or len(x) != 1 or len(y) != 1:
                ok = False; break
            q += x == y
        if not ok:
            continue
        jp = len(others)
        touch = any(A.claims_at(a, e) for e in r if A.mult[e] == 2)
        st[('C13', 'j', jp, 'q', q, 'even' if (jp + q) % 2 == 0 else 'odd', 'touch', touch)] += 1
        if (jp + q) % 2 == 0 and not touch:
            bad.append(f'{tag} C13 FAIL P axis={a} j\'={jp} q={q}')
    # ---------------- C15 shape
    for P, a in axis_of.items():
        cr, bl, br, typ = info[P]
        for b in bl:
            X, C = b['X'], b['cap']
            kx = A.idx[a][X]; kp = A.idx[a][P]
            j = kx if kx > kp else kx - 1
            if not (0 <= j < len(A.rows[a]) - 1):
                continue
            use = A.usage.get((a, j), [])
            if not use:
                continue
            # mutual pair: find V_s on C adjacent to X on the used side
            kc = A.idx[C][X]; rc = A.rows[C]
            for s in use:
                Vs = [rc[u] for u in (kc - 1, kc + 1) if 0 <= u < len(rc) and A.side(rc[u], a) == s]
                Q = Vs[0]
                if A.mult[Q] < 3:
                    bad.append(f'{tag} C15/LemmaA: V_s simple')
                    continue
                cq, blq, brq, typq = info[Q]
                has = any(bb['X'] == X and bb['cap'] == a for bb in blq)
                if not has:
                    bad.append(f'{tag} C15: Q lacks block at X capped by a_P')
                common = A.ev[P] & A.ev[Q]
                cons = any(abs(A.idx[m][P] - A.idx[m][Q]) == 1 for m in common)
                if not cons:
                    bad.append(f'{tag} C15: P,Q not consecutive')
                st[('C15 mutual partner type', typq, 'beta0', beta == 0)] += 1
                if typq == 'axis' and axis_of[Q] != C:
                    bad.append(f'{tag} C15: Q axis != C')
                if typq != 'axis' and beta == 0 and st['C15_ex'] < 2:
                    st['C15_ex'] += 1
                    bad.append(f'INFO C15 partner Q type {typq} (beta=0) {tag} tokens={" ".join(A.tokens)}')
    # ---------------- C15 parity on lines, as stated (beta = 0, m not cap, no axis on m, j even)
    if beta == 0:
        for m in range(A.n):
            tps = [e for e in A.rows[m] if A.mult[e] >= 3]
            if len(tps) < 2 or len(tps) % 2 or m in caps:
                continue
            if any(axis_of.get(P) == m for P in tps):
                continue
            touch = any(A.claims_at(m, e) for e in A.rows[m] if A.mult[e] == 2)
            allX = all(info[P][3] == 'axis' for P in tps)
            st[('C15par', 'allX', allX, 'touch', touch)] += 1
            if not touch:
                if allX:
                    bad.append(f'{tag} C15 parity FAIL with all type X')
                elif st['C15par_ex'] < 2:
                    st['C15par_ex'] += 1
                    bad.append(f'INFO C15 parity (stated hyps) fails: m={m} types={[info[P][3] for P in tps]} '
                               f'n={A.n} T={A.T} tokens={" ".join(A.tokens)}')


def worker(args):
    wid, N, seed, files = args
    rng = random.Random(seed * 7919 + wid)
    st = Counter(); bad = []
    toks_all = [(int(Path(f).parent.name.split('-')[0]), json.load(open(f))['gens'].split()) for f in files]
    for it in range(N):
        n, toks = rng.choice(toks_all)
        try:
            A = from_tokens(toks, n, complete=True)
            for _ in range(rng.choice([0, 0, 1, 2, 4, 8])):
                s = simple_tris(A)
                if s:
                    A = contract(A, rng.choice(s))
            for _ in range(rng.choice([0, 0, 1, 3])):
                s = simple_tris(A)
                if s:
                    A = flip(A, rng.choice(s))
        except (ValueError, AssertionError, IndexError):
            st['gen_error'] += 1; continue
        st['arr'] += 1
        try:
            check(A, st, bad, f'w{wid}i{it}')
        except (AssertionError, IndexError) as ex:
            bad.append(f'assert {ex!r}')
    return st, bad


def gal(f):
    n = int(Path(f).parent.name.split('-')[0])
    st = Counter(); bad = []
    if n % 2:
        return st, bad
    A = from_tokens(json.loads(Path(f).read_text())['gens'].split(), n)
    st['arr'] += 1
    check(A, st, bad, f)
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
    real = [b for b in bad if not b.startswith('INFO')]
    print('FAILS', len(real))
    for b in real[:20]:
        print('  ', b[:300])
    info = [b for b in bad if b.startswith('INFO')]
    print('INFO', len(info))
    for b in info[:6]:
        print('  ', b[:2500])

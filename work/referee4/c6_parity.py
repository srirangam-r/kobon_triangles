"""Referee4: test C6, the per-line parity rule.
Stated rule: a claim-free line (no hasBoth) has j + K odd, j = #triple points on it,
K = #cap roles (blocks at other triple points whose cap line is L).
We test two readings of "claim-free":
  weak   : kappa(L) = 0 (no unused segment touched at a simple crossing of L)
  strong : weak, and every bounded segment ending at a multiple point of L is used
and the corrected rule (strong, no triple point at an end of L):  j_alt + K odd,
where j_alt counts triple points on L whose t-pattern alternates (s,-s).
usage: python3 c6_parity.py gallery | mut N SEED sizes..."""
import json, random, sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee')
from arr import from_tokens  # noqa
from mutate import simple_tris, flip, contract  # noqa
GAL = Path('/home/nail/stuff/sundai_math/tools/external/kobon-solutions/gallery/data')


def line_data(A):
    n = A.n
    blocks = {}
    for P in A.triples:
        cr, bl = A.blocks(P)
        blocks[P] = (cr, bl)
    capcnt = Counter(b['cap'] for P in blocks for b in blocks[P][1])
    full_axis = {}
    for P, (cr, bl) in blocks.items():
        if len(bl) == 2 and (bl[0]['i'] - bl[1]['i']) % 6 == 3:
            full_axis[P] = bl[0]['ray'][0]
    out = []
    for L in range(n):
        r = A.rows[L]
        t = A.tseq(L)
        hasBoth = any(len(x) == 2 for x in t)
        simple = [A.mult[e] == 2 for e in r]
        weak_cf = not any(A.claims_at(L, e) for e, s in zip(r, simple) if s)
        mults = [i for i, s in enumerate(simple) if not s]
        # strong: all bounded segments at L's multiple points used
        strong_cf = weak_cf
        for i in mults:
            Y = r[i]
            for M in A.ev[Y]:
                k = A.idx[M][Y]
                for j in (k - 1, k):
                    if 0 <= j < len(A.rows[M]) - 1 and not A.usage.get((M, j)):
                        strong_cf = False
        pats = []
        for i in mults:
            Y = r[i]
            if i == 0 or i == len(r) - 1:
                pats.append('end'); continue
            a, b = t[i], t[i + 1]  # segments l_{i-1}, l_i around X_{i+1}=r[i] in 1-based
            if len(a) == 2 or len(b) == 2:
                pats.append('both')
            elif not a or not b:
                pats.append('zero')
            elif a == b:
                pats.append('same')
            else:
                pats.append('alt')
        # repeats at simple crossings
        rep = 0
        for i, s in enumerate(simple):
            if not s or i == 0 or i == len(r) - 1:
                continue
            a, b = t[i], t[i + 1]
            if len(a) == 1 and a == b:
                rep += 1
        j = len(mults)
        K = capcnt.get(L, 0)
        fullnonaxis = [r[i] for i in mults if r[i] in full_axis and full_axis[r[i]] != L]
        out.append(dict(L=L, j=j, K=K, hasBoth=hasBoth, weak=weak_cf, strong=strong_cf, pats=pats,
                        rep=rep, maxmult=max([A.mult[r[i]] for i in mults], default=2),
                        fullnonaxis=len(fullnonaxis)))
    return out


def check(A, st, bad, tag):
    if A.n % 2:
        return
    if any(m > 3 for m in A.mult):
        st['skip4'] += 1
        return
    st['arr'] += 1
    for d in line_data(A):
        st['lines'] += 1
        j, K = d['j'], d['K']
        if not d['hasBoth'] and d['rep'] != K:
            bad.append(f"{tag} REP!=K L={d['L']} rep={d['rep']} K={K}")
        if d['hasBoth']:
            st['line_hasBoth'] += 1
            continue
        pc = Counter(d['pats'])
        key = (j, K, 'end' if pc['end'] else '', 'zero' if pc['zero'] else '')
        if d['weak']:
            st['weak_cf'] += 1
            if (j + K) % 2 == 0:
                st['WEAK_stated_viol'] += 1
                st[('WEAK_viol', j, K, tuple(sorted(d['pats'])))] += 1
        if d['strong']:
            st['strong_cf'] += 1
            st[('strong_cf', j, K, tuple(sorted(d['pats'])))] += 1
            if (j + K) % 2 == 0:
                st['STRONG_stated_viol'] += 1
                st[('STRONG_viol', j, K, tuple(sorted(d['pats'])))] += 1
                if len(bad) < 400:
                    bad.append(f"STRONGVIOL {tag} L={d['L']} j={j} K={K} pats={d['pats']} n={A.n} tokens={' '.join(A.tokens)}")
            if not pc['end']:
                assert not pc['zero'] and not pc['both']
                if (pc['alt'] + K) % 2 == 0:
                    bad.append(f"{tag} CORRECTED RULE FAIL L={d['L']} j={j} K={K} pats={d['pats']}")
        # consequences
        if j == 0 and K == 2 and not d['weak']:
            st['cons1_ok'] += 1
        if j == 0 and K == 2 and d['weak']:
            bad.append(f"{tag} CONS1 FAIL (non-triple, 2 caps, no claim) L={d['L']}")
        if j == 1 and d['fullnonaxis'] == 1 and K == 1:
            st['cons2_cases'] += 1
            if d['weak']:
                st['cons2_weak_noclaim'] += 1
                if d['strong']:
                    bad.append(f"{tag} CONS2 FAIL strong L={d['L']} pats={d['pats']} tokens={' '.join(A.tokens)}")
                else:
                    st['cons2_noclaim_but_Ztr'] += 1


def gal(f):
    n = int(Path(f).parent.name.split('-')[0])
    st = Counter(); bad = []
    if n % 2:
        return st, bad
    A = from_tokens(json.loads(Path(f).read_text())['gens'].split(), n)
    try:
        check(A, st, bad, f)
    except AssertionError as ex:
        bad.append(f'assert {f} {ex!r}')
    return st, bad


def mut_worker(args):
    wid, N, seed, files = args
    rng = random.Random(seed * 7919 + wid)
    st = Counter(); bad = []
    toks_all = [(int(Path(f).parent.name.split('-')[0]), json.load(open(f))['gens'].split()) for f in files]
    for it in range(N):
        n, toks = rng.choice(toks_all)
        try:
            new = []
            keep = rng.random()
            for t in toks:
                if t.endswith('*') and rng.random() > keep:
                    g = int(t[:-1])
                    new += [str(g), str(g + 1), str(g)] if rng.random() < 0.5 else [str(g + 1), str(g), str(g + 1)]
                else:
                    new.append(t)
            A = from_tokens(new, n, complete=True)
            for _ in range(rng.choice([0, 0, 1, 2, 3, 5])):
                s = simple_tris(A)
                if s:
                    A = contract(A, rng.choice(s))
            for _ in range(rng.choice([0, 0, 1, 2, 4, 8])):
                s = simple_tris(A)
                if s:
                    A = flip(A, rng.choice(s))
        except (ValueError, AssertionError, IndexError):
            st['gen_error'] += 1; continue
        try:
            check(A, st, bad, f'w{wid}i{it}')
        except AssertionError as ex:
            bad.append(f'assert {ex!r} ' + ' '.join(A.tokens))
    return st, bad


if __name__ == '__main__':
    mode = sys.argv[1]
    st = Counter(); bad = []
    if mode == 'gallery':
        files = [str(f) for d in sorted(GAL.iterdir()) if d.is_dir() for f in sorted(d.glob('*.json'))]
        with Pool(4) as pool:
            for s, b in pool.imap_unordered(gal, files, chunksize=8):
                st.update(s); bad += b
    else:
        N, seed = int(sys.argv[2]), int(sys.argv[3]); sizes = sys.argv[4:]
        files = [str(f) for s in sizes for f in sorted((GAL / s).glob('*.json'))]
        with Pool(4) as pool:
            for s, b in pool.imap_unordered(mut_worker, [(w, N, seed, files) for w in range(4)]):
                st.update(s); bad += b
    for k in sorted(st, key=str):
        print(st[k], k)
    fails = [b for b in bad if not b.startswith('STRONGVIOL')]
    viol = [b for b in bad if b.startswith('STRONGVIOL')]
    print('FAILS', len(fails))
    for b in fails[:20]:
        print('  ', b[:400])
    print('STRONG VIOLATION EXAMPLES', len(viol))
    for b in viol[:5]:
        print('  ', b[:3000])

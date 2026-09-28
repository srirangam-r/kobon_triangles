"""Referee4: C52 rich 4-fold points on random sweeps (c51_test generator).
Per 4-fold point: sectors t_i, rays in order a+..d-, doubly used rays, middles (simple far end) with caps,
bridges; checks: rich <=> t>=7 or (t=6 with opposite gaps); middles in runs <= 2 sharing caps; D,e bounds
(t=8: D<=5; t=7: D<=4; t=6: D<=4 with D=4 => e=0); m' = h + x - e/2 >= 0.5 for rich points."""
import random, sys
from collections import Counter
from multiprocessing import Pool
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee4'); sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee')
from c51_test import build, random_sweep, sector_counts, gaining

def check(A, P, st, bad):
    lines = sorted(A.ev[P])
    rays = []
    for k, L in enumerate(lines):
        i = A.idx[L][P]
        rays.append((L, i - 1))    # left ray: previous vertex
    for k, L in enumerate(lines):
        rays.append((L, A.idx[L][P] + 1))
    t = sector_counts(A, P); tt = sum(t)
    rich = all(sum(t[s] for s in G) >= 3 and sum(t[s] for s in set(range(8)) - G) >= 3 for G in (gaining(j) for j in range(4)))
    st[('t', tt, 'rich', rich)] += 1
    if not rich: return
    if tt < 6: bad.append('rich with t<6')
    info = []
    for r, (L, j) in enumerate(rays):
        row = A.rows[L]
        if not (0 <= j < len(row)):
            info.append(('ray', None)); continue
        far = row[j]
        seg = (L, min(j, A.idx[L][P]))
        dbl = len(A.usage.get(seg, ())) == 2
        if not dbl: info.append(('-', None)); continue
        if A.mult[far] == 2:
            (C,) = tuple(A.ev[far] - {L}); info.append(('M', C))
        else:
            info.append(('B', far))
    D = sum(1 for x in info if x[0] == 'M'); e = sum(1 for x in info if x[0] == 'B')
    # adjacent middles share a cap; runs <= 2
    for r in range(8):
        if info[r][0] == 'M' and info[(r + 1) % 8][0] == 'M' and info[r][1] != info[(r + 1) % 8][1]:
            bad.append('adjacent middles with different caps')
        if all(info[(r + s) % 8][0] == 'M' for s in range(3)): bad.append('run of 3 middles')
    caps = {x[1] for x in info if x[0] == 'M'}
    xP = sum(1 for C in caps if any(A.mult[v] >= 3 for v in A.rows[C]))
    h = 12 - 2 * D - len(caps)
    mp = h + xP - e / 2
    st[('rich t', tt, 'D', D, 'e', e)] += 1
    if tt == 8 and D > 5: bad.append('t8 D>5')
    if tt == 7 and D > 4: bad.append('t7 D>4')
    if tt == 6 and (D > 4 or (D == 4 and e > 0)): bad.append('t6 bound')
    if mp < 0.5: bad.append(f"m' < 0.5 (t={tt} D={D} e={e} caps={len(caps)} x={xP})")
    st['min m\' rich'] = min(st.get("min m' rich", 99), mp)

def worker(args):
    wid, N = args
    rng = random.Random(777 + wid); st = Counter(); bad = []
    for it in range(N):
        n = rng.choice([8, 9, 10, 11, 12])
        toks = random_sweep(n, rng, p4=0.2, p3=0.2)
        try: A = build(toks, n)
        except (AssertionError, ValueError): continue
        st['arr'] += 1
        for P, (g, w) in enumerate(toks):
            if w == 4: check(A, P, st, bad)
    return st, bad

if __name__ == '__main__':
    st = Counter(); bad = []
    with Pool(4) as pool:
        for s, b in pool.imap_unordered(worker, [(w, int(sys.argv[1])) for w in range(4)]):
            for k, v in s.items():
                if isinstance(k, str) and k.startswith('min'): st[k] = min(st.get(k, 99), v)
                else: st[k] += v
            bad += b
    for k in sorted(st, key=str): print(st[k], k)
    print('FAILS', len(bad), Counter(bad).most_common(5))

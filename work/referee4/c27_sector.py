"""Referee4: C27 sector lemma on pseudoline arrangements.  Ends: line L has left end at cyclic
position L and right end at L+n (order 0L..(n-1)L,0R..(n-1)R).  For each simple X = a^a' and each
of the 4 sectors, (#ends strictly inside the sector arc) == (#lines crossing the two rays exactly once)."""
import json, random, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee')
from arr import from_tokens
from mutate import simple_tris, contract, flip
GAL = Path('/home/nail/stuff/sundai_math/tools/external/kobon-solutions/gallery/data')
rng = random.Random(4); st = Counter(); bad = 0
files = [f for s in ('10', '14', '18', '18-1', '20') for f in sorted((GAL / s).glob('*.json'))]
for it in range(600):
    f = rng.choice(files); n = int(f.parent.name.split('-')[0])
    A = from_tokens(json.load(open(f))['gens'].split(), n)
    for _ in range(rng.choice([0, 3, 8])):
        s = simple_tris(A)
        if s: A = contract(A, rng.choice(s))
    for _ in range(rng.choice([0, 5, 20])):
        s = simple_tris(A)
        if s: A = flip(A, rng.choice(s))
    N = 2 * n
    for X in range(len(A.ev)):
        if A.mult[X] != 2: continue
        a, b = sorted(A.ev[X])
        for da in (-1, 1):
            for db in (-1, 1):
                pa = a if da == -1 else a + n
                pb = b if db == -1 else b + n
                qa, qb = (pa + n) % N, (pb + n) % N
                # arc from pa to pb (either direction) not containing qa, qb
                def arc(u, v):
                    out = []; p = (u + 1) % N
                    while p != v: out.append(p); p = (p + 1) % N
                    return out
                A1 = arc(pa, pb)
                inside = A1 if (qa not in A1 and qb not in A1) else arc(pb, pa)
                assert qa not in inside and qb not in inside
                ends_inside = len(inside)
                def on_ray(L, line, d):
                    e = A.pe(L, line); k = A.idx[line][e] - A.idx[line][X]
                    return k * d > 0
                cnt = 0
                for L in range(n):
                    if L in (a, b): continue
                    c = on_ray(L, a, da) + on_ray(L, b, db)
                    cnt += c == 1
                st['sectors'] += 1
                if cnt != ends_inside: bad += 1
print(dict(st), 'FAILS', bad)

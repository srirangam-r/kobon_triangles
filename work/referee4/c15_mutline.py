"""Referee4, C15: parity on a *mutual* line with the stated hypotheses only (beta=0, m not a cap,
no axis on m, j(m) even, m carries a mutual pair).  Look for lines without a touch."""
import json, random, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee'); sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee4')
from arr import from_tokens
from mutate import simple_tris, contract
from c7_lemmaC import point_info
GAL = Path('/home/nail/stuff/sundai_math/tools/external/kobon-solutions/gallery/data')
st = Counter(); shown = 0
rng = random.Random(2)
files = [f for d in sorted(GAL.iterdir()) if d.is_dir() and int(d.name.split('-')[0]) % 2 == 0 for f in sorted(d.glob('*.json'))]
for it in range(12000):
    f = files[it] if it < len(files) else rng.choice(files)
    n = int(f.parent.name.split('-')[0])
    try:
        A = from_tokens(json.load(open(f))['gens'].split(), n)
        if it >= len(files):
            for _ in range(rng.choice([1, 2, 4])):
                s = simple_tris(A)
                if s: A = contract(A, rng.choice(s))
    except (ValueError, AssertionError, IndexError):
        continue
    if any(m > 3 for m in A.mult): continue
    beta = sum(1 for (L, j), s in A.usage.items() if len(s) == 2 and A.mult[A.rows[L][j]] >= 3 and A.mult[A.rows[L][j + 1]] >= 3)
    if beta: continue
    info = {P: point_info(A, P) for P in A.triples}
    caps = set(b['cap'] for P in info for b in info[P][1])
    axis_of = {P: info[P][1][0]['ray'][0] for P in info if info[P][3] == 'axis'}
    mutual_lines = set()
    for P, a in axis_of.items():
        for b in info[P][1]:
            X, C = b['X'], b['cap']
            kx, kp = A.idx[a][X], A.idx[a][P]
            j = kx if kx > kp else kx - 1
            if 0 <= j < len(A.rows[a]) - 1 and A.usage.get((a, j)):
                kc = A.idx[C][X]; rc = A.rows[C]
                for s in A.usage[(a, j)]:
                    Q = [rc[u] for u in (kc - 1, kc + 1) if 0 <= u < len(rc) and A.side(rc[u], a) == s][0]
                    for m in A.ev[P] & A.ev[Q]:
                        mutual_lines.add(m)
    for m in mutual_lines:
        tps = [e for e in A.rows[m] if A.mult[e] >= 3]
        if len(tps) % 2 or m in caps or any(axis_of.get(P) == m for P in tps): continue
        touch = any(A.claims_at(m, e) for e in A.rows[m] if A.mult[e] == 2)
        allX = all(info[P][3] == 'axis' for P in tps)
        st[(n, 'allX', allX, 'touch', touch)] += 1
        if not touch and not allX and n == 18 and shown < 2:
            shown += 1
            print('n=18 mutual line without touch:', f.name, 'contracted' if it >= len(files) else 'gallery', 'T', A.T,
                  'm', m, 'types', [info[P][3] for P in tps], 'tokens', ' '.join(A.tokens))
for k, v in sorted(st.items()): print(v, k)

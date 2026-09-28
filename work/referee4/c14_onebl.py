"""Referee4, C14: a 1-block triple point R with no bridge end has an unused (or unbounded)
first segment on ray r2 or r4 (r0 = block middle).  Gallery + mutations."""
import json, random, sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee'); sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee4')
from arr import from_tokens
from mutate import simple_tris, flip, contract
from c7_lemmaC import point_info
GAL = Path('/home/nail/stuff/sundai_math/tools/external/kobon-solutions/gallery/data')
def check(A, st, bad):
    if any(m > 3 for m in A.mult): return
    for P in A.triples:
        cr, bl, br, typ = point_info(A, P)
        if typ != 'b1' or br: continue
        i = bl[0]['i']
        st['b1_nobridge'] += 1
        segs = [cr[(i + d) % 6][2] for d in (2, 4)]
        if all(s is not None and A.usage.get(s) for s in segs):
            bad.append('FAIL')
        for d in (1, 5):
            # sectors (r1,r2),(r4,r5) no triangle <=> r1/r5 first segments singly used
            s = cr[(i + d) % 6][2]
            if s is not None and len(A.usage.get(s, ())) == 2: bad.append('FAIL r1/r5 doubly used')
def worker(args):
    wid, N, files = args
    rng = random.Random(wid); st = Counter(); bad = []
    for it in range(N):
        f = rng.choice(files); n = int(Path(f).parent.name.split('-')[0])
        try:
            A = from_tokens(json.load(open(f))['gens'].split(), n)
            for _ in range(rng.choice([0, 2, 5, 10])):
                s = simple_tris(A)
                if s: A = contract(A, rng.choice(s))
        except (ValueError, AssertionError, IndexError):
            continue
        st['arr'] += 1; check(A, st, bad)
    return st, bad
files = [str(f) for s in ('18', '18-1', '16', '20') for f in sorted((GAL / s).glob('*.json'))]
st = Counter(); bad = []
with Pool(4) as pool:
    for s, b in pool.imap_unordered(worker, [(w, 1500, files) for w in range(4)]):
        st.update(s); bad += b
print(dict(st), 'FAILS', len(bad))

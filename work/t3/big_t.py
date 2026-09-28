import glob, sys, collections
sys.path.insert(0, '.')
from arr import *
from lemmas import point_info
R = '../../tools/external/kobon-solutions/gallery/data'
c = collections.Counter()
for s in sys.argv[1:]:
    for f in sorted(glob.glob(f'{R}/{s}/*.json')):
        a = load(f)
        if any(len(e) > 3 for e in a.events): continue
        t = len(a.triples)
        if t < 5: continue
        B = sum(len(blocks(a, P)) for P in a.triples)
        beta = a.D() - B
        per = collections.Counter()
        for P in a.triples:
            I = point_info(a, P)
            e = 0
            for r in I['rays']:
                fs = first_seg(a, P, r)
                if fs and len(a.t[fs[0]][fs[1]]) == 2 and len(a.events[far_end(a, P, r)]) == 3: e += 1
            per[(I['kind'], e)] += 1
        c[(a.n, t, a.T(), 'B', B, 'beta', beta, 'Z', a.Z())] += 1
for k, v in sorted(c.items()): print(v, k)

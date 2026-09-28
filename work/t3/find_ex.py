import glob, sys, collections
sys.path.insert(0, '.')
from arr import *
from gstats import ptype
R = '../../tools/external/kobon-solutions/gallery/data'
want_k = int(sys.argv[1]); want = eval(sys.argv[2])
for series in sys.argv[3:]:
    for f in sorted(glob.glob(f'{R}/{series}/*.json')):
        a = load(f)
        if len(a.triples) != want_k: continue
        lines = collections.Counter(L for P in a.triples for L in a.events[P])
        mult = tuple(sorted((v for v in lines.values() if v > 1), reverse=True))
        types = tuple(sorted(ptype(a, P) for P in a.triples))
        br = 0
        for L, v in lines.items():
            if v > 1:
                ps = sorted(a.pos[L][P] for P in a.triples if L in a.events[P])
                br += sum(1 for x, y in zip(ps, ps[1:]) if y == x + 1)
        if (mult, br, types) == want:
            print(f, a.n); 

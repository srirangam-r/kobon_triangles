import glob, sys, collections
sys.path.insert(0, '.')
from arr import *
from lemmas import point_info
R = '../../tools/external/kobon-solutions/gallery/data'
stats = collections.Counter()
for series in sys.argv[1:]:
    for f in sorted(glob.glob(f'{R}/{series}/*.json')):
        a = load(f)
        if any(len(ev) > 3 for ev in a.events): continue
        T = a.triples
        info = {P: point_info(a, P) for P in T}
        for P in T:
            I = info[P]
            if I['kind'] != 'X': continue
            # doubly used bridges at P
            for k, r in enumerate(I['rays']):
                fs = first_seg(a, P, r)
                if fs is None: continue
                L, e = fs
                Q = far_end(a, P, r)
                if len(a.events[Q]) == 3 and len(a.t[L][e]) == 2:
                    # expect: adjacent non-cap sector triangle P Q R with R triple
                    tri = [t for t in a.tris if P in [a.rows[x][ee] for x, ee, _ in t] or True]
                    # find triangle faces with vertices P, Q, and a third triple point
                    found = False
                    for t in a.tris:
                        verts = set()
                        for x, ee, _ in t:
                            verts |= {a.rows[x][ee], a.rows[x][ee + 1]}
                        if P in verts and Q in verts and all(len(a.events[v]) == 3 for v in verts):
                            found = True
                    stats['X-bridge doubly used, PQR face found' if found else 'X-bridge FAIL'] += 1
                    caps = [c for _, c in I['blocks']]
                    trip_lines = set().union(*[a.events[x] for x in T])
                    stats['caps triple: %d' % sum(c in trip_lines for c in caps)] += 1
print(dict(stats))

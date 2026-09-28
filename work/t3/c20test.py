"""C20 test.  (a) 1-block point, block middle r0, no doubly used bridge on r1, r3, r5:
some first segment among r2, r3, r4 is unused or a ray.
(b) bent point (middles 1,3, shared 2), V0 and V4 simple: first segment of ray 5 unused or a ray.
(c) C19: bent P->Q with another doubly used bridge [P,R]: Q and R not consecutive on any line."""
import glob, sys, json, collections, random
sys.path.insert(0, '.')
from arr import *
from lemmas import point_info
from mutate import random_move
R_ = '../../tools/external/kobon-solutions/gallery/data'
st = collections.Counter()
def dbl_bridge(a, P, r):
    fs = first_seg(a, P, r)
    return fs is not None and len(a.t[fs[0]][fs[1]]) == 2 and len(a.events[far_end(a, P, r)]) >= 3
def unused_or_ray(a, P, r):
    fs = first_seg(a, P, r)
    return fs is None or not a.t[fs[0]][fs[1]]
def test(a):
    for P in a.triples:
        I = point_info(a, P); rs = I['rays']
        if len(I['blocks']) == 1:
            k0 = I['blocks'][0][0]
            r = lambda i: rs[(k0 + i) % 6]
            if not any(dbl_bridge(a, P, r(i)) for i in (1, 3, 5)):
                st['C20a ok' if any(unused_or_ray(a, P, r(i)) for i in (2, 3, 4)) else 'C20a FAIL'] += 1
        if I['kind'] == 'V':
            (k1, _), (k2, _) = I['blocks']
            sh = [j for j in range(6) if (j - k1) % 6 in (1, 5) and (j - k2) % 6 in (1, 5)][0]
            r = lambda i: rs[(sh + i) % 6]   # r(0) = shared ray toward Q; middles r(1), r(-1)
            V0, V4 = far_end(a, P, r(2)), far_end(a, P, r(-2))
            if V0 is not None and V4 is not None and len(a.events[V0]) == 2 and len(a.events[V4]) == 2:
                st['C20b ok' if unused_or_ray(a, P, r(3)) else 'C20b FAIL'] += 1
            Q = far_end(a, P, r(0))
            for i in range(6):
                if i == 0: continue
                if dbl_bridge(a, P, r(i)):
                    Rr = far_end(a, P, r(i))
                    cons = any(abs(a.pos[L][Q] - a.pos[L][Rr]) == 1 for L in a.events[Q] & a.events[Rr])
                    st['C19 FAIL' if cons else 'C19 ok'] += 1
for s in sys.argv[1:]:
    for f in sorted(glob.glob(f'{R_}/{s}/*.json')):
        a = Arr(json.load(open(f))['gens'])
        if any(len(e) > 3 for e in a.events): continue
        test(a)
        rng = random.Random(hash(f) & 0xffff)
        for it in range(12):
            w = random_move(a, rng, 0.55, 0.05)
            if w is None: continue
            b = Arr(w, a.n)
            if any(len(e) > 3 for e in b.events): continue
            a = b; test(a)
print(dict(st))

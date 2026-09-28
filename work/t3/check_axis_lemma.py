"""Empirical check of the cap-adjacent zero lemma on gallery arrangements."""
import glob, sys, collections
sys.path.insert(0, '.')
from arr import *

R = '../../tools/external/kobon-solutions/gallery/data'
stats = collections.Counter()
for series in sys.argv[1:]:
    for f in sorted(glob.glob(f'{R}/{series}/*.json')):
        a = load(f)
        for P in a.triples:
            bl = blocks(a, P)
            stats['blocks%d' % len(bl)] += 1
            if len(bl) == 2:
                (k1, c1), (k2, c2) = bl
                rs = rays(a, P)
                if (k1 - k2) % 6 != 3:
                    stats['bent'] += 1
                    continue
                ax = rs[k1][0]
                p = a.pos[ax][P]
                # apexes: first vertices of the 4 side rays
                apex_simple = all(a.is_simple(far_end(a, P, rs[j])) for j in range(6) if j not in (k1, k2) and far_end(a, P, rs[j]) is not None)
                t = a.t[ax]
                for d in (+1, -1):
                    e = p + 1 if d == +1 else p - 2
                    if 0 <= e < len(t):
                        key = ('apex_simple' if apex_simple else 'apex_triple', 'zero' if not t[e] else 'nonzero')
                        stats[key] += 1
                    else:
                        stats['ray'] += 1
print(dict(stats))

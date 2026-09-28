import glob, sys, collections
sys.path.insert(0, '.')
from arr import *
R = '../../tools/external/kobon-solutions/gallery/data'

def config(a):
    T = a.triples
    lines = [a.events[P] for P in T]
    shared = []
    for i in range(len(T)):
        for j in range(i + 1, len(T)):
            s = lines[i] & lines[j]
            if s:
                shared.append((i, j, next(iter(s))))
    return shared

if __name__ == '__main__':
    cnt = collections.Counter()
    ex = {}
    for series in sys.argv[1:]:
        for f in sorted(glob.glob(f'{R}/{series}/*.json')):
            a = load(f)
            if len(a.triples) != 3:
                continue
            sh = config(a)
            ls = collections.Counter(l for _, _, l in sh)
            if len(sh) == 0: c = 'disjoint'
            elif len(sh) == 1: c = 'one'
            elif len(sh) == 2: c = 'path'
            elif len(ls) == 1: c = 'collinear'
            else: c = 'triangle'
            # consecutive?
            cons = 0
            for i, j, m in sh:
                P, Q = a.triples[i], a.triples[j]
                if abs(a.pos[m][P] - a.pos[m][Q]) == 1: cons += 1
            cnt[(c, cons, a.Z(), a.D())] += 1
            ex.setdefault((c, cons), f)
    for k, v in sorted(cnt.items()): print(k, v)
    for k, v in ex.items(): print(k, v)

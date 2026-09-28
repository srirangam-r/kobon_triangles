import sys, collections
sys.path.insert(0, '.')
from arr import *

def tseq(a, L):
    out = []
    for i, eid in enumerate(a.rows[L]):
        v = 'P' if len(a.events[eid]) == 3 else '.'
        out.append(v)
        if i < len(a.t[L]):
            s = a.t[L][i]
            out.append('0' if not s else ('B' if len(s) == 2 else ('+' if +1 in s else '-')))
    return ''.join(out)

def describe(a):
    trip_lines = set().union(*[a.events[P] for P in a.triples]) if a.triples else set()
    print('T', a.T(), 'Z', a.Z(), 'D', a.D())
    caps = collections.defaultdict(list)
    axes = {}
    for P in a.triples:
        bl = blocks(a, P)
        rs = rays(a, P)
        info = [(rs[k], c) for k, c in bl]
        ax = None
        if len(bl) == 2 and (bl[0][0] - bl[1][0]) % 6 == 3:
            ax = rs[bl[0][0]][0]
            axes[P] = ax
        for k, c in bl:
            caps[c].append(P)
        print('P', P, sorted(a.events[P]), 'blocks', info, 'axis', ax)
    for L in range(a.n):
        kind = []
        if L in trip_lines: kind.append('trip')
        if L in caps: kind.append('cap' + str(caps[L]))
        if L in axes.values(): kind.append('axis')
        if not kind: kind.append('clean')
        tl = collections.Counter(tch for _, _, tch in touches(a))
        print(f'{L:2d} {tseq(a, L):40s} {",".join(kind):20s} touches={tl.get(L,0)}')
    for u, X, w in touches(a):
        print('  unused', u, 'endpoint', X, 'touched by', w)

if __name__ == '__main__':
    describe(load(sys.argv[1]))

"""C35 test: splitting a triple point P into a small triangle gives T+1-t_even or T+1-t_odd
(the two split directions), where t_even/t_odd count triangles in the sectors
{s0,s2,s4} / {s1,s3,s5}, s_i = (r_i, r_{i+1}) with rays from arr.rays()."""
import glob, sys, json, collections, random
sys.path.insert(0, '.')
from arr import *
from mutate import expand, random_move
R_ = '../../tools/external/kobon-solutions/gallery/data'
st = collections.Counter()

def sector_tris(a, P):
    rs = rays(a, P)
    # triangle faces with vertex P: find, for each triangle, its two edges at P
    cls = [0, 0]
    for f in a.tris:
        edges_at_P = []
        for (x, e, side) in f:
            if a.rows[x][e] == P or a.rows[x][e + 1] == P:
                d = +1 if a.rows[x][e] == P else -1
                edges_at_P.append((x, d))
        if len(edges_at_P) != 2:
            continue
        i, j = sorted(rs.index(r) for r in edges_at_P)
        if j - i == 1: s = i
        elif (i, j) == (0, 5): s = 5
        else:
            st['non-adjacent?'] += 1; continue
        cls[s % 2] += 1
    return cls

def test(a):
    T = a.T()
    for P in a.triples:
        ce, co = sector_tris(a, P)
        got = set()
        for o in (0, 1):
            w = expand(a, P, o)
            if w is None: continue
            got.add(Arr(w, a.n).T())
        pred = {T + 1 - ce, T + 1 - co}
        st['ok' if got == pred else 'FAIL'] += 1
        st[('min', min(ce, co))] += 1

for s in sys.argv[1:]:
    for f in sorted(glob.glob(f'{R_}/{s}/*.json'))[:150]:
        a = Arr(json.load(open(f))['gens'])
        if any(len(e) > 3 for e in a.events): continue
        test(a)
        rng = random.Random(1)
        for it in range(3):
            w = random_move(a, rng, 0.5, 0.1)
            if w: a = Arr(w, a.n); test(a)
print(dict(st))

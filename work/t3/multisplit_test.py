"""C38 test: splitting a set S of triple points sequentially (each via expand with a chosen
orientation) gives T + |S| - |union of chosen-class triangles| (classes w.r.t. the original arrangement)."""
import glob, sys, json, random, collections
sys.path.insert(0, '.')
from arr import *
from mutate import expand, random_move
from split_test import sector_tris
R_ = '../../tools/external/kobon-solutions/gallery/data'
st = collections.Counter()

def class_sets(a, P):
    rs = rays(a, P)
    cls = [set(), set()]
    for idx, f in enumerate(a.tris):
        at = [(x, +1 if a.rows[x][e] == P else -1) for (x, e, _) in f if P in (a.rows[x][e], a.rows[x][e + 1])]
        if len(at) != 2: continue
        i, j = sorted(rs.index(r) for r in at)
        s = i if j - i == 1 else 5
        cls[s % 2].add(frozenset(x for x, _, _ in f))
    return cls

def which_class(a, P, o):
    """class (0 even / 1 odd) destroyed by expand(a,P,o): compare T drop."""
    ce, co = [len(c) for c in class_sets(a, P)]
    w = expand(a, P, o); b = Arr(w, a.n)
    d = a.T() + 1 - b.T()
    return (0 if d == ce else 1) if ce != co else None, b

rng = random.Random(3)
for s in sys.argv[1:]:
    for f in sorted(glob.glob(f'{R_}/{s}/*.json'))[:120]:
        a0 = Arr(json.load(open(f))['gens'])
        if any(len(e) > 3 for e in a0.events) or len(a0.triples) < 2: continue
        for trial in range(4):
            S = rng.sample(a0.triples, min(len(a0.triples), rng.choice([2, 3])))
            # original classes and triangles as line-triples
            orig = {P: class_sets(a0, P) for P in S}
            lines_of = {P: a0.events[P] for P in S}
            a = a0; chosen = {}
            ok = True
            for P in S:
                # locate P in current arrangement by its lines
                cur = [Q for Q in a.triples if a.events[Q] == lines_of[P]]
                if not cur: ok = False; break
                Pc = cur[0]
                o = rng.randrange(2)
                # determine which class (in the current arrangement's labelling) this orientation hits,
                # by matching the destroyed triangles
                before_tris = {frozenset(x for x, _, _ in fc) for fc in a.tris}
                w = expand(a, Pc, o)
                if w is None: ok = False; break
                b = Arr(w, a.n)
                after = {frozenset(x for x, _, _ in fc) for fc in b.tris}
                lost = before_tris - after
                # chosen class in ORIGINAL terms: the one whose triangles (still present) were lost
                c0, c1 = orig[P]
                if lost & c0 and not lost & c1: chosen[P] = 0
                elif lost & c1 and not lost & c0: chosen[P] = 1
                elif not lost: chosen[P] = 0 if not (c0 & before_tris) else 1
                else: ok = False; break
                a = b
            if not ok: st['skip'] += 1; continue
            U = set().union(*[orig[P][chosen[P]] for P in S])
            pred = a0.T() + len(S) - len(U)
            st['ok' if pred == a.T() else 'FAIL'] += 1
print(dict(st))

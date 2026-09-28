"""Test Lemma D (parity through triple points): n even, L not a cap line (no doubly used piece
adjacent to L at a simple crossing), every entry adjacent to a triple point on L is a single
nonzero sign (rays count as zero), j = #triple points on L, q = #triple points where the two
adjacent entries have the same sign.  If j + q is even then kappa(L) >= 1.
Also tests the SAT clause of Lemma A (C10)."""
import glob, sys, collections, json, random
sys.path.insert(0, '.')
from arr import *
from lemmas import kappa
from mutate import random_move
R = '../../tools/external/kobon-solutions/gallery/data'
st = collections.Counter()

def is_cap_somewhere(a, L):
    # doubly used piece adjacent to L at a simple crossing
    for i, X in enumerate(a.rows[L]):
        if not a.is_simple(X): continue
        Rr = a.other(X, L)
        j = a.pos[Rr][X]
        for e in (j - 1, j):
            if 0 <= e < len(a.t[Rr]) and len(a.t[Rr][e]) == 2:
                return True
    return False

def testD(a):
    if a.n % 2: return
    kap, _ = kappa(a)
    for L in range(a.n):
        trips = [i for i, X in enumerate(a.rows[L]) if len(a.events[X]) == 3]
        if not trips: continue
        if any(len(a.events[X]) > 3 for X in a.rows[L]): continue
        if is_cap_somewhere(a, L): continue
        ok = True; q = 0
        for i in trips:
            ent = []
            for e in (i - 1, i):
                s = a.t[L][e] if 0 <= e < len(a.t[L]) else set()
                if len(s) != 1: ok = False
                ent.append(next(iter(s)) if len(s) == 1 else None)
            if ok and ent[0] == ent[1]: q += 1
        if not ok: continue
        j = len(trips)
        if (j + q) % 2 == 0:
            st['D applies, claims' if kap[L] >= 1 else 'D FAIL'] += 1
        else:
            st['D parity odd'] += 1

def testA(a):
    # clause: z(abc) & tri(abC) & tri(acC) & tri(aCN) -> z(bCN) or z(cCN)
    tris = {frozenset(x for x, _, _ in f) for f in a.tris}
    trip = [a.events[P] for P in a.triples]
    conc = set(frozenset(t) for t in trip)
    def z(*l): return frozenset(l) in conc
    for P in trip:
        for aa in P:
            b, c = sorted(P - {aa})
            for C in range(a.n):
                if C in P: continue
                if frozenset((aa, b, C)) in tris and frozenset((aa, c, C)) in tris:
                    for N in range(a.n):
                        if N in P or N == C: continue
                        if frozenset((aa, C, N)) in tris:
                            st['A clause ok' if (z(b, C, N) or z(c, C, N)) else 'A clause FAIL'] += 1

for s in sys.argv[1:]:
    for f in sorted(glob.glob(f'{R}/{s}/*.json')):
        a = Arr(json.load(open(f))['gens'])
        testD(a); testA(a)
        rng = random.Random(hash(f) & 0xffff)
        for it in range(8):
            w = random_move(a, rng, 0.4, 0.15)
            if w is None: continue
            b = Arr(w, a.n)
            if any(len(e) > 3 for e in b.events) or b.T() < a.T() - 3: continue
            a = b; testD(a); testA(a)
print(dict(st))

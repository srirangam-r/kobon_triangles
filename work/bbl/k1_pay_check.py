#!/usr/bin/env python3
"""Lead's K_1 payment lemma (THEORY §27 notes): every kite with exactly one quadruple corner is paid 2 units,
either by the two endpoint N tokens of a singly used cap edge (case A) or by 2 units of S_P at its quadruple
corner P (case B, all four cap edges doubly used). Checks: tokens are N rays on singly used segments, never
claimed by sol's §4 payments, never reused; in case B the rays of P at distance 2 from the kite block are not
blocks; S_P >= 2 * (#case-B kites at P). Then 2 Lambda = sum of nonnegative credits (exact)."""
import sys, json
from collections import Counter, defaultdict
sys.path[:0] = ["work/bbl", "work/t3", "work/eng/pert"]
import note2_check as NC
from arr import Arr, rays, far_end, first_seg
BC = NC.BC; GB = NC.GB

def use(a, seg): return len(a.t[seg[0]][seg[1]])

def claimed_tokens(a):
    """sol's §4 selections (outer-triangle rule; K_0 two single cap edges), re-implemented."""
    recs = BC.block_partition(a)
    at = defaultdict(list)
    for r in recs: at[r['far']].append(r)
    tf = defaultdict(list)
    for f in a.tris:
        vs = NC.tri_vertices(a, f)
        for L, e, _ in f: tf[L, e].append(vs)
    out = set()
    def cand(P, X, T):
        pt = NC.edge(a, P, T)
        if use(a, pt) == 1: return (P, pt)
        tx = NC.edge(a, T, X); assert use(a, tx) == 1 and len(a.events[T]) >= 3
        return (T, tx)
    def add(tok):
        assert tok not in out; out.add(tok)
    for r in recs:
        P, X = r['point'], r['far']
        if len(a.events[P]) != 3: continue
        fs = tf[NC.edge(a, P, X)]
        if r['kind'] in ('U', 'I'):
            for f in fs:
                (T,) = f - {P, X}; add(cand(P, X, T))
        elif len(at[X]) == 2:
            (Q,) = {s['point'] for s in at[X]} - {P}
            (f,) = [f for f in fs if Q not in f]; (T,) = f - {P, X}; add(cand(P, X, T))
    for X, rr in at.items():
        if len(rr) != 4: continue
        cs = [far_end(a, X, ray) for ray in rays(a, X)]
        if any(len(a.events[p]) == 4 for p in cs): continue
        sides = [NC.edge(a, cs[i], cs[(i + 1) % 4]) for i in range(4)]
        singles = [i for i in range(4) if use(a, sides[i]) == 1]
        for i in singles[:2]:
            add((cs[i], sides[i])); add((cs[(i + 1) % 4], sides[i]))
    return out

def is_block(a, P, k):
    rs = rays(a, P); fs = first_seg(a, P, rs[k])
    return fs is not None and use(a, fs) == 2 and a.is_simple(far_end(a, P, rs[k]))

def check(a):
    cl = claimed_tokens(a)
    used = set(); caseB = Counter(); nA = nB = 0
    for X, ev in enumerate(a.events):
        if len(ev) != 2 or sum(GB.tri_sectors(a, X)) != 4: continue
        cs = [far_end(a, X, r) for r in rays(a, X)]
        if any(c is None or len(a.events[c]) < 3 for c in cs): continue
        q = [len(a.events[c]) == 4 for c in cs]
        if sum(q) != 1: continue
        i = q.index(True); P, Q, R, S = cs[i], cs[(i + 1) % 4], cs[(i + 2) % 4], cs[(i + 3) % 4]
        done = False
        for u, v in ((P, Q), (P, S), (Q, R), (R, S)):
            e = NC.edge(a, u, v)
            if use(a, e) == 1:
                for tok in ((u, e), (v, e)):
                    assert len(a.events[tok[0]]) >= 3
                    assert tok not in cl, ("claimed", tok)
                    assert tok not in used, ("reused", tok)
                    used.add(tok)
                nA += 1; done = True; break
        if done: continue
        nB += 1; caseB[P] += 1
        rs = rays(a, P); m = len(rs)
        # kite block ray index at P: the ray of P pointing to X
        k = [j for j, r in enumerate(rs) if far_end(a, P, r) == X][0]
        for d in (-2, -1, 1, 2):
            assert not is_block(a, P, (k + d) % m), ("block at distance", d)
    recs = BC.block_partition(a)
    at = defaultdict(list)
    for r in recs: at[r['far']].append(r)
    kite_at = Counter(r['point'] for r in recs if len(at[r['far']]) == 4)
    for P, c in caseB.items():
        D = sum(is_block(a, P, j) for j in range(8))
        S = 8 - D - kite_at[P]
        assert S >= 2 * c, ("S_P too small", P, S, c)
    return nA, nB

if __name__ == "__main__":
    tot = Counter(); narr = 0; seen = set()
    for f in sys.argv[1:]:
        for line in open(f):
            d = json.loads(line); g = d.get("gens")
            if not g or g in seen: continue
            seen.add(g)
            try: a = Arr(g, d.get("n", 18))
            except Exception: continue
            if any(len(e) > 4 for e in a.events): continue
            nA, nB = check(a); narr += 1; tot["A"] += nA; tot["B"] += nB
    print("arrangements", narr, "K_1 kites: case A", tot["A"], "case B", tot["B"], "failures 0")

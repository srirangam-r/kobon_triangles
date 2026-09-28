"""kN_fixed: the referee's p11_fixed (C37-C50, joint C49/C45 minimisation) generalised to K points, with the
verdict-C54 no-C35 restriction, plus C55 (centroid side gaps) and C56 (O1b consecutive neighbour).
Usage: python3 kN_fixed.py K c35|noc35"""
import sys
K = int(sys.argv[1]); WITH_C35 = sys.argv[2] == 'c35'
CENT = True
T = ['X', 'F', 'V', 'C', 'O1', 'O1b', 'O0']
BL = {'X': 2, 'F': 2, 'V': 2, 'C': 3, 'O1': 1, 'O1b': 1, 'O0': 0}
R = set(range(0, K))
EOK = {'X': {0}, 'F': {2, 4}, 'V': {1, 2, 4}, 'C': {3},
       'O1': {1} if WITH_C35 else {0, 1}, 'O1b': R - {0} if WITH_C35 else R, 'O0': R - {0, 1} if WITH_C35 else R}
from itertools import combinations, product
import collections
pairs = list(combinations(range(K), 2)); NP = len(pairs)
def run(types):
    out = []
    surv = collections.Counter(); examples = {}
    for mask in range(1, 1 << NP):
        E = [pairs[i] for i in range(NP) if mask >> i & 1]
        adj = {v: set() for v in range(K)}
        for a, b in E: adj[a].add(b); adj[b].add(a)
        if any(len(adj[v]) not in EOK[types[v]] for v in range(K)): continue
        if any(all(b in adj[a] for a, b in combinations(q, 2)) for q in combinations(range(K), 4)): continue
        tris = [q for q in combinations(range(K), 3) if all(b in adj[a] for a, b in combinations(q, 2))]
        ok = True
        faces_opts = [[]]
        for v in range(K):
            if types[v] == 'F':
                nb = sorted(adj[v])
                opts = []
                if len(nb) == 2: opts = [[tuple(sorted([v] + nb))]]
                else:
                    a0 = nb[0]
                    for b0 in nb[1:]:
                        rest = [x for x in nb if x not in (a0, b0)]
                        opts.append([tuple(sorted([v, a0, b0])), tuple(sorted([v] + rest))])
                faces_opts = [fo + o for fo in faces_opts for o in opts]
        best = None
        cand = []
        for fo in faces_opts:
            faces = list(set(fo + tris))
            ok = True
            for v in range(K):
                if types[v] == 'F':
                    mine = [f for f in faces if v in f]
                    if len(mine) != len(adj[v]) // 2: ok = False; break
                    cover = [u for f in mine for u in f if u != v]
                    if sorted(cover) != sorted(adj[v]): ok = False; break
            for f in faces:
                nx = sum(types[u] in ('X', 'F') for u in f)
                if nx == 3: ok = False
                if nx == 2 and not any(types[u] in (('O1b',) if WITH_C35 else ('O1b', 'O0')) for u in f): ok = False   # C42: third vertex of a 2-F face is O1b
                if any(types[u] == 'X' for u in f): ok = False
            if not ok: continue
            # C44 (Hall, C38 with S = face): a face with two F vertices P,R and O1b vertex Q needs an extra
            # triangle: P or R has a second face (e = 4), or Q has a bridge besides P and R.
            sidecount = collections.Counter(p for f in faces for p in combinations(f, 2))
            if any(v > 2 for v in sidecount.values()): ok = False   # C46: a segment borders <= 2 faces
            twoF = [f for f in faces if sum(types[u] == 'F' for u in f) == 2]
            if not ok: continue
            fs = set()
            for f in faces:
                for a_, b_ in combinations(f, 2): fs.add((a_, b_))
            sm = len(E) + len([p for p in fs if p not in E])
            # C49: an F point with two faces (e = 4) has each cap through one vertex of each face, adjacent but
            # not consecutive on the cap: two gap pairs (one of the two matchings); minimise over matchings
            # referee fix: keep BOTH matchings per two-face F point; minimise jointly (with bent gaps) later
            fopts = []
            Eset = {tuple(sorted(e)) for e in E}
            for v in range(K):
                if types[v] == 'F' and len(adj[v]) == 4:
                    mine = [f for f in faces if v in f]
                    if len(mine) == 2:
                        a, b = [u for u in mine[0] if u != v]; c_, d = [u for u in mine[1] if u != v]
                        m1 = {frozenset((a, c_)), frozenset((b, d))}; m2 = {frozenset((a, d)), frozenset((b, c_))}
                        filt = lambda mm: {pr for pr in mm if tuple(sorted(pr)) not in fs and tuple(sorted(pr)) not in Eset}
                        fopts.append([filt(m1), filt(m2)])
            cand.append((sm, twoF, faces, fopts))
        if not cand: continue
        # bent partners (all valid maps); gap pairs (W, Q): extra-bridge neighbour W of bent V lies on a cap
        # of V through its partner Q, non-consecutive with Q (C19 (a)/(b)) -> +1 to sigma each (C45)
        Vs = [v for v in range(K) if types[v] == 'V']
        maps = []
        def rec(i, load, cur):
            if i == len(Vs):
                maps.append(dict(cur)); return
            v = Vs[i]
            for q in adj[v]:
                if types[q] not in ('O1', 'O1b', 'O0'): continue
                if load.get(q, 0) >= (2 if types[q] == 'O0' else 1): continue
                if any(r in adj[q] for r in adj[v] if r != q): continue
                load[q] = load.get(q, 0) + 1; cur[v] = q
                rec(i + 1, load, cur)
                load[q] -= 1; del cur[v]
        rec(0, {}, {})
        if not maps: continue
        best = None
        for sm, twoF, facesX, fopts in cand:
            Eset = {tuple(sorted(e)) for e in E}
            fsX = {tuple(sorted(p)) for f in facesX for p in combinations(f, 2)}
            for m in maps:
                okm = True
                for f in twoF:
                    Fs = [u for u in f if types[u] == 'F']; q = [u for u in f if u not in Fs][0]
                    if types[q] != 'O1b': continue   # verdict C54: rules need q's block at q5
                    ii = len(adj[q] - set(Fs)) >= 1 and q not in m.values()   # C45: bent partner Q cannot supply (ii)
                    if not (len(adj[Fs[0]]) == 4 or len(adj[Fs[1]]) == 4 or ii): okm = False
                if not okm: continue
                # referee fix: a degree-4 bent point has extra set {0,4,5}; the back-ray neighbour V5 lies on
                # line VQ beyond V (V between V5 and Q), so (V5, Q) is not a gap pair.  Minimise over the choice of V5.
                from itertools import product as _prod
                opts = []
                for v in m:
                    ex = [w for w in adj[v] if w != m[v]]
                    opts.append([None] if len(ex) < 3 else ex)
                gap = None
                for choice in _prod(*opts):
                    prs = set()
                    for (v, back) in zip(m, choice):
                        for w in adj[v]:
                            if w != m[v] and w != back:
                                prs.add(frozenset((w, m[v])))
                    for v in range(K):   # C55: centroid arm partners pairwise adjacent-non-consecutive on the sides
                        if types[v] == 'C':
                            for a_, b_ in combinations(sorted(adj[v]), 2):
                                if (a_, b_) not in Eset and (a_, b_) not in fsX: prs.add(frozenset((a_, b_)))
                    for fch in _prod(*fopts) if fopts else [()]:
                        u = set(prs)
                        for mm in fch: u |= mm
                        gap = len(u) if gap is None else min(gap, len(u))
                gap = gap or 0
                facepart = collections.defaultdict(set)   # C56: O1b needs a consecutive triple neighbour T off its arms
                for f in facesX:
                    for a_, b_ in combinations(f, 2): facepart[a_].add(b_); facepart[b_].add(a_)
                for q in range(K):
                    if types[q] != 'O1b': continue
                    givers = {v for v in m if m[v] == q} | {v for v in adj[q] if types[v] == 'C'}
                    if not ((adj[q] | facepart[q]) - givers): gap += 1
                if best is None or sm + gap < best: best = sm + gap; bestF = (facesX, twoF, dict(m))
        if best is None: continue
        gapmin = 0
        beta = len(E)
        B = sum(BL[t] for t in types)
        if B + beta < 3 * K - 6: continue
        sigma_min = best + gapmin
        c = collections.Counter(types)
        base = 2 * c['V'] + 2 * c['F'] + 3 * (c['O1'] + c['O1b']) + 6 * c['O0'] + c['X'] + c['O1b'] + 6 - 3 * K
        if not any(2 * beta - (sigma_min + (c['X'] - i + 1) // 2) >= base + i for i in range(c['X'] + 1)): continue  # C42: isolated X +1 (L4 or new x pair); non-isolated X adds to sigma   # X: Lemma-A touch or killed (x>=1)
        surv[types] += 1
        if 'C' not in types or K != 5:
            slack = max(2 * beta - (sigma_min + (c['X'] - i + 1) // 2) - (base + i) for i in range(c['X'] + 1))
            out.append(('ROW', types, E, 'slack', slack, 'faces', sorted(bestF[0]), 'twoF', sorted(bestF[1]), 'partners', bestF[2]))
        examples.setdefault(types, (E, B, beta, sigma_min))
    return out

if __name__ == '__main__':
    from multiprocessing import Pool
    ms = [t for t in product(T, repeat=K) if list(t) == sorted(t, key=T.index) and any(x in ('F', 'V', 'C', 'O1', 'O1b', 'O0') for x in t)]
    with Pool(4) as pool:
        for res in pool.imap_unordered(run, ms, chunksize=4):
            for r in res: print(*r, flush=True)

"""C37: k=5, beta>=1 type/bridge-graph profiles surviving proven constraints.
Types: X (no bridge), F (type X in all-multiple face(s), e in {2,4}), V (bent, e in {1,2,4}),
C (centroid, e=3), O1 (1 block, e>=1 by C35), O0 (0 blocks, e>=2 by C35).
Constraints:
  bridge graph G: simple, K4-free (Lemma K4), degrees = e.
  triangles of G are all-multiple faces; a face has <= 2 type-X vertices (X/F), and if it has 2 the
    third is O1/O0 (C24 F3); an F point with e=2 has its two neighbours forming a face with it
    (they are consecutive; the edge between them may or may not be a bridge); e=4: two faces.
  V: one neighbour is its partner in O1/O0; partner receives <= 2 bent, and 2 only if O0 (C21);
    V's other neighbours are not G-adjacent to its partner (C19 (b)); e=4 needs rays 0,4,5 bridges.
  D-count: B + beta >= 9.
  master (Cred>=0): 2beta - sigma >= 2#V + 2#F + 3#O1 + 6#O0 - 9, sigma >= beta + #(face sides not bridges).
Output: surviving (types, edges)."""
from itertools import combinations, product
import collections, sys
CENT = len(sys.argv) > 1
T = ['X', 'F', 'V', 'C', 'O1', 'O1b', 'O0']
BL = {'X': 2, 'F': 2, 'V': 2, 'C': 3, 'O1': 1, 'O1b': 1, 'O0': 0}
EOK = {'X': {0}, 'F': {2, 4}, 'V': {1, 2, 4}, 'C': {3}, 'O1': {1}, 'O1b': {1, 2, 3, 4}, 'O0': {2, 3, 4}}
pairs = list(combinations(range(5), 2))
surv = collections.Counter(); examples = {}
for types in product(T, repeat=5):
    if list(types) != sorted(types, key=T.index): continue   # multiset representative
    if not any(t in ('F', 'V', 'C', 'O1', 'O1b', 'O0') for t in types): continue
    for mask in range(1, 1 << 10):
        E = [pairs[i] for i in range(10) if mask >> i & 1]
        adj = {v: set() for v in range(5)}
        for a, b in E: adj[a].add(b); adj[b].add(a)
        if any(len(adj[v]) not in EOK[types[v]] for v in range(5)): continue
        if any(all(b in adj[a] for a, b in combinations(q, 2)) for q in combinations(range(5), 4)): continue
        tris = [q for q in combinations(range(5), 3) if all(b in adj[a] for a, b in combinations(q, 2))]
        ok = True
        faces_opts = [[]]
        for v in range(5):
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
        for fo in faces_opts:
            faces = list(set(fo + tris))
            ok = True
            for f in faces:
                nx = sum(types[u] in ('X', 'F') for u in f)
                if nx == 3: ok = False
                if nx == 2 and not any(types[u] in ('O1b', 'O0') for u in f): ok = False
                if any(types[u] == 'X' for u in f): ok = False
            if not ok: continue
            fs = set()
            for f in faces:
                for a_, b_ in combinations(f, 2): fs.add((a_, b_))
            sm = len(E) + len([p for p in fs if p not in E])
            if best is None or sm < best: best = sm
        if best is None: continue
        # bent partners
        partners = {}
        good = True
        def assign(vs, load):
            if not vs: return True
            v = vs[0]
            for q in adj[v]:
                if types[q] not in ('O1', 'O1b', 'O0'): continue
                if load.get(q, 0) >= (2 if types[q] == 'O0' else 1): continue
                if any(r in adj[q] for r in adj[v] if r != q): continue      # C19 (b)
                load[q] = load.get(q, 0) + 1
                if assign(vs[1:], load): return True
                load[q] -= 1
            return False
        arms = [v for v in range(5) if types[v] == 'V']
        if CENT:
            # centroid arms: every centroid neighbour is a 0/1-block partner (capacity as for bent)
            load = {}
            bad = False
            for v in range(5):
                if types[v] == 'C':
                    for q in adj[v]:
                        if types[q] not in ('O1', 'O1b', 'O0'): bad = True
                        load[q] = load.get(q, 0) + 1
            if bad: continue
            if any(load[q] > (2 if types[q] == 'O0' else 1) for q in load): continue
        if not assign(arms, {}): continue
        beta = len(E)
        B = sum(BL[t] for t in types)
        if B + beta < 9: continue
        sigma_min = best
        c = collections.Counter(types)
        if 2 * beta - sigma_min < 2 * c['V'] + 2 * c['F'] + 3 * (c['O1'] + c['O1b']) + 6 * c['O0'] + c['X'] + c['O1b'] - 9: continue   # X: Lemma-A touch or killed (x>=1)
        surv[types] += 1
        examples.setdefault(types, (E, B, beta, sigma_min))
for t, k in sorted(surv.items(), key=lambda kv: -kv[1]):
    print(t, k, examples[t])
print(len(surv), 'type multisets survive;', sum(surv.values()), 'labelled graphs')

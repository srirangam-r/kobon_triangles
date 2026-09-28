"""Referee (AUDIT_k5L, Q2): re-derive the k=5 beta>0 residue rows from the k5_p11.py filter logic and check
 (a) every jsonl row's faces / twoF are the ONLY valid face option (so FC units and C43 sites are forced),
 (b) survival and slack are invariant under type-preserving relabelling (so the 28 labelled rows are closed
     under isomorphism and the free label bijection of k5L covers every labelling),
 (c) the jsonl rows = all labelled survivors of the filter after C47 / C50(b), with the same slack, sites, need.
Filter logic copied from work/t3/k5_p11.py (greedy C49 matching; referee's p11_fixed gives identical rows)."""
import collections, json, sys
from itertools import combinations, permutations, product
T = ['X', 'F', 'V', 'C', 'O1', 'O1b', 'O0']
BL = {'X': 2, 'F': 2, 'V': 2, 'C': 3, 'O1': 1, 'O1b': 1, 'O0': 0}
EOK = {'X': {0}, 'F': {2, 4}, 'V': {1, 2, 4}, 'C': {3}, 'O1': {1}, 'O1b': {1, 2, 3, 4}, 'O0': {2, 3, 4}}
pairs = list(combinations(range(5), 2))


def evaluate(types, E):
    """k5_p11.py body for one labelled graph; returns None (killed) or dict(slack, faces, twoF, allopts)."""
    adj = {v: set() for v in range(5)}
    for a, b in E: adj[a].add(b); adj[b].add(a)
    if any(len(adj[v]) not in EOK[types[v]] for v in range(5)): return None
    if any(all(b in adj[a] for a, b in combinations(q, 2)) for q in combinations(range(5), 4)): return None
    tris = [q for q in combinations(range(5), 3) if all(b in adj[a] for a, b in combinations(q, 2))]
    faces_opts = [[]]
    for v in range(5):
        if types[v] == 'F':
            nb = sorted(adj[v]); opts = []
            if len(nb) == 2: opts = [[tuple(sorted([v] + nb))]]
            else:
                a0 = nb[0]
                for b0 in nb[1:]:
                    rest = [x for x in nb if x not in (a0, b0)]
                    opts.append([tuple(sorted([v, a0, b0])), tuple(sorted([v] + rest))])
            faces_opts = [fo + o for fo in faces_opts for o in opts]
    cand = []
    for fo in faces_opts:
        faces = list(set(fo + tris)); ok = True
        for v in range(5):
            if types[v] == 'F':
                mine = [f for f in faces if v in f]
                if len(mine) != len(adj[v]) // 2: ok = False; break
                cover = [u for f in mine for u in f if u != v]
                if sorted(cover) != sorted(adj[v]): ok = False; break
        for f in faces:
            nx = sum(types[u] in ('X', 'F') for u in f)
            if nx == 3: ok = False
            if nx == 2 and not any(types[u] == 'O1b' for u in f): ok = False
            if any(types[u] == 'X' for u in f): ok = False
        if not ok: continue
        sidecount = collections.Counter(p for f in faces for p in combinations(f, 2))
        if any(v > 2 for v in sidecount.values()): ok = False
        twoF = [f for f in faces if sum(types[u] == 'F' for u in f) == 2]
        if not ok: continue
        fs = set()
        for f in faces:
            for a_, b_ in combinations(f, 2): fs.add((a_, b_))
        sm = len(E) + len([p for p in fs if p not in E])
        fgap = set()
        for v in range(5):
            if types[v] == 'F' and len(adj[v]) == 4:
                mine = [f for f in faces if v in f]
                if len(mine) == 2:
                    a, b = [u for u in mine[0] if u != v]; c_, d = [u for u in mine[1] if u != v]
                    m1 = {frozenset((a, c_)), frozenset((b, d))}; m2 = {frozenset((a, d)), frozenset((b, c_))}
                    fgap |= min(m1, m2, key=lambda mm: len(mm - fgap))
        fgap = {pr for pr in fgap if tuple(sorted(pr)) not in fs and tuple(sorted(pr)) not in [tuple(sorted(e)) for e in E]}
        sm += len(fgap)
        cand.append((sm, twoF, faces))
    if not cand: return None
    Vs = [v for v in range(5) if types[v] == 'V']; maps = []
    def rec(i, load, cur):
        if i == len(Vs): maps.append(dict(cur)); return
        v = Vs[i]
        for q in adj[v]:
            if types[q] not in ('O1', 'O1b', 'O0'): continue
            if load.get(q, 0) >= (2 if types[q] == 'O0' else 1): continue
            if any(r in adj[q] for r in adj[v] if r != q): continue
            load[q] = load.get(q, 0) + 1; cur[v] = q
            rec(i + 1, load, cur)
            load[q] -= 1; del cur[v]
    rec(0, {}, {})
    if not maps: return None
    best = None; allopts = set()
    for sm, twoF, facesX in cand:
        for m in maps:
            okm = True
            for f in twoF:
                Fs = [u for u in f if types[u] == 'F']; q = [u for u in f if u not in Fs][0]
                ii = len(adj[q] - set(Fs)) >= 1 and q not in m.values()
                if not (len(adj[Fs[0]]) == 4 or len(adj[Fs[1]]) == 4 or ii): okm = False
            if not okm: continue
            allopts.add((tuple(sorted(facesX)), tuple(sorted(twoF))))
            opts = []
            for v in m:
                ex = [w for w in adj[v] if w != m[v]]
                opts.append([None] if len(ex) < 3 else ex)
            gap = None
            for choice in product(*opts):
                prs = set()
                for (v, back) in zip(m, choice):
                    for w in adj[v]:
                        if w != m[v] and w != back: prs.add(frozenset((w, m[v])))
                gap = len(prs) if gap is None else min(gap, len(prs))
            gap = gap or 0
            if best is None or sm + gap < best: best = sm + gap; bestF = (facesX, twoF, dict(m))
    if best is None: return None
    beta = len(E); B = sum(BL[t] for t in types)
    if B + beta < 9: return None
    c = collections.Counter(types)
    base = 2 * c['V'] + 2 * c['F'] + 3 * (c['O1'] + c['O1b']) + 6 * c['O0'] + c['X'] + c['O1b'] - 9
    if not any(2 * beta - (best + (c['X'] - i + 1) // 2) >= base + i for i in range(c['X'] + 1)): return None
    slack = max(2 * beta - (best + (c['X'] - i + 1) // 2) - (base + i) for i in range(c['X'] + 1))
    return dict(slack=slack, faces=sorted(bestF[0]), twoF=sorted(bestF[1]), allopts=allopts, B=B, beta=beta)


def sites_need(types, twoF, slack):
    inface = {u for f in twoF for u in f if types[u] == 'O1b'}
    s = [('C43', tuple(f)) for f in twoF] + [('C50', u) for u, x in enumerate(types) if x == 'O1' or (x == 'O1b' and u not in inface)]
    return s, len(s) - slack


def canon(types, E):
    best = None
    for p in permutations(range(5)):
        if any(types[p[v]] != types[v] for v in range(5)): continue
        key = tuple(sorted(tuple(sorted((p[a], p[b]))) for a, b in E))
        best = key if best is None or key < best else best
    return best


def main():
    rows = [json.loads(l) for l in open(sys.argv[1])]
    bad = 0
    # (a) + (c): each row reproduced, unique face option
    for gi, r in enumerate(rows):
        t = tuple(r['types']); E = [tuple(e) for e in r['bridges']]
        ev = evaluate(t, E)
        assert ev is not None, gi
        fdeg4 = [v for v in range(5) if t[v] == 'F' and sum(v in e for e in E) == 4]
        s, need = sites_need(t, ev['twoF'], ev['slack'])
        okrow = (ev['slack'] == r['slack'] and [list(f) for f in ev['faces']] == r['faces'] and need == r['need']
                 and [x['kind'] for x in r['sites']] == [k for k, _ in s] and len(ev['allopts']) == 1)
        if not okrow: bad += 1
        print(gi, t, 'slack', ev['slack'], 'faceopts', len(ev['allopts']), 'Fdeg4', fdeg4, 'need', need, 'OK' if okrow else 'DIFF')
    # (b) + (c): all labelled graphs of the residue multisets, grouped by isomorphism class
    multisets = sorted({tuple(r['types']) for r in rows})
    surv = []
    classes = collections.defaultdict(list)
    for t in multisets:
        for mask in range(1, 1 << 10):
            E = [pairs[i] for i in range(10) if mask >> i & 1]
            ev = evaluate(t, E)
            classes[t, canon(t, E)].append((E, ev))
            if ev is not None:
                o4 = [u for u, x in enumerate(t) if x == 'O1b' and sum(u in f for f in ev['twoF']) >= 2]
                if t != ('X', 'X', 'X', 'V', 'O1') and not o4: surv.append((t, E, ev))
    noninv = 0
    for key, lst in classes.items():
        vals = {None if ev is None else (ev['slack'], sites_need(key[0], ev['twoF'], ev['slack'])[1]) for _, ev in lst}
        if len(vals) > 1:
            noninv += 1; print('NON-INVARIANT class', key, vals)
    rowset = {(tuple(r['types']), tuple(tuple(e) for e in r['bridges'])) for r in rows}
    survset = {(t, tuple(E)) for t, E, _ in surv}
    print('labelled survivors', len(survset), 'jsonl rows', len(rowset), 'equal', survset == rowset,
          'iso classes among survivors', len({(t, canon(t, E)) for t, E, _ in surv}), 'non-invariant classes', noninv)
    print('ROW CHECK', 'PASS' if bad == 0 and survset == rowset and noninv == 0 else 'FAIL')


main()

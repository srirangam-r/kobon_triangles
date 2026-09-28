"""Independent re-implementation of the C62-C65 kill application on work/t3/k5_exceptions.jsonl."""
import json
from itertools import combinations
rows = [json.loads(l) for l in open('/home/nail/stuff/sundai_math/work/t3/k5_exceptions.jsonl')]
res = {}
for g, r in enumerate(rows):
    t = r['types']; E = {frozenset(e) for e in r['bridges']}; Fs = [frozenset(f) for f in r['faces']]
    nb = {v: {u for e in E if v in e for u in e if u != v} for v in range(5)}
    # sanity: every listed face is a triangle of the bridge graph; every bridge-graph triangle is listed
    tri_g = {frozenset(c) for c in combinations(range(5), 3) if all(frozenset(p) in E for p in combinations(c, 2))}
    assert tri_g <= set(Fs), (g, Fs, tri_g)
    for f1, f2 in combinations(Fs, 2):
        if len(f1 & f2) == 2: assert frozenset(f1 & f2) in E, "twin side not a bridge"
    k = []
    for f in Fs:                                   # C65: >= 2 type-X (F) vertices in one face
        if sum(t[v] == 'F' for v in f) >= 2: k.append('C65')
    for f1, f2 in combinations(Fs, 2):             # C62: faces sharing a side, both apexes F
        if len(f1 & f2) == 2:
            (p1,), (p2,) = f1 - f2, f2 - f1
            if t[p1] == 'F' and t[p2] == 'F': k.append('C62')
    for Q in range(5):                             # C63: Q with a block in 3 faces consecutive around Q, outer sides bridges, e(Q)=4
        if t[Q] in ('O0',): continue
        mine = [f for f in Fs if Q in f]
        for f1 in mine:
            for f2 in mine:
                for f3 in mine:
                    if len({f1, f2, f3}) < 3: continue
                    s12 = (f1 & f2) - {Q}; s23 = (f2 & f3) - {Q}
                    if len(s12) == 1 and len(s23) == 1 and s12 != s23:
                        o1 = next(iter(f1 - {Q} - s12)); o3 = next(iter(f3 - {Q} - s23))
                        if o1 != o3 and frozenset((Q, o1)) in E and frozenset((Q, o3)) in E and len(nb[Q]) == 4:
                            k.append('C63')
    for V in range(5):                             # C64: every possible partner (0/1-block bridge nbr) has a face with both sides bridges
        if t[V] != 'V': continue
        cand = [q for q in nb[V] if t[q] in ('O0', 'O1', 'O1b')]
        bad = lambda q: any(q in f and all(frozenset((q, u)) in E for u in f - {q}) for f in Fs)
        if cand and all(bad(q) for q in cand): k.append('C64')
    res[g] = sorted(set(k))
    print(g, t, res[g])
print('dead', sum(1 for v in res.values() if v), 'of', len(rows))

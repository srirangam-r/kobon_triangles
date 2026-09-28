"""Apply the proposed lemmas C62-C65 to the 28 residue graphs of work/t3/k5_exceptions.jsonl.

C62 (twin faces): two listed faces sharing a side, both third vertices of type F      -> contradiction.
C63 (fan):        a point Q in three listed faces, consecutive around Q (f1,f2 share a side at Q, f2,f3 share
                  another), with the two outer face sides at Q bridges, e(Q) = 4 and Q with a block -> contradiction.
C64 (bent partner): every admissible partner of some bent point (a bridge neighbour of type O1/O1b/O0) is a
                  vertex of a listed face whose two sides at that vertex are bridges               -> contradiction.
C65 (converging caps): a listed face with two type-F vertices                                   -> contradiction.
    python3 work/t3/c62_kills.py
"""
import json
from itertools import combinations

rows = [json.loads(l) for l in open('/home/nail/stuff/sundai_math/work/t3/k5_exceptions.jsonl')]
dead = {}
for gi, r in enumerate(rows):
    t, E, faces, slack = r['types'], {tuple(sorted(e)) for e in r['bridges']}, [tuple(sorted(f)) for f in r['faces']], r['slack']
    adj = {v: {u for e in E for u in e if v in e and u != v} for v in range(5)}
    br = lambda a, b: tuple(sorted((a, b))) in E
    why = []
    # C62
    for f1, f2 in combinations(faces, 2):
        sh = set(f1) & set(f2)
        if len(sh) == 2:
            (p1,), (p2,) = set(f1) - sh, set(f2) - sh
            if t[p1] == 'F' and t[p2] == 'F':
                why.append(f'C62 twin faces {f1},{f2} with F third vertices {p1},{p2}')
    # C63
    for Q in range(5):
        mine = [f for f in faces if Q in f]
        for f1, f2, f3 in ((a, b, c) for a in mine for b in mine for c in mine if len({a, b, c}) == 3):
            s12, s23 = set(f1) & set(f2) - {Q}, set(f2) & set(f3) - {Q}
            if len(s12) == 1 and len(s23) == 1 and s12 != s23:
                (o1,) = set(f1) - {Q} - s12
                (o3,) = set(f3) - {Q} - s23
                if br(Q, o1) and br(Q, o3) and len(adj[Q]) == 4 and t[Q] in ('O1', 'O1b', 'V', 'F', 'X'):
                    why.append(f'C63 fan at {Q} ({t[Q]}): faces {f1},{f2},{f3}, e=4, needs a 5th bridge for its block')
                    break
    # C64
    for V in range(5):
        if t[V] != 'V':
            continue
        cands = [q for q in adj[V] if t[q] in ('O1', 'O1b', 'O0')]

        def blocked(q):
            return any(q in f and all(br(q, u) for u in f if u != q) for f in faces)
        if cands and all(blocked(q) for q in cands):
            why.append(f'C64 bent {V}: every partner candidate {cands} has both sides of a face doubly used')
    # C65 (converging caps): a face with two type-X (F) vertices is impossible
    for f in faces:
        if sum(t[u] == 'F' for u in f) >= 2:
            why.append(f'C65 face {f} has two F vertices')
    dead[gi] = why
    print(gi, t, 'slack', slack, 'need', r['need'], '->', '; '.join(why) if why else 'SURVIVES')
print(f"\nkilled {sum(1 for w in dead.values() if w)}/{len(rows)}")
for tag in ('C62', 'C63', 'C64', 'C65'):
    print(tag, sorted(g for g, w in dead.items() if any(x.startswith(tag) for x in w)))

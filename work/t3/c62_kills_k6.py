"""Apply the k-independent parts of C62-C65 to the k = 6, beta > 0 centroid-free graphs (kNj6_c35.out ROW lines,
kN_fixed2.py with C35; C35 at k = 6 needs k = 5 closed, which C62-C65 would give).
C62 twin faces with two F third vertices; C63 fan point with exactly its 4 fan bridges and a block;
C64 bent point whose every O-type bridge neighbour has both sides of a listed face as bridges; C65 face with two F.
    python3 work/t3/c62_kills_k6.py [kNj6_c35.out]"""
import ast, re, sys, collections
from itertools import combinations
fn = sys.argv[1] if len(sys.argv) > 1 else 'kNj6_c35.out'
rows = []
for l in open(fn):
    if not l.startswith('ROW'): continue
    m = re.match(r"ROW (\(.*?\)) (\[.*?\]) slack (-?\d+) faces (\[.*?\]) twoF (\[.*?\]) partners (\{.*?\})", l.strip())
    rows.append((ast.literal_eval(m.group(1)), ast.literal_eval(m.group(2)), int(m.group(3)), ast.literal_eval(m.group(4))))
K = len(rows[0][0])
BLK = {'X': 2, 'F': 2, 'V': 2, 'C': 3, 'O1': 1, 'O1b': 1, 'O0': 0}
kill = collections.Counter(); surv = []
for t, E, slack, faces in rows:
    E = {tuple(sorted(e)) for e in E}; faces = [tuple(sorted(f)) for f in faces]
    adj = {v: {u for e in E for u in e if v in e and u != v} for v in range(K)}
    br = lambda a, b: tuple(sorted((a, b))) in E
    why = set()
    for f1, f2 in combinations(faces, 2):
        sh = set(f1) & set(f2)
        if len(sh) == 2:
            (p1,), (p2,) = set(f1) - sh, set(f2) - sh
            if t[p1] == 'F' and t[p2] == 'F': why.add('C62')
    for Q in range(K):
        mine = [f for f in faces if Q in f]
        for f1 in mine:
            for f2 in mine:
                for f3 in mine:
                    if len({f1, f2, f3}) < 3: continue
                    s12, s23 = set(f1) & set(f2) - {Q}, set(f2) & set(f3) - {Q}
                    if len(s12) == 1 and len(s23) == 1 and s12 != s23:
                        (o1,) = set(f1) - {Q} - s12; (o3,) = set(f3) - {Q} - s23
                        fan = {o1, o3} | s12 | s23
                        if br(Q, o1) and br(Q, o3) and adj[Q] == fan and BLK[t[Q]] >= 1: why.add('C63')
    for V in range(K):
        if t[V] != 'V': continue
        cands = [q for q in adj[V] if t[q] in ('O1', 'O1b', 'O0')]
        if cands and all(any(q in f and all(br(q, u) for u in f if u != q) for f in faces) for q in cands): why.add('C64')
    for f in faces:
        if sum(t[u] == 'F' for u in f) >= 2: why.add('C65')
    for w in why: kill[w] += 1
    if why: kill['any'] += 1
    else: surv.append((t, sorted(E), slack, faces))
print(f'{len(rows)} graphs (K={K}); killed by: {dict(kill)}; survivors {len(surv)}')
ms = collections.Counter(s[0] for s in surv)
for k_, v in ms.most_common(15): print('  ', v, k_)
# C50 read-out on the survivors (1-block Lemma-A sites; no 2-F faces remain, so every O1/O1b point is a site)
need = collections.Counter()
for t, E, slack, faces in surv:
    sites = sum(1 for x in t if x in ('O1', 'O1b'))
    need[max(0, sites - slack)] += 1
print('survivors by C50 exceptions needed (need -> #graphs):', dict(sorted(need.items())))

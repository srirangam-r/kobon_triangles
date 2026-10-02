# For every kite with exactly one quadruple corner: are the cap edges between triple corners singly used?
import sys, json, glob
from collections import Counter
sys.path[:0] = ["work/bbl", "work/t3"]
import note2_check as NC
from arr import Arr, rays, far_end
BC = NC.BC; GB = BC.GB
files = ["work/eng/lattice/lattice18.jsonl", "work/eng/lattice/lattice_family.jsonl", "work/eng/lattice/mixed_all.jsonl", "work/phi/gallery18.jsonl"]
stat = Counter(); ex = []
seen = set()
for f in files:
    for line in open(f):
        d = json.loads(line); g = d.get("gens")
        if not g or g in seen: continue
        seen.add(g)
        try: a = Arr(g, d.get("n", 18))
        except Exception: continue
        if any(len(e) > 4 for e in a.events): continue
        for X, ev in enumerate(a.events):
            if len(ev) != 2 or sum(GB.tri_sectors(a, X)) != 4: continue
            cs = [far_end(a, X, r) for r in rays(a, X)]
            if any(c is None or len(a.events[c]) < 3 for c in cs): continue
            q = [len(a.events[c]) == 4 for c in cs]
            if sum(q) != 1: continue
            i = q.index(True); P = cs[i]
            w = "".join(map(str, GB.tri_sectors(a, P)))
            typ = "all8" if w == "11111111" else ("w7" if w.count("1") == 7 else "other")
            # cyclic corners P, Q, R, S
            Q, R, S = cs[(i + 1) % 4], cs[(i + 2) % 4], cs[(i + 3) % 4]
            use = lambda u, v: len(a.t[NC.edge(a, u, v)[0]][NC.edge(a, u, v)[1]])
            key = (typ, use(P, Q), use(Q, R), use(R, S), use(S, P))
            stat[key] += 1
            if typ == "all8" and use(Q, R) == 2 and use(R, S) == 2 and len(ex) < 3: ex.append((g, X))
for k, v in sorted(stat.items()): print(k, v)
print("all8 with QR,RS both double:", ex[:3])

"""Emit the 28 surviving k=5, beta>0 graphs (after C47, C49, C50(b)) as JSONL with their credit sites.
Each row: types, bridges, faces, slack, credit sites (C43: 2-F faces -> exception E2 at the non-mutual
F vertex; C50: 1-block points not in 2-F faces -> exception (i) mutual apex [O1b only] or (ii) block
cap point is a line end), and 'need' = #credit sites - slack = minimum number of exceptions."""
import json, sys
sys.argv = ['x', 'k5_p11.out']
exec(open('profile_ilp.py').read().split("kill = collections.Counter()")[0])
out = open('k5_exceptions.jsonl', 'w'); n = 0
for r in rows:
    t = r['types']
    o4 = [u for u, x in enumerate(t) if x == 'O1b' and sum(u in f for f in r['twoF']) >= 2]
    if o4: continue                                   # C50 (b)
    inface = {u for f in r['twoF'] for u in f if t[u] == 'O1b'}
    sites = [{'kind': 'C43', 'face': f, 'exception': 'E2 at the non-mutual F vertex (2nd on its axis)'} for f in r['twoF']]
    sites += [{'kind': 'C50', 'point': u, 'type': x,
               'exception': ('(ii) cap point is a line end' if x == 'O1' else '(i) mutual apex or (ii) cap point is a line end')}
              for u, x in enumerate(t) if x == 'O1' or (x == 'O1b' and u not in inface)]
    need = len(sites) - r['slack']
    out.write(json.dumps({'types': t, 'bridges': r['E'], 'faces': r['faces'], 'slack': r['slack'], 'sites': sites, 'need': need}) + '\n')
    n += 1
print(n, 'graphs written to k5_exceptions.jsonl')

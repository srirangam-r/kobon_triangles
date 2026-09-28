"""Discharging read-out for the k=5, beta>0 residue (refereed lemmas as encoded in
referee4/p10_fixed.py + C46 + C49 two-face gaps; C47 kill of (X,X,X,V,O1) applied).
For each surviving bridge graph: slack (max over the isolated-X split and min over face
options / partner maps, as in the filter) and structural features; then, for each candidate
credit type, how many graphs would die if every occurrence were worth +1.
Input: ROW lines from k5_p11.py (python3 k5_p11.py cent > k5_p11.out)."""
import ast, collections, re, sys
rows = []
for l in open(sys.argv[1] if len(sys.argv) > 1 else 'k5_p11.out'):
    if not l.startswith('ROW'): continue
    m = re.match(r"ROW (\(.*?\)) (\[.*?\]) slack (-?\d+) faces (\[.*?\]) twoF (\[.*?\]) partners (\{.*?\})", l.strip())
    types, E, slack, faces, twoF, partners = (ast.literal_eval(m.group(1)), ast.literal_eval(m.group(2)), int(m.group(3)),
                                               ast.literal_eval(m.group(4)), ast.literal_eval(m.group(5)), ast.literal_eval(m.group(6)))
    if types == ('X', 'X', 'X', 'V', 'O1'): continue          # C47
    rows.append(dict(types=types, E=E, slack=slack, faces=faces, twoF=twoF, partners=partners))
def feat(r):
    t = r['types']
    oneF = [f for f in r['faces'] if sum(t[u] == 'F' for u in f) == 1]
    zeroF = [f for f in r['faces'] if sum(t[u] == 'F' for u in f) == 0]
    return {'2F faces (C43 w/o E2)': len(r['twoF']), '1F faces': len(oneF), '0F faces': len(zeroF),
            'O1b points': t.count('O1b'), 'O1a points': t.count('O1'), 'bent points': t.count('V'),
            'F points': t.count('F')}
kill = collections.Counter()
print(f"{len(rows)} graphs")
for r in rows:
    f = feat(r)
    print(r['types'], r['E'], 'slack', r['slack'], f)
    for k, v in f.items():
        if v > r['slack']: kill[k] += 1
print('\nGraphs killed if every occurrence of the feature gave +1 credit:')
for k, v in kill.most_common(): print(f'  {k}: {v}/{len(rows)}')

# C50: Lemma-A touch for 1-block points (C10 at the block's cap point), +1 each unless
# (i) mutual with a triple apex (never for O1a; always for the O1b vertex of a 2-F face, C42), or
# (ii) the cap point is an end of the block line.  Report: graphs killed with no exception, and for
# the rest the number of exceptions the adversary needs (credits - slack).
print('\nC50 credit (1-block Lemma-A touches):')
need = collections.Counter(); dead = 0
for r in rows:
    t = r['types']
    inface = {u for f in r['twoF'] for u in f if t[u] == 'O1b'}
    cred = sum(1 for u, x in enumerate(t) if x == 'O1') + sum(1 for u, x in enumerate(t) if x == 'O1b' and u not in inface)
    ex = cred - r['slack']
    if ex > 0:
        dead += 1; need[ex] += 1
    else:
        print('  SURVIVES C50 outright:', t, r['E'], 'slack', r['slack'], 'credit', cred)
print(f'  {dead}/{len(rows)} graphs need >= 1 C50 exception ((i) mutual apex or (ii) line end); distribution {dict(need)}')

# Combined: C43 (2-F faces, exception E2) + C50 (1-block points, exceptions (i)/(ii)).
print('\nCombined C43 + C50:')
dist = collections.Counter(); surv = []
for r in rows:
    t = r['types']
    inface = {u for f in r['twoF'] for u in f if t[u] == 'O1b'}
    c50 = sum(1 for x in t if x == 'O1') + sum(1 for u, x in enumerate(t) if x == 'O1b' and u not in inface)
    tot = len(r['twoF']) + c50
    ex = tot - r['slack']
    dist[max(ex, 0)] += 1
    if ex <= 0: surv.append((t, r['E'], r['slack'], tot))
print('  exceptions needed -> #graphs:', dict(sorted(dist.items())))
for s in surv: print('  no exception needed:', s)

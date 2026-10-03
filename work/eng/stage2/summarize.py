import json, glob, os, collections
res = {}
for tag in ['r1', 'r2', 'r3']:
    for d in sorted(glob.glob(f'logs/{tag}/q*')):
        f = d + '/result.json'
        if not os.path.exists(f): continue
        j = json.load(open(f)); key = os.path.basename(d)
        res[key] = (j['result'], j['seconds'], tag)   # later rounds override
tp = lambda k: 'double-B (C...C...)' if k.count('C') == 2 else 'single-B' if k.count('C') == 1 else 'alternating'
tab = collections.defaultdict(collections.Counter); tm = collections.defaultdict(float)
for k, (r, s, t) in res.items():
    ty = tp(k.split('_')[1].replace('d', '.')); tab[ty][r] += 1; tm[ty] += s
for ty in tab: print(ty, dict(tab[ty]), 'core-seconds', round(tm[ty]))
print('total', len(res), collections.Counter(v[0] for v in res.values()))
print('SAT:', [k for k, v in res.items() if v[0] == 'SAT'])
print('UNKNOWN:', sorted(k for k, v in res.items() if v[0] == 'UNKNOWN')[:60])

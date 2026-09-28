import sys, json, glob, collections
sys.path.insert(0, '.'); sys.path.insert(0, '../../search')
from arr import Arr
from base2 import chi_from_word
f = sorted(glob.glob('../../tools/external/kobon-solutions/gallery/data/18/*.json'))[0]
d = json.load(open(f)); a = Arr(d['gens']); chi = chi_from_word(d['gens'], 18)
c = collections.Counter()
for r in range(18):
    for i in range(18):
        for j in range(18):
            if len({r, i, j}) < 3: continue
            t = tuple(sorted((r, i, j)))
            if chi[t] == 0: continue
            model = chi[t] == (-1 if i < j else 1)
            Xi = next(e for e in a.rows[r] if i in a.events[e]); Xj = next(e for e in a.rows[r] if j in a.events[e])
            sweep = a.pos[r][Xi] < a.pos[r][Xj]
            c[(model, sweep)] += 1
print(c)

#!/usr/bin/env python3
"""Coverage of the 1248 open-type cubes (104 quads x 12 masks): a cube is closed if some round has it UNSAT unsplit,
or if all 16 children of a split on one ray are UNSAT. Any SAT is reported."""
import os, json, collections, glob
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs'))
L1 = [l.split() for l in open('list_r1.txt') if l.strip()]
open_cubes = [(c, m) for c, m in L1 if m.count('C') >= 1]
res = collections.defaultdict(list); sat = []
for f in glob.glob('r*/*/result.json'):
    d = os.path.basename(os.path.dirname(f)); r = json.load(open(f))['result']
    res[d].append(r)
    if r == 'SAT': sat.append(f)
closed = collections.Counter(); total = collections.Counter(); unk = []
for c, m in open_cubes:
    k = f"q{c}_{m.replace('.', 'd')}"; t = 'starB' if m.count('C') == 2 else 'singleB'; total[t] += 1
    ok = 'UNSAT' in res.get(k, [])
    if not ok:
        kids = collections.defaultdict(dict)
        for d, rs in res.items():
            if d.startswith(k + '_s'):
                sp = d[len(k) + 2:]; mm, cc = sp.split('-')
                kids[mm][cc] = 'UNSAT' in rs
        ok = any(len(v) == 16 and all(v.values()) for v in kids.values())
    closed[t] += ok
    if not ok: unk.append(k)
print({t: f"{closed[t]}/{total[t]}" for t in total}, "SAT models:", sat)
import sys
if len(sys.argv) > 1: open(sys.argv[1], 'w').write('\n'.join(unk) + '\n')

#!/usr/bin/env python3
"""Export per-cube Stage-2 SAT results (all rounds) to results.csv and print coverage of the 1,248 open-type cubes.
usage: export_results.py LOGDIR OUTCSV"""
import os, sys, json, glob, csv, collections
logdir, outcsv = sys.argv[1], sys.argv[2]
rows = []
for f in sorted(glob.glob(os.path.join(logdir, 'r[0-9]*', '*', 'result.json'))):
    rnd = os.path.basename(os.path.dirname(os.path.dirname(f))); d = os.path.basename(os.path.dirname(f))
    r = json.load(open(f)); built = json.loads(open(os.path.join(os.path.dirname(f), 'log.jsonl')).readline())
    cube, mask = d.split('_')[0][1:], d.split('_')[1].replace('d', '.')
    typ = {2: 'double-B star', 1: 'single-B endpoint', 0: 'alternating'}[mask.count('C')]
    rows.append(dict(round=rnd, cube=cube, quad='-'.join(map(str, r['quad'])), mask=mask, type=typ, qpin=int(bool(built.get('qpin'))),
                     result=r['result'], seconds=r['seconds'], conflicts=r['stats'].get('conflicts')))
with open(outcsv, 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
best = {}
for r in rows:
    k = (r['cube'], r['mask'])
    if r['result'] in ('UNSAT', 'SAT') or k not in best: best[k] = r
tot = collections.Counter(); cnt = collections.Counter()
for (c, m), r in best.items():
    if r['type'] == 'alternating': continue
    tot[r['type']] += 1; cnt[r['type'], r['result']] += 1
open_total = {'double-B star': 416, 'single-B endpoint': 832}
for t, n in open_total.items():
    print(f"{t}: {cnt[t, 'UNSAT']} UNSAT, {cnt[t, 'SAT']} SAT, {cnt[t, 'UNKNOWN']} UNKNOWN, {n - tot[t]} not run, of {n}")

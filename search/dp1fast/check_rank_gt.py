"""Per-rank comparison of best_by_rank() with work/ext n=17 ground truth (sign +1: all 18 ranks SAT at 93)."""
import sys,glob,json,collections
sys.path.insert(0,'search/dp1fast')
from dp1fast import *
gt=collections.defaultdict(dict)
for f in glob.glob('work/ext/n17_t93_s*.jsonl'):
    for l in open(f):
        r=json.loads(l); gt[r['base']][(r['ranks'][0],r['sign'])]=r['res']=='SAT'
for base in gt:
    j=json.load(open('tools/external/kobon-solutions/gallery/data/17/'+base))
    d=Dp1.from_gens(j['gens'],17)
    br=d.best_by_rank()
    mine=sorted(h for h,v in br.items() if v>=93)
    print(base[:12],d.T0,'mine>=93',mine,'best',sorted(set(br.values())),'| gt+',[r for r in range(18) if gt[base].get((r,1))],'gt-',[r for r in range(18) if gt[base].get((r,-1))])

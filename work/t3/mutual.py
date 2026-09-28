"""Mutual pairs in gallery arrangements with many triple points: for each mutual pair (P,Q),
report the shared line m: #triple points on it, whether some point uses m as axis, whether m is a cap."""
import glob, sys, collections, json
sys.path.insert(0, '.')
from arr import *
from lemmas import point_info
from lemmaD import is_cap_somewhere
R = '../../tools/external/kobon-solutions/gallery/data'
st = collections.Counter()
for s in sys.argv[1:]:
    for f in sorted(glob.glob(f'{R}/{s}/*.json')):
        a = Arr(json.load(open(f))['gens'])
        if any(len(e) > 3 for e in a.events) or len(a.triples) < 5: continue
        info = {P: point_info(a, P) for P in a.triples}
        axes = {P: I['axis'] for P, I in info.items()}
        for P, I in info.items():
            if I['kind'] != 'X': continue
            for k, cap in I['blocks']:
                X = far_end(a, P, I['rays'][k])
                # partner Q: triple point whose block middle ends at X with cap = axis(P)
                for Q, J in info.items():
                    if Q == P or J['kind'] != 'X': continue
                    for kk, cc in J['blocks']:
                        if far_end(a, Q, J['rays'][kk]) == X and cc == axes[P] and P < Q:
                            m = a.events[P] & a.events[Q]
                            if len(m) != 1: st['no shared line?!'] += 1; continue
                            m = next(iter(m))
                            onm = [R_ for R_ in a.triples if m in a.events[R_]]
                            ax_on = any(axes[R_] == m for R_ in onm)
                            cons = abs(a.pos[m][P] - a.pos[m][Q]) == 1
                            st[(a.n, len(a.triples), 'Z', a.Z(), 'j', len(onm), 'axis on m', ax_on, 'm cap', is_cap_somewhere(a, m), 'consec', cons)] += 1
for k, v in sorted(st.items(), key=str): print(v, k)

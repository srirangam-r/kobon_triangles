#!/usr/bin/env python3
"""T=94 probe with triple optimality and the proved necessary W>=12 cut.
UNSAT requires a separate checked proof and encoding audit. UNKNOWN proves nothing.
"""
from pathlib import Path
from itertools import combinations
import argparse
import json
import sys
import threading
import time
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'work/bbl/all8_work/pydeps'),str(ROOT/'work/bbl/all8_work'),str(ROOT/'work/bbl')]
import global_sat as G
import q_probe as Q
import note3_check as N
from pysat.solvers import Solver
from pysat.card import CardEnc,EncType


def augment(B,minimum):
    for t in B.trip:
        exact=B.AND([B.z[t],-B.zp2[t[0],t[1]]])
        ring=G.C.triple_ring(B,t)
        for alt in [ring[::2],ring[1::2]]:
            for i,j in combinations(range(3),2):B.cl.append([-exact,alt[i],alt[j]])
    wedges=[];R=list(range(B.K))
    for p,q in combinations(R,2):
        ex=[]
        for L,M in [(p,q),(q,p)]:
            first=B.AND([B.before(L,M,r) for r in R if r not in [p,q]])
            last=B.AND([B.before(L,r,M) for r in R if r not in [p,q]])
            ex.append(B.OR([first,last]))
        tri=B.OR([B.S[p,q,k] for k in ['pp','qp','mm','pq']])
        wedges.append(B.AND([-B.zp[p,q],tri]+ex))
    if minimum:
        card=CardEnc.atleast(wedges,bound=minimum,top_id=B.nv,encoding=EncType.seqcounter)
        B.cl.extend(card.clauses);B.nv=card.nv
    return wedges


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--seconds',type=int,default=300)
    ap.add_argument('--out',default='work/bbl/all8_work/ends18')
    ap.add_argument('--validate',action='store_true')
    args=ap.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    known=N.extend_right(N.CORE10,10,18) if args.validate else None
    t0=time.time();B=G.build(18,None if known else 94,known)
    wedges=augment(B,0 if known else 12)
    print(json.dumps(dict(event='built',variables=B.nv,clauses=len(B.cl),
                         target_T=None if known else 94,minimum_W=0 if known else 12)),flush=True)
    lazy=0
    with Solver(name='glucose4',bootstrap_with=B.cl) as sv:
        while True:
            left=args.seconds-(time.time()-t0)
            if left<=0:
                result='UNKNOWN';break
            sv.clear_interrupt();timer=threading.Timer(left,sv.interrupt)
            timer.daemon=True;timer.start()
            try:res=sv.solve_limited(expect_interrupt=True)
            finally:timer.cancel()
            if res is None:result='UNKNOWN';break
            if not res:result='UNSAT_UNCERTIFIED';break
            Ms={x for x in sv.get_model() if x>0}
            violations=G.C.pair_violations(B,Ms)
            if violations:
                for v in violations:
                    cl=G.C.violation_clause(B,v);B.cl.append(cl);sv.add_clause(cl)
                lazy+=len(violations)
                print(json.dumps(dict(event='lazy',clauses=lazy)),flush=True)
                continue
            a,word=Q.to_arr(B,Ms)
            assert N.GB.class_check(a)[0] and N.opt_triples(a)
            actual=N.credit_state(a)
            w=sum(x in Ms for x in wedges)
            assert w==actual['W']
            if not known:assert a.T()==94 and a.Z()<=6 and w>=12
            evidence=dict(n=18,T=a.T(),Lambda=actual['C']//2,W=w,credits=actual,gens=word)
            (out/'witness.json').write_text(json.dumps(evidence,indent=2))
            print(json.dumps(dict(event='verified',n=18,T=a.T(),Lambda=actual['C']//2,W=w)),flush=True)
            result='SAT_VERIFIED';break
        summary=dict(result=result,seconds=time.time()-t0,variables=B.nv,clauses=len(B.cl),
                     lazy_clauses=lazy,validation=args.validate,statistics=sv.accum_stats())
    if result=='UNSAT_UNCERTIFIED':
        with (out/'final.cnf').open('w') as f:
            f.write(f'p cnf {B.nv} {len(B.cl)}\n')
            for cl in B.cl:f.write(' '.join(map(str,cl))+' 0\n')
    (out/'result.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary),flush=True)


if __name__=='__main__':main()

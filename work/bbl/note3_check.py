#!/usr/bin/env python3
"""Exact checks for ALL8_NOTE3: I4 payments, end slots, wedges, and corrected parity.
This is not a proof that C>=13 for every 18-line arrangement.
"""
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'work/bbl'), str(ROOT/'work/t3')]
import k1_pay_check as KP
import note2_check as NC
from arr import Arr, rays, first_seg, far_end
BC, GB = NC.BC, NC.GB

CORE10 = '1 0 4 6 7 5* 4 3 1* 3** 6* 8 2 0 7 5* 3* 5 6 7 6 4 2 1 2 3 4 5 6 0'
PARITY12 = ('1 4 6 5 6 4 3 8 10 9 7* 9* 6 4* 6** 5 3 2 3 4 5* '
            '1 0 1 3 2 3 4 5 6* 8* 10 7 8 9 1 8 5* 3 2 3 4 5 6 7 8 3')
ZERO18 = ('3 2 5 4 6 7 8 7 5* 3* 1* 0 11 12 11 10 9 7* 5* 3* 1* 10* 9 13 12 '
          '10* 7** 5* 3* 5 10 15 14 13 12 15 14 15* 13* 11* 9* 6** 4* 2* 0* 2 1 '
          '9 10* 8* 6* 4* 3 2 1 6 5 12* 10* 9 8 7 6 5 4 3 2 5 9 8 7 10 9 14* '
          '12* 11 10 9 8 7 6 7 9 11 16 14* 13 12 14')


def extend_right(gens, n, N):
    return gens+' '+' '.join(str(i) for high in range(n-1,N-1)
                            for i in range(high,-1,-1))


def word_valid(gens, n):
    tracks=list(range(n));pairs=Counter()
    for t in gens.split():
        g=int(t.rstrip('*'));w=2+t.count('*')
        assert 0<=g and g+w<=n
        block=tracks[g:g+w]
        pairs.update(tuple(sorted(p)) for p in combinations(block,2))
        tracks[g:g+w]=reversed(block)
    assert tracks==list(reversed(range(n)))
    assert len(pairs)==n*(n-1)//2 and set(pairs.values())=={1}


def opt_triples(a):
    return all(sum(GB.tri_sectors(a,p)[::2])>=2 and
               sum(GB.tri_sectors(a,p)[1::2])>=2
               for p,e in enumerate(a.events) if len(e)==3)


def ray_token(a,P,r):
    fs=first_seg(a,P,r)
    return (P,fs) if fs is not None else (P,('unbounded',)+r)


def end_data(a):
    out=[]
    for L,row in enumerate(a.rows):
        for d in [-1,1]:
            v=row[0] if d<0 else row[-1]
            u=row[1] if d<0 else row[-2]
            seg=(L,0 if d<0 else len(row)-2)
            rec=dict(L=L,d=d,v=v)
            if len(a.events[v])>=3:
                rec.update(kind='N',token=ray_token(a,v,(L,d)))
            elif len(a.t[seg[0]][seg[1]])==2:
                assert len(a.events[u]) in [3,4]
                rec.update(kind='I'+str(len(a.events[u])),origin=u)
            else:
                M=a.other(v,L);i=a.pos[M][v]
                unused=[(M,j) for j in [i-1,i]
                        if 0<=j<len(a.t[M]) and not a.t[M][j]]
                if unused:
                    rec.update(kind='Z',slot=(unused[0],v))
                else:
                    assert i in [0,len(a.rows[M])-1]
                    assert len(a.t[seg[0]][seg[1]])==1
                    rec.update(kind='W',other=M)
            out.append(rec)
    return out


def credit_state(a):
    costs,ring,_,lam=GB.analyse(a)
    records=BC.block_partition(a)
    at=defaultdict(list)
    for r in records:at[r['far']].append(r)
    tf=defaultdict(list)
    for f in a.tris:
        vertices=NC.tri_vertices(a,f)
        for L,e,_ in f:tf[L,e].append(vertices)
    allN=set()
    for P,s in ring.items():
        m=len(a.events[P]);B={i for i,c in enumerate(s) if c=='B'}
        assert not any(all((i+j)%(2*m) in B for j in range(m-1))
                       for i in range(2*m))
        for i,r in enumerate(rays(a,P)):
            if s[i]=='N':allN.add(ray_token(a,P,r))
    assert len(allN)==sum(s.count('N') for s in ring.values())
    old=KP.claimed_tokens(a)
    assert old<=allN
    k1A=set();caseB=Counter();caseBi=defaultdict(list);kiteq=Counter()
    mixed_tokens=set();mixed_single_caps=0
    for X,rr in at.items():
        if len(rr)!=4:continue
        cs=[far_end(a,X,r) for r in rays(a,X)]
        q=sum(len(a.events[p])==4 for p in cs);kiteq[q]+=1
        if q>=2:
            for u,v in zip(cs,cs[1:]+cs[:1]):
                e=NC.edge(a,u,v)
                if len(a.t[e[0]][e[1]])!=1:continue
                mixed_single_caps+=1
                for p in a.rows[e[0]][e[1]:e[1]+2]:
                    tok=(p,e)
                    assert tok in allN and tok not in old and tok not in mixed_tokens
                    mixed_tokens.add(tok)
        if q!=1:continue
        i=next(i for i,p in enumerate(cs) if len(a.events[p])==4)
        P,Q,R,S=cs[i:]+cs[:i]
        sides=[NC.edge(a,u,v) for u,v in [(P,Q),(P,S),(Q,R),(R,S)]]
        singles=[e for e in sides if len(a.t[e[0]][e[1]])==1]
        if singles:
            e=singles[0]
            for v in a.rows[e[0]][e[1]:e[1]+2]:
                tok=(v,e)
                assert tok in allN and tok not in old and tok not in k1A
                k1A.add(tok)
        else:
            caseB[P]+=1
            k=next(i for i,r in enumerate(rays(a,P)) if far_end(a,P,r)==X)
            caseBi[P].append(k)
            assert all(ring[P][(k+d)%8]!='B' for d in [-2,-1,1,2])
    free=allN-old-k1A
    kiteat=Counter(r['point'] for r in records if len(at[r['far']])==4)
    Scorr={P:8-s.count('B')-kiteat[P]-2*caseB[P]
           for P,s in ring.items() if len(a.events[P])==4}
    assert min(Scorr.values(),default=0)>=0
    for P,S in Scorr.items():
        if S or not all(GB.tri_sectors(a,P)):continue
        d=ring[P].count('B');k=kiteat[P];b=caseB[P]
        assert (d,k,b) in [(4,4,0),(3,3,1),(2,2,2)]
        rs=rays(a,P)
        if b==0:
            assert any(len(a.events[far_end(a,P,r)])==4 for i,r in enumerate(rs)
                       if ring[P][i]=='R')
        if b==1:
            (i,)=caseBi[P]
            q2,q4,q6=[far_end(a,P,rs[(i+j)%8]) for j in [2,4,6]]
            assert len(a.events[q4])==4 or (len(a.events[q2])==len(a.events[q6])==4)
            if not any(Scorr.values()) and not kiteq[3] and not kiteq[4]:
                assert len(a.events[q4])==4
    dec=BC.decomposition(a,records)
    if dec is not None:
        c=(dec['residual2']+len(free)+
           2*sum(r['kind']=='U' and len(a.events[r['point']])==3 for r in records)+
           sum(r['kind']=='I' and len(a.events[r['point']])==3 for r in records)+
           sum(r['kind']=='U' and len(a.events[r['point']])==4 for r in records)+
           sum(Scorr.values())+2*kiteq[3]+4*kiteq[4])
        assert c==2*lam

    def candidate(P,X,T):
        e=NC.edge(a,P,T)
        if len(a.t[e[0]][e[1]])==1:return (P,e)
        assert len(a.t[e[0]][e[1]])==2
        if len(a.events[T])==2:return None
        e=NC.edge(a,T,X)
        assert len(a.t[e[0]][e[1]])==1
        return (T,e)

    extra=set();one={}  # one token for each quad-origin U/I block
    for r in records:
        P,X=r['point'],r['far']
        if len(a.events[P])!=4 or r['kind'] not in ['U','I']:continue
        candidates=[]
        for f in tf[NC.edge(a,P,X)]:
            (T,)=f-{P,X}
            token=candidate(P,X,T)
            if token is not None:candidates.append(token)
        assert len(candidates)>=1
        for token in candidates:
            assert token in free and token not in extra
            extra.add(token)
        one[(P,X)]=candidates[0]
    assert len(set(one.values()))==len(one)
    assert len(mixed_tokens)==2*mixed_single_caps
    assert mixed_tokens<=free and not mixed_tokens.intersection(one.values())

    # Two slots per unused edge. A touch consumes its simple-end slot.
    slots={( (L,e),v) for L in range(a.n) for e,t in enumerate(a.t[L])
           if not t for v in a.rows[L][e:e+2]}
    touchslots=set()
    for r in records:
        if r['kind']=='U':
            slot=(tuple(r['beyond']),r['far'])
            assert slot in slots and slot not in touchslots
            touchslots.add(slot)
    available=slots-touchslots
    ends=end_data(a);usedN=set();usedZ=set();wedges=set();C=2*lam
    for r in ends:
        k=r['kind']
        if k=='N':
            assert r['token'] in free and r['token'] not in extra
            assert r['token'] not in usedN
            usedN.add(r['token'])
        elif k=='I4':
            token=one[(r['origin'],r['v'])]
            assert token not in usedN
            usedN.add(token)
        elif k=='Z':
            assert r['slot'] in available and r['slot'] not in usedZ
            usedZ.add(r['slot'])
        elif k=='W':wedges.add(r['v'])
    ec=Counter(r['kind'] for r in ends)
    assert ec['W']==2*len(wedges)
    U=sum(r['kind']=='U' for r in records)
    S=sum(Scorr.values());bon=2*kiteq[3]+4*kiteq[4]
    end_lower=2*a.n-2*len(wedges)+2*U+S+bon
    remainder=(2*a.Z()-U-ec['Z'])+(len(free)-len(one)-ec['N'])
    emptyN=[(P,e) for P,e in allN if len(e)==2 and not a.t[e[0]][e[1]]]
    for tok in emptyN:
        assert tok in free and tok not in set(one.values())
        assert (tok[1],tok[0]) in available and (tok[1],tok[0]) not in usedZ
    assert remainder>=2*len(emptyN)+2*mixed_single_caps and C==end_lower+remainder
    if remainder==0:
        for X,rr in at.items():
            if len(rr)!=4:continue
            cs=[far_end(a,X,r) for r in rays(a,X)]
            q=sum(len(a.events[p])==4 for p in cs)
            singles=sum(len(a.t[e[0]][e[1]])==1
                        for e in [NC.edge(a,u,v) for u,v in zip(cs,cs[1:]+cs[:1])])
            assert singles==2 if q==0 else singles in [0,1] if q==1 else singles==0
        for f in a.tris:
            if all(len(a.events[v])>=3 for v in NC.tri_vertices(a,f)):
                assert all(len(a.t[L][e])==2 for L,e,_ in f)
    if a.n%2==0:
        # Wedge graph is a union of paths. Verify no cycle by union/find.
        ds=GB.DSU(a.n)
        for v in wedges:
            L,M=tuple(a.events[v])
            assert ds.find(L)!=ds.find(M)
            ds.join(L,M)
        assert len(wedges)<=a.n-1
    # Exact parity for lines whose bounded segments are all singly used.
    npar=0;ncap=0
    for L,row in enumerate(a.rows):
        if not all(len(t)==1 for t in a.t[L]):continue
        if any(len(a.events[v])>=4 for v in row):continue
        if any(len(a.events[v])==3 and
               (sum(GB.tri_sectors(a,v)[::2])<2 or sum(GB.tri_sectors(a,v)[1::2])<2)
               for v in row):continue
        if not all(any(e['L']==L and e['v']==v and e['kind']=='W' for e in ends)
                   for v in [row[0],row[-1]]):continue
        tcount=sum(len(a.events[v])==3 for v in row)
        f=0
        for i,v in enumerate(row[1:-1],1):
            same=a.t[L][i-1]==a.t[L][i]
            if len(a.events[v])==3:
                assert not same
            elif same:
                (b,)= [r for r in records if r['far']==v and r['cap']==L]
                assert b['kind'] in ['U','I']
                f+=1
        assert (tcount+f-(a.n-3))%2==0
        npar+=1;ncap+=f
    return dict(C=C,Z=a.Z(),R2=2*a.Z()-U,Ncirc=len(free),S=S,U=U,
                I4=ec['I4'],U4=sum(r['kind']=='U' and len(a.events[r['point']])==4
                                  for r in records),quad_nonmut_tokens=len(extra),
                W=len(wedges),paths=a.n-len(wedges),end_lower=end_lower,
                end_remainder=remainder,empty_bounded_N=len(emptyN),
                mixed_single_caps=mixed_single_caps,
                end_counts=dict(sorted(ec.items())),parity_lines=npar,
                parity_cap_steps=ncap,K1A=len(k1A)//2,K1B=sum(caseB.values()),Scorr=Scorr)


def examples():
    n18=extend_right(CORE10,10,18);word_valid(n18,18)
    a=Arr(n18,18);good,_=GB.class_check(a)
    assert good and opt_triples(a)
    dec=BC.decomposition(a,BC.block_partition(a))
    assert dec['Q2']==11 and dec['Lambda']==189 and a.T()==33 and a.Z()==184
    cs,ring,comps,lam=GB.analyse(a)
    assert len(comps)==1 and len(comps[0])==6 and sum(cs.values())==5
    print('18-line Q counterexample:',dict(n=18,T=a.T(),Z=a.Z(),Lambda=lam,
          Q2=dec['Q2'],component_cost2=int(2*sum(cs.values())),
          structural_class=good,triple_optimality=opt_triples(a),gens=n18))
    print('18-line example credits:',credit_state(a))
    a=Arr(PARITY12,12);word_valid(PARITY12,12)
    good,_=GB.class_check(a);assert good and opt_triples(a)
    L=7;row=a.rows[L]
    assert all(len(a.events[v])==2 for v in row)
    assert all(len(t)==1 for t in a.t[L])
    es=end_data(a);assert sum(e['L']==L and e['kind']=='W' for e in es)==2
    same=[v for i,v in enumerate(row[1:-1],1) if a.t[L][i-1]==a.t[L][i]]
    assert same==[6]
    (r,)=[r for r in BC.block_partition(a) if r['far']==6 and r['cap']==L]
    assert r['kind']=='I' and len(a.events[r['point']])==3
    print('Even-n perfect-cap parity counterexample:',dict(n=12,T=a.T(),Lambda=120-3*a.T(),
          L=L,labels=[next(iter(t)) for t in a.t[L]],same_side=same,
          cap_origin=r['point'],cap_kind=r['kind'],structural_class=good,
          triple_optimality=opt_triples(a),gens=PARITY12))
    print('12-line example credits:',credit_state(a))
    a=Arr(ZERO18,18);word_valid(ZERO18,18)
    good,_=GB.class_check(a);assert good and opt_triples(a)
    z=credit_state(a)
    assert a.T()==75 and z['C']==126 and z['K1B']==2 and z['Scorr'][41]==0
    assert len(a.events[41])==4 and all(GB.tri_sectors(a,41))
    print('Optimal double-case-B example:',dict(n=18,T=a.T(),Z=a.Z(),Lambda=63,
          P=41,S_at_P=0,S_other=z['S'],case_B=2,structural_class=good,
          triple_optimality=opt_triples(a),gens=ZERO18))


def zero_slack_checks():
    # Exhaustive local masks: this classifies patterns, not realizability.
    shapes=Counter();configs=0
    for mask in range(256):
        B={i for i in range(8) if mask>>i&1}
        if len(B)>5 or any(all((i+j)%8 in B for j in range(3)) for i in range(8)):continue
        eligible=[i for i in B if (i-1)%8 not in B and (i+1)%8 not in B]
        for km in range(1<<len(eligible)):
            K={i for j,i in enumerate(eligible) if km>>j&1}
            possible=[i for i in K if (i-2)%8 not in B and (i+2)%8 not in B]
            for cm in range(1<<len(possible)):
                c=sum(cm>>j&1 for j in range(len(possible)))
                S=8-len(B)-len(K)-2*c
                assert S>=0
                configs+=1
                if S==0:shapes[len(B),len(K),c]+=1
    assert set(shapes)=={(4,4,0),(3,3,1),(2,2,2)}
    print('Zero-slack local enumeration:',dict(configurations=configs,
          shapes={str(k):v for k,v in sorted(shapes.items())},failures=0))
    ls=[(1,0,0),(0,1,0),(1,-1,0),(1,1,0),(1,0,-1),(1,0,1),
        (2,1,-3),(-2,1,-3),(2,1,3),(-2,1,3),(0,1,5)]
    ls=NC.transform(ls,NC.F(1,97),NC.F(1,89))
    ls=[(a,b-a/NC.F(37),c) for a,b,c in ls]
    g,_=NC.to_gens(ls);a=Arr(g,11);word_valid(g,11)
    assert GB.class_check(a)[0] and not opt_triples(a)
    z=credit_state(a)
    assert z['K1B']==2 and z['S']==0
    print('Double-case-B geometric example:',dict(n=11,T=a.T(),Z=a.Z(),Lambda=z['C']//2,
          S_corrected=z['S'],case_B=z['K1B'],structural_class=True,
          triple_optimality=False,gens=g))


def main():
    zero_slack_checks()
    examples()
    count=Counter();seen=set()
    for name in sys.argv[1:]:
        for s in Path(name).open():
            d=json.loads(s);g=d['gens']
            if g in seen:continue
            seen.add(g);a=Arr(g,d.get('n',18))
            if max(map(len,a.events))>4:continue
            z=credit_state(a)
            count['arrangements']+=1
            for key in ['quad_nonmut_tokens','I4','U4','W','empty_bounded_N','mixed_single_caps','parity_lines','parity_cap_steps','K1A','K1B']:
                count[key]+=z[key]
    print('Dataset checks:',dict(sorted(count.items())),'failures=0')


if __name__=='__main__':main()

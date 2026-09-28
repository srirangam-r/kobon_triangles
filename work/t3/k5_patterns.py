"""Emit the k=5, beta=0, B=10, clean<=1, K=4 end patterns (C31) with roles, in the solver's
convention: position l = left (first) end of label l, l+18 = right (last) end of label l;
circle L0..L17, R0..R17.  Line 0 is WLOG a non-triple line other than the touch line, so
positions 0 and 18 are wedges.

Each output row: N (6 non-wedge positions), t (touch end), s0 (U0's singleton, cd(s0,t)=5),
match (2 pairs of the other 4 singletons, cd <= 5), wedges (pairs of cyclically adjacent
positions), and the implied units:
  wedge (p,q): end(p, line(q)) and end(q, line(p))  [c17f if position < 18 else c17l]
  singleton p (line l=p%18, end e = first if p<18 else last): l's 2nd vertex from e is triple,
     l's 1st vertex simple (C26 (a)); l's 3rd vertex from e simple (cap point)
  t (line l_t): l_t's end vertex Y lies on a_{U0} = line(s0), and the segment of a_{U0} from
     its 3rd vertex X (from the s0 end) to Y is the unique slack pair (u0); Y = 4th vertex of
     a_{U0} from the s0 end.
  match pairs (p,p'): mutual pair; line(p) ∩ line(p') is the 3rd vertex of both from their
     singleton ends (C26 (c)).
    python3 work/t3/k5_patterns.py > k5_patterns.jsonl
"""
import json
import sys
from itertools import combinations
sys.path.insert(0, '/home/nail/stuff/sundai_math/search')
from wedge_cubes import wedges

def cd(a, b):
    d = abs(a - b) % 36
    return min(d, 36 - d)

def matchings(S, test):
    S = list(S)
    if not S:
        yield []
        return
    a = S[0]
    for i in range(1, len(S)):
        if test(a, S[i]):
            for m in matchings(S[1:i] + S[i + 1:], test):
                yield [(a, S[i])] + m

rows = 0
for N in combinations([p for p in range(36) if p not in (0, 18)], 6):
    W = wedges(N)
    if W is None:
        continue
    for t in N:
        for s0 in N:
            if s0 == t or cd(s0, t) != 5 or s0 % 18 == t % 18:
                continue
            rest = [x for x in N if x not in (t, s0)]
            for m in matchings(rest, lambda a, b: cd(a, b) <= 5 and a % 18 != b % 18):
                print(json.dumps({"N": list(N), "t": t, "s0": s0, "match": m, "wedges": W}))
                rows += 1
print(f"# rows: {rows}", file=sys.stderr)

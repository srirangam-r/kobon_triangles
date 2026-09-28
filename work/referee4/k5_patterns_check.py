"""Referee4: independent regeneration of work/t3/k5_patterns.jsonl (own admissibility + matching code)."""
import json
from itertools import combinations
N36 = 36
cd = lambda a, b: min((a - b) % N36, (b - a) % N36)
def wedge_pairs(S):
    S = sorted(S); pairs = []
    for i, a in enumerate(S):
        b = S[(i + 1) % len(S)] + (N36 if i + 1 == len(S) else 0)
        run = [p % N36 for p in range(a + 1, b)]
        if len(run) % 2: return None
        pairs += [(run[j], run[j + 1]) for j in range(0, len(run), 2)]
    part = {}
    for p, q in pairs: part[p], part[q] = q % 18, p % 18
    for l in range(18):
        if l in part and l + 18 in part and part[l] == part[l + 18]: return None
    return pairs
def matchings(S, ok):
    if not S: yield []; return
    a = S[0]
    for i in range(1, len(S)):
        if ok(a, S[i]):
            for m in matchings(S[1:i] + S[i+1:], ok): yield [(a, S[i])] + m
mine = set()
for N in combinations([p for p in range(N36) if p not in (0, 18)], 6):
    W = wedge_pairs(N)
    if W is None: continue
    for t in N:
        for s0 in N:
            if s0 == t or cd(s0, t) != 5 or s0 % 18 == t % 18: continue
            rest = [x for x in N if x not in (t, s0)]
            for m in matchings(rest, lambda a, b: cd(a, b) <= 5 and a % 18 != b % 18):
                mine.add((N, t, s0, tuple(tuple(p) for p in m), tuple(W)))
theirs = set()
for l in open('/home/nail/stuff/sundai_math/work/t3/k5_patterns.jsonl'):
    r = json.loads(l)
    theirs.add((tuple(r['N']), r['t'], r['s0'], tuple(tuple(p) for p in r['match']), tuple(tuple(p) for p in r['wedges'])))
print('mine', len(mine), 'theirs', len(theirs), 'equal', mine == theirs, 'distinct N', len({x[0] for x in mine}))
print('rows with wedge (0,1) (trivially UNSAT under chi(0,1,2) != -1):', sum(1 for x in mine if (0, 1) in x[4]))

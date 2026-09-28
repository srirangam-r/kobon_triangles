"""k=5, beta=0, B=10 (Z=1) line-end patterns (C30/C31).  N = non-wedge end positions (6 of 36).
clean=2: 4 singletons perfectly matched at cyclic distance exactly 5 + 2 cyclically adjacent touch ends.
clean<=1: 5 singletons + 1 touch end t; one singleton s0 at distance exactly 5 from t; the other
4 singletons perfectly matched at distance <= 5."""
from itertools import combinations
import sys
sys.path.insert(0, '.')
from wedges import admissible
def cd(a, b):
    d = abs(a - b) % 36
    return min(d, 36 - d)
def pm(S, test):
    S = list(S)
    if not S: return True
    a = S[0]
    return any(test(a, S[i]) and pm(S[1:i] + S[i + 1:], test) for i in range(1, len(S)))
c2 = c1 = tot = 0
ex2 = ex1 = None
for N in combinations(range(36), 6):
    if not admissible(N): continue
    tot += 1
    ok2 = False
    for t1, t2 in combinations(N, 2):
        if cd(t1, t2) == 1:
            rest = [x for x in N if x not in (t1, t2)]
            if pm(rest, lambda a, b: cd(a, b) == 5): ok2 = True; break
    ok1 = False
    for t in N:
        for s0 in N:
            if s0 != t and cd(s0, t) == 5:
                rest = [x for x in N if x not in (t, s0)]
                if pm(rest, lambda a, b: cd(a, b) <= 5): ok1 = True; break
        if ok1: break
    c2 += ok2; c1 += ok1
    if ok2 and ex2 is None: ex2 = N
    if ok1 and ex1 is None: ex1 = N
print('admissible |N|=6 sets:', tot, '| clean=2 pattern:', c2, ex2, '| clean<=1 pattern:', c1, ex1)

# variant: all distances exactly 5 (if C27 is exact in this setting)
c1x = 0
for N in combinations(range(36), 6):
    if not admissible(N): continue
    ok = False
    for t in N:
        for s0 in N:
            if s0 != t and cd(s0, t) == 5:
                rest = [x for x in N if x not in (t, s0)]
                if pm(rest, lambda a, b: cd(a, b) == 5): ok = True
    c1x += ok
print('clean<=1 with exact-5 matching:', c1x)

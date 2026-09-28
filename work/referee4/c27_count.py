"""Referee4: recount C27's (A) pruning. Admissibility as in work/t3/wedges.py; singletons avoid
positions 0 and 18 (line 0 is off all triple points in k6z); a perfect matching of the 6
singletons with every pair at cyclic distance <= 5 (on the 36-cycle) is required.
Also report the count if the matched pair must additionally have an even number of ends
strictly between on the short side (automatic when no singleton lies between)."""
import sys
from itertools import combinations
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/t3')
import importlib.util
spec = importlib.util.spec_from_file_location('w', '/home/nail/stuff/sundai_math/work/t3/wedges.py')
src = open('/home/nail/stuff/sundai_math/work/t3/wedges.py').read().split('for size in')[0]
ns = {}; exec(src, ns); admissible = ns['admissible']
N = 36
def cd(a, b):
    d = abs(a - b) % N
    return min(d, N - d)
def matchings(S):
    if not S:
        yield []
        return
    a = S[0]
    for i in range(1, len(S)):
        b = S[i]
        rest = S[1:i] + S[i + 1:]
        for m in matchings(rest):
            yield [(a, b)] + m
tot = 0; ok = 0; ok_strict = 0; examples = []
for S in combinations([p for p in range(N) if p not in (0, 18)], 6):
    if not admissible(S):
        continue
    tot += 1
    good = [m for m in matchings(list(S)) if all(cd(a, b) <= 5 for a, b in m)]
    if good:
        ok += 1
        if len(examples) < 3: examples.append((S, good[0]))
    # stricter: also no two matched ends on the same line (automatic) -- and distance <= 5 on the
    # side that is the sector arc; either side allowed here
print('admissible u=6 sets (0,18 excluded):', tot)
print('with a perfect matching at cyclic distance <= 5:', ok)
print('examples', examples)

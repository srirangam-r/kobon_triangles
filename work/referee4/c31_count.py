"""Referee4: independent re-count for C31 (own matching code; wedges.admissible reused)."""
from itertools import combinations, permutations
src = open('/home/nail/stuff/sundai_math/work/t3/wedges.py').read().split('for size in')[0]
ns = {}; exec(src, ns); adm = ns['admissible']
cd = lambda a, b: min((a - b) % 36, (b - a) % 36)
def perfect(S, ok):
    S = list(S)
    if not S: return True
    return any(ok(S[0], S[i]) and perfect(S[1:i] + S[i+1:], ok) for i in range(1, len(S)))
tot = c2 = c1 = c1x = 0; c1_excl = 0
for N in combinations(range(36), 6):
    if not adm(N): continue
    tot += 1
    if any(cd(a, b) == 1 and perfect([x for x in N if x not in (a, b)], lambda p, q: cd(p, q) == 5) for a, b in combinations(N, 2)):
        c2 += 1
    ok1 = any(cd(t, s) == 5 and perfect([x for x in N if x not in (t, s)], lambda p, q: cd(p, q) <= 5) for t, s in permutations(N, 2))
    c1 += ok1
    if ok1 and 0 not in N and 18 not in N: c1_excl += 1
print('admissible 6-sets', tot, 'clean=2 patterns', c2, 'clean<=1 patterns', c1, '(of which avoiding 0/18:', c1_excl, ')')

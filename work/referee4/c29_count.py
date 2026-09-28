"""Referee4: re-run C29's enumeration.  u = 4 admissible singleton sets (work/t3/wedges.py rules),
with and without positions 0/18 excluded; count those with a perfect matching into two pairs at
cyclic distance <= 5, == 5, and (for comparison) any distance on different lines."""
from itertools import combinations
src = open('/home/nail/stuff/sundai_math/work/t3/wedges.py').read().split('for size in')[0]
ns = {}; exec(src, ns); adm = ns['admissible']
N = 36
cd = lambda a, b: min((a - b) % N, (b - a) % N)
def pm(S, ok):
    a, b, c, d = S
    return any(ok(x, y) and ok(u, v) for (x, y), (u, v) in (((a, b), (c, d)), ((a, c), (b, d)), ((a, d), (b, c))))
for excl in (False, True):
    pos = [p for p in range(N) if not (excl and p in (0, 18))]
    sets = [S for S in combinations(pos, 4) if adm(S)]
    le5 = [S for S in sets if pm(S, lambda x, y: cd(x, y) <= 5)]
    eq5 = [S for S in sets if pm(S, lambda x, y: cd(x, y) == 5)]
    dist = sorted({cd(x, y) for S in sets for x, y in combinations(S, 2)})
    print(f'exclude 0/18={excl}: admissible {len(sets)}, matchable at <=5: {len(le5)}, at ==5: {len(eq5)}; pair distances occurring: {dist[:12]}')
    mind = min(min(cd(x, y) for x, y in combinations(S, 2)) for S in sets)
    print('   min pairwise distance over all admissible sets:', mind)

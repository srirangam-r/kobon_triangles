"""C17 check: Z=0 structure at infinity.  36 ray positions on a cycle (0..17 left ends, 18..35
right ends; line l owns positions l and l+18).  Singletons S (cap-point ends), every other
position paired with a cyclic neighbour (wedge).  A line with both ends paired must have its
two wedge partners distinct (it meets each line once): so the two ends pair in opposite
directions.  Count admissible S of each size."""
from itertools import combinations
import sys
def admissible(S, N=36):
    S = sorted(S)
    if not S:
        return False
    # runs between singletons must have even length
    for a, b in zip(S, S[1:] + [S[0] + N]):
        if (b - a - 1) % 2:
            return False
    Sset = set(S)
    dirn = {}
    for i, a in enumerate(S):
        b = S[(i + 1) % len(S)] + (N if i + 1 == len(S) else 0)
        for k, p in enumerate(range(a + 1, b)):
            dirn[p % N] = 'F' if k % 2 == 0 else 'B'
    for l in range(N // 2):
        if l in dirn and l + N // 2 in dirn and dirn[l] == dirn[l + N // 2]:
            return False
    return True
for size in map(int, sys.argv[1:]):
    cnt = 0; ex = None
    for S in combinations(range(36), size):
        if admissible(S):
            cnt += 1; ex = ex or S
    print('size', size, 'admissible', cnt, 'example', ex)

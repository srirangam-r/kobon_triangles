"""Orbit representatives of 4-subsets of the slope labels Z_18 under the dihedral group of label permutations
(label i -> +-i + s mod 18; exactly the permutation part of search/symmetry.py actions)."""
from itertools import combinations
N = 18
def orbit_reps():
    seen = {}; reps = []
    for q in combinations(range(N), 4):
        if q in seen: continue
        orb = set()
        for sgn in (1, -1):
            for s in range(N):
                orb.add(tuple(sorted((sgn*x + s) % N for x in q)))
        for o in orb: seen[o] = len(reps)
        reps.append((q, len(orb)))
    return reps
if __name__ == '__main__':
    r = orbit_reps(); print(len(r), sum(x[1] for x in r)); print(r[:10])

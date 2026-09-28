"""Exact symmetries of slope-labelled, pairwise-intersecting arrangements.

Ends are L0,...,L(n-1),R0,...,R(n-1), cyclically. `start` chooses
new L0; `mirror` reverses the circle; `orientation=-1` additionally
reverses all ends (a half-turn). Thus the requested 8n parameter choices
have only 4n distinct actions: orientation duplicates start+n.
No geometry, floating point, or realizability assumption is needed.
"""
from dataclasses import dataclass
from itertools import combinations, product


@dataclass(frozen=True)
class Action:
    start: int = 0
    orientation: int = 1
    mirror: bool = False

    def ends(self, n):
        if self.orientation not in (-1, 1):
            raise ValueError("orientation must be +1 or -1")
        step = -1 if self.mirror else 1
        return tuple((self.start + step * i + (n if self.orientation == -1 else 0)) % (2*n)
                     for i in range(n))

    def permutation(self, n):
        """New label -> old label."""
        return tuple(e % n for e in self.ends(n))

    def signed_map(self, n):
        """new chi[t] = factor * old chi[source], with sorted source."""
        ends = self.ends(n)
        out = {}
        for t in combinations(range(n), 3):
            src = tuple(ends[i] % n for i in t)
            inversions = sum(src[i] > src[j] for i in range(3) for j in range(i+1, 3))
            flips = sum(ends[i] >= n for i in t)
            factor = -1 if (inversions + flips) % 2 else 1
            out[t] = (tuple(sorted(src)), factor)
        return out

    def apply(self, chi, n):
        return {t: factor * chi[src] for t, (src, factor) in self.signed_map(n).items()}


def actions(n, *, fixed_line0=False, unique=True):
    """All parameter choices, or distinct actions (default).

    fixed_line0 selects the subgroup preserving the *unoriented* line 0.
    It preserves off-triple/defect-free conditions, not a chosen end of 0.
    """
    if n < 3:
        raise ValueError("at least three lines required")
    seen = set()
    for start, orientation, mirror in product(range(2*n), (1, -1), (False, True)):
        g = Action(start, orientation, mirror)
        ends = g.ends(n)
        if fixed_line0 and ends[0] % n != 0:
            continue
        key = (ends, mirror)
        if unique and key in seen:
            continue
        seen.add(key)
        yield g


def transform(chi, n, start=0, orientation=1, mirror=False):
    return Action(start, orientation, mirror).apply(chi, n)

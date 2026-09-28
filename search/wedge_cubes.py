"""Cubes on the structure at infinity for k6z2 (C16 + C17).

36 ray ends on the circle at infinity: position l is the left end of line l, position l + 18 its right
end (labels = left order, top to bottom, so the circle reads L0..L17, R0..R17). Under k = 6, beta = 0,
Z = 0, every line end is either a cap-point end (a singleton, u of them, u in {4, 6} by C16) or a
wedge with a cyclic neighbour (C17). Choosing the singleton set S fixes every wedge, so the admissible
S cover the whole instance. Line 0 avoids every triple point, so positions 0 and 18 are never singletons.
Each cube is the unit clauses end(L, R) for every wedge: c17f for a left (first) end, c17l for a right (last) end.

    python3 search/wedge_cubes.py <spec.json> <out.jsonl>
"""
import json
import sys
from itertools import combinations

N = 36


def wedges(S):
    """Pairs of cyclically adjacent positions forced by singleton set S, or None if S is inadmissible."""
    S = sorted(S)
    pairs = []
    for i, a in enumerate(S):
        b = S[(i + 1) % len(S)] + (N if i + 1 == len(S) else 0)
        run = [p % N for p in range(a + 1, b)]
        if len(run) % 2:
            return None
        pairs += [(run[j], run[j + 1]) for j in range(0, len(run), 2)]
    partner = {}
    for p, q in pairs:
        partner[p], partner[q] = q % 18, p % 18
    for l in range(18):  # a line meets each other line once: its two wedge partners differ
        if l in partner and l + 18 in partner and partner[l] == partner[l + 18]:
            return None
    return pairs


def main(spec_path, out):
    spec = json.load(open(spec_path))
    f, g = spec["c17f"], spec["c17l"]
    end = lambda p, other: (f if p < 18 else g)[f"{p % 18},{other}"]
    n = 0
    with open(out, "w") as fh:
        for u in (4, 6):
            for S in combinations([p for p in range(N) if p not in (0, 18)], u):
                pairs = wedges(S)
                if pairs is None:
                    continue
                lits = []
                for p, q in pairs:
                    lits += [end(p, q % 18), end(q, p % 18)]
                fh.write(json.dumps({"u": u, "S": list(S), "units": lits}) + "\n")
                n += 1
    print(f"{n} cubes -> {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])

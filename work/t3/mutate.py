"""Random local moves on pseudoline arrangements (local-sequence form) + re-sweep to a word.

Moves: triangle flip (Reidemeister III through a triangular face), collapse a triangular
face to a triple point, expand a triple point to a triangle (either orientation).
"""
import random, sys
sys.path.insert(0, '.')
from arr import Arr


def local_sequences(a):
    """seq[L] = list of frozensets (the lines through each vertex of L, including L)."""
    return [[a.events[e] for e in a.rows[L]] for L in range(a.n)]


def sweep(seqs, n):
    """Rebuild a wiring word from local sequences; None if impossible."""
    wires = list(range(n))
    ptr = [0] * n
    toks = []
    total = sum(len(s) for s in seqs)
    done = 0
    while True:
        progress = False
        for g in range(n - 1):
            L = wires[g]
            if ptr[L] >= len(seqs[L]):
                continue
            pt = seqs[L][ptr[L]]
            w = len(pt)
            block = wires[g:g + w]
            if set(block) != pt:
                continue
            if any(ptr[x] >= len(seqs[x]) or seqs[x][ptr[x]] != pt for x in block):
                continue
            if block != sorted(block):
                return None
            toks.append(str(g) + '*' * (w - 2))
            for x in block:
                ptr[x] += 1
            wires[g:g + w] = list(reversed(block))
            done += w
            progress = True
            break
        if not progress:
            break
    if done != total:
        return None
    return ' '.join(toks)


def tri_vertices(a, f):
    vs = set()
    for x, e, _ in f:
        vs |= {a.rows[x][e], a.rows[x][e + 1]}
    return vs


def flip(a, f):
    """Reidemeister III on a triangular face with 3 simple vertices."""
    vs = tri_vertices(a, f)
    if any(len(a.events[v]) != 2 for v in vs):
        return None
    seqs = local_sequences(a)
    for x, e, _ in f:
        seqs[x][e], seqs[x][e + 1] = seqs[x][e + 1], seqs[x][e]
    return sweep(seqs, a.n)


def collapse(a, f):
    vs = tri_vertices(a, f)
    if any(len(a.events[v]) != 2 for v in vs):
        return None
    lines = frozenset().union(*[a.events[v] for v in vs])
    seqs = local_sequences(a)
    for x, e, _ in f:
        seqs[x][e:e + 2] = [lines]
    return sweep(seqs, a.n)


def push_through(a, P, w):
    """move line w through the multiple point P (lines S): allowed when w's crossings with S are consecutive on w and
    each of them is adjacent to P on its line of S. The result has the point S + {w}. None if not allowed."""
    S = a.events[P]
    if w in S:
        return None
    seqs = local_sequences(a)
    cr = {frozenset((w, s)) for s in S}
    idx = [i for i, pt in enumerate(seqs[w]) if pt in cr]
    if len(idx) != len(S) or max(idx) - min(idx) != len(S) - 1:
        return None
    for s in S:
        i, j = seqs[s].index(S), seqs[s].index(frozenset((w, s)))
        if abs(i - j) != 1:
            return None
    new = S | {w}
    seqs[w][min(idx):max(idx) + 1] = [new]
    for s in S:
        seqs[s] = [new if pt == S else pt for pt in seqs[s] if pt != frozenset((w, s))]
    return sweep(seqs, a.n)


def expand(a, P, orient):
    """Split triple point P into a small triangle; orient in {0,1} picks which way."""
    A, B, C = sorted(a.events[P])
    seqs = local_sequences(a)
    # around P on each line: order of the two new crossings; two consistent choices
    # (the middle line B's two crossings get swapped relative to the outer ones)
    ab, ac, bc = frozenset((A, B)), frozenset((A, C)), frozenset((B, C))
    choice = {
        0: {A: [ab, ac], B: [ab, bc], C: [ac, bc]},
        1: {A: [ac, ab], B: [bc, ab], C: [bc, ac]},
    }[orient]
    for x in (A, B, C):
        i = seqs[x].index(a.events[P])
        seqs[x][i:i + 1] = choice[x]
    return sweep(seqs, a.n)


def random_move(a, rng, p_collapse=0.3, p_expand=0.2):
    r = rng.random()
    if r < p_expand and a.triples:
        P = rng.choice(a.triples)
        return expand(a, P, rng.randrange(2))
    tris = [f for f in a.tris if all(len(a.events[v]) == 2 for v in tri_vertices(a, f))]
    if not tris:
        return None
    f = rng.choice(tris)
    if r < p_expand + p_collapse:
        return collapse(a, f)
    return flip(a, f)


if __name__ == '__main__':
    import json
    d = json.load(open(sys.argv[1]))
    a = Arr(d['gens'])
    w = sweep(local_sequences(a), a.n)
    b = Arr(w)
    print('resweep T', a.T(), b.T())
    rng = random.Random(1)
    for it in range(20):
        w = random_move(a, rng)
        if w is None:
            continue
        a = Arr(w, a.n)
        print(it, 'T', a.T(), 'k', len(a.triples))

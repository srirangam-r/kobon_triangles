# Local rearrangement lemma in a window: a partial wiring diagram on k tracks whose events are w0.
# Enumerate every reduced word (multi-crossing letters allowed) with the same crossing set, and compute
# for each boundary face f its number of window vertices in_f, plus the local bounded triangles.
# Boundary faces: top (gap 0, through), bottom (gap k, through), and for each internal gap j a left face
# (open at the left boundary) and a right face (open at the right boundary) -- assuming every internal gap
# is crossed by some wire (asserted).
import itertools
from functools import lru_cache

def apply(perm, i, j):
    return perm[:i] + tuple(reversed(perm[i:j+1])) + perm[j+1:]

def crossing_set(k, w):
    perm = tuple(range(k)); S = set()
    for (i, j) in w:
        blk = perm[i:j+1]
        for a, b in itertools.combinations(blk, 2):
            p = (min(a, b), max(a, b)); assert p not in S; S.add(p)
        perm = apply(perm, i, j)
    return frozenset(S), perm

def all_words(k, req):
    out = []
    def rec(perm, done, w):
        if len(done) == len(req):
            out.append(tuple(w)); return
        for i in range(k):
            for j in range(i+1, k):
                blk = perm[i:j+1]
                pairs = [(min(a, b), max(a, b)) for a, b in itertools.combinations(blk, 2)]
                if any(p in done or p not in req for p in pairs): continue
                rec(apply(perm, i, j), done | set(pairs), w + [(i, j)])
    rec(tuple(range(k)), frozenset(), [])
    return out

def faces(k, w):
    """returns (vec, tloc, nv, inc) where vec = in-counts of boundary faces in fixed order
    [top, bottom, left_1..left_{k-1}, right_1..right_{k-1}], inc[event] = list of boundary-face indices
    incident to that event (for sector bookkeeping)."""
    cnt = [0]*(k+1); state = ['L']*(k+1)   # 'L' = left-open face, 'I' = internal (started at vertex)
    members = [[] for _ in range(k+1)]     # events on the boundary of the current face in gap g
    left = {}; tloc = 0; inc = [[] for _ in w]; internal_faces = []
    for ev, (i, j) in enumerate(w):
        for g in range(i+1, j+1):
            members[g].append(ev)
            if state[g] == 'L':
                left[g] = (cnt[g] + 1, list(members[g]))    # +1: the closing vertex itself
            else:
                if cnt[g] + 2 == 3: tloc += 1           # start vertex + inner vertices + closing vertex
                internal_faces.append(list(members[g]))
            cnt[g] = 0; state[g] = 'I'; members[g] = [ev]
        for g in (i, j+1):
            cnt[g] += 1; members[g].append(ev)
    top = (cnt[0], members[0]); bot = (cnt[k], members[k])
    for g in range(1, k):
        assert state[g] == 'I', "gap not crossed"
    right = [(cnt[g] + 1, members[g]) for g in range(1, k)]   # +1: start vertex
    lefts = [left[g] for g in range(1, k)]
    allf = [top, bot] + lefts + right
    vec = tuple(c for c, _ in allf)
    for fi, (c, mem) in enumerate(allf):
        for ev in set(mem): inc[ev].append(fi)
    return vec, tloc, len(w), inc

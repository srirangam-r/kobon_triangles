# Perturbation lemma: replace an m-fold point P by a local arrangement (wiring word of w0 in S_m
# with multi-crossing letters). For each local arrangement compute:
#   e[s]  = extra edges added to the face in sector s of P (2m sectors, cyclic order)
#   tloc  = local bounded triangles.
# Then Delta T = tloc - #{s in Tri : e[s] > 0}.
import sys, itertools
from functools import lru_cache

def words(m):
    """All wiring words: sequences of (i,j) block reversals of tracks i..j (j>=i+1), each pair crossing once,
    ending at full reversal, excluding the single letter (0,m-1)."""
    out = []
    start = tuple(range(m))
    def rec(perm, crossed, w):
        if len(crossed) == m*(m-1)//2:
            out.append(tuple(w)); return
        for i in range(m):
            for j in range(i+1, m):
                blk = perm[i:j+1]
                pairs = [(min(a,b),max(a,b)) for a,b in itertools.combinations(blk,2)]
                if any(p in crossed for p in pairs): continue
                # block must be in increasing wire order relative to start orientation (each pair uncrossed)
                np_ = perm[:i] + tuple(reversed(blk)) + perm[j+1:]
                rec(np_, crossed | set(pairs), w + [(i,j)])
    rec(start, frozenset(), [])
    return [w for w in out if w != ((0,m-1),)]

def faces(m, w):
    # gap g in 0..m ; gap 0 = top, gap m = bottom
    cnt = [0]*(m+1)
    left_open = [True]*(m+1)
    closed_left = {}   # gap -> extra count of left-open face in that gap (closed at a vertex)
    tloc = 0; maxmult = 0
    for (i,j) in w:
        maxmult = max(maxmult, j-i+1)
        for g in range(i+1, j+1):          # internal gaps close
            if left_open[g]:
                closed_left[g] = cnt[g]
            else:
                if cnt[g] == 1: tloc += 1
            cnt[g] = 0; left_open[g] = False
        cnt[i] += 1          # gap above top track of event (lower boundary)
        cnt[j+1] += 1        # gap below bottom track (upper boundary)
    # right ends: gaps 1..m-1 are right-open faces (started at a vertex)
    e_top = cnt[0] - 1; e_bot = cnt[m] - 1
    right = [cnt[g] for g in range(1, m)]
    left = [closed_left[g] for g in range(1, m)]
    # cyclic sector order: top, right gaps 1..m-1, bottom, left gaps m-1..1
    e = [e_top] + right + [e_bot] + left[::-1]
    return tuple(e), tloc, maxmult

def analyse(m):
    ws = words(m)
    opts = set(faces(m, w) for w in ws)
    print(f"m={m}: {len(ws)} words, {len(opts)} distinct (e, tloc, maxmult)")
    for o in sorted(opts, key=lambda o:(o[2], -o[1])):
        print("  ", o)
    # classify all Tri patterns
    bad = {}
    for mask in range(1 << (2*m)):
        tri = [(mask >> s) & 1 for s in range(2*m)]
        best = max(t - sum(1 for s in range(2*m) if tri[s] and e[s] > 0) for (e, t, mm) in opts)
        bad[mask] = best
    return opts, bad

if __name__ == "__main__":
    m = int(sys.argv[1])
    opts, bad = analyse(m)
    from collections import Counter
    print("best Delta T distribution over 2^(2m) sector patterns:", Counter(bad.values()))
    neg = [mask for mask, b in bad.items() if b < 0]
    def canon(mask):
        n2 = 2*m; best = None
        for r in range(n2):
            for refl in (False, True):
                bits = [(mask >> ((r + (s if not refl else -s)) % n2)) & 1 for s in range(n2)]
                t = tuple(bits); best = t if best is None or t > best else best
        return best
    cl = sorted(set(canon(x) for x in neg))
    print("patterns with every perturbation losing (up to dihedral):")
    for c in cl:
        mask = sum(b << s for s, b in enumerate(c))
        print("  tri bits", ''.join(map(str, c)), " #tri", sum(c), " best dT", bad[mask])

# Window outcome enumerator by memoised DP over sweep states (replaces the exponential all_words for larger windows).
# Same conventions as work/eng/pert2/window.py: k tracks, a word = list of blocks (i, j) reversing tracks i..j.
# Outcome of a word = (vec, tloc, nv): vec = window-vertex counts of the 2k boundary faces in the order
# [top, bottom, left_1..left_{k-1}, right_1..right_{k-1}] (capped at CAP), tloc = number of closed internal faces
# with exactly 3 vertices, nv = number of events.  All words with the crossing set req are enumerated implicitly.
import itertools, sys
from functools import lru_cache
sys.path.insert(0, "/home/nail/stuff/sundai_math/work/eng/pert2")
CAP = 4

def outcomes(k, req):
    req = frozenset(req)
    total = len(req)
    sys.setrecursionlimit(100000)
    @lru_cache(maxsize=None)
    def f(perm, cnt, crossed, lefts, ndone):
        """set of (vec_tail, tloc, nv) reachable from this state; vec = (top, bottom, lefts..., rights...)"""
        if ndone == total:
            if not all(crossed[1:k]):
                return frozenset()
            right = tuple(min(cnt[g] + 1, CAP) for g in range(1, k))
            vec = (cnt[0], cnt[k]) + lefts + right
            return frozenset({(vec, 0, 0)})
        out = set()
        for i in range(k):
            for j in range(i + 1, k):
                blk = perm[i:j + 1]
                pairs = [(min(a, b), max(a, b)) for a, b in itertools.combinations(blk, 2)]
                if any(p not in req for p in pairs):
                    break                     # a larger block containing this one also contains the bad pair
                # pairs already crossed?  perm order: a pair crossed iff it is inverted
                if any((blk[x] > blk[y]) for x in range(len(blk)) for y in range(x + 1, len(blk))):
                    break
                np_ = perm[:i] + tuple(reversed(blk)) + perm[j + 1:]
                c = list(cnt); cr = list(crossed); lf = list(lefts); t = 0
                for g in range(i + 1, j + 1):
                    if not cr[g]:
                        lf[g - 1] = min(c[g] + 1, CAP)
                    else:
                        if c[g] + 2 == 3:
                            t += 1
                    c[g] = 0; cr[g] = True
                for g in (i, j + 1):
                    c[g] = min(c[g] + 1, CAP)
                for (vec, tl, nv) in f(np_, tuple(c), tuple(cr), tuple(lf), ndone + len(pairs)):
                    out.add((vec, tl + t, nv + 1))
        return frozenset(out)
    k1 = k - 1
    return f(tuple(range(k)), (0,) * (k + 1), (False,) * (k + 1), (None,) * k1, 0)

if __name__ == "__main__":
    from window import crossing_set, all_words, faces
    for k, w0 in ((4, [(0, 3)]), (5, [(0, 4)]), (6, [(2, 5), (0, 2)]), (5, [(1, 4), (0, 1)])):
        req, _ = crossing_set(k, w0)
        ref = set()
        for w in all_words(k, req):
            v, t, nv, _ = faces(k, list(w))
            ref.add((tuple(min(x, CAP) for x in v), t, nv))
        got = set(outcomes(k, req))
        print(k, w0, "ref", len(ref), "dp", len(got), "equal", ref == got)

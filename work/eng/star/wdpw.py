# DP window enumerator that also returns one representative word per outcome (vec, tloc, nv).
import itertools, sys
from functools import lru_cache
CAP = 4

def outcomes_w(k, req):
    req = frozenset(req); total = len(req)
    sys.setrecursionlimit(100000)
    @lru_cache(maxsize=None)
    def f(perm, cnt, crossed, lefts, ndone):
        if ndone == total:
            if not all(crossed[1:k]): return {}
            right = tuple(min(cnt[g] + 1, CAP) for g in range(1, k))
            return {((cnt[0], cnt[k]) + lefts + right, 0, 0): ()}
        out = {}
        for i in range(k):
            for j in range(i + 1, k):
                blk = perm[i:j + 1]
                if any((min(a, b), max(a, b)) not in req for a, b in itertools.combinations(blk, 2)): break
                if any(blk[x] > blk[y] for x in range(len(blk)) for y in range(x + 1, len(blk))): break
                np_ = perm[:i] + tuple(reversed(blk)) + perm[j + 1:]
                c = list(cnt); cr = list(crossed); lf = list(lefts); t = 0
                for g in range(i + 1, j + 1):
                    if not cr[g]: lf[g - 1] = min(c[g] + 1, CAP)
                    elif c[g] + 2 == 3: t += 1
                    c[g] = 0; cr[g] = True
                for g in (i, j + 1): c[g] = min(c[g] + 1, CAP)
                npairs = (j - i + 1) * (j - i) // 2
                for (vec, tl, nv), w in f(np_, tuple(c), tuple(cr), tuple(lf), ndone + npairs).items():
                    key = (vec, tl + t, nv + 1)
                    if key not in out: out[key] = ((i, j),) + w
        return out
    return f(tuple(range(k)), (0,) * (k + 1), (False,) * (k + 1), (None,) * (k - 1), 0)

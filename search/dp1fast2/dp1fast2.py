"""ctypes wrapper for the compiled one-line extension DP with the face graph built in C (graph.c, dp1.c).

Same API as dp1fast.Dp1:
    from dp1fast2 import Dp1
    d = Dp1.from_gens(j['gens'])          # or Dp1(tokens, n)
    d.T0, d.max_T()                       # base triangles, exact best T after adding one line
    d.solve()                             # dict: gain, T, by_k (best T by #new triple points), start_best, path, ...
    d.best_by_rank()                      # {h: best T}, h = #base lines below the new line at its start
    d.enum(thr)                           # all directed paths with T >= thr (list of Python-format x-sequences)
Option complete=True (Dp1(tokens, n, complete=True) / from_gens(..., complete=True)) first appends the far
crossings of parallel pairs (see complete_tokens); default False = exactly the semantics of dp1fast.
Differences: the Python face structure (extend_dp.build) is built lazily, only when x-sequences / rows are
requested (solve()['path'], enum(), rows()); T0, by_k and the per-rank bests never touch it.  The raw state arrays
of a path are in solve()['path_states'] and enum_states().
"""
import ctypes
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "work" / "research2"))
import extend_dp  # noqa: E402

NEG = -9999
_lib = None


def parallel_pairs(tokens, n):
    """Pairs of wires that never cross in the word (parallel lines)."""
    a = list(range(n))
    crossed = set()
    for g, w in tokens:
        blk = a[g:g + w]
        for i in range(w):
            for j in range(i + 1, w):
                crossed.add((min(blk[i], blk[j]), max(blk[i], blk[j])))
        a[g:g + w] = blk[::-1]
    return [(i, j) for i in range(n) for j in range(i + 1, n) if (i, j) not in crossed]


def complete_tokens(tokens, n):
    """Append the missing crossings of parallel pairs beyond all events (adjacent swaps until the order is fully
    reversed).  This is the arrangement the SAT models (kobon_sat / fastext: chi over triples, every pair crosses)
    see; without it the DP treats a parallel pair as never meeting and misses extensions that pass beyond the
    far crossing.  A no-op for words in which every pair crosses (all gallery words with n >= 10)."""
    a = list(range(n))
    for g, w in tokens:
        a[g:g + w] = a[g:g + w][::-1]
    toks = list(tokens)
    while True:
        for s in range(n - 1):
            if a[s] < a[s + 1]:
                a[s], a[s + 1] = a[s + 1], a[s]
                toks.append((s, 2))
                break
        else:
            return toks


def lib():
    global _lib
    if _lib is None:
        so = HERE / "libdp1f2.so"
        srcs = [HERE / f for f in ("graph.h", "graph.c", "dp1.c", "ext2.c")]
        if not so.exists() or so.stat().st_mtime < max(s.stat().st_mtime for s in srcs):
            subprocess.check_call([str(HERE / "build.sh")])
        L = ctypes.CDLL(str(so))
        P = ctypes.c_void_p
        I = ctypes.c_int
        L.dp1_from_tokens.restype = P
        L.dp1_from_tokens.argtypes = [I, I, P, P]
        L.dp1_free.argtypes = [P]
        for f in ("dp1_base_T", "dp1_nstarts", "dp1_nf", "dp1_ns"):
            getattr(L, f).argtypes = [P]
        L.dp1_starts.argtypes = [P, P]
        L.dp1_export.argtypes = [P] * 9
        L.dp1_solve.argtypes = [P, I, I, P, P, P, P, P, P]
        L.dp1_solve_max.argtypes = [P, I, I, P]
        L.dp1_enum.restype = ctypes.c_long
        L.dp1_enum.argtypes = [P, I, I, I, ctypes.c_long, I, P, P]
        _lib = L
    return _lib


def _ptr(a):
    return a.ctypes.data_as(ctypes.c_void_p)


class _Result(dict):
    """solve() result; 'path' (x-sequence) is converted on first access."""
    def __init__(self, d, conv):
        super().__init__(d)
        self._conv = conv

    def __missing__(self, key):
        if key == "path":
            v = self[key] = self._conv(self["path_states"])
            return v
        raise KeyError(key)


class Dp1:
    def __init__(self, tokens, n, complete=False):
        self.n = n
        self.tokens = complete_tokens(tokens, n) if complete else list(tokens)
        tg = np.ascontiguousarray([g for g, _ in self.tokens], dtype=np.int32)
        tw = np.ascontiguousarray([w for _, w in self.tokens], dtype=np.int32)
        self.h = lib().dp1_from_tokens(n, len(self.tokens), _ptr(tg), _ptr(tw))
        if not self.h:
            raise ValueError("graph build failed (bad word?)")
        L = lib()
        self.T0 = L.dp1_base_T(self.h)
        self.nf, self.ns = L.dp1_nf(self.h), L.dp1_ns(self.h)
        self.K = n + 2
        self.starts = np.zeros(L.dp1_nstarts(self.h), dtype=np.int32)
        L.dp1_starts(self.h, _ptr(self.starts))
        self._struct = None
        self._arrays = None

    @classmethod
    def from_gens(cls, gens, n=None, complete=False):
        toks = extend_dp.parse_tokens(gens)
        return cls(toks, n or max(g + w for g, w in toks), complete)

    def __del__(self):
        try:
            lib().dp1_free(self.h)
        except Exception:
            pass

    # --- lazily materialised views -------------------------------------------------------------------------
    def _export(self):
        if self._arrays is None:
            nf, ns = self.nf, self.ns
            foff, flen, below = (np.zeros(nf, dtype=t) for t in (np.int32, np.int32, np.uint32))
            kind, nxt, face_of, sel = (np.zeros(ns, dtype=np.int32) for _ in range(4))
            mask = np.zeros(ns, dtype=np.uint32)
            lib().dp1_export(self.h, *[_ptr(a) for a in (foff, flen, kind, mask, nxt, below, face_of, sel)])
            self._arrays = (foff, flen, kind, mask, nxt, below, face_of, sel)
        return self._arrays

    foff = property(lambda s: s._export()[0])
    flen = property(lambda s: s._export()[1])
    kind_ = property(lambda s: s._export()[2])
    mask_ = property(lambda s: s._export()[3])
    nxt_ = property(lambda s: s._export()[4])
    below_ = property(lambda s: s._export()[5])
    face_of = property(lambda s: s._export()[6])

    @property
    def struct(self):
        if self._struct is None:
            self._struct = extend_dp.build(self.tokens, self.n)
        return self._struct

    def _xs(self, states):
        faces = self.struct[0]
        foff, face_of = self.foff, self.face_of
        out = []
        for s in states:
            if s < 0:
                break
            fid = int(face_of[s])
            out.append(faces[fid]["cyc"][s - int(foff[fid])])
        return out

    # --- API -----------------------------------------------------------------------------------------------
    def solve(self, allow4=False, canonical=False):
        ns, K = len(self.starts), self.K
        bs = np.zeros(ns, dtype=np.int32)
        bsk = np.zeros(ns * K, dtype=np.int16)
        bk = np.zeros(K, dtype=np.int32)
        ps = ctypes.c_int()
        pl = ctypes.c_int()
        po = np.zeros(64, dtype=np.int32)
        val = lib().dp1_solve(self.h, int(allow4), int(canonical), _ptr(bs), _ptr(bsk), _ptr(bk),
                              ctypes.byref(ps), _ptr(po), ctypes.byref(pl))
        by_k = {k: self.T0 + int(v) for k, v in enumerate(bk) if v > NEG}
        return _Result(dict(gain=val, T=self.T0 + val if val > NEG else None, by_k=by_k, start_best=bs,
                            start_best_k=bsk.reshape(ns, K), path_states=[int(x) for x in po[:pl.value]],
                            path_start=ps.value), self._xs)

    def _start_best(self, allow4, canonical):
        """(overall gain, per-start best gain) from the scalar DP (no per-k tables)."""
        bs = np.zeros(len(self.starts), dtype=np.int32)
        val = lib().dp1_solve_max(self.h, int(allow4), int(canonical), _ptr(bs))
        return val, bs

    def max_T(self, allow4=False):
        val, _ = self._start_best(allow4, False)
        return self.T0 + val if val > NEG else None

    def best_by_rank(self, allow4=False):
        """{h: best T}: h = #base lines below the new line at its canonical (left/bottom) start,
        h in 0..n (0 = bottom face; the top-face start is its reverse and is merged into h=0)."""
        _, sb = self._start_best(allow4, True)
        below = self.below_
        face_of = self.face_of
        out = {}
        for i, s in enumerate(self.starts):
            v = sb[i]
            if v > NEG:
                h = bin(int(below[face_of[s]])).count("1")
                out[h] = max(out.get(h, -1), self.T0 + int(v))
        return out

    def enum_states(self, thr, allow4=False, canonical=False, cap=100000):
        """(count, array cap x (n+1) of exit-state sequences, -1 padded)."""
        stride = self.n + 1
        buf = np.zeros(cap * stride, dtype=np.int32)
        sb = np.zeros(cap, dtype=np.int32)
        cnt = lib().dp1_enum(self.h, int(allow4), int(canonical), thr - self.T0, cap, stride, _ptr(buf), _ptr(sb))
        return cnt, buf.reshape(cap, stride)

    def enum(self, thr, allow4=False, canonical=False, cap=100000):
        """All directed paths with T >= thr.  Returns (count, list of x-sequences); the list is capped."""
        cnt, buf = self.enum_states(thr, allow4, canonical, cap)
        return cnt, [self._xs(buf[i]) for i in range(min(cnt, cap))]

    def rows(self, seq):
        return extend_dp.path_rows(self.struct, self.n, seq)


def _setup_ext2(L):
    P = ctypes.c_void_p
    I = ctypes.c_int
    L.ext2_new.restype = P
    L.ext2_new.argtypes = [I, I, P, P, I]
    L.ext2_free.argtypes = [P]
    L.ext2_T0.argtypes = [P]
    L.ext2_pair.argtypes = [P, I, I, I, I, P]
    L.ext2_stats.argtypes = [P, P]
    L.ext2_mgmn.argtypes = [P, I, P, P]
    L.ext2_partner.argtypes = [P, I, P, I, I]
    L.ext2_bydn.argtypes = [P, I, P]
    L.ext2_scratch_T0.argtypes = [P]
    L.ext2_count_ge.argtypes = [P, I, I, I]
    return L


def ext2_lib():
    L = lib()
    if not getattr(L, "_ext2_ready", False):
        _setup_ext2(L)
        L._ext2_ready = True
    return L

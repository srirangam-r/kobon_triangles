"""ctypes wrapper for the compiled one-line extension DP (dp1.c).

    from dp1fast import Dp1
    d = Dp1.from_gens(j['gens'])          # or Dp1(tokens, n)
    d.T0, d.max_T()                       # base triangles, exact best T after adding one line
    d.solve()                             # dict with best T by #new triple points, per-start bests, argmax path
    d.best_by_rank()                      # {h: best T} , h = #base lines below the new line at its start
    d.enum(thr)                           # all directed paths with T >= thr (list of Python-format x-sequences)
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


def lib():
    global _lib
    if _lib is None:
        so = HERE / "libdp1.so"
        if not so.exists() or so.stat().st_mtime < (HERE / "dp1.c").stat().st_mtime:
            subprocess.check_call([str(HERE / "build.sh")])
        L = ctypes.CDLL(str(so))
        P = ctypes.c_void_p
        I = ctypes.c_int
        L.dp1_new.restype = P
        L.dp1_new.argtypes = [I, I, I] + [P] * 6
        L.dp1_free.argtypes = [P]
        L.dp1_base_T.argtypes = [P]
        L.dp1_nstarts.argtypes = [P]
        L.dp1_starts.argtypes = [P, P]
        L.dp1_solve.argtypes = [P, I, I, P, P, P, P, P, P]
        L.dp1_enum.restype = ctypes.c_long
        L.dp1_enum.argtypes = [P, I, I, I, ctypes.c_long, I, P, P]
        _lib = L
    return _lib


def _ptr(a):
    return a.ctypes.data_as(ctypes.c_void_p)


class Dp1:
    def __init__(self, tokens, n):
        self.n = n
        self.struct = extend_dp.build(tokens, n)
        faces, edges, verts, _, _ = self.struct
        foff, flen, kind, mask, nxt, below, self.elem = [], [], [], [], [], [], []
        pos = 0
        for f in faces:
            foff.append(pos)
            flen.append(len(f["cyc"]))
            pos += len(f["cyc"])
        index = [{x: i for i, x in enumerate(f["cyc"])} for f in faces]
        for fid, f in enumerate(faces):
            for x in f["cyc"]:
                self.elem.append((fid, x))
                if x[0] == "inf":
                    kind.append(0); mask.append(0); nxt.append(-1)
                elif x[0] == "e":
                    w, bel, abv = edges[x[1]]
                    nf = abv if bel == fid else bel
                    kind.append(1); mask.append(1 << w); nxt.append(foff[nf] + index[nf][x])
                else:
                    ls, opp = verts[x[1]]
                    nf = opp[fid]
                    kind.append(2); mask.append(sum(1 << w for w in ls)); nxt.append(foff[nf] + index[nf][x])
            below.append(sum(1 << w for w in f["below"]))
        self.nf, self.ns = len(faces), pos
        self.K = n + 2
        a = lambda v, t: np.ascontiguousarray(v, dtype=t)
        self._keep = [a(foff, np.int32), a(flen, np.int32), a(kind, np.int32), a(mask, np.uint32),
                      a(nxt, np.int32), a(below, np.uint32)]
        self.foff, self.flen, self.kind_, self.mask_, self.nxt_, self.below_ = self._keep
        self.h = lib().dp1_new(n, self.nf, self.ns, *[_ptr(x) for x in self._keep])
        self.T0 = lib().dp1_base_T(self.h)
        ns = lib().dp1_nstarts(self.h)
        self.starts = np.zeros(ns, dtype=np.int32)
        lib().dp1_starts(self.h, _ptr(self.starts))

    @classmethod
    def from_gens(cls, gens, n=None):
        toks = extend_dp.parse_tokens(gens)
        return cls(toks, n or max(g + w for g, w in toks))

    def __del__(self):
        try:
            lib().dp1_free(self.h)
        except Exception:
            pass

    def _xs(self, states):
        faces = self.struct[0]
        out = []
        for s in states:
            if s < 0:
                break
            fid, _ = self.elem[s]
            out.append(faces[fid]["cyc"][s - self.foff[fid]])
        return out

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
        return dict(gain=val, T=self.T0 + val if val > NEG else None, by_k=by_k, start_best=bs,
                    start_best_k=bsk.reshape(ns, K), path=self._xs(po[:pl.value]), path_start=ps.value)

    def max_T(self, allow4=False):
        return self.solve(allow4)["T"]

    def best_by_rank(self, allow4=False):
        """{h: best T}: h = #base lines below the new line at its canonical (left/bottom) start,
        h in 0..n (0 = bottom face; the top-face start is its reverse and is merged into h=0)."""
        r = self.solve(allow4, canonical=True)
        out = {}
        for i, s in enumerate(self.starts):
            v = r["start_best"][i]
            if v > NEG:
                h = bin(int(self.below_[self.elem[s][0]])).count("1")
                out[h] = max(out.get(h, -1), self.T0 + int(v))
        return out

    def enum(self, thr, allow4=False, canonical=False, cap=100000):
        """All directed paths with T >= thr.  Returns (count, list of x-sequences); the list is capped."""
        stride = self.n + 1
        buf = np.zeros(cap * stride, dtype=np.int32)
        sb = np.zeros(cap, dtype=np.int32)
        cnt = lib().dp1_enum(self.h, int(allow4), int(canonical), thr - self.T0, cap, stride,
                             _ptr(buf), _ptr(sb))
        buf = buf.reshape(cap, stride)
        return cnt, [self._xs(buf[i]) for i in range(min(cnt, cap))]

    def rows(self, seq):
        return extend_dp.path_rows(self.struct, self.n, seq)

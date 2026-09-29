"""ctypes wrapper for libwalkc.so: compiled hot paths of the DP ruin-and-recreate walk.

A word is a wiring word: bytes (g0 w0 g1 w1 ...), a list of (g, w) tuples (dpwalk.py's tokens) or a gens string
("3 5* 2 ...").  Functions return the same kind of word they were given (bytes for bytes, tokens for tokens,
gens for str).  n is optional (inferred as max(g + w), which is right for every word with a line on top).

    import walkc
    walkc.delete_line(word, d)                  -> word with line d removed (labels above d shift down)
    walkc.count(word)                           -> (T, k, bridges, Z, D)   exact
    walkc.count_lines(word)                     -> (T, k, bridges, Z, D, Zl, Dl, Zi)  per-line lists
    walkc.canon_hash(word)                      -> 64-bit hash of the canonical form (4n end-circle symmetries + sign flip)
    walkc.canon_bytes(word)                     -> the canonical form itself (== coverage.canon of the chi vector)
    walkc.rows_hash(word)                       -> 64-bit hash of the labelled event rows
    walkc.insert_path(word, path, start=None)   -> word of base + the new line along a dp1 path (exit states)
    walkc.rows_to_word(rows, order=None, mode=0)-> wiring word from event rows (frozenset rows), mode 0 = dpwalk.sweep,
                                                   mode 1 = audit_planted.rows_to_word
    walkc.Base(word, n)                         -> one-line DP handle: solve_max(), solve(), enum(thr, cap), eval(i)
"""
import ctypes
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
MAXE = 34
_lib = None
_BUF = ctypes.create_string_buffer(4096)
_INFO = (ctypes.c_int32 * (5 + 3 * 40 + 4))()


def lib():
    global _lib
    if _lib is None:
        so = HERE / "libwalkc.so"
        srcs = [HERE / "walkc.c", HERE.parent / "dp1fast2" / "graph.c", HERE.parent / "dp1fast2" / "graph.h",
                HERE.parent / "dp1fast2" / "dp1.c"]
        if not so.exists() or so.stat().st_mtime < max(s.stat().st_mtime for s in srcs):
            subprocess.check_call([str(HERE / "build.sh")])
        L = ctypes.CDLL(str(so))
        P, I, U8 = ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p
        L.wc_delete.argtypes = [U8, I, I, I, P]
        L.wc_info.argtypes = [U8, I, I, P]
        L.wc_rows_hash.restype = ctypes.c_uint64
        L.wc_rows_hash.argtypes = [U8, I, I]
        L.wc_hash_bytes.restype = ctypes.c_uint64
        L.wc_hash_bytes.argtypes = [U8, I]
        L.wc_set_tables.argtypes = [I, I, P, P]
        L.wc_canon.argtypes = [U8, I, I, P, P]
        L.wc_rows_to_word.argtypes = [P, P, I, P, I, P]
        L.wc_insert_path.argtypes = [P, P, I, I, P]
        L.wc_insert_path_word.argtypes = [U8, I, I, P, I, I, P]
        L.wc_eval.argtypes = [P, P, I, I, P, P]
        L.wc_base_new.restype = P
        L.wc_base_new.argtypes = [U8, I, I]
        L.dp1_free.argtypes = [P]
        L.dp1_base_T.argtypes = [P]
        L.dp1_nstarts.argtypes = [P]
        L.dp1_starts.argtypes = [P, P]
        L.dp1_solve_max.argtypes = [P, I, I, P]
        L.dp1_solve.argtypes = [P, I, I, P, P, P, P, P, P]
        L.dp1_enum.restype = ctypes.c_long
        L.dp1_enum.argtypes = [P, I, I, I, ctypes.c_long, I, P, P]
        L.wc_prepare.argtypes = [P]
        L.wc_enum.restype = ctypes.c_long
        L.wc_enum.argtypes = [P, I, ctypes.c_long, I, P, P]
        _lib = L
    return _lib


def _p(a):
    return a.ctypes.data_as(ctypes.c_void_p)


# ---------------------------------------------------------------------------------------------- word types
def _to_bytes(word):
    """(bytes, kind) with kind in 'b' / 't' / 's'."""
    if isinstance(word, (bytes, bytearray)):
        return bytes(word), "b"
    if isinstance(word, str):
        toks = [(int(t.rstrip("*")), 3 if t.endswith("*") else 2) for t in word.split()]
        return bytes(x for gw in toks for x in gw), "s"
    return bytes(x for gw in word for x in gw), "t"


def _from_bytes(b, kind):
    if kind == "b":
        return b
    toks = [(b[i], b[i + 1]) for i in range(0, len(b), 2)]
    if kind == "t":
        return toks
    return " ".join(f"{g}*" if w == 3 else str(g) for g, w in toks)


def to_word(word):
    return _to_bytes(word)[0]


def tokens(word):
    return _from_bytes(_to_bytes(word)[0], "t")


def gens(word):
    return _from_bytes(_to_bytes(word)[0], "s")


def infer_n(b):
    return max(b[i] + b[i + 1] for i in range(0, len(b), 2))


# ---------------------------------------------------------------------------------------------- primitives
def delete_line(word, d, n=None):
    b, kind = _to_bytes(word)
    n = n or infer_n(b)
    nt = lib().wc_delete(b, len(b) // 2, n, d, _BUF)
    return _from_bytes(ctypes.string_at(_BUF, 2 * nt), kind)


def _info(b, n):
    if lib().wc_info(b, len(b) // 2, n, _INFO):
        raise ValueError("malformed word")
    return _INFO


def count(word, n=None):
    """(T, k, bridges, Z, D)"""
    b, _ = _to_bytes(word)
    I = _info(b, n or infer_n(b))
    return I[0], I[1], I[2], I[3], I[4]


def count_lines(word, n=None):
    """(T, k, bridges, Z, D, Zl, Dl, Zi): per-line unused / doubly used segments and the unused segments ending in a
    simple crossing with that line (the other line at a simple end of an unused segment)."""
    b, _ = _to_bytes(word)
    n = n or infer_n(b)
    I = _info(b, n)
    return (I[0], I[1], I[2], I[3], I[4], list(I[5:5 + n]), list(I[5 + n:5 + 2 * n]), list(I[5 + 2 * n:5 + 3 * n]))


def rows_hash(word, n=None):
    b, _ = _to_bytes(word)
    return lib().wc_rows_hash(b, len(b) // 2, n or infer_n(b))


_TABLES = set()


def _tables(n):
    if n not in _TABLES:
        sys.path.insert(0, str(ROOT / "search"))
        sys.path.insert(1, str(ROOT / "work" / "lns" / "push"))
        import coverage  # noqa: E402
        _, P, F = coverage.tables(n)
        P32 = np.ascontiguousarray(P, dtype=np.int32)
        F8 = np.ascontiguousarray(F, dtype=np.int8)
        lib().wc_set_tables(n, P32.shape[0], _p(P32), _p(F8))
        _TABLES.add(n)


def canon(word, n=None):
    """(hash, canonical bytes)"""
    b, _ = _to_bytes(word)
    n = n or infer_n(b)
    _tables(n)
    m = n * (n - 1) * (n - 2) // 6
    out = ctypes.create_string_buffer(m)
    h = ctypes.c_uint64()
    rc = lib().wc_canon(b, len(b) // 2, n, out, ctypes.byref(h))
    if rc:
        raise ValueError(f"canon failed ({rc}): word with a parallel pair?")
    return h.value, out.raw


def canon_hash(word, n=None):
    b, _ = _to_bytes(word)
    n = n or infer_n(b)
    _tables(n)
    h = ctypes.c_uint64()
    rc = lib().wc_canon(b, len(b) // 2, n, None, ctypes.byref(h))
    if rc:
        raise ValueError(f"canon failed ({rc}): word with a parallel pair?")
    return h.value


def canon_bytes(word, n=None):
    return canon(word, n)[1]


def hash_bytes(data):
    """The hash applied to canon_bytes (to compare with coverage.canon output)."""
    return lib().wc_hash_bytes(data, len(data))


def rows_to_word(rows, order=None, mode=0):
    """rows: per line the tuple of events (frozensets of the other lines); order: bottom-to-top initial line order
    (default identity).  Returns tokens [(g, w)] or None."""
    N = len(rows)
    arr = np.zeros((N, MAXE), dtype=np.uint32)
    rl = np.zeros(N, dtype=np.int32)
    for x, r in enumerate(rows):
        rl[x] = len(r)
        for i, ev in enumerate(r):
            arr[x, i] = sum(1 << y for y in ev)
    init = np.array(list(order) if order is not None else range(N), dtype=np.int32)
    out = ctypes.create_string_buffer(4096)
    nt = lib().wc_rows_to_word(_p(arr), _p(rl), N, _p(init), mode, out)
    if nt < 0:
        return None
    return _from_bytes(ctypes.string_at(out, 2 * nt), "t")


def insert_path(word, path, start=None, n=None):
    """Word of base + a new line along `path` (list of dp1 exit states, as dp1fast2 solve()['path_states'] or a row
    of enum_states()).  start: the path's start state (solve()['path_start'] / enum start), used as a hint for the
    slot / direction of the new line (without it every (slot, direction) is tried, like Base.word_of(seq, None))."""
    b, kind = _to_bytes(word)
    n = n or infer_n(b)
    p = np.ascontiguousarray([int(x) for x in path if x >= 0], dtype=np.int32)
    nt = lib().wc_insert_path_word(b, len(b) // 2, n, _p(p), len(p), -1 if start is None else start, _BUF)
    if nt < 0:
        raise RuntimeError(f"could not rebuild wiring word ({nt})")
    return _from_bytes(ctypes.string_at(_BUF, 2 * nt), kind)


# ---------------------------------------------------------------------------------------------- one-line DP handle
_ENUM = {}


def _enum_buf(cap, stride):
    key = (cap, stride)
    if key not in _ENUM:
        _ENUM[key] = (np.zeros(cap * stride, dtype=np.int32), np.zeros(cap, dtype=np.int32))
    return _ENUM[key]


class Base:
    """One-line extension DP of a base word (same semantics as dp1fast2.Dp1 / dpwalk.Base), built from bytes."""

    def __init__(self, word, n=None):
        b, _ = _to_bytes(word)
        self.word = b
        self.n = n or infer_n(b)
        self.h = lib().wc_base_new(b, len(b) // 2, self.n)
        if not self.h:
            raise ValueError("graph build failed (bad word?)")
        self.T0 = lib().dp1_base_T(self.h)
        self._stride = self.n + 1
        self._enum = None
        self._prepared = False

    def __del__(self):
        try:
            lib().dp1_free(self.h)
        except Exception:
            pass

    def solve_max(self):
        """Exact best T after adding one line (None if there is no extension).  Also prepares the scalar DP memos
        that enum() reuses, so call it before enum() (enum() does so itself if needed)."""
        val = lib().wc_prepare(self.h)
        self._prepared = True
        return self.T0 + val if val > -9999 else None

    def solve_max_ref(self):
        """dp1_solve_max (no memo sharing), for testing."""
        ns = lib().dp1_nstarts(self.h)
        bs = np.zeros(ns, dtype=np.int32)
        val = lib().dp1_solve_max(self.h, 0, 0, _p(bs))
        return self.T0 + val if val > -9999 else None

    def solve(self):
        """(T, path_states, path_start) of one argmax path (dp1_solve)."""
        L = lib()
        ns = L.dp1_nstarts(self.h)
        K = self.n + 2
        bs = np.zeros(ns, dtype=np.int32)
        bsk = np.zeros(ns * K, dtype=np.int16)
        bk = np.zeros(K, dtype=np.int32)
        ps, pl = ctypes.c_int(), ctypes.c_int()
        po = np.zeros(64, dtype=np.int32)
        val = L.dp1_solve(self.h, 0, 0, _p(bs), _p(bsk), _p(bk), ctypes.byref(ps), _p(po), ctypes.byref(pl))
        T = self.T0 + val if val > -9999 else None
        return T, [int(x) for x in po[:pl.value]], ps.value

    def enum(self, thr, cap):
        """Canonical-start paths with T >= thr; returns the total count, the first min(count, cap) are kept in the
        shared buffer (valid until the next enum call, any Base).  Same paths, same order as dp1_enum."""
        buf, sb = _enum_buf(cap, self._stride)
        cnt = lib().wc_enum(self.h, thr - self.T0, cap, self._stride, _p(buf), _p(sb)) if self._prepared else -1
        if cnt < 0:                      # another Base was prepared since: redo
            self.solve_max()
            cnt = lib().wc_enum(self.h, thr - self.T0, cap, self._stride, _p(buf), _p(sb))
        self._enum = (buf, sb)
        return cnt

    def enum_ref(self, thr, cap):
        """dp1_enum (K-table DP), for testing; fills the same buffer as enum()."""
        buf, sb = _enum_buf(cap, self._stride)
        cnt = lib().dp1_enum(self.h, 0, 1, thr - self.T0, cap, self._stride, _p(buf), _p(sb))
        self._enum = (buf, sb)
        return cnt

    def path(self, i):
        buf, sb = self._enum
        row = buf[i * self._stride:(i + 1) * self._stride]
        return [int(x) for x in row if x >= 0], int(sb[i])

    def word_of(self, path, start=None):
        p = np.ascontiguousarray(path, dtype=np.int32)
        nt = lib().wc_insert_path(self.h, _p(p), len(p), -1 if start is None else start, _BUF)
        if nt < 0:
            raise RuntimeError(f"could not rebuild wiring word ({nt})")
        return ctypes.string_at(_BUF, 2 * nt)

    def eval(self, i):
        """Rebuild the i-th enumerated path and score it in one call: (word bytes, T, k, bridges, Z, D, rows hash)."""
        buf, sb = self._enum
        n1 = self.n + 1
        nt = lib().wc_eval(self.h, buf.ctypes.data + 4 * i * self._stride, self._stride, int(sb[i]), _BUF, _INFO)
        if nt < 0:
            raise RuntimeError(f"could not rebuild wiring word ({nt})")
        off = 5 + 3 * n1
        h = (_INFO[off] & 0xffffffff) | ((_INFO[off + 1] & 0xffffffff) << 32)
        return ctypes.string_at(_BUF, 2 * nt), _INFO[0], _INFO[1], _INFO[2], _INFO[3], _INFO[4], h

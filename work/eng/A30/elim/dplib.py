"""A30: independent exact-integer DP over an exported T25 window graph (see export_graph.py).
Only the graph topology / option tables come from T25's builder; everything else (window minima, layered DP, flagged DP,
joint tightness) is re-implemented here in exact integer arithmetic (numpy int64, all values < 2^62, checked)."""
import pickle, collections
import numpy as np

INF = np.int64(1 << 62)
W17 = 17


class Graph:
    def __init__(self, path):
        d = pickle.load(open(path, "rb"))
        self.d = d
        self.N = d["N"]
        self.ku = np.array(d["ku"], dtype=np.int64)
        self.starts = np.array(d["starts"], dtype=np.int64)
        self.src = np.array(d["src"], dtype=np.int64)
        self.dst = np.array(d["dst"], dtype=np.int64)
        self.ew = np.array(d["ew"], dtype=np.int64)
        self.tn = np.array(d["tn"], dtype=np.int64)
        self.tw = np.array(d["tw"], dtype=np.int64)
        self.win_repr = d["win_repr"]
        self.nwin = len(self.win_repr)
        self.keyidx = {k: i for i, k in enumerate(d["keys"])}
        # half-integer -> integer numerators
        self.term_alts2 = []
        for alts in d["term_alts"]:
            al = []
            for a in alts:
                v = []
                for c, x in a:
                    x2 = int(round(2 * x))
                    assert abs(2 * x - x2) < 1e-12
                    v.append((c, x2))
                al.append(v)
            self.term_alts2.append(al)
        self.opts = []
        for opts in d["opts"]:
            o2 = []
            for v2, terms in opts:
                iv = int(round(v2)); assert abs(v2 - iv) < 1e-12
                tl = []
                for t, c in terms:
                    ic = int(round(c)); assert abs(c - ic) < 1e-12
                    tl.append((t, ic))
                o2.append((iv, tl))
            self.opts.append(o2)
        self.unit_e = self.ku[self.src]
        self.m_by = {c0: np.nonzero(self.unit_e == c0)[0] for c0 in (1, 2)}
        # edge/terminal sanity
        assert self.ew.max() < self.nwin

    def weights_vec(self, wdict):
        """dict key -> int weight -> dict col -> int (only columns present in this graph)"""
        return {self.keyidx[k]: int(v) for k, v in wdict.items() if k in self.keyidx}

    def window_values(self, wcol, D):
        """per window: list of option values (Python ints)  D*v2 + sum_t count_t * min_alt sum_c w_c * (2x_c)  (this equals
        D*v2 + 2*sum count*min_alt w.x  where w is the integer weight vector with denominator D)."""
        tval = []
        for al in self.term_alts2:
            tval.append(min(sum(wcol.get(c, 0) * x2 for c, x2 in a) for a in al))
        out = []
        for opts in self.opts:
            out.append([D * v2 + sum(cnt * tval[t] for t, cnt in tl) for v2, tl in opts])
        return out

    def wmin_array(self, optvals):
        return np.array([min(v) for v in optvals], dtype=np.int64)

    # ------------------------------------------------------------------------------ DP
    def layered_forward(self, ewt, W=W17, flag_mask=None):
        """F[c][node] = min path weight from a start, using exactly c units.  flag_mask: boolean over windows; returns F0,F1 (paths
        avoiding / having used a flagged window) if given."""
        N = self.N
        nl = 2 if flag_mask is not None else 1
        F = [np.full((W + 1, N), INF, dtype=np.int64) for _ in range(nl)]
        F[0][0][self.starts] = 0
        fe = flag_mask[self.ew] if flag_mask is not None else None
        for c in range(W + 1):
            for c0 in (1, 2):
                c2 = c + c0
                if c2 > W:
                    continue
                m = self.m_by[c0]
                for f_from in range(nl):
                    fs = F[f_from][c][self.src[m]]
                    ok = fs < INF
                    if not ok.any():
                        continue
                    mm = m[ok]
                    cand = fs[ok] + ewt[mm]
                    if nl == 1:
                        f_to = np.zeros(len(mm), dtype=np.int64)
                    else:
                        f_to = np.where(fe[mm], 1, f_from)
                    for t in range(nl):
                        sel = f_to == t
                        if sel.any():
                            np.minimum.at(F[t][c2], self.dst[mm[sel]], cand[sel])
        return F

    def path_min(self, wmin, W=W17, flag_mask=None):
        """min over complete admissible paths with exactly W units of the total weight; with flag_mask returns (min over all, min over
        paths through a flagged window)"""
        F = self.layered_forward(wmin[self.ew] if False else wmin[self.ew], W, flag_mask)
        nl = len(F)
        best = [int(INF)] * nl
        for u, wi in zip(self.tn.tolist(), self.tw.tolist()):
            c = W - int(self.ku[u])
            if c < 0:
                continue
            for f in range(nl):
                v = int(F[f][c][u])
                if v < INF:
                    if nl == 2 and flag_mask[wi]:
                        ff = 1
                    else:
                        ff = f
                    tot = v + int(wmin[wi])
                    if tot < best[ff]:
                        best[ff] = tot
        if nl == 1:
            return best[0]
        return best

    def backward(self, ewt, termw, W=W17):
        """B[r][node] = min weight of a completion using exactly r units *excluding node's own* units?  Convention used below:
        B[r][u] = min over paths from u (before taking u's outgoing edge), where the remaining units AFTER the edge from u include the
        units of the successor; we define via forward units: a path is a sequence of edges e1..ek ending at terminal node u_k with the
        terminal window.  Units are counted as ku[src] per edge, plus ku[terminal node]."""
        N = self.N
        B = np.full((W + 1, N), INF, dtype=np.int64)
        for u, wi in zip(self.tn.tolist(), self.tw.tolist()):
            un = int(self.ku[u])
            if un <= W:
                v = int(termw[wi])
                if v < B[un][u]:
                    B[un][u] = v
        for c in range(W + 1):
            for c0 in (1, 2):
                if c - c0 < 0:
                    continue
                m = self.m_by[c0]
                bs = B[c - c0][self.dst[m]]
                ok = bs < INF
                if not ok.any():
                    continue
                mm = m[ok]
                np.minimum.at(B[c], self.src[mm], bs[ok] + ewt[mm])
        return B

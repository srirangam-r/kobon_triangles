"""Integrality test: is there a multiset of 18 lines from the jointly tight language (pooled window options and term alternatives)
with all transfer columns conserved, 282 triangle sides (T = 94), and 3t triple-point incidences?
usage: ilp.py STATE_K [--lp] [--time T]"""
import sys, os, pickle, argparse, collections, time
from fractions import Fraction as F
ROOT = __import__("pathlib").Path(__file__).resolve().parents[4].as_posix()
sys.path.insert(0, ROOT + "/search"); sys.path.append(ROOT + "/work/t3"); sys.path.insert(0, ROOT + "/work/eng/T25/elim")
import numpy as np
import scipy.sparse as sp
from scipy.optimize import milp, LinearConstraint, Bounds, linprog
import elim as E
import rule_lp_t25 as T
import rule_lp as RL

TRANSFER = {"A", "C", "L", "R", "M", "SV", "TRI", "PT", "U"}


def enum_paths(G, arr, W=17):
    tight, tterm, Bk, cw, ku, target = arr["tight"], arr["tterm"], arr["Bk"], arr["cw"], arr["ku"], arr["target"]
    out = collections.defaultdict(list)
    for e in np.nonzero(tight)[0]: out[int(G.src[e])].append(int(e))
    term = {}
    for i in np.nonzero(tterm)[0]: term[int(G.tn[i])] = int(i)
    INF = 1e17
    paths = []
    def dfs(u, used, cost, edges):
        if used + ku[u] == W and u in term:
            i = term[u]
            if abs(cost + cw[G.tw[i]] - target) < 1e-6: paths.append((tuple(edges), int(G.tw[i]), u))
        nu = used + ku[u]
        if nu >= W: return
        rem = W - nu
        for e in out[u]:
            v = int(G.dst[e]); c = cw[G.ew[e]]
            if Bk[rem][v] < INF and cost + c + Bk[rem][v] <= target + 1e-6:
                dfs(v, nu, cost + c, edges + [e])
    for s in G.starts: dfs(int(s), 0, 0.0, [])
    return paths


def build(statek, verbose=True):
    o = E.make_o()
    st = pickle.load(open(f"{E.DIR}/state_{statek}.pkl", "rb"))
    certs, allowed = st["certs"], st["allowed"]
    cat = T.build_graph(o, allowed=allowed).cat
    G = T.build_graph(o, cat=cat, allowed=allowed)
    res = E.joint_structure(o, cat, allowed, certs, G=G)
    arr = res["arrays"]
    paths = enum_paths(G, arr)
    if verbose: print("tight paths", len(paths), "graph windows", len(G.win_list), flush=True)
    return o, G, certs, paths, res


def tight_sets(G, certs):
    K = G.K
    opt_ok = np.ones(len(G.ov2), dtype=bool)
    nterm_rows = G.n_term_opts
    alt_ok = np.ones(nterm_rows, dtype=bool)
    for c in certs:
        w = E.cert_vec(G.cat, c, K); D = c["D"]
        wmin, val = G.window_min(w, D)
        opt_ok &= val <= wmin[G.opt_win] + 1e-7
        tov = G.TO @ w
        nt = len(G.term_start)
        ends = np.append(G.term_start[1:], nterm_rows)
        for t in range(nt):
            lo, hi = G.term_start[t], ends[t]
            m = tov[lo:hi].min()
            alt_ok[lo:hi] &= tov[lo:hi] <= m + 1e-7
    return opt_ok, alt_ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("k", type=int)
    ap.add_argument("--lp", action="store_true")
    ap.add_argument("--time", type=float, default=600)
    ap.add_argument("--tri", type=int, default=282)
    a = ap.parse_args()
    o, G, certs, paths, res = build(a.k)
    opt_ok, alt_ok = tight_sets(G, certs)
    nt = len(G.term_start)
    ends = np.append(G.term_start[1:], G.n_term_opts)
    # usable options: tight and every term has a tight alternative
    WO = G.WO.tocsr()
    term_has = np.array([alt_ok[G.term_start[t]:ends[t]].any() for t in range(nt)])
    opt_use = opt_ok.copy()
    for r in np.nonzero(opt_ok)[0]:
        ts = WO.indices[WO.indptr[r]:WO.indptr[r + 1]]
        if not term_has[ts].all(): opt_use[r] = False
    # windows on paths
    P = len(paths)
    wins_of = []
    for (edges, tw, u) in paths:
        wins_of.append([int(G.ew[e]) for e in edges] + [tw])
    used_w = sorted({w for ws in wins_of for w in ws})
    print("windows used", len(used_w), "usable option rows", int(sum(opt_use[G.win_start[j]:(G.win_start[j + 1] if j + 1 < len(G.win_start) else len(G.opt_win))].sum() for j in used_w)))
    bad_w = [j for j in used_w if not opt_use[G.win_start[j]:(G.win_start[j + 1] if j + 1 < len(G.win_start) else len(G.opt_win))].any()]
    print("windows with no usable option:", len(bad_w))
    # variables
    var = {}
    def V(key):
        if key not in var: var[key] = len(var)
        return var[key]
    for p in range(P): V(("x", p))
    optrows = {}
    for j in used_w:
        lo = G.win_start[j]; hi = G.win_start[j + 1] if j + 1 < len(G.win_start) else len(G.opt_win)
        rows = [r for r in range(lo, hi) if opt_use[r]]
        optrows[j] = rows
        for r in rows: V(("u", r))
    termset = set()
    for j in used_w:
        for r in optrows[j]:
            for t in WO.indices[WO.indptr[r]:WO.indptr[r + 1]]: termset.add(int(t))
    termalts = {}
    for t in sorted(termset):
        alts = [q for q in range(G.term_start[t], ends[t]) if alt_ok[q]]
        termalts[t] = alts
        for q in alts: V(("v", q))
    nv = len(var)
    print("variables", nv, "terms", len(termset), flush=True)
    rows_i, rows_j, rows_v, rhs_lo, rhs_hi = [], [], [], [], []
    def add_row(coefs, lo, hi):
        i = len(rhs_lo)
        for k, x in coefs.items():
            rows_i.append(i); rows_j.append(k); rows_v.append(x)
        rhs_lo.append(lo); rhs_hi.append(hi)
    # A: sum x = 18
    add_row({var[("x", p)]: 1 for p in range(P)}, 18, 18)
    # B: window usage
    m_pw = collections.defaultdict(lambda: collections.Counter())
    for p, ws in enumerate(wins_of):
        for w in ws: m_pw[w][p] += 1
    for j in used_w:
        co = collections.Counter()
        for r in optrows[j]: co[var[("u", r)]] += 1
        for p, m in m_pw[j].items(): co[var[("x", p)]] -= m
        add_row(dict(co), 0, 0)
    # C: term usage
    tuse = collections.defaultdict(collections.Counter)
    for j in used_w:
        for r in optrows[j]:
            for k in range(WO.indptr[r], WO.indptr[r + 1]):
                tuse[int(WO.indices[k])][var[("u", r)]] += WO.data[k]
    for t in sorted(termset):
        co = collections.Counter()
        for q in termalts[t]: co[var[("v", q)]] += 1
        for vi, m in tuse[t].items(): co[vi] -= m
        add_row(dict(co), 0, 0)
    # D: column conservation for transfer columns
    TO = G.TO.tocsr()
    colrows = collections.defaultdict(collections.Counter)
    for t in sorted(termset):
        for q in termalts[t]:
            for k in range(TO.indptr[q], TO.indptr[q + 1]):
                c = int(TO.indices[k]); key = G.cat.keys[c]
                fam = key[0] if isinstance(key[0], str) else "?"
                if key in (("a",), ("alpha",), ("wr",)): continue
                colrows[c][var[("v", q)]] += TO.data[k]
    fams = collections.Counter(G.cat.keys[c][0] for c in colrows)
    print("conserved columns", len(colrows), dict(fams), flush=True)
    for c, co in colrows.items():
        co = {k: x for k, x in co.items() if x != 0}
        if co: add_row(co, 0, 0)
    # E: triangle sides, T incidences, integer t
    tri_p, nT_p = [], []
    for (edges, tw, u) in paths:
        fr = [G.nodes[int(G.src[e])][1] for e in edges] + [G.nodes[u][1]]
        tri_p.append(sum(f.bout[0] + f.bout[1] for f in fr))
        nT_p.append(sum(1 for f in fr if f.kind == "T"))
    add_row({var[("x", p)]: tri_p[p] for p in range(P) if tri_p[p]}, a.tri, a.tri)
    tv = V(("t",))
    co = {var[("x", p)]: nT_p[p] for p in range(P) if nT_p[p]}
    co[tv] = -3
    add_row(co, 0, 0)
    nv = len(var)
    A = sp.csr_matrix((rows_v, (rows_i, rows_j)), shape=(len(rhs_lo), nv))
    print("constraints", A.shape, flush=True)
    c = np.zeros(nv)
    integ = np.ones(nv)
    if a.lp:
        r = linprog(c, A_eq=A, b_eq=np.array(rhs_lo), bounds=[(0, None)] * nv, method="highs")
        print("LP relaxation:", r.status, r.message)
        if r.status == 0:
            x = r.x
            for p in range(P):
                if x[var[("x", p)]] > 1e-9: print("  path", p, "x =", round(x[var[("x", p)]], 4), "tri", tri_p[p], "nT", nT_p[p])
        return
    t0 = time.time()
    r = milp(c, constraints=LinearConstraint(A, np.array(rhs_lo), np.array(rhs_hi)), integrality=integ, bounds=Bounds(0, np.inf), options=dict(time_limit=a.time, disp=True))
    print("MILP:", r.status, r.message, time.time() - t0)
    if r.x is not None:
        x = r.x
        sol = {p: round(x[var[("x", p)]]) for p in range(P) if x[var[("x", p)]] > 0.5}
        print("solution: line types", sol, "t =", round(x[var[("t",)]]))
        pickle.dump(dict(sol=sol, paths=paths), open(f"{E.DIR}/ilp_sol_{a.k}.pkl", "wb"))


if __name__ == "__main__":
    main()

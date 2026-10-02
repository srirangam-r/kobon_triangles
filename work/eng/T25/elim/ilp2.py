"""Integrality test v2: pooled ILP over the jointly tight language with sig-level choices at triple windows.
Constraints: sum x = 18; window usage; term-alternative pooling; conservation of every transfer column; sum tri sides = 282;
corner count (sum of triangle corners = 3T); triple-point incidences = 3 t; per configuration: role counts = mult * y_cfg;
parity of simple-vertex classes (frames = 2 * vertices).  Options: --flowers f fixes y(centre)=f, y(corner)=6f, y(X)=6-3f (Gauss-Bonnet flower reduction, sum c_P = 6).
usage: ilp2.py STATE_K [--flowers f] [--nopar] [--time T] [--tmin a] [--tmax b] [--enum N]"""
import sys, os, pickle, argparse, collections, time, itertools
from fractions import Fraction as F
ROOT = __import__("pathlib").Path(__file__).resolve().parents[4].as_posix()
sys.path.insert(0, ROOT + "/search"); sys.path.append(ROOT + "/work/t3"); sys.path.insert(0, ROOT + "/work/eng/T25/elim")
import numpy as np
import scipy.sparse as sp
from scipy.optimize import milp, LinearConstraint, Bounds, linprog
import elim as E
import ilp as I
import rule_lp_t25 as T
import rule_lp as RL

CENTRE = ("NNNNNN", (1, 1, 1, 1, 1, 1))
CORNER = ("NNNSSS", (1, 1, 1, 0, 1, 1))
XPTS = {("NSSNSS", (0, 1, 1, 0, 1, 1)), ("NSSSSS", (0, 1, 1, 0, 1, 1))}


def d4_class(bits):
    b = tuple(bits)
    imgs = []
    for s in (1, -1):
        for k in range(4):
            imgs.append(tuple(b[(k + s * i) % 4] for i in range(4)) if s == 1 else tuple(b[(k - i) % 4] for i in range(4)))
    return min(imgs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("k", type=int)
    ap.add_argument("--flowers", type=int, default=None)
    ap.add_argument("--nopar", action="store_true")
    ap.add_argument("--time", type=float, default=600)
    ap.add_argument("--tmin", type=int, default=None)
    ap.add_argument("--tmax", type=int, default=None)
    ap.add_argument("--tri", type=int, default=282)
    ap.add_argument("--lp", action="store_true")
    ap.add_argument("--obj", default=None, help="min_t | max_t")
    ap.add_argument("--nocorner", action="store_true")
    a = ap.parse_args()
    o, G, certs, paths, res = I.build(a.k)
    opt_ok, alt_ok = I.tight_sets(G, certs)
    nt = len(G.term_start)
    ends = np.append(G.term_start[1:], G.n_term_opts)
    WO = G.WO.tocsr()
    TO = G.TO.tocsr()
    term_has = np.array([alt_ok[G.term_start[t]:ends[t]].any() for t in range(nt)])
    opt_use = opt_ok.copy()
    for r in np.nonzero(opt_ok)[0]:
        ts = WO.indices[WO.indptr[r]:WO.indptr[r + 1]]
        if not term_has[ts].all(): opt_use[r] = False
    termid = {t: i for i, t in enumerate(G.term_list)}
    rowmap = {}
    for r in range(len(G.ov2)):
        j = int(G.opt_win[r])
        tids = []
        for k in range(WO.indptr[r], WO.indptr[r + 1]):
            tids += [int(WO.indices[k])] * int(WO.data[k])
        rowmap[(j, int(G.ov2[r]) if G.ov2[r] == int(G.ov2[r]) else float(G.ov2[r]), tuple(sorted(tids)))] = r
    P = len(paths)
    wins_of = [[int(G.ew[e]) for e in edges] + [tw] for (edges, tw, u) in paths]
    used_w = sorted({w for ws in wins_of for w in ws})
    # choices per window: list of (key, row, cfgrole or None)
    choices = {}
    for j in used_w:
        prev, cur, nxt = G.win_list[j]
        ch = []
        if cur.kind == "T":
            seen = {}
            for (sig, g, opt) in G.cat.sig_options(prev, cur, nxt):
                tids = tuple(sorted(termid[t] for t in opt[4]))
                v2 = opt[0]
                r = rowmap.get((j, int(v2) if v2 == int(v2) else float(v2), tids))
                if r is None or not opt_use[r]: continue
                chr_of = lambda info: "U" if info is None else ("T" if info[0] == "T" else "S")
                ring = [chr_of(nxt), "T" if sig[0] else "S", "T" if sig[2] else "S", chr_of(prev), "T" if sig[3] else "S", "T" if sig[1] else "S"]
                sec6 = (cur.bout[0], cur.h[0], cur.bin[0], cur.bin[1], cur.h[1], cur.bout[1])
                cr = T.cfg_role("".join(ring).replace("T", "N"), sec6, 0)
                key = (r, cr[0] if cr else None, cr[1] if cr else None)
                if key in seen: continue
                seen[key] = 1
                ch.append((sig, r, cr))
        else:
            lo = G.win_start[j]; hi = G.win_start[j + 1] if j + 1 < len(G.win_start) else len(G.opt_win)
            for r in range(lo, hi):
                if opt_use[r]: ch.append((None, r, None))
        choices[j] = ch
    bad = [j for j in used_w if not choices[j]]
    print("paths", P, "windows", len(used_w), "windows without usable choice", len(bad), flush=True)
    var = {}
    def V(key):
        if key not in var: var[key] = len(var)
        return var[key]
    for p in range(P): V(("x", p))
    for j in used_w:
        for ci, (sig, r, cr) in enumerate(choices[j]): V(("u", j, ci))
    termset = set()
    for j in used_w:
        for (sig, r, cr) in choices[j]:
            for t in WO.indices[WO.indptr[r]:WO.indptr[r + 1]]: termset.add(int(t))
    termalts = {}
    for t in sorted(termset):
        alts = [q for q in range(G.term_start[t], ends[t]) if alt_ok[q]]
        termalts[t] = alts
        for q in alts: V(("v", q))
    rows_i, rows_j, rows_v, lo_, hi_ = [], [], [], [], []
    def add_row(coefs, lo, hi):
        i = len(lo_)
        for k, x in coefs.items():
            if x != 0:
                rows_i.append(i); rows_j.append(k); rows_v.append(float(x))
        lo_.append(lo); hi_.append(hi)
    add_row({var[("x", p)]: 1 for p in range(P)}, 18, 18)
    m_pw = collections.defaultdict(collections.Counter)
    for p, ws in enumerate(wins_of):
        for w in ws: m_pw[w][p] += 1
    for j in used_w:
        co = collections.Counter()
        for ci in range(len(choices[j])): co[var[("u", j, ci)]] += 1
        for p, m in m_pw[j].items(): co[var[("x", p)]] -= m
        add_row(dict(co), 0, 0)
    tuse = collections.defaultdict(collections.Counter)
    for j in used_w:
        for ci, (sig, r, cr) in enumerate(choices[j]):
            for k in range(WO.indptr[r], WO.indptr[r + 1]):
                tuse[int(WO.indices[k])][var[("u", j, ci)]] += WO.data[k]
    for t in sorted(termset):
        co = collections.Counter()
        for q in termalts[t]: co[var[("v", q)]] += 1
        for vi, m in tuse[t].items(): co[vi] -= m
        add_row(dict(co), 0, 0)
    colrows = collections.defaultdict(collections.Counter)
    for t in sorted(termset):
        for q in termalts[t]:
            for k in range(TO.indptr[q], TO.indptr[q + 1]):
                c = int(TO.indices[k]); key = G.cat.keys[c]
                if key in (("a",), ("alpha",), ("wr",)): continue
                colrows[c][var[("v", q)]] += TO.data[k]
    for c, co in colrows.items(): add_row(dict(co), 0, 0)
    # triangle sides and T incidences
    tri_p, nT_p, cor_p, sv_class = [], [], [], []
    for (edges, tw, u) in paths:
        fr = [G.nodes[int(G.src[e])][1] for e in edges] + [G.nodes[u][1]]
        tri_p.append(sum(f.bout[0] + f.bout[1] for f in fr))
        nT_p.append(sum(1 for f in fr if f.kind == "T"))
        c_ = F(0); cls = collections.Counter()
        for f in fr:
            if f.kind == "S":
                sec = (f.bout[0], f.bin[0], f.bin[1], f.bout[1])
                c_ += F(sum(sec), 2)
                cls[d4_class(sec)] += 1
            else:
                c_ += F(f.bout[0] + f.h[0] + f.bin[0] + f.bin[1] + f.h[1] + f.bout[1], 3)
        cor_p.append(c_); sv_class.append(cls)
    add_row({var[("x", p)]: tri_p[p] for p in range(P)}, a.tri, a.tri)
    # end pairing at simple vertices: sum over S frames of (ub flags) = number of S frames that are first/last on their line
    endc = []
    for (edges, tw, u) in paths:
        fr = [G.nodes[int(G.src[e])][1] for e in edges] + [G.nodes[u][1]]
        endc.append(sum(f.ub[0] + f.ub[1] for f in fr if f.kind == "S") - sum(1 for i, f in enumerate(fr) if f.kind == "S" and (i == 0 or i == len(fr) - 1)))
    add_row({var[("x", p)]: endc[p] for p in range(P) if endc[p]}, 0, 0)
    if not a.nocorner:
        add_row({var[("x", p)]: float(cor_p[p]) for p in range(P)}, a.tri, a.tri)
    tv = V(("t",))
    co = {var[("x", p)]: nT_p[p] for p in range(P)}
    co[tv] = -3
    add_row(co, 0, 0)
    if a.tmin is not None or a.tmax is not None:
        add_row({tv: 1}, a.tmin if a.tmin is not None else 0, a.tmax if a.tmax is not None else 1000)
    # cfg balance
    cfgs = set()
    for j in used_w:
        for (sig, r, cr) in choices[j]:
            if cr: cfgs.add(cr[0])
    ycfg = {c: V(("y", c)) for c in cfgs}
    for c in cfgs:
        row = T.cfg_row(c)
        for role, mult in row.items():
            co = collections.Counter()
            for j in used_w:
                for ci, (sig, r, cr) in enumerate(choices[j]):
                    if cr and cr[0] == c and cr[1] == role: co[var[("u", j, ci)]] += 1
            co[ycfg[c]] -= mult
            add_row(dict(co), 0, 0)
    # frames in T windows without cfg (cr None) must not exist
    for j in used_w:
        for ci, (sig, r, cr) in enumerate(choices[j]):
            if choices[j] and G.win_list[j][1].kind == "T" and cr is None:
                print("warning: T choice without cfg/role", j)
    if not a.nopar:
        classes = set(c for cls in sv_class for c in cls)
        for cl in classes:
            yv = V(("ys", cl))
            co = {var[("x", p)]: sv_class[p][cl] for p in range(P) if sv_class[p][cl]}
            co[yv] = -2
            add_row(co, 0, 0)
    if a.flowers is not None:
        f = a.flowers
        def yc(pred):
            return {ycfg[c]: 1 for c in cfgs if pred(c)}
        add_row(yc(lambda c: c == CENTRE), f, f)
        add_row(yc(lambda c: c == CORNER), 6 * f, 6 * f)
        add_row(yc(lambda c: c in XPTS), 6 - 3 * f, 6 - 3 * f)
        add_row(yc(lambda c: c not in XPTS and c != CENTRE and c != CORNER), 0, 0)
    nv = len(var)
    A = sp.csr_matrix((rows_v, (rows_i, rows_j)), shape=(len(lo_), nv))
    print("variables", nv, "constraints", A.shape, "cfgs", sorted(cfgs), flush=True)
    c = np.zeros(nv)
    if a.obj == "min_t": c[tv] = 1
    if a.obj == "max_t": c[tv] = -1
    if a.lp:
        r = linprog(c, A_eq=A, b_eq=np.array(lo_), bounds=[(0, None)] * nv, method="highs") if all(l == h for l, h in zip(lo_, hi_)) else None
        print("LP relaxation:", None if r is None else (r.status, r.message))
        return
    t0 = time.time()
    r = milp(c, constraints=LinearConstraint(A, np.array(lo_), np.array(hi_)), integrality=np.ones(nv), bounds=Bounds(0, np.inf), options=dict(time_limit=a.time, disp=False))
    print("MILP:", r.status, r.message, "%.1fs" % (time.time() - t0))
    if r.x is not None:
        x = r.x
        sol = {p: int(round(x[var[("x", p)]])) for p in range(P) if x[var[("x", p)]] > 0.5}
        print("t =", int(round(x[tv])), " y_cfg:", {c_: int(round(x[ycfg[c_]])) for c_ in cfgs if x[ycfg[c_]] > 0.5})
        def fr_(f): return f"{f.kind}{''.join(str(b) for b in f.bin)}{''.join(str(b) for b in f.bout)}" + (f"h{''.join(map(str, f.h))}" if f.kind == "T" else "")
        for p, n in sorted(sol.items()):
            edges, tw, u = paths[p]
            fr = [G.nodes[int(G.src[e])][1] for e in edges] + [G.nodes[u][1]]
            print(f"  {n} x path {p}: tri {tri_p[p]}, nT {nT_p[p]}: " + " ".join(fr_(f) for f in fr))
        pickle.dump(dict(sol=sol, t=int(round(x[tv]))), open(f"{E.DIR}/ilp2_sol_{a.k}_{a.flowers}.pkl", "wb"))
        def fr_full(f):
            return f"{f.kind}[bin={f.bin} bout={f.bout} ub={f.ub} h={f.h} ain={f.ain} aout={f.aout}]"
        lines = []
        for p, n in sorted(sol.items()):
            edges, tw, u = paths[p]
            fr = [G.nodes[int(G.src[e])][1] for e in edges] + [G.nodes[u][1]]
            wl = [int(G.ew[e]) for e in edges] + [tw]
            lines.append(f"LINE TYPE path {p}: count {n}, triangle sides {tri_p[p]}, triple frames {nT_p[p]}")
            for i, (f, j) in enumerate(zip(fr, wl)):
                s_ = f"  v{i:2d} {fr_full(f)}"
                if f.kind == "T":
                    us = [(choices[j][ci][0], choices[j][ci][2], round(x[var[('u', j, ci)]], 3)) for ci in range(len(choices[j])) if x[var[('u', j, ci)]] > 1e-9]
                    s_ += f"  window {j}: sig choices used (sig, (cfg,role), pooled count) = {us}; all tight sigs {[(c_[0], c_[2]) for c_ in choices[j]]}"
                lines.append(s_)
        open(f"{E.DIR}/ilp2_types_{a.k}_{a.flowers}.txt", "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

"""Integrality ILP v5: line types q = (tight path p, sig/cfg assignment sigma to its triple windows), adjacency rules for triple runs
(centre only next to role-1 corners, role-1 corner only next to a centre, role-0/2 corners next to role-0/2 corners, X next to X),
only the 4 jointly tight configurations.  Same conservation / tri / corner / parity / end-pairing constraints as ilp2.
usage: ilp5.py STATE_K [--flowers f] [--minT4 n|--noT4] [--enum N] [--support]"""
import sys, os, pickle, argparse, collections, time, itertools
from fractions import Fraction as F
ROOT = __import__("pathlib").Path(__file__).resolve().parents[4].as_posix()
sys.path.insert(0, ROOT + "/search"); sys.path.append(ROOT + "/work/t3"); sys.path.insert(0, ROOT + "/work/eng/T25/elim")
import numpy as np
import scipy.sparse as sp
from scipy.optimize import milp, LinearConstraint, Bounds
import elim as E
import ilp as I
import ilp2 as I2
import rule_lp_t25 as T

CENTRE, CORNER, XPTS = I2.CENTRE, I2.CORNER, I2.XPTS
SURV = {CENTRE, CORNER} | XPTS


def cls_of(cr):
    cfg, role = cr
    if cfg == CENTRE: return "O"
    if cfg == CORNER: return "C%d" % role
    if cfg in XPTS: return "X"
    return "?"


def adj_ok(c1, c2):
    a, b = cls_of(c1), cls_of(c2)
    if a == "O": return b == "C1"
    if b == "O": return a == "C1"
    if a == "C1" or b == "C1": return False
    if a in ("C0", "C2") and b in ("C0", "C2"): return True
    if a == "X" and b == "X": return True
    return False


def get_args(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("k", type=int)
    ap.add_argument("--flowers", type=int, default=None)
    ap.add_argument("--time", type=float, default=600)
    ap.add_argument("--tri", type=int, default=282)
    ap.add_argument("--minT4", type=int, default=None)
    ap.add_argument("--noT4", action="store_true")
    ap.add_argument("--enum", type=int, default=0)
    ap.add_argument("--support", action="store_true")
    ap.add_argument("--noadj", action="store_true")
    ap.add_argument("--pair", action="store_true", help="exact vertex pairing (wiring-diagram convention) for simple and triple vertices")
    ap.add_argument("--obj", default=None)
    ap.add_argument("--sigrange", action="store_true", help="min/max total count of every line SHAPE over all solutions")
    ap.add_argument("--sigenum", type=int, default=0, help="enumerate distinct multisets of line SHAPES (tags + start/mid/end) up to N")
    return ap.parse_args(argv)


def signature_tags(M, q):
    G, paths, choices, wins_of = M["G"], M["paths"], M["choices"], M["wins_of"]
    p, sg = M["types"][q]
    tags = []
    for i, ci in sorted(sg.items()):
        cr = choices[wins_of[p][i]][ci][2]
        tags.append(f"{cls_of(cr)}/{cr[0][0]}r{cr[1]}" if cls_of(cr) != "O" else "O")
    return tuple(tags)


def signature(M, q):
    G, paths, choices, wins_of = M["G"], M["paths"], M["choices"], M["wins_of"]
    p, sg = M["types"][q]
    L = len(wins_of[p])
    tags = []; where = []
    for i, ci in sorted(sg.items()):
        cr = choices[wins_of[p][i]][ci][2]
        tags.append(cls_of(cr))
        where.append("S" if i <= 1 else "E" if i >= L - 2 else "M")
    return (len(sg), tuple(tags), tuple(where))


def build(a):
    o, G, certs, paths, res = I.build(a.k)
    opt_ok, alt_ok = I.tight_sets(G, certs)
    nt = len(G.term_start)
    ends = np.append(G.term_start[1:], G.n_term_opts)
    WO = G.WO.tocsr(); TO = G.TO.tocsr()
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
        for k in range(WO.indptr[r], WO.indptr[r + 1]): tids += [int(WO.indices[k])] * int(WO.data[k])
        rowmap[(j, float(G.ov2[r]), tuple(sorted(tids)))] = r
    P = len(paths)
    wins_of = [[int(G.ew[e]) for e in edges] + [tw] for (edges, tw, u) in paths]
    used_w = sorted({w for ws in wins_of for w in ws})
    choices = {}
    for j in used_w:
        prev, cur, nxt = G.win_list[j]
        ch = []
        if cur.kind == "T":
            seen = {}
            for (sig, g, opt) in G.cat.sig_options(prev, cur, nxt):
                tids = tuple(sorted(termid[t] for t in opt[4]))
                r = rowmap.get((j, float(opt[0]), tids))
                if r is None or not opt_use[r]: continue
                chr_of = lambda info: "U" if info is None else ("T" if info[0] == "T" else "S")
                ring = [chr_of(nxt), "T" if sig[0] else "S", "T" if sig[2] else "S", chr_of(prev), "T" if sig[3] else "S", "T" if sig[1] else "S"]
                sec6 = (cur.bout[0], cur.h[0], cur.bin[0], cur.bin[1], cur.h[1], cur.bout[1])
                cr = T.cfg_role("".join(ring).replace("T", "N"), sec6, 0)
                if cr is None or cr[0] not in SURV: continue
                key = (r, cr[0], cr[1])
                if key in seen: continue
                seen[key] = 1
                ch.append((sig, r, cr))
        else:
            lo = G.win_start[j]; hi = G.win_start[j + 1] if j + 1 < len(G.win_start) else len(G.opt_win)
            for r in range(lo, hi):
                if opt_use[r]: ch.append((None, r, None))
        choices[j] = ch
    # types
    types = []
    for p, ws in enumerate(wins_of):
        tpos = [i for i, j in enumerate(ws) if G.win_list[j][1].kind == "T"]
        if any(not choices[ws[i]] for i in tpos): continue
        for sigma in itertools.product(*[range(len(choices[ws[i]])) for i in tpos]):
            if not a.noadj:
                lab = dict(zip(tpos, [choices[ws[i]][ci][2] for i, ci in zip(tpos, sigma)]))
                ok = True
                for i in tpos:
                    if i + 1 in lab and not adj_ok(lab[i], lab[i + 1]): ok = False; break
                if not ok: continue
                # T-run ends: a centre needs both neighbours, corners exactly one T neighbour: guaranteed by ring kinds
            types.append((p, dict(zip(tpos, sigma))))
    print("paths", P, "types", len(types), "windows", len(used_w), flush=True)
    return dict(o=o, G=G, certs=certs, paths=paths, choices=choices, types=types, wins_of=wins_of, used_w=used_w, WO=WO, TO=TO, alt_ok=alt_ok, ends=ends, nt=nt)


def frames_of(G, path):
    edges, tw, u = path
    return [G.nodes[int(G.src[e])][1] for e in edges] + [G.nodes[u][1]]


def model(a, M):
    G, paths, choices, types, wins_of, used_w, WO, TO, alt_ok, ends = (M[k] for k in ("G", "paths", "choices", "types", "wins_of", "used_w", "WO", "TO", "alt_ok", "ends"))
    Q = len(types)
    var = {}
    def V(key):
        if key not in var: var[key] = len(var)
        return var[key]
    for q in range(Q): V(("x", q))
    ROWS = []
    def add_row(coefs, lo, hi):
        ROWS.append(({k: float(x) for k, x in coefs.items() if x != 0}, lo, hi))
    # usage expressions
    Sw = [j for j in used_w if G.win_list[j][1].kind == "S"]
    Tw = [j for j in used_w if G.win_list[j][1].kind == "T"]
    for j in Sw:
        for ci in range(len(choices[j])): V(("u", j, ci))
    cnt_tq = collections.defaultdict(collections.Counter)      # (j,ci) -> {q: count}
    cnt_sw = collections.defaultdict(collections.Counter)      # S window j -> {q: count}
    for q, (p, sg) in enumerate(types):
        ws = wins_of[p]
        for i, j in enumerate(ws):
            if i in sg: cnt_tq[(j, sg[i])][q] += 1
            elif G.win_list[j][1].kind == "S": cnt_sw[j][q] += 1
    add_row({var[("x", q)]: 1 for q in range(Q)}, 18, 18)
    for j in Sw:
        co = collections.Counter()
        for ci in range(len(choices[j])): co[var[("u", j, ci)]] += 1
        for q, m in cnt_sw[j].items(): co[var[("x", q)]] -= m
        add_row(dict(co), 0, 0)
    # usage of choices as linear expressions
    def usage(j, ci):
        if G.win_list[j][1].kind == "S": return {var[("u", j, ci)]: 1}
        return {var[("x", q)]: m for q, m in cnt_tq[(j, ci)].items()}
    termset = set()
    for j in used_w:
        for (sig, r, cr) in choices[j]:
            for t in WO.indices[WO.indptr[r]:WO.indptr[r + 1]]: termset.add(int(t))
    termalts = {}
    for t in sorted(termset):
        alts = [q for q in range(G.term_start[t], ends[t]) if alt_ok[q]]
        termalts[t] = alts
        for qq in alts: V(("v", qq))
    tuse = collections.defaultdict(collections.Counter)
    for j in used_w:
        for ci, (sig, r, cr) in enumerate(choices[j]):
            us = usage(j, ci)
            for k in range(WO.indptr[r], WO.indptr[r + 1]):
                t = int(WO.indices[k])
                for vi, m in us.items(): tuse[t][vi] += m * WO.data[k]
    for t in sorted(termset):
        co = collections.Counter()
        for qq in termalts[t]: co[var[("v", qq)]] += 1
        for vi, m in tuse[t].items(): co[vi] -= m
        add_row(dict(co), 0, 0)
    colrows = collections.defaultdict(collections.Counter)
    for t in sorted(termset):
        for qq in termalts[t]:
            for k in range(TO.indptr[qq], TO.indptr[qq + 1]):
                c = int(TO.indices[k]); key = G.cat.keys[c]
                if key in (("a",), ("alpha",), ("wr",)): continue
                colrows[c][var[("v", qq)]] += TO.data[k]
    for c, co in colrows.items(): add_row(dict(co), 0, 0)
    # per type numbers
    tri_q, nT_q, cor_q, cls_q, end_q = [], [], [], [], []
    for (p, sg) in types:
        fr = frames_of(G, paths[p])
        tri_q.append(sum(f.bout[0] + f.bout[1] for f in fr))
        nT_q.append(sum(1 for f in fr if f.kind == "T"))
        c_ = F(0); cls = collections.Counter()
        for f in fr:
            if f.kind == "S":
                sec = (f.bout[0], f.bin[0], f.bin[1], f.bout[1]); c_ += F(sum(sec), 2); cls[I2.d4_class(sec)] += 1
            else:
                c_ += F(f.bout[0] + f.h[0] + f.bin[0] + f.bin[1] + f.h[1] + f.bout[1], 3)
        cor_q.append(c_); cls_q.append(cls)
        end_q.append(sum(f.ub[0] + f.ub[1] for f in fr if f.kind == "S") - sum(1 for i, f in enumerate(fr) if f.kind == "S" and (i == 0 or i == len(fr) - 1)))
    add_row({var[("x", q)]: tri_q[q] for q in range(Q)}, a.tri, a.tri)
    add_row({var[("x", q)]: float(cor_q[q]) for q in range(Q)}, a.tri, a.tri)
    add_row({var[("x", q)]: end_q[q] for q in range(Q)}, 0, 0)
    tv = V(("t",))
    co = {var[("x", q)]: nT_q[q] for q in range(Q)}; co[tv] = -3
    add_row(co, 0, 0)
    cfgs = set()
    for j in Tw:
        for (sig, r, cr) in choices[j]: cfgs.add(cr[0])
    ycfg = {c: V(("y", c)) for c in cfgs}
    for c in cfgs:
        for role, mult in T.cfg_row(c).items():
            co = collections.Counter()
            for j in Tw:
                for ci, (sig, r, cr) in enumerate(choices[j]):
                    if cr[0] == c and cr[1] == role:
                        for vi, m in usage(j, ci).items(): co[vi] += m
            co[ycfg[c]] -= mult
            add_row(dict(co), 0, 0)
    classes = set(c for cls in cls_q for c in cls)
    for cl in classes:
        yv = V(("ys", cl))
        co = {var[("x", q)]: cls_q[q][cl] for q in range(Q) if cls_q[q][cl]}; co[yv] = -2
        add_row(co, 0, 0)

    if a.pair:
        kd = lambda info: None if info is None else info[0]
        code = {"T": 1, "S": 2}
        def flag(f, sd):
            v = 0
            if f.bin[sd]: v = f.ain[sd] or v
            if f.bout[sd]: v = f.aout[sd] or v
            return v
        def compat_S(ja, jb):
            pa, fa, na = G.win_list[ja]; pb, fb, nb = G.win_list[jb]
            sa = (fa.bout[0], fa.bin[0], fa.bin[1], fa.bout[1]); sb = (fb.bout[0], fb.bin[0], fb.bin[1], fb.bout[1])
            if sb != (sa[1], sa[2], sa[3], sa[0]): return False
            if fa.ub[0] != int(nb is None) or fa.ub[1] != int(pb is None): return False
            if fb.ub[0] != int(pa is None) or fb.ub[1] != int(na is None): return False
            for (fl, other) in ((flag(fa, 0), kd(nb)), (flag(fa, 1), kd(pb)), (flag(fb, 0), kd(pa)), (flag(fb, 1), kd(na))):
                if fl and code.get(other) != fl: return False
            return True
        zS = {}
        for ja in Sw:
            for jb in Sw:
                if compat_S(ja, jb): zS[(ja, jb)] = V(("zS", ja, jb))
        for j in Sw:
            co = collections.Counter()
            for q, mm in cnt_sw[j].items(): co[var[("x", q)]] += mm
            for (ja, jb), vi in zS.items():
                if ja == j: co[vi] -= 1
                if jb == j: co[vi] -= 1
            add_row(dict(co), 0, 0)
        info = {}
        Tch = [(j, ci) for j in Tw for ci in range(len(choices[j]))]
        for (j, ci) in Tch:
            pv, fc, nx = G.win_list[j]
            info[(j, ci)] = dict(sec=(fc.bout[0], fc.h[0], fc.bin[0], fc.bin[1], fc.h[1], fc.bout[1]), sig=choices[j][ci][0], pk=kd(pv), nk=kd(nx))
        rot = lambda t, k: tuple(t[(i + k) % 6] for i in range(6))
        isT = lambda k: int(k == "T")
        bysec = collections.defaultdict(list)
        for c_ in Tch: bysec[info[c_]["sec"]].append(c_)
        zT = {}
        for ca in Tch:
            ia = info[ca]
            for cb in bysec.get(rot(ia["sec"], 1), []):
                ib = info[cb]
                if ia["sig"][0] != isT(ib["nk"]) or ia["sig"][3] != isT(ib["pk"]): continue
                if ib["sig"][2] != isT(ia["pk"]) or ib["sig"][1] != isT(ia["nk"]): continue
                for cc in bysec.get(rot(ia["sec"], 2), []):
                    ic = info[cc]
                    if ia["sig"][2] != isT(ic["nk"]) or ia["sig"][1] != isT(ic["pk"]): continue
                    if ib["sig"][0] != isT(ic["nk"]) or ib["sig"][3] != isT(ic["pk"]): continue
                    if ic["sig"][0] != isT(ia["pk"]) or ic["sig"][2] != isT(ib["pk"]): continue
                    if ic["sig"][3] != isT(ia["nk"]) or ic["sig"][1] != isT(ib["nk"]): continue
                    zT[(ca, cb, cc)] = V(("zT", ca, cb, cc))
        print("pairing variables: S pairs", len(zS), "T triples", len(zT), flush=True)
        for c_ in Tch:
            co = collections.Counter()
            for vi, mm in usage(*c_).items(): co[vi] += mm
            for tri_, vi in zT.items():
                for c2 in tri_:
                    if c2 == c_: co[vi] -= 1
            add_row(dict(co), 0, 0)
    if a.flowers is not None:
        f = a.flowers
        yc = lambda pred: {ycfg[c]: 1 for c in cfgs if pred(c)}
        add_row(yc(lambda c: c == CENTRE), f, f)
        add_row(yc(lambda c: c == CORNER), 6 * f, 6 * f)
        add_row(yc(lambda c: c in XPTS), 6 - 3 * f, 6 - 3 * f)
    if a.minT4 is not None: add_row({var[("x", q)]: 1 for q in range(Q) if nT_q[q] >= 4}, a.minT4, 1000)
    if a.noT4: add_row({var[("x", q)]: 1 for q in range(Q) if nT_q[q] >= 4}, 0, 0)
    return dict(ROWS=ROWS, var=var, nT_q=nT_q, tri_q=tri_q, tv=tv, ycfg=ycfg, Q=Q)


def assemble(rows, ncols):
    ri, ci, vv = [], [], []
    for i, (co, lo, hi) in enumerate(rows):
        for k, x in co.items(): ri.append(i); ci.append(k); vv.append(x)
    return sp.csr_matrix((vv, (ri, ci)), shape=(len(rows), ncols)), np.array([r[1] for r in rows], dtype=float), np.array([r[2] for r in rows], dtype=float)


def describe(M, q):
    G, paths, choices, wins_of = M["G"], M["paths"], M["choices"], M["wins_of"]
    p, sg = M["types"][q]
    fr = frames_of(G, paths[p])
    tags = []
    for i, ci in sorted(sg.items()):
        cr = choices[wins_of[p][i]][ci][2]
        tags.append(f"pos{i}:{cls_of(cr)}({cr[0][0]}/r{cr[1]})")
    word = " ".join(f"{f.kind}{''.join(str(b) for b in f.bin)}{''.join(str(b) for b in f.bout)}" + (f"h{''.join(map(str, f.h))}" if f.kind == "T" else "") for f in fr)
    return f"path {p} len {len(fr)} nT {len(sg)} T:[{' '.join(tags)}]", word


def main(argv=None):
    a = get_args(argv)
    M = build(a)
    m = model(a, M)
    ROWS, var, Q = m["ROWS"], m["var"], m["Q"]
    nv = len(var)
    print("variables", nv, "constraints", len(ROWS), flush=True)
    xs = [var[("x", q)] for q in range(Q)]
    Ma, lo_a, hi_a = assemble(ROWS, nv)
    c = np.zeros(nv)
    if a.obj == "min_t": c[m["tv"]] = 1
    if a.support:
        table = {}
        for q in range(Q):
            cc = np.zeros(nv); cc[xs[q]] = -1.0
            r = milp(cc, constraints=LinearConstraint(Ma, lo_a, hi_a), integrality=np.ones(nv), bounds=Bounds(0, np.inf), options=dict(time_limit=60, disp=False))
            table[q] = int(round(-r.fun)) if r.x is not None else 0
        feas = {q: v for q, v in table.items() if v > 0}
        print("feasible line types:", len(feas), "of", Q, flush=True)
        out = []
        for q, v in sorted(feas.items()):
            d, w = describe(M, q)
            out.append(f"type {q}: max mult {v}, {d}; word {w}")
        tag = f"{a.k}_{a.flowers}_{a.minT4}_{int(a.noT4)}_{int(a.noadj)}"
        open(f"{E.DIR}/ilp5_support_{tag}.txt", "w").write("\n".join(out) + "\n")
        for l in out[:80]: print(l[:230])
        return
    if a.sigrange:
        sigs = collections.defaultdict(list)
        for q in range(Q): sigs[signature_tags(M, q)].append(q)
        out = []
        for sgn, qs in sorted(sigs.items(), key=lambda t: str(t[0])):
            rng = []
            for sign in (1.0, -1.0):
                cc = np.zeros(nv)
                for q in qs: cc[xs[q]] = sign
                r = milp(cc, constraints=LinearConstraint(Ma, lo_a, hi_a), integrality=np.ones(nv), bounds=Bounds(0, np.inf), options=dict(time_limit=60, disp=False))
                rng.append(int(round(r.fun * sign)) if r.x is not None else None)
            out.append((sgn, len(qs), rng))
            print(f"tags={list(sgn)}: {len(qs)} types, total count range {rng}", flush=True)
        return
    if a.sigenum:
        sigs = collections.defaultdict(list)
        for q in range(Q): sigs[signature(M, q)].append(q)
        print("signatures:", len(sigs), flush=True)
        rows = list(ROWS); ncols = nv; ub = [np.inf] * nv
        ysig = {}
        for sgn, qs in sigs.items():
            ysig[sgn] = ncols; ncols += 1; ub.append(np.inf)
            rows.append(({**{xs[q]: 1.0 for q in qs}, ysig[sgn]: -1.0}, 0, 0))
        sols = []
        names = sorted(sigs, key=str)
        while len(sols) < a.sigenum:
            Mm, lo2, hi2 = assemble(rows, ncols)
            r = milp(np.zeros(ncols), constraints=LinearConstraint(Mm, lo2, hi2), integrality=np.ones(ncols), bounds=Bounds(np.zeros(ncols), np.array(ub)), options=dict(time_limit=a.time, disp=False))
            if r.x is None:
                print("enumeration finished:", r.message, flush=True); break
            x = np.rint(r.x)
            sol = {sgn: int(x[ysig[sgn]]) for sgn in sigs if x[ysig[sgn]] > 0.5}
            sols.append(sol)
            print(f"solution {len(sols)}: t={int(round(x[m['tv']]))} " + "; ".join(f"{n} x nT{k[0]}{list(k[1])}{''.join(k[2])}" for k, n in sorted(sol.items(), key=lambda t: str(t[0]))), flush=True)
            co = {ysig[sgn]: 1.0 for sgn in sigs if sgn not in sol}
            for sgn, xv in sol.items():
                ap_, bp_ = ncols, ncols + 1
                ncols += 2; ub += [1, 1]
                co[ap_] = 1.0; co[bp_] = 1.0
                rows.append(({ysig[sgn]: 1.0, ap_: 18.0}, -np.inf, xv - 1 + 18))
                rows.append(({ysig[sgn]: 1.0, bp_: -18.0}, xv + 1 - 18, np.inf))
            rows.append((co, 1, np.inf))
        pickle.dump(dict(sols=sols), open(f"{E.DIR}/ilp5_sigenum_{a.k}_{a.flowers}_{a.minT4}_{int(a.noT4)}.pkl", "wb"))
        return
    if a.enum:
        rows = list(ROWS); ncols = nv; ub = [np.inf] * nv
        sols = []
        while len(sols) < a.enum:
            Mm, lo2, hi2 = assemble(rows, ncols)
            r = milp(np.zeros(ncols), constraints=LinearConstraint(Mm, lo2, hi2), integrality=np.ones(ncols), bounds=Bounds(np.zeros(ncols), np.array(ub)), options=dict(time_limit=a.time, disp=False))
            if r.x is None:
                print("enumeration finished:", r.message, flush=True); break
            x = np.rint(r.x)
            sol = {q: int(x[xs[q]]) for q in range(Q) if x[xs[q]] > 0.5}
            sols.append(sol)
            print(f"solution {len(sols)}: t={int(round(x[m['tv']]))} types " + " ".join(f"{n}x{q}(nT{m['nT_q'][q]})" for q, n in sorted(sol.items())), flush=True)
            co = {xs[q]: 1.0 for q in range(Q) if q not in sol}
            for q, xv in sol.items():
                ap_, bp_ = ncols, ncols + 1
                ncols += 2; ub += [1, 1]
                co[ap_] = 1.0; co[bp_] = 1.0
                rows.append(({xs[q]: 1.0, ap_: 18.0}, -np.inf, xv - 1 + 18))
                rows.append(({xs[q]: 1.0, bp_: -18.0}, xv + 1 - 18, np.inf))
            rows.append((co, 1, np.inf))
        tag = f"{a.k}_{a.flowers}_{a.minT4}_{int(a.noT4)}_{int(a.noadj)}"
        pickle.dump(dict(sols=sols, types=[(p, sg) for (p, sg) in M["types"]]), open(f"{E.DIR}/ilp5_enum_{tag}.pkl", "wb"))
        with open(f"{E.DIR}/ilp5_enum_{tag}.txt", "w") as fo:
            for i, sol in enumerate(sols):
                fo.write(f"solution {i + 1}\n")
                for q, n in sorted(sol.items()):
                    d, w = describe(M, q)
                    fo.write(f"  {n} x type {q}: {d}\n")
        return
    r = milp(c, constraints=LinearConstraint(Ma, lo_a, hi_a), integrality=np.ones(nv), bounds=Bounds(0, np.inf), options=dict(time_limit=a.time, disp=False))
    print("MILP:", r.status, r.message)
    if r.x is not None:
        x = np.rint(r.x)
        print("t =", int(round(x[m["tv"]])))
        for q in range(Q):
            if x[xs[q]] > 0.5:
                d, w = describe(M, q)
                print(f"  {int(x[xs[q]])} x type {q}: {d}\n      {w}")


if __name__ == "__main__":
    main()

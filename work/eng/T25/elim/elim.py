"""Iterated elimination (T25).  G_k = reduced graph (set of allowed windows).  Any 94's lines are paths of G_k.
A certificate w (final >= 0 on all G_k paths) that is strict (>= delta) on all paths through a window set removes that set (group or single).
Every acceptance is verified in exact integer arithmetic on the reduced graph.  Joint tightness under all accepted certificates shrinks G further.
usage:  elim.py init                     -> round 0: joint tight structure of the 5 initial certificates (state_0.pkl)
        elim.py round K [--jobs N] [--kinds groups,T,S] [--limit M]
        elim.py report K"""
import sys, os, pickle, argparse, collections, time, json, itertools, traceback
from fractions import Fraction as F
ROOT = __import__("pathlib").Path(__file__).resolve().parents[4].as_posix()
sys.path.insert(0, ROOT + "/search"); sys.path.append(ROOT + "/work/t3")
import __main__
import numpy as np
import flint
import rule_lp as RL, rule_lp_t25 as T
import line_automaton as LA
__main__.EFrame = RL.EFrame
DIR = ROOT + "/work/eng/T25/elim"
INITIAL = [("FD24", 144), ("FC", 16), ("FS1", 24), ("FS2", 16), ("FS3", 4)]
DENS = (8, 16, 24, 32, 48, 64, 96, 144, 192, 288, 384, 576, 720, 960, 1152, 1440, 2880)
W17 = 17


def make_o():
    ap = T.add_args(argparse.ArgumentParser())
    return ap.parse_args(["lp", "--class", "full", "--split", "--alpha", "--celldom", "--wr", "--sv", "--tri", "--pt", "--eps", "0"])


def cert_vec(cat, cert, K):
    w = np.zeros(K)
    for k, x in cert["w"].items():
        i = cat.idx.get(k)
        if i is not None and i < K:
            w[i] = x
    return w


def opt_vals(opts, w, D):
    """proper scaled option values D*v2 + 2 sum_terms min_alt w.vec"""
    return [D * o_[0] + (T.option_value(o_, w) - o_[0]) for o_ in opts]


def joint_options(G, win, cvecs):
    prev, cur, nxt = win
    if cur.kind == "T":
        opts = G.cat.sig_options(prev, cur, nxt)
        keys = [(s, g) for (s, g, _) in opts]
        os_ = [o_ for (_, _, o_) in opts]
    else:
        os_ = G.cat.window_options(prev, cur, nxt)
        keys = [None] * len(os_)
    if not os_:
        return []
    common = None
    for (w, D) in cvecs:
        v = opt_vals(os_, w, D)
        m = min(v)
        s = {i for i, x in enumerate(v) if x <= m + 1e-7}
        common = s if common is None else (common & s)
    if not common:
        return []
    return [keys[i] for i in sorted(common)] if cur.kind == "T" else [None]


def joint_structure(o, cat, allowed, certs, W=W17, export=None, G=None):
    """graph restricted to `allowed` windows; exact jointly tight edges/terminals under all certificates (common tight option per window).
    returns dict(windows=set of windows on jointly tight edges/terminals, jopt=..., stats)"""
    G = G if G is not None else T.build_graph(o, cat=cat, allowed=allowed)
    K = G.K
    cvecs = [(cert_vec(cat, c, K), c["D"]) for c in certs]
    comb = np.zeros(len(G.win_list))
    for (w, D) in cvecs:
        wm, _ = G.window_min(w, D)
        comb += wm / D
    jopt = {win: joint_options(G, win, cvecs) for win in G.win_list}
    ok_w = np.array([bool(jopt[win]) for win in G.win_list])
    INF = 1e18
    cw = np.where(ok_w, comb, INF)
    N = G.N
    ku = np.array([2 if G.nodes[i][1].kind == "T" else 1 for i in range(N)])
    ewt = cw[G.ew]
    unit_e = ku[G.src]
    target = 2.0 * len(certs)
    Fw = np.full((W + 1, N), INF); Fw[0][G.starts] = 0.0
    for c in range(W + 1):
        for c0 in (1, 2):
            if c + c0 > W: continue
            m = (unit_e == c0) & (Fw[c][G.src] < INF)
            np.minimum.at(Fw[c + c0], G.dst[m], Fw[c][G.src[m]] + ewt[m])
    Bk = np.full((W + 1, N), INF)
    for u, wi in zip(G.tn, G.tw):
        un = ku[u]
        if un <= W and cw[wi] < INF: Bk[un][u] = min(Bk[un][u], cw[wi])
    for c in range(W + 1):
        for c0 in (1, 2):
            if c - c0 < 0: continue
            m = unit_e == c0
            np.minimum.at(Bk[c], G.src[m], Bk[c - c0][G.dst[m]] + ewt[m])
    tight = np.zeros(len(G.src), dtype=bool)
    best = INF
    for c in range(W + 1):
        for c0 in (1, 2):
            rem = W - c - c0
            if rem < 0: continue
            m = unit_e == c0
            tot = Fw[c][G.src] + ewt + Bk[rem][G.dst]
            tight |= m & (np.abs(tot - target) < 1e-6)
            if m.any(): best = min(best, tot[m].min())
    tterm = np.zeros(len(G.tn), dtype=bool)
    for i, (u, wi) in enumerate(zip(G.tn, G.tw)):
        c = W - ku[u]
        if c >= 0 and cw[wi] < INF:
            best = min(best, Fw[c][u] + cw[wi])
            if abs(Fw[c][u] + cw[wi] - target) < 1e-6: tterm[i] = True
    wins = set(G.win_list[int(w)] for w in G.ew[tight]) | set(G.win_list[int(w)] for w in G.tw[tterm])
    arrays = dict(tight=tight, tterm=tterm, Fw=Fw, Bk=Bk, cw=cw, ku=ku, unit_e=unit_e, target=target)
    res = dict(arrays=arrays, windows=wins, jopt={w: jopt[w] for w in wins}, stats=dict(graph_windows=len(G.win_list), edges=int(tight.sum()), terminals=int(tterm.sum()),
                                                                      windows_tight=len(wins), min_combined=float(best), target=float(target)))
    if export:
        te = np.nonzero(tight)[0]
        tt = np.nonzero(tterm)[0]
        nodes_used = sorted(set(G.src[te].tolist()) | set(G.dst[te].tolist()) | set(int(G.tn[i]) for i in tt))
        nid = {u: i for i, u in enumerate(nodes_used)}
        edges = [(nid[int(G.src[e])], nid[int(G.dst[e])], G.win_list[int(G.ew[e])], float(cw[int(G.ew[e])]), int(unit_e[e])) for e in te]
        terms = [(nid[int(G.tn[i])], G.win_list[int(G.tw[i])], float(cw[int(G.tw[i])]), int(ku[int(G.tn[i])])) for i in tt]
        starts = [nid[int(s)] for s in G.starts if int(s) in nid]
        ndata = [(G.nodes[u][0], G.nodes[u][1]) for u in nodes_used]
        idx = np.array(nodes_used, dtype=int)
        pickle.dump(dict(nodes=ndata, edges=edges, terms=terms, starts=starts, F=Fw[:, idx] if len(idx) else Fw[:, :0], B=Bk[:, idx] if len(idx) else Bk[:, :0],
                         jopt=res["jopt"], Wt=W, target=target), open(export, "wb"))
    return res


# ---------------------------------------------------------------------------------------------------- strictness tests

def fr(x, maxden=1 << 20):
    return F(float(x)).limit_denominator(maxden)


def exactify(A, b, bounds, w, tol=1e-8, dens=(64, 1024, 1 << 16, 1 << 24)):
    """exact rational vertex near the float LP solution w: fix variables at bounds, solve the active rows exactly, return list of Fractions or None"""
    m, K = A.shape
    lo = np.array([bd[0] for bd in bounds], dtype=float); hi = np.array([bd[1] for bd in bounds], dtype=float)
    slack = b - A @ w
    act = np.nonzero(slack < tol * (1 + np.abs(b)))[0]
    at_lo = (w - lo) < 1e-9
    at_hi = (hi - w) < 1e-9
    free = [j for j in range(K) if not (at_lo[j] or at_hi[j])]
    xfix = {}
    for j in range(K):
        if at_lo[j]: xfix[j] = fr(lo[j], 1000)
        elif at_hi[j]: xfix[j] = fr(hi[j], 1000)
    fidx = {j: i for i, j in enumerate(free)}
    rows = []
    for i in act:
        idxs = np.nonzero(A[i])[0]
        coef = {}
        rhs = fr(b[i], 1 << 12)
        for j in idxs:
            a = fr(A[i, j], 1 << 12)
            if abs(float(a) - A[i, j]) > 1e-9: return None
            if j in xfix: rhs -= a * xfix[j]
            else: coef[fidx[j]] = a
        if not coef:
            if rhs != 0 and False: return None
            continue
        rows.append((coef, rhs))
    nf = len(free)
    for den in dens:
        if not rows:
            x = {}
        else:
            M = flint.fmpq_mat(len(rows), nf + 1)
            for r, (coef, rhs) in enumerate(rows):
                for c, a in coef.items(): M[r, c] = flint.fmpq(a.numerator, a.denominator)
                M[r, nf] = flint.fmpq(rhs.numerator, rhs.denominator)
            R, rank = M.rref()
            piv = []
            r = 0
            ok = True
            for r in range(rank):
                c = next(c for c in range(nf + 1) if R[r, c] != 0)
                if c == nf: ok = False; break
                piv.append(c)
            if not ok: return None
            nonpiv = [c for c in range(nf) if c not in set(piv)]
            xs = [None] * nf
            for c in nonpiv: xs[c] = fr(w[free[c]], den)
            for r, c in enumerate(piv):
                v = F(int(R[r, nf].p), int(R[r, nf].q))
                for c2 in nonpiv:
                    e = R[r, c2]
                    if e != 0: v -= F(int(e.p), int(e.q)) * xs[c2]
                xs[c] = v
            x = {free[c]: xs[c] for c in range(nf)}
        full = dict(xfix); full.update(x)
        # exact check of ALL rows and bounds on the support
        good = True
        for j, v in full.items():
            if v < 0 and lo[j] >= 0: good = False; break
            if v < fr(lo[j], 1000) or v > fr(hi[j], 1000): good = False; break
        if good:
            supp = {j: v for j, v in full.items() if v != 0}
            for i in range(m):
                idxs = np.nonzero(A[i])[0]
                s_ = sum((fr(A[i, j], 1 << 12) * supp[j] for j in idxs if j in supp), F(0))
                if s_ > fr(b[i], 1 << 12):
                    good = False; break
        if good:
            return {j: v for j, v in full.items() if v != 0}
    return None


def verify_exact(G0, G1, wint, D):
    v0, _, _ = T.solve_exactw(G0, wint, W17, scale=D)
    v1, _, _ = T.solve_exactw(G1, wint, W17, scale=D)
    ok0 = v0 is None or v0 >= 2 * D - 1e-9
    ok1 = v1 is None or v1 > 2 * D + 1e-9
    return ok0 and ok1, v0, v1


def strict_test(task):
    """task = dict(name, windows, allowed, deltas, tlimit).  returns dict(name, status, D, w, delta)"""
    t0 = time.time()
    name = task["name"]
    try:
        o = make_o()
        T.GROUP[0] = set(task["windows"])
        cat = CAT[0]
        G0 = T.build_graph(o, cat=cat, fmode="f0", allowed=task["allowed"])
        G1 = T.build_graph(o, cat=cat, fmode="f1", allowed=task["allowed"])
        Km = len(cat.keys); T.pad_K(G0, Km); T.pad_K(G1, Km)
        if G1.N == 0 or len(G1.tn) == 0:
            return dict(name=name, status="vacuous", D=None, w=None, delta=None, time=time.time() - t0)
        last = "tight"
        for delta in task["deltas"]:
            target2 = float(2 + 2 * F(delta))
            w, cuts = T.lp_loop_exactw(G0, W17, o.wmax, o.iters, verbose=False, time_limit=task["tlimit"], target=2.0, E=0.0, G2=G1, target2=target2)
            if w is None:
                return dict(name=name, status="tight" if delta == task["deltas"][0] else last, D=None, w=None, delta=str(delta), time=time.time() - t0)
            if isinstance(w, str):
                return dict(name=name, status="timeout", D=None, w=None, delta=str(delta), time=time.time() - t0)
            last = "float-only"
            xe = exactify(T.LP_SYS["A"], T.LP_SYS["b"], T.LP_SYS["bounds"], w)
            if xe is not None:
                import math
                D = 1
                for v in xe.values(): D = D * v.denominator // math.gcd(D, v.denominator)
                wint = np.zeros(len(w))
                for j, v in xe.items(): wint[j] = int(v * D)
                ok, v0, v1 = verify_exact(G0, G1, wint, D)
                if ok:
                    wd = {G0.cat.keys[i]: int(wint[i]) for i in range(len(wint)) if wint[i] != 0}
                    return dict(name=name, status="strict", D=D, w=wd, delta=str(delta), v0=v0, v1=v1, time=time.time() - t0)
                last = "float-only(exact vertex failed)"
            for D in DENS:
                wint = np.rint(w * D)
                bd = T.col_bounds(G0)
                if any(wint[i] > bd[i][1] * D + 1e-9 or wint[i] < bd[i][0] * D - 1e-9 for i in range(len(wint))): continue
                ok, v0, v1 = verify_exact(G0, G1, wint, D)
                if ok:
                    wd = {G0.cat.keys[i]: int(wint[i]) for i in range(len(wint)) if wint[i] != 0}
                    return dict(name=name, status="strict", D=D, w=wd, delta=str(delta), v0=v0, v1=v1, time=time.time() - t0)
        return dict(name=name, status="float-only", D=None, w=None, delta=str(task["deltas"][-1]), time=time.time() - t0)
    except Exception as e:
        return dict(name=name, status="error: " + repr(e) + traceback.format_exc()[-400:], D=None, w=None, delta=None, time=time.time() - t0)


CAT = [None]


def tight_groups(o, cat, res, allowed):
    """(cfg, role) groups of tight T windows (correct sig tightness)"""
    groups = collections.defaultdict(set); cfgs = collections.defaultdict(set)
    chr_of = lambda info: "U" if info is None else ("T" if info[0] == "T" else "S")
    for win in res["windows"]:
        prev, cur, nxt = win
        if cur.kind != "T": continue
        for sg in res["jopt"][win]:
            sig = sg[0]
            ring = [chr_of(nxt), "T" if sig[0] else "S", "T" if sig[2] else "S", chr_of(prev), "T" if sig[3] else "S", "T" if sig[1] else "S"]
            sec6 = (cur.bout[0], cur.h[0], cur.bin[0], cur.bin[1], cur.h[1], cur.bout[1])
            cr = T.cfg_role("".join(ring).replace("T", "N"), sec6, 0)
            if cr is None: continue
            (c, sc), role = cr
            groups[(c, sc, role)].add(win); cfgs[(c, sc)].add(role)
    return groups, cfgs


def initial_certs():
    certs = []
    for n, D in INITIAL:
        Wf = pickle.load(open(f"{ROOT}/work/eng/T25/w_{n}.pkl", "rb"))
        certs.append(dict(name=n, D=D, w={k: int(round(x * D)) for k, x in Wf.items() if round(x * D) != 0}))
    return certs


def point_types(res):
    """census of jointly tight point configurations (far-ends, sector bits) with the role classes that have a tight window"""
    cfg_roles = collections.defaultdict(set)
    chr_of = lambda info: "U" if info is None else ("T" if info[0] == "T" else "S")
    for win in res["windows"]:
        prev, cur, nxt = win
        if cur.kind != "T": continue
        for sg in res["jopt"][win]:
            sig = sg[0]
            ring = [chr_of(nxt), "T" if sig[0] else "S", "T" if sig[2] else "S", chr_of(prev), "T" if sig[3] else "S", "T" if sig[1] else "S"]
            sec6 = (cur.bout[0], cur.h[0], cur.bin[0], cur.bin[1], cur.h[1], cur.bout[1])
            cr = T.cfg_role("".join(ring).replace("T", "N"), sec6, 0)
            if cr is None: continue
            cfg_roles[cr[0]].add(cr[1])
    joint = [c for c, r in cfg_roles.items() if set(T.cfg_row(c).keys()) <= r]
    return cfg_roles, joint


def report(k, res, extra=""):
    st = res["stats"]
    cfg_roles, joint = point_types(res)
    nT = sum(1 for w in res["windows"] if w[1].kind == "T")
    lines = [f"round {k}: {extra}", f"  jointly tight structure: {st}", f"  T windows {nT}, S windows {len(res['windows']) - nT}",
             f"  point configs with a tight window: {len(cfg_roles)}, jointly tight (every role class has one): {len(joint)}"]
    for c in sorted(joint, key=str):
        lines.append(f"     {c[0]} {''.join(map(str, c[1]))} roles {sorted(cfg_roles[c])}")
    fl = flower_windows_present(res)
    lines.append(f"  flower-corner (NNNSSS 111011) tight windows: {fl[0]}, centre (NNNNNN 111111) windows: {fl[1]}")
    txt = "\n".join(lines)
    print(txt, flush=True)
    open(f"{DIR}/report_{k}.txt", "w").write(txt + "\n")


def flower_windows_present(res):
    cfg_count = collections.Counter()
    chr_of = lambda info: "U" if info is None else ("T" if info[0] == "T" else "S")
    for win in res["windows"]:
        prev, cur, nxt = win
        if cur.kind != "T": continue
        for sg in res["jopt"][win]:
            sig = sg[0]
            ring = [chr_of(nxt), "T" if sig[0] else "S", "T" if sig[2] else "S", chr_of(prev), "T" if sig[3] else "S", "T" if sig[1] else "S"]
            sec6 = (cur.bout[0], cur.h[0], cur.bin[0], cur.bin[1], cur.h[1], cur.bout[1])
            cr = T.cfg_role("".join(ring).replace("T", "N"), sec6, 0)
            if cr is None: continue
            cfg_count[(cr[0][0], "".join(map(str, cr[0][1])))] += 1
    return cfg_count[("NNNSSS", "111011")], cfg_count[("NNNNNN", "111111")]


def main():
    import multiprocessing as mp
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd"); ap.add_argument("k", nargs="?", type=int, default=0)
    ap.add_argument("--jobs", type=int, default=14)
    ap.add_argument("--kinds", default="groups,T,S")
    ap.add_argument("--limit", type=int, default=10 ** 9)
    ap.add_argument("--tlimit", type=float, default=900.0)
    ap.add_argument("--deltas", default="1/1000,1/32,1/128")
    a = ap.parse_args()
    o = make_o()
    if a.cmd == "init":
        Gfull = T.build_graph(o)
        cat = Gfull.cat
        certs = initial_certs()
        t0 = time.time()
        res = joint_structure(o, cat, None, certs, export=f"{DIR}/prep_0.pkl", G=Gfull)
        print("round 0 joint structure", res["stats"], time.time() - t0, flush=True)
        res.pop("arrays", None)
        pickle.dump(dict(certs=certs, allowed=res["windows"], res=res, removed=set()), open(f"{DIR}/state_0.pkl", "wb"))
        report(0, res, "initial 5 certificates")
        return
    if a.cmd == "round":
        st = pickle.load(open(f"{DIR}/state_{a.k - 1}.pkl", "rb"))
        certs, allowed, res, removed = st["certs"], st["allowed"], st["res"], st["removed"]
        CAT[0] = T.build_graph(o, allowed=allowed).cat
        groups, cfgs = tight_groups(o, CAT[0], res, allowed)
        tasks = []
        if "groups" in a.kinds:
            for (c, sc, role), ws in sorted(groups.items(), key=str):
                tasks.append(dict(name=f"G|{c}|{''.join(map(str, sc))}|r{role}", windows=ws, allowed=allowed))
        if "T" in a.kinds:
            for i, win in enumerate(sorted([w for w in allowed if w[1].kind == "T"], key=repr)):
                tasks.append(dict(name=f"T{i}", windows={win}, allowed=allowed))
        if "S" in a.kinds:
            for i, win in enumerate(sorted([w for w in allowed if w[1].kind == "S"], key=repr)):
                tasks.append(dict(name=f"S{i}", windows={win}, allowed=allowed))
        tasks = tasks[:a.limit]
        for t in tasks:
            t["deltas"] = [F(x) for x in a.deltas.split(",")]; t["tlimit"] = a.tlimit
        print(f"round {a.k}: {len(tasks)} tasks, allowed windows {len(allowed)}", flush=True)
        results = []
        ctx = mp.get_context("fork")
        with ctx.Pool(a.jobs, maxtasksperchild=1) as pool:
            for r in pool.imap_unordered(strict_test, tasks):
                results.append(r)
                print(f"  {r['name'][:60]:60s} {r['status'][:40]:40s} D={r['D']} delta={r['delta']} {r['time']:.0f}s", flush=True)
                open(f"{DIR}/round_{a.k}_results.jsonl", "a").write(json.dumps({k: v for k, v in r.items() if k != "w"}) + "\n")
        strict = [r for r in results if r["status"] in ("strict", "vacuous")]
        newcerts = []
        newrem = set()
        tasks_by_name = {t["name"]: t for t in tasks}
        for r in strict:
            newrem |= set(tasks_by_name[r["name"]]["windows"])
            if r["status"] == "strict":
                newcerts.append(dict(name=f"r{a.k}_{r['name']}", D=r["D"], w=r["w"]))
        removed2 = removed | newrem
        certs2 = certs + newcerts
        # dedupe certificates by content, keep at most 60
        seen = set(); cc = []
        for c in certs2:
            key = (c["D"], tuple(sorted(c["w"].items())))
            if key in seen: continue
            seen.add(key); cc.append(c)
        certs2 = cc[:5] + cc[5:][-55:]
        allowed2 = set(allowed) - removed2
        res2 = joint_structure(o, CAT[0], allowed2, certs2, export=f"{DIR}/prep_{a.k}.pkl")
        res2.pop("arrays", None)
        pickle.dump(dict(certs=certs2, allowed=res2["windows"], res=res2, removed=removed2), open(f"{DIR}/state_{a.k}.pkl", "wb"))
        report(a.k, res2, f"removed {len(newrem)} windows this round ({len(strict)} strict tests), total removed {len(removed2)}; float-only {sum(1 for r in results if r['status'] == 'float-only')}, tight {sum(1 for r in results if r['status'] == 'tight')}, timeouts {sum(1 for r in results if r['status'] == 'timeout')}")
        return


if __name__ == "__main__":
    main()

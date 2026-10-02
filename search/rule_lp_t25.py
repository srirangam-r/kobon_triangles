"""T25: closed loop LP <-> pattern SAT, extension of search/rule_lp.py (which stays untouched).

Adds
  --t1pp     fixed rule T1'': for every block that T1 leaves unserved, each TRIPLE flanker F whose gap-end ray is N pays 3/2
             from the cap to the axis (equivalently: the cap pays 3/2 per N gap-end ray at a triple flanker for every block,
             served or not; the served blocks are unchanged).  It is part of the base window values (v2), i.e. of
             LA.exact_vec, which is patched at import time when `enable_t1pp()` is called.
  --exactw W paths of weight exactly W = #S + 2 #T (no cycles): W = 17 is the set of lines of an 18-line arrangement with
             points of multiplicity <= 3.  Short deficit lines (n < 18) drop out.
  --cuts-in / --dump  cut files in the T21 format (json), readable by work/eng/T23/cutload.py.

    uv run --no-project --with numpy --with scipy --with networkx python search/rule_lp_t25.py lp --enriched --f4p --k1 --k2 \
        --k2g --k3 --t1pp --exactw 17 --dump work/eng/T25/cuts_A.json --export ... --save ...
"""
import collections
import json
import pickle
import sys
import time
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
import inspect  # noqa: F401,E402
sys.path.append(str(ROOT / "work/t3"))
import numpy as np  # noqa: E402
import line_automaton as LA  # noqa: E402
import rule_lp as RL  # noqa: E402

_EXACT_VEC_ORIG = LA.exact_vec
_T1PP_ON = [False]


# ---------------------------------------------------------------------------------------------------- T1''
def t1pp_delta(prev, cur, nxt, hid=None):
    """change of v2 (= 2 * value) of the line of window (prev, cur, nxt) caused by T1'' with respect to T1 + F.
    cap (simple vertex):  T1 already counts 3 per N gap-end ray when BOTH neighbours (= flankers) are triple; T1'' counts it also
                          when only one of them is triple (the block is then unserved, and the axis gets it).
    axis (triple vertex): an unserved block (T1 gives nothing) receives 3 per triple flanker with N gap-end ray."""
    if cur.kind == "S":
        if prev is None or nxt is None or (prev[0] == "T" and nxt[0] == "T"):
            return 0
        d = 0
        for k in (0, 1):
            if cur.bin[k] and cur.bout[k]:
                if prev[0] == "T" and cur.bin[1 - k] == 0:
                    d -= 3
                if nxt[0] == "T" and cur.bout[1 - k] == 0:
                    d -= 3
        return d
    sig, g = hid
    d = 0
    for bits, other, fl in ((cur.bout, nxt, (0, 1)), (cur.bin, prev, (2, 3))):
        if LA.ray_status_L(bits, other) != "B":
            continue
        nb = other[2]                       # bits of the segment beyond X: nb[s] == 0 <=> the gap-end ray at the side-s flanker is N
        f1, f2 = sig[fl[0]], sig[fl[1]]
        if f1 and f2 and (nb[0] == 0 or nb[1] == 0):
            continue                        # served by T1
        d += 3 * (int(bool(f1) and nb[0] == 0) + int(bool(f2) and nb[1] == 0))
    return d


def exact_vec_t1pp(prev, cur, nxt, hid=None):
    p, v2, nRN, nRR, nT = _EXACT_VEC_ORIG(prev, cur, nxt, hid)
    if _T1PP_ON[0]:
        v2 += t1pp_delta(prev, cur, nxt, hid)
    return p, v2, nRN, nRR, nT


def enable_t1pp(on=True):
    """patch LA.exact_vec (used by rule_lp.SigCatalogue.window_options, LA.options, LA.check_line) to include T1''"""
    _T1PP_ON[0] = bool(on)
    LA.exact_vec = exact_vec_t1pp
    LA._opt_cache.clear()


# ---------------------------------------------------------------------------------------------------- exact-weight DP
def solve_exactw(G, w, W, scale=1, tol=1e-9, noise=None):
    """min over admissible paths with #simple + 2 #triple = W exactly of  scale*v2 + 2 w.counts   (layered DP, no cycles).
    Returns (value, 'path', (v2, counts, windows)) or (None, 'none', None)."""
    wmin, val = G.window_min(w, scale)
    wsel = wmin if noise is None else wmin + noise            # noise: per-window perturbation (diverse near-minimal paths)
    ewt = wsel[G.ew]
    N = G.N
    INF = 1e18
    if not hasattr(G, "_kunits"):
        G._kunits = np.array([2 if G.nodes[i][1].kind == "T" else 1 for i in range(N)])
    ku = G._kunits
    unit_e = ku[G.src]
    F_ = np.full((W + 1, N), INF)
    Pe = np.full((W + 1, N), -1, dtype=np.int64)
    F_[0][G.starts] = 0.0
    m_by = {c0: np.nonzero(unit_e == c0)[0] for c0 in (1, 2)}
    for c in range(W + 1):
        fc = F_[c]
        for c0 in (1, 2):
            c2 = c + c0
            if c2 > W:
                continue
            m = m_by[c0]
            fs = fc[G.src[m]]
            ok = fs < INF
            if not ok.any():
                continue
            m = m[ok]
            cand = fs[ok] + ewt[m]
            best = F_[c2].copy()
            np.minimum.at(best, G.dst[m], cand)
            imp = best < F_[c2] - tol
            if imp.any():
                sel = m[cand <= best[G.dst[m]] + 1e-12]
                sel = sel[imp[G.dst[sel]]]
                Pe[c2][G.dst[sel]] = sel
                F_[c2] = np.where(imp, best, F_[c2])
    bestv, bnode, bc, bw = INF, None, None, None
    for u_, wi in zip(G.tn, G.tw):
        uu = int(ku[u_])
        c = W - uu
        if c < 0:
            continue
        v = F_[c][u_]
        if v < INF and v + wsel[wi] < bestv:
            bestv, bnode, bc, bw = v + wsel[wi], int(u_), c, int(wi)
    if bnode is None:
        return None, "none", None
    edges = []
    x, c = bnode, bc
    while c > 0:
        e = int(Pe[c][x])
        edges.append(e)
        c -= int(unit_e[e])
        x = int(G.src[e])
    edges = edges[::-1]
    cnt = G._counts(edges, wmin, val, extra_window=bw)
    if noise is not None:
        bestv = float(sum(wmin[i] for i in cnt[2]))          # true relaxed value of the path (without the noise)
    return float(bestv), "path", cnt


def export_rules_t25(G, wint, D, path):
    """rule table incl. the special columns a and alpha' (weights are exact fractions wint / D)"""
    rows, special = [], {}
    families = []
    for i in np.nonzero(wint)[0]:
        key = G.cat.keys[i]
        if len(key) == 1:
            special[key[0]] = str(F(int(wint[i]), D))
            continue
        if key[0] in ("SV", "TRI", "PT", "U"):
            families.append(dict(family=key[0], key=repr(key[1:]), weight=str(F(int(wint[i]), D))))
            continue
        pay, rec, cell = key
        ring5, u, pL, pR, tL, tR, oth = cell
        rows.append(dict(payer=pay, receiver=rec, ring5="".join(ring5), u=u, pL=pL, pR=pR, tL=tL, tR=tR, oth=list(oth),
                         weight=str(F(int(wint[i]), D))))
    json.dump(dict(description="rule (payer role, receiver role, block signature cell) with weight; a = portion split, alpha = waste "
                               "identity column; roles A axis, C cap, L/R flank lines, M = both flank lines when symmetric",
                   denominator=D, special=special, rules=rows, families=families), open(path, "w"), indent=1)
    return rows


GROUP = [None]      # set of windows (prev, cur, nxt) for the strictness-through-a-window test


def load_warm_cuts(G, path):
    import ast
    d = json.load(open(path))
    out = []
    for c in d:
        try:
            cnt = {G.cat.idx[ast.literal_eval(k)]: x for k, x in c["counts"].items()}
        except KeyError:
            continue
        out.append((c["v2"], cnt, [], "path", None, c.get("target") or RL.TARGET))
    return out


def pad_K(g, K):
    """enlarge the column space of a graph built earlier (the shared catalogue gained columns while a second graph was built)"""
    if g.K >= K:
        return
    from scipy.sparse import csr_matrix
    coo = g.TO.tocoo()
    g.TO = csr_matrix((coo.data, (coo.row, coo.col)), shape=(g.TO.shape[0], K))
    g.K = K


def col_bounds(G, wmax=100.0):
    """LP bounds per column: a in [0, 1/3] (or fixed), alpha' in [0, 1], rule weights in [0, wmax]"""
    bd = []
    af = getattr(G.cat, "afix", None)
    for k in G.cat.keys:
        if k == ("a",):
            bd.append((0.0, 1.0 / 3.0) if af is None else (af, af))
        elif k == ("alpha",):
            bd.append((0.0, 1.0))
        else:
            bd.append((0.0, wmax))
    return bd


def ring_rows_matrix(G, K):
    """rows  -sum_role mult * U(cfg, role) <= -E  (E is added by the caller as the rhs): returns list of {col: -mult}"""
    rows = []
    for cfg, m in sorted(G.cat.tau_rows.items(), key=repr) if hasattr(G.cat, "tau_rows") else []:
        rows.append({G.cat.idx[("U", cfg, role)]: -float(mult) for role, mult in m.items()})
    return rows


def ring_min_exact(G, wint, D):
    m = None
    for cfg, mm in G.cat.tau_rows.items() if hasattr(G.cat, "tau_rows") else []:
        sm = sum(F(int(wint[G.cat.idx[("U", cfg, role)]]), D) * mult for role, mult in mm.items())
        m = sm if m is None or sm < m else m
    return m


def rationalize_exactw(G, w, W, target=RL.TARGET, E=0, G2=None, target2=None, dens=(1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 36, 48, 60, 72, 96, 120, 144, 180, 240, 288, 360, 480, 720, 960, 1440, 2880)):
    bd = col_bounds(G)
    for D in dens:
        wint = np.rint(w * D)
        if any(wint[i] > bd[i][1] * D + 1e-9 or wint[i] < bd[i][0] * D - 1e-9 for i in range(len(wint))):
            continue
        v, kind, cnt = solve_exactw(G, wint, W, scale=D)
        if v is None or v < target * D - 1e-9:
            continue
        if G2 is not None:
            v2_, _, _ = solve_exactw(G2, wint, W, scale=D)
            if v2_ is not None and v2_ < target2 * D - 1e-9:
                continue
        if E:
            rm = ring_min_exact(G, wint, D)
            if rm is None or rm < E:
                continue
        return D, wint, v
    return None, None, None


LP_SYS = {}


def lp_loop_exactw(G, W, wmax=100.0, max_it=2000, w0=None, extra_cuts=None, verbose=True, time_limit=None, tag="", target=RL.TARGET, E=0.0,
                   G2=None, target2=None, obj=None):
    """LP cutting-plane loop.  G2/target2: a second graph over the SAME rule columns (e.g. clean paths only) with its own target."""
    from scipy.optimize import linprog
    K = G.K
    cuts = list(extra_cuts or [])
    w = np.zeros(K) if w0 is None else np.array(w0, dtype=float)
    bounds = col_bounds(G, wmax)
    rrows = ring_rows_matrix(G, K)
    xrows = []
    for (coefs, rhs) in getattr(G.cat, "extra_rows", []):
        xr = {}
        for k, x in coefs.items():
            if k in G.cat.idx:
                xr[G.cat.idx[k]] = x
        xrows.append((xr, rhs))
    t_start = time.time()
    for it in range(max_it):
        t0 = time.time()
        v, kind, cnt = solve_exactw(G, w, W)
        v2_, kind2, cnt2 = (solve_exactw(G2, w, W) if G2 is not None else (None, None, None))
        if v is None:
            print("no path of that weight")
            return w, cuts
        viol1 = v < target - 1e-9
        viol2 = G2 is not None and v2_ is not None and v2_ < target2 - 1e-9
        if verbose and (it % 5 == 0 or not (viol1 or viol2)):
            print(f"{tag}it {it:3d} DP min (2*final+2) = {v:9.4f}" + (f" clean {v2_:9.4f}" if v2_ is not None else "") +
                  f", len {len(cnt[2])}, cuts {len(cuts)}, |w|_1 = {w.sum():.3f}, {time.time() - t0:.1f}s", flush=True)
        if not (viol1 or viol2) and (it > 0 or not rrows):
            return w, cuts
        if viol1:
            cuts.append(cnt + ("path", window_sigsets(G, cnt[2], w), target))
        if viol2:
            cnt2 = (cnt2[0], cnt2[1], [G2.win_list[wi] for wi in cnt2[2]])
            cuts.append(cnt2 + ("path", None, target2))
        A = np.zeros((len(cuts) + len(rrows) + len(xrows), K))
        b = np.zeros(len(cuts) + len(rrows) + len(xrows))
        for i, cut in enumerate(cuts):
            v2, d = cut[0], cut[1]
            for c, x in d.items():
                A[i, c] = -2.0 * x
            b[i] = v2 - (cut[5] if len(cut) > 5 else target)
        for j, r in enumerate(rrows):
            for c, x in r.items():
                A[len(cuts) + j, c] = x
            b[len(cuts) + j] = -E
        for j, (xr, rhs) in enumerate(xrows):
            for c, x in xr.items():
                A[len(cuts) + len(rrows) + j, c] = x
            b[len(cuts) + len(rrows) + j] = rhs
        res = linprog(np.ones(K) if obj is None else obj, A_ub=A, b_ub=b, bounds=bounds, method="highs")
        LP_SYS.update(A=A, b=b, bounds=bounds)
        if res.status != 0:
            print(f"{tag}LP infeasible after {len(cuts)} cuts")
            return None, cuts
        w = res.x
        if time_limit and time.time() - t_start > time_limit:
            print(f"{tag}time limit")
            return "timeout", cuts
    return w, cuts


def window_sigsets(G, wins, w):
    """per window of a path: None for S windows, else the list of hidden sig tuples achieving the window minimum at weights w"""
    out = []
    for wi in wins:
        prev, cur, nxt = G.win_list[wi]
        if cur.kind != "T":
            out.append(None)
            continue
        if nxt is not None and nxt[0] == "MENTRY":
            opts = []
            for hW in LA.BITS:
                opts += G.cat.sig_options(prev, cur, ("T", hW, nxt[1], nxt[2], "M"))
        else:
            opts = G.cat.sig_options(prev, cur, nxt)
        vals = [option_value(o_, w) for (_, _, o_) in opts]
        m = min(vals) if vals else 0
        out.append([sg for (sg, _, _), vv in zip(opts, vals) if vv <= m + 1e-7])
    return out


def dump_cuts(G, cuts, path):
    dump = []
    for c in cuts:
        dump.append(dict(kind=c[3] if len(c) > 3 else "path", v2=c[0],
                         counts={repr(G.cat.keys[k]): x for k, x in c[1].items()},
                         windows=[[repr(t) for t in (G.win_list[wi] if isinstance(wi, (int, np.integer)) else wi)] for wi in c[2]],
                         sigsets=(c[4] if len(c) > 4 else None), target=(c[5] if len(c) > 5 else None)))
    if path:
        json.dump(dump, open(path, "w"), indent=1)
    return dump


# ---------------------------------------------------------------------------------------------------- minimal infeasible core
def cut_matrix(dump):
    keys = {}
    for c in dump:
        for k in c["counts"]:
            keys.setdefault(k, len(keys))
    return keys


def key_bounds(keys, wmax):
    bd = [None] * len(keys)
    for k, i in keys.items():
        kk = eval(k) if isinstance(k, str) else k
        bd[i] = (0.0, 1.0 / 3.0) if kk == ("a",) else (0.0, 1.0) if kk == ("alpha",) else (0.0, wmax)
    return bd


def lp_feasible(dump, idx, keys, wmax=100.0, target=RL.TARGET, xrows=()):
    from scipy.optimize import linprog
    K = len(keys)
    A = np.zeros((len(idx) + len(xrows), K))
    b = np.zeros(len(idx) + len(xrows))
    for j, (coefs, rhs) in enumerate(xrows):
        for k, x in coefs.items():
            if k in keys:
                A[len(idx) + j, keys[k]] = x
        b[len(idx) + j] = rhs
    for r, i in enumerate(idx):
        c = dump[i]
        for k, x in c["counts"].items():
            A[r, keys[k]] = -2.0 * x
        b[r] = c["v2"] - ((c.get("target") or target) if c["kind"] == "path" else 0.0)
    res = linprog(np.zeros(K), A_ub=A, b_ub=b, bounds=key_bounds(keys, wmax), method="highs")
    return res.status == 0


def min_core(dump, wmax=100.0, target=RL.TARGET, xrows=()):
    """deletion filter: minimal infeasible sub-system of the cuts"""
    keys = cut_matrix(dump)
    for coefs, rhs in xrows:
        for k in coefs:
            keys.setdefault(k, len(keys))
    idx = list(range(len(dump)))
    assert not lp_feasible(dump, idx, keys, wmax, target, xrows)
    i = 0
    while i < len(idx):
        trial = idx[:i] + idx[i + 1:]
        if not lp_feasible(dump, trial, keys, wmax, target, xrows):
            idx = trial
        else:
            i += 1
    return idx


def farkas_multipliers(dump, idx, wmax=100.0):
    """dual multipliers y >= 0 of the core (sum_i y_i * row_i <= ... contradiction), to see which cuts matter most"""
    from scipy.optimize import linprog
    keys = cut_matrix([dump[i] for i in idx])
    K = len(keys)
    A = np.zeros((len(idx), K))
    b = np.zeros(len(idx))
    for r, i in enumerate(idx):
        c = dump[i]
        for k, x in c["counts"].items():
            A[r, keys[k]] = -2.0 * x
        b[r] = c["v2"] - (2.0 if c["kind"] == "path" else 0.0)
    # Farkas: y >= 0, y^T A >= 0 componentwise? with bounds 0 <= w <= wmax: exists y>=0,z>=0: y^T A + z >= 0... just solve
    # min b^T y + wmax*sum(z)  s.t. y^T A >= -z ... use the standard: feasible iff no y>=0 with y^T A >= 0 (columns) and y^T b < 0 (for w >= 0)
    m = len(idx)
    res = linprog(b, A_ub=-A.T, b_ub=np.zeros(K), A_eq=np.ones((1, m)), b_eq=[1.0], bounds=[(0, None)] * m, method="highs")
    return res.x if res.status == 0 else None


# ---------------------------------------------------------------------------------------------------- driver
C2_RINGS = "NNNNNN,BNNNNN,BNNBNN,BNNRNN,NNNNNR,NNNNRR,NNRNNR,NNNRRR,NNRRRR,RRRRRR,BNNNNR,BNNNRR,BRNNNR,BNNRRR,BRNNRR"


def add_args(ap):
    ap.add_argument("cmd")
    ap.add_argument("--wmax", type=float, default=100.0)
    ap.add_argument("--iters", type=int, default=3000)
    ap.add_argument("--class", dest="cls", default="full", help="full | C2 (ring types of the C2 certificate) | comma list of ring types")
    ap.add_argument("--k2g", action="store_true", default=True)
    ap.add_argument("--nok3", action="store_true")
    ap.add_argument("--nok1", action="store_true")
    ap.add_argument("--nok2", action="store_true")
    ap.add_argument("--nok2g", action="store_true")
    ap.add_argument("--nof4p", action="store_true")
    ap.add_argument("--t1pp", action="store_true", default=True)
    ap.add_argument("--f5", action="store_true", default=True, help="F5* (on by default)")
    ap.add_argument("--nof5", action="store_true")
    ap.add_argument("--split", action="store_true", help="portion split column a in [0,1/3]")
    ap.add_argument("--alpha", action="store_true", help="alpha' column (waste identity)")
    ap.add_argument("--celldom", action="store_true", help="T23 axis-cell filter")
    ap.add_argument("--pat", default=None, help="json list of proved forbidden positive patterns (slots/seg/apex/sig dicts); all 4 symmetric variants are used")
    ap.add_argument("--facts", action="store_true", help="plug in all proven patterns of search/automaton_facts.py (P000-P009)")
    ap.add_argument("--sv", action="store_true", help="SV cells: transfers between the two lines of a simple vertex keyed by the 4 face bits")
    ap.add_argument("--pt", action="store_true", help="PT cells: transfers among the 3 lines of a triple point keyed by its 6 sector bits")
    ap.add_argument("--tri", action="store_true", help="TRI cells: transfers among the 3 side lines of a triangle keyed by the vertex multiplicities")
    ap.add_argument("--wr", action="store_true", help="waste recovery column: lost touch share at triple endpoints of own unused segments")
    ap.add_argument("--proj", default="", help="comma list of cell features to drop from the rule keys: u,p,pL,pR,t,oth")
    ap.add_argument("--eps", default="0", help="uniform strict target: every line final >= 3*eps (fraction); with --tau: credit sum E = 3*eps")
    ap.add_argument("--tau", action="store_true", help="targeted strictness with tau-credits on full point configurations (final_L >= sum of credits)")
    ap.add_argument("--afix", default=None, help="fix the portion split a (fraction), e.g. 0 or 1/6")
    ap.add_argument("--onlyclean", action="store_true", help="keep only CLEAN paths (delete every path with a T frame or a capping simple vertex)")
    ap.add_argument("--cleandelta", default=None, help="require final >= this fraction on CLEAN paths (separate DP over clean paths only, same columns)")
    ap.add_argument("--group", default=None, help="pickle {name: set of windows}; with --gname: paths through a window of that set need final >= delta")
    ap.add_argument("--gname", default=None)
    ap.add_argument("--delta", default="1/1000")
    ap.add_argument("--warm", default=None, help="json cut dump used as initial cuts (valid for targets >= those of the dump)")
    ap.add_argument("--tmode", default=None, help="lt2 | ge2: keep only paths with < 2 / >= 2 T frames")
    ap.add_argument("--tcredit", default=None, help="final >= 3*eps on paths with >= 2 T frames (separate DP over those paths, same columns), eps here")
    ap.add_argument("--noclean", action="store_true", help="delete clean paths (no T frame, no capped block): arrangements without a clean line")
    ap.add_argument("--objseed", type=int, default=None, help="random positive LP objective (different vertex of the feasible region)")
    ap.add_argument("--exactw", type=int, default=17)
    ap.add_argument("--margin", type=float, default=0.0, help="solve the LP against target + margin so that the rounding to a common denominator keeps the certificate")
    ap.add_argument("--dump", default=None)
    ap.add_argument("--export", default=None)
    ap.add_argument("--save", default=None)
    ap.add_argument("--core", action="store_true", help="on infeasibility compute the minimal core and print it")
    ap.add_argument("--time-limit", type=float, default=3000.0)
    return ap


def target_of(o):
    return 2.0 if o.tau else float(2 + 6 * F(o.eps))


def build_graph(o, hidden_filters=(), pset=None, cat=None, onlyclean=None, tmode=None, fmode=None, allowed=None):
    if o.t1pp:
        enable_t1pp(True)
    rings = None
    if o.cls == "C2":
        rings = C2_RINGS.split(",")
    elif o.cls != "full":
        rings = o.cls.split(",")
    cat = cat if cat is not None else FCatalogue(enriched=True, rings=rings, k1=not o.nok1, k2=not o.nok2, k2g=(o.k2g and not o.nok2g), hidden_filters=hidden_filters,
                     celldom=o.celldom, split_a=o.split, alpha=o.alpha, W=o.exactw, tau=o.tau,
                     afix=None if o.afix is None else float(F(o.afix)), proj=[x for x in o.proj.split(",") if x], wr=o.wr, sv=o.sv, tri=o.tri, pt=o.pt)
    if o.facts:
        pset = facts_pattern_set(pset)
    if o.pat:
        pset = pattern_set_from_json(o.pat, pset)
    install_combined_step(not o.nok3, pset, f5=(o.f5 and not o.nof5), noclean=o.noclean, onlyclean=(o.onlyclean if onlyclean is None else onlyclean), tmode=(o.tmode if tmode is None else tmode), group=GROUP[0], fmode=fmode)
    G = RL.WGraph(cat, edge_allow=(RL.f4p_edge_allow if not o.nof4p else (lambda c, n: True)), allowed=allowed, k3=True)
    print("catalogue stats:", dict(cat.stats), flush=True)
    return G


def main():
    import argparse
    ap = add_args(argparse.ArgumentParser())
    o = ap.parse_args()
    if o.group:
        GROUP[0] = pickle.load(open(o.group, "rb"))[o.gname]
        print("group", o.gname, "windows:", len(GROUP[0]), flush=True)
    G = build_graph(o, tmode=("lt2" if o.tcredit is not None else None), fmode=("f0" if o.group else None))
    target = target_of(o)
    if o.cmd == "base":
        v, kind, cnt = solve_exactw(G, np.zeros(G.K), o.exactw)
        print("w=0:", v, kind)
        print(RL.describe(G, cnt))
        print(RL.show_path(G, cnt))
    elif o.cmd == "lp":
        E = float(3 * F(o.eps)) if o.tau else 0.0
        G2 = target2 = None
        if o.cleandelta is not None:
            G2 = build_graph(o, cat=G.cat, onlyclean=True)
            Km = len(G.cat.keys)
            pad_K(G, Km)
            pad_K(G2, Km)
            target2 = float(2 + 2 * F(o.cleandelta))
        if o.group:
            G2 = build_graph(o, cat=G.cat, fmode="f1")
            Km = len(G.cat.keys)
            pad_K(G, Km)
            pad_K(G2, Km)
            target2 = float(2 + 2 * F(o.delta))
        if o.tcredit is not None:
            G2 = build_graph(o, cat=G.cat, tmode="ge2")
            Km = len(G.cat.keys)
            pad_K(G, Km)
            pad_K(G2, Km)
            target2 = float(2 + 6 * F(o.tcredit))
        w, cuts = lp_loop_exactw(G, o.exactw, o.wmax, o.iters, time_limit=o.time_limit, target=target + o.margin, E=E, G2=G2, target2=target2, extra_cuts=(load_warm_cuts(G, o.warm) if o.warm else None),
                                obj=(None if o.objseed is None else np.random.RandomState(o.objseed).uniform(0.3, 1.7, G.K)))
        if w is None:
            dump = dump_cuts(G, cuts, o.dump)
            if o.core:
                xr = [({repr(k): x for k, x in coefs.items()}, rhs) for coefs, rhs in getattr(G.cat, "extra_rows", [])]
                if o.tau:
                    for cfg, mm in G.cat.tau_rows.items():
                        xr.append(({repr(("U", cfg, role)): -float(mult) for role, mult in mm.items()}, -E))
                idx = min_core(dump, o.wmax, target, xr)      # (cuts + extra rows; tau ring rows not included in this deletion filter)
                print("core size", len(idx), "of", len(dump), "cuts:", idx)
                for i in idx:
                    c = dump[i]
                    print(f"--- cut {i} (path) v2 = {c['v2']}  (2*value at w=0 = {c['v2'] - 2})")
                    for wv in c["windows"]:
                        print("    ", wv[1])
        elif isinstance(w, str):
            print("timeout")
        else:
            if o.dump:
                dump_cuts(G, cuts, o.dump)
            D, wint, v = rationalize_exactw(G, w, o.exactw, target, E=(3 * F(o.eps) if o.tau else 0), G2=G2, target2=target2)
            print("exact certificate:", "denominator", D, "DP min (D*(2*final+2)) =", v, "target", None if D is None else target * D)
            if D is not None:
                w = wint / D
            for i in np.argsort(-w):
                if w[i] > 1e-9:
                    print(F(int(round(w[i] * (D or 1))), D or 1), G.cat.keys[i])
            if D is not None:
                mb = RL.min_by_units(G, wint, D, o.exactw)
                print("verify (bounded): min D*(2*final+2) per n-1:", {u: mb[u] for u in sorted(mb)}, "target", target * D)
                if o.export:
                    export_rules_t25(G, wint, D, o.export)
            if o.save:
                pickle.dump({G.cat.keys[i]: float(w[i]) for i in range(len(w)) if w[i] > 1e-9}, open(o.save, "wb"))


# ---------------------------------------------------------------------------------------------------- real lines (necessary LP)
def real_line_vectors(a, cat, t1pp=True, add_cols=False, extras=False, credit=False, info=None, proj_fn=None, ctx=None):
    """For a real arrangement a (search/arr.Arr): for every line L the exact value v_L (T1 + F + T1'' when t1pp) and its exact rule
    net vector  {column: net count}  in the SigCatalogue column numbering.  final_L(w) = v_L + sum_col w[col] * net[col].
    Returns {L: (v_L Fraction, {col: net})} and the set of keys unknown to the catalogue."""
    import bbl_rules2 as R2
    import rule_ref as RR
    c = ctx if ctx is not None else R2.Ctx(a)
    if info is not None:
        info["ctx"] = c
    v = dict(c.v0)
    if t1pp:
        from arr import rays, far_end
        trip = c.ch.trip
        for b in c.blk:
            if c.served[b]:
                continue
            (P, i, l, dd, X, C) = b
            rs = rays(a, P)
            for f in ((i - 1) % 6, (i + 1) % 6):
                Q = far_end(a, P, rs[f])
                if Q in trip:
                    dq = 1 if a.pos[C][X] > a.pos[C][Q] else -1
                    k = rays(a, Q).index((C, dq))
                    if c.ch.st[Q][k] == "N":
                        v[C] -= F(3, 2)
                        v[l] += F(3, 2)
    net = collections.defaultdict(collections.Counter)
    unknown = set()
    for b, (sg, lines) in RR.block_sigs(c).items():
        if proj_fn is not None:
            sg = proj_fn(sg)
        sm = RR.mirror_sig(sg)
        lines = dict(lines)
        symm = sm == sg
        if sm < sg:
            sg = sm
            lines["L"], lines["R"] = lines["R"], lines["L"]
        lab = (lambda x: "M" if (symm and x in "LR") else x)
        for p in "ACLR":
            for q in "ACLR":
                if p == q:
                    continue
                key = (lab(p), lab(q), sg)
                col = key if cat is None else cat.idx.get(key)
                if col is None:
                    unknown.add(key)
                    continue
                net[lines[p]][col] -= 1
                net[lines[q]][col] += 1
    if credit:
        from arr import rays as _rays
        for P in c.a.triples if hasattr(c.a, "triples") else [e for e in range(len(a.events)) if len(a.events[e]) == 3]:
            rs = _rays(a, P)
            ring = "".join(c.ch.st[P])
            sec = tuple(int(bool(LA._sector(a, P, rs, m))) for m in range(6))
            for j0 in range(3):
                L = rs[j0][0]
                cr = cfg_role(ring, sec, j0)
                if cr is not None:
                    net[L][("U", cr[0], cr[1])] -= 1
    out = {}
    for L in range(a.n):
        nt = {k: x for k, x in net[L].items() if x}
        vL = v[L]
        if extras:
            # exact quantities of the line: own unused segments, touches, triangle bits on L's segments (same definitions as exact_vec)
            frames, _h = LA.extract(c.ch, L)
            frames = LA.normalise(frames)
            m = len(frames)
            own = sum(1 for i in range(m - 1) if frames[i].bout == LA.NONE)
            touch = sum(1 for f in frames if f.kind == "S" for k in (0, 1) if not f.ub[k] and f.bin[k] + f.bout[k] == 0)
            bits = sum(frames[i].bout[0] + frames[i].bout[1] for i in range(m - 1))
            s_ = (a.n - 2) - bits
            ka, kal = (("a",), ("alpha",))
            nt[("wr",)] = sum(int(frames[i].kind == "T") + int(frames[i + 1].kind == "T") for i in range(m - 1) if frames[i].bout == LA.NONE)
            ef, _h2 = RL.eframes_of_line(c.ch, L)
            for i, f in enumerate(ef):
                if f.kind == "S":
                    for key_, x_ in sv_events(f):
                        nt[key_] = nt.get(key_, 0) + x_
                if f.kind == "T":
                    for key_, x_ in pt_events(f):
                        nt[key_] = nt.get(key_, 0) + x_
                if i < m - 1:
                    for key_, x_ in tri_events(f, ef[i + 1].info_next()):
                        nt[key_] = nt.get(key_, 0) + x_
            nt[ka] = F(3 * own) - F(3 * touch, 2)
            nt[kal] = 3 * s_ - 1 - vL                      # alpha' * (3 s - 1 - v_base), v_base = value at a = 1/3
            vL = vL - own + F(touch, 2)                    # value at a = 0 (a's column adds a * (3 own - 1.5 touch))
            nt = {k: x for k, x in nt.items() if x}
        out[L] = (vL, nt)
    return out, unknown


# ---------------------------------------------------------------------------------------------------- filters: hidden-domain + frame patterns
# ---------------------------------------------------------------------------------------------------- SV and TRI cells
_SVC = {}


def sv_cell_role(f0, f1, f2, f3):
    """Simple vertex X = L cap W.  The four faces around X in cyclic order f0 (between L east and W's next ray), f1, f2, f3 as seen from L:
    (bout[0], bin[0], bin[1], bout[1]).  Returns (canonical face tuple, role) with role 0/1 = which of the two lines of the canonical cell the
    line L is (None if an automorphism of the cell swaps the two lines: the transfer cancels)."""
    key = (f0, f1, f2, f3)
    r = _SVC.get(key)
    if r is not None:
        return r
    # cyclic structure r0 f0 r1 f1 r2 f2 r3 f3, lines: r0,r2 -> 0 (L), r1,r3 -> 1 (W)
    items = [(0, "r"), (f0, "f"), (1, "r"), (f1, "f"), (0, "r"), (f2, "f"), (1, "r"), (f3, "f")]
    imgs = []
    for refl in (False, True):
        seq = items[::-1] if refl else items
        # reversal maps the cyclic sequence r f r f ... to f r f r ...: rotate by one to start at a ray
        if refl:
            seq = seq[1:] + seq[:1]
        for k in range(0, 8, 2):
            t = seq[k:] + seq[:k]
            faces = tuple(x for x, kind in t if kind == "f")
            lab = t[0][0]                       # line label of the ray at position 0
            imgs.append((faces, lab))
    best = min(im[0] for im in imgs)
    labs = {lab for fc, lab in imgs if fc == best}
    r = (best, labs.pop() if len(labs) == 1 else None)
    _SVC[key] = r
    return r


def sv_events(cur):
    """[(column key, count)] of the SV cell at the simple frame cur (empty for symmetric cells)"""
    c, role = sv_cell_role(cur.bout[0], cur.bin[0], cur.bin[1], cur.bout[1])
    if role is None:
        return []
    k0, k1 = ("SV", c, 0), ("SV", c, 1)
    return [(k0, -1), (k1, 1)] if role == 0 else [(k0, 1), (k1, -1)]


def tri_events(cur, nxt):
    """[(column key, count)] for the triangles on the segment after cur (one per side bit): cell = multiset of the multiplicities of the three
    vertices (endpoints of the segment + apex), role of this side line = multiplicity of the OPPOSITE vertex (the apex); transfers between the
    side lines of different roles, both directions."""
    out = collections.Counter()
    if nxt is None:
        return []
    for s_ in (0, 1):
        if not cur.bout[s_]:
            continue
        ap = cur.aout[s_]
        if ap == 0:
            continue
        m = ["T" if cur.kind == "T" else "S", "T" if nxt[0] == "T" else "S", "T" if ap == 1 else "S"]
        cell = "".join(sorted(m))
        if cell in ("SSS", "TTT"):
            continue
        r = m[2]
        # number of side lines of each role: role = multiplicity of the opposite vertex, the three opposite vertices are the three vertices
        nT, nS = m.count("T"), m.count("S")
        other = "S" if r == "T" else "T"
        nother = nS if r == "T" else nT
        # this line pays w[r>other] to each of the nother lines of role `other`, receives w[other>r] from each of them
        out[("TRI", cell, r + ">" + other)] -= nother
        out[("TRI", cell, other + ">" + r)] += nother
    return [(k, x) for k, x in out.items() if x]


# ---------------------------------------------------------------------------------------------------- point configurations and credits
def cfg_apply(ring, sec, s, k):
    r = "".join(ring[(s * i + k) % 6] for i in range(6))
    sc = tuple(sec[(i + k) % 6] for i in range(6)) if s == 1 else tuple(sec[(-i - 1 + k) % 6] for i in range(6))
    return r, sc


_CFGC = {}


def cfg_role(ring, sec, j0):
    """Full point configuration = 6 ray statuses (cyclic order) + 6 sector bits (sector m between rays m and m+1), canonical under the
    dihedral group.  The line owning the rays j0, j0+3: returns (canonical cfg, role class) if it owns the middle ray of a run of 3
    non-bridge rays, else None.  Role class = smallest line index in the orbit of the line under the automorphisms of the cfg."""
    ring = "".join(ring)
    sec = tuple(int(bool(x)) for x in sec)
    key = (ring, sec, j0 % 3)
    if key in _CFGC:
        return _CFGC[key]
    cands = [(cfg_apply(ring, sec, s, k), s, k) for s in (1, -1) for k in range(6)]
    (c, sc), s, k = min(cands, key=lambda t: t[0])
    i = (s * (j0 - k)) % 6
    line = i % 3
    aut = [(s2, k2) for s2 in (1, -1) for k2 in range(6) if cfg_apply(c, sc, s2, k2) == (c, sc)]
    role = min((s2 * line + k2) % 3 for (s2, k2) in aut)
    mids = [m for m in range(6) if all(c[(m + d) % 6] != "R" for d in (-1, 0, 1))]
    out = ((c, sc), role) if (line in mids or (line + 3) % 6 in mids) else None
    _CFGC[key] = out
    return out


_ROWC = {}


def cfg_row(cfg):
    """{role: multiplicity} over the three lines of the canonical configuration cfg (only credit-eligible lines)"""
    if cfg in _ROWC:
        return _ROWC[cfg]
    c, sc = cfg
    m = collections.Counter()
    for line in range(3):
        cr = cfg_role(c, sc, line)
        if cr is not None:
            assert cr[0] == cfg
            m[cr[1]] += 1
    _ROWC[cfg] = dict(m)
    return _ROWC[cfg]


def pt_events(cur):
    """PT cells at the triple frame cur: key = the 6 sector bits of the point (canonical under the dihedral group), fully visible to the three
    lines; role of L = orbit of its line index.  Transfers between different roles, both directions (count = number of lines of the other role)."""
    sec6 = (cur.bout[0], cur.h[0], cur.bin[0], cur.bin[1], cur.h[1], cur.bout[1])
    cr = cfg_role("NNNNNN", sec6, 0)
    (ring_c, sec_c), role = cr[0], cr[1]
    row = cfg_row(cr[0])
    out = []
    for other, mult in row.items():
        if other == role:
            continue
        out.append((("PT", sec_c, f"{role}>{other}"), -mult))
        out.append((("PT", sec_c, f"{other}>{role}"), mult))
    return out


class FCatalogue(RL.SigCatalogue):
    """SigCatalogue with extras (all optional):
      hidden_filters   extra restrictions of the triple-window hidden domain, f(prev, cur, nxt, sig) -> True if impossible
      celldom          T23 axis-cell filter: completions whose block cell is not an axis-visible cell are impossible
      split_a          portion split LP column a in [0, 1/3]: own portion 6a, touch 3(1-a) (v2 units); base v2 - 2 own + touch,
                       column count 3 own - 1.5 touch (per window)
      alpha            LP column alpha' in [0, 1]: alpha' * (3 s - 1 - v_base), s = (n - 2) - #triangle bits on L's segments, valid
                       because the terms sum to the waste; v_base = value at a = 1/3.  In 2*final+2 units, per path 6 (W - 1) alpha'
                       (attached to the first window) and per window alpha' * (-6 bits - v2_base).
    """

    def project(self, sg):
        """coarsen a block signature (rule cell): drop the features in self.proj ('u', 'pL', 'pR', 'p' = both, 'tL', 'tR', 't' = both, 'oth')"""
        ring5, u, pL, pR, tL, tR, oth = sg
        pr = self.proj
        if "u" in pr:
            u = 0
        if "p" in pr:
            pL = pR = 0
        if "pL" in pr:
            pL = 0
        if "pR" in pr:
            pR = 0
        if "t" in pr:
            tL = tR = 0
        if "oth" in pr and oth != RL.NOOTH:
            oth = (0, 0, 0)
        if "ring" in pr:
            ring5 = (ring5[0], "X", "X", "X", ring5[4])
        return (ring5, u, pL, pR, tL, tR, oth)

    def role_vec(self, role, sg):
        if self.proj:
            sg = self.project(sg)
        return super().role_vec(role, sg)

    def __init__(self, *a, hidden_filters=(), celldom=False, split_a=False, alpha=False, W=17, tau=False, afix=None, proj=(), wr=False, sv=False, tri=False, pt=False, **kw):
        super().__init__(*a, **kw)
        self.proj = set(proj)
        self.wr = wr
        self.sv, self.tri, self.pt = sv, tri, pt
        self.extra_rows = []
        self.hidden_filters = list(hidden_filters)
        self.celldom, self.split_a, self.alpha, self.W = celldom, split_a, alpha, W
        self.tau, self.afix = tau, afix
        self.tau_rows = {}          # canonical cfg -> {role: multiplicity}
        if celldom:
            sys.path.insert(0, str(ROOT / "work/eng/T23"))
            from cell_domains_lib import AXIS_CELLS
            self.axis_cells = AXIS_CELLS
        self.stats = collections.Counter()

    def cell_ok(self, cell):
        if not self.celldom:
            return True
        ok = cell in self.axis_cells or RL.mirror_sig(cell) in self.axis_cells
        if not ok:
            self.stats["cell_removed"] += 1
        return ok

    # ---- cap role (simple vertex) : copy of SigCatalogue.cap_terms with the axis-cell filter
    def cap_terms(self, prev, cur, nxt):
        if prev is None or nxt is None:
            return ()
        terms = []
        for k in (0, 1):
            if not (cur.bin[k] and cur.bout[k]):
                continue
            o = 1 - k
            u = int(cur.ub[o])
            pR, pL = cur.bin[o], cur.bout[o]
            tR, tL = int(prev[0] == "T"), int(nxt[0] == "T")
            fR = "R" if (prev[0] == "T" and prev[1][k]) else "N"
            fL = "R" if (nxt[0] == "T" and nxt[1][k]) else "N"
            s12, s45 = fR == "R", fL == "R"
            if self.norr and s12 and s45:
                return None
            if self.rfree and (s12 or s45):
                return None
            opts = set()
            for s23 in (0, 1):
                for s34 in (0, 1):
                    dbl = (s12 and s23, s23 and s34, s34 and s45)
                    for far in RL.itertools.product(*[(0, 1) if d else (None,) for d in dbl]):
                        x = ["N" if d is None else ("B" if d == 0 else "R") for d in far]
                        if (x[0] == "B" and x[1] == "B") or (x[1] == "B" and x[2] == "B"):
                            continue
                        if self.rfree and "R" in x:
                            continue
                        if self.rings is not None and RL.canon_ring(("B", fR) + tuple(x) + (fL,)) not in self.rings:
                            continue
                        if self.norr and ((x[0] == "B" and (fR == "R" and x[1] == "R")) or (x[1] == "B" and x[0] == "R" and x[2] == "R")
                                          or (x[2] == "B" and x[1] == "R" and fL == "R")):
                            continue
                        ring5 = (fR, x[0], x[1], x[2], fL)
                        for oth in (RL.OTH_STATUSES if x[1] == "B" else (RL.NOOTH,)):
                            cell = (ring5, u, pL, pR, tL, tR, oth)
                            if not self.cell_ok(cell):
                                continue
                            opts.add(self.role_vec("C", cell))
            if not opts:
                return None
            terms.append(tuple(sorted(opts)))
        return tuple(sorted(terms))

    # ---- flank / axis roles (triple vertex) : copy of SigCatalogue.triple_terms with the axis-cell filter on flank completions
    def triple_terms(self, prev, cur, nxt, sig, r, zero=()):
        terms = []
        done = set()
        for j in range(6):
            if r[j] != "B" or j in done:
                continue
            ring5 = tuple(r[(j + t) % 6] for t in range(1, 6))
            if j % 3 == 0:
                terms.append((self.role_vec("A", self.sig_axis(prev, nxt, sig, r, j)),))
                continue
            jo = (j + 3) % 6
            grp = [j] + ([jo] if r[jo] == "B" else [])
            done.update(grp)
            info = []
            for jj in grp:
                side, ok, sg_, own, hid = RL.M_TABLE[jj]
                other = nxt if ok == "nxt" else prev
                pM = other[1][sg_] if other[0] == "T" else 0
                tOwn = int(other[0] == "T")
                tHid = sig[RL.POS_IDX[hid]]
                info.append((jj, side, pM, tOwn, tHid))
            opts = set()
            for comp in RL.itertools.product(*[self._m_completions(pM, tHid, jj in zero) for (jj, side, pM, tOwn, tHid) in info]):
                vec = collections.Counter()
                sgs = []
                for (jj, side, pM, tOwn, tHid), (u, pO) in zip(info, comp):
                    sgs.append((jj, side, pM, tOwn, tHid, u, pO))
                cells = []
                bad = False
                for idx_, (jj, side, pM, tOwn, tHid, u, pO) in enumerate(sgs):
                    if side == "L":
                        pL, pR, tL, tR = pM, pO, tOwn, tHid
                    else:
                        pR, pL, tR, tL = pM, pO, tOwn, tHid
                    if len(sgs) == 2:
                        jj2, side2, pM2, tOwn2, tHid2, u2, pO2 = sgs[1 - idx_]
                        oth = (u2, pM2, pO2) if side2 == "L" else (u2, pO2, pM2)
                    else:
                        oth = RL.NOOTH
                    r5 = tuple(r[(jj + t) % 6] for t in range(1, 6))
                    cell = (r5, u, pL, pR, tL, tR, oth)
                    if not self.cell_ok(cell):
                        bad = True
                        break
                    cells.append((side, cell))
                if bad:
                    continue
                for side, cell in cells:
                    for cc, x in self.role_vec(side, cell):
                        vec[cc] += x
                opts.add(tuple(sorted((c, x) for c, x in vec.items() if x)))
            if not opts:
                self.stats["window_no_completion"] += 1
                return None
            terms.append(tuple(sorted(opts)))
        return tuple(sorted(terms))

    def sig_options(self, prev, cur, nxt):
        """all admissible hidden assignments of a triple window: list of (sig, g, option) with option = (v2, p, nRN, nRR, terms)"""
        out = []
        for (sig, g) in LA.sig_domain(prev, cur, nxt):
            if self.enriched and not RL.tau_compatible(cur, sig):
                continue
            r = RL.ring_of(prev, cur, nxt, sig)
            if self.rfree and "R" in r:
                continue
            if self.norr and RL.has_rr_block(r):
                continue
            if self.rings is not None and RL.canon_ring(r) not in self.rings:
                continue
            if self.k1 and RL.k1_violation(prev, cur, nxt, sig):
                continue
            if any(f(prev, cur, nxt, sig) for f in self.hidden_filters):
                continue
            zero = set()
            if self.k2g:
                g, zero = RL.k2g_force(prev, cur, nxt, sig)
            p, v2, nRN, nRR, nT = LA.exact_vec(prev, cur, nxt, (sig, g))
            tt = self.triple_terms(prev, cur, nxt, sig, r, zero)
            if tt is None:
                continue
            if self.tau:
                sec6 = (cur.bout[0], cur.h[0], cur.bin[0], cur.bin[1], cur.h[1], cur.bout[1])
                cr = cfg_role(r, sec6, 0)
                if cr is not None:
                    if cr[0] not in self.tau_rows:
                        self.tau_rows[cr[0]] = cfg_row(cr[0])
                        for role in sorted(self.tau_rows[cr[0]]):
                            self.col(("U", cr[0], role))
                    tt = tuple(sorted(tt + ((((self.col(("U", cr[0], cr[1])), -1),),),)))
            out.append((sig, g, self.finish(prev, cur, nxt, (v2, p, nRN, nRR, tt))))
        return out

    def finish(self, prev, cur, nxt, opt):
        """add the split / alpha' columns to a window option"""
        v2, p, nRN, nRR, terms = opt
        if not (self.split_a or self.alpha or self.wr or self.sv or self.tri or self.pt):
            return opt
        own = int(nxt is not None and cur.bout == NONE_)
        touch = sum(1 for k in (0, 1) if not cur.ub[k] and cur.bin[k] + cur.bout[k] == 0) if cur.kind == "S" else 0
        bits = (cur.bout[0] + cur.bout[1]) if nxt is not None else 0
        ex = []
        v2n = v2
        if self.split_a:
            v2n = v2 - 2 * own + touch
            ca = 3 * own - 1.5 * touch
            if ca:
                ex.append((self.col(("a",)), ca))
        if self.alpha:
            x = (-6 * bits - v2) / 2 + (3 * (self.W - 1) if prev is None else 0)
            if x:
                ex.append((self.col(("alpha",)), x))
        if self.wr and own:
            # waste recovery: the lost touch share at every TRIPLE endpoint of an own unused segment goes back to the line itself
            cw = int(cur.kind == "T") + int(nxt[0] == "T")
            if cw:
                ex.append((self.col(("wr",)), cw))
                if not self.extra_rows:
                    self.extra_rows = [({("wr",): 1.0, ("a",): 1.5}, 1.5)]
        if self.sv and cur.kind == "S":
            for key_, x_ in sv_events(cur):
                ex.append((self.col(key_), x_))
        if self.tri:
            for key_, x_ in tri_events(cur, nxt):
                ex.append((self.col(key_), x_))
        if self.pt and cur.kind == "T":
            for key_, x_ in pt_events(cur):
                ex.append((self.col(key_), x_))
        if ex:
            terms = tuple(sorted(tuple(terms) + ((tuple(sorted(ex)),),)))
        return (v2n, p, nRN, nRR, terms)

    def window_options(self, prev, cur, nxt):
        if cur.kind == "S":
            if self.k2 and RL.k2_violation(prev, cur, nxt):
                return set()
            p, v2, nRN, nRR, nT = LA.exact_vec(prev, cur, nxt)
            ct = self.cap_terms(prev, cur, nxt)
            if ct is None:
                return set()
            return {self.finish(prev, cur, nxt, (v2, p, nRN, nRR, ct))}
        return {o for (_, _, o) in self.sig_options(prev, cur, nxt)}


NONE_ = LA.NONE


def option_value(o, w):
    """value (in units of v2, i.e. 2*value) of a window option at weights w (dict col -> weight or array): v2 + 2 * sum_terms min_alt w.vec"""
    v2, p, nRN, nRR, terms = o
    tot = 0.0
    for t in terms:
        tot += min(sum(w[c] * x for c, x in vec) for vec in t)
    return v2 + 2.0 * tot


def frame_pred(kind=None, bin=(0, 0), bout=(0, 0), h=(0, 0), ain=(0, 0), aout=(0, 0), exact=None):
    return (kind, tuple(bin), tuple(bout), tuple(h), tuple(ain), tuple(aout), exact)


def match_pred(pred, f):
    kind, bin_, bout, h, ain, aout, exact = pred
    if f.kind not in ("S", "T"):
        return False                     # M frames (multiplicity >= 4) never match a pattern proved for multiplicity <= 3
    if exact is not None:
        return f == exact
    if kind == "T" and f.kind != "T":
        return False
    if kind == "S" and f.kind != "S":
        return False
    for s in (0, 1):
        if bin_[s] and not f.bin[s]:
            return False
        if bout[s] and not f.bout[s]:
            return False
        if h[s] and not (f.kind == "T" and f.h[s]):
            return False
        if ain[s] and f.ain[s] != ain[s]:
            return False
        if aout[s] and f.aout[s] != aout[s]:
            return False
    return True


def preds_from_core(core):
    """patsat.Pattern (positive core, no sig) -> list of frame predicates (one per slot)"""
    out = []
    m = len(core.slots)
    for s, (k, h) in enumerate(core.slots):
        bin_ = core.seg.get(s - 1, (0, 0)) if s > 0 else (0, 0)
        bout = core.seg.get(s, (0, 0)) if s < m - 1 else (0, 0)
        ain = tuple(core.apex.get((s - 1, sg), 0) for sg in (0, 1)) if s > 0 else (0, 0)
        aout = tuple(core.apex.get((s, sg), 0) for sg in (0, 1)) if s < m - 1 else (0, 0)
        out.append(frame_pred(k if k == "T" else None, bin_, bout, h if k == "T" else (0, 0), ain, aout))
    return out


class PatternSet:
    """forbidden frame patterns: list of (anchored, [frame predicates]).  anchored = must start at the first vertex of the line
    (used for exact-n-only bans of whole words).  Subset-construction automaton: state = frozenset of (pattern index, matched length)."""

    def __init__(self, patterns=()):
        self.pats = [(bool(a), tuple(p)) for a, p in patterns]
        self._cache = {}
        self.init = frozenset((j, 0) for j, (a, p) in enumerate(self.pats) if a)

    def step(self, state, f):
        key = (state, f)
        r = self._cache.get(key)
        if r is not None:
            return r if r != "BAD" else None
        new = set()
        for (j, i) in state:
            a, ps = self.pats[j]
            if match_pred(ps[i], f):
                new.add((j, i + 1))
        for j, (a, ps) in enumerate(self.pats):
            if not a and match_pred(ps[0], f):
                new.add((j, 1))
        bad = any(i == len(self.pats[j][1]) for (j, i) in new)
        if bad:
            self._cache[key] = "BAD"
            return None
        res = frozenset(new)
        self._cache[key] = res
        return res


_K3_ORIG = RL.k3_step


def install_combined_step(k3, pset, f5=False, noclean=False, onlyclean=False, tmode=None, group=None, fmode=None):
    """monkeypatch rule_lp.k3_step by K3 (optional) + F5* (optional) + pattern automaton + 'no clean line' flag; the WGraph must be built
    with k3=True.  State: (0, 0) initially, then ("X", k3 state, pattern state, U, NC) with U = union of the ub flags of the vertices
    seen so far and NC = a non-clean frame (T frame or a simple vertex capping a block) has been seen.
    F5* (proved, THEORY section 19): no two different vertices of L carry ub flags on opposite sides.
    noclean: paths without any non-clean frame (clean lines) are deleted (terminal dropped)."""
    def step(state, prev, cur, ni):
        if state == (0, 0):
            k3s, pst, U, NC, TC, FL = (0, 0), (pset.init if pset is not None else frozenset()), (0, 0), 0, 0, 0
        else:
            _, k3s, pst, U, NC, TC, FL = state
        if k3:
            k3n = _K3_ORIG(k3s, prev, cur, ni)
            if k3n is None:
                return None
        else:
            k3n = (0, 0)
        if f5:
            a, b = cur.ub
            if (U[0] and b) or (U[1] and a):
                return None
            U = (U[0] | a, U[1] | b)
        if pset is not None and pset.pats:
            pst = pset.step(pst, cur)
            if pst is None:
                return None
        if noclean or onlyclean:
            if cur.kind != "S" or (cur.bin[0] and cur.bout[0]) or (cur.bin[1] and cur.bout[1]):
                NC = 1
            if noclean and ni is None and not NC:
                return None
            if onlyclean and NC:
                return None
        if tmode:
            if cur.kind == "T":
                TC = min(TC + 1, 2)
            if tmode == "lt2" and TC >= 2:
                return None
            if tmode == "ge2" and ni is None and TC < 2:
                return None
        if group is not None and fmode:
            if (prev, cur, ni) in group:
                FL = 1
            if fmode == "f0" and FL:
                return None
            if fmode == "f1" and ni is None and not FL:
                return None
        return ("X", k3n, pst, U, NC, TC, FL)
    RL.k3_step = step


def word_pattern(frames):
    """anchored exact pattern: the whole line has exactly these (enriched) frames"""
    return (True, [frame_pred(exact=f) for f in frames])


def preds_from_pat(v, rel=None):
    """search/automaton_facts.Pat (one orientation) -> frame predicates; rel[i] = the S slot i may match a triple vertex (the pattern uses at most
    one of its two lines, see automaton_facts.used_lines); otherwise an S slot needs a simple vertex and a T slot a triple vertex"""
    out = []
    m = len(v.slots)
    for i, (k, h) in enumerate(v.slots):
        bin_ = v.seg.get(i - 1, (0, 0)) if i > 0 else (0, 0)
        bout = v.seg.get(i, (0, 0)) if i < m - 1 else (0, 0)
        ain = tuple(v.apex.get((i - 1, sg), 0) for sg in (0, 1)) if i > 0 else (0, 0)
        aout = tuple(v.apex.get((i, sg), 0) for sg in (0, 1)) if i < m - 1 else (0, 0)
        kind = "T" if k == "T" else (None if (rel is not None and rel[i]) else "S")
        out.append(frame_pred(kind, bin_, bout, h if k == "T" else (0, 0), ain, aout))
    return out


def facts_pattern_set(base=None, names=None):
    """all proven sig-free forbidden patterns of search/automaton_facts.py (P000-P009), four orientations each, as an unanchored PatternSet"""
    import automaton_facts as AF
    pats = [] if base is None else [(a, list(p)) for a, p in base.pats]
    seen = set()
    for f in AF.FACTS:
        if names is not None and f.name not in names:
            continue
        if f.pat.sig:
            continue                     # sig-conditioned facts are not frame patterns
        for v, rel in zip(f.vars, f.relax):
            key = (tuple(v.slots), tuple(sorted(v.seg.items())), tuple(sorted(v.apex.items())), tuple(rel))
            if key in seen:
                continue
            seen.add(key)
            pats.append((False, preds_from_pat(v, rel)))
    return PatternSet(pats)


def pattern_set_from_json(path, base=None):
    """json list of serialised positive patterns (patsat format: slots [[kind,[h+,h-]]], seg [[s,[b+,b-]]], apex [[s,sg,v]], sig []): the four symmetric
    variants (flip sides, reverse direction) of each are forbidden as unanchored frame patterns"""
    sys.path.insert(0, str(ROOT / "work/eng/T23"))
    import patsat
    pats = [] if base is None else [(a, list(p)) for a, p in base.pats]
    seen = set()
    for c in json.load(open(path)):
        pt = patsat.Pattern([(k, tuple(h)) for k, h in c["slots"]], {s_: tuple(b) for s_, b in c["seg"]},
                            {(s_, sg): v for s_, sg, v in c["apex"]}, {})
        for v in patsat.variants(pt):
            key = patsat.key(v)
            if key in seen:
                continue
            seen.add(key)
            pats.append((False, preds_from_core(v)))
    return PatternSet(pats)


def preds_from_core_dict(c):
    """serialised patsat pattern (dict with slots/seg/apex/sig) -> frame predicates (no sig)"""
    class _P:
        pass
    p = _P()
    p.slots = [(k, tuple(h)) for k, h in c["slots"]]
    p.seg = {s: tuple(b) for s, b in c["seg"]}
    p.apex = {(s, sg): v for s, sg, v in c["apex"]}
    return preds_from_core(p)


if __name__ == "__main__":
    main()

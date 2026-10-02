"""A30 item 2: independent exact check of T25's elimination certificates (state_2.pkl)."""
import sys, pickle, math, time, collections
from fractions import Fraction as F
import numpy as np
ROOT = __import__("pathlib").Path(__file__).resolve().parents[4].as_posix()
sys.path.insert(0, ROOT + "/search"); sys.path.append(ROOT + "/work/t3"); sys.path.insert(0, ROOT + "/work/eng/A30/elim")
import __main__
import rule_lp as RL
__main__.EFrame = RL.EFrame
import dplib as DP

st0 = pickle.load(open(ROOT + "/work/eng/T25/elim/state_0.pkl", "rb"))
st2 = pickle.load(open(ROOT + "/work/eng/T25/elim/state_2.pkl", "rb"))
certs = st2["certs"]
a0_reprs = set(repr(w) for w in st0["allowed"])
a2_reprs = set(repr(w) for w in st2["allowed"])
print("state_0 allowed", len(a0_reprs), " state_2 allowed", len(a2_reprs), " certs", len(certs), flush=True)

Gf = DP.Graph(ROOT + "/work/eng/A30/elim/g_full.pkl")
Ga = DP.Graph(ROOT + "/work/eng/A30/elim/g_a0.pkl")
print("full graph: N", Gf.N, "edges", len(Gf.src), "windows", Gf.nwin, "| a0 graph: N", Ga.N, "edges", len(Ga.src), "windows", Ga.nwin, flush=True)
# consistency: a0 graph windows == state_0 allowed
assert set(Ga.win_repr) <= a0_reprs, "a0 graph has windows outside state_0 allowed"
print("a0 graph windows subset of state_0.allowed:", len(set(Ga.win_repr)), "of", len(a0_reprs))

# ---- bounds
bad = 0
for c in certs:
    D = c["D"]; w = {k: F(x, D) for k, x in c["w"].items()}
    a = w.get(("a",), F(0)); al = w.get(("alpha",), F(0)); wr = w.get(("wr",), F(0))
    ok = all(v >= 0 for v in w.values()) and a <= F(1, 3) and al <= 1 and wr + F(3, 2) * a <= F(3, 2)
    if not ok:
        bad += 1; print("BOUNDS VIOLATED", c["name"])
print("bounds violations:", bad)

# ---- per-certificate validity (min over graph >= 2D)
def cert_wmin(G, c):
    wcol = G.weights_vec(c["w"])
    ov = G.window_values(wcol, c["D"])
    return G.wmin_array(ov), ov, len(c["w"]) - len(wcol)

res = []
t0 = time.time()
for i, c in enumerate(certs):
    G = Gf if i < 5 else Ga
    wm, ov, miss = cert_wmin(G, c)
    mn = G.path_min(wm)
    D = c["D"]
    res.append((c["name"], D, mn, miss))
    print(f"{c['name']:10s} D={D:8d} graph={'full' if i < 5 else 'a0':4s} min={mn} need>={2*D} final_min={F(mn - 2*D, 2*D)} unused_keys={miss}  {'OK' if mn >= 2*D else 'FAIL'}  [{time.time()-t0:.0f}s]", flush=True)
pickle.dump(res, open(ROOT + "/work/eng/A30/elim/validity.pkl", "wb"))

# ---- strictness on the targeted window (single-window tasks T{i} / S{i}; indices into the sorted allowed list of state_0)
Tw = sorted([w for w in st0["allowed"] if w[1].kind == "T"], key=repr)
Sw = sorted([w for w in st0["allowed"] if w[1].kind == "S"], key=repr)
print("state_0 T windows", len(Tw), "S windows", len(Sw))
idx_a = {r: i for i, r in enumerate(Ga.win_repr)}
strict_windows = {}
nstrict = 0
for i, c in enumerate(certs[5:], 5):
    nm = c["name"]
    kind, num = nm[3], int(nm[4:])
    w = (Tw if kind == "T" else Sw)[num]
    r = repr(w)
    if r not in idx_a:
        print(nm, "WINDOW NOT IN a0 GRAPH (dropped as no-option window?)"); continue
    mask = np.zeros(Ga.nwin, dtype=bool); mask[idx_a[r]] = True
    wm, ov, miss = cert_wmin(Ga, c)
    mn_all, mn_thru = Ga.path_min(wm, flag_mask=mask)
    D = c["D"]
    okv = mn_all >= 2 * D
    oks = mn_thru > 2 * D if mn_thru < int(DP.INF) else True
    strict_windows[nm] = r
    nstrict += okv and oks
    if not (okv and oks) or i < 8:
        print(f"{nm:10s} D={D} all-min {mn_all}  through-window min {mn_thru if mn_thru < int(DP.INF) else 'no path'}  (2D={2*D})  margin final >= {F(mn_thru-2*D, 2*D) if mn_thru < int(DP.INF) else None}  valid={okv} strict={oks}")
print("strict-on-own-window OK:", nstrict, "of", len(certs) - 5)
removed_by_stored = set(strict_windows.values())
print("distinct windows targeted by the 55 stored certs:", len(removed_by_stored))
removed = set(repr(w) for w in st2["removed"])
print("T25's removed set:", len(removed), " covered by stored single-window certs:", len(removed & removed_by_stored))

# ---- joint tightness (exact) under the 60 certificates on the a0 graph (no removal), and under the 5 initial ones on the full graph
from math import gcd
def lcm(a, b): return a * b // gcd(a, b)

def joint(G, cert_list, label):
    L = 1
    for c in cert_list: L = lcm(L, c["D"])
    nw = G.nwin
    comb = np.zeros(nw, dtype=np.int64)
    common = [None] * nw
    for c in cert_list:
        wcol = G.weights_vec(c["w"])
        ov = G.window_values(wcol, c["D"])
        f = L // c["D"]
        for j, vals in enumerate(ov):
            m = min(vals)
            s = {k for k, v in enumerate(vals) if v == m}
            common[j] = s if common[j] is None else (common[j] & s)
            comb[j] += f * m
    ok = np.array([bool(s) for s in common])
    BIG = np.int64(1 << 50)        # invalid windows (no common tight option): any path through one is > 2^49 > target
    LIM = 1 << 49
    cw = np.where(ok, comb, BIG)
    target = 2 * L * len(cert_list)
    assert target < LIM // 100
    F_ = G.layered_forward(cw[G.ew])[0]
    B = G.backward(cw[G.ew], cw)
    tight = np.zeros(len(G.src), dtype=bool)
    best = int(DP.INF)
    for c in range(DP.W17 + 1):
        for c0 in (1, 2):
            rem = DP.W17 - c - c0
            if rem < 0: continue
            m = G.m_by[c0]
            fs = F_[c][G.src[m]]; bs = B[rem][G.dst[m]]
            good = (fs < LIM) & (bs < LIM) & ok[G.ew[m]]
            tot = np.where(good, fs + cw[G.ew[m]] + bs, DP.INF)
            if good.any(): best = min(best, int(tot[good].min()))
            tight[m] |= (tot == target)
    tterm = np.zeros(len(G.tn), dtype=bool)
    for i, (u, wi) in enumerate(zip(G.tn.tolist(), G.tw.tolist())):
        c = DP.W17 - int(G.ku[u])
        if c >= 0 and ok[wi] and F_[c][u] < LIM:
            v = int(F_[c][u]) + int(cw[wi])
            best = min(best, v)
            if v == target: tterm[i] = True
    wins = set(G.win_repr[int(w)] for w in G.ew[tight]) | set(G.win_repr[int(w)] for w in G.tw[tterm])
    print(f"[{label}] joint tightness: min combined {best}, target {target}, {'CONSISTENT (all certs valid)' if best == target else 'INCONSISTENT'}; tight edges {int(tight.sum())}, terminals {int(tterm.sum())}, windows {len(wins)}", flush=True)
    return wins, tight, tterm

w5, _, _ = joint(Gf, certs[:5], "5 initial certs on FULL graph")
print("  windows tight under the 5 initial certs:", len(w5), " subset of state_0.allowed:", w5 <= a0_reprs, " equal:", w5 == a0_reprs, " |w5 - a0|=", len(w5 - a0_reprs), " |a0 - w5|=", len(a0_reprs - w5))
w60, tight60, tterm60 = joint(Ga, certs, "60 certs on a0 graph (no removal)")
print("  windows tight under all 60:", len(w60), " subset of state_2.allowed:", w60 <= a2_reprs, " equal:", w60 == a2_reprs, " |w60 - a2|=", len(w60 - a2_reprs), " |a2 - w60|=", len(a2_reprs - w60))
# also: same with the removed windows deleted from the graph (T25's own procedure)

extra = sorted(w60 - a2_reprs)
print("extra windows (tight under stored 60 certs but removed by T25):")
for r in extra:
    print("  in T25 removed set:", r in removed, r[:160])
pickle.dump(dict(w60=w60, extra=extra), open(ROOT + "/work/eng/A30/elim/w60.pkl", "wb"))

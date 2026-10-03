"""second implementation: T25's own graph + RL.min_by_units on the FC integer weights at exact W; plus planted single-weight decrements (A30 DP)."""
import sys, pickle, argparse
import numpy as np
from fractions import Fraction as F
R = str(__import__("pathlib").Path(__file__).resolve().parents[3])
sys.path.insert(0, R + "/search"); sys.path.append(R + "/work/t3"); sys.path.insert(0, R + "/work/eng/A30/elim")
import __main__
import rule_lp as RL, rule_lp_t25 as T
__main__.EFrame = RL.EFrame
import dplib as DP
W = int(sys.argv[1]); nocd = len(sys.argv) > 2 and sys.argv[2] == "nocd"
st = pickle.load(open(R + "/work/eng/T25/elim/state_2.pkl", "rb")); c = st["certs"][1]; D = c["D"]
ap = T.add_args(argparse.ArgumentParser())
o = ap.parse_args(["lp", "--class", "full", "--split", "--alpha"] + ([] if nocd else ["--celldom"]) + ["--wr", "--sv", "--tri", "--pt", "--eps", "0", "--exactw", str(W)])
G = T.build_graph(o)
wint = np.zeros(G.K, dtype=np.int64)
miss = 0
for k, x in c["w"].items():
    if k in G.cat.idx: wint[G.cat.idx[k]] = x
    elif x: miss += 1
print("W", W, "missing keys", miss)
mb = RL.min_by_units(G, wint, D, W)
print("T25 min_by_units D*(2final+2) per units:", {u: mb[u] for u in sorted(mb)}, " need >=", 2 * D)
# planted decrements with the A30 DP on the exported graph
Gx = DP.Graph(f"{R}/work/eng/othern/g_W{W}.pkl")
det = tot = 0
for k, x in c["w"].items():
    if not x: continue
    w2 = dict(c["w"]); w2[k] = x - 1
    wm = Gx.wmin_array(Gx.window_values(Gx.weights_vec(w2), D))
    mn = Gx.path_min(wm, W=W)
    tot += 1; det += mn < 2 * D
print(f"planted -1/D decrements detected: {det}/{tot}")

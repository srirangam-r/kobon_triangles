"""Sensitivity test: build the FC-M graph at exact weight W once, check the true weights (min = target), then lower each of the 15 weights by 1/16
(and raise it by 1/16 for contrast) and report the DP minimum.  usage: PAIRLEM=1 planted_fcm.py W   (flags as in verify_fcm_n.sh)"""
import sys, pickle, argparse
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3].as_posix()
sys.path.insert(0, ROOT + "/search"); sys.path.append(ROOT + "/work/t3"); sys.path.append(ROOT + "/work/eng/T27")
import numpy as np
import rule_lp_t25 as T, rule_lp_t25m as M
W = int(sys.argv[1]); D = 16
w = pickle.load(open(ROOT + "/work/eng/T27/cegar/w_FCM25.pkl", "rb"))
flags = "lp --class full --split --alpha --wr --sv --tri --pt --splitm --mb --wmax 1000 --projall AC,AL,LC,LR --pats work/eng/T27/cegar/pats.json --eps=-1/12".split() + ["--exactw", str(W)]
import os; os.chdir(ROOT)
o = M.add_m_args(argparse.ArgumentParser()).parse_args(flags)
M.apply_m_opts(o)
G = M.build_graph_m(o)
target = T.target_of(o)
def run(dw=None):
    wi = np.zeros(G.K)
    for k, x in w.items():
        wi[G.cat.idx[k]] = round(x * D)
    if dw: wi[G.cat.idx[dw[0]]] += dw[1]
    v, kind, cnt = M.solve_exactw_m(G, wi, W, scale=D)
    return v
print("base", run(), "target*D", target * D, flush=True)
bad = 0
for k in w:
    if abs(w[k]) < 1e-9: continue
    v = run((k, -1))
    bad += v < target * D - 1e-9
    print("decrement", k, "->", v, "DETECTED" if v < target * D - 1e-9 else "not detected (slack)", flush=True)
print("detected", bad, "of", sum(1 for k in w if abs(w[k]) > 1e-9))

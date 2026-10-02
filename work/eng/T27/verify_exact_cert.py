"""independent exact re-verification of an LP certificate with the CURRENT code: rebuild the graph with the same flags, round w to integers / D, run the exact integer DP.
usage: PAIRLEM=1 verify_exact_cert.py w.pkl D <rule_lp_t25m lp flags...>   (prints min D*(2*final+2) per unit count and the target)"""
import sys, pickle, argparse
ROOT = __import__("pathlib").Path(__file__).resolve().parents[3].as_posix()
sys.path.insert(0, ROOT + "/search"); sys.path.append(ROOT + "/work/t3"); sys.path.append(ROOT + "/work/eng/T27")
import numpy as np
from fractions import Fraction as F
import rule_lp_t25 as T, rule_lp_t25m as M
w = pickle.load(open(sys.argv[1], "rb")); D = int(sys.argv[2])
ap = M.add_m_args(argparse.ArgumentParser())
o = ap.parse_args(sys.argv[3:])
M.apply_m_opts(o)
G = M.build_graph_m(o)
target = T.target_of(o)
wi = np.zeros(G.K)
miss = []
for k, x in w.items():
    if k in G.cat.idx: wi[G.cat.idx[k]] = round(x * D)
    else: miss.append(k)
print("weights", len(w), "not in the rebuilt catalogue:", miss)
assert all(abs(x * D - round(x * D)) < 1e-6 for x in w.values())
v, kind, cnt = M.solve_exactw_m(G, wi, o.exactw, scale=D)
print("exact DP min D*(2*final+2) =", v, " target * D =", target * D, " OK:", v is not None and v >= target * D - 1e-9)
mb = M.min_by_units_m(G, wi, D, o.exactw)
print("min per number of units:", {u: mb[u] for u in sorted(mb)})

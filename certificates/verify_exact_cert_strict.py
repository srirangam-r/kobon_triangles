"""Same as work/eng/T27/verify_exact_cert.py (rebuild the DP graph with the same flags, round the weights to integers / D, run
the exact integer DP) but ALSO re-checks the second graph when --mstrict is given (paths through an M4 frame must have
final >= mstrict), as search/rule_lp_t25m.py main() does at the end of an lp run.
usage: [env PAIRLEM=1 TMX=1 ...] verify_exact_cert_strict.py w.pkl D lp <rule_lp_t25m flags...>"""
import sys, pickle, argparse
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1].as_posix()
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
G2 = None
if o.mstrict is not None:
    G2 = M.build_graph_m(o, cat=G.cat, mpath=True)
    target2 = float(2 + 2 * F(o.mstrict))
    Km = len(G.cat.keys); T.pad_K(G, Km); T.pad_K(G2, Km)
wi = np.zeros(G.K)
miss = []
for k, x in w.items():
    if k in G.cat.idx: wi[G.cat.idx[k]] = round(x * D)
    else: miss.append(k)
print("weights", len(w), "not in the rebuilt catalogue:", miss)
assert all(abs(x * D - round(x * D)) < 1e-6 for x in w.values())
v, kind, cnt = M.solve_exactw_m(G, wi, o.exactw, scale=D)
ok1 = v is not None and v >= target * D - 1e-9
print("exact DP min D*(2*final+2) =", v, " target * D =", target * D, " OK:", ok1)
mb = M.min_by_units_m(G, wi, D, o.exactw)
print("min per number of units:", {u: mb[u] for u in sorted(mb)})
ok2 = True
if G2 is not None:
    v2, _, _ = M.solve_exactw_m(G2, wi, o.exactw, scale=D)
    ok2 = v2 is not None and v2 >= target2 * D - 1e-9
    print("second graph (M-strict) exact DP min =", v2, " target2 * D =", target2 * D, " OK:", ok2)
print("ALL OK" if ok1 and ok2 else "FAILED")
sys.exit(0 if ok1 and ok2 else 1)

import sys, pickle
from fractions import Fraction as F
import numpy as np
exec(open(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + '/work/eng/A30/elim/audit_elim.py').read().split("# ---- bounds")[0])   # reuse loading
ex = pickle.load(open(ROOT + "/work/eng/A30/elim/extra_certs.pkl", "rb"))
w60 = pickle.load(open(ROOT + "/work/eng/A30/elim/w60.pkl", "rb"))
idx_a = {r: i for i, r in enumerate(Ga.win_repr)}
newc = []
for c, r in ex:
    D = c["D"]; wd = {k: F(x, D) for k, x in c["w"].items()}
    a = wd.get(("a",), F(0)); al = wd.get(("alpha",), F(0)); wr = wd.get(("wr",), F(0))
    assert all(v >= 0 for v in wd.values()) and a <= F(1, 3) and al <= 1 and wr + F(3, 2) * a <= F(3, 2)
    wcol = Ga.weights_vec(c["w"]); ov = Ga.window_values(wcol, D); wm = Ga.wmin_array(ov)
    mask = np.zeros(Ga.nwin, dtype=bool); mask[idx_a[r]] = True
    mn_all, mn_thru = Ga.path_min(wm, flag_mask=mask)
    print(c["name"], "D", D, "all-min", mn_all, "(2D =", 2 * D, ")  through-window min", mn_thru, " valid:", mn_all >= 2 * D, " strict:", mn_thru > 2 * D, " margin", F(mn_thru - 2 * D, 2 * D))
    newc.append(dict(name="A30_" + c["name"], D=D, w=c["w"]))
src = open(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + '/work/eng/A30/elim/audit_elim.py').read()
jointdef = src[src.index("from math import gcd"):src.index("w5, _, _ = joint")]
exec(jointdef)
w68, t68, tt68 = joint(Ga, certs + newc, "60 stored + 8 re-derived certs on a0 graph (no removal)")
print("  windows:", len(w68), " subset of state_2.allowed:", w68 <= a2_reprs, " equal:", w68 == a2_reprs, " |w68 - a2|=", len(w68 - a2_reprs), " |a2 - w68|=", len(a2_reprs - w68))
pickle.dump(dict(certs=certs + newc, windows=w68), open(ROOT + "/work/eng/A30/elim/certs68.pkl", "wb"))

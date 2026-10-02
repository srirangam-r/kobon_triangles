"""A30: in the UNRESTRICTED ILP5 model (no --flowers row), which (#centre, #corner, #X) triples are feasible?  (cross-checks the flower reduction)"""
import sys, math, itertools
from fractions import Fraction as F
exec(open(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + '/work/eng/A30/ilp/cpsat_ilp.py').read().split("t0 = time.time()")[0].replace("mode = sys.argv[1]", "mode = 'free'").replace("workers = int(sys.argv[2]) if len(sys.argv) > 2 else 1", "workers = 2"))
ycfg = m["ycfg"]
names = {c: f"{c[0]}/{''.join(map(str,c[1]))}" for c in ycfg}
print(names)
feas = []
def yv(cp, X, pred):
    return sum(X[var[("y", c)]] for c in ycfg if pred(c))
CENTRE, CORNER, XPTS = I5.CENTRE, I5.CORNER, I5.XPTS
for f in range(0, 5):
    for ncor in range(0, 14):
        for nx in range(0, 9):
            cp, X = build_cp()
            cp.Add(yv(cp, X, lambda c: c == CENTRE) == f)
            cp.Add(yv(cp, X, lambda c: c == CORNER) == ncor)
            cp.Add(yv(cp, X, lambda c: c in XPTS) == nx)
            s, st = solve(cp, tl=60)
            if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                feas.append((f, ncor, nx)); print("feasible (centre, corner, X) =", (f, ncor, nx), flush=True)
            elif st != cp_model.INFEASIBLE:
                print("UNKNOWN", (f, ncor, nx), s.StatusName(st), flush=True)
print("all feasible triples:", feas)

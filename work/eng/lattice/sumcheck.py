# Per-arrangement check of a certificate on real rows: every line final >= -eps0, and sum_L final <= 3*Lambda - 18
# (waste >= 0). final here is in identity units: rows hold final directly (2*final+2 reported in logs).
import sys, json, collections
sys.path.insert(0, "/home/nail/stuff/sundai_math/work/t3")
from arr import Arr
from fractions import Fraction as F
rows = json.load(open(sys.argv[1])); eps0 = float(F(sys.argv[2]))
by = collections.defaultdict(list)
for g, L, hasM, fin in rows: by[g].append((L, fin))
nfull = nbad_sum = nbad_line = 0; worst = []; minline = 1e9
for g, lst in by.items():
    a = Arr(g, 18); Lam = 288 - 3 * a.T(); lines = {L for L, _ in lst}
    s = sum(f for _, f in lst); minline = min(minline, min(f for _, f in lst))
    if any(f < -eps0 - 1e-9 for _, f in lst): nbad_line += 1
    if len(lines) == 18:
        nfull += 1
        if s > 3 * Lam - 18 + 1e-9: nbad_sum += 1; worst.append((s - (3 * Lam - 18), a.T(), g[:60]))
print(f"arrangements {len(by)}, with all 18 rows {nfull}; min line final {minline:.4f} (floor -{eps0}); "
      f"arrangements with a line below floor: {nbad_line}; arrangements with sum > 3Lambda-18: {nbad_sum}")
for w in sorted(worst, reverse=True)[:5]: print("   ", w)

"""Crude necessary conditions for a 94 with k=6, beta>=1 (C37): type profiles
(#X, #Xf, #V, #C, #O1, #O0) and bridge-end totals satisfying
  capacity   3#C + #V <= #O1 + 2#O0          (arms of bent/centroid need 0/1-block partners)
  D-count    B + beta >= 12                  (Z >= 0)
  master     beta >= 2#V + 2#Xf + 3#O1 + 6#O0 - 12   (Cred >= 0, sigma >= beta)
  e ranges   Xf {2,4}, V {1,2,4}, C 3, O1 1..5 (C35), O0 2..6 (C35), X 0."""
from itertools import product
surv = []
for nX, nXf, nV, nC, nO1, nO0 in product(range(7), repeat=6):
    if nX + nXf + nV + nC + nO1 + nO0 != 6: continue
    if 3 * nC + nV > nO1 + 2 * nO0: continue
    B = 2 * (nX + nXf + nV) + 3 * nC + nO1
    emin = 2 * nXf + 1 * nV + 3 * nC + 1 * nO1 + 2 * nO0
    emax = 4 * nXf + 4 * nV + 3 * nC + 5 * nO1 + 6 * nO0
    if emax < 2: continue
    need = max(12 - B, 2 * nV + 2 * nXf + 3 * nO1 + 6 * nO0 - 12, 1)
    if emax // 2 >= need:
        surv.append(((nX, nXf, nV, nC, nO1, nO0), B, need, emax // 2))
for s in surv: print(s)
print(len(surv), 'profiles (X, Xf, V, C, O1, O0), B, beta needed, beta max')

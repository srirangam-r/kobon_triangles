# A-stream claims (generator: t >= 7 triple points, no 4-fold point)

One line per claim. Status is always "proposed": this stream never referees its own claims.

| id | claim | file | status | test |
|----|-------|------|--------|------|
| A01 | Bridge-line lemma: every bridge joins two triple points consecutive on their line, so a line carries <= j_L - 1 bridges and beta <= sigma = 3t - m; bridges form a plane graph. For a 94 with t >= 7: B >= m + Z - 6, m + Z <= 2t + 6 + C, n_2 + 2n_3 >= m + Z - 6 - t | work/loop/claims/A01.md | proposed | work/t3/a_struct.py --selftest 200 (200 random exact arrangements + C07 bent fixture + repo arrangements, 0 failures) |
| A02 | Block-cap charging: the three first vertices of a block lie on its cap line, so a multiple one (in particular a bridge on an outer ray) puts the pair (P, cap) in x; at an axis point or centroid every bridge charges, only bent back rays and 1-block/0-block rays do not | work/loop/claims/A02.md | proposed | work/t3/a_struct.py --selftest 200 (259 positive instances, 0 failures) |
| A03 | Residue system for t >= 7 (R-a..R-h) plus an exact SAT encoding spec; at t = 7 it forces m + Z <= 20, B >= m + Z - 6 and, when m = 18, Z <= 2 with at least 5 - Z killed two-block points. Reduction only, not a closure; explicitly avoids C35 (t - 1 not closed) | work/loop/claims/A03.md | proposed | arithmetic derived by hand from the A01/A02/C34 system; identities checked by work/t3/a_struct.py |

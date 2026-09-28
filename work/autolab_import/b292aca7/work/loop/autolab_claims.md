# A-stream claims (generator: t >= 7 triple points, no 4-fold point)

One line per claim. Status is always "proposed": this stream never referees its own claims.

| id | claim | file | status | test |
|----|-------|------|--------|------|
| A01 | Bridge-line lemma: every bridge joins two triple points consecutive on their line, so a line carries <= j_L - 1 bridges and beta <= sigma = 3t - m; bridges form a plane graph. For a 94 with t >= 7: B >= m + Z - 6, m + Z <= 2t + 6 + C, n_2 + 2n_3 >= m + Z - 6 - t | work/loop/claims/A01.md | proposed | work/t3/a_struct.py --selftest 200 (200 random exact arrangements + C07 bent fixture + repo arrangements, 0 failures) |
| A02 | Block-cap charging: the three first vertices of a block lie on its cap line, so a multiple one (in particular a bridge on an outer ray) puts the pair (P, cap) in x; at an axis point or centroid every bridge charges, only bent back rays and 1-block/0-block rays do not | work/loop/claims/A02.md | proposed | work/t3/a_struct.py --selftest 200 (259 positive instances, 0 failures) |
| A03 | Round-2 corrected residue: threshold uses >=; low-degree one/blockless points remain allowed; no line-0-off-triples restriction; A05 replaces the preliminary encoding sketch | work/loop/claims/A03.md | proposed, revised per operator referee corrections | A04/A05 give the new windows and explicit limits |
| A04 | Interrupted cap gaps imply 3C<=2(sigma-beta) and m+Z+ceil(C/2)<=2t+6; proposes exclusion of t=7,m=18 and centroids at t=8,m=18; remaining high-m aggregate profiles explicit, lower-m cases open | work/loop/claims/A04.md | proposed | work/t3/a_gap.py --selftest 200; finite sigma=3 graph check and exact structural diagnostics |
| A05 | Canonical-segment SAT spec for the A04 residue: 116 high-m profiles, lower-m coverage formula, no unsupported splitting or symmetry assumptions; specification only, not implemented/solved | work/loop/claims/A05.md | proposed | work/t3/a_gap.py --profiles reproduces work/t3/a_gap_profiles.jsonl |

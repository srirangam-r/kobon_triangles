# K(10) = 25 for ALL arrangements (FC-M certificate at exact weight W = 9)

Same method and trust base as work/eng/k14all (RESULT.md, FACTS.md there). Only n = 10 is verified here; n = 22 and 26 were not run.

## Arithmetic (double-checked, all three n)
Lambda = n(n-2) - 3T, 3 Lambda - n >= -n/4 so Lambda >= n/4.
- n=10: 80 = 2 mod 3, Lambda in {2,5,..}, need >= 2.5 so Lambda >= 5, T <= 25 (record 25). Correct.
- n=22 (not run): 440 = 2 mod 3, need >= 5.5, Lambda >= 8, T <= 144. Correct.
- n=26 (not run): 624 = 0 mod 3, need >= 6.5, Lambda >= 9, T <= 205. Correct.

## Exact DP (verify_fcm_n.sh 9, log_verify_W9.log; 324 s graph build under load, ~1.2 GB RAM, 1 core)
graph 156156 nodes, 9220102 edges, K=451 columns, weights 15 not in catalogue: []
`exact DP min D*(2*final+2) = 24.0  target * D = 24.0  OK: True`
min per number of units: {2: 336, 3: 312, 4: 240, 5: 216, 6: 144, 7: 120, 8: 48, 9: 24}
(final >= -1/4 on every line.) Planted-decrement test not run at W = 9 (graph rebuild ~5 min); done at W = 13 in k14all.

## Patterns re-proved with K = 10 lines (regen_k.py 10 asserts restricted preds == stored preds; prove_k.sh 10 i)
All four: kissat UNSAT, drat-trim s VERIFIED (logs log_kissat_K10_pat*.log, log_dratcheck_K10_pat*.log; CNF sha256 in cnf_K10.sha256; regen log log_regen_K10.log).
Pattern 4 is the n-free hand fact. Minimal line counts of patterns are 5,6,5,7 <= 10, so the K=10 statements are non-vacuous (the realisability question is posed on 10 lines; more lines only weaken it).

## Perturbation lemma coverage (pert_cover.py, log_pert_cover_m7_25.log; pert.faces and pert2/faces_indep agree)
Needed at n = 10: m = 4, 5 exhaustive, m = 6 sampled cover (from the n=14 work, unchanged, not rerun here), 7 <= m <= 10 explicit simple lossless W_m: scores t_loc - #affected = 2, 0, 1, 3 for m = 7, 8, 9, 10 (all >= 0 = the criterion used by search_m.py/pert_indep.py; m = 8 has exactly 0, not >= 1). m = n = 10 pencil is T = 0.
Bonus: explicit W_m found for every m = 7..25 (scores >= 0), so the perturbation range needed for n = 22 and 26 (18 <= m <= 25) is also covered by explicit words (scores 18..44); those n were NOT otherwise run.

## Conclusion and caveats
Every arrangement of 10 pseudolines has T <= 25, so K(10) = 25 (known value is already 25; this is an independent bound for all arrangements). The M identities B = C, A = 3C/2 are proved in `proofs/additional/special_column_identities.md`. Caveats as n = 14/18: M-window soundness validated on n = 18 data only, hand proofs (K3, F4', perturbation, pair lemmas) and Python code not machine-checked; m = 6 sampled cover; no real-arrangement data check at n = 10; the multiplicity<=3 case relies on FC at W = 9 (from work/eng/othern, not rerun here).
Files: verify_fcm_n.sh regen_k.py prove_k.sh planted_fcm.py pert_cover.py cnf_K10/ (DRAT proofs deleted after checking).

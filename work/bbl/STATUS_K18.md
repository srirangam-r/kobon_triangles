# K(18): proof status (2026-10-01)

Question: does any arrangement of 18 lines (or pseudolines) in the plane have 94 bounded triangular faces? (T = 93
is attained.)

**Answer so far:** T ≤ 94 is proved for every arrangement. A 94 is excluded in every case except arrangements that
contain an *all-8 point*, a point where exactly 4 lines meet with all 8 angles triangles. No 94 has been found.

## What is proved, and where

| Claim | Method | Location | Exact certificate |
|---|---|---|---|
| T ≤ 94, multiplicity ≤ 3 | per-line LP certificate (FC), DP over a line automaton | THEORY §20 | work/eng/T25/rules_FC_full.json (D = 16) |
| T ≤ 93, multiplicity ≤ 3 | FD24, joint tightness, elimination, flower reduction (Gauss–Bonnet), ILP, 9-line tip lemma (DRAT) | THEORY §20–§23 | audited by A30 (all 5 items PASS) |
| 6-X-point case | independent cube SAT, 2,841/2,841 cubes DRAT-verified | THEORY §22 note | work/eng/T28/x6cert/summary.json |
| Only triple and *bad* 4-fold points in a (T, V)-maximal counterexample | perturbation lemma (exhaustive local re-drawings) | THEORY §24 | work/eng/pert/ (validated on 597 real points; independently re-derived, pert_indep.py) |
| (4-fold, triple) neighbours: only 48 of 2,080 patterns | pair optimality lemma | THEORY §25 | work/eng/pert2/pair_PQ_all.json (validated on 770 real pairs) |
| T ≤ 94 with 4-fold points | per-line LP, slack 1/4 (Σ final + waste is a multiple of 9) | THEORY §26 | work/eng/T27/cegar/w_FCM25.pkl (D = 16), CERT_FCM25.txt |
| No 94 with a 6-type bad point (11101110) | per-word credit certificate, margin 3 (9/8 without celldom) | THEORY §26 | work/eng/oth/w_mw6.pkl, w_mw6_nocdy.pkl (D = 16) |
| No 94 with a 7-type point (11111110) and no all-8 point | per-word credit, margin 7/10 (also without celldom) | THEORY §26 | work/eng/oth/w_mw7_no8x.pkl, w_mw7_no8x_nocd.pkl (D = 288) |
| No 94 without (triple, 4-fold) adjacency | strict certificate | THEORY §25 | work/eng/T27/cegar/w_TMXs.pkl (D = 48) |
| Gauss–Bonnet identity, touch lemma, star subcase | outside contribution (sol), checked by the lead | THEORY §27 | work/bbl/ALL8_GB_NOTE.md |
| U-UB lemma | proof checked | THEORY §26 notes | search/rule_lp_t25m.py --uub |
| Injective N-payment, pure-triple components cost ≥ 0, exact signed-kite identity (only −2K_1 negative), star subcase Λ ≥ 8, triple optimality | sol (ALL8_NOTE2), proofs checked by the lead | THEORY §27 | work/bbl/ALL8_NOTE2.md, note2_check.py |
| K_1 payment: 2Λ = sum of nonnegative credits (2R + N_*° + 2U_3 + I_3 + U_4 + ΣS_P° + 2K_3 + 4K_4) | lead, hand proof | THEORY §27 | work/bbl/k1_pay_check.py (3,445 arrangements, 0 failures) |
| Line-end lemma: every line end is good (≥ 1 disjoint credit) or a bad wedge / I_4 end | lead, hand proof (U_4 slip corrected by sol) | THEORY §27 | work/bbl/ends_check.py |
| No 3 consecutive 4-fold blocks; fresh tokens for U_4, I_4; exact end identity; bad-wedge graph is a forest at even n; Λ = π + U + ½ΣS_P° + K_3 + 2K_4 + ½Δ | sol (ALL8_NOTE3), proofs checked by the lead | THEORY §27 | work/bbl/ALL8_NOTE3.md, note3_check.py |

## The open case

Exclude a 94 containing an all-8 point. The class is: only triple points and bad 4-fold points, no 6-type point, and
the pair lemma.
- Sharpest form (sol, NOTE3 (9)): Λ = π + U + ½ΣS_P° + K_3 + 2K_4 + ½Δ, every term ≥ 0, with π = #components of the
  bad-wedge forest ≥ 1. Need Λ ≥ 7; a 94 needs π ≤ 6, i.e. at least 12 bad wedges.
- Previous form (after the K_1 payment): 2R + N_*° + 2U_3 + I_3 + U_4 + Σ_quad S_P° + 2K_3 + 4K_4 ≥ 14. Every term is
  ≥ 0; in a 94 the sum is exactly 12. Sent to sol as work/bbl/SOL_TASK3.md.
- Small-n SAT with an all-8 point in the class: minimum Λ = 9 at n = 9 and 8 at n = 10; Λ ≤ 6 UNSAT at n = 8–10.
  The surplus partly comes from line ends (R), so a proof must use the parity of n.
- Equivalent inequality (THEORY §27): Z + Σ_triples N/2 + 4A + 5J ≥ 7 + b/2. Every block must be paid for. Touch
  blocks are paid by Z; mutual blocks (kites, 3-fans) and end blocks are the unpaid ones.
- Evidence it holds: every real in-class arrangement with an all-8 point has Λ ≥ 66 (T ≤ 74), and real lines support
  a per-line margin ≥ 12. The per-line DP model reaches only −2.29, because of model looseness in lattice-plus-height
  patches.
- Partial results: Gauss–Bonnet reformulation; touch lemma (Z ≥ 1 when an all-8 point has exactly 3 triple
  neighbours); closed star subcase; U-UB lemma; hidden-state DP (sound, no effect on the optimum).

## Verification debts (before claiming a complete proof)
- DONE (2026-10-01): DRAT certificates (kissat + drat-trim, s VERIFIED) for T27's four CEGAR frame patterns
  (work/eng/oth/drat_pats/regen.py) and for the class-UNSAT all-8 core pattern (work/eng/oth/core4/r_cnf).
  The SAT encodings themselves (patsat_m, classsat) are validated, not formally verified.
- DONE (2026-10-01): independent re-derivation of the pair-lemma enumeration (faces by half-edge tracing,
  plain-Python exclusion check): identical 2,032 excluded / 48 allowed (work/eng/pert2/faces_indep.py, pair_indep.py).
- Hand proofs of the guarded facts at 4-fold apexes (validated on 543k real lines).
- An independent audit of the multiplicity ≥ 4 certificates (A30 covered multiplicity ≤ 3 only).

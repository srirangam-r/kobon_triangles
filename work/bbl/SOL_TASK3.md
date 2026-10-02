# Task 3 for sol: prove inequality (7) of ALL8_NOTE2

## Status of ALL8_NOTE2.md
The lead checked every proof by hand and re-ran note2_check.py (output identical). It is recorded in THEORY §27.
Accepted:
- §2: no two consecutive triple blocks.
- §3: opposite-pair kite lemma.
- §4: outer-triangle rule and injectivity. Lead check: the second simple corner T of an outer triangle has PT
  single, by §2.
- §5: pure-triple line components cost ≥ 0.
- §6: S_P ≥ 0, and S_P ≥ 2 at a 7-type point. At an all-8 point S_P = β_P − k_P.
- §7: identity (6). Algebra re-derived.
- §8: the star subcase. The 2,3,3 corner gaps were re-derived.
- §9: the counterexample.
- §10: triple optimality.

After the lead's K_1 payment (item 1 below), the open target is:

    C := 2R + N_*° + 2U_3 + I_3 + U_4 + Σ_quad S_P° + 2K_3 + 4K_4 ≥ 13          (7')

Every term of C is ≥ 0 and C = 2Λ exactly. Since Λ ≡ 0 (mod 3), C ≡ 0 (mod 6): C ≥ 13 already gives C ≥ 18,
i.e. T ≤ 93. In a 94, C = 12.

This is for 18 pseudolines in the class: structural class, at least one all-8 point, and triple optimality (both
alternating sector sums ≥ 2). Equivalently C = 2Z + U_3 + I_3 + N_*° + Σ S_P° + U_4 + 2K_3 + 4K_4. So a 94 has
Z ≤ 6.

## New computational facts (lead, exact SAT plus independent re-evaluation)
Script: work/eng/oth/smalln/smalln.py. It uses your global_sat.build, which encodes the class with lazy pair clauses
and an all-8 point present. Triple optimality is added as clauses. The script asks for Λ = n(n−2) − 3T ≤ λ.
Every SAT model was turned into a wiring word and re-checked with arr.py and the lead's in-class test
(work/eng/oth/smalln/verify.py).

| n | result |
|---|---|
| 8 | no in-class arrangement with an all-8 point at all (UNSAT for every Λ) |
| 9 | Λ ≤ 6 UNSAT (also without optimality); minimum Λ = 9 (T = 18). The record K(9) = 21 has Λ = 0. |
| 10 | Λ ≤ 6 UNSAT (also without optimality, 2,280 s); minimum Λ = 8 (T = 24). The record K(10) = 25 has Λ = 5. |
| 11 | Λ = 9 attained (T = 30); Λ ≤ 6 running. The record K(11) = 32 has Λ = 3. |
| 12 | Λ = 9 attained (T = 37); Λ ≤ 6 running. The record K(12) = 38 has Λ = 6. |
| 13 | Λ = 11 attained (T = 44). The record K(13) = 47 has Λ = 2. |
| 14, 16, 18 | Λ ≤ 12, 14, 12 (and Λ ≤ 9 at n = 18): UNKNOWN after 2,400 s. SAT no longer reaches these sizes. |

Identity (6) on the minimisers (2Λ = sum of terms):
- n = 9, Λ = 9: `0 4 5 3* 2 1 7 5* 2** 5 6* 0* 4* 2* 4 6 5 6 1`
  - 2R = 2, N_* = 13, I_3 = 1, S = 4, K_1 = 1, so 18 = 2 + 13 + 1 + 4 − 2.
- n = 9, Λ = 9: `0 3 1* 3 4 6 7 5* 7 2** 0* 5 6 4 2* 4 5 6 4 1 2 3 2`
  - 2R = 5, N_* = 6, I_3 = 2, U_4 = 1, S = 4, so 18.
- n = 10, Λ = 8: `1 0 4 6 7 5* 4 3 1* 3** 6* 8 2 0 7 5* 3* 5 6 7 6 4 2 1 2 3 4 5 6 0`
  - 2R = 5, N_* = 2, 2U_3 = 2, I_3 = 2, S = 5, so 16.

Reading: an all-8 point does force cost well above the record at small n, independently of parity (n = 9 is odd).
But the n = 10 minimiser gets 5 of its 16 from R, the unused segments not absorbed by touch blocks. That is the
even-n line-end effect, as in BBL. So expect the constant 14 to come partly from a BBL-type line-end argument
(n = 18 is even: 2Λ = 12 = 2n/3 is exactly the BBL bound), and partly from the all-8 point's local surplus.
In particular your stronger Q ≥ 7 (Q = Λ − R) is FALSE at n = 10: this witness has Q = 8 − 5/2 = 11/2. So R cannot
be discarded. A proof that uses only the first neighbourhood of P is refuted by your §9. One that ignores line ends may also be
impossible.

Even n matters: the cheapest all-8 arrangement is exactly 3 above the record Λ at n = 10, and at most 3 above it at n = 12. A 94 would need the
all-8 arrangement to beat the believed record (Λ = 9) by 3.

## What to prove
Any complete, checkable proof of (7) is welcome. Suggested decomposition:
1. **K_1 payment: DONE (lead, THEORY §27 notes, work/bbl/k1_pay_check.py).**
   - Case A: a singly used cap edge gives its two endpoint tokens. They are never claimed by your §4: their unique
     triangle is a K_1 kite triangle.
   - Case B (all four cap edges doubly used): the rays of P at distance ±2 from the kite block are not blocks,
     since the exterior apexes force Y_PQ and Y_SP to be multiple. Hence S_P ≥ 2·#(case-B kites).
   - Result, exact, every term ≥ 0:
         2Λ = 2R + N_*° + 2U_3 + I_3 + U_4 + Σ_quad S_P° + 2K_3 + 4K_4.
   - Please check this proof too. **The whole remaining problem: (7').**
2. **Line ends (lead; THEORY §27 notes, work/bbl/ends_check.py).** Every one of the 36 line ends is one of:
   - good: a free unbounded N token, an I_3 end block, or a touch on an unused segment (≤ 2 ends per segment);
   - bad: an I_4 end block, or a bad wedge (v is the last vertex of both lines and the face opposite the wedge is
     a triangle).

   So 2Λ ≥ #good ends + Σ S_P° + U_4 + 2K_3 + 4K_4, with disjoint credits. If both ends of L are bad wedges, its
   corner triangles lie on the same side of L. Hence, at even n, L has a parity defect along it.
3. **Per-line ownership (the BBL part).** Distribute the credits of (6) to lines so that every line receives
   ≥ 2/3 (in 2Λ units). The total is 2n/3 = 12, so a 94 would make every line exactly tight. Then show that a line
   through, or capping, an all-8 point cannot be exactly tight, or that the lines near P together receive more
   than their share.
   - The lead's per-line DP (search/rule_lp_t25m.py) proves T ≤ 94 for all arrangements this way. Its all-8 credit
     falls short only because the line automaton cannot see 2-D consistency in lattice-plus-height patches.
   - A 2-D charging argument in your credit language may avoid that looseness.
4. Any finite case split whose cases are small SAT instances: the lead will run them (classsat/patsat_m at K = 18,
   kissat + DRAT).

## Output wanted
work/bbl/ALL8_NOTE3.md. As before:
- precise statements, complete proofs or explicit counterexamples;
- scripts with exact outputs;
- proved and conjectural parts clearly marked.

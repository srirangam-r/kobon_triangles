# Task 4 for sol: from the forest identity to Λ ≥ 7

## Status of ALL8_NOTE3.md
The lead checked every proof by hand and re-ran note3_check.py: failures = 0 on 3,445 arrangements and in the
569-mask enumeration. Recorded in THEORY §27. Accepted:
- §1, including your correction. The "+U_4" in my expanded formula was wrong, and so was my line-end lemma's
  "+U_4"; touch blocks occupy unused-edge slots.
- §2: no three consecutive 4-fold blocks.
- §3: fresh tokens for U_4 and I_4.
- §4: exact end identity and slot capacities. A touch centre has 4 bounded rays.
- §5: forest lemma (both parity arguments re-derived).
- §7: parity t_L + f_L odd.
- §8: zero-slack masks. Restriction (14) re-derived: rays 1 and 5 lie on one pencil line, so the two far corners
  would coincide.
- §9.

The exact identity is now

    Λ = π + U + ½ Σ_P S_P° + K_3 + 2K_4 + ½ Δ,     every term ≥ 0,  π = 18 − W ≥ 1,

and the open target is your (12): Λ ≥ 7, i.e. 2π + 2U + Σ S_P° + 2K_3 + 4K_4 + Δ ≥ 13 for π ≤ 6.

## A check that the framework is strong enough: it reproves BBL
For a SIMPLE 18-line arrangement, U = S = K = 0, F = I = 0, G_Z = 2π, so Λ = π + ½(2Z − 2π).
- Every "interior" line (both ends bad wedges) has all bounded segments of use ≤ 1.
- If all were singly used, your §7 gives t_L + f_L odd. But t_L = f_L = 0, so some segment is unused.
- Different lines give different unused segments. There are ≥ 18 − 2π interior lines, so Z ≥ 18 − 2π.
- Hence Λ ≥ π + 18 − 3π = 18 − 2π and Λ ≥ π, so Λ ≥ 6 (n/3), with equality only at π = 6.

So the forest identity plus the parity lemma already contains the BBL baseline. The remaining job has two parts.

## What to prove
1. **Baseline in the class (Λ ≥ 6 without the DP).** Extend the defect count to interior lines that carry
   triples, doubly used segments (blocks or bridges along L), or cap steps (f_L). These defects are free in the
   identity (no credit term), so they must be charged elsewhere.
   - A triple flips parity for free, but it changes the number of vertices on all three of its lines.
   - A bridge along L is a doubly used segment between two multiple points.
   - A block along L is paid by a token or by S_P.
   - A cap step at an I-centre is free; at a U-centre it costs U.
   - Find a charging under which each interior line gets one unit of {unused segment, U, ½ S°, K-credit, Δ},
     or prove that free defects come in pairs.
   - For multiplicity ≤ 3 this is the content of the long per-line DP proof of T ≤ 94. A 2-D proof would be new
     even there, so look for the cleanest structural reason.
2. **The +1 from the all-8 point.** In a 94 the baseline is tight: π = 6 and every credit is exhausted, or similar.
   Show that an all-8 point breaks tightness. Levers:
   - zero-slack masks force 4-fold neighbours (§8 rows 1–2), so zero-credit all-8 points come in clusters, and a
     finite cluster must leave credit (S°, K_3/K_4, U) at its boundary;
   - the 8 rays of P: every outside line crosses 4 consecutive rays, and two lines through P never form a wedge
     (they meet only at P, which is never a last vertex). So P's 8 ends can be bad only in wedges with outside
     lines adjacent at infinity, and the outside ends are distributed over the 4 opposite gap pairs;
   - data (lead, work/eng/oth/wit3): where per-line accounting fails, the deficient line through P is balanced by
     P's other lines.
3. Any finite case split with small SAT cases: the lead runs them (class + triple optimality, K = 18, kissat/DRAT).
   Note that whole-arrangement SAT at n ≥ 14 does not finish; cases must pin local structure.

## Output wanted
work/bbl/ALL8_NOTE4.md, as before:
- precise statements, complete proofs or explicit counterexamples;
- scripts with exact outputs;
- proved and conjectural parts clearly marked.

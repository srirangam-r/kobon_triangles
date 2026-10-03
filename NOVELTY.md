# Contribution and novelty

## The problem and what was known

K(n) is the largest number of bounded triangular faces in an arrangement of n lines (the Kobon triangle problem).
At n = 18, before this work:
- **Lower bound 93.** Many arrangements are known; the Utkin–Parpalak gallery holds about 3,000.
- **Simple arrangements** (no three lines concurrent): 93 is optimal (Blanc, arXiv:0801.2845). The value 94 found
  in tables (OEIS A006066 and elsewhere) comes from the earlier simple-arrangement bound of Bartholdi–Blanc–Loisel
  (arXiv:0706.0723).
- **Arbitrary arrangements:** every known even-n record uses triple points, and here we know only Tamura's 96 and an
  unpublished 95 (Clément–Bader). So K(18) ∈ {93, 94, 95, 96}.

## What is new here

1. **New upper bound: K(18) ≤ 94 for all arrangements.** This holds for lines and pseudolines, with points of any
   multiplicity. It is the first bound below 95 that allows multiple points (computer-assisted; paper Thm 1).
2. **New theorem: T ≤ 93 for multiplicity ≤ 3.** This extends Blanc's optimality of 93 from simple arrangements to
   arrangements with triple points (paper Thm 2).
3. **New exact value K(14) = 54, for all arrangements.**
   - Previously only the simple case was proved, and there Blanc's bound is 53; the 54-triangle record uses triple
     points.
   - Our multiplicity ≥ 4 certificate also verifies at n = 14, and there the slack suffices.
4. **The Bartholdi–Blanc–Loisel bound for triple points.** T ≤ ⌊n(n − 7/3)/3⌋ for every even n from 6 to 40, for
   multiplicity ≤ 3; that bound was previously proved for simple arrangements only.
   - It is exact at n = 6, 8, 10, 12, 14, 16, 20, so K(16) = 72 and K(20) = 117 hold for multiplicity ≤ 3.
   - These values appear in OEIS as exact, but the published proofs cover only simple arrangements.
5. **Structure of a hypothetical 94.** Vertex-maximal: only triple points and three "bad" fourfold types. No 11101110
   point, and necessarily an all-8 point. Local pair and triple constraints (paper Thm 3).
6. **A reduction of K(18) = 93 to one inequality in nonnegative local credits** in the all-8 case (paper §6). The
   bad-wedge forest lemma gives a short new proof of the simple-arrangement baseline Λ ≥ n/3.
7. **Method.** The Bartholdi–Blanc–Loisel charging argument is made into an exact, machine-checkable form for
   non-simple arrangements:
   - an exact budget identity;
   - transfer rules with LP weights;
   - an exact DP over a finite automaton of all possible line views, with SAT-certified local facts in a
     cutting-plane loop;
   - rational certificates.

   Local optimality lemmas come from exhaustive enumeration of local redrawings.

## What is not new

- **The 93 constructions.** Our 93 (no multiple points) is a new arrangement, found by our own unseeded search. But
  93 is the known record value, so this is a reproduction of the record, not a new bound. The second 93 is taken from
  the published gallery.
- The n = 15 value 65 is a known optimum.

## Why it matters

- K(18) was the smallest open case with this kind of gap: 93 attained against 96/95 for general arrangements.
- Result 1 narrows it to 93 or 94. The structural results say exactly what a 94 would have to look like.
- The certificate method applies to other n.

## Dates

All results were completed between 2026-09-27 and 2026-10-02. No competition cutoff was specified to us, so each item
is date-stamped for the judges.

| Date | Result |
|---|---|
| 2026-09-27 | 93-triangle arrangement found by unseeded search; official evaluator score 93 |
| 2026-09-30 | certificate FC: T ≤ 94 for multiplicity ≤ 3 |
| 2026-09-30 | T ≤ 93 for multiplicity ≤ 3 (with DRAT proofs; independent audit passed) |
| 2026-09-30 | perturbation lemma and pair lemma |
| 2026-09-30 | certificate FC-M: **T ≤ 94 for all arrangements** |
| 2026-10-01 | 11101110 points excluded; 11111110 points excluded without an all-8 point |
| 2026-10-01 | credit identity in the all-8 case (payments, K₁ lemma) |
| 2026-10-02 | bad-wedge forest identity Λ = π + U + ½ΣS° + K₃ + 2K₄ + ½Δ |
| 2026-10-02 | BBL bound for multiplicity ≤ 3 at every even n ≤ 40 (exact at 6–16, 20) |
| 2026-10-02 | K(14) = 54 for all arrangements |

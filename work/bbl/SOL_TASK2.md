# Task for sol: close the all-8 case of K(18) ≤ 93

Context: work/bbl/ALL8_BRIEF.md (the problem and the notation) and your own work/bbl/ALL8_GB_NOTE.md. The lead has
checked your note; it is recorded in THEORY.md §27. Everything below is established unless marked open.

## The class (properties of a hypothetical lexicographically (T, V)-maximal 94)
- n = 18 pseudolines, every pair crossing once, T = 94, so Λ = 288 − 3T = 6.
- Only simple points, triple points and "bad" 4-fold points:
  - all-8: all 8 sectors triangles;
  - 7-type: sector word 11111110.
  - No 6-type point (excluded by an exact certificate).
- At least one all-8 point. (With no all-8 point, a 7-type point is already excluded by a certificate; with no
  4-fold point at all, the multiplicity ≤ 3 theorem applies.)
- Pair lemma: if a 4-fold point P and a triple point Q are consecutive on a line, the canonical pair
  (P word, Q word) is one of 48 allowed patterns (work/eng/pert2/pair_PQ_all.json). For P all-8 the allowed Q
  words, listed from the sector right after the ray Q→P, are 100111, 101101, 101111, 110011, 110111 and 111111.
- Optimality: no local re-drawing of any small disk has ΔT > 0, or ΔT = 0 with more vertices.
- U-UB lemma (proved, THEORY §26 notes): let P be a triple point of line L with a block along A to a simple X, where X
  is the last vertex of A. Then any line W that meets L at v ≠ P and has no vertex on the far side of L from X is the
  block's cap line, and v is P's neighbour.

## Exact identities
- Λ = Z + Σ_P c_P, with:
  - c = (N − D)/2 at triple points;
  - c = 4 + N/2 − D/2 at 4-fold points: 4 − D/2 for all-8, and 5 − D/2 for 7-type, where β ≥ 2 so D ≤ 4.
- Equivalently Λ = Z + Σ_triples N/2 + 4A + 5J − b/2. Here b = Σ D = total blocks, A = #all-8 points, J = #7-type
  points.
- Every block has exactly one simple endpoint X. Classify blocks P → X by Lemma A:
  - **touch block:** both faces beyond X along the block's line are non-triangles, and the segment u beyond X is
    bounded. Then u is unused, and each unused segment absorbs ≤ 2 touch blocks, so Z ≥ (#touch)/2.
  - **end block:** the block's line has no vertex beyond X (u is unbounded).
  - **mutual block:** some face beyond X is a triangle. Then X has ≥ 3 triangles: X is a kite centre (4 triangles,
    4 mutual blocks) or a 3-fan (3 triangles, 2 mutual blocks).
- So b = 4K + s2 + 2s3, with K = #kite centres. Your Gauss–Bonnet identity is Λ = Z − 6χ + 2A + J + B.

## OPEN: prove the inequality
    Λ ≥ 7, i.e.   Z + Σ_triples N/2 + 4A + 5J ≥ 7 + b/2,
for every arrangement in the class above (n = 18, A ≥ 1). Λ is a multiple of 3, so this gives Λ ≥ 9, T ≤ 93.
Equivalently: (#mutual blocks + #end blocks)/2 ≤ (Z − #touch/2) + Σ_triples N/2 + 4A + 5J − 7.

## What is known to be true or false (so you do not chase dead ends)
- True in all data: every in-class arrangement with an all-8 point has Λ ≥ 66.
- FALSE: "a bridge component containing an all-8 point costs > 6". Your 18-line witness costs exactly 6 (with
  Z ≥ 1).
- Not known: whether every bridge component has cost ≥ 0. Do not assume it.
- Local re-drawings cannot remove perfect patches. In the triangular lattice with height lines, every local move loses
  triangles.
- Per-line accounting fails here: the lattice patch interior balances to about 0, and the slack sits at the patch
  boundary.

## Useful directions
1. Generalise your touch lemma:
   - an all-8 point with β ≥ 4 multiple first vertices;
   - multiple first vertices that are 4-fold (all-8 or 7-type);
   - mixed cases.
   Aim for "every all-8 point owns ≥ x units of Z or N-charge that no other all-8 point claims".
2. Bound mutual blocks. A kite centre's 4 corners each give a block toward it. A kite with an all-8 corner is paid by
   that corner's budget, with 4 per all-8 point in hand. Kites with only triple corners also exist in multiplicity
   ≤ 3 arrangements, so any argument must work there as well. There, T ≤ 93 is known only through the per-line
   machinery. A purely 2-D proof must not contradict the existence of 93s.
3. Combine with your Gauss–Bonnet form: the −6χ term must be paid by boundary charge B. Isolated simple triangles
   cancel exactly (+6 in B, +1 in χ).
4. Any finite case split is welcome if each case is closed by a checkable argument or a small SAT instance.
   - Example: an all-8 point plus its first-vertex octagon plus the caps, at K = 18, with the class constraints.
   - work/eng/T27/classsat.py builds such instances.

## Output wanted
Write work/bbl/ALL8_NOTE2.md:
- precise statements and complete proofs, or an explicit counterexample to any step;
- any computation with a script and its exact output.
Mark clearly which parts are proved and which are conjectural. The lead will check every step before it enters
THEORY.md.

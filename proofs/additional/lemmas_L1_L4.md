# Claim: 18 lines with at most two triple points have at most 93 triangles

**Setting.** An arrangement A of 18 lines (or pseudolines) in the affine plane. Every point
where lines meet has exactly 2 or 3 lines through it. There are at most two triple points,
and no three lines are mutually parallel. T is the number of bounded triangular faces.

**Claim.** T ≤ 93.

The case of no triple point is Blanc's theorem (arXiv 0801.2845, Cor. 2.0.5). The case of
one triple point is the extension written in SUMMARY.md. This note covers **exactly two
triple points P, Q**; the same framework also re-proves the one-triple-point case.

## 0. Reductions and counting

- **Parallels.** A projective map sending a generic far-away line to infinity keeps every
  bounded triangular face bounded and triangular (T can only grow). It turns each pair of
  parallel lines into an ordinary crossing and creates no new multiple point, because no
  three lines are mutually parallel. So assume no parallels.
- **Segments.** A line through k' distinct points has k' − 1 bounded segments. With two
  triple points, S = 282 bounded segments in total:
  - Case A (no line through both): 6·15 + 12·16.
  - Case B (one line m through both): 14 + 4·15 + 13·16.
- **Counting identity.** Each triangle side is a bounded segment, and a segment is a side of
  at most 2 triangles (one on each side). So 3T = S − Z + D, where Z counts segments used by
  no triangle and D counts segments used by two. Hence **T ≥ 94 ⟺ Z ≤ D**.

## 1. Local lemmas

**L1. Doubly used segments.** If a segment is a side of two triangles, one of its endpoints
is a multiple point.
- Say the segment is [X, Y] with X and Y simple, lying on line M.
- At a simple point only M and one other line meet. Both triangles have their side at X on
  that other line, one above M and one below, so they lie on the two sides of one line
  through X; the same holds at Y.
- Then the triangle above M has its sides at X and Y on the lines L_X and L_Y, and so does
  the one below. Two lines meet only once, but the two apexes lie on opposite sides of M.
  Contradiction.

**L2. Cap blocks.** Let P be a triple point with 6 rays in circular order.
- A doubly used segment with endpoint P is the first segment of some ray ρ at P. The two
  triangles on it lie in the sectors (ρ−, ρ) and (ρ, ρ+).
- If its far endpoint X is simple, both triangles have their third side on the unique other
  line C through X. So C meets ρ−, ρ and ρ+ at their first vertices; call C a *cap line*
  and {ρ−, ρ, ρ+} a *cap block*.
- A line avoiding P meets exactly 3 consecutive rays of P, so two blocks with the same cap
  line coincide, and distinct blocks are disjoint. Hence **at most 2 blocks at P**.
- **Caveat (added):** disjointness uses that each ray's first vertex is a *simple* crossing,
  which has a unique "first crossing line". This holds for every ray at P unless the ray's
  first vertex is the other triple point Q, which can only happen in case B, on the ray of
  m toward Q.
  - In case B, two blocks at P may overlap on that ray, with cap lines q1 and q2 through
    Q. P then has no axis.
  - Both of those blocks have cap lines through a triple point, so they count in x (§3).
    The missing axis is charged to one of them, keeping "#missing or invalid axes ≤ x".
  - The bound "at most 2 blocks with simple-ended middle rays at P" still holds, because a
    third block would need a first-crossing line already used on its rays.
- If there are 2 blocks (and, in case B, they do not overlap), they cover all 6 rays, and
  their middle rays are opposite rays of
  one line through P, the **axis** of P. The 4 cap triangles use the first segment of every
  ray at P.

**L3. Blanc's claims for clean lines.** Call a line L *clean* if it avoids every triple
point and is a cap line of no block.
- Every clean line *claims* a bounded unused segment s of some other line M, where one
  endpoint of s is L ∩ M (Blanc, Prop. 2.0.4). The proof, from Blanc and restated in §2,
  uses only that L's crossings are simple, that L has 17 crossings (so 16 bounded segments,
  an even number), and that no piece adjacent to L is doubly used. The last point holds by
  L1–L2, since otherwise L would be a cap line.
- A claim happens at a simple endpoint X of s and is made by the unique line through X
  other than M. So **each unused segment with two simple endpoints is claimed at most
  twice**.

## 2. Blanc's argument in t-sequence form (used for L3 and L4)

Let L have simple crossings X_1, ..., X_r in order, with lines R_1, ..., R_r, and bounded
segments l_1, ..., l_{r−1}. Add virtual entries t_0 and t_r for the two rays.

1. Set t_j = +, − or 0 according to whether the face above l_j is a triangle, the face below
   is, or neither. By L1 it is never both on a segment with simple endpoints.
2. The piece r_i^s of R_i from X_i to the next vertex on side s is used iff t_{i−1} = s or
   t_i = s. The only faces it borders are the two faces on side s of L next to X_i.
3. **(d) No "s, s".** Two triangles on the same side over consecutive segments would share
   r_i^s. By L1 its far endpoint is a triple point, which makes L a cap line there.
4. **Claims at a crossing X_i.** Pattern (s, −s) gives none. Patterns (s, 0) and (0, s) give
   a claim iff R_i has a crossing on side −s. Pattern (0, 0) always gives one: both pieces
   are unused, and at least one is bounded.
5. **One-sided lines share a side.** If R_i has all its other crossings on side s and R_j
   has all of its on side −s, then R_i ∩ R_j would have to be on both sides. (R_i ∩ R_j is
   not on L, because L's crossings are simple.)
6. **Stretch lemma.** Take a stretch of entries between two zeros, with m entries in between.
   If there are no claims inside it, then:
   - zeros are isolated,
   - each run of nonzeros alternates in sign (by (d)),
   - every run end next to a zero has the common one-sided sign σ (by 4 and 5),
   so every run has odd length. Then m = Σ(odd lengths) + (runs − 1), which is odd.
   **So a stretch with m even contains a claim**, including m = 0, which is pattern (0, 0).
7. **Clean line.** Here r = 17, so the whole line is one stretch with m = 16 (even), and it
   contains a claim. That is L3.

**L4. Axis lemma.** Let P have 2 cap blocks with axis a. Assume a passes through no other
triple point and is not a cap line of any block at the other triple point.
- a has 16 distinct points, P = X_p, with 2 ≤ p ≤ 15 (both rays of a at P carry doubly used
  segments, so P is interior). The segments l_{p−1} and l_p at P are doubly used ("both").
- **t_{p−2} = 0 (or it is the ray).** A triangle on side s over l_{p−2} would share the
  s-piece of the cap line R_{p−1} with the cap triangle on side s. That piece ends at the
  apex V of the cap triangle, which lies on a line through P other than a.
  - V ≠ P, so by L1 V must be the other triple point Q, and the shared piece would be a
    doubly used segment at Q.
  - Its cap line would be a. That is excluded by the hypothesis, or in case A by the fact
    that Q lies on no line through P.
  - Similarly t_{p+1} = 0.
- The remaining segments of a split into two stretches bounded by zeros, of m-values p − 3
  and 14 − p (for p = 2 or 15, one stretch has m = 12). These sum to 11, so one is even.
- Rule (d) holds on these stretches: a violation would need three lines through Q crossing
  a consecutively at simple points, which would make a a cap line of Q.
- By the stretch lemma, **a claims an unused segment at a simple crossing**.

## 3. The two cases (T ≥ 94, so Z ≤ D)

In both cases, if a triple point has 2 blocks, all 6 of its segments are used (L2). So when
both points have 2 blocks, every unused segment has two simple endpoints, and the claims
number at most 2Z.

Let c' be the number of distinct cap lines that pass through neither triple point, and let
x be the number of blocks whose cap line passes through a triple point. Then c' ≤ #blocks − x.

**Case A: no line contains both P and Q.**
- D = number of blocks ≤ 4, and 18 − 6 = 12 lines avoid P and Q, so clean = 12 − c'.
- If D ≤ 3: claims ≥ clean ≥ 9, so Z ≥ 5 > D. Contradiction.
- So D = 4, and both points have 2 blocks and an axis.
- The axis of P fails L4's hypotheses only if it is a cap line of a block at Q, which makes
  that block's cap line a triple line. The same holds for Q.
- So claims ≥ (12 − (4 − x)) + (2 − invalid axes) ≥ 10, since x ≥ number of invalid axes.
  Then Z ≥ 5 > 4 ≥ D. Contradiction.

**Case B: a line m contains both P and Q.**
- If P and Q are not consecutive on m, then D = blocks ≤ 4 and clean = 13 − c' ≥ 9, so
  Z ≥ 5 > D. Contradiction.
- Otherwise D ≤ blocks + 1, where the +1 is segment PQ. A counting pass without axes gives
  ⌈(13 − blocks)/2⌉ ≤ blocks + 1, which forces 4 blocks.
- m is not an axis: the first segment of m's ray toward Q ends at Q, not at a simple point.
- If P's two blocks overlap on the ray toward Q (L2 caveat), P has no axis. Both of P's
  blocks then have cap lines q1 and q2 through Q, so they add 2 to x. The inequality below
  counts P's missing axis against one of them. A different block of P serves any
  (ii)-invalid axis of Q whose cap line is q1 or q2.
- The axis of P, say p1, fails L4 only if p1 is a cap line of a block at Q. The shared-piece
  mechanism in L4 also produces exactly this. Symmetrically for Q, and the corresponding
  blocks are distinct.
- So claims ≥ (13 − (4 − x)) + (2 − invalid) ≥ 11. Then Z ≥ 6 > 5 ≥ D. Contradiction.

**Hence T ≤ 93** for 18 lines with at most two triple points (with the stated conditions).


## Referee's simpler argument for case B (recommended; verified)

Take P and Q consecutive on m, with 4 blocks.
- **P has a block whose cap line passes through Q.**
  - If P's blocks are disjoint, they cover all 6 rays. The ray toward Q is then in a block,
    and it cannot be the middle ray, since its first vertex is Q, not a simple point. So it
    is an end ray, and that block's cap line meets it first, at Q.
  - If P's blocks overlap on that ray, both cap lines pass through Q.
- Symmetrically, Q has a block whose cap line passes through P.
- So x ≥ 2, c' ≤ 2, clean = 13 − c' ≥ 11, and Z ≥ ⌈11/2⌉ = 6 > 5 ≥ D. This contradicts
  Z ≤ D.

No axis lemma is needed. §3's remark "all 6 segments at a triple point are used" is false in
the overlap sub-case, but the proof only needs claims ≤ 2Z, which holds unconditionally:
every claim sits at a simple endpoint, and that endpoint determines the claimer.

**Referee verdict (independent subagent, 2026-09-27): correct.** 142,160 arrangements were
tested exactly with no counterexample to any lemma. Details are in work/referee/.

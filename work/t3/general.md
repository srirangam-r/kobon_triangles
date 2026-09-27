# Credit framework for any number of multiple points

Setting: n lines or pseudolines, **n even**, no three mutually parallel (parallels removed
projectively). Multiple points P have multiplicity k_P. S, Z, D, Λ are as in `proof_general.md`.

## 1. Master inequality (proven)

Notation:
- σ = Σ over lines L with j_L ≥ 2 multiple points of (j_L − 1).
- β = number of doubly used segments joining two multiple points (*bridges*).
- D_P = number of doubly used first segments at P with a simple far end.
- caps_P = number of distinct cap lines of P.
- x = number of pairs (P, cap line C of P) where C passes through another multiple point.
- κ(L) = number of pairs (u, X) where u is an unused segment, X is a simple endpoint of u,
  and L is the other line through X.
- Z_tr = number of multiple endpoints of unused segments.

Then 2Z = Σ_L κ(L) + Z_tr.

- Clean lines have κ ≥ 1 (L3).
- There are n − (Σk_P − σ) lines avoiding all multiple points, and at most Σcaps_P − x of
  them are cap lines.

So, with h_P := 2k_P(k_P−2) − 2D_P − k_P − caps_P,

  **2Λ ≥ n + Φ, where Φ = σ + x − 2β + Σ_P h_P + Cred.**

Here Cred counts touches by non-clean lines, plus Z_tr. Since Λ is an integer,
**Λ ≥ ⌈(n+Φ)/2⌉**. At n = 18, **T ≤ 93 whenever Φ ≥ −5**.

## 2. Lemmas

**Lemma A (cap touch), any multiplicity (proven).**
- Setting: [P, X] is a doubly used first segment of the ray ρ ⊂ ℓ, X is simple, and C is
  the cap line through X. V_± are the neighbours of X on C (the first vertices of ρ±).
  u is the segment of ℓ beyond X.
- If the face beyond X on side s is a triangle, it shares the edge [X, V_s] with the cap
  triangle. So [X, V_s] is doubly used, V_s is a multiple point Q (by L1), and [Q, X] is a
  doubly used first segment at Q whose cap line is ℓ. Call this a *mutual pair*.
- Otherwise u is unused, if it is bounded, and C touches it at X. C is a cap line, so it is
  never clean.
- For a line with both rays doubly used at P (an axis), at least one of its two
  u-segments is bounded.
- Distinct cap points give distinct touches.
- If P is *killed* (no Lemma-A touch), then some cap line of P passes through a multiple
  point, so x_P ≥ 1.

**Lemma B (bridges at triple points; proven).**
- Two disjoint blocks at P: then a bridge [P, Q] is doubly used only if PQR is a
  triangular face whose three vertices are all multiple points.
- *Bent pair* (two blocks sharing the ray P→Q): both cap lines pass through Q, so x_P = 2,
  and [P, Q] is doubly used.

**L4 (proven, as in `proof_k2`).** Suppose the axis a_P passes through no other multiple
point and caps no block. Then a_P claims. If a_P caps a block of Q, the pair (Q, a_P) is in
x, and distinct axes give distinct pairs.

**Shared axis (proven).** Suppose j type-X triple points all have the same axis m, and m caps
nothing. Then:
- m has n−1−j vertices;
- the stretches between the forced zeros satisfy Σ(m_i + 1) = n − 1 − 4j, which is odd, so
  m claims;
- each of the j − 1 gaps gives 2 Lemma-A touches.

## 3. Per-point values

| Point | h_P | + local credit | worst φ_P |
|---|---|---|---|
| triple, 2 disjoint blocks, unkilled | −3 | Lemma A +1, and L4 or an x-pair +1 (general position) | **−1** (general position); −2 in general |
| triple, killed | −3 | x_P ≥ 1 | −2 |
| triple, bent | −3 | x_P = 2 | −1, and it owns one bridge |
| triple, 1 block | 0 | | 0 |
| triple, 0 blocks | 3 | | 3 |
| 4-fold (2 caps, D_P ≤ 4) | ≥ 2 | Lemma A: 2 more touches in general position | **≥ 2** |
| 4-fold, spans sharing multiple first vertices (D_P ≤ 5, 3 caps) | ≥ −1 | x_P ≥ 3 | ≥ 2 |
| k ≥ 5 | ≥ 2k² − 9k + 6 ≥ 11 | | ≥ 11 |

For 4-fold points, h ≥ 2 comes from D_P ≤ min(2k − 2·caps, caps·(k−2)) with k = 4:
- 1 cap gives h ≥ 7;
- 2 caps give h ≥ 2;
- 3 caps give h ≥ 5;
- 4 caps give h ≥ 8.

So **points of multiplicity ≥ 4 always contribute positively**: each raises Φ by at least 2.
In mixtures they only help, provided their bridges are paid for (see gaps).

## 4. Theorem H: general position (proven)

**Statement.** Suppose no line passes through two multiple points. Then β = σ = 0 and no
point is killed (every apex is simple). With t triple points and q points of higher
multiplicity,

  **Λ ≥ ⌈(n − t + 2q)/2⌉,** i.e. T ≤ ⌊(n(n−2) − ⌈(n−t)/2⌉)/3⌋.

This improves Theorem G's bound n/2 − t.

**At n = 18 (every t).**
- t ≤ 5: Λ ≥ 7, so T ≤ 93.
- t = 6: Λ ≥ 6. A 94 would force Λ = 6 and D = 12, hence Z = 0. But every one of the 6
  points has an axis, and Lemma A then gives Z ≥ 1. Contradiction.
- t ≥ 7: 3T ≤ S + D ≤ 288 − t < 282.
- 4-fold points only reduce S + D further, since each costs 8 in S and adds at most 4 to D.

**So an arrangement of 18 lines whose multiple points are in general position has T ≤ 93.**

## 5. Shared lines, k ≥ 4

Here Φ ≥ −2·(#killed or shared-axis points) − (#other axis points) + σ + extra credits
+ 2q − (bridges not paid). Each doubly used bridge must be paid by one of:
- bent endpoints (x);
- endpoints with ≤ 1 block;
- a triangular face with all three vertices multiple (Lemma B).

**What closes at n = 18:**
- k ≤ 3: all configurations (`report`/`notes.md`).
- k = 4: all-type-X configurations with σ ≥ 3, or with an isolated point, or with a
  shared axis carrying both of its points.
- Any k: all points collinear on one common axis.

**Residual family (not closed).** Configurations of 4–6 triple points in which one of the
following happens:
- (R1) some axis point is *killed* by mutual pairs (its cap lines pass through other triple
  points, and its axis caps their blocks back);
- (R2) an axis contains another triple point for which that line is not an axis, so neither
  L4 nor the shared-axis parity applies;
- (R3) there is a triangular face all of whose vertices are multiple points (the Lemma B
  exception), or a bridge at a 4-fold point.

In R1–R3 the counting needs σ + (extra credits) ≥ 2t − 5 and is not automatic.

## 6. The stalled k = 4 configuration (characterized exactly)

**Configuration.**
- m ∋ P1, P2 consecutive; m′ ∋ P3, P4 consecutive; no other sharing, so σ = 2.
- Every point is type X with a private axis b_i.
- Mutual pairs: (P1's block capped by b2, P2's block capped by b1), meeting at
  X12 = b1 ∩ b2; likewise X34 for P3 and P4.
- Each P_i is the 2nd vertex of b_i, so the other side is unbounded and A(P_i) = 0.
- x = 4, the 4 other caps are distinct non-triple lines, β = 0 (Lemma B), D = 8.

**Counts.**
- There are 18 − 10 = 8 non-triple lines, 4 of them caps, so clean = 4.
- 94 needs Z ≤ D + 6 − 3k = 2. The clean lines force 2Z ≥ 4, so Z ≥ 2 and Λ = Z + 4 ≥ 6.
- **So this configuration is NOT closed** (it is one short).

**Exact tight structure (a candidate for an exhaustive SAT run, `kobon_sat.py --defect`).**
- Z = 2, and both unused segments have two simple endpoints (Z_tr = 0).
- The 4 clean lines each make exactly one claim, and each unused segment is claimed from
  both ends.
- Every other line (the axes b_i, the shared lines m and m′, the second private lines c_i,
  and the 4 caps) touches no unused segment.
- The 4 non-triple caps each cap exactly one block.
- The coordinator's parity rule does not apply directly to the b_i, because their
  t-sequences contain "both" entries at P_i.

No missing credit was found.

## 7. Evidence

- `lemmas.py` on gallery arrangements (n = 10–22, 5,516 arrangements): no failures.
- `walk.py` (flip/collapse/expand walks): about 1,000 arrangements with k = 3, Cred ≥ need
  in all.
- `gp_test.py`: Theorem H on 16,208 general-position arrangements (gallery plus mutations,
  t ≤ 5): no failures.
- 4-fold points were **not** exercised: the mutation moves only create triple points.

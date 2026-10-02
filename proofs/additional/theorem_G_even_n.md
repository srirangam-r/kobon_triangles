# Theorem G: a Blanc-type bound with multiple points (even n)

**Setting.**
- A is an affine arrangement of n lines or pseudolines, **n even**, with no three lines
  mutually parallel.
- Multiple points P have multiplicities k_P ≥ 3.
- **General position of multiple points:** no line passes through two multiple points.
- t = number of triple points; T = number of bounded triangular faces.

**Claim.** Λ := Z − D + Σ_P k_P(k_P − 2) ≥ n/2 − t. Since 3T = n(n−2) − Λ, this gives

  T ≤ ⌊(2n² − 5n + 2t)/6⌋.

With t = 0 this is Blanc's bound (arXiv 0801.2845). Points of multiplicity ≥ 4 only
strengthen the inequality.

## Definitions and lemmas

These generalize L1–L4 of `proof_k2.md`.

1. **Segments and uses.**
   - Parallels are removed by a projective map; this keeps bounded triangles and creates no
     new multiple points.
   - A line through k' distinct points has k' − 1 bounded segments, so
     S = n(n−2) − Σ_P k_P(k_P − 2). (Each line through P loses k_P − 2 crossings, and there
     are k_P such lines.)
   - Each triangle has 3 sides and each segment serves at most 2 triangles, so
     3T = S − Z + D. Hence 3T = n(n−2) − Λ.
2. **L1.** A doubly used segment has a multiple endpoint (proof as in `proof_k2.md`).
3. **L2 (cap structure at a k-fold point P, with 2k rays).**
   - A line avoiding P crosses exactly k consecutive rays of P, the ones pointing into its
     side.
   - A doubly used segment with endpoint P and simple far end X is the first segment of a
     ray ρ. The triangles in both sectors next to ρ have their third side on the other line
     C through X, so C crosses ρ−, ρ, ρ+ first. Call C a cap line of P.
   - Each ray has a unique first crossing, so distinct cap lines of P own disjoint sets of
     consecutive rays. Each owns between 3 and k rays.
   - The doubly used segments at P with simple far end number D_P ≤ Σ_C (owned_C − 2)
     ≤ min(#caps·(k−2), 2k − 2·#caps). In particular D_P ≤ 2k − 4.
   - In general position no doubly used segment joins two multiple points, because that
     would need a line through both. So D = Σ_P D_P.
4. **Claims.**
   - A line is *clean* if it avoids all multiple points and is a cap line of no point.
   - L3 (Blanc's Prop. 2.0.4 in t-sequence form, needing n even): **every clean line claims**
     a bounded unused segment, at a simple endpoint of it.
   - A claim at a simple endpoint X is made by the unique line through X other than the
     segment's line. So the number of distinct claimer lines is at most 2Z (unconditional).
5. **L4 (axis lemma, triple points).**
   - A triple point P with 2 cap lines has two disjoint blocks of 3 rays covering all 6
     rays. The middle rays are opposite, forming the axis a_P.
   - If a_P is not a cap line of any other point, then a_P claims. In general position a_P
     passes through no other multiple point, and the apex of each cap triangle is simple.
     Proof as in `proof_k2.md`: the n − 7 segments of a_P left over split into two stretches
     of total odd size, so one is even.

## Counting

Write:
- ℓ = Σ_P k_P, the number of lines through multiple points (general position);
- c' = number of distinct cap lines avoiding all multiple points;
- x = number of pairs (point P, cap line C of P) with C through another multiple point.

Then c' ≤ Σ_P #caps_P − x.

An axis a_P fails L4 only if it is a cap line of some other point Q. That pair (Q, a_P) is
counted in x, and it is a different pair for each failing axis. So:

- claims ≥ (n − ℓ − c') + #(valid axes) ≥ n − Σ_P k_P − Σ_P #caps_P + #{triple P with 2 caps}.
- Z ≥ claims/2, and D = Σ D_P.

So Λ ≥ n/2 + Σ_P f_P, where the per-point contribution is

  f_P = k(k−2) − D_P − (k + #caps_P)/2 + ½·[P triple with 2 caps].

Case by case:

| Point | #caps | D_P | f_P |
|---|---|---|---|
| k = 3 | 2 | ≤ 2 | 3 − 2 − 2.5 + 0.5 = **−1** |
| k = 3 | 1 | ≤ 1 | 3 − 1 − 2 = 0 |
| k = 3 | 0 | 0 | 3 − 1.5 = 1.5 |
| k = 4 | worst case (2 caps, D_P ≤ 4) | ≤ 4 | 8 − 4 − 3 = **1** |
| k ≥ 5 | any | ≤ 2k − 4 | ≥ k(k−2) − (2k−4) − (k+2)/2 > 0 |

Hence Λ ≥ n/2 − t. ∎

## Consequences

- **n ≡ 0, 4 (mod 6):** with t ≤ 2, T is at most Blanc's simple bound.
- **n ≡ 2 (mod 6):** with t ≤ 2, T is at most Blanc's bound + 1.
- **n = 18:** T ≥ 94 needs t ≥ 3. With the segment bound
  3T ≤ S + D ≤ n(n−2) − 3t + 2t, it also needs t ≤ 6. So a 94 in general position has
  3 to 6 triple points.
- **Without general position:** the argument needs the extra doubly used segments that join
  two multiple points, and axes through a second multiple point. For t = 2 the case
  analysis in `proof_k2.md` handles this.

## Corollary 0 (any n, odd or even; elementary, possibly known)

In general position, L1 and L2 alone give D ≤ Σ_P (2k_P − 4). Since Z ≥ 0,

  Λ ≥ Σ_P [k_P(k_P−2) − (2k_P − 4)] = Σ_P (k_P − 2)² ≥ t,

so T ≤ ⌊(n(n−2) − Σ_P (k_P−2)²)/3⌋ ≤ ⌊(n(n−2) − t)/3⌋. This is Tamura's bound minus
1/3 per triple point, and more for higher multiplicities.

In particular, an arrangement attaining Tamura's bound n(n−2)/3 (possible only for
n ≡ 3, 5 mod 6), whose multiple points are in general position, is simple.

Caveat: general position is essential. In a triangle with three concurrent cevians, the
centroid has 6 doubly used segments, because the rays' first vertices are the triangle's
vertices, which are themselves triple points.

# The special-column identities B = C and A = 3C/2, for every multiplicity

The per-line certificates use three special LP columns (portion split `a`, `α′`, `wr`). Their validity condition,
α′ + wr + 1.5a ≤ 3/2 (THEORY §23, audit A30), was derived using two identities. The identities had previously been
validated on data only for arrangements with fourfold points (11,117 arrangements, `work/eng/T27/special_ident.py`).
Here is a proof for arrangements of any multiplicity.

## Definitions (as in `special_ident.py`)

For an arrangement of n pseudolines, with Z unused bounded segments, and for each line L:
- `own_L`: unused bounded segments of L;
- `touch_L`: pairs (u, X) where u is an unused segment of another line and X is a simple endpoint of u lying on L;
- `tri_L`: number of triangle sides on L, so Σ_L tri_L = 3T;
- `s_L = (n − 2) − tri_L`;
- `wr_L`: multiple (non-simple) endpoints of the unused segments of L;
- `v_L`: per-line value of `search/bbl_hallm.py: values`. It is rec_L − 1, plus ±3/2 per N/block ray of a multiple
  point along L, plus 3(m_P − 3) for each multiple point P on L, plus the T1/F transfers. Here
  rec_L = own_L + touch_L.

The sums are A = Σ_L (3 own_L − 1.5 touch_L), B = Σ_L (3 s_L − 1 − v_L) and C = Σ_L wr_L.

For an unused segment u, let m(u) ∈ {0, 1, 2} be its number of multiple endpoints. Then C = Σ_u m(u).

## A = 3C/2

Each unused segment u is counted once in Σ own_L. Each of its 2 − m(u) simple endpoints gives exactly one touch, to
the other line through that endpoint. So

    A = 3Z − 1.5 Σ_u (2 − m(u)) = 1.5 Σ_u m(u) = 1.5 C.

## B = C

- **Portions.** Σ_L rec_L = Z + Σ_u (2 − m(u)) = 3Z − C.
- **Ray terms.** At a point P of multiplicity m with D_P blocks, β_P bridges and N_P = 2m − D_P − β_P other rays,
  the ray terms sum to (3/2)(N_P − D_P) + 3m(m − 3) = 3(m(m − 2) − D_P − β_P/2) = 3c_P.
- **Transfers.** The T1 and F transfers move value between lines and cancel in the sum.
- **Budget identity** (paper, Lemma "budget identity"; valid for all multiplicities, since L1 holds generally and
  S = n(n − 2) − Σ_P m_P(m_P − 2)): Λ = Z + Σ_P c_P.

Hence Σ_L v_L = (3Z − C) − n + 3(Λ − Z) = 3Λ − n − C.

Since Σ_L s_L = n(n − 2) − 3T = Λ, we get B = 3Λ − n − Σ_L v_L = C.

Both identities are exact for every arrangement of pseudolines with points of any multiplicity. The validity
condition of the special columns therefore holds for the multiplicity ≥ 4 certificates as well.

# Status of the K(18) proof

Notation: an arrangement of n = 18 pseudolines (lines, after the projective treatment of parallels), T its number of
bounded triangles, Λ = 288 − 3T, which is a multiple of 3. So T ≤ 94 ⟺ Λ ≥ 6, and T ≤ 93 ⟺ Λ ≥ 7.

## Proved

| Claim | Proof / certificate | Where |
|---|---|---|
| Budget identity Λ = Z + Σ_P c_P | short proof | paper, Lemma (budget identity) |
| T ≤ 94, multiplicity ≤ 3 | per-line LP certificate FC (D = 16), exact DP | `certificates/` (FC); `technical_notes/THEORY.md` §20 |
| T ≤ 93, multiplicity ≤ 3 | FD24 certificate, joint tightness, exact elimination, ILP, flower reduction. Tip lemma (DRAT); 6-X case (2,841 DRAT cubes). Independent audit: 5/5 items pass | `certificates/`; THEORY §20–§23 |
| Perturbation lemma (only triple and bad fourfold points) | exhaustive local redrawings; independent re-derivation | `certificates/`; THEORY §24 |
| Pair lemma (48 of 2,080 patterns) | exhaustive enumeration; independent re-derivation | `certificates/`; THEORY §25 |
| Triple optimality (alternating sums ≥ 2) | short proof | paper, Lemma (triple optimality) |
| T ≤ 94, all multiplicities | per-line LP certificate FC-M (D = 16, ε = 1/4; Σ final + waste ∈ 9ℤ) | `certificates/`; THEORY §26 |
| No 11101110 point in a 94 | credit certificate, margin 9/8 | `certificates/` |
| No 11111110 point in a 94 without an all-8 point | credit certificate, margin 7/10 | `certificates/` |
| A 94 has a (fourfold, triple) adjacency | strict certificate | `certificates/` |
| **Hence a 94 contains an all-8 point** | the above | paper Thm 3 |
| T ≤ ⌊n(n − 7/3)/3⌋ for multiplicity ≤ 3, every even n from 6 to 40 (exact at 6, 8, 10, 12, 14, 16, 20) | the FC certificate (unchanged weights) verified exactly at W = n − 1. Every ingredient is valid for all n (`work/eng/othern/FACTS.md`) | `work/eng/othern/TABLE.md`, `RESULT.md` |
| **K(14) = 54 for all arrangements** | FC-M (unchanged weights) verified exactly at W = 13: final ≥ −1/4, so 3Λ − 14 ≥ −3.5, so Λ ≥ 6. CEGAR patterns 0–3 re-proved for 14 lines (kissat + drat-trim) | `work/eng/k14all/RESULT.md`, `FACTS.md` |

## The open case: an all-8 point

Proved (hand proofs, each step checked; exact checks on 3,474 arrangements; notes in `all8/`):
- Injective token payments: no two consecutive blocks at a triple point, and no three at a fourfold point. Kites with
  triple corners have singly used cap edges in opposite pairs. One-fourfold-corner kites are paid (far-corner
  argument). Fourfold touch and end blocks get fresh tokens.
- Bad-wedge forest lemma (n even).
- Exact identity, with every term ≥ 0:

      Λ = π + U + ½ Σ_P S°_P + K₃ + 2K₄ + ½ Δ.

- A 94 needs π + U + K₃ + 2K₄ ≤ 6, so at least 12 bad wedges.
- Zero-slack all-8 points take one of three local masks and force further fourfold points nearby.

**Remaining inequality (equivalent to K(18) = 93):** in the class,

    2π + 2U + Σ_P S°_P + 2K₃ + 4K₄ + Δ ≥ 13.

**Two-stage plan.**
- Stage 1: prove (B), E ≥ 18 − 3π. This would force any 94 to π = 6 and E = 0, the "zero-credit corner".
- Stage 2: exclude that corner.

**Stage 2 progress (hand proofs, checked by the lead; `all8/ALL8_NOTE6.md`, `all8/STAGE2_TASK6.md`).** Under zero
credit:
- every zero-slack fourfold point is all-8;
- two case-B kites are opposite;
- fourfold first-neighbour clusters are isolated double-case-B stars or collinear paths;
- paths with ≥ 3 fourfold points need ≥ 3k + 11 lines;
- every alternating endpoint forces ≥ 21 lines.

Only two local types remain open: the isolated double-case-B star (needs ≥ 14 lines) and a two-point path with two
single-case-B ends (needs ≥ 17).

**Stage 1 progress (`all8/ALL8_NOTE5.md`, `all8/ALL8_NOTE6.md`).**
- Exact reduction of (B) to an allocation (O2Q) plus an end reconciliation.
- Payment locality and a conditional Hall theorem: a local capacity inequality (LC) implies O2Q.
- LC has 0 failures on all 14,376 93s and the other datasets, but is unproved.

Known 93s spread their credit over all terms (`data/kobon18_93_catalogue.jsonl`), so a trade-off lemma is needed. Its form:
bad wedges force parity defects on interior lines, and the defects force U or Δ. The candidate trade-off inequalities
(B) and (A) are stated in `all8/ALL8_NOTE4.md`; (A) would finish the proof.

## Limitations

- No human refereeing; no formal verification (no Lean files exist).
- Automaton facts used at fourfold apexes are validated on large real data sets; their hand proofs are not all written.
  The special-column identities B = C and A = 3C/2, earlier validated only on data for fourfold points, are proved for
  all multiplicities in `additional/special_column_identities.md`.
- The independent audit covers the multiplicity ≤ 3 chain, not the fourfold certificates.
- SAT encodings are validated on pinned cases, not formally verified.

## Files in this directory

- `technical_notes/THEORY.md`: the complete technical record (definitions, every lemma, the certificate runs), in the
  order it was developed. The paper is the curated statement.
- `all8/`: the notes on the all-8 case (`ALL8_NOTE2.md` to `ALL8_NOTE4.md`; Note 4 is work in progress).
- `additional/`: Theorem G for even n, the lemmas it uses, and the special-column identities B = C, A = 3C/2.

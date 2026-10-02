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

Known 93s spread their credit over all terms (`data/kobon18_93_catalogue.jsonl`), so a trade-off lemma is needed. Its form:
bad wedges force parity defects on interior lines, and the defects force U or Δ. The candidate trade-off inequalities
(B) and (A) are stated in `all8/ALL8_NOTE4.md`; (A) would finish the proof.

## Limitations

- No human refereeing; no formal verification (no Lean files exist).
- Automaton facts used at fourfold apexes are validated on large real data sets; their hand proofs are not all written.
- The independent audit covers the multiplicity ≤ 3 chain, not the fourfold certificates.
- SAT encodings are validated on pinned cases, not formally verified.

## Files in this directory

- `technical_notes/THEORY.md`: the complete technical record (definitions, every lemma, the certificate runs), in the
  order it was developed. The paper is the curated statement.
- `all8/`: the notes on the all-8 case (`ALL8_NOTE2.md` to `ALL8_NOTE4.md`; Note 4 is work in progress).
- `additional/`: Theorem G for even n, and the lemmas it uses.

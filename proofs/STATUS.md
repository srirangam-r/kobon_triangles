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
| K(10) = 25 for all arrangements (known record; independent proof) | FC-M verified exactly at W = 9: 3Λ − 10 ≥ −2.5 and Λ ≡ 2 (mod 3), so Λ ≥ 5. Patterns 0–3 re-proved for 10 lines; explicit lossless redrawings for 7 ≤ m ≤ 25 | `work/eng/fcm_othern/RESULT.md` |

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

The two-point path with two single-case-B ends is **excluded** (`all8/STAGE2_TASK7.md` §3, hand proof, checked by
the lead). Applying a cyclic-order lemma at four triple kite corners shows that one cap line passes through both
outer far corners, which also lie on H; two lines would then cross twice.

**Only one local type remains open in Stage 2: the isolated double-case-B star** (needs ≥ 14 lines). The first vertex
on H beyond each far corner is multiple, and other proved pins hold (`all8/STAGE2_TASK7.md` §§4–5). Also proved:
if the first vertices V± beyond both far corners are triples of type 111100, then each is the last vertex of H, and
H meets exactly 3 + 2 + 4 + 4 = 13 lines, so n = 14. At n = 18 at least one V± is therefore a triple of type 111110
or full, or a quad (which is then a second double-B star with a different case-B axis).

**Stage 2 by SAT (partial; `work/eng/stage2/RESULT.md`).** The zero-credit corner is encoded exactly, and the two
remaining types are split into 1,248 cubes; after the path exclusion only the 416 star cubes matter. Coverage is in `work/eng/stage2/results_summary.txt`: so far about half
of the cubes are UNSAT and **none is SAT**. The rest are undecided at 120–300 s per cube, so Stage 2 is not proved.
The UNSAT cubes have no DRAT certificates yet.

**Stage 1 progress (`all8/ALL8_NOTE5.md`, `all8/ALL8_NOTE6.md`).**
- Exact reduction of (B) to an allocation (O2Q) plus an end reconciliation.
- Payment locality and a conditional Hall theorem: a local capacity inequality (LC) implies O2Q.
- LC has 0 failures on all 14,376 93s and the other datasets.
- LC is **proved for every component of size 1** (`all8/STAGE1_ISOLATED.md`), **for every component made only of
  110110 triples, of any size, and for every component of size 2** (`all8/ALL8_NOTE7.md` §§2–4, checked by the lead).
  - In the data this leaves 149 / 1 / 27 components (93 corpus / earlier / bindings) outside the proved families.
  - Note 7 §5 also proves a disjoint partial payment for bad wedges in the direct form of (B). A wider transport
    graph (§7) has 0 failures on all data, but its Hall theorem is open. `all8/ALL8_NOTE8.md` §2 (checked) shows
    that this Hall condition is equivalent to |E(G_W[S])| ≤ ρ(S) for every set S of lines. Here G_W is the
    bad-wedge forest, and ρ(S) counts the resources with a root on a line of S.
  - In a 94 such a component is an isolated triple with sector pattern 110110 and M = 2.
  - These components are about 97% of all components in the data, and include every component where LC is tight.
  - Corollary: U ≥ #isolated triples.
- LC for larger components, and the end reconciliation, remain unproved.

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

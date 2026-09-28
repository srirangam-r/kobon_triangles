# Claims ledger (decoupled loop)

Status values: proposed → encoded → sampled → refereed-correct | refereed-fixed | refuted.
Every solver constraint carries the tag of the claim it comes from, so a refuted claim can be
rolled back.

| id | claim | source | status | solver tag |
|----|-------|--------|--------|------------|
| C1 | No 94 with ≤ 1 triple point (Blanc extension) | SUMMARY.md | refereed-correct | exact_triple / --blanc |
| C2 | No 94 with exactly 2 triple points | work/proof_k2.md | refereed-fixed | --case2 A (case B deductions removed) |
| C3 | Theorem G: even n, general position, Λ ≥ n/2 − t | work/proof_general.md | refereed-correct | — |
| C4 | No 94 with exactly 3 triple points | work/t3/notes.md | refereed-correct (two steps spelled out) | exact k ≥ 4 |
| C5 | Theorem H: n=18, general position ⇒ T ≤ 93 | work/t3/general.md | refereed-correct (hand only; 4-fold untested) | shared-line constraint |
| C6 | Per-line parity rule: a claim-free line has (#triple points on it) + (#cap roles) odd | SUMMARY.md "Toward the full problem" | refereed-fixed | not encoded |
| C7 | t ≥ 7 impossible without bridges / bent / centroid / all-multiple faces / ≥3-bridge-end points (Lemma C) | work/t3/shared.md | refereed-fixed (both impossibility statements correct; bent-point bound in Lemma C corrected, see verdicts/C07.md) | not encoded |
| C8 | k = 4 open pattern = two disjoint consecutive pairs; then Z ≤ 2, claims ≤ 4 | work/t3/general.md §6 | proposed | k4 pattern, us ≤ 2, U ≤ 4 |
| C9 | Budgets: unused simple segments + ℓ ≤ 6+2k; claims + 2ℓ ≤ 12+4k | derived 23:36 UTC (identity + D ≤ 2k+σ) | proposed | us+h, U+2h |
| C10 | Lemma A as clause: z(abc)∧tri(abC)∧tri(acC)∧tri(aCN) ⇒ z(bCN)∨z(cCN) | work/loop/claims/C10.md | proposed | lemmaA clause |
| C11 | Lemma D: non-cap line, single entries at its triple points, j+q even ⇒ claims (non-axis shared lines with even #points claim) | work/loop/claims/C11.md | proposed | parity-through-triple |
| C12 | k=4 two-mutual-pairs pattern impossible (via C11 on m, m′) — closes C8's pattern | work/loop/claims/C12.md | proposed | k4 pattern + C11 |
| C13 | Axis lemma through other triple points: j′+q even ⇒ axis claims (kills R2 even case) | work/loop/claims/C13.md | proposed (untested) | axis-parity |
| C14 | k=6, β=0 ⇒ B=12, Z=0, all type X & killed, every non-triple line a cap, zero defects; k=5, β=0 ⇒ B≥9, Z≤B−9 (+ forced sub-structure) | work/loop/claims/C14.md | proposed; encoded as k6z (Z=0 via correct "segment used" form, beta=0, non-triple lines are caps) | defect-0 / budget |
| C15 | Mutual pair shape (P,Q consecutive on m, X=a_P∩a_Q, face PQX); β=0 ⇒ mutual line m with even #points, no axis on it, not a cap, claims ⇒ k=6 collinear zigzag impossible | work/loop/claims/C15.md | proposed | mutual-line parity |

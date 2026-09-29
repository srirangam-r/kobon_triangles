
# Shared context for T17–T19: the two-hop Hall lemma (read work/bbl/THEORY.md sections 10–12 first)

**Line values** (spec: search/bbl_hall.py, `values()`).
- v_L = p_L − 1 + Σ over triple points P on L of 3/2·(#N rays of P along L) − 3/2·(#B rays along L), then:
  - **T1 (cap gap):** a block whose two flankers are triple takes 3/2 from its cap per N gap-end ray; it is then
    *served*.
  - **F:** an unserved block takes 1 from the line of each N flank ray.
- Exact identity: 3Λ − n = Σ_L v_L + waste, where Λ = n(n−2) − 3T.
- d_L = v_L − ε·[L through a triple point].

**Relations and HL(ε).**
- 1-hop: a common triple point; axis ↔ cap; pure cap ↔ lines through the blocked point. N2 = distance ≤ 2.
- HL(ε): every set S of negative lines has Σ_S d + Σ_{M∈N2(S), d_M>0} d_M ≥ 0.

**Consequences (even n only; HL is false for odd n).**
- HL(0) ⇒ Λ ≥ n/3. This gives T ≤ 54 at n=14 and T ≤ 72 at n=16 for arrangements with triple points. Both are new for
  non-simple arrangements.
- At n = 18:
  - (a) *strict* HL(0): every nonempty S has Hall sum ≥ 1/2, i.e. violation iff Hall sum ≤ 0;
  - (b) no triple point has all its 1-hop lines at exactly 0;
  - (a) + (b) ⇒ Λ ≥ 9 ⇒ T ≤ 93.

**Data facts (ε = 0).**
- Negative lines are rare. Two families:
  - pure caps with p = 0 (value exactly −1). They cap an odd number of I-blocks, all unserved;
  - axes of blocks with values −1/2 … −2.
- The min Hall sum over nonempty S is ≥ 1. The minimising S is a single line whenever the sum is ≤ 2.

**Code.**
- search/unit_sat.py: T14's UnitModel over χ (triple points; no 4-fold point), validated. Note: its before(r, i, j)
  runs *against* the sweep order of work/t3/arr.py.
- search/hall_model_frozen.py: HallModel. A frozen copy of T15's search/hall_sat.py, validated with 0 mismatches vs
  bbl_hall.py on 738 arrangements. `dwork(L)` gives (terms, const) of the scaled d_L. `build_cp` / `solve_cp` /
  `add_layer` is a CP-SAT Hall layer with threshold −1.
- search/hall_lemma_run.py: runner.
  - Flags: `--eps`, `--strict` (threshold 0), `--cubeB` (line 0 has no triple point and caps a block), `--S0` (S fixed
    to {line 0}), `--nolemmas`, `--workers`.
  - Its `layer()` takes a threshold.
- search/parity_lemmas.py: proven order-free lemmas P1/P2 for lines with no multiple point. Checked sound on 448
  arrangements; they speed up L3 (search/l3_sat.py) from ~13 h projected to 155 s at n = 18.
- search/hall_pure.py: a sound pure-SAT Hall layer with thermometers. Too big (3M clauses at n=8).

**Timings so far** (strict ε = 0, CP-SAT, 8 workers):

| query | n | time |
|---|---|---|
| free query | 8 | 80 s |
| cube B, free S | 10 | 1285 s |
| cube B, S = {0} | 10 | 117 s |

ε = 1/6 is slower: it makes every zero-valued line through a triple point negative. The parity lemmas do not help the
Hall layer at n ≤ 10.

**Rules for you** (override COMMON.md where they differ):
- Create only new files (search/<yours>.py, work/eng/<T>/*); never modify existing files.
- Use at most the number of cores stated in your task.
- Validate every model against the Python reference before timing it.
- Every SAT witness must be re-checked with bbl_hall.py.

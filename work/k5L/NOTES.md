# k5L: per-graph labelled cubes for the k = 5, β > 0 residue

**Files**
- Base: `search/build_k5L.py`. It is k5g (byte-identical refactor) + `search/k5L_layer.py` + the slack counter ZR.
  The CNF has 4.09M vars and 11.8M clauses.
- Cubes: `search/k5L_cubes.py`, producing 196 unit-only cubes (`cubes.jsonl`).
- Layer test: `search/test_k5L_layer.py`, on 117 gallery arrangements. The verifier's re-test (707 mutated + 108 real
  arrangements) is in `work/referee4/k5L/`.
- Verdict: `work/loop/verdicts/AUDIT_k5L.md`, which finds the encoding sound.

**Pilot (150 s per cube, 12 workers)**
- 84 cubes ran, and all timed out: the 80 need-3 cubes plus 4 more. The last 12 of these were aborted when the
  pilot was stopped.

**Diagnostics** (`search/build_k5L_local.py`: the same layer on the bare pseudoline model with exactly 5 triple
points and no triangle count)
- A cube asserting a mutual apex at an O1a point is locally impossible. It still survived 300 s, even as a
  4-unit cube and with extra unique-successor clauses (`--succ`).
- With the signs fixed from a real 18-line arrangement, the model is satisfied instantly, so it is consistent.

**Reading**
- Every local deduction is tied to concrete line indices. The solver would have to re-learn it for each index
  tuple, of order 10^5 of them.
- Labelling points does not pin line indices. The β = 0 closures worked because the cubes pinned concrete line
  ends (wedges).
- So β > 0 needs theory that fixes line-level structure, or kills graphs outright, before SAT can help.

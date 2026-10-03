# Stage 2 by SAT: the zero-credit corner (partial)

**Status: partial. No cube has a model (0 SAT); not all cubes are decided. This is not a proof of Stage 2.**
Current coverage is in `results_summary.txt`, and per-cube results are in `results.csv`.

## What is being excluded
Stage 1, the inequality (B), would force a 94 into the *zero-credit corner*:
- π = 6, every quadruple has zero corrected slack, K₃ = K₄ = 0, U = 0 and Δ = 0.

Under these assumptions, hand proofs (`proofs/all8/ALL8_NOTE6.md`, `proofs/all8/STAGE2_TASK6.md`) leave two local types
of fourfold cluster at n = 18:
- (a) an isolated star with two opposite case-B kites;
- (b) a two-point path whose two endpoints are single case-B.

Every 94 in the corner contains an all-8 point P of type (a), or an endpoint P of type (b).

## Encoding (`stage2_sat.py`, notes in `ENCODING.md`)
- **Base model:** the class model for 18 pseudolines (signotope variables with concurrency, every structural-class
  constraint), with T = 94 by a cardinality constraint.
- **Zero-credit consequences, encoded exactly:**
  - c1: W = 12;
  - c2: U = 0;
  - c3: K₃ = K₄ = 0;
  - c4: blocks at a fourfold point end at kite centres;
  - c5: η₀ = 0;
  - c6: e_mix = 0;
  - c7: all-multiple triangles are double;
  - c8, c9: kite caps;
  - c10: S°_P = 0 at every fourfold point.
- **Validation:**
  - every constraint was checked against exact predicates on about 1,000 pinned arrangements (0 mismatches) and on
    351 fourfold points;
  - all 72 label symmetries preserve the model (864 tests);
  - base-model SAT solutions at T = 70 and 80 were rebuilt and recounted.

## Cubes
- **Cube = (Q, mask).** Q is a D₁₈-orbit representative of the 4 lines through the all-8 point P (104 orbits). The mask
  gives the 8 rays at P:
  - double-B star: 4 rotations of `C...C...`;
  - single-B endpoint: 8 rotations of `C..K.K..`.
- **Total:** 104 × 12 = 1,248 cubes.
- **Pins on first multiple neighbours** (`run_cube.py --pins`; STAGE2_TASK5 §3–4, Note 3 §8):
  - star: all six bridge neighbours are triple;
  - single-B endpoint: the neighbour on the ray opposite the case-B block is fourfold, and the other bridge
    neighbours are triple.
- **Q-endpoint pin** (`run_cube2.py --qpin`, rounds r3+; single-B cubes only):
  - Paths with k ≥ 3 points and alternating endpoints are excluded at n = 18 (STAGE2_TASK6 §5–§6). So the fourfold
    neighbour Q of P on the shared line H is also a single-case-B endpoint.
  - Q's case-B block is therefore the ray of H at Q pointing away from P.
- **Full-corner pin** (`--fullpin`, used for the cubes started after the pilot in round r3).
  - Applies to every case-B kite at P (STAGE2_TASK6 §4, with Δ = 0). Its far corner T on H and its two corners on the
    diagonal through the kite centre are full six-sector triples.
  - So the following first segments are doubly used: H beyond T, T's other line at T in both directions, and the
    diagonal beyond each of the two corners.

## Solving
- **Solver:** CaDiCaL 1.5.3 (python-sat), in conflict-budget chunks.
- **Lazy pair clauses:** a model violating the pair lemma gets its pair clause added, and the solve continues.
- **Results:**
  - UNSAT = no zero-credit 94 in that cube.
  - UNKNOWN = the wall-clock limit ran out (120–300 s per cube).
- **Not yet done:** the final CNFs of the UNSAT cubes were saved but are not in this repository (about 11 GB), and
  none has been DRAT-checked.
- **Pilot of the full-corner pin:** 1 of 2 path cubes that were undecided under the Q pin became UNSAT; the hard star
  cube stayed undecided.
- **Speed tests on one hard star cube:**
  - CaDiCaL at 600 s and kissat at 580 s both return UNKNOWN;
  - a 16-way split on one neighbour decides only 5 of 16 parts at 120 s.

  So the hard star cubes need further hand facts as pins, not just more time.

## Reproduce one cube
```sh
python3 work/eng/stage2/run_cube2.py --cube 12 --mask K.K..C.. --pins --qpin --seconds 300 --out /tmp/q12
python3 work/eng/stage2/run_cube2.py --cube 12 --mask K.K..C.. --pins --qpin --out /tmp/x --dump q12.cnf  # CNF only
```
The CNF built from this repository is byte-identical to the one used in the campaign (sha256 prefix `26c21e2dde6cb6c0`
for this cube).

A whole round runs with `campaign2.py LIST NPROC TAG`, where each LIST line is `cube mask seconds [--qpin]`. The
coverage table comes from `export_results.py`.

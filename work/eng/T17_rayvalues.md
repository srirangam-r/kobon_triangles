
# Task T17: faster Hall queries through a per-ray value model (new files: search/hall_ray.py, work/eng/T17/*; ≤ 6 cores)

The CP-SAT Hall query is slow even at n = 10.

**Hypothesis.** The solver needs lower bounds on donor lines' values, and each value is a flat sum of thousands of
literals. Split per ray instead: an N ray is worth +3/2 and gives away at most 3/2, so its net value is ≥ 0. A block
ray ends at:
- ≥ 0 if served, or if unserved with two N flanks;
- −1/2 if unserved with one bridge flank;
- −3/2 if unserved with two bridge flanks.

So v_L ≥ −1 − ½·#(unserved RN blocks on L) − 3/2·#(unserved RR blocks on L) + p_L. These bounds are invisible in the
flat sum.

**Build `search/hall_ray.py`.** An independent value model on T14's UnitModel:
- each line value is −1 + Σ over rays along L of a per-ray value (an integer variable or a small unary) + portions;
- redundant, *proven* sign/domain constraints for each ray;
- optionally the per-line lower bound above, and per-vertex structure (portions at the vertex where they occur);
- the Hall layer: copy `layer()` from search/hall_lemma_run.py, or write a better one.

**Validation.** With χ fixed, compare v_L, served flags and relations against search/bbl_hall.py on ≥ 300
arrangements (gallery n = 10–18, work/bbl/lineadv/pilot.jsonl, work/phi/bridge93.jsonl), with 0 mismatches.

**Benchmark** against the baseline `search/hall_lemma_run.py`. Same query: strict ε = 0, cube B, n = 10, S = {0} and
free S. Baseline: 117 s and 1285 s.
- Try CP-SAT parameters as well (workers, linearization_level, search branching), a decision order that fixes line 0's
  structure first, and a pure-SAT variant if you see a compact one.
- If you get a large speedup, also run n = 12 (cube B, and the full query with cubes of your choice). Report the growth
  per two lines.

Output: work/eng/T17/REPORT.md with a timing table, what helped, what did not, and a recommendation.

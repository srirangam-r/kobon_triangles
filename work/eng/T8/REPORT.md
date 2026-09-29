# T8: compiled hot paths of the exact extension tools

## Summary (≤ 200 words)
Built `search/dp1fast2/` and `search/extend2_fast.py`. `graph.c` builds the face graph from a wiring word in C,
with arrays element-for-element identical to `dp1fast`. `dp1.c` is the one-line DP on it, and `dp1fast2.py` is a
drop-in `Dp1` wrapper (`from_gens`, `solve`, `best_by_rank`, `enum`; plus a scalar max-only DP). `ext2.c` is the
whole two-line `pair_search` in C: modes G/N/S DPs, (G,D) tables, plan costs, pruned enumeration, base+L1 rebuild,
exact second line. `extend2_fast.py` has the same CLI as `extend2_dp.py`.
**Validation, 0 mismatches:**
- 600 gallery words, n = 10–18, 221 with triple points: arrays, T, by_k, per-start and per-rank bests equal `dp1fast`.
- 154 (base, rank pair) cases at n0 = 8–12 equal `extend2_dp`, plus 21 at n0 = 13–15; 44 of them also SAT-checked.
- 2601 bridge-seed pairs at target 94: all unreached, with counters identical to `extend2_dp`'s run.
- Planted audit: 1000 one-line and 160 two-line cases, all ≥ 93.

**Speed:**
- One-line build+solve: 0.4–0.7 ms at n = 14–18, ×6 vs `dp1fast`.
- Two-line target-94, all ranks per n0 = 16 core: 0.43 s mean (17 cores 7.3 s total), ×62 vs Python end to end.
- Exact max per rank pair: 0.08–0.8 s, against 12–146 s in Python.

**Finding:** DP tools (also the Python originals) do not match SAT on bases with parallel pairs. Use `--complete`.

## Files (all new)
- `search/dp1fast2/graph.h`, `graph.c`: C face-graph builder (`graph_build`), O(1) per-face gain via prefix counts.
- `search/dp1fast2/dp1.c`: `dp1_solve`, `dp1_enum` (same semantics as `dp1fast/dp1.c`) and `dp1_solve_max` (scalar).
- `search/dp1fast2/ext2.c`: two-line solver. `build.sh` builds `libdp1f2.so` (auto-rebuilt by the wrappers).
- `search/dp1fast2/dp1fast2.py`: wrapper, API of `dp1fast.Dp1`.
  - The Python face structure is built lazily, only for x-sequences (`solve()['path']`, `enum()`, `rows()`).
  - Raw state arrays are in `path_states` and `enum_states()`.
- `search/extend2_fast.py`: `max2 INPUT [--ranks r1,r2] [--target T] [--limit K] [--verify] [--verbose] [--out F]
  [--complete]`, `selftest`, and the library class `FastBase(gens).pair(r1, r2, target=None)`.
- Tests and benchmarks (in `search/dp1fast2/`): `test_dp1fast2.py`, `test_extend2_fast.py` (parts A, B, D, E),
  `audit_planted_fast.py`, `bench_dp1fast2.py`, `bench_extend2_fast.py`. Logs are in `work/eng/T8/`.

## What is in C
- **Builder.** Port of `extend_dp.build` plus the flattening. Faces are numbered as in Python (B, Tp, cur[h], then
  creation order) and cyc order is preserved. The wrapper compares `foff, flen, kind, mask, nxt, below, starts, T0`
  with `dp1fast`, and they are identical on every tested word. Gains are computed on the fly from prefix sums, so
  there are no len² tables.
- **Two-line solver.** The whole of `extend2_dp.pair_search` runs in C. Python only parses input, computes the
  interaction constant Kx (`extend2_dp.interaction_bound`, once per base, 0.01–0.6 s, cached per face shape across
  bases) and prints.
  - Base graph: per-state transition tables.
  - Exact second line: rows → word sweep (`rows_to_tokens` port) → `graph_build` → one-start DP, about 40 µs + 40 µs.
  - S-mode filter DP: about 13 µs.
  - The DFS order is the same as in Python. Because the search tree is identical, the partner-eval and pruned counters
    match the Python run exactly.
- Same restrictions as the originals: no 4-fold point, triple points allowed. n0 ≤ 30 (uint32 masks). Not
  thread-safe (static count hash): use one process per worker.

## Validation evidence (logs in work/eng/T8/)
1. **dp1fast2 == dp1fast** (`test_dp1fast2.py`, 600 words, n = 10–18, 221 with triple points). For allow4 ∈ {False,
   True}:
   - the arrays, `by_k`, `T`, `gain`, `start_best`, `start_best_k` and the argmax path are identical;
   - canonical starts and `best_by_rank` are identical, and the scalar max DP equals max over k;
   - the argmax path recounts to T.

   Enumeration (thr = max−1, canonical and not) is identical on 40 small words (80 comparisons). n = 17 records:
   T0 = 85, max 93 (also allow4), all per-rank bests 93. `complete_tokens` is a no-op on words without parallel pairs.
   **0 mismatches.**
2. **extend2_fast == extend2_dp.**
   - **Part D** (3799 comparisons, n0 = 8–16, incl. triple-point bases): MG/MN, (G,D) tables, `count_ge` and the
     base+L1 rebuild + exact partner gain equal the Python versions on random first-line paths (through vertices too).
   - **Part A** (154 (base, pair) cases, n0 = 8–12, incl. edge pairs and triple-point bases): max equal, witness recount
     equal, target mode at max and max+1 agrees. 44 cases are additionally checked against SAT (`fastext.Ext`: SAT at
     max, UNSAT at max+1).
   - **Part E** (21 cases, n0 = 13–15): max equal.
   - **Part B** (`bridge_seeds.json`, 17 seeds × 153 pairs = 2601, target 94): all unreached (as in `bench94.jsonl`) and
     the evals/pruned counters equal `bench94.log` for every seed. The exact maxima quoted in T1 (88, 88, 89, 88, 88
     at (5,8), (3,9), (0,1), (7,16), (2,17)) are reproduced, with witness recount.

   **0 mismatches** in all parts.
3. **Planted audit** (`audit_planted_fast.py`, gallery n=18 93s):
   - **One-line:** 1000 cases (300 seed 777, 700 seed 4242): the exact DP started at the deleted line's rank reaches
     ≥ 93 in all 1000, and so does the overall maximum.
   - **Two-line:** 160 cases (60 + 100): `extend2_fast` at the deleted ranks reaches ≥ 93 in target mode, and the exact
     max is ≥ 93 with witness recount, in all 160.
   - **0 false negatives.**

## Finding: parallel pairs (pre-existing, not a port bug)
- The gallery bases used so far (all `data/n` words with n ≥ 10 and all bridge seeds) have every pair crossing.
  Some words in the `-k` directories and the small n0 = 8 files have parallel pairs (e.g. lines 0 and 1).
- `extend_dp`, `dp1fast` and `extend2_dp` treat a parallel pair as never meeting. The SAT models (chi over triples)
  complete it with a crossing beyond all events, so SAT allows new lines to pass beyond that far crossing.
- Example: `8-1kop1p9na2ibu`, ranks (0,3). Python DP and C both give 22, but the SAT solution has 24 triangles, checked
  with `count_general` and the independent `extend_dp.count_triangles`. With the word completed, DP = 25 = SAT max
  (UNSAT at 26); (1,9) has no placement at all without completion.
- I kept the default semantics identical to the originals, so the Python-vs-C parity tests are exact. The new opt-in
  `complete=True` / `--complete` (`dp1fast2.complete_tokens`) appends the far crossings. With it, DP = SAT on the
  parallel-pair test bases (9 SAT-checked cases at n0 ≤ 10). For words with no parallel pairs it is a no-op.
- A warning is printed when a parallel pair is present and completion is off. **Recommendation:** use `--complete`
  for any base that is not a gallery n ≥ 10 word.

## Speed (one core, machine load about 12, so absolute numbers are noisy)
One-line, end to end from a gens string (`bench_dp1fast2.py`, 20 words per n):

| n | Python build+solve | dp1fast (Py build + C) | dp1fast2 | vs dp1fast |
|---|---|---|---|---|
| 14 | 71 ms | 2.2 ms | 0.39 ms | ×5.7 |
| 16 | 121 ms | 3.1 ms | 0.52 ms | ×6.0 |
| 17 | 156 ms | 4.1 ms | 0.62 ms | ×6.6 |
| 18 | 178 ms | 4.6 ms | 0.71 ms | ×6.4 |

The gain over `dp1fast` comes from the C builder and the scalar max DP in `max_T` and `best_by_rank`. The rest is
ctypes and numpy overhead.

Two-line, n0 = 16 bridge cores, target 94 over all 153 rank pairs (`bench_extend2_fast.py`):
- **Compiled:** 0.13–0.93 s per core, mean 0.43 s, 17 cores in 7.3 s (plus 0.9 s setup incl. Kx).
- **Python** (`extend2_dp`, same machine): first three cores 26.9 s, 83.2 s and 14.9 s.
  - Compiled search for the same three cores: 0.38 s, 0.82 s and 0.16 s, so the search alone is ×72, ×101 and ×95.
  - End to end including setup: ×62 over the three cores, ×32 to ×88 per core.
  - The T1 log (unloaded machine) had 845 s for the 17 cores, against 8.2 s now.
- **Exact max** of five rank pairs of core 0: 0.08, 0.11, 0.17, 0.20 and 0.79 s (Python 12–146 s in T1).

The remaining time is spread over the S-filter DP (about 60%), the partner rebuild + DP (about 35%) and the
enumeration. Kx setup is now a visible share for the fastest cores; it could be ported or cached if needed.

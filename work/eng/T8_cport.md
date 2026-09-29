# Task T8: compile the hot paths of the exact extension tools

**Context:**
- search/dp1fast/ (compiled one-line DP; see work/eng/T2/REPORT.md) still builds the face graph in Python
  (extend_dp.build, about 3.3 ms of about 6 ms per call).
- search/extend2_dp.py (exact two-line solver; work/eng/T1/REPORT.md) is pure Python. Its time goes to rebuilding
  base+L1 (a rows-to-word sweep plus the face-graph build, 6-15 ms) and to the pruned DFS.
- Both tools are validated; keep their semantics exactly (no 4-fold point; triple points allowed).

**Build:**
1. A C face-graph builder from a wiring word (tokens g / g*), producing exactly the arrays dp1fast feeds to C, in
   new files search/dp1fast2/ with a wrapper exposing the same API as dp1fast.Dp1 (from_gens, solve, best_by_rank,
   enum).
2. A C (or dp1fast2-based) inner loop for the two-line solver: new file search/extend2_fast.py, same CLI as
   extend2_dp.py (`max2 <input> [--ranks] [--target]`). Move the base+L1 rebuild, the exact second-line DP and the
   first-line enumeration into compiled code where they dominate.

**Validate (mandatory):**
- dp1fast2 == dp1fast (T, by_k, per-rank bests) on ≥ 500 gallery words, n = 10-18, with triple points.
- extend2_fast == extend2_dp: exact max on ≥ 40 (base, rank pair) cases at n0 = 8-12, and target-94 answers on
  work/eng/T1/bridge_seeds.json.
- Planted audit: search/audit_planted.py-style cases (delete 1 or 2 lines from gallery 93s): the new tools must
  reach ≥ 93 at the deleted ranks, 0 false negatives on ≥ 300 one-line and ≥ 30 two-line cases.

**Benchmark:** speedups end to end, and the target-94 all-ranks time per n0=16 core.

**Deliverables:** new files only; work/eng/T8/REPORT.md.

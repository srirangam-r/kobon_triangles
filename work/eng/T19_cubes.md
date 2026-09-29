
# Task T19: settle HL decisively at n = 10, 12, then 14, 16 by cube-and-conquer (new files: search/hall_cubes.py, work/eng/T19/*; ≤ 8 cores)

**Goal.** Decisive proofs (every cube UNSAT, no timeouts) of HL(0) at even n. HL(0) is the non-strict version:
violation iff Hall sum ≤ −1 in the model's scaled units.
- n = 10 and 12 first.
- Then n = 14 and 16: these would prove T ≤ 54 and T ≤ 72 for arrangements with triple points and no 4-fold point.
- Also run the strict version (threshold 0) wherever it is cheap. n = 18 needs it.

**Tools.**
- Build on search/hall_model_frozen.py (the HallModel) and the runner search/hall_lemma_run.py. Import them; do not
  modify them.
- Cube B (line 0 has no triple point and caps a block) at n = 10, strict: 1285 s with free S, 117 s with S = {0}.

**Design cubes that together cover every case.** Ideas:
- A: line 0 clean; B: pure cap; C: line 0 through k triple points (k = 1, 2, 3, 4+).
- Split by the scaled value of line 0 (it must be negative since line 0 ∈ S), and by the point types or block statuses
  on line 0.
- Split by |S| = 1 versus |S| ≥ 2. A minimal violating S is connected: when it splits into parts whose N2
  neighbourhoods are disjoint, one part already violates. So a connectivity cut is sound. Write the argument in your
  report.
- Use CP-SAT with 4–8 workers per cube, or run several cubes in parallel.
- Log each cube as one JSON line with result and seconds.

**Pilot, then production.**
- Report the projected cost before any run expected to exceed 2 hours of wall time.
- Every SAT witness: re-check it with search/bbl_hall.py and save it. A genuine violation is big news: stop and report.

Output: work/eng/T19/results.md (n × cube table) and work/eng/T19/REPORT.md, including the exact list of cubes and why
they cover everything.

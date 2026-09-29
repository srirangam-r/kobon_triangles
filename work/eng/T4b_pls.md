# Task T4b: continue T4, the local-search generator (search/pls.py exists; read it and work/pls/)

**Status:** your first run produced about 60k n=17 samples (work/pls/n17_plain_w*.jsonl, T up to 85, some with 4-5
triple points and 3-4 bridges). The parent swept all 44,547 distinct samples with T >= 82 through the exact compiled
one-line DP (`search/sweep_dp1.py`, using search/dp1fast): best completion to 18 lines is 93, never 94. That sweep
takes 60 s on 6 cores, so the generator is now the bottleneck and the key lever.

**Goal:** maximize the number of DISTINCT, DIVERSE near-optimal 17-line arrangements (T >= 82) per core-hour,
biased toward the family a 94 would need:
- many triple points (k 4-9);
- doubly used bridges;
- low Z;
- a 94 needs D − Z = 3k − 6.

**Also:** diversify away from the gallery structures (random restarts, tabu or annealing on T plus a bonus for k
and bridges, and crossover). Report what fraction of samples are new up to symmetry: dedupe by canonical form
under the 4n end-circle actions of search/symmetry.py, or a cheap invariant hash if that is too slow.

**Deliverables:**
- improve search/pls.py in place (it is your file) and write work/eng/T4/REPORT.md with throughput and diversity
  stats;
- run it for about 45 minutes on 3 cores, writing work/pls/gen2_*.jsonl (same row format: n, T, k, bridges, h,
  gens, chi);
- then run `uv run --no-project --with python-sat --with numpy python search/sweep_dp1.py work/pls/hits94_gen2.jsonl work/pls/gen2_*.jsonl --workers 3 --min-T 82`
  and include its output in the report.

If ANY hit >= 94 appears, stop and put it first in the report.

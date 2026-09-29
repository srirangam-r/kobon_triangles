# Task T6: DP-based large-neighbourhood walk at n = 18

Use the compiled exact one-line DP in search/dp1fast/ (read work/eng/T2/REPORT.md and dp1fast.py) as a search
engine.

**State:** an 18-line pseudoline arrangement, a wiring word; start from gallery 93s in
tools/external/kobon-solutions/gallery/data/18/*.json, from high-T samples in work/pls/, and from random restarts.

**Move ("ruin and recreate"):**
1. Delete one line; see work/research2/delete_line.py or extend_dp.py `reinsert` mode for how a line is removed
   from a word.
2. Compute the EXACT best re-insertion with dp1fast, or sample among the top re-insertions using `.enum(thr)`.
3. Rebuild the new wiring word from the returned path. extend_dp.path_rows and the reinsert code show the path
   format; verify every rebuilt word by recounting T with kobon-solutions verification quick_check or
   kobon_sat.count_general.

**Acceptance:** simulated annealing or tabu on T, with an optional bonus for triple points and doubly used bridges
(search/test_k5L_layer.py geometry()). Walk the 93-plateau widely. Also try a 2-line move: delete 2 lines, then
re-insert them greedily with the DP.

**Throughput goal:** ≥ 10 exact moves per second per core. Dedupe visited states by hash.

Any arrangement with T >= 94 must be verified independently: recount with both counters, then write it to
work/dpwalk/HIT_*.json and stop.

**Deliverables:**
- search/dpwalk.py;
- a 60-minute run on 3 cores with stats (states visited, distinct 93s found, best T, T/k/bridge histograms) in
  work/dpwalk/ and work/eng/T6/REPORT.md.

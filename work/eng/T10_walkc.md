# Task T10: compile the DP walk's remaining Python hot paths

**Context:**
- search/dpwalk.py (T6; see work/eng/T6/REPORT.md) runs about 54 exact moves/s/core with dp1fast.
- The compiled one-line DP is now much faster (search/dp1fast2/, work/eng/T8/REPORT.md: build+solve 0.4-0.7 ms),
  so the walk's per-move Python work dominates:
  - deleting a line from a word;
  - rebuilding the wiring word from the DP path (the rows-to-word sweep);
  - the exact recount of triangles;
  - hashing/dedupe;
  - k and bridge counting.
- search/dpwalk2.py (T9) is being used right now: do not modify it or dpwalk.py.

**Build:**
- search/walkc/: a C library plus a Python wrapper with
  - `delete_line(word, d) -> word`;
  - `insert_path(word, path) -> word`, the rebuild from a dp1fast2 argmax or enum path;
  - `count(word) -> (T, k, bridges, Z, D)`, exact, with bridge = a doubly used segment between two triple points;
  - `canon_hash(word)`, invariant under the 4n end-circle symmetries and a global sign flip; see
    search/coverage.py canon() for the definition. Hash the canonical form.
- search/dpwalk_c.py: the same walk logic as dpwalk.py (moves, acceptance, starts, HIT handling) using walkc +
  dp1fast2. Add `--start FILE`, `--wb`/`--wk` weights, and Z-targeted deletion (`--zprob`), as T9 describes in
  work/eng/T9_walk2.md.

**Validate (mandatory):**
- walkc functions equal the Python ones (search/audit_planted.py rows_to_word, delete_line.py, quick_check
  count_triangles, test_k5L_layer.geometry, coverage.canon) on ≥ 1,000 words, n = 10-18, with triple points.
- Every recorded 93 from a 5-minute dpwalk_c run re-counts to 93 with quick_check.
- Throughput: exact moves/s/core, dpwalk_c vs dpwalk.

**Deliverables:** new files only; work/eng/T10/REPORT.md. CPU ≤ 3 cores.

# Task T11: raise the calibrated REACH of the exact walk, then rerun production at n=18

**Context:** read work/eng/T6/REPORT.md, work/eng/T9_walk2.md and search/dpwalk2.py (T9 died before its report;
its results are in work/lns/PROGRESS.md and work/dpwalk2/).
- The exact DP walk covers the bridge-rich 93 plateau it can reach well: Chao1 says 92-96% of about 137 classes.
- But calibration at n=16 shows REACH is the bottleneck. From bridge-free starts, the best trial (calE) found only
  4/17 held-out bridged 72 classes (work/pls/bridge16_heldout.json), plus 52 new bridged-72 classes.

**Goal:** raise held-out reach at n=16 well above 4/17 (aim ≥ 10/17), then apply the same portfolio at n=18.

**Levers (your choice, measure each):**
1. **Exact two-line moves.** search/extend2_fast.py (validated, T8: about 0.4 s per core in all-ranks target mode)
   in target mode "≥ current T", or `FastBase(gens).pair(r1, r2, target=...)`: delete 2 lines, accept an exact
   re-insertion of 2 lines reaching >= the current T, preferring more bridges or triple points.
2. **Diverse starts:** random words grown line by line with sampled DP paths; high-T pls samples (work/pls/); and
   restarts from archived states with bridges.
3. **A parameter portfolio** across chains (weights wb/wk, zprob, temperatures) instead of one setting.
4. **Any valid idea you find.**

**Calibration protocol:** n=16, start only from bridge-free gallery records (hold out the 17 files in
bridge16_heldout.json); count held-out classes rediscovered (canonical classes, as search/coverage.py canon or
T9's hash); report per lever.

**Production:** n=18, the best portfolio, 12 chains for 60 minutes (you may use 12 cores), seeded as T9 did plus
work/dpwalk2/bridge93_prod.json.
- Any T >= 94 is verified with count_general and quick_check, written to work/dpwalk3/HIT_*.json, and ends the run.
- Report capture-recapture (Chao1 across chains) for 93 classes, for bridge-rich (b>=3) 93 classes and for the
  realizable range (k 6-9, b>=3).

**Deliverables:** a new file search/dpwalk3.py, work/dpwalk3/ and work/eng/T11/REPORT.md.

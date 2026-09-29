# Task T9: bridge- and Z-targeted exact DP walk, calibrated

**Start from** search/dpwalk.py (read work/eng/T6/REPORT.md). Write a NEW file search/dpwalk2.py (copy and
extend; do not edit dpwalk.py).

**Background:**
- A 94 needs Λ = Z − D + 3k = 6, while every 93 has Λ = 9. So it needs about 3 more doubly used segments or 3 fewer
  unused ones. Z counts unused bounded segments; D counts doubly used ones; bridges are doubly used segments
  between two triple points.
- The known bridged optima: work/dpwalk/bridge93.json (198 bridge-rich 93s, 54 classes up to symmetry;
  k up to 21, bridges up to 39). At n=16 there are 17 bridged records (T=72) in work/pls/bridge16_heldout.json.
- A flip-based generator never found those 17 from bridge-free starts (frontier with bridges >= 1 stuck at 71).

**Add:**
1. `--start FILE` (jsonl or json rows with "gens"), and `--n` (16 and 18 at least).
2. Z-targeted deletion: prefer deleting lines that carry unused segments or defects (compute per-line Z and D
   contributions from the arrangement). Mix it with uniform deletion at a tunable rate.
3. Tunable objective weights for triple points (k) and bridges; also try a Λ-aware score.
4. Cross-chain dedupe by canonical class. search/coverage.py canon() works up to symmetry: use it, or a cheaper
   invariant hash.
5. Optional exact two-line moves via search/extend2_dp.py in target mode (or via extend2_fast.py if
   work/eng/T8/REPORT.md shows it is validated) for bridge-rich states.

**Calibration (mandatory, before production):**
- At n=16, start ONLY from bridge-free gallery records: tools/external/kobon-solutions/gallery/data/16/*.json
  minus the 17 held-out files.
- Report how many of the 17 held-out bridged 72 classes you rediscover, and whether you find bridged 72s at all.
  Use canonical classes to compare.
- Tune until reach is clearly nonzero, or report honestly that it stays zero.

**Production:**
- At n=18, seed from bridge93.json plus gallery 93s; 60 minutes on 8 cores (8 independent chains, different
  seeds).
- Any T >= 94 is verified with count_general and quick_check, written to work/dpwalk2/HIT_*.json, and ends the run.
- Report capture-recapture (Chao1 on incidence across the 8 chains) for distinct 93 classes and for bridge-rich
  (>= 3 bridges) 93 classes, and the bridge/k histograms.

**Deliverables:** search/dpwalk2.py, work/dpwalk2/, work/eng/T9/REPORT.md.

CPU: you may use up to 8 cores for the production run (3 otherwise).

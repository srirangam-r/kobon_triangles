# Autonomous search log (user away; started 00:47 UTC, 2026-09-28)

## Standing setup
- **Local (24 cores):**
  - 2-line extension of the 17 bridge-carrying n=16 records (18 workers, Blanc on);
  - k=8 two-line re-placement, resumed (3 workers);
  - one-call selector timing test;
  - lineage step n=12 bridge core -> n=14 (T >= 54).
- **AutoLab (1 x cpu-xlarge, sequential agent):**
  - 6a4a8edf k=6 re-placement (running, old code);
  - queued with Blanc: c28ea3c3 k=7 re-placement, 91d6ab5f 3-line bridge seeds, e7d4e559 16-line extension without bridges.
- Every call decides SAT/UNSAT; any SAT is re-counted exactly and saved with its full sign vector.

## Log
- 00:47 Bridge-seed 2-line re-placement (3 seeds, 603 calls): **all UNSAT**.
- 00:47 Blanc adopted everywhere (1.8x faster). Runner resume now works across worker counts. AutoLab queue resubmitted with the faster code.
- 00:47 Lineage n=12 bridge core (k6, beta6, T38) -> n=14 with T >= 54 (the n=14 record): **UNSAT for every 2-line placement** (21 min). The core does not survive at record level; that lineage stops.
- 01:29 Sampler (SAT-generate 17-line arrangements with T>=83, k=7, beta>=3, then one-line 94 completion): no first sample in 40 min. As with k5L, SAT cannot generate structured near-optimal 17-18 line arrangements from scratch. Stopped.
- 01:38 Queued: local top-17 bridge-preserving 16-line cores (after the n=16 extension); AutoLab d49b4f55 = next 60 cores (replaces the record-based e7d4e559). Reason: a 94's 16-line cores should have T16 ~63-66, like these, not the 72 records.
- 02:47 **AutoLab 6a4a8edf (k=6 seeds, 2-line re-placement): 10,231 / 12,261 calls, all UNSAT, 0 SAT** (150-minute deadline; 2,030 left; mean 26 s, max 317 s). Results committed on the AutoLab branch exp/autolab-.../6a4a8edf (b78ac35). The platform marked the experiment "discarded" (score unchanged), as expected. The first fetch of the files hit an HTTP 500; will retry.
- 02:47 Local: n=16 bridge extension 2,455 / 3,417 UNSAT; k=8 re-placement 848 / 3,417 UNSAT. Runner v2 (dynamic queue, single orientation) validated for correctness (93 control SAT), but its 94 calls look slow; diagnosing Blanc vs the symmetry break before the cores batch uses it.
- 02:52 **AutoLab fix:**
  - The first batch's seed commits came from a stale base with only .gitignore and push94/ (no submission/solution.json), so the evaluator hard-rejected them and the orchestrator raised "repeated_failures".
  - Re-seeded all queued experiments from the full tree (after `autolab pull`): 5bd1002f k=7 re-placement, 40546499 the 60 bridge cores, 2504f758 bridge-seed 3-line.
  - Told the agent via `autolab say` and resumed it.
- 02:52 **Runner lesson:** dropping the chi(0,1,2) != -1 break made placements with a new line among lines 0-2 about 40x slower (about 2,000 s vs 51 s). Kept the break (both orientations there). Kept the shared job queue. Re-validated: n=17 base at 94 gives 21/21 UNSAT, max 61 s.
- 02:52 Encoding A/B on extension calls (3 ranks away from 0-2): Blanc/break variants are all 27-42 s total, so Blanc is roughly neutral on extensions and 1.8x faster on re-placement.

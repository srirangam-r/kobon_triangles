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

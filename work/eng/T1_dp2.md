# Task T1: exact two-line extension

Build an exact solver for "max bounded triangles after adding TWO new pseudolines to a fixed arrangement" (all slope
ranks, triple points allowed, no 4-fold point). It must be far faster than SAT per placement.

**Method** (your choice, but any pruning bound must be provably valid):
- Branch-and-bound over first-line paths using the one-line DP's upper bounds, with an exact best second line by
  the one-line DP on base + L1.
- Or a joint DP over both paths.

**Validate:**
- On small gallery bases (n0 = 8–12), the DP max equals the largest SAT target from fastext.Ext for several rank
  pairs (both sides: SAT at max, UNSAT at max+1).
- Brute force on tiny cases.
- No placement reaches 94 on the ext16_bridges seeds.

**Benchmark:** seconds per n=16 seed over all 153 rank pairs.

**Deliverables:** search/extend2_dp.py (CLI `max2 <input>`) and work/eng/T1/REPORT.md.

# Task A1: independent adversarial audit of search/extend2_dp.py (exact two-line extension)

You are an AUDITOR. Do not trust the author's report (work/eng/T1/REPORT.md); read the code.

A pruning bug would silently hide a 94, so the question is whether the pruned search can ever return a maximum
below the true maximum (a false negative).

1. **Check the math.** The bound is `T <= T0 + Kx + G1 + G2 + min(D1, D2)`, with the interaction term I computed
   in `interaction_bound`. Check the two-case cover (case A: G1 >= ta; case B: G2 >= X + 1 - ta), the
   enumeration thresholds, and the incumbent tightening. Look for off-by-one errors, missed face types (faces with
   triple-point corners, unbounded faces, the L1 x L2 crossing at a base vertex or on a base line), and rank-pair
   edge cases (r1 = 0, r2 = n0+1, adjacent ranks).
2. **Test adversarially.**
   - Hundreds of random small bases (n0 = 5–10), including many with triple points: random wiring words, or
     mutations of gallery words in tools/external/kobon-solutions/gallery/data. For every rank pair, compare the
     pruned max with an unpruned brute force (all first-line paths × exact best second line), and with fastext.Ext
     SAT at max and max+1 where feasible.
   - Also planted cases at n0 = 12–16: delete 2 lines from gallery arrangements; the max at the deleted ranks must
     be >= the original T.
3. **Report** any counterexample with a minimal reproducer.

**Deliverables:** work/eng/A1/REPORT.md (verdict: sound / unsound / sound-with-caveats, plus evidence counts) and
the test scripts in work/eng/A1/. Do not modify search/extend2_dp.py; if you find a bug, describe the fix.

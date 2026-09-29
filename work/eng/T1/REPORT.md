# T1: exact two-line extension: report

## Summary
`search/extend2_dp.py` (CLI `max2 <input> [--ranks r1,r2] [--target T] [--verify] [--out F]`, plus `selftest`) computes the
exact maximum number of bounded triangles after adding two pseudolines at final slope ranks (r1 < r2) to a wiring word.
Triple points are allowed, 4-fold points are not.

The method is branch-and-bound over first-line paths with an exact second line.
- Base: one-line face-graph DP, imported from `work/research2/extend_dp.py`.
- Exact second line: rebuild base+L1 from event rows via a new rows→wiring-word sweep, then run the one-line DP.
- Bound: `T <= T0 + Kx + G1 + G2 + min(D1, D2)`.
  - `G` is the one-line gain and `D` the number of base triangles cut.
  - `Kx` is the L1×L2 crossing term. Brute force over all chord pairs in every base face gives Kx = 2 on every instance
    tried. Non-crossing shared faces contribute at most [face is a triangle]; this is asserted per instance.
- Search: the bound gives a two-pass cover (N = G + D).
  - Pass A enumerates line e with N_e >= a.
  - Pass B enumerates line f with G_f >= X - a + 1.
  - The enumeration is an exact (G, D)-Pareto DFS, so no dead leaves are visited.
  - A cheap DP with +1 on shared triangles filters candidates before the exact evaluation.
  - The incumbent tightens the thresholds while the search runs.

## Validation
- **Brute force** (all first-line paths × exact second line) equals the pruned search on every rank pair of gallery bases:
  n0=6 (3 bases, 84 pairs) and n0=8 (3 bases, 135 pairs). 0 mismatches. `selftest` re-runs a subset.
- **SAT ground truth** (fastext.Ext, both orientations, SAT at DP max and UNSAT at max+1), 0 mismatches:
  - 132 pruned-search checks on gallery bases: n0=9 (8 checks), n0=10 (45, including triple-point bases), n0=11 (12),
    n0=12 (12, triple-point bases). These include the edge pairs (0,1), (0,n0+1) and (n0,n0+1).
  - 37 brute-force-vs-SAT checks at n0=10 (older code path).
  - n0=6: brute force = SAT on all pairs.
- **n0=16**: for `16-1bz86nu5hcy50` (work/eng/T1/bridge_seeds.json[0]), ranks (7,16) and (5,8) both have DP max 88. SAT is SAT at 88 and UNSAT at 89 (56–97 s for the UNSAT).
- **No 94 on the bridge seeds**: all 17 seeds × 153 rank pairs (2601 pairs) are below 94 in `--target 94` mode.
  This is consistent with all recorded SAT UNSAT results.
  The per-pair output is in `work/eng/T1/bench94.jsonl`.
  Exact maxima at n0=16 are about 88–89 (T0=72): (5,8)=88, (3,9)=88, (0,1)=89, (7,16)=88, (2,17)=88 on the first seed.
- **Witness recount**: `--verify` recounts the triangles of the extracted arrangement (`extend_dp.count_triangles`) in max mode.

## Speed (one core, pure Python)
- `--target 94`, all 153 rank pairs: **15.5–132 s per n=16 seed (mean 50 s, 845 s for the 17 seeds)**.
  That is 0.1–0.9 s per rank pair. A SAT call took 30–200 s per (R, sign) for the same job, so about 100–300× faster overall.
- Exact-max mode: 12–146 s per rank pair at n0=16 (26 s, 24 s, 146 s, 12 s, 29 s for the five pairs above).
  This is about the cost of one SAT UNSAT call, so it is no big win there.
- The time goes to the exact second-line evaluation (rebuilding base+L1, about 6–15 ms) and the shared-triangle filter DP (about 1 ms).
  Neither is compiled.

## Caveats
- The bound assumes bounded triangles and no 4-fold points, as in fastext.Ext.
- Line pairs at ranks 0 and n0+1 are handled natively (validated against SAT); no rank-equivalence shortcut is used.

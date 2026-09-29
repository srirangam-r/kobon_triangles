# Seeded constructive searches for a 94 (pseudolines; each call runs to SAT/UNSAT)

**Runners**
- `work/lns/push/run_lns.py`: re-place r lines of a seed at the same slope ranks.
- `work/lns/push/run_ext.py`: add lines to an n0-line record at all slope ranks.
- Both are resumable and write per-worker jsonl files. When the freed lines meet {0, 1, 2}, both orientations are tried.
- AutoLab copies of the runners are in `~/stuff/kobon-loop-al/push94/`.
- `search/ext_sel.py`: one SAT call per seed, with a selector variable per placement.

## Engineering A/B (same 8 bridge-seed LNS calls, all UNSAT)
| Variant | Total s | Notes |
|---|---|---|
| base (kmax 16, cadical153) | 481 | |
| **+ Blanc clean-line clauses** | **264** | **1.8× faster; now the default (`--no-blanc` to disable)** |
| kmax 10 (tighter defect budget) | no gain | stopped |
| Blanc + cadical195 | slower | 57–69 s per call |
| Blanc + cadical300 | 322 | |
| kissat on unit-fixed CNF, fresh per call | ≈ same | 28–36 s per call; no gain over incremental |
| one-call selector (n0 = 17 base, 21 placements) | 152 vs 246 | control: 93 SAT in 1.8 s, recount T = 93 |

## Results so far
- One-line extension of the 10 n = 17 records: 360/360 UNSAT (duplicates the earlier DP over all 255).
- 16-line sub-arrangements of the high-k 93s have T16 ≤ 70 (1,908 at 70). The gallery n = 16 records are 72, so
  they are the better extension seeds.
- Sub-arrangements of the n = 20 records have 18-line T ≤ 91.
- The rest are running: see `work/lns/push/*/part_*.jsonl` and the AutoLab experiments 6a4a8edf, 01c6875e,
  b9fed6bc and 5c526679.

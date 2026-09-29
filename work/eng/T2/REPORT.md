# T2: compiled one-line DP (search/dp1fast/)

**Built.** `dp1.c` is a C port of `extend_dp.solve` and `extend_dp.all_paths`. `build.sh` compiles it with gcc (`-O2`, `libdp1.so`). `dp1fast.py` is the ctypes wrapper. It reuses `extend_dp.build` for the face graph, then flattens that graph into arrays for C.
- `Dp1(tokens, n)` / `Dp1.from_gens(gens)`.
- `.solve(allow4, canonical)` returns the exact max T, best T by number of new triple points, per-start bests, and an argmax path in `extend_dp.path_rows` format.
- `.best_by_rank()` gives the best T per start class h (the number of base lines below the new line at its left/bottom start).
- `.enum(thr)` lists all directed paths with T >= thr, via a C DFS pruned by the DP bound. `canonical=True` halves the count by dropping reversed duplicates.

**Validation** (`test_dp1fast.py`, `check_rank_gt.py`):
- 370 gallery arrangements, n=10..18, 178 with triple points, each run with `allow4` False and True (740 comparisons). T0 and the full best-T-by-k dict are identical to Python in all 740. The C argmax path recounts to the maximum, and canonical starts give the same maximum.
- Enumeration (thr = max−1) on 10 arrangements with n=10–11 gives identical path multisets to `all_paths` plus recount (counts 68–2278). The canonical count is exactly half in every case.
- n=17 ground truth: all 10 records have T0=85 and max T=93, also with `allow4`, never 94. That matches the 360 UNSAT at 94 in `work/ext`. In `check_rank_gt.py`, all 17 start classes reach 93. The ground truth has sign +1 SAT at all 18 ranks; the two extreme ranks are the same bottom-to-top path.
- Ground-truth sign −1 is SAT only at ranks 0–2. I think that is the `chi(0,1,2) != -1` symmetry break, but I did not verify it.

**Speed** (`bench_dp1fast.py`, 20 arrangements per n):

| n | Python build+solve | C solve | End-to-end speedup |
|---|---|---|---|
| 14 | 141 ms | 2.2 ms | ×24 |
| 16 | 201 ms | 2.2 ms | ×39 |
| 17 | 169 ms | 2.9 ms | ×27 |
| 18 | 185 ms | 3.4 ms | ×28 |

The solve step alone is about ×55–90 faster. The end-to-end figure includes about 3.3 ms of Python build and flatten, which is now the bottleneck. The 370-file test took 107 s in Python and 4.8 s in C.

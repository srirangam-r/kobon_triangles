# T6: DP ruin-and-recreate walk at n=18 — no 94

**Built:** `search/dpwalk.py` (`selftest` / `run` / `stats`). State = wiring word. Move = delete 1 line (85%) or 2 lines (15%, greedy: sampled top re-insertion, then exact best), then re-insert with `dp1fast` (`.solve` for the exact max; C `dp1_enum` for candidates within 0–2 of the max, chosen by temperature). The rebuilt word comes from a rows→wiring-word sweep, and every candidate is recounted with `count_triangles`. Acceptance is annealing on T + 0.05·k + 0.15·bridges, with the temperature cycling 0.15–0.65. Visited states are deduplicated by hash of the rows. Starts: gallery 93s, earlier 93s from the run, n=17 `work/pls` samples plus one DP line, and random words grown line by line with sampled DP paths. Any T>=94 is recounted with `count_general` and `quick_check` and written to `work/dpwalk/HIT_*.json`.

**Validation** (`selftest`): the sweep round-trips the rows of 25 gallery arrangements. For 75 delete/re-insert cases, the rebuilt word's recount equals the DP max exactly, and 375 sampled near-top paths recount to >= max−1. The 2-line delete followed by re-insert also recounts exactly.

**Run** (60 min, 3 cores, seed 7): 584,656 exact moves (87,430 of them 2-line) with 672,086 DP solves. That is **54 moves/s/core**, above the 10/s goal. 543,630 distinct states visited (revisits 41k). **Best T = 93; no 94, no HIT.** 56,044 distinct 93-arrangements found, all reached from 284 gallery, 139 archived-93, 62 pls17+1 and 77 random starts. Two words can encode the same arrangement up to reflection or rotation, so the true count of distinct 93s up to symmetry is lower.
- T histogram (distinct states): 93: 56,089; 92: 118,407; 91: 138,363; 90: 85,888; 89: 57,504; below 89: about 87k.
- 93s by (k, bridges): most have k=0 (44,117), then k=1 (9,411), k=2 (1,449). Bridge-carrying 93s exist up to k=21 with 39 bridges; the bridge metric follows `geometry()`, i.e. triple-to-triple segments with a triangle on both sides.
- Full k and bridge histograms are in `work/dpwalk/run1_stats.txt`; the per-worker 93 words are in `work/dpwalk/run1/d93_w*.jsonl`.

Interpretation: the 93-plateau is huge and connected under single-line DP moves, but no single- or greedy double-line re-insertion from any of the 543k visited states reaches 94.

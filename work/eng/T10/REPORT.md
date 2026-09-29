# T10: the DP walk's remaining Python hot paths, compiled

## Summary (≤ 200 words)
Built `search/walkc/` (C library `walkc.c` + wrapper `walkc.py`) and `search/dpwalk_c.py`. `walkc.c` includes the
unmodified dp1fast2 graph builder and DP and adds `delete_line`, `insert_path`, `count` (T, k, bridges, Z, D, plus
per-line Z/D/incident-Z), `canon_hash` / `canon_bytes`, `rows_hash`, `rows_to_word` (both sweeps) and fused
`Base.eval` (rebuild + count + hash). `dpwalk_c.py` is the dpwalk.py/dpwalk2.py walk on top, with `--start`,
`--wk/--wb/--wd/--wz`, `--zprob` and the rest of dpwalk2's options (not `--pair-rate`).
**Validation, 0 mismatches:** 1,113 gallery/bridge words, n = 10–18, 512 with triple points (delete, count, bridges,
canon, sweeps, symmetry invariance), plus 800 delete/re-insert bases with 21,405 rebuilt paths against dpwalk's
Python path. A 5-minute, 3-core `dpwalk_c` run recorded 70,249 T = 93 class rows; all recount to 93 with
quick_check (k too; 2,650 deep-checked). No 94.
**Speed** (1 core, exact moves/s): dpwalk 116, dpwalk_c **1,012** (×8.7). Per primitive: ×17–50. The walk is now
DP-bound.

## Files (all new)
- `search/walkc/walkc.c`, `build.sh` (→ `libwalkc.so`, auto-rebuilt by the wrapper), `walkc.py`.
- `search/walkc/test_walkc.py`, `bench_walkc.py`, `recount_records.py`.
- `search/dpwalk_c.py`; logs and runs in `work/eng/T10/`.

## API (`walkc.py`; a word is bytes `g0 w0 g1 w1 ...`, a token list or a gens string; results have the same type)
| function | meaning |
|---|---|
| `delete_line(word, d)` | = `extend_dp.delete_wire` |
| `count(word)` → `(T, k, bridges, Z, D)` | exact; `count_lines` adds per-line Z, D and incident-Z lists |
| `canon_hash(word)`, `canon_bytes(word)` | 64-bit hash of / the canonical chi form = `coverage.canon` |
| `rows_hash(word)` | 64-bit hash of the labelled event rows (cheap visited-set key) |
| `insert_path(word, path, start)` | rebuild from a dp1 argmax/enum exit-state path (`start` = slot/direction hint) |
| `rows_to_word(rows, order, mode)` | mode 0 = `dpwalk.sweep`, mode 1 = `audit_planted.rows_to_word` |
| `Base(word)` | `solve_max()`, `enum(thr, cap)`, `path(i)`, `word_of`, `eval(i)` |

- `count` counts, per line segment, the triangles using it. Z = unused segments (0 triangles), D = doubly used
  segments (2 triangles), and a bridge is a D segment whose two ends are both triple points.
- `canon_*` runs over the 8n images (4n end-circle symmetries × global sign flip). The tables come from
  `coverage.tables(n)`, but the C code is checked against `coverage.canon` byte for byte and independently against
  hand-derived symmetries (see below).
- `Base.solve_max()` + `Base.enum()` are one fused scalar-memo DP (`wc_prepare` / `wc_enum`). It enumerates exactly
  the paths of `dp1_enum` (allow4 = 0, canonical starts) in the same order, and needs no per-k tables.

## Validation (`test_walkc.py`, log `work/eng/T10/test_walkc.log`)
1,113 words (gallery n = 10–18: 10:69, 11:115, 12:19, 13:60, 14:49, 15:4, 16:314, 17:10, 18:473, plus bridge93 /
bridge16_heldout records; 512 have triple points; words with parallel pairs excluded).

| check | reference | result |
|---|---|---|
| A. `delete_line`, every line of every word (17,417) | `extend_dp.delete_wire` tokens; `delete_line.delete` on rows | equal |
| B. T | `quick_check.count_triangles` and `Arr` | equal (1,113) |
| B. (T, k, bridges, Z, D), per-line Z/D/incident Z | work/t3 `Arr` | equal |
| B. bridges | `test_k5L_layer.geometry(Arr)` | equal |
| B. Λ identity Z − D + 3k = n(n−2) − 3T | | holds |
| B. `rows_hash` | | invariant under commutation-equivalent words; same collision pattern as Python `hash(rows)` |
| C. `canon_bytes` | `coverage.canon` | byte-equal (1,113); hash = hash of those bytes |
| C. `canon_hash` under vertical flip, left-right reversal, both (3 × 1,113) | | invariant |
| D. `rows_to_word` mode 0 | `dpwalk.sweep` | token-equal (also failing on shuffled start orders) |
| D. `rows_to_word` mode 1 | `audit_planted.rows_to_word` | gens-equal |
| D. both modes | | round-trip to the same rows |
| E. 800 bases (1 or 2 lines deleted, n = 12–18): `solve_max` | `dpwalk.Base.best()` (dp1fast) and `dp1_solve_max` | equal |
| E. `Base.enum` at thresholds max, max−1, max−2 (2,400 enumerations) | `dpwalk.Base.paths` | same counts |
| E. fused `enum` | C `dp1_enum` | same count, path rows and start states, in order (2,400) |
| E. rebuilt word from the argmax path (unhinted) | `dpwalk.Base.word_of(seq, None)` | token-equal (800) |
| E. rebuilt word from enum paths (21,405) | `dpwalk.Base.word_of(seq, fid)` | token-equal |
| E. rebuilt words | | recount ≥ threshold |
| E. `Base.eval` (word, T, k, b, Z, D, hash) | `count` / `rows_hash` of the returned word | equal (21,405) |

**0 mismatches.**

## 5-minute run (3 workers, seed 1, n = 18, dpwalk.py start mix, `--audit 0.005`)
`work/eng/T10/run5*`.
- 860,498 moves (128,626 of them 2-line), 796,824 distinct states, best T = 93, no HIT.
- 3,974 audited states recounted with quick_check: 0 mismatches.
- `recount_records.py`: all **70,249** class rows (T ≥ 93; 64,190 distinct classes) recount to **T = 93** with
  quick_check, and k = number of multiple points. 15,988 records have k > 0 and 322 have bridges. 2,650 records are deep-checked (all bridged ones, 5% of the
  other k > 0 ones, 1,500 random ones): Arr (T, k, bridges, Z, D), the canon id
  `sha1(coverage.canon)[:16]` and `count_general` all equal. **0 mismatches.**
- The run reaches k up to 36 and up to 84 bridges. Those come from the archive-restart chains and were not checked
  for realizability. T6 had reported at most k = 21.
- Options exercised: `--n 16 --start gallery/16 --zprob 0.5 --wb 0.3 --wk 0.1 --zinc 0.5 --cand-score` (60 s, 2
  workers) and `--n 18 --start work/dpwalk/bridge93.json --zprob 0.5 --wb 0.3 --wd 0.1 --wz 0.05` (60 s). Their
  12,344 and 123 class rows all recount, deep-checked (`opts_check.txt`).

## Speed
**Walk throughput** (1 worker, 150 s, seed 3, same start mix, both run at the same time on an otherwise lightly
loaded 24-core box; exact moves/s/core, a move = a delete + DP + re-insert attempt):

| | moves/s/core |
|---|---|
| dpwalk.py (T6 code, dp1fast) | **116** (an earlier identical run: 136; T6's 54 was under load) |
| dpwalk_c, first version (K-table `dp1_enum`) | 607 |
| dpwalk_c, fused enum | **1,012** |

- **×8.7 (×7.4 against the 136 run).** The 3-worker 5-minute run gave 959/s/core.
- `--n 16` gives 1,504/s/core with Z-targeting (T = 72 records).
- Phase seconds for the 150 s run, from the stats file (`dp` = delete + graph build + scalar solve, `enum` = the
  fused enumeration, `eval` = rebuild + count + hash of up to 8 candidates):

| dp | enum | eval | record |
|---|---|---|---|
| 108.8 | 13.5 | 16.6 | 1.3 |

- **The walk is now bound by dp1fast2's graph build + DP (about 0.6 ms of the ≈1 ms per move); the Python glue is
  ≈5%.**

**Per primitive** (`bench_walkc.py`, n = 18 words, µs per call):

| function | Python | walkc | speed-up |
|---|---|---|---|
| delete_line | 86 | 1.8 | ×47 |
| count T (quick_check) | 176 | 10.4 | ×17 |
| count T, k, bridges, Z, D (Arr) | 238 | 10.8 | ×22 |
| canon hash (chi + 144 images) | 285 | 5.6 | ×50 |
| rows hash | 67 | 2.2 | ×31 |
| path → word + T + hash | 496 | 23.8 | ×21 |

The `rows_to_word` wrapper is only ×1.6 because Python builds the frozenset masks (the C sweep takes a few µs); inside
the walk `eval` does everything in C.

## Caveats
- Not ported: dpwalk2's `--pair-rate` two-line probe. The stats output has no held-out comparison (`--heldout`);
  the cls_w*.jsonl / stats_w*.json formats and canon ids are dpwalk2's, so dpwalk2's `stats --heldout` should work on
  dpwalk_c runs (not tried).
- The fused enum scratch and the `Base` enum buffer are global: one prepared `Base` at a time, one process per
  worker. `Base.enum` re-prepares transparently if another Base was prepared in between, but the path buffer is
  valid only until the next `enum` call (a benchmark bug of mine, fixed, showed this).
- `canon_*` needs complete arrangements (every pair crosses), like `coverage.vec`, and raises `ValueError`
  otherwise. Gallery words with parallel pairs (the `-k` directories) are skipped by `dpwalk_c.load_rows`.
  `count`, `delete_line`, `rows_hash` work on any word.
- `insert_path` without a `start` hint tries every (slot, direction) as `Base.word_of(seq, None)` does. dpwalk_c
  always passes the hint.

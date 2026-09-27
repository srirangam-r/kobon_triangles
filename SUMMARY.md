# Kobon triangles, 18 lines: where things stand

*Last updated 2026-09-27, 18:55 UTC. The live log with every scored run is `journal.html`.*

## The task

The hill `alejandrozu/kobon-triangles` asks for exactly *n* straight lines, given as
integer triples `[a, b, c]` for `a·x + b·y + c = 0`, arranged to form as many triangles
as possible that no other line cuts through (bounded triangular faces). The evaluator
counts with exact rational arithmetic. Each *n* has its own leaderboard, and the
default is 18.

## Results

| n | Score | How | Status |
|---|---|---|---|
| 18 | **93** | My own unseeded simulated annealing (no triple points) | **Official**: scored by AutoLab on the real hill (tree `7d3f1d91`, climb `srirangam-r/kobon-triangles-18`) |
| 18 | 93 | Exact certificate from the Utkin–Parpalak gallery (3 triple points) | Reproduced; local score only |
| 15 | **65** | My own unseeded annealing; 65 is the proven optimum | Local score only. The leaderboard refused the local report (its version hash is my frozen copy's, not the official one) |
| 18 | 16 | Hill baseline (18 tangents to a parabola) | Reference |

93 ties the best known result for 18 lines. No one has found 94.

## What the literature says

- **Simple arrangements (no three lines through a point): 93 is proven optimal.**
  Blanc (arXiv 0801.2845) shows at most ⌊n(n−5/2)/3⌋ triangles for even *n*, which is
  93 at 18 lines. The "94" in Wikipedia's table is an older bound for simple
  arrangements (Bartholdi–Blanc–Loisel).
- **So a 94 must have a point where 3 or more lines meet.** For that case the only
  bounds are 95 (Clément–Bader, an informal unpublished draft) and 96 (Tamura). It is
  open.
- A counting identity: 3T = n(n−2) − Λ, where Λ = (unused segments) − (segments shared
  by two triangles) + Σ over multiple points of k(k−2). For 18 lines, 94 means Λ ≤ 6.
  Every 93 has Λ = 9.
- Every known even-*n* record uses triple points (the gallery's 8, 10, 12, 14, 16, 20
  and 18). The gallery holds about 3,000 distinct 18-line 93s, with up to 8 triple
  points, and no 94. No SAT attempt at 18 lines has been published.

## Methods and what they showed

**Geometric search** (dev numbers are mine; official numbers come from the hill):

- Float simulated annealing over line angles and offsets. It reaches 65 at 15 lines in
  seconds and 93 at 18 lines in minutes, from random starts. It cannot make exact
  triple points.
- Exact moves that remove a line and try every line through two crossing points
  (these create triple points), then walks across equal scores and two-line moves.
  About 2,300 distinct 93s were visited with no 94. Every 93 found is a local maximum
  for one-line moves.
- Running now: exact annealing over those moves. It sometimes accepts 92/91 to leave
  the 93 plateau and prefers new lines through more crossing points.

**SAT models** (`search/kobon_sat.py`):

1. *Simple arrangements*: one sign per triple of slope-sorted lines (the standard
   signotope encoding). The triangle rule was derived from 20,000 real 4-line
   arrangements and matches the evaluator exactly on real ones.
2. *With triple points*: a 3-valued sign per triple (0 = concurrent). Real 4-line
   arrangements produce exactly 17 sign patterns, and those are the constraints. This
   is a relaxation of real arrangements, so "impossible" results transfer to straight
   lines. It finds 15 for 8 lines (which needs 2 triple points) and rules out 16.
3. *Defect budget* (`--defect K`), the fastest: each line's crossing order is explicit.
   On line r, line i's crossing comes before line j's (i < j) exactly when
   sign(sorted r,i,j) = −1. Consecutive pairs that are not triangle sides are capped at
   n(n−2) + 3K + C(K,2) − 3T, which holds for at most K triple points and no 4-fold
   point. The rotation symmetry lets line 0 be defect-free.

   | Case | Result | Time |
   |---|---|---|
   | 11 lines, 33 | impossible | 3.3 s (earlier models: unsolved after 20 min) |
   | 10 lines, 26, ≤2 triple points | impossible | 379 s |
   | 12 lines, 39, simple | impossible | 534 s |
   | 18 lines, 94, K = 0, 1, 2 | no answer yet | running since 18:29 UTC |

**Checkable proofs** (`search/cnc.py`): march_cu splits a formula into cubes, CaDiCaL
writes a DRAT proof for each, and drat-trim checks it. A final proof shows the cubes
cover every case. Example: 10 lines, 26 triangles, ≤1 triple point gives 190 cubes
plus coverage, all refuted and all verified.

## Honest assessment

- Solve time grows steeply with the defect budget. 18 lines needs budgets of 6 (no
  triple points, which only re-proves Blanc), 9 (≤1 triple point) and 13 (≤2).
  Without a better encoding or ideas borrowed from faster tools, a full proof is days
  of compute, not hours.
- Evidence so far leans toward 93 being optimal. Thousands of distinct 93s are known,
  no local move improves any of them, and the small-*n* pattern (Λ ≥ n/2 − 1 for even
  *n*) predicts 93. None of this is a proof.

## AutoLab notes

- For this hill a climb has no run step: AutoLab scores the committed files, and code
  only runs inside the agent's coding session. The agent works one experiment at a
  time, so rented machines never started (rental spend $0).
- `autolab pause` did not stop a session already in progress. Freeing the laptop took
  cancelling the experiments and detaching the node.
- The climb is paused and the laptop is detached from it. A spend guard releases
  rentals at $75 (systemd user timer `kobon-rental-guard`). The AutoLab agent's own cap
  is still $5; raising it has to be done on the dashboard.

## Reproduce

```sh
hills eval submissions/007-anneal-n18 -H kobon-triangles            # 93, local
uv run --no-project --with python-sat python search/kobon_sat.py 8 16 --nonsimple
uv run --no-project --with python-sat python search/kobon_sat.py 11 33 --defect 0
python3 search/structure.py submissions/005-gallery-n18/solution.json   # Z, D, triple points, Lambda
```

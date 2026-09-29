# A1: audit of search/extend2_dp.py (exact two-line extension)

## Verdict: SOUND (default path), with one robustness caveat. No counterexample found.

`search/extend2_dp.py` was not modified. Everything here is in work/eng/A1/. I read the code and did not rely on T1/REPORT.md.

## 1. Math review
- **Decomposition.**
  - T = T0 + G1 + G2 + I holds because triangles are face-local. I is a sum over base faces cut by both lines.
  - A face cut by only one line contributes 0 to I.
  - Two chords that neither cross nor touch give I_f <= [f is a triangle]. This is asserted per base face (`ok` in `interaction_bound`).
  - The only positive contribution besides shared triangles is the single L1×L2 crossing. It lies in one face interior ('cross'), or on a base edge, where it shows up as 'touch' in two faces (hence 2·touch).
  - A crossing at a base vertex would be a 4-fold point and is excluded by the model, so nothing is missed.
  - The brute force over chord pairs is over-inclusive: it ignores cross-chord line conflicts. That only enlarges Kx, so it is safe.
  - Chords ending at inf elements, offsets ±1 on shared inf or edge elements, and faces with several inf elements are all handled.
- **Bound.** T <= T0 + Kx + min(N1+G2, G1+N2) with N = G + D. Correct.
- **Two-case cover.** N_e + G_f >= X for the enumerated pair (e,f) in either order. If N_e < a then G_f >= X-a+1. Any integer a is valid, so the plan search over a is only a cost heuristic.
- **Thresholds.**
  - `condA` is G+D >= max(a, X-MG[f]) and G+f2f(D) >= X.
  - `condB` is G >= max(X-a+1, X-MN[e]) and G+f2e(D) >= X.
  - Both are implied by the cover and by max over d of (bestG_f[d] + min(D,d)).
  - `paths_gd` prunes with the exact per-D suffix table `byd`. No dead nodes, and no pruning of a feasible one.
- **Incumbent tightening.**
  - X is non-decreasing. A pair P with T_P > inc_end satisfies every threshold at every time, so it is never lost.
  - The shared-triangle filter (`S` mode) is exact: it counts triangle faces visited by both lines.
- **Rank pairs.** gaps[1]=r1, gaps[2]=r2-1, pgap[1]=r2, pgap[2]=r1 are right for r1=0, r2=n0+1 and adjacent ranks.
- **Wiring rebuild.** `rows_to_tokens` and `extend_graph` are consistent. The rebuilt word is relabelled by start position, and everything uses `start_face(gap)` on the rebuilt graph.

## 2. Evidence (all runs: 0 mismatches)
| test (script) | what | count |
|---|---|---|
| T1 `t1_random_brute.py` | pruned == unpruned brute force (all L1 paths × exact best L2) on random bases n0=5–10: random words, triangle-hill-climbed words, gallery minus 2 lines, mutations; 53 with triple points. Each rank pair run with warm on, warm off, target=max, max+1 (must be None), max-1, max-3, in shuffled order on a shared Base. | 200 bases, ~6,180 rank pairs, 37,060 checks (+6 bases in `t1_0_6`) |
| T2 `t2_sat.py` | pruned max vs fastext SAT (both orientations): SAT at max, UNSAT at max+1. n0=5–8, all pairs for n0<=6, 30 random plus the 3 edge pairs otherwise. | 353 bases (100 with triple points), 8,689 rank pairs |
| T3 `t3_lemma.py` | independent triangle recount (quick_check-style sets) of A+L1+L2, A+L1, A+L2. Checks I <= Kx + S, S <= min(D1,D2) and the full bound. Exhaustive over all (path1, path2) for n0<=6, top-plus-random samples above. Also exhaustive optimum vs `pair_search`. | 70 bases, 10,469,376 path pairs, 0 violations, 1,257 exhaustive optima all equal |
| T4 `t4_planted.py` | delete 2 lines from gallery arrangements (n=10–18); `pair_search(target=T_orig)` at the deleted ranks must reach it, with a witness recount. | 2,604 cases, 0 failures |
| T5 `t5_edge.py` | tiny bases n0=3,4 (warm path, max and target modes vs brute force); the 61 "T_orig+1 reachable" witnesses at n=11 and 13 recounted independently. | 4,500 checks, 61/61 correct |

- **T3 tightness.** The lemma is tight: max(I − S) = 2 = Kx, attained on real placements (max I = 5). So Kx is not padded.
- **T4 breakdown by n.** n=10: 120 cases, and the exact max also equals brute force. n=11: 150. n=12: 228. n=13: 300. n=14: 350. n=15: 96. n=16: 560. n=17: 240. n=18: 560.
  - The n=18 cases are n0=16 bases with T*=93 (tight).
  - n=17 has T*=85 and n=16 has T*=72.
  - For the known-optimal T_orig, T_orig+1 was unreachable in all cases (n=10, 12, 14–18). This is consistent with the records being optimal.

## 3. Caveats (robustness, not soundness)
1. **Crash when x is very negative.** `pair_search` unpacks `plan`, which is None when `range(max(1,(x+1)//2-2), (x+1)//2+3)` is empty (x = inc+1−T0−Kx <= −5).
   - `warm=False` in max mode always crashes. Reproducer: word `0 4 2 3 1 2 4 0 3 4 1 0 2 1 3` (n0=6), `pair_search(Base(word), 2, 5, warm=False)` → TypeError. All 7,412 no-warm max-mode calls in T1 crashed.
   - The CLI default (warm=True) never crashed in T1 or T5. A very low `--target` could still hit it.
   - Fix: `if plan is None: plan = (0, 1, 2, (x+1)//2)`. Or use `range(min(1, …), …)`, or clamp `a = max(1, …)` and always include one candidate. Any integer `a` is valid.
2. `interaction_bound` uses a bare `assert ok`. It would be skipped under `python -O`. It is only an assertion of the none-kind property, and it held on every base tested.
3. Scope of the guarantee: bounded triangles, no 4-fold points, bases without parallel pairs.
   - Gallery series with parallel pairs (e.g. `14-4`, `16-7`) were not tested. T4 used series without parallels.
   - The n0=16 exact-max mode was tested only in target mode, plus T1's report.

**Summary (≤200 words).** I found no false negative. The bound T <= T0+Kx+G1+G2+min(D1,D2), the two-case cover, the thresholds and the incumbent tightening are all correct. Kx=2 is tight (I−S reaches 2 in real placements). Evidence, all clean:
- T1: 37,060 pruned-vs-brute checks on 200 bases.
- T2: 8,689 SAT rank-pair checks on 353 bases.
- T3: 10.47M independently recounted path pairs, with 0 lemma violations.
- T4: 2,604 planted-deletion cases at n=10–18, including tight n0=16 with T*=93.
- T5: 4,500 tiny-base checks.

The only defect is a crash: `pair_search(..., warm=False)` in max mode, or a very low target, hits `plan=None`. It is a crash, not a silent wrong answer. Fix: fall back to a=(x+1)//2 when the range is empty.

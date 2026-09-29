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
- 00:47 Lineage n=12 bridge core (k6, beta6, T38) -> n=14 with T >= 54 (the n=14 record): **UNSAT for every 2-line placement** (21 min). The core does not survive at record level; that lineage stops.
- 01:29 Sampler (SAT-generate 17-line arrangements with T>=83, k=7, beta>=3, then one-line 94 completion): no first sample in 40 min. As with k5L, SAT cannot generate structured near-optimal 17-18 line arrangements from scratch. Stopped.
- 01:38 Queued: local top-17 bridge-preserving 16-line cores (after the n=16 extension); AutoLab d49b4f55 = next 60 cores (replaces the record-based e7d4e559). Reason: a 94's 16-line cores should have T16 ~63-66, like these, not the 72 records.
- 02:47 **AutoLab 6a4a8edf (k=6 seeds, 2-line re-placement): 10,231 / 12,261 calls, all UNSAT, 0 SAT** (150-minute deadline; 2,030 left; mean 26 s, max 317 s). Results committed on the AutoLab branch exp/autolab-.../6a4a8edf (b78ac35). The platform marked the experiment "discarded" (score unchanged), as expected. The first fetch of the files hit an HTTP 500; will retry.
- 02:47 Local: n=16 bridge extension 2,455 / 3,417 UNSAT; k=8 re-placement 848 / 3,417 UNSAT. Runner v2 (dynamic queue, single orientation) validated for correctness (93 control SAT), but its 94 calls look slow; diagnosing Blanc vs the symmetry break before the cores batch uses it.
- 02:52 **AutoLab fix:**
  - The first batch's seed commits came from a stale base with only .gitignore and push94/ (no submission/solution.json), so the evaluator hard-rejected them and the orchestrator raised "repeated_failures".
  - Re-seeded all queued experiments from the full tree (after `autolab pull`): 5bd1002f k=7 re-placement, 40546499 the 60 bridge cores, 2504f758 bridge-seed 3-line.
  - Told the agent via `autolab say` and resumed it.
- 02:52 **Runner lesson:** dropping the chi(0,1,2) != -1 break made placements with a new line among lines 0-2 about 40x slower (about 2,000 s vs 51 s). Kept the break (both orientations there). Kept the shared job queue. Re-validated: n=17 base at 94 gives 21/21 UNSAT, max 61 s.
- 02:52 Encoding A/B on extension calls (3 ranks away from 0-2): Blanc/break variants are all 27-42 s total, so Blanc is roughly neutral on extensions and 1.8x faster on re-placement.
- 03:10 Selector one-call test (201 placements, one n=16 seed): no answer after 3 h vs ~2 h for separate calls; abandoned. Reduced model (search/fastext.py): 720/720 agreement with the full model; 1.3-4x faster on hard 2-line calls (solve-dominated).
- 03:27 Engineering push: 5 headless Sonnet 5.5 workers (T1 exact two-line DP, T2 compiled one-line DP, T3 solver benchmark, T4 local-search generator, T5 realizability); briefs in work/eng/. New runner run_ext_fast.py (reduced model): n=17 control 21/21 UNSAT, mean 2.4 s (vs up to 61 s). k=8 run paused (resumable) to free cores.
- 03:28 AutoLab paused: rented nodes repeatedly failed workspace prep (node_unhealthy); queued experiments used the old slow runner. Cancelled them, rentals stopped (compute spend ~$4). Will resubmit with the fast runner if remote compute is still useful.
- 03:45 T2 done (Sonnet 5.5, $0.75): compiled one-line DP search/dp1fast, exact vs Python on 740 cases, ~27x faster (~6 ms per 17-line base). **Sweep: 44,547 distinct near-optimal 17-line arrangements (T 82-85, from T4's local search) completed exactly by one line: max 93, never 94** (60 s on 6 cores). T4 ended early (headless); relaunched as T4b to scale the generator plus sweep.
- 03:47 Held the SAT cores batch (chain2) so the cores go to DP-based work: T1's exact two-line DP should do it far faster. Fallback: run_lns_fast/run_ext_fast (the fast LNS control passed, 153/153 placements reach 93). Launched T6 (Sonnet 5.5): exact DP ruin-and-recreate walk at n=18.
- 04:07 **Coverage measured (capture-recapture + external check):**
  - First generator run: 3 chains, band T >= 82: 39,042 classes up to symmetry; Chao1 64k (coverage 0.61, LP 0.80-0.88).
  - Calibrated at T=85: the 255-word perfect-17 census = 10 classes, all 10 found.
  - **But of the 1,150 real 17-line cores of the gallery 93s (T17 80-84) the generator had sampled only 6.1% (84), 2.9% (83), 0% (82-80).**
  - So the generator's basin misses where real cores live: implied P(detect a 94) ~ 1.5%.
  - Fix in progress: 3 chains seeded from 575 real cores; reach is measured on 575 held-out cores (search/reach.py).
- 04:12 **Approach re-think:**
  - By the D-count a 94 needs Λ = 6 against Λ = 9 for every known 93, so it needs about 3 or more doubly used bridges. Bridges are essentially absent from the known 93s (3/2,376 have one).
  - So record neighbourhoods and "reach of 93-like cores" target the wrong region. The held-out 93-core metric (~1.9%) measures the wrong distribution.
  - Bridge-rich optima do exist nearby: n=12 (6 bridges), n=16 (17 records with bridges, up to 4).
  - **New plan:**
    1. Calibrate a bridge-biased generator at n=16: start only from bridge-free records, hold out the 17 bridge records, measure reach.
    2. Map the frontier T_max(beta) at n=17/18 with bridge-biased generation plus exact one-line DP completion, and the DP walk with a bridge bias.
    3. Decide on the frontier: if bridge-rich n=18 arrangements plateau well below 93, a 94 is implausible; if bridge-rich 93s appear, concentrate there.
- 04:13 **T1 done (Sonnet 5.5, $3.86): exact two-line extension, search/extend2_dp.py.** Branch-and-bound over first lines plus exact second line by the one-line DP. Validated by brute force (n0=6,8), SAT on both sides (132 checks, n0=9-12) and witness recount. Target-94 mode: 0.1-0.9 s per rank pair (~100-300x faster than SAT).
  - All 17 bridge-carrying n=16 records x 153 rank pairs: no 94.
  - **Exact 2-line max from an n=16 record is only ~88-89 (+17 on 72)**: records are rigid, confirming record-based extension is the wrong family.
- 04:13 93-core-seeded generator chains: held-out reach ~0% (seeding alone does not move the basin); superseded by the bridge-family plan. T3 (solver bench) and T5 (realize) died of OAuth expiry; T3 is superseded by the DP tools, T5 deferred until a hit exists.
- 04:26 **Calibration at n=16 FAILED for the flip-based generator (pls.py, bridge bonus 1.0):** frontier bridges>=1 tops at 71 and it never found any of the 17 known bridged 72s (0/17). Its n=17/18 frontier chains stopped as uninformative.
- 04:26 **Planted audits pass:** one-line DP 300/300, two-line solver 20/20 (0 false negatives at n0=16/17). Independent auditor A1 (Sonnet 5.5, --effort high) is checking the two-line pruning argument.
- 04:26 **Key finding, T6's exact DP walk (delete a line, exact best re-insertion) at n=18:** ~50 exact moves/s/core, **30,824 distinct 93s** (gallery: 3,016), best 93, never 94.
  - Includes **198 bridge-rich 93s** (>= 3 bridges): families (k,beta) = (21,39) x18, (20,36) x14, (19,32-36) x17, (18,31), (15-17, 24-28), (7,12) x63, (8,12) x20, and more.
  - So bridge-rich 18-line arrangements DO reach 93, and the search concentrates there.
- 04:26 Running: exact 2-line same-rank sweep over all 153 deleted pairs of the 198 bridge-rich 93s (work/b93/, ~0.05 s per core).
- 04:39 Stopped T4b (flip-based generator improvements) and its run: that generator failed the n=16 calibration and the exact DP walk supersedes it. Samples so far are kept in work/pls/.
- 04:52 T6 done ($0.66): 584,656 exact moves (54/s/core), 543,630 distinct states, 56,044 93-words, no 94 via any 1-line or greedy 2-line move. Launched T9 (Sonnet 5.5, effort high): bridge/Z-targeted calibrated DP walk (n=16 held-out bridged 72s first, then 8-chain n=18 production with capture-recapture).
- 04:53 **Bridge-rich 93s, exact 2-line re-placement at the same ranks: all 153 pairs x 198 seeds = 30,294 cores, 0 reach 94.**
- 05:18 **Realizability** (search/realize.py; exact chi reproduction plus the hill counter):
  - Gallery control (k=5) realized.
  - **Bridge-rich 93 with 7 triple points and 12 bridges REALIZED by 18 integer lines**: hill eval count_triangles = 93, exactly 7 triple points (work/realize/k7b12.solution.json). A new straight-line 93 family; no public 93 has more than 1 bridge.
  - The (21 triple points, 39 bridges) 93 was not realized in 21 min (inconclusive).
- 05:18 T9 calibration trial A at n=16: the new walk found 32 bridged 72 classes it was never shown (k 5-11, up to 14 bridges) and 1/17 held-out. The old generator found none. T8's C ports are in validation: planted audits clean, 100-500x on two-line exact max; 4 C-vs-Python mismatches at n0=11 under investigation (tools not switched yet).
- 05:29 **A1 audit (Sonnet 5.5, effort high, $2.34): search/extend2_dp.py is SOUND.** 37,060 pruned-vs-brute checks, 8,689 SAT-verified rank pairs, 2,604 planted cases (560 at n=18) and 4,500 edge checks: 0 false negatives. Only bug: a crash with warm=False or very low targets, never on the default path used here. The 4 C-vs-Python mismatches in T8's testA must therefore be in the C port; T8 is still validating, and the C tools are not adopted until resolved.
- 05:54 **T8 done ($4.07): C face-graph builder + C two-line solver adopted** (search/dp1fast2/, search/extend2_fast.py). 0 mismatches vs Python (the earlier 4 were bases with parallel pairs; the DP tools need --complete there, a no-op otherwise). Planted audit 1,000 one-line + 160 two-line, all >= 93. Two-line all-rank per n0=16 core 0.43 s (x62); one-line x6 vs dp1fast. All-rank sweep of bridge-rich cores: 21 pairs finished in Python (0 hits); the remaining 132 now run in C with --complete.
- 05:56 **All-rank 2-line sweep of the 198 bridge-rich 93s complete: 30,294 cores x 153 placements (about 4.6M exact placement checks), 0 reach 94, 0 errors.**
- 11:30 Realizability map: 7/15 bridge-rich families realized by integer lines: (6,3) (7,4) (8,3) (8,4) (8,12) (9,3) (9,4), plus (7,12) earlier. All high-k families (15-21 triple points, 24-39 bridges) and (9,7) failed in 20 min. The geometric bridge-rich region is k = 6-9 with 3-12 bridges.
- 11:30 T9 and T10 died on the account session limit. T9's calibration: best trial calE rediscovered 4/17 held-out bridged 72s and found 52 new bridged-72 classes (the old generator found 0).
- 11:30 **T9 production (8 chains x 60 min at n=18, about 1.4M exact moves): no 94.** Capture-recapture: 93 classes 26,206 seen (Chao1 133k, coverage 0.20); **bridge-rich 93 (b>=3): 126 seen, Chao1 137, coverage 0.92; realizable range (k 6-9, b>=3): 94 seen, Chao1 98, coverage 0.96.** The reachable bridge-rich plateau is small and nearly exhausted, so no GPU is needed. The remaining risk is reach: n=16 held-out reach was only 4/17.
- 11:34 **All-rank 2-line sweep of T9's 126 bridge-rich 93 classes: 19,278 cores x 153 placements, 0 reach 94, 0 errors.** Total so far: ~49.6k bridge-rich cores, ~7.6M exact placements.

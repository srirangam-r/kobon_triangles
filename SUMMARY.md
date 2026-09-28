# Kobon triangles, 18 lines: where things stand

*Last updated 2026-09-27, 23:10 UTC. The live log with every scored run is `journal.html`.*

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

## New result: no 94 with at most one triple point (21:10 UTC)

**Claim.** An arrangement of 18 lines has at most 93 bounded triangular faces if it has at
most one point where three lines meet and no point where four or more meet. The same holds
for pseudolines. Parallel lines are allowed, as long as no three are mutually parallel.

With no triple point this is Blanc's theorem (arXiv 0801.2845, Cor. 2.0.5). The case of
exactly one triple point is new, as far as we can tell. The argument extends Blanc's
Prop. 2.0.4. It was extracted from the paper by a subagent, re-derived step by step here,
and checked without counterexample on 7,264 exact perturbations of real arrangements
(`work/blanc/`). It has not yet had an outside check.

*Proof sketch.*

1. **No parallels.** A projective map that sends a generic far-away line to infinity keeps
   every bounded triangle and turns parallel pairs into ordinary crossings.
2. **Counting.** With one triple point P (lines a, b, c) there are 285 bounded segments.
   Counting triangle sides gives 3T = 285 − Z + D. Here Z counts unused segments (sides of
   no triangle) and D counts segments that are sides of two triangles. So T ≥ 94 needs
   Z − D ≤ 3.
3. **Doubly used segments.** Two triangles can share a side only if one end of that side is
   P. Then the side is the first segment of one of the six rays at P, and a single line
   ("cap line") is the first to cross three consecutive rays. Such blocks of three rays
   cannot overlap, so D ≤ 2. There are exactly D cap lines.
4. **Clean lines.** Call a line *clean* if it avoids P and is not a cap line. There are at
   least 15 − D clean lines.
5. **Blanc's argument works for clean lines.** Every crossing on a clean line L is simple,
   and no segment next to L is shared by two triangles.

   Suppose every bounded piece of another line next to L were a triangle side. Record, for
   each segment of L, whether the triangle on it (if any) is above or below.
   - The two end entries are empty.
   - No two empty entries are adjacent.
   - "Triangle, empty" forces "triangle, empty, triangle" on the same side.
   - Neighbouring triangles alternate sides.

   Because 18 − 3 is odd, the first and last triangles land on opposite sides. That forces
   the two outermost crossing lines to lie entirely on opposite sides of L, so they could
   not cross each other. This is a contradiction. So L meets an unused segment at one of
   its endpoints.
6. **Each unused segment is claimed at most twice.** A clean line claims a segment at one of
   the segment's endpoints. A simple endpoint lies on only one other line, and lines through
   P are never clean. So each unused segment is claimed by at most 2 lines.
7. **Conclusion.** Z ≥ ⌈(15 − D)/2⌉, so Z − D ≥ 8, 6 or 5 for D = 0, 1 or 2. Every case
   exceeds 3, so T ≤ 93.

For two triple points P and Q the same counting leaves two rigid cases (corrected 21:25 UTC;
an earlier version wrongly said only case A survives):

| Case | Structure | D | Z | Clean lines |
|---|---|---|---|---|
| A | P and Q share no line; 4 distinct cap lines | 4 | 4 | 8, whose claims pair up exactly on the 4 unused segments |
| B | P and Q consecutive on a common line m, with segment PQ a side of two triangles; up to 4 cap lines | 5 | 5 | 9 |

If P and Q share a line but are not consecutive on it, then D ≤ 4 and Z ≥ 5, which rules
that configuration out.

**Both cases are ruled out by hand (refereed 23:10 UTC).** Full proof: `work/proof_k2.md`.
- **Case A:** each triple point with two cap blocks has an *axis*. That is the line
  carrying the two middle rays, and by Blanc's parity argument it also claims an unused
  segment. The axes add 2 claimers to the 8 clean lines, so Z ≥ 5 > 4 ≥ D.
- **Case B** (the referee's simpler argument): each point has a cap block whose cap line
  passes through the other point. So at least 2 cap lines are triple lines, clean ≥ 11,
  and Z ≥ 6 > 5 ≥ D.

Correction: an earlier version of this section said each triple point has two
*disjoint* blocks covering all 6 rays, and that case B forces 5 triangles at each point. The
referee found both false in case B: P's two blocks can overlap on the ray toward Q, and it
built explicit examples. The `--case2 B` SAT deductions that relied on those statements have
been removed; the SAT runs had been stopped anyway.

**Generalization (same argument, any even n):** with at most one triple point,
T ≤ ⌊(2n² − 5n + 2)/6⌋.
- For n ≡ 0 or 4 (mod 6), this equals Blanc's simple bound, so one triple point never
  helps.
- For n ≡ 2 (mod 6), it allows one more triangle than Blanc's simple bound. That matches
  the known records that beat the simple bound (8/15, 14/54, 20/117), all of which have
  n ≡ 2 (mod 6) and use triple points.

## Toward the full problem (23:00 UTC; not refereed)

- **What remains.** In general position, Λ ≥ (18 + 3t₀ − 2t₂)/2, where t₂ counts triple
  points with two cap blocks ("full") and t₀ those with none. So a 94 needs at least 3 full
  triple points, each contributing −1 net to Λ. A full proof needs a lemma making each full
  triple point net ≥ 0.
- **Per-line parity rule (corrected by the referee; see `work/loop/verdicts/C06.md`).**
  - *My original statement was false as stated*: it counted all triple points and had
    missing hypotheses. The referee found counterexamples among real 18-line 93s.
  - *Corrected rule.* Assume L has no doubly used segment, no 4-fold point, simple first and
    last vertices, κ(L) = 0, and every segment at L's triple points used. Then K + j_alt is
    odd, where K counts the blocks L caps and j_alt counts the triple points where L's
    triangles alternate sides.
  - This is equivalent to the generator's C11 (Lemma D), which C12 uses.
  - Both consequences stated earlier (a non-triple line capping two blocks claims; a
    non-axis line through one full triple point capping exactly one block claims) are
    correct.
- **The rigid tight configuration** (general position, t₂ = 3):
  - three triple points on disjoint lines;
  - T = 94 exactly, D = 6, Z = 3;
  - six single-block cap lines;
  - three clean lines and three axes, each claiming exactly once, with every unused
    segment claimed from both ends.

  Ruling it out, plus t₂ = 4–6, shared-line clusters and 4-fold mixtures, would complete
  the proof. The last step would be to encode each rigid configuration exactly and let the
  solver exhaust it.

## Three triple points: refereed, CORRECT with two steps spelled out (23:20 UTC)

A subagent reports a hand proof that three triple points also give T ≤ 93, in every
sub-case (`work/t3/notes.md`).

- **Credit framework.** Count unused-segment endpoints: 2Z = Σ_L κ(L) + Z_tr.
- **Lemma A (cap touch).** At each full triple point, the axis segment just beyond the cap
  point is unused unless a "mutual pair" occurs. Its endpoint belongs to the cap line, which
  never claims, so it gives an extra credit. This kills the rigid t₂ = 3 configuration.
- **Lemma B.** Doubly used segments between triple points occur only in a special
  triangle-of-triple-points configuration.
- **Also claimed:**
  - any number of triple points on pairwise disjoint lines (up to 6);
  - any number all on one shared axis line.
- **Where it stalls:** 4 triple points in a "two mutual pairs" configuration.
- **Tests:** no failures on 5,516 gallery arrangements and about 1,000 random three-triple-point
  arrangements.
- **Status:** independent referee: correct. Two steps must be written out, and the
  referee's arguments for them are in `work/t3/notes.md`. Tested on 100,214 eighteen-line
  arrangements with exactly three triple points, with zero failures.

## Theorem H (general position): refereed, CORRECT (23:25 UTC)

**Claim.** At n = 18, T ≤ 93 for every arrangement in which no line contains two multiple
points, whatever the number of triple points and whatever 4-fold or higher points it has.

**Argument.**
- The master inequality is 2Λ ≥ n + Φ.
- Lemma A for any multiplicity: in general position it is never "killed".
- This gives Λ ≥ ⌈(n − t + 2q)/2⌉, where q counts points of multiplicity 4 or more.

**Cases at n = 18.**
- t ≤ 5: Λ ≥ 7.
- t = 6: a 94 forces Z = 0, which Lemma A contradicts.
- t ≥ 7: too few segments remain.

**Status.** Write-up: `work/t3/general.md`.
- Independent referee: correct, checked by hand.
- The author tested 16,208 general-position arrangements with no failures.
- The 4-fold-point values were hand-checked only; no one has tested them on arrangements.
- Referee strengthening: at t = 6 every line passes through a triple point, so Z ≥ 3; and
  t ≥ 7 is impossible in general position, because Σk_P ≤ 18.

**Remaining open (corrected 23:30 UTC; the earlier "4–6" was wrong).** Arrangements with 4 or
more triple points where some share a line, and 4-fold or higher points sharing lines.
- 7+ triple points are impossible in general position (3t ≤ 18), but possible with shared
  lines. There the segment bound 3T ≤ S + D = 288 − 3t + 2t + β requires β ≥ t − 6 bridges
  (doubly used segments between two multiple points). Lemma B restricts bridges strongly,
  but t ≥ 7 has not been analysed.
- Such clusters are real: gallery 93s have up to 8 triple points on shared lines.

The open cases include those where:
- a triple point is killed by mutual pairs (R1);
- an axis passes through another triple point (R2);
- a triangular face has three multiple-point vertices (R3).

The stalled 4-point case is exactly characterized and falls short of 7 by one:
- P1 and P2 are consecutive on a line m, and P3 and P4 on a line m′;
- the private axes form mutual pairs;
- x = 4, D = 8.

A 94 there would need Z = 2, with each unused segment claimed from both ends by 4 clean
lines. This is a well-defined candidate for an exhaustive solver run.

## Shared-line clusters: partial, NOT refereed (23:45 UTC)

- **t ≥ 7 triple points** (`work/t3/shared.md`). A 94 needs
  Σ_P [b(P) + e(P)/2 − 2] ≥ t − 6 + Z ≥ 1, where b(P) counts blocks at P and e(P) counts
  bridge ends at P. Lemma C bounds each point type's contribution. So t ≥ 7 is impossible
  when:
  - there are no doubly used bridges; or
  - there are no bent points, no centroid-type points, no triangular faces with all vertices
    multiple, and no point with 3 or more bridge ends.

  Mixed configurations of bent pairs and all-multiple triangles remain open.
- **Data.** Every gallery arrangement with t ≥ 7 has zero bridges, including the 57
  eighteen-line ones with t = 7 or 8. In the 8-triple-point 93s, mutual pairs cancel Lemma A
  at every axis point, so mutual pairs are common in real arrangements.
- **Solver on the stalled 4-point case** (assuming the refereed theorems):
  - the whole instance timed out at 600 s;
  - 5 of 20 random line-0 cases were UNSAT in 0.4 s, and 15 timed out at 600 s;
  - no SAT was found.

  It is not quickly decidable.

## Solver on the open shared-line space (23:44 UTC)

Assuming all theorems (refereed and not), the solver was given:
- exactly k triple points for k = 4, 5, 6, with at least one shared line;
- line 0 off every triple point;
- the Blanc claims, the opposite-sides rule and the defect budget;
- two new budgets:
  - unused simple segments + lines through triple points ≤ 6 + 2k;
  - claims + 2·(lines through triple points) ≤ 12 + 4k;
- for k = 4, only the open two-pair pattern, with Z ≤ 2 and claims ≤ 4.

**Result:** all 22 completed jobs timed out at 300 s (whole instances under both Kissat
modes, and 16 non-trivial line-0 cases). No SAT was found. The constraints do not yet shrink
these instances enough. The next step is theory: exact credit analysis for 5 and 6 triple
points, and a bidirectional encoding of "touches no unused segment" for k = 4.

## Decoupled loop, rounds 3–8 (2026-09-28, 00:45 UTC)

The generator proposed C10–C25, and the verifier refereed C6–C18. Verdicts are in
`work/loop/verdicts/`, and the ledger (`work/loop/ledger.md`) is authoritative.

**Refereed since the last update.**
- *Correct:* C10 (Lemma A as a clause), C11 (Lemma D, parity through triple points), C12
  (the k = 4 two-mutual-pairs pattern is impossible), C13 (axis parity), C14 (k = 5, 6 with
  β = 0 force Z = 0 structure), C16 (k = 6, β = 0 leaves only u ∈ {4, 6}) and C17 (mutual
  line ends are slope-adjacent "wedges at infinity").
- *Fixed:* C6 (parity rule), C7 (bent-point bound), C8 (holds only for β = 0), C9 (budgets
  true, with a new proof), C15 and C18.
- **New refereed consequence: no 94 with exactly 4 triple points and no doubly used bridge
  (β = 0)**, from C8 and C12.

**Refereed (01:10 UTC): no 94 with exactly 4 triple points, for every β (C25).** With k ≤ 3, this closes 0–4 triple points (no 4-fold points). C25's ingredients are listed below. The verifier flagged five SAT variants in C19–C23 as unsound; C25 does not use them, and none is encoded.
- C19: no bridge triangle through a bent point.
- C20: credits from unused first segments.
- C21: at most two bent points per partner.
- C22: no back-ray bridge.
- C23: the case list, with Lemma K4 (four triple points cannot be pairwise consecutive).
- C24: all-multiple faces.
- Also: C18 (fixed) shows **k = 5, β = 0, B = 9 has no 94**. Only B = 10 remains for k = 5, β = 0.
- **C26/C27 (proposed):** rigidity of the singleton ends, and a sector lemma. Together they cut C16 (A) from 3,668 wedge cases to **32** (recounted independently: 32).

**Solver on k = 6, β = 0** (all encoded claims refereed: C5, C10, C14; C16/C17 for the
split).
- *k6z, line-0 prefix splitting:* stopped at the budget after 19 minutes. 169 cases were
  UNSAT, 0 SAT, and 6.9% of the space was closed. Timeouts persisted down to depth 5, and the
  projection was over 100 h.
- *k6z2 = k6z + C17 clauses* (`search/build_k6z.py --c17`): little gain alone. 1 of 16 k6z
  timeouts closed.
- *Wedge cubes* (`search/wedge_cubes.py`).
  - By C16 and C17 every line end is either one of u ∈ {4, 6} cap-point ends or a wedge
    with its cyclic neighbour at infinity. Choosing the cap-point set S therefore fixes all
    36 line ends.
  - The admissible S, with line 0 off the triple points, give a complete split into
    **4,118 cases** (450 with u = 4 and 3,668 with u = 6).
  - The position conventions were checked against 9 exact arrangements (3,996 first/last
    literal checks, 113 mutual ends).
  - Pilot: 8 of 16 random cases UNSAT in about 2 s; the other 8 timed out at 150 s and again
    at 300 s.
  - Adding τ counts (C16) and "the line of each cap-point end is a triple line" (k6z3) did
    not help the hard cases.
  - *Splitting a hard case one line-0 crossing deeper* gave the same pattern: 8 of 16
    children UNSAT in about 2 s, and 8 timed out at 150 s. The easy half is refuted by
    propagation; the hard half needs real search at every level. So a full run is not in
    budget, and the next gain has to come from theory: closing C16 (A)/(B) by hand, or new
    structure that fixes the axes and mutual pairs from S.
  - `search/cube_runner.py` (incremental CaDiCaL under assumptions, loading the formula once
    per worker) is ready for when the instance gets smaller. It has not been run yet.

## k = 6 triple points, β = 0: closed (solver, on refereed claims; 02:05 UTC)

The claims used are all refereed-correct: C5 (line 0 off the triple points), C10, C14 (Z = 0 structure),
C16 (u ∈ {4, 6}), C17 (wedges), C26 (singleton rigidity) and C27 (sector lemma).
- **Split.** `search/wedge_cubes.py` fixes all 36 line ends at infinity by the singleton set S, giving
  4,118 cases.
- **u = 6, sub-pattern (A).**
  - C27 kills 3,636 of the 3,668 sets outright.
  - Of the 32 left, the 16 with min S even contradict the 180° symmetry break χ(0,1,2) ≠ −1 at once:
    line 0 would meet line 1 first. All 16 were solver-checked UNSAT (about 2 s each).
  - The 16 with min S odd, with C26 (c) encoded (`search/wedge_cubes_c26.py`, one matching each), are
    all UNSAT in 5–24 s.
- **u = 4, sub-pattern (B): closed by hand**, C28 + C29 (both refereed-correct). No admissible 4-set
  pairs its singletons at cyclic distance ≤ 5.
  - **Correction:** an earlier "225 (B) cubes UNSAT in about 2 s" solver result was **invalid**.
    `wedge_cubes_single.py` numbered its new variables from the known ids, not from the k6z3 header nv,
    so they collided with k6z3's C16 counter auxiliaries. The verifier's audit found this
    (`work/loop/verdicts/AUDIT_k6z.md`).
  - Fixed: all generators now start after the base header nv, and `wedge_cubes_c26.py` asserts u = 6.
    With correct numbering the (B) cubes take minutes each (9 of 225 re-run by the verifier, all UNSAT).
    The rerun is not needed, since (B) is closed by hand.
  - The 225 min-S-even (B) cubes (plain k6z2, no new variables) are valid and UNSAT.
- **Audit** (`AUDIT_k6z.md`): symmetry breaks, the cube cover, the build_k6z base, and the wedge_cubes /
  wedge_cubes_c26 clauses are sound. On 721 real axis-end configurations there were 0 failures.
  - (A)'s 16 C26 sub-cubes were re-run by the verifier: UNSAT in 3–12 s.
- **DRAT: all 257 valid k6z solver cases are DRAT-verified** by drat-trim (the 32 (A) cases and all
  225 even (B) cases), each check ≤ 39 s. Logs: `work/k6z2/drat_all.jsonl`, `drat_B_even_rest.jsonl`.
- **What is left for k = 6:** β > 0 (doubly used bridges).

## k = 5 triple points, β = 0, B = 10 (03:20 UTC)

Refereed-correct: C30 (Z = 0 impossible; Z = 1 splits into four rigid sub-cases) and C31 (clean = 2
dead; clean ≤ 1 with K = 4 leaves 48 end patterns, 32 avoiding positions 0 and 18).
- **Instance.** C32 spec (proposed), built by `search/build_k5.py` into work/k5/k5.cnf (1.66M
  variables, 8.64M clauses).
  - It adds one slack s = u₀ with Σs = 1 and guards, type X at every triple point, Σ clean ≤ 1,
    11 ≤ τ ≤ 13, and C17 with Statement 2 weakened at u₀.
- **Cases.** `search/k5_cubes.py` makes one cube per C32 (c) row: 192 rows over 32 end sets.
- **Result:** **all 192 cubes are UNSAT and DRAT-verified** (median 2.5 s, checks ≤ 9 s; log
  `work/k5/drat_k5.jsonl`). The base alone times out at 200 s.
- **Audit:** `work/loop/verdicts/AUDIT_k5.md`.
  - Every base clause and per-row unit is a necessary condition. There were 0 failures on 670 real
    configurations with the solver's own literal semantics.
  - The numbering is clean, and the verifier regenerated the same 192 rows independently.
- **C32 (d), the clean = 0, K = 3 shared-axis configuration: killed by hand**, C33 (refereed-correct),
  using C11 on the second mutual line.
- **So k = 5, β = 0 is closed:** B = 9 (C18), B = 10 with Z = 0 (C30), clean = 2 (C31), the 192 cubes,
  and C33.

## Where things stand (03:50 UTC)

**Closed, with refereed arguments and DRAT-verified solver steps:**
- 0–4 triple points (no 4-fold point);
- general position, any number (Theorem H);
- 5 triple points with β = 0;
- 6 triple points with β = 0.

**Open:**
- 5 or 6 triple points with a doubly used bridge (β > 0);
- 7+ triple points (these need ≥ t − 6 bridges; Lemma C covers part of it);
- 4-fold points on shared lines.

The generator's C34 collects the β > 0 toolkit. The next step is a C25-style case tree for k = 6,
β > 0.

## Next steps for a future session

1. Read the fast referee's verdict on the three-triple-point claim and fix any gaps.
   `work/referee3/` has its notes; `work/t3/notes.md` has the claim.
2. Four triple points: the credit framework stalls at "two disjoint consecutive pairs, each a
   mutual pair" (x = 4, need = 1, no credit found). Try a hand argument first. If it
   resists, encode exactly that configuration with all proven structure (cap blocks, claims,
   credits) and let the solver exhaust it. That instance is small and rigid, which is the
   only kind the solver handles well.
3. Generalize Lemma A/B credits to any number of triple points and to 4-fold points (net
   charge ≤ −2 each, so they only add slack), then referee.
4. Formalize the counting and parity core in Lean. The geometric lemmas L1–L4 become explicit
   hypotheses.
5. Do not restart brute-force runs on the full 18-line problem. Every estimate was days or
   more.

## Partial results: where a 94 cannot be (updated 23:10 UTC)

None of these is a full proof that 94 is impossible. Each rules out one class of arrangement.
"Referee" means an independent subagent that checked the argument and tested every lemma
on exact arrangements. There has been no human review and no formal (Lean) check. Treat
these as carefully argued drafts, not published results.

| Class | Result | How | Checked |
|---|---|---|---|
| Simple arrangements (no triple points) | ≤ 93 | Blanc's theorem (literature) | Published |
| **Exactly one triple point** (no 4-fold points) | **≤ 93** | **New: Blanc's lemma extended to clean lines, plus D ≤ 2 (see above)** | Hand proof; independent referee subagent: correct; 142,160 arrangements tested |
| **General position** (no line through two multiple points), any number of triple and 4-fold+ points | **≤ 93** | **New: Theorem H, `work/t3/general.md`** | Referee: correct (hand-checked); 4-fold cases untested empirically |
| **Exactly three triple points** (no 4-fold points) | **≤ 93** | **New: credit framework (Lemma A cap touch, Lemma B); `work/t3/notes.md`** | Referee: correct with two steps spelled out; 100,214 arrangements tested |
| **Exactly two triple points** (no 4-fold points) | **≤ 93** | **New: axis lemma (case A) and cap lines through the other point (case B); `work/proof_k2.md`** | Hand proof; referee: correct after one fix; 17,038 two-triple-point 18-line arrangements tested |
| **Exactly four triple points, no doubly used bridge (β = 0)** (no 4-fold points) | **≤ 93** | **New: C8 characterizes the only surviving pattern; C12 kills it with Lemma D (C11)** | Referee: C8 correct after a fix (β = 0 only), C11 and C12 correct; 173,381 lines tested for C11 |
| **Exactly four triple points, any β** (no 4-fold points) | **≤ 93** | **New: C25 = C8 (β = 0) + C12 + centroid case + C23 (Lemma K4) + C24 + C19 (k = 4 form) + C21 + C22** | Referee: correct, checked by hand end to end; accounting inequality held on 2,981 k = 4 arrangements (min slack 3); the rarest configurations were hand-checked only |
| Five triple points, β = 0, exactly 9 blocks (B = 9) | ≤ 93 | C18 (fixed) plus C11 on the shared line | Referee: correct after a fix (found while fixing C18) |
| **Any number t of triple points, in general position** (no line through two multiple points), even n | T ≤ ⌊(2n² − 5n + 2t)/6⌋; so 94 at n=18 needs 3 ≤ t ≤ 6 | **New: Theorem G, `work/proof_general.md`** | Referee: correct; Λ ≥ n/2 − t tested on 82,975 arrangements |
| A 94 whose deletion of some line leaves a *perfect* 17-line arrangement (85) | none | Exact one-line extension DP over all 255 perfect 17-line wiring diagrams, triple points allowed | DP validated against brute force and known optima; one base cross-checked with an independent exact counter |
| One line away from any of the 3,016 known 93s | none | The same DP: every line of every gallery 93 deleted and re-inserted optimally (54,288 cases, all give 93) | As above |
| One specific 16/72 base plus any 2 lines | none | SAT at all 153 slope positions, triple points allowed | Solver answer; no DRAT proof yet |

The SAT model behind the last row is checked for soundness. Seven real arrangements with
triple points (8/15, 10/25, 12/38, 14/54, 16/72, 18/93, 20/117) and a second 18/93 with
4 triple points (from parpalak's fork) all satisfy it.

## Honest assessment

- 21:10 UTC update: "no 94 with ≤1 triple point" is now settled by hand (section above),
  which makes the SAT run for it unnecessary. The text below is the earlier status, kept
  for the record.
- Proof track closed (20:30 UTC). The smallest new theorem in reach would have been "no
  94 with ≤1 triple point", and a feasibility sample ruled it out. Split into 4,096
  cases, 0 of 8 sampled cases were solved within 8 minutes. Split into 65,536 cases,
  6 of 8 still timed out. That puts a checkable proof above about 11 days on all 24
  cores, and a full proof is further away still. The split-proof and small-n runs
  serve only as validation: they re-prove known theorems (Blanc and others), which is
  not a new result.
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

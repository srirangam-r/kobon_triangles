# Audit: k = 6, β = 0 solver encoding (build_k6z.py, wedge_cubes.py, wedge_cubes_c26.py, wedge_cubes_single.py)

**Summary.**
- The symmetry breaks, the cube covers, and every clause family were checked. All are
  sound, with one serious exception.
- **wedge_cubes_single.py has a variable-id collision with the k6z3 base.** The 225 (B)
  "UNSAT in about 1.6 s" results were produced on k6z3. I confirmed this byte for byte. They
  are **not valid evidence**, and neither is any DRAT proof of those `*_single` sub-CNFs.
- (A) is unaffected: its 16 sub-cubes use the k6z2 base, where there is no collision. I
  re-ran all 16: all UNSAT in 3–12 s.
- (B) is now closed by hand anyway (C28 + C29, refereed-correct).
- A corrected (B) rerun was started and then stopped to free cores:
  `work/referee4/log_rerun_B.txt`. **9 of the 225 cubes finished, all UNSAT, but they took
  187–243 s and up to about 3,600 s each**, against 1.2–2.5 s in the collided runs.

## 1. Symmetry breaks and the positions 0 and 18

**The relabelling group.** The wiring labels come from choosing a starting point on the
circle of 36 ends (0L..17L, 0R..17R).
- Starting at position s gives the labelling i ↦ i − s (mod 18), with the wrapped lines
  reversed.
- Starting at L and at L + 18 gives the *same* label map, with all orientations reversed.
  That is the 180° rotation, which sends χ to −χ.

**The two breaks are compatible.** The breaks are "line 0 avoids every triple point"
(build_k6z) and χ(0,1,2) ≠ −1 (build_defect, `[-ng[0,1,2]]`).
- Pick any line off every triple point. One exists: there are 18 − σ ≤ 17 triple lines,
  because σ ≥ 1 (not general position).
- Of its two start points, at least one gives χ(0,1,2) ∈ {0, +1}. ✓
- The rotation-based "line 0 defect-free" break in build_defect is **not** active here,
  because budget = 39 ≥ n.
- The C17 clauses are invariant under first↔last, and valid for every wiring labelling. ✓

**Excluding positions 0 and 18 from S is valid.** Line 0 is not an axis, so its ends are
not cap-point ends. ✓

**Cubes with min S even are UNSAT at once, as the coordinator observed.**
- In wedges(), position 0 pairs with 1 exactly when min S is even: the run through 0 has
  even length and is paired from its start.
- That unit c17f(0,1) contains ¬pz[0,1,2] ∧ ¬z[0,1,2], so it forces ng[0,1,2], which is
  forbidden.
- In every solution under the break, line 0's left end pairs with 35 = 17R: first(0,17),
  last(17,0), which C17 allows for {0, n−1}.
- This is expected and loses no coverage. The genuine cubes are the min-S-odd ones.

## 2. wedge_cubes cover and units

**Every real (A)/(B) arrangement lies in some cube.**
- |S| = u ∈ {4, 6} (C16), and S avoids 0 and 18.
- Every non-singleton end is a wedge with a cyclic neighbour (C17), and the run between
  two singletons has a unique pairing by neighbours.
- The filter "a line's two wedge partners differ" is valid: two lines meet once.

**Units.** end(p, other) is c17f for p < 18 and c17l for p ≥ 18, with line p mod 18.
c17f and c17l are the conjunctions first(L,R) and last(L,R), including ¬z. ✓
- The solver's `before` equals the real left-to-right order on every line (C17 verdict).
- On 67,997 simple end vertices of real pseudoline arrangements, "left end ⇒ c17f true"
  and "right end ⇒ c17l true" held with 0 failures (`work/referee4/audit_semantics.py`).

**Counts reproduced.**
- u = 4: 450 admissible sets, 225 with min S odd. `wedge_cubes_B_real.jsonl` equals this
  set.
- u = 6: 3,668 admissible sets, 32 C27-matchable, 16 with min S odd.
  `wedge_cubes_A_real.jsonl` equals this set.

## 3. wedge_cubes_c26 ((A) sub-cubes)

**Each clause is a necessary condition** under C26 (a)–(c), counting from the singleton end e
of L with L2 = ℓ′:
- **Exactly 3 lines cross L strictly before L2.** C crosses at X_1, and b, c cross at P.
  The direction is correct: before(L,x,L2) for a left end, before(L,L2,x) for a right end.
- **¬z(L,L2,x) for all x.** X_3 = X is a block far end, so it is simple.
- **The witness w(b,c) → z(L,b,c) ∧ bef(b) ∧ bef(c) ∧ tri(L,b,L2) ∧ tri(L,c,L2), and the OR
  of the witnesses.** P = X_2 = L∩b∩c, and P's other block lies at X_3 with cap D = L2
  (C26 (b)).
- **Tested with the solver's own literal semantics** on 721 real configurations where the
  2nd vertex from an end is a type-X point with that line as axis. There X_3's other line
  plays L2, and this holds in any arrangement. **0 failures** (`audit_semantics.py`).

**The matching enumeration is complete.**
- matchings() pairs the smallest remaining singleton with every admissible partner:
  distance ≤ 5 and a different line.
- Each of the 16 genuine sets has exactly **1** admissible matching.
- `A_c26.jsonl` holds exactly those 16 (set, matching) pairs, and `A_c26.log` has all 16
  UNSAT.

**Numbering.** The new variables start at k6z2's nv + 1 (1,543,286). That is correct for
the k6z2 base, and my rerun on k6z2 reproduced 16/16 UNSAT (3–12 s,
`work/referee4/log_rerun_A.txt`). **Do not combine A_c26.jsonl with k6z3**: its variables
1,543,286 onward are k6z3's tl, sel and C16-counter variables.

**Missing guard.** The script does not check c["u"] == 6. Applied to u = 4 cubes it would
impose the (A) matching, which is **unsound** for (B) shapes P–A–P′. The inputs used were
correct (u6 only). Add an assert.

## 4. wedge_cubes_single ((B) sub-cubes): clauses sound, numbering broken on k6z3

**The clauses are necessary conditions** under C26 (a)/(b), at every singleton end:
- w(b,c) → z(L,b,c) ∧ AtMost1{x ∉ {L,b,c} : x before b from e}. Only C, at X_1, precedes P.
- v1(x): x before b, with tri(L,b,x) ∧ tri(L,c,x). Take x = C, the block at X_1.
- v2(x): b before x, with the same triangles. Take x = D, the block at X_3.
- The units sel_u(|S|) and tl[p mod 18] are valid by C16.
- **Tested on the same 721 real configurations: 0 failures.**

**The collision (critical).**
- The script's IDPool starts at max(ids.top, max tl, max sel) + 1 = 1,543,306.
- k6z3.cnf declares nv = 1,543,534. Variables 1,543,306–1,543,534 are the seqcounter
  auxiliaries of its C16 cardinality constraints, for example the clause
  `-1543304 1543286 1543306 0`.
- So each (B) sub-cube's w, v1, v2 and AtMost1 auxiliaries reuse those ids, which couples
  unrelated constraints.
- **Confirmed.** The recorded sub-file `sub_u4_5_12_13_22_single.cnf` (200,267,814 bytes)
  matches the k6z3 base exactly. With the k6z2 base the predicted size is 200,207,453.
- **Effect.** With correct numbering (all sub-cube variables shifted by +229, the rest
  unchanged; `work/referee4/rerun_cubes.py`), the same cubes take **187–202 s** each
  instead of 1.5 s.
  - 9 cubes are UNSAT, taking 187–243 s, and two took about 3,580 s.
  - I stopped the run to stay within the core budget. `rerun_cubes.py` resumes from the log.
  - The 100–2,000-fold speed-up of the originals is consistent with the collision adding
    spurious constraints.
- **Fix.** Start the sub-cube pool at the *base CNF's header nv* + 1, or dump ids for the
  exact base used. Regenerate B_single.jsonl.
- **Any DRAT proof of the old `*_single` sub-CNFs certifies the wrong formula.** The plain
  wedge-cube DRAT inputs in `work/k6z2/drat/` (u4_*.cnf, k6z2 plus units only, 198,686,792
  bytes) contain no new variables and are unaffected.

## 5. build_k6z base clauses (spot audit)

Each of these is a necessary condition for a real 94 with k = 6, β = 0 and no 4-fold point:
- C10 clause (refereed).
- Z = 0 as "each consecutive pair is a side of tri(r,x,y) with x through r∩i and y through
  r∩j". This enumerates all line pairs through the two endpoints.
- β = 0: at most one of the four tri(r,x,y) on a segment between two triple points.
- Non-triple lines are caps. The cap literal only implies z ∧ ≥2 tri, so it is a
  relaxation.
- Not general position (Theorem H) and line 0 off every triple point (§1).
- C17 Statements 1 and 2. For Statement 2 with t_1 = "both", the two triangles must use
  different lines at X_2, which gives z(L,s1,s2) ∧ tri(L,R,s1) ∧ tri(L,R,s2).
- C16: tl, sel_u4 ⇒ exactly 14 triple lines, sel_u6 ⇒ 12..15.

build_defect components:
- The defect budget n(n−2) + 3k + C(k,2) − 3T = 39. I re-derived it: per line, the
  A-pairs number Σ d_s d_{s+1} ≤ 16 + τ_r + a_r, with Σ a_r ≤ C(k,2), and each triangle
  accounts for exactly 3 A-pairs.
- "alternate", the Blanc claims (U variables; exemption is a relaxation), exactly 6 zero
  triples, and ≥ 94 triangles.
- The 17 realizable 4-line sign patterns and the triangle rule are from earlier validated
  work and were not re-derived here.

## Bottom line

- **(A):** sound on the k6z2 base. 16/16 genuine sub-cubes UNSAT, reproduced.
- **(B):** closed by the hand proof C28 + C29. The old solver runs and their DRATs are
  invalid because of the collision. With correct numbering the cubes are genuinely hard
  (minutes to an hour each); 9 of 225 are UNSAT so far.

# Audit: k = 5, β = 0, B = 10 encoding (search/build_k5.py, search/k5_cubes.py) and C32 as a spec

**Summary.** Every base clause and every per-row cube constraint is a necessary condition
under the refereed claims:
- C10, C11, C14, C17, C18 and C25;
- C26 (a)–(c) and C27;
- C30 and C31.

Numbering is correct. The 192 rows are complete and exactly reproduced. Together with C30
(Z = 0), C31 (clean = 2) and C33 (clean = 0, K = 3, refereed-correct), they cover k = 5,
β = 0, B = 10. **The 192/192 UNSAT therefore closes the clean ≤ 1, K = 4 case, and k = 5,
β = 0 is closed**, assuming the DRAT pass (72/192 verified, 0 failed, when I checked)
completes.

## 1. Base clauses (build_k5.py)

**build_defect(18, 94, 5, alternate, exact_triple, blanc).**
- The budget is 288 + 15 + 10 − 282 = 31, derived as in AUDIT_k6z §5. Since 31 ≥ 18, no
  rotation break is added.
- Exactly 5 zero triples.
- The Blanc claim clauses are sound for n even. A clean line is non-exempt, so it must
  claim, which is consistent with Z = 1.
- The unit ¬ng[0,1,2] is the 180° break.

**C10 and β = 0.** Unchanged from k6z (audited).

**Segment used, with one slack.** Clause: [¬A(r,i,j), tri, usedvia…, s(r,i,j)], with
Σs = 1 (equals).
- In a real 94 here, Z = 1 exactly (C30 (1)).
- Both endpoints of u₀ are simple in every C30 sub-case:
  - clean = 2: touched by the clean lines;
  - clean = 1 and clean = 0, K = 4: X is a cap point and Y is touched;
  - K = 3: both are cap points.
- So u₀ has **exactly one** representation with A true, (r0; i, j) with i before j. The
  equality is therefore exact, and every other consecutive pair has a witness. The
  witness list is complete: a triangle on r plus one line through each endpoint.

**The slack guards are all satisfied by u₀.**
- s → A: yes.
- s → ¬tri(r,i,j): u₀ is unused.
- s → ¬z at both endpoints: both are simple.
- s → ∃M before i and ∃M after j (u₀ is not an end segment): u₀ as an end segment would
  give the pattern (0,0) at a simple end vertex, hence two unused pieces. Type-X points
  are never line ends. ✓

**Type X: z[t] → at least 4 tri(x,y,L) with {x,y} ⊂ t, L ∉ t.**
- B = 10 and β = 0 make every point type X.
- Its 4 cap triangles all have the vertex x∩y = P and are 4 distinct literals. ✓

**"No triple point is a line end."** z[t] → on each L ∈ t, some M ∉ t crosses before
L∩a and some M ∉ t crosses after it. Type-X points have all six first segments bounded. ✓

**Clean lines.** cl(L) is added as a third option beside "on a triple point" or "cap".
- cl(L) → ¬z for the triples on L, which is correct: clean lines avoid triple points.
- Σcl ≤ 1, because clean = 2 is dead (C31, refereed). ✓

**11 ≤ τ ≤ 13.** τ = 15 − σ. The real range is σ ∈ {2, 3} in every live sub-case, so
τ ∈ {12, 13}; the bound used is weaker, hence sound. ✓

**C5 and line 0.**
- Some line carries two triple points (Theorem H). ✓
- Line 0 avoids every triple point, with a WLOG compatible with the 180° break (AUDIT_k6z
  §1). There are ≥ 3 + σ ≥ 5 non-triple lines. ✓

**C17 Statement 1.** Unchanged and unconditional. ✓

**C17 Statement 2 with the touch disjunct.** Suppose L's end X = L∩R is simple.
- t_1 = 0 is impossible, since u₀ is not an end segment.
- t_1 = "both" gives both(L,R).
- If t_1 is single, R's piece on side −t_1 borders only the ray face and a non-triangle.
  - If that piece is a ray, X is R's end: F[R,L] or G[R,L].
  - If it is bounded and unused, it is u₀ = R's consecutive pair (L, x) or (x, L), so
    s(R,L,x) or s(R,x,L).
- The disjunct lists both orientations for all x, which is a superset. ✓

## 2. k5_cubes per-row units

**Wedges.** Same units as wedge_cubes (AUDIT_k6z §2). Every end outside N is a wedge,
because C30 classifies ends as wedges, singletons or touch ends, and N is the 5 singletons
plus t. ✓

**Singleton shape (all 5 singletons, U0 included).** This is the wedge_cubes_single
encoding: w, AtMost1, and v1/v2.
- It is valid for any type-X point that is 2nd on its axis with X_1 and X_3 simple, both
  for U0 (whose X_3 side is its bounded Lemma-A side) and for the four killed points.
- Tested earlier on 721 real configurations. ✓

**Match pairs (p,p′), C26 (c).**
- Each killed point has exactly one mutual side and a ray on the other side, so X =
  a_Q ∩ a_{Q′} is the 3rd vertex from both singleton ends.
- The encoding is exactly 3 lines before, ¬z at X, and the witness with tri(L,b,L2) and
  tri(L,c,L2).
- It relies on no double cross, which C30's verdict shows holds here. ✓

**s0 and t.**
- end(t, a): Y is L_Y's end vertex on a_{U0}.
- Exactly 4 lines cross a before L from s0: C_1 at X_1, b and c at U0, and C at X. Y is
  simple.
- The slack is OR_D s(a,D,L) for a left end and OR_D s(a,L,D) for a right end, i.e.
  u₀ = [X,Y] oriented from s0.
- **Tested with the solver's literal semantics** on 670 real configurations (a type-X
  point 2nd on its axis, with vertices 1, 3 and 4 simple):
  - the count is exactly 4;
  - the orientation from a left end is before(a,D,L), and from a right end before(a,L,D);
  - in the 73 cases where Y is also an end of L, the end(t,a) unit is the correct
    c17f/c17l.
  - **0 failures** (`work/referee4/audit_k5_semantics.py`). ✓

## 3. Numbering

- k5.cnf has nv = 1,657,054, which equals ids.top.
- k5_cubes takes max(ids.top, header nv) + 1, and all 192 cubes have their new variables
  in [1,657,055, 1,688,542].
- No unit touches a new variable. ✓

## 4. Coverage

**The rows.** `work/referee4/k5_patterns_check.py` independently regenerates the rows
(own wedge and matching code), and the set is **identical** to k5_patterns.jsonl: 192 rows,
32 distinct N.
- 96 rows contain the wedge (0,1). They are UNSAT at once under ¬ng[0,1,2], as in k6z.
  This is expected and loses no coverage; the other 96 are the genuine ones.
- Excluding positions 0 and 18 is valid under the WLOG in C32 (a) 7: line 0 is a
  non-triple line other than the touch line, so both its ends are wedges.
- The base encodes only "line 0 is off every triple point". The "not the touch line" part
  is enforced by excluding t ∈ {0, 18}. That is consistent, because the WLOG can pick
  line 0 among ≥ 4 non-triple non-touch lines.

**The case split for k = 5, β = 0.**
- B ∈ {9, 10} (C14). B = 9 is dead (verdict C18).
- For B = 10:
  - Z = 0 is dead (C30 (1)).
  - Z = 1 has four sub-cases:
    - clean = 2: dead (C31);
    - clean = 1: covered by the 192 rows;
    - clean = 0, K = 4: covered by the 192 rows (cl is free, Σcl ≤ 1);
    - clean = 0, K = 3: dead (C33).
- A row needs U0 2nd on its axis with u₀ = [X_3, X_4] and a touch end at Y.
  - The distance d(s0, t) = 5 comes from T1.
  - The matching of the other 4 singletons at distance ≤ 5 on different lines comes from
    C27.
  - All of these hold in both K = 4 sub-cases (C30 and C31 verdicts). ✓

## 5. C32 as a spec

**(a)–(c) are sound**, and the code implements them as described. The optional "¬usedvia"
tightening in (a) 3 is not implemented, which is harmless.

**(d)**, the K = 3 shared-axis configuration, is a correct description: vertex order,
blocks, the u₀ slack, the U1–K1 mutual pair with face tri(a,m,D), K2–K3 matched, 4
singleton ends and no touch end. It is now moot by C33.

Status: C32 refereed-correct as a spec.

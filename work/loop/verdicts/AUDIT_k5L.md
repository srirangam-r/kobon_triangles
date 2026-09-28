# Audit: k5L (search/k5L_layer.py, build_k5L.py, k5L_cubes.py; work/k5L/k5L.cnf, cubes.jsonl)

**Verdict: sound.** Every unit in the 196 cubes is a necessary condition. Every real 94 in the k = 5, β > 0
residue satisfies k5g + layer + some cube. I found no unsound unit, so no fix is needed.
- One inherited dependency: the k5g base still contains the global exception clause (cpe ∨ axcap). That clause
  relies on "E1 is net-neutral" (AUDIT_k5g §4, audited). So the E1 subtlety is avoided only at the cube level.

Test scripts are in `work/referee4/k5L/` (logs `log_layer_*.txt`).

## Q1. Layer definitions ✓

I checked each clause by hand.
- **Exact definitions (↔).** p is a bijection (exactly one p per label, z → some label, injective). l, blkL, t2, TB,
  Lbw, BR, the GE1/GE2/AX counters are all exact.
- **One-directional definitions (→ only).** FC, ce, CPE, mu/MUT, bl, E2, E1. These carry only clauses of the form
  v → property. So "every aux = truth of its property" satisfies all layer clauses at once.
- **Blocks.**
  - Adjacent rays are impossible. Blocks on r0 and r1 share the sector-(r0,r1) face, so they have the same cap C.
    Then c∩C would be the first vertex of both r2 and r5, which is absurd.
  - Two blocks on one line need different caps. So AX ⟺ same line ⟺ X/F, and ¬AX ⟺ bent.
- **TB.** A block's apexes b∩C and c∩C are the first vertices of r1 and r5. So TB ⟺ O1b (C39).
- **BR.** Take two distinct witnesses tri(r,x,y), with x a line of i and y a line of j. Both contain the side [i,j]
  (vertices r∩x = i, r∩y = j), and that side is an edge. So the witnesses are distinct triangles on opposite sides,
  and [i,j] is doubly used. Conversely, a bridge gives the pair tri(r,x,y), tri(r,x′,y′). No triangle is counted
  twice, because i and j share only r.
- **Counters.** A brute-force test (`counter_test.py`, 2,520 cases) confirms the counter is exactly ↔ and `upper`
  is a correct forward counter.
- **Tests on independent geometry.** Ground truth comes from the referee's `work/referee/arr.py` (ray cycles),
  not from the author's harness.
  - Mutated pseudoline arrangements (`layer_mut_test.py`): 707 arrangements, **22 bent points**, 1,445 one-block
    points.
  - Exact real line arrangements (`layer_real_test.py`): grid-concurrence lines, 108 arrangements, **35 bent
    points**.
  - The referee's k = 5 bent example with e = 4.
  - Every two-directional indicator was forced to its geometric value. Every true one-directional indicator was
    satisfiable. All true values asserted together were satisfiable.
  - Blocks on adjacent rays: 0. Every block had a common cap. The type map (axis / bent / b1 with O1a/O1b) held
    everywhere. The author's harness also passes when re-run.

## Q2. Exact graph, types, faces; completeness ✓

`enum_check.py` re-runs the k5_p11 filter.
- **The 28 rows are exactly all labelled survivors** of the residue multisets, after C47 and C50(b). The ROW lines
  reproduce k5_p11.out exactly and match the referee's p11_fixed.
- **Faces are forced.** No residue F point has e = 4. Every row has exactly one valid face option, namely the
  G-triangles plus the forced faces of the e = 2 F points. So the FC units and the C43 sites are determined.
- **Why the faces are real.**
  - A G-triangle is a face, because its sides are edges and a third line through a vertex would need to exit
    through an edge.
  - An e = 2 F face is real by Lemma B: at an axis point, bridges pair up as (r1,r2) or (r4,r5) with the face in
    between.
- **Relabelling invariance.** Slack and need are invariant under type-preserving relabelling. The 28 rows form 12
  isomorphism classes, each present in every sorted-type labelling.
- **Types.** They are exact: X/F/V by block count and axis, O1a/O1b by TB. The label bijection is free.
- Since BR ⟺ bridge, −BR on non-edges is justified.

## Q3. Zmax = B + β − 9 ✓

- **Identity.** C34(a) at k = 5 gives Σc = B + β − 10 ≥ Z − 1.
- **D = B + β.** A doubly used segment with two simple ends would carry two copies of the same triangle tri(r,x,y),
  so it has at least one triple end: one triple end makes it a block, two make it a bridge.
- **Slack count.** A(r,i,j) is ordered (A → before(r,i,j)). Canonicity is the smallest label at each end. So Σs = Z
  exactly (AUDIT_k5g §1).
- B and β come from the exact types and edges.
- Note: Zmax = 5 in 15 of the 28 graphs, so there is no gain over k5g's global cap there.

## Q4. Exceptions and need ✓

- **C43.** Q's block is mutual with exactly one of P and R (C42), and both orders are offered. E1 is weaker than
  "a triple point at b_Q ∩ m_PR". The E2 literal is right.
  - R's block toward X_RQ has middle b_R and cap b_Q. Its outer triangle (R, Q, X_RQ) has its side at Q on the ray
    next to Q→R, which lies on b_Q.
  - b_Q is Q's block middle (C42), so ce(R, b_R, b_Q) ∧ bl(Q, b_Q) holds.
- **C50 (i).** An apex V = b∩C carries the block (C, a), i.e. bL(V, C, a). That is MUT.
- **C50 (ii).** This is ce, i.e. F/G[a, C]. MUT is superfluous for O1a points but harmless.
- **need.**
  - Each site without an exception gives a Cred +1.
  - These credits are distinct: an unkilled cap point belongs to one block (C43 and C50 verdicts).
  - A 94 absorbs at most `slack` extra credits.
  - `slack` is the filter's maximum over options.
  - So at least #sites − slack sites have exceptions. Cubes cover every choice of `need` sites and every
    alternative.

## Q5. Id hygiene ✓

`ids_check.py` rebuilt k5L in-process.
- **Byte-identical.** The CNF matches work/k5L/k5L.cnf (md5 a9ee57ce…) and ids.json is equal.
- **Id range.** The top of k5g is 3,797,524. All 289,144 named layer ids lie above it.
- **Clean base reads.** The 1,676,743 layer clauses read only these k5g literals: z, tri, blk, F, G and s.
- **No CardEnc collisions.** No CardEnc call leaves pool.top below its aux ids.
- **Cube units.**
  - The 60 distinct unit variables are all layer variables, and each occurs in a layer clause.
  - The header nv equals top (4,090,743).
- **Cube file.**
  - Regenerating it reproduces cubes.jsonl exactly.
  - pilot_cubes.jsonl holds the same 196 cubes in a different order.

**Efficiency note (sound).** Because labels are free and the classes are invariant, one row per isomorphism class
suffices: 86 cubes instead of 196.

Not audited: search/build_k5L_local.py and work/k5L/local*.

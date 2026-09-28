# Audit: search/build_k5g.py (k = 5, β > 0) and work/k5g/cubes.jsonl

**Verdict: sound.** Every clause family is a necessary condition for a real 94 with k = 5
and β > 0. The 35 cubes cover the instance.
- The one unwritten dependency is that **C43's exception E1 is net-neutral**, so only E2,
  (ii) and (i) can absorb a credit. That fact was in C45's appendix, which I had not
  refereed before. It is proved in §4 below.
- Numbering is correct: base nv = ids.top = 3,797,524, and the cube variables start at
  3,797,525.

## 1. Canonical slack

- For (r,i,j), the clause is vacuous unless i and j are the smallest lines at their
  endpoints, via the literals z(r,i,x) for x < i and z(r,j,x) for x < j.
- Each unused segment has exactly one canonical representative, and every used one has a
  witness. So in the real assignment Σs = Z, and s → A holds.
- **Σs ≤ 5.** On all 28 residue graphs B ∈ [7,8] and max(B + β − 9) = 5, rechecked from
  k5_exceptions.jsonl. With D − Z ≥ 9 this gives Z ≤ 5. ✓

## 2. C17 Statement 2 with the touch disjunct (any Z)

Suppose X = L∩R is L's simple end vertex.
- If t_1 is "both", then both(L,R) holds.
- If t_1 is single, R's piece on side −t_1 is a ray (F/G[R,L]) or unused.
- If t_1 = 0, both pieces of R at X are unused, and one of them is bounded unless X is an
  end of R.
- The unused bounded piece is R's segment [X,Y], whose canonical representative is
  (R; L, x) or (R; x, L), with x the smallest line at Y. The disjunct lists both
  orientations for every x. ✓

## 3. Blocks

- **Exact blk.** z ∧ tri(a,b,C) ∧ tri(a,c,C) → blk is exact: the two faces fill the
  half-plane at X, so X is simple and this is a real block. The dz counters use the same
  variables, so this is consistent.
- **≤ 2 blocks per point:** no centroid at k = 5 (C41).
- **7 ≤ B ≤ 8:** from the residue. ✓

## 4. The exception clause

Every one of the 28 graphs has need ≥ 1. The three exceptions map as follows:
- **E2** (the non-mutual F vertex R is 2nd on b_R): blk(t_R, b_R, b_Q) ∧ F/G[b_R, b_Q].
  This is a cap-point end.
- **(ii)** (the 1-block cap point is a line end): blk(t_Q, ℓ, C) ∧ F/G[ℓ, C]. This is a
  cap-point end.
- **(i)** (a mutual apex V): ℓ carries Q's block, so it is a block line, and V's block
  toward X is capped by ℓ, which gives blk(t_V, C, ℓ). This is an axis-cap. ✓

**E1 is net-neutral.**
- E1 puts V on b_Q with Q, X_RQ and V consecutive. So (Q,V) is a non-edge adjacent pair,
  which gives σ + 1.
- **(Q,V) is not an already-counted C45 or C49 gap.** That would need a gap owner Y with
  its block far end at X_RQ, on b_R. Then all four sectors at X_RQ would be triangles, and
  [Q, X_RQ] would be doubly used. That is a second block of Q, contradicting O1b.
- **(Q,V) is not a C42 pair either.** If V is a plain X point, it has two such pairs:
  (V,Q) and (V,R) on m_PR. Neither is a bridge or a face side, so V yields at least 2
  units, against the ≤ 1 per point assumed by the ⌈·/2⌉ count.
- Hence E1 always replaces the Cred +1 by a fresh σ + 1, and the exception list
  {E2, (ii), (i)} is complete.

## 5. Cube cover (35 cubes)

- Each model satisfies the exception clause, so some cpe(t,a,C) or some axcap(a) holds.
- A cpe gives blk(t,a,C) with a ∈ t, so a ≠ 0, because line 0 carries no triple point. It
  also gives F[a,C] (position a) or G[a,C] (position a + 18).
- Cube capend_p asserts OR over (t ∋ a, C) of blk ∧ F (for p < 18) or blk ∧ G (for
  p ≥ 18), with 2,040 witnesses each. There are 34 such positions, plus the axcap cube.
- **The cover is complete.**

# C36 — encoding spec: k = 5, β ≥ 1

**Literals.** `bf(u,L,v) := before(u,L,v)`, the kobon_sat convention: on u, L's crossing
strictly precedes v's.
- *Check:* this is the REVERSE of the gallery sweep order of chi_from_word
  (`work/t3/c36_orient.py`). The constraints below are symmetric in the two classes, so
  this does not affect soundness. The class definitions are stated in the model
  convention.
- Only C17 Statement 1 is valid here. Statement 2 needs Z = 0.

## 1. C35 sector classes (sound given C25: k ≤ 4 closed; C35 proposed)

For a sorted triple t = (A,B,C), let P = A∩B∩C.
- **Class K1:**
  - tri(A,B,L) ∧ bf(A,B,L) ∧ bf(B,A,L);
  - tri(B,C,L) ∧ bf(B,L,C) ∧ bf(C,L,B);
  - tri(A,C,L) ∧ bf(A,L,C) ∧ bf(C,A,L).
- **Class K2:**
  - tri(A,B,L) ∧ bf(A,L,B) ∧ bf(B,L,A);
  - tri(B,C,L) ∧ bf(B,C,L) ∧ bf(C,B,L);
  - tri(A,C,L) ∧ bf(A,C,L) ∧ bf(C,L,A).

Here L ranges over lines not in t. Each row is one sector: sectors k1_AB, k1_BC, k1_AC,
k2_AB, …. Each sector holds at most one triangle.

Encode:
- aux `sec(t,row)` with `sec → OR_L w_L`, where `w_L → tri(·), w_L → bf(·), w_L → bf(·)`;
- `z[t] → ≥2 of {k1_AB, k1_BC, k1_AC}`: the clauses [¬z, p, q] for each pair;
- the same for K2.

**Audit.** `work/t3/c36_class_check.py` (run with `uv … --with python-sat`) evaluates this
formula on gallery arrangements. It matched the geometric class partition on **6,613/6,613**
triangles at triple points.
- Mixed-direction pairs, e.g. tri(A,B,L) with bf(A,L,B) ∧ bf(B,A,L), are geometrically
  impossible at P. They need no clause.

## 2. β ≥ 1

For each line r, two sorted triples t1 = (r,x,x′) and t2 = (r,y,y′) with t1 < t2, and
disjoint other lines, and each pairing π ∈ {((x,y),(x′,y′)), ((x,y′),(x′,y))}:
- aux `br(r,t1,t2,π)` with
  `br → z[t1], br → z[t2], br → tri(r,x,y), br → tri(r,x′,y′)`, the tri according to π;
- the clause **OR br**.

*Soundness.* A doubly used bridge [P,Q] ⊂ r carries exactly two triangles. Their sides at P
lie on the two rays next to P→Q, which belong to P's other two lines. The same holds at Q. So
the pair is tri(r,x,y) and tri(r,x′,y′) for one pairing. Conversely, br forces two distinct
triangles on the segment [P,Q].

## 3. D − Z ≥ 9 (sound weakened form; about 3·10⁵ aux, optional)

- **Unused segments with simple endpoints:** `u(r,i,j)` forced by the k6z C14 clause, extended by
  `[¬A(r,i,j), tri(r,i,j), usedvia…, z(r,i,x) ∀x, z(r,j,x) ∀x, u(r,i,j)]`.
  - So u is forced exactly when the segment is unused and both endpoints are simple. Then
    Σu ≥ Z_simple ≤ Z.
- **Blocks:** `blk(t,a,C) → z[t] ∧ tri(a,b,C) ∧ tri(a,c,C)` for t = {a,b,c} and C ∉ t.
  - A far end a∩C cannot be triple, since the bridge triangles use different Q-lines. So
    blk counts only blocks, once each.
- **Constraint:** Σu − Σblk − Σbr ≤ −9.
  - Sound: a real 94 has Z_simple ≤ Z ≤ D − 9, and D = Σblk + Σbr at their maxima.
  - Do not drop the br terms; that would be unsound.

## 4. Bent facts (verdicts C08, C19; C21 Claim 1)

**Pattern.** For t_P = {a,b,c} and t_Q = {a,d,e}:
- `bent(tP,tQ)` is forced by `[¬z[tP], ¬z[tQ], ¬tri(a,b,C1), ¬tri(b,c,C1), ¬tri(a,c,C2), ¬tri(b,c,C2), bent]` for {C1,C2} = {d,e}, both assignments.
- The pattern also matches centroids.
- The proofs of (i) and (ii) use only the two blocks next to PQ, so I believe they apply to
  centroids verbatim. **Auditor, please confirm.**

**(i) Q has at most one block:** `bent(tP,tQ) → AtMost1{blk(tQ,·,·)}`.

**(ii) Two points bent toward the same Q (C21):**
- `¬bent(tP1,tQ) ∨ ¬bent(tP2,tQ)` if t_P1 and t_P2 meet t_Q in different lines;
- if they meet it in the same line: `bent ∧ bent → ¬blk(tQ,·,·)`.

## 5. C35 consequences

These are the 1-block and 0-block bridge requirements. They are implied by §1 plus the model.
No extra clauses are needed.

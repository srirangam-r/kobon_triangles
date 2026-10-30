# W = 13, case (e): Δ = 2 cannot rescue an isolated double-B star

This is a hand proof. It has not yet been refereed. A straight-line model was used only to check orientations (§8).

**Result.** In case (e) of W13.md §1 (ΣS° = 0, K3 = K4 = 0, U = 0, Δ = 2), **no isolated double-B star exists**,
wherever the Δ-event sits. The status of path clusters in case (e) is in §7: the B–B two-quad path is excluded
Δ-free, and the rest is OPEN.

**The proof in brief.**
1. Every Δ-dependence of the short star theorem (W13.md §§3–4) is an O* or M* statement at one of 24 named edges or
   triangles of the star. These are 6 "checkpoints" at each of the 4 corners. Each failure costs exactly two
   residual tokens, so with Δ = 2 at most one checkpoint fails.
2. The short star theorem also relied on one global Δ-dependent input: the alternating exclusion, inside STAGE2_TASK7
   §4. Lemma 2.1 replaces it with a Δ-free argument.
3. The route claim is true. Two checkpoints per corner are route-specific and are closed by the other route. The
   other four are shared. The lead's shared list needs a correction (§3.3).
4. Each shared failure either forces a second, disjoint pair of tokens (so Δ ≥ 4) or turns a vertex simple that one
   route needs as a triple far corner, so that route closes trivially.

## 0. Setting, notation and inputs

The notation follows SOL_TASK8 Addenda 2–5, STAR_CASES.md and W13.md. P = H∩a∩b∩c has rays 0..7 = H+, a+, b+, c+,
H−, a−, b−, c−, mask BRRRBRRR, kites (P, A+, T+, F+) and (P, C−, T−, A−), and diagonals D± through the simple
centres X±.

The skeleton orders below are SOL_TASK8 (S2) plus Addendum 5. In each case below, those parts that hold depend only
on the facts proved for that case.

    H : V− T− X− P X+ T+ V+            a : W2− Y− A− P A+ Y+ W2+          c : W1− Z− C− P F+ Z+ W1+
    D+: U+ A+ X+ F+ U+′                D−: U− C− X− A− U−′                b : B− P B+
    α+: U− B+ A+ T+ Z+                 φ+: U−′ B− F+ T+ Y+
    γ−: U+ B+ C− T− Y−                 α−: U+′ B− A− T− Z−
    e1: U+ Y+ V+ W1+   e2: U+′ Z+ V+ W2+   e3: U−′ Y− V− W1−   e4: U− Z− V− W2−

**Rings**, cyclic, listed in one orientation; "v→(−ℓ)" is the ray of ℓ at v opposite the named one:

    A+ : A+B+, A+P, A+X+, A+T+, A+Y+, A+→(−D+)              (lines α+, a, D+, α+, a, D+)
    T+ : T+A+, T+X+, T+F+, T+Z+, T+V+, T+Y+                  (α+, H, φ+, α+, H, φ+)
    B+ : B+A+, B+P, B+C−, B+→(−α+), B+→(−b), B+→(−γ−)
    Y+ (if triple, third line e1):  Y+A+, Y+T+, Y+V+, Y+→(−a), Y+→(−φ+), Y+→(−e1)
    Z+ (if triple, third line e2):  Z+F+, Z+T+, Z+V+, Z+→(−c), Z+→(−α+), Z+→(−e2)
    V+ (if triple):                 V+Z+, V+T+, V+Y+, V+→(−e2), V+→(−H), V+→(−e1)

The rings at A+ and T+ follow from the faces PA+B+, PX+A+, X+A+T+, T+A+Y+ and from the kite and the two exterior
faces at T+. The rings at Y+, Z+ and V+ follow from the consecutive faces T+A+Y+ and T+V+Y+, T+F+Z+ and T+Z+V+, and
T+Z+V+ and T+V+Y+, plus alternation.

**Principles.**
- **(P1)** A triangular face at v lies in one sector between consecutive rays r, r′. Its other two vertices are the
  first vertices on r and r′. A first segment vw is double iff both sectors at v beside the ray v→w are faces. A
  triple with ≥ 5 double rays is full.
- **(P2)** Rings alternate lines: at a triple l1 l2 l3 −l1 −l2 −l3; at a quad l1..l4, −l1..−l4; at a simple vertex
  l1 l2 −l1 −l2.
- **(P3)** Unique crossing ("wrong ray").
- **(P4)** Triple-cap continuation (STAGE2_TASK7 §2).

**Δ-free inputs** (none uses Δ, U, η0 or π):
- **(I1)** Masks: ALL8_NOTE3 §8 and STAGE2_TASK5 §§1–2.
  - S° = 0 ⇒ all-8 with one of the three zero masks.
  - Every block at a zero quad is a kite block, with a simple four-fan centre.
  - In the double-B mask the blocks lie on the two rays of the case-B axis. Both kites are K1 case B: all caps are
    double, every corner other than the quad is a triple, and the far corners lie on the axis.
- **(I2)** STAGE2_TASK5 §3: a double-B zero star has no quad first neighbour. So B± are triples.
- **(I3)** STAGE2_TASK5 §4: the cluster reduction, so P is an isolated double-B star. Also n ≥ 3k+5+b for paths.
- **(I4)** ALL8_NOTE3 §8 propagation, and the STAGE2_TASK6 §§3/5 mask lemma derived from it.
  - In a single-B zero star the central neighbour Q4 is a quad.
  - Hence a zero quad whose kite block has two quad corners and triple adjacent corners is **alternating**.
- **(I5)** ALL8_NOTE5 (4)/(5): O* and M* tokens are residual, pairwise disjoint, and Δ ≥ |O*| + |M*|.
- **(I6)** STAGE2_TASK6 §4, wrong ray: if Y+ is simple, then T+Y+ and A+Y+ are both single.
  - The second face on T+Y+ would have apex a∩H = P, which lies on T+→X+, not on T+→(−H).
  - The second face on A+Y+ would have apex φ+∩D+ = F+, which lies on A+→X+, not on A+→(−D+).
  - Likewise for Z+.

Also Δ-free, given S° = 0 and K1 case B:
- A±, F+, C−, T± are triples. X± are simple. Every kite cap is double.
- The faces at P, the kite faces, and the exterior faces T+A+Y+, T+F+Z+ (and their − mirrors) exist.
- (S1): B± = b∩α+∩γ−, b∩φ+∩α−.
- Every quad is all-8, so **every first segment at a quad is double**. This is used repeatedly.

## 1. Accounting in case (e)

Λ = π + U + ½ΣS° + K3 + 2K4 + ½Δ with π = 5, U = 0, ΣS° = K3 = K4 = 0. So **Δ = 2**.

**Costs.**
- An **M\* failure** (a single edge of an all-multiple triangular face) puts 2 tokens in the residual set.
- An **O\* failure** (a face with multiple Q, Q′ and simple X, with QX and Q′X single) puts 2 tokens in the residual
  set.
- Tokens on different single edges are distinct: a single edge determines its unique face.

By (I5), **at most one O\*/M\* feature exists anywhere**. Any derivation that produces a second such feature on a
different edge gives Δ ≥ 4, a contradiction.

One-token items (B*, Δ_Z slots, untyped residual tokens) are never O*/M* features. So two 1-token events cannot
break any checkpoint below.

## 2. Δ-inventory of the short star theorem

### 2.1 Checkpoints

**Symmetry.** The labelled star skeleton is invariant under the Klein group generated by y ↦ −y and x ↦ −x, both
reflections of the abstract star.
- y ↦ −y swaps A+↔F+, C−↔A−, B+↔B−, a↔c, α+↔φ+, γ−↔α−, Y±↔Z±, U+↔U+′, U−↔U−′, e1↔e2, e3↔e4.
- x ↦ −x swaps A+↔C−, F+↔A−, a↔c, α+↔γ−, φ+↔α−, Y+↔Z−, U+↔U−, U+′↔U−′, e1↔e4, e2↔e3.

The group acts simply transitively on the four **corners**:

| corner | kite corner | bridge | apex | return | apex line | V-face tip |
|---|---|---|---|---|---|---|
| (+,a) | A+ | B+ | Y+ = a∩φ+ | U+ = D+∩γ− | e1 | W2+ = a∩e2 |
| (+,c) | F+ | B− | Z+ = c∩α+ | U+′ = D+∩α− | e2 | W1+ = c∩e1 |
| (−,c) | C− | B+ | Z− = c∩α− | U− = D−∩α+ | e4 | W1− = c∩e3 |
| (−,a) | A− | B− | Y− = a∩γ− | U−′ = D−∩φ+ | e3 | W2− = a∩e4 |

The **checkpoints at (+,a)** are listed below. The other 18 are their images.

| name | statement | if false |
|---|---|---|
| Y1 | Y+ is multiple | O*(T+A+Y+): tokens on T+Y+ and A+Y+, by (I6) |
| Y2 | T+Y+ is double | M*(T+A+Y+), on T+Y+ |
| Y3 | A+Y+ is double | M*(T+A+Y+), on A+Y+ |
| B5 | A+B+ is double | M*(P A+ B+), on A+B+ |
| VY | V+ multiple ⇒ V+Y+ is double | M*(T+V+Y+), on V+Y+ |
| UY | U+ multiple ⇒ Y+U+ is double | M*(A+Y+U+), on Y+U+ |

At (+,c) the checkpoints are Z1, Z2, Z3, B6 (F+B− double), VZ and UZ (Z+U+′ double).

### 2.2 Derived facts at the + end, and what they use

- **(D1) T+ full ⟸ Y1, Y2, Z1, Z2.**
  - T+'s sectors (T+Z+, T+V+) and (T+V+, T+Y+) are faces iff T+Z+ and T+Y+ are double.
  - Then the faces T+Z+V+ and T+V+Y+ exist and T+V+ is double.
- **(D2) A+ full ⟸ Y3, B5.**
  - The faces A+Y+U+ and A+U+B+ exist, with U+ the first vertex on A+→(−D+).
  - At B+ the face A+U+B+ lies in B+'s sector (B+→(−γ−), B+A+). So U+ = D+∩γ− is the vertex next to B+ on γ−,
    beyond B+.
  - Likewise F+ full ⟸ Z3, B6.
- **(D3) Y+ is not a quad ⟸ B5** (Addendum 4, plus Lemma 2.1 below).
  - If V+ is simple, use Lemma 2.1.
  - If V+ is multiple and Y+ is a quad:
    - Y+ is all-8. The faces T+A+Y+ and T+V+Y+ exist, since Y+T+ is double.
    - Y+A+, Y+T+, Y+V+ are three consecutive bridges. So Y+ has the double-B mask with Y+T+ in the middle.
    - Y+A+ is double, so A+'s sector (A+Y+, A+→(−D+)) is the face A+Y+U+. So Y+U+ is the block next to Y+A+, and U+
      is a simple centre on D+ and on Y+'s fourth line.
    - B5 gives the face A+U+B+, which puts U+ on γ− as well. Neither D+ nor γ− passes through Y+.
    - So U+ is on three lines. Contradiction.
  - Mirror: Z+ is not a quad ⟸ B6.
- **(D4) V+ multiple ⟸ D1, Y3, Z3** (STAGE2_TASK7 §4, quad branch replaced by Lemma 2.1).
  - Suppose V+ is simple, with non-H line E. By Lemma 2.1, Y+ and Z+ are triples, and by D1 both lie on E.
  - Y3 gives the face A+Y+U+ in Y+'s sector (Y+→(−E), Y+A+), so U+ ∈ E. Z3 gives U+′ ∈ E.
  - U+ and U+′ are distinct points of D+, so E = D+. But D+∩H = X+ ≠ V+.
- **(D5) Pin 5 ⟸ D1, D2, D3.** Y+ is a triple whose third line e1 contains V+ (face T+V+Y+) and U+ (face A+Y+U+).
  So U+ ∈ D+∩γ−∩e1 is multiple. Mirror for U+′ ∈ D+∩α−∩e2.
- **(D6) V+ is not a quad ⟸ (B5 ∧ Y3) ∨ (B6 ∧ Z3).** This is Lemma 2.2: STAGE2_TASK8 §3, run on either side.
- **(D7) The four forced faces.** Given D1, D4 and D6, V+ is a triple with the ring of §0.
  - VZ ⇒ face V+Z+W1+ in V+'s sector (V+→(−e1), V+Z+). At the triple Z+ this face is in (Z+V+, Z+→(−c)). So
    **W1+ = c∩e1 is the vertex next to Z+ on c, beyond Z+**.
  - VY ⇒ face V+Y+W2+, so **W2+ = a∩e2 is next to Y+ on a, beyond Y+**.

**Lemma 2.1** (Δ-free; replaces STAGE2_TASK7 §4's appeal to the Δ-dependent alternating exclusion, STAGE2_TASK6 §6).
*If V+ is simple, neither Y+ nor Z+ is a quad.*

*Proof.*
1. Let Y+ be a quad. It is all-8, so Y+T+ is double. Then T+'s sector (T+V+, T+Y+) is the face T+V+Y+, and the
   double segment Y+V+ ends at the simple V+. By (I1), V+ is a simple kite centre with four double rays.
2. V+T+ is double, so T+Z+V+ is a face. V+'s kite is (T+, Z+, W, Y+), with W the next vertex on H beyond V+.
3. If Z+ is a triple: the cap Z+T+ has the exterior face T+F+Z+. By (P4) at Z+, F+ lies on the line Z+W. So
   W ∈ c∩H = P. But W lies beyond V+, while P lies behind T+. Contradiction.
4. So Z+ is a quad. K3 = 0 makes T+ and W triples. By (I4), Y+ is alternating (BRBRBRBR).
5. But the face T+A+Y+ makes Y+A+, Y+T+ two consecutive double rays to multiple vertices. Those are two consecutive
   bridges, which BRBRBRBR forbids. Contradiction.
6. The case of Z+ a quad is the mirror. ∎

**Lemma 2.2** (STAGE2_TASK8 §3 needs only one + corner). *If B5 and Y3 hold (or B6 and Z3), V+ is not a quad.*

*Proof.*
1. Suppose V+ is a quad. It is all-8, so V+T+, V+Y+, V+Z+ are double, and the faces T+Z+V+ and T+V+Y+ exist.
2. Y+ is multiple. Otherwise Y+V+ would be a kite block, Y+ a four-fan centre, and Y+T+ double, contradicting (I6).
   Likewise Z+.
3. So V+Z+, V+T+, V+Y+ are consecutive bridges. V+ is double-B with V+T+ in the middle, and Y+, Z+ are triples by
   (I2). Write g for V+'s case-B axis. The ring is V+Z+, V+T+, V+Y+, g, −e2, −H, −e1, −g.
4. Take the case-B kite (V+, Y+, R, K), where K is the first vertex on V+→(−e2).
   - By (P4) at Y+ (exterior face T+V+Y+), R ∈ φ+ beyond Y+.
   - Y+'s kite rays are Y+V+, Y+→(−a) (the diagonal) and Y+R = Y+→(−φ+). So the face across the double cap Y+R lies
     in (Y+R, Y+→(−e1)). Its apex is the first vertex on Y+→(−e1).
   - By Y3, that first vertex is U+ (face A+Y+U+). By (P4) at R, U+ lies on R's other cap line ℓ = RK.
   - By (P4) at K (exterior face V+ K T_v in V+'s sector (−e2, −H)), T_v ∈ ℓ, where T_v is the next vertex on H
     beyond V+.
5. U+ ∈ D+, γ− (by B5), e1, ℓ. These lines meet H at X+, T−, V+, T_v, which are distinct. So U+ is a quad.
6. U+ is all-8, and U+B+, U+A+, U+Y+ are consecutive bridges. So the double-B block axis at U+ is its fourth line ℓ.
7. But U+R is an edge on ℓ (face Y+RU+) with R multiple, so it is a bridge. Contradiction.
8. With B6 and Z3, use the kite at Z+. ∎

## 3. Verification of the two routes

### 3.1 What each step uses

The quad case of Lemma R is all-8, so its own bridges are double without saturation.

**R(U+′)** (U+′ quad ⇒ ⊥):
- (+,c): Z1, Z3, B6. These give the faces F+U+′B− and F+Z+U+′, hence three consecutive bridges at U+′.
- Kite at Z+: (P4) puts its far corner on c beyond Z+, on c's + side.
- Kite at B−: (P4) puts its far corner next to B− on φ+, beyond B−. B5− identifies it as U−′.
- Its line d is U−′'s third line e3. This uses D5−: Y1−, Y2−, Y3−, B5−. Note d ≠ D− (D−∩α− = A−) and d ≠ φ+
  (φ+∩α− = B−).
- e3∩c lies beyond Z−. This uses D7−: V− triple (D1−, D4−, D6−), VZ−, and Z− triple (B6−).

**R(U−)** is the x ↦ −x mirror of R(U+′):
- (−,c): Z1−, Z3−, B6−.
- The **donor** is U+ at (+,a): B5 makes U+ the far corner; D5 (Y1, Y2, Y3, B5) puts U+ on e1.
- c∩e1 lies on the + side. This uses D7: V+ triple and VZ, together with D1, D4, D6 and B6.

**R(U+)**: the y ↦ −y mirror of R(U+′). It uses (+,a) for its own faces, (−,c) as donor, and VY−.

**R(U−′)**: the y ↦ −y mirror of R(U−). It uses (−,a), donor (+,c), and VY.

**M1** (U+′ and U− not both triple):
- The F+ and C− faces, Z± triple, and UZ, UZ−.
- The rings at U+′ and U−.
- The α+-order U− B+ A+ T+ Z+, from the faces C−U−B+ (B6−) and T+F+Z+.

**M2**: the mirror, using UY, UY−.

### 3.2 Usage table (+ end; the − end is the x ↦ −x mirror)

| checkpoint | Route 1 = R(U+′) + R(U−) + M1 | Route 2 = R(U+) + R(U−′) + M2 |
|---|---|---|
| Y1, Y2 | donor: T+ full ⇒ V+ ∈ e1 (D1, D5); V+ triple | own corner + V+ |
| Y3 | donor: U+ ∈ e1 (D5); D4 | own: face A+Y+U+ |
| B5 | donor: U+ is the far corner of U−'s B+-kite; D3, D6 | own: face A+U+B+ |
| **VY** | **not used** | face V+Y+W2+ (R(U−′)) |
| **UY** | **not used** | M2+ |
| Z1, Z2, Z3, B6 | own corner + V+ | donor (mirror) |
| **VZ** | face V+Z+W1+ (R(U−)) | **not used** |
| **UZ** | M1+ | **not used** |

### 3.3 Verdict on the lead's claim

**Verified: the claim is TRUE.** A failure of VY±, UY± leaves Route 1 intact, and a failure of VZ±, UZ± leaves
Route 2 intact. The proof is in §4.5.

**Correction to the list of shared facts.**
- **Shared:**
  - P's mask and B± triple (Δ-free);
  - T± full (Y1, Y2, Z1, Z2);
  - **A±, F+, C− full** (Y3, Z3, B5, B6 at both ends), missing from the lead's list;
  - **Y±, Z± triple**, which follows from these;
  - V± triple, together with the faces TZV and TVY. These are not independent: they follow from the corner
    checkpoints by D1, D4 and D6.
- **Not shared:** the faces V±Z±W1± (Route 1 only, via VZ±) and V±Y±W2± (Route 2 only, via VY±). The lead's list
  counted these as shared.
- So the shared checkpoints are exactly **Y1, Y2, Y3, B5 at each a-corner and Z1, Z2, Z3, B6 at each c-corner**.
  Up to symmetry this leaves four shared sub-cases (§4.1–§4.4) and two route-specific ones (§4.5).

## 4. Sub-cases

By the Klein symmetry, assume the failed checkpoint is at corner (+,a). Every other checkpoint holds, and every
derived O*/M* feature on another edge is forbidden (§1). The − end is untouched, so D1–D7 hold there.

### 4.0 B± non-triple: impossible

- B± are first neighbours of a zero double-B star. STAGE2_TASK5 §3 excludes a quad there using only S° = 0 (mask
  classification, the case-B exterior faces, and (P4)).
- B± are multiple, because rays 2 and 6 of the mask are bridges.
- So **B± are triples for any Δ**. PROVED.
- The faces PA+B+, PB+C−, PA−B−, PB−F+ exist (P is all-8). Only their saturation can fail: that is B5 and its
  images (§4.3).

### 4.1 Lemma A (T+V+ forced single), and sub-cases Y1, Y2

**Lemma A.** Assume Z1 and Z2 hold and T+Y+ is single. Then Δ ≥ 4, counting the tokens on T+Y+.

*Proof.*
1. T+Y+'s only face is T+A+Y+, in the sector (T+Y+, T+A+). So the sector (T+V+, T+Y+) is not a face.
2. Z2 makes the sector (T+Z+, T+V+) the face T+Z+V+. So **T+V+ is single**.
3. *V+ multiple.* T+Z+V+ is all-multiple (Z1) with T+V+ single. M* gives 2 tokens on T+V+.
4. *V+ simple, Z+V+ single.* O*(T+Z+V+) gives tokens on T+V+ and Z+V+.
5. *V+ simple, Z+V+ double, Z+ a triple.*
   - By (P2), with the faces T+F+Z+ and T+Z+V+, the second face on Z+V+ is in Z+'s sector (Z+V+, Z+→(−c)).
   - At V+ it is in (V+Z+, V+→(−H)), since the neighbours of V+Z+ in V+'s 4-ring are V+T+ and V+→(−H).
   - Its apex is c∩H = P, which lies on Z+→F+. Wrong ray: contradiction.
6. *V+ simple, Z+ a quad.* Z+V+ is a zero-quad block, so V+ is a kite centre (I1) and T+V+ is double.
   Contradiction.
7. In cases 3–4 the new tokens lie on T+V+ or Z+V+, not on T+Y+ or A+Y+. So Δ ≥ 4. ∎

**Sub-case Y1 fails (Y+ simple, O\* at T+).** By (I6), T+Y+ is single, and Z1 and Z2 hold. Lemma A gives Δ ≥ 4.
**PROVED impossible.** The same holds for Z+ simple and for Y−, Z− simple, by symmetry.

**Sub-case Y2 fails (T+Y+ single, Y+ multiple).** Lemma A again gives Δ ≥ 4. **PROVED impossible.** Mirrors: T+Z+,
T−Y−, T−Z− single.

This covers every event that makes **T± not full**. It also covers a missing face TVY or TZV, and T+V+ single: for
T+V+ single, T+ must lack a face on one side, so Y2 or Z2 has failed.

### 4.2 Sub-case Y3 fails (A+Y+ single, Y+ multiple): the face A+Y+U+ is missing

1. **Y+ is a triple.** A quad Y+ would be all-8, making Y+A+ double.
2. **U+ is simple.**
   - A+Y+'s only face is T+A+Y+, so A+'s sector (A+Y+, A+→(−D+)) is not a face.
   - B5 holds, so (A+→(−D+), A+B+) is the face A+U+B+. Hence A+U+ is single.
   - If U+ were multiple, A+U+B+ would be an all-multiple face with a single side: M* gives 2 more tokens.
3. U+ is still the vertex next to B+ on γ−, beyond B+ (D2's B+ part uses only B5).
4. **Route 1 survives:**
   - **R(U+′)** uses only (+,c), B−, and the − end (§3.1), all intact. So U+′ is a triple.
   - **U− is a triple.** If U− were a quad, its double-B kite at B+ would have, by (P4) at B+ (exterior face C−U−B+),
     its far corner at the vertex next to B+ on γ− beyond B+. That vertex is U+, which is simple. But case-B far
     corners are triples. Contradiction.
   - **Z+ is a triple.** If V+ is multiple, use D3's mirror (needs only B6). If V+ is simple, use Lemma 2.1.
   - **M1** uses only F+ and C− faces, Z± triple, UZ, UZ−, and the rings at the triples U+′ and U−. All are intact.
     It gives α+∩α− both beyond Z+ and beyond U− on α+. Contradiction.

**PROVED impossible.** V+ is never used here, so V+ simple (D4 may fail) does no harm.

### 4.3 Sub-case B5 fails (A+B+ single): the "B+ side" of A+

1. A+'s sector (A+→(−D+), A+B+) is not a face.
2. Y3 makes (A+Y+, A+→(−D+)) the face A+Y+U+, with U+ the first vertex on A+→(−D+). So **A+U+ is single**.
3. *U+ multiple:* M*(A+Y+U+) on A+U+ gives Δ ≥ 4.
4. *U+ simple, Y+ a quad:* Y+ is all-8, so Y+U+ is a block. Then U+ is a kite centre (I1) and A+U+ is double.
   Contradiction.
5. *U+ simple, Y+ a triple*, with third line e. Y+'s ring is Y+A+, Y+T+, e, −a, −φ+, −e, so Y+U+ = Y+→(−e).
   - *Y+U+ single:* O*(A+Y+U+) gives tokens on A+U+ and Y+U+. With the A+B+ tokens, Δ ≥ 4.
   - *Y+U+ double:* the second face on Y+U+ lies in (Y+→(−φ+), Y+U+) at Y+ and in (U+Y+, U+→(−D+)) at U+. Its apex
     is φ+∩D+ = F+, which lies on Y+→T+. Wrong ray: contradiction.

**PROVED impossible.** The proof uses only A+ and Y+. Mirrors: F+B−, C−B+, A−B− single.

### 4.4 Sub-cases at V+: its four forced faces

The face missing at V+ depends on the event:
- **TVY or TZV missing** ⇒ some Y1, Y2, Z1, Z2 fails. This is §4.1.
- **V+ simple.** By D4 this needs a failure of D1, Y3 or Z3. These are §4.1 and §4.2 and their mirrors, all closed.
- **V+ a quad.** By Lemma 2.2 this needs *both* (B5 ∧ Y3) and (B6 ∧ Z3) to fail, i.e. two failures, so Δ ≥ 4.
  Never possible.
- **VYW2 or VZW1 missing** ⇒ a VY or VZ failure (§4.5).

There is no other way for V+ to lose a forced face. **PROVED.**

### 4.5 The route-specific sub-cases (this proves the claim of §3.3)

- **VY fails** (V+Y+ single, so V+ is multiple).
  - V+ is not a quad, since all-8 would make V+Y+ double. So V+ is a triple.
  - Route 1 uses no VY (§3.2). It uses VZ, so it still has the face V+Z+W1+ and W1+ = c∩e1 next to Z+. All of
    Route 1's other inputs are intact.
  - So R(U+′), R(U−) and M1 run verbatim. Contradiction.
- **UY fails** (Y+U+ single, U+ multiple). Route 1 never uses Y+U+, and everything else is intact. Contradiction.
  (D6 even fails at once here: Lemma 2.2's quad U+ would be all-8, with Y+U+ double.)
- **Mirrors:** VZ± and UZ± failures are closed by Route 2, and VY− and UY− by Route 1.

**PROVED.**

### 4.6 Events that hit no checkpoint

Δ = 2 may instead come from other sources:
- a single O*/M* feature elsewhere;
- η0 (a bounded unused first ray);
- Δ_Z = 2;
- H* (a single central three-fan cap);
- B*;
- an extra single cap at a K0 or case-A K1 kite;
- e_mix (a single cap edge of a kite with ≥ 2 quad corners);
- untyped residual tokens.

In all of these, all 24 checkpoints hold. Before this note, the short star theorem's only non-local Δ-dependent input
was the alternating exclusion inside STAGE2_TASK7 §4. Lemma 2.1 removes it. So the theorem applies **verbatim**,
whether the event lies in another cluster or in a path. **PROVED.**

## 5. Theorem E

**Theorem E** (case (e), n = 18, the structural class, ΣS° = 0, K3 = K4 = 0, Δ = 2, any U). *No isolated
double-case-B star exists.*

*Proof.* By §1, at most one checkpoint fails. If none fails, §4.6 applies. If one fails, by symmetry it is at
(+,a): it is closed by §4.1–§4.3 (shared) or §4.5 (route-specific). B± triple and P's mask are Δ-free (§4.0). The
derived facts at V± are covered by §4.4. ∎

**Corollaries.**
- **Case (d).** In case (d) (ΣS° = 1, Δ = 1), the Δ-part alone cannot break any star checkpoint, since each costs 2.
  The S° = 1 quad still needs its own treatment.
- **Required credit.** With ΣS° = 0 and K3 = K4 = 0, a star forces Δ ≥ 4.
  - Δ is even, because ΣS° + Δ is even.
  - Theorem 0 excludes Δ = 0, and Theorem E excludes Δ = 2.
  - Locally: a Y1 or Y2 failure already costs 4 (Lemma A), and a B5 failure costs 4 or gives a contradiction.
  - This is not needed for W = 13.

## 6. Interaction with Theorem 0's chain

What Theorem E uses from the cluster chain:
- the cluster reduction (I3), which is Δ-free;
- the zero masks, STAGE2_TASK5 §§1–3, and ALL8_NOTE3 §8 propagation, all Δ-free.

STAGE2_TASK8 §§6–9 (five-run, S after a full V, terminal S) and STAGE2_TASK8 §7, Lemma Q and Pin 6 (η0) are **not
needed**.

## 7. Path clusters in case (e): where Δ = 0 is used (notes only)

A case-(e) 94 has an all-8 point (given). By Theorem E it lies in a mixed path cluster (k = 2, 3, 4). The path
exclusions use Δ = 0 at these points.

**Δ-free:**
- STAGE2_TASK5 §4: n ≥ 3k+5+b.
- **STAGE2_TASK7 §3, the B–B two-quad path.** The faces PAB, PFC, QRE and QSG come from all-8. A, B, R, E are
  triples by case B and K3 = 0. The rest is (P4). **So the k = 2, b = 2 path is excluded in case (e): PROVED.**
- Lemma 2.1 also repairs STAGE2_TASK7 §4 at path boundaries.

**Δ-dependent:**
- **STAGE2_TASK6 §2.** An alternating endpoint with a triple outward far corner has a K1A kite with ≥ 2 single caps,
  so V_K ≥ 2. With **Δ = 2 this is exactly affordable once**, and every later count that relies on it fails:
  - §3's "three additional axes";
  - §6's n ≥ 21 and the triangle of alternating endpoints.
- **STAGE2_TASK6 §3.** K2 caps double (e_mix): affordable once.
- **STAGE2_TASK6 §4.** Case-B endpoints use O* (Y, Z multiple) and M*. Lemma A and §§4.2–4.3 may transfer here, but
  this is not checked.

**OPEN:** mixed paths in case (e) with an alternating endpoint, or with k ∈ {3, 4}.

## 8. Orientation check (scratch only)

A symmetric straight-line model of the 14-line skeleton was used:
- P = 0; H: y = 0, a: y = x, b: x = 0, c: y = −x, D±: x = ±1;
- T± = (±13/10, 0), A+ = (1, 1), F+ = (1, −1), C− = (−1, 1), A− = (−1, −1);
- e1–e4 through the stated pairs.

What it reproduces:
- every skeleton line order of §0;
- the triple and quad incidences, including V± = H∩e∩e′ and G, G′;
- the rings of §0 at A+, T+, B±, Y+, Z+, U+, U+′, U−, V+, C−, Z−;
- all 22 faces used: TAY, TFZ, TZV, TVY, AUB, AYU, FU′B−, FZU′, VZW1, VYW2, the P-faces and the − mirrors.

The model's parallel pairs (α+∥α−, φ+∥γ−, e1∥e3, e2∥e4, b∥D±) are crossings at infinity. They match the fact that
M1 and M2 make the full zero corner impossible. The model checks orientations only; it is not a witness.

## 9. Summary

| claim | status |
|---|---|
| In case (e) at most one O*/M* checkpoint fails; 1-token events break none (§1) | PROVED |
| The short star theorem's Δ-uses are exactly the 24 corner checkpoints Y1–3, B5, VY, UY and their images, after Lemma 2.1 (§2) | PROVED |
| Lemma 2.1: V+ simple ⇒ Y+, Z+ not quad, Δ-free (replaces the alternating-exclusion input) | PROVED |
| Lemma 2.2: V+ quad excluded by either + corner alone | PROVED |
| Route claim: VY±, UY± are Route-2-only and VZ±, UZ± are Route-1-only; the other route survives (§3, §4.5) | PROVED |
| Correction: shared = Y1–3, B5 and Z1–3, B6 at both ends (adds A±, F+, C− full and Y±, Z± triple; removes VZW1, VYW2) | PROVED |
| B± non-triple is impossible for any Δ (§4.0) | PROVED |
| Y+ simple (O* at T+), or T+Y+ single ⇒ Δ ≥ 4 (Lemma A; mirrors) | PROVED |
| A+Y+ single ⇒ U+ simple ⇒ Route 1 closes (§4.2) | PROVED |
| A+B+ single ⇒ Δ ≥ 4 or wrong ray (§4.3) | PROVED |
| V+ loses a forced face only through the sub-cases above (§4.4) | PROVED |
| **Theorem E: no isolated double-B star in case (e)** | **PROVED** (hand proof, conditional on inputs (I1)–(I6), not yet refereed) |
| B–B two-quad path excluded in case (e) (STAGE2_TASK7 §3 is Δ-free) | PROVED |
| Mixed paths with an alternating endpoint, or k = 3, 4, in case (e) | OPEN |

# W = 14, pure-Δ case: isolated double-B stars with Δ = 4

These are hand proofs (2026-10-03). They have not been refereed, and this file is local only. One scratch script checked
ray directions in the caseE §8 straight-line model (§1.7). That model is not a witness.

## Result

- **New lemma, Δ-free: Lemma UM, the uniform M-lemma (§1).** Define two sets of six edges:
  - Σ_c = {F+Z+, F+B−, Z+U+′, C−Z−, C−B+, Z−U−};
  - Σ_a = {A+Y+, A+B+, Y+U+, A−Y−, A−B−, Y−U−′}.

  In caseE's names, Σ_c is Z3, B6, UZ at the two c-corners, and Σ_a is Y3, B5, UY at the two a-corners.
  - **If every edge of Σ_c is double, the star does not exist. The same holds for Σ_a.**
  - Quad returns are handled inside the lemma.
  - The lemma does not use Lemma R, Lemma Q, STAGE2_TASK8 §7, V±, T± full, or the checks Y1, Y2, VY, VZ.
- **Corollary 1.6.** Every isolated double-B star with ΣS° = 0 and K3 = K4 = 0 has **Δ ≥ 4**. This gives the star
  parts of Theorem 0 and of Theorem E (W13_caseE) in one line each.
- **Δ = 4 (this case).** A surviving star has exactly one single edge in Σ_a and exactly one in Σ_c. Each costs exactly
  2 tokens, and there is no other feature anywhere. Up to the Klein group, seven configurations C1–C7 remain (§2.3).
- **PROVED:**
  - all of the brief's family (i): each shared failure together with its forced partner;
  - every pair in (ii) or (iii) that involves VY± or VZ±, or that has both failures on the same side;
  - **C1** (Y3 and Z3 at the same end, with both returns simple);
  - **C7** (Y+ and Z+ both simple).
- **OPEN: C2, C3, C4, C5, C6.** Each is one a-side unit plus one c-side unit:
  - the a-side unit is "Y3 with a simple return" or "UY", at an a-corner;
  - the c-side unit is "Z3 with a simple return" or "UZ", at a c-corner.

  §5 gives the forced structure and §6 the exact open statements.

## 0. Setting

- **The budget.** W = 14 gives π = 4. A 94 has Λ = 6 = π + U + H, where H = ½ΣS° + K3 + 2K4 + ½Δ (W13 §0). In the
  pure-Δ case U = 0, ΣS° = 0 and K3 = K4 = 0, so **Δ = 4**.
- **Paths are excluded.** Lemma SB′ (Δ-free) rules out single-B stars, so both endpoints of a path are alternating.
  Corollary AE′ charges each such endpoint Δ ≥ 4, giving Δ ≥ 8. So every quad is an isolated double-B (DB) star, all-8
  with the DB mask. Fix one, P.
- **Notation.** This follows caseE §0 and SOL_TASK8 Addendum 5. The points that the Δ = 0 skeleton identifies as
  intersections are defined here as **first vertices**, so that the definitions survive failures:
  - U+, U+′, U−, U−′ are the first vertices on A+→(−D+), F+→(−D+), C−→(−D−), A−→(−D−).
  - Y+ and Z+ are the first vertices on T+→(−φ+) and T+→(−α+). The exterior faces T+A+Y+ and T+F+Z+ make them a∩φ+
    and c∩α+. Y− and Z− are defined in the same way.
  - G and G′ are the first vertices on B+→(−b) and B−→(−b). V± are the first vertices on T±→H±.
- **Token bound.** By NOTE5 (5), Δ ≥ 2η0 + |H\*| + |M\*| + |O\*| + |B\*| + V_K. The token sets are disjoint, and each
  token lies on a single edge, which determines its unique triangle. Here at most four tokens exist.
- **Features.** A *feature* is one of:
  - a single edge of an all-multiple triangle (M\*, 2 tokens);
  - an O\* triangle (2 tokens, or 4);
  - a bounded unused first ray at a multiple point (η0, worth 2).
- **Δ-free inputs** (as in caseE §0):
  - (I1) masks and kite blocks; (I2) B± are triples; (I4);
  - (I6) the wrong-ray lemma at the apices;
  - (P1)–(P4), where (P4) is STAGE2_TASK7 §2;
  - K3 = 0.
- **Δ-free faces and points:**
  - the faces at P, the kite faces, and the exterior faces T+A+Y+, T+F+Z+, T−C−Z−, T−A−Y−;
  - A±, F+, C−, T± and B± are triples, and X± are simple.

## 1. Lemma UM

### 1.1 Apex lemma
**Lemma 1.1.** Suppose F+Z+ is double. Then:
- Z+ is a triple. Write e2 for its third line.
- Its ring is Z+F+ (c), Z+T+ (α+), e2, −c, −α+, −e2.
- The face across F+Z+ from T+F+Z+ is F+Z+U+′, and U+′ is the first vertex on Z+→(−e2).

The Klein images hold at Y+, Z− and Y−.

*Proof.*
1. Z+ is multiple, by (I6).
2. **Suppose Z+ is a quad.** Then it is all-8. Z+F+ and Z+T+ are consecutive bridges (face T+F+Z+). F+Z+ is double,
   so the face F+Z+U+′ exists and Z+U+′ is the other neighbour of Z+F+.
   - (a) **U+′ simple.** Z+U+′ is a block, so U+′ is a kite centre (I1) and all four of its rays are double.
     - F+U+′ is double, so F+'s sector (U+′, B−) is a face. Hence U+′ is the first vertex on B−→(−α−).
     - So U+′ lies on D+, on α− and on the line Z+U+′.
     - These three lines are distinct: the line Z+U+′ passes through Z+ ∈ c, while D+∩c = F+ and α−∩c = Z−.
     - A simple point cannot lie on three lines ✗.
   - (b) **U+′ multiple.** Then Z+U+′, Z+F+, Z+T+ are three consecutive bridges. So Z+ is DB with Z+F+ in the middle,
     and the ray after Z+T+ is a block.
     - The face in that sector lies at T+ in the sector (T+Z+, T+→H+). So V+ is that block's simple kite centre, with
       all four rays double.
     - T+V+ is double, which gives the face T+V+Y+. So V+'s kite is (T+, Z+, W, Y+), where W is the next vertex on H.
     - Y+ is not simple: its cap T+Y+ is double, which (I6) forbids.
     - If Y+ is a triple: (P4) at Y+, with exterior face T+A+Y+, puts W on a. So W = a∩H = P. But W lies beyond V+ ✗.
     - If Y+ is a quad: W is a triple because K3 = 0, so Z+ is alternating by (I4). But Z+ is DB ✗.
3. **The ring and the face.** The ring is alternation at a triple. The face F+Z+U+′ lies in the sector beside Z+F+
   other than (F+, T+), namely (−e2, F+). ∎

### 1.2 Half-lemma at (+,c)
**Lemma 1.2.** If F+Z+, F+B− and Z+U+′ are double, then α+∩α− is the first vertex on U+′→(−α−), and it lies on
Z+→(−α+).

*Proof.*
1. **U+′ is multiple.**
   - By Lemma 1.1, Z+ is a triple and U+′ is the first vertex on Z+→(−e2).
   - The face F+U+′B− exists because F+B− is double. It makes U+′ the first vertex on B−→(−α−).
   - So U+′ lies on D+, α− and e2. These lines are distinct (e2 ∋ Z+, D+∩c = F+, α−∩c = Z−), so U+′ is multiple.
   - Its rays toward B−, F+ and Z+ are consecutive (faces F+U+′B− and F+Z+U+′).
2. **The face Φ.** Let Φ be the face across Z+U+′ from F+Z+U+′; it exists because Z+U+′ is double. At Z+ the
   neighbours of −e2 are c and −α+, so Φ lies in the sector (−α+, −e2). Its vertex next to Z+ is the first vertex on
   Z+→(−α+).
3. **U+′ a triple.** Its ring is α− (B−), D+ (F+), e2 (Z+), −α−, −D+, −e2. The neighbours of U+′Z+ are U+′F+ and −α−,
   so Φ lies in (U+′Z+, −α−). Its third vertex is the first vertex on both U+′→(−α−) and Z+→(−α+), so it is α+∩α−.
4. **U+′ a quad.** It is all-8 with three consecutive bridges, so it is DB with U+′F+ in the middle. Its ring is
   α−, D+, e2, d, −α−, −D+, −e2, −d, where d is the block axis.
   - Its kite at the block d after U+′Z+ has corners Z+ and K, where K is the first vertex on U+′→(−α−).
   - Φ is the kite triangle U+′Z+X, where X is the simple centre. By step 2, X is the first vertex on Z+→(−α+).
   - Z+ and K are opposite corners of the kite, so Z+, X and K are collinear on the line Z+X, which is α+.
   - Hence K = α+∩α− lies on Z+→(−α+), beyond X. ∎

**Lemma 1.3 (the z-image).** Here z = x∘y exchanges (+,c) ↔ (−,c), α+ ↔ α−, F+ ↔ C−, B− ↔ B+ and U+′ ↔ U−. If
C−Z−, C−B+ and Z−U− are double, then α+∩α− is the first vertex on U−→(−α+), and it lies on Z−→(−α−).

### 1.4 Theorem UM
**Theorem 1.4.** If every edge of Σ_c is double, the star does not exist. The same holds for Σ_a.

*Proof.*
- On α+ the vertices U−, B+, A+, T+, Z+ are consecutive:
  - U− is the first vertex on B+→(−α+), by the face C−U−B+;
  - B+A+ is an edge, by the face PA+B+;
  - A+T+ is a kite cap;
  - T+Z+ is an edge, by the face T+F+Z+.
- Lemma 1.2 puts α+∩α− on Z+→(−α+), and Lemma 1.3 puts it on U−→(−α+). These rays are disjoint, one at each end of
  α+ ✗.
- For Σ_a, use the y-image:
  - φ+∩γ− lies on Y+→(−φ+) and is the first vertex on U−′→(−φ+);
  - φ+ has the order U−′ B− F+ T+ Y+. ∎

This is STAR_CASES Lemma M without its hypothesis that the U are triples. Step 4 of Lemma 1.2 replaces Lemma R, Lemma Q
and STAGE2_TASK8 §7.

### 1.5 Cost of a single sextuple edge
**Lemma 1.5.** A single edge of Σ_a at (+,a) puts at least 2 tokens on edges of the a-side triangles T+A+Y+, PA+B+,
A+Y+U+ and A+U+B+.
- **A+Y+ single.** If Y+ is multiple, this is M\*. If Y+ is simple, it is O\*(T+A+Y+), with tokens on T+Y+ and A+Y+
  (I6).
- **A+B+ single.** This is M\*(PA+B+).
- **Y+U+ single while A+Y+ and A+B+ are double.** Then U+ lies on D+, γ− and e1, three distinct lines, so it is
  multiple. This gives M\*(A+Y+U+).

In every case the failing edge itself carries a token. The other corners are the Klein mirrors. The eight a-side and
eight c-side triangles are 16 distinct faces, so the a-side and c-side token sets are disjoint.

**Corollary 1.6.** Every isolated DB star with ΣS° = 0 and K3 = K4 = 0 (any U, any W) has Δ ≥ 4. In particular there
is none at Δ = 0 (Theorem 0) or at Δ = 2 (Theorem E).

### 1.7 Orientation check (scratch only)
In the caseE §8 model:
- Z+→(−α+) and U+′→(−α−) both point along (0.287, −0.958). U−→(−α+) and Z−→(−α−) point the opposite way.
- Y+→(−φ+) and U+→(−γ−) both point along (0.287, 0.958). U−′→(−φ+) and Y−→(−γ−) point the opposite way.

So each half-lemma's two rays meet at infinity in that model (α+∥α−, φ+∥γ−), and the + and − halves point apart.
This agrees with Lemmas 1.2–1.4.

## 2. Δ = 4: the reduction

### 2.1 Exact costs
By Theorem 1.4, a surviving star has a single edge in Σ_a and one in Σ_c. By Lemma 1.5 each costs at least 2 tokens,
the two token sets are disjoint, and the total is at most 4. Hence:

**(E)** exactly 2 tokens lie on a-side triangle edges and exactly 2 on c-side ones. There is no other feature anywhere:
no η0, and no further M\*, O\*, H\*, B\* or V_K token.

### 2.2 The a-side unit
**Lemma 2.2.** Assume (E). After applying z, assume a single Σ_a edge lies at (+,a). Then exactly one of the following
holds.
- **Y3s+.**
  - A+Y+ is single, Y+ is a triple, and T+Y+ and A+B+ are double.
  - U+ is simple, on D+ and γ−, and B+U+ is double.
  - Every other Σ_a edge is double.
- **UY+.** Y+U+ is single, U+ is a triple, and every other a-side triangle edge is double.
- **C7.** Y+ and Z+ are both simple, and T+ is the last vertex of H on the + side. The c-side unit is F+Z+, through
  O\*(T+F+Z+).

*Proof.*
- **A+B+ single.** M\*(PA+B+) uses both a-side tokens, and A+'s sector (−D+, B+) is not a face.
  - Suppose A+Y+ is double. Then the face A+Y+U+ has A+U+ single, and caseE §4.3 applies. One of these follows:
    - M\* on A+U+ (U+ multiple);
    - O\*(A+Y+U+) (U+ simple, Y+U+ single);
    - a contradiction: if U+ is simple and Y+U+ double, the wrong ray at F+; if Y+ is a quad, U+ is a kite centre.

    The first two need more a-side tokens ✗.
  - If A+Y+ is also single, that costs 2 more ✗.
- **A+Y+ single, A+B+ double, Y+ multiple.** M\* on A+Y+ uses the 2 tokens.
  - T+Y+ is double, since a single T+Y+ would add an M\*.
  - A+'s sector (Y+, U+) is not a face. So the face A+U+B+ has A+U+ single.
  - Then U+ is simple (else M\*(A+U+B+)), and B+U+ is double (else O\*(A+U+B+)).
  - Y+ is not a quad, since all-8 would make A+Y+ double. This is **Y3s+**.
- **A+Y+ single, Y+ simple.** O\*(T+A+Y+) uses the 2 tokens, and T+Y+ is single.
  - If T+Z+ is double, Lemma A (caseE §4.1) gives a feature on T+Z+V+. That triangle is neither a-side nor c-side ✗.
  - If T+Z+ is single and Z+ multiple, M\* on T+Z+ uses the c-side budget. Then Σ_c can have no single edge ✗.
  - So Z+ is simple, and O\*(T+F+Z+) is the c-side unit, with F+Z+ single.
  - T+'s ray H+ then lies in no face. η0 = 0 makes it unbounded. This is **C7**.
- **Only Y+U+ single.** U+ is multiple, and not a quad, since all-8 would make Y+U+ double. This is **UY+**. ∎

The c-side unit is the y-image of this. It is **Z3s** (F+Z+ single, U+′ simple) or **UZ** (Z+U+′ single), at (+,c) or
at (−,c).

### 2.3 The configurations
First apply z to put the a-unit at (+,a). Then y (for the same end) or x (for the diagonal) identifies mirror pairs.
"Diagonal" means (+,a) together with (−,c), the two corners at B+.

| | a-unit | c-unit | position | status |
|---|---|---|---|---|
| C1 | Y3s+ | Z3s+ | same end | **PROVED** (§4) |
| C2 | UY+ | UZ+ | same end | OPEN |
| C3 | Y3s+ | UZ+ (≅ UY+ & Z3s+) | same end | OPEN |
| C4 | Y3s+ | Z3s− | diagonal | OPEN |
| C5 | UY+ | UZ− | diagonal | OPEN |
| C6 | Y3s+ | UZ− (≅ UY+ & Z3s−) | diagonal | OPEN |
| C7 | Y+ simple | Z+ simple (F+Z+), H ends at T+ | same end | **PROVED** (§4) |

## 3. The brief's families

| brief | configuration | sextuple left intact | status |
|---|---|---|---|
| (i) | Y1 fails (Y+ simple), plus its Lemma A partner on T+Z+V+ | Σ_c | **PROVED** |
| (i) | Y2 fails (T+Y+ single, Y+ multiple), plus its partner | Σ_a and Σ_c | **PROVED** |
| (i) | T+ last on H with T+Y+, T+Z+ single, Y+ and Z+ not both simple | Σ_a or Σ_c | **PROVED** |
| (i) | Y3 fails with U+ multiple (partner M\* on A+U+) | Σ_c | **PROVED** |
| (i) | B5 fails, plus its partner (M\* on A+U+, or O\*(A+Y+U+)) | Σ_c | **PROVED** |
| (i) | Y3 fails with U+ simple: no partner is forced. With any second event outside Σ_c: | Σ_c | **PROVED** |
| (ii) | VY± or VZ± together with anything: these are not inputs of UM | the sextuple not hit | **PROVED** |
| (ii) | UY and UZ at the same end / on the diagonal | — | C2 / C5 OPEN |
| (iii) | two failures on the same side | the other sextuple | **PROVED** |
| (iii) | Y3s and Z3s at the same end | — | C1 **PROVED** |
| (iii) | Y3s and Z3s on the diagonal | — | C4 OPEN |
| (iii) | Y3s and UZ, or UY and Z3s | — | C3, C6 OPEN |
| (iii) | Y and Z both simple at one T | — | C7 **PROVED** |

The Klein images carry the same status.
- **In (i)** the stronger conclusion holds: the forced partner never touches the other sextuple, so no third failure is
  needed.
- **In (ii) and (iii)** two failures do suffice to break both sextuples. C2–C6 are exactly the pairs that this note
  cannot close.

## 4. Closed cases: C1 and C7

**Lemma 4.1 (simple return).** Suppose A+B+ is double, A+U+ is single, U+ is simple and B+U+ is double. Then G is the
first vertex on U+→(−D+), so **G = b∩D+**, lying on B+→(−b).

*Proof.*
- U+ is the first vertex on B+→(−γ−), by the face A+U+B+. So U+ ∈ D+∩γ−, and its ring is A+ (D+), B+ (γ−), −D+, −γ−.
- The face across B+U+ from A+U+B+ lies at U+ in (U+B+, −D+). At B+, whose ring is A+, P, C−, −α+, −b, −γ−, it lies
  in (−b, −γ−).
- So its third vertex is on U+→(−D+) and on B+→(−b). ∎

The mirror at (+,c): if F+B− is double, F+U+′ single, U+′ simple and B−U+′ double, then G′ = b∩D+, lying on
U+′→(−D+).

**C1 (Y3s+ and Z3s+).**
- By Lemma 2.2, U+ is simple and B+U+ is double. By its y-image, U+′ is simple and B−U+′ is double.
- So Lemma 4.1 applies at both corners. The point b∩D+ then lies both on B+→(−b) and on B−→(−b), which are on opposite
  sides of P ✗. **PROVED.** The z-image (Y3s− and Z3s−) is the same.

**C7.**
- O\*(T+A+Y+) makes A+Y+ single, and B5 holds by (E). So the face A+U+B+ has A+U+ single.
- Then U+ is simple (else M\*) and B+U+ is double (else O\*(A+U+B+)). The same holds at F+.
- Lemma 4.1 at both corners gives the contradiction of C1. **PROVED.**

Orientation check: in the model, B+→(−b) and U+→(−D+) both point along (0, 1), and B−→(−b) and U+′→(−D+) along
(0, −1).

## 5. Forced structure in C2–C6
Throughout, (E) holds and the units are as in §2.3.

**5.1 T, Y, Z and V.**
- **T±, Y±, Z±.** T± are full, since a single T-edge would be a further token. Y± and Z± are triples (Lemma 1.1 and
  Lemma 2.2). Their third lines are e1–e4.
- **An end with no Y3s/Z3s unit.** There V is a triple with the four faces TZV, TVY, VZW1 and VYW2:
  - V is not simple (caseE D4);
  - V is not a quad (caseE Lemma 2.2, which needs only one intact corner, and one is always intact);
  - VY and VZ are double, else M\* on TVY or on TZV.
- **An end carrying one Y3s/Z3s unit** (+ in C3, C4, C6; − in C4). There V is either such a triple, or **simple** on a
  line E. In the simple case:
  - E is the third line of both apices, and E passes through the other corner's return (U+′ for Y3s+);
  - V+Y+ and V+Z+ are single, by the wrong ray (apex a∩H = P, resp. c∩H = P);
  - this costs no token, because T+V+ is double.

**5.2 Returns.** Every return that is not simple by definition is a triple.
- **A UY or UZ return** is not a quad: all-8 would make the failing edge double.
- **U− is not a quad if U+ is simple** (C3, C4, C6). By (P4) at B+, U−'s B+-kite has far corner U+, and far corners are
  triples. The mirror holds with + and − exchanged.
- **U+′ is not a quad.**
  - Its B−-kite has far corner U−′ (face A−U−′B−). That corner is a triple D−∩φ+∩e3, since (−,a) is intact.
  - Its axis passes through U−′ and is neither D− (D−∩α− = A−) nor φ+ (φ+∩α− = B−). So the axis is e3.
  - The far corner of its Z+-kite lies on Z+→(−c), by (P4) with the face F+Z+U+′.
  - But c∩e3 is W1−, which lies on Z−→(−c) (V− a triple, face V−Z−W1−), or it is Z− (V− simple, e3 = E′) ✗.
- **U−′ is not a quad.**
  - Its far corner U+′ is a triple, so its axis is e2.
  - The far corner of its Y−-kite then puts a∩e2 on a−.
  - But a∩e2 is W2+ on a+ (V+ a triple) or Y+ (V+ simple) ✗.
- **U− is not a quad when U+ is a triple** (C2).
  - The axis is then e1, which puts c∩e1 beyond Z−.
  - But c∩e1 is W1+ ✗.

| case | simple returns | triple returns |
|---|---|---|
| C2, C5 | — | U+, U+′, U−, U−′ |
| C3, C6 | U+ | U+′, U−, U−′ |
| C4 | U+, U− | U+′, U−′ |

**5.3 The fans at B±.**
- **B+ is full**, and G is a triple. Each line through G comes from the face across B+U±: at a triple return, from the
  return's third line; at a simple return, from Lemma 4.1 or its x-image.
  - In C2 and C5, G = b∩e1∩e4.
  - In C3 and C6, G = b∩D+∩e4.
  - In C4, G = b∩D+∩D−.
- **G is not a quad.**
  - In C3, C4 and C6, GU+ would be a block. That makes U+ a kite centre, which forces A+U+ double.
  - In C2 and C5, G would be DB with the bridges GU−, GB+, GU+. Its case-B kite at U+ would have a double cap along
    U+→(−γ−), which forces Y+U+ double.
- **Further faces at G.**
  - C2, C5: the faces U+K2G and U−GL2. Here K2 = D+∩e4 is next to U+ on D+, and L2 = D−∩e1 is next to U− on D−.
  - C3, C6: the face GK0U−, where **K0 = D+∩D−** is the first vertex on G→(−D+) and on U−→(−D−).
  - C4: **D+∩D− = G**. GU+ and GU− are single by the wrong ray: their second faces would need C− (resp. A+) on
    G→(−D−) (resp. G→(−D+)).
- **B− is full**, and G′ = b∩e2∩e3 is a triple in all five cases. There are faces B−U+′G′, B−U−′G′, U+′K1G′ with
  K1 = D+∩e3, and U−′L1G′ with L1 = D−∩e2.
- **G′ is not a quad.**
  - In C2 and C3, G′'s case-B kite at U+′ would have a double cap along U+′→(−α−), forcing Z+U+′ double.
  - In C4–C6, G′ would be a second isolated DB star. Its corner U−′ has apex Y− (exterior face Y−N′U−′), bridge B− and
    return A−.
  - Its sextuple through U−′ is {U−′Y−, U−′B−, Y−A−} together with three edges at the opposite kite corner D+∩e3,
    which lies on D+ beyond U+′.
  - None of these six edges is one of P's two failing edges. Any other single edge would carry a new token. So
    Theorem 1.4, applied to G′, rules it out.

**5.4 Intact half-lemmas.**
- **C2, C3.** The − end is intact. Lemma 1.3 and its y-image give the faces Z−M′U− and Y−N′U−′:
  - M′ = α+∩α− is the first vertex on U−→(−α+) and on Z−→(−α−);
  - N′ = φ+∩γ− is the first vertex on U−′→(−φ+) and on Y−→(−γ−).
- **C4, C5, C6.** The corners (+,c) and (−,a) are intact, giving the faces Z+MU+′ and Y−N′U−′:
  - M = α+∩α− lies on the + side, on Z+→(−α+) and U+′→(−α−);
  - N′ lies on the − side, as above.

**5.5 η0 pins at the broken corners.** Each listed ray is either unbounded, so that its line ends at that vertex, or it
lies in the stated triangle. In such a triangle:
- the edge along the ray is single, so the triangle's other two vertices are not both multiple (else M\*);
- if its simple vertex has both triangle edges single, that is O\*, so one of those edges is double.

The pins:
- **UY+.** Y+→(−φ+) needs the face (−a, −φ+) = Y+W2+Q. U+→(−γ−) needs the face (−γ−, −D+) = U+SK2.
- **UZ+.** Z+→(−α+) needs the face (−c, −α+). U+′→(−α−) needs the face (−α−, −D+) = U+′S′K1.
- **UZ−.** Z−→(−α−) needs the face (−c, −α−). U−→(−α+) needs the face (−α+, −D−), whose third vertex is L2 in C5 and
  K0 in C6.
- **Y3s+.**
  - Y+→(−e1) needs the face (−φ+, −e1).
  - A+'s sector (Y+, U+) is a non-triangular face Π_A. At U+ it occupies the sector (−γ−, A+).
  - If V+ is simple, Y+→(−a) also needs the face (−a, −φ+).
- **Z3s− (C4).** The x-image of Y3s+, with Π_C in C−'s sector (Z−, U−).
- **C4 at G.** G→(−D−) needs the face (−D−, −b), and G→(−D+) needs the face (−b, −D+).
- **C4 at G′.**
  - K1 is multiple, or K1 is simple with G′K1 single, U+′K1 double, and then **M ∈ e3**.
  - If G′K1 were double with K1 simple, b∩D+ would lie on B−→(−b). But b∩D+ = G ✗.
  - Mirror: L1 is multiple, or N′ ∈ e2.

## 6. The OPEN configurations, stated exactly

**Common to all five.**
- Δ = 4 is spent on exactly two M\* edges.
- T± are full, Y± and Z± are triples, and B±, G, G′ are as in 5.3. The returns are as in 5.2.
- Every other face of the Δ = 0 skeleton (Addendum 5) at an intact corner is present. This includes VZW1 and VYW2 at
  each end whose V is a triple.

**C2 (UY+ and UZ+).**
- The failing edges are Y+U+ and Z+U+′.
- The whole Addendum 5 skeleton is present: G = b∩e1∩e4, G′ = b∩e2∩e3, K1, K2, L1, L2.
- The − faces Z−M′U− and Y−N′U−′ are present.
- The faces across Y+U+ and across Z+U+′ are not triangles. The pins are those for UY+ and UZ+.
- What is missing is exactly the two + half-lemmas.

**C3 (Y3s+ and UZ+; equivalently UY+ and Z3s+).**
- The failing edges are A+Y+ and Z+U+′.
- U+ is simple. G = b∩D+∩e4, with the faces B+U+G, B+U−G and GK0U−.
- The − end is intact, with M′ and N′ as in C2.
- V+ is a triple, or simple on a line E ∋ Y+, Z+, U+′.
- The non-triangles are Π_A and the face across Z+U+′.

**C4 (Y3s+ and Z3s−).**
- The failing edges are A+Y+ and C−Z−.
- U+ and U− are simple and are two-fans at B+. G = b∩D+∩D−.
- M lies on the + side and N′ on the − side.
- V+ is a triple or simple (E ∋ Y+, Z+, U+′). V− is a triple or simple (E′ ∋ Y−, Z−, U−′).
- The non-triangles are Π_A, Π_C, and G's sectors (U+, −D−) and (−D+, U−). The C4 pins of 5.5 apply.

**C5 (UY+ and UZ−).**
- The failing edges are Y+U+ and Z−U−, the two return edges at the corners sharing B+.
- The full Addendum 5 skeleton is present, with M on the + side and N′ on the − side.
- The non-triangles are the faces across Y+U+ and across Z−U−.

**C6 (Y3s+ and UZ−; equivalently UY+ and Z3s−).**
- The failing edges are A+Y+ and Z−U−.
- U+ is simple. G = b∩D+∩e4, with the face GK0U−.
- M lies on the + side and N′ on the − side. V+ is a triple or simple; V− is a triple.
- The non-triangles are Π_A and the face across Z−U−.

**Why the local tools stop here.** The local contradictions available are:
- the half-lemmas (Lemmas 1.2 and 1.3 and their y-images);
- Lemma R/Q (used in 5.2);
- the b∩D argument (Lemma 4.1);
- Lemma A and the wrong ray.

In every OPEN case, each of the pairs (α+, α−) and (φ+, γ−) still has exactly one half-lemma available; its other half
is a failing unit. Lemma 4.1 needs two simple returns on the same diagonal. C4 has them on different diagonals (D+ and
D−) and so only yields G = D+∩D−. The symmetric model of §1.7 is degenerate for both pairs at once, so it cannot tell
which half survives.

Closing C2–C6 needs global input:
- the four lines outside the 14-line skeleton;
- the 17-crossing budget on α±, φ+, γ− and D±;
- the 14 bad wedges.

A SAT cube carrying the pins of §§5–6 would be another route.

## 7. Status

| item | status |
|---|---|
| Lemma 1.1 (an apex is a triple, Δ-free) | PROVED |
| Lemmas 1.2, 1.3 (half-lemmas, quad returns included) | PROVED |
| Theorem 1.4 (UM) | PROVED |
| Corollary 1.6: every star costs Δ ≥ 4 (re-proves the star parts of Theorems 0 and E) | PROVED |
| Lemma 2.2 and §2.3: reduction to C1–C7 at Δ = 4 | PROVED |
| family (i), every shared failure with its forced partner | PROVED |
| (ii) with VY or VZ; any pair on one side | PROVED |
| C1 (Y3s+ and Z3s+), C7 (Y+ and Z+ simple) | PROVED |
| C2, C3, C4, C5, C6 | OPEN (exact statements in §6) |

**Referee priorities:**
1. Lemma 1.2 step 4, the quad return: K is the corner opposite Z+, and the kite diagonal through Z+ is α+.
2. Lemma 1.1 step 2(b).
3. The exhaustiveness of Lemma 2.2, especially the C7 branch.
4. 5.3: the exclusion of a quad G′ in C4–C6 through the second star's sextuple.

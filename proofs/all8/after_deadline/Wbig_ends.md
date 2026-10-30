# W ≥ 15 by counting non-bad ends (hand analysis, 2026-10-03; local only)

Notation follows SOL_TASK8 Addenda 2–5, STAR_CASES.md, W13_caseE.md §0 and W13_caseBCD.md. P is a DB star with
rays 0..7 = H+, a+, b+, c+, H−, a−, b−, c−. The + end has the kite (P, A+, T+, F+), apices Y+ = a∩φ+ and
Z+ = c∩α+, V+ = the next H-vertex after T+, and (when V+ is a triple) e1 = V+Y+, e2 = V+Z+, W1+ = first vertex on
V+→(−e1), W2+ = first vertex on V+→(−e2). The − end is the mirror image.

**Status words.** PROVED means a complete hand proof here, given the inputs it names. OPEN means not done.
Nothing here has been refereed.

## 0. Summary

| # | Claim | Status |
|---|---|---|
| 1.1 | N_nb := number of non-bad ends = 2π = 12 − E, where E = 2U + ΣS° + 2K3 + 4K4 + Δ; W = 12 + E/2 | PROVED (NOTE3 (9)) |
| 1.2 | Lines with a non-bad end are exactly the endpoints of the π edges removed from the slope 18-cycle C18. W = 17: the 2 non-bad ends lie on two slope-adjacent lines | PROVED |
| 1.3 | a and c (and H and b) are never slope-adjacent | PROVED |
| 2.1 | At any all-8 point, at least 8 − N_nb of its 8 half-lines end in bad wedges (≥ 6 at W = 17, ≥ 4 at W = 16, ≥ 2 at W = 15) | PROVED |
| 3.1 | Chain lemma: a bad end needs a break vertex (touch, η0, or single outgoing segment) before it | PROVED |
| 3.2 | After a touch or η0 break, a bad end needs ≥ 2 further vertices, the first simple | PROVED |
| 4.1 | T-break: if T+V+ is not double, then H ends at T+ (non-bad), or the + end carries E_+ ≥ 4, or E_+ ≥ 2 plus a nonzero-slack quad at Y+ or Z+ | PROVED |
| 4.2 | V+ simple ⇒ H ends at V+ (I-end) or V+ is a touch centre, unless S°(Y+) or S°(Z+) ≥ 1, or K3 at V+'s kite | PROVED |
| 4.3 | V+ triple: V+Y+, V+Z+ double unless M* (2 each). Four-run ⇒ H ends at V+ (F) or η0 (2). Five-run costs ≥ 2 (M*/O*) or S° ≥ 1 at Z+, W1+ (mirror Y+, W2+) | PROVED |
| 4.4 | V+ full, S simple ⇒ H ends at S (I-end) or S is a touch centre, unless S° ≥ 1 at W1+/W2+ or K3 at S's kite | PROVED (removes U = 0 from STAGE2_TASK8 §9) |
| 4.5 | After a touch at S, H can end bad only via ≥ 2 further vertices, the first simple | PROVED |
| 4.6 | H weight: with T± full and V± triples, H weighs 13 from V− to V+, so 4 crossings lie beyond V±. A bad H-end costs weight: five-run ≥ 1, η0 ≥ 2, touch ≥ 3 | PROVED |
| 4.7 | V+ full, S multiple: fate of H | OPEN (zero corner only: STAGE2_TASK8 §8, STAR_CASES "S never five-run", unchecked) |
| 5.1 | **Four-run end forces three non-bad ends:** H ends at V+ (F; or η0), and **c ends at W1+ and a ends at W2+, both I-ends**, unless one of the costed exceptions of §5 occurs at that end | PROVED |
| 5.2 | Cap lines α+, φ+ and the lines e1, e2 never end at Y+, Z+, W1+, W2+ under the §5 hypotheses | PROVED |
| 5.3 | At a full end, a and c are not forced locally | OPEN (no forcing found) |
| 6.1 | The lead's "relaxing an end costs ≥ 2 hard units" holds only for T-breaks (4.1). H's end can be relaxed for E = 2 (η0 at a four-run V, or a touch at S) | PROVED (correction) |
| 6.2 | W = 17: no DB star has a four-run end free of §5 exceptions; no DB star has both H-ends quiet | PROVED |
| 6.3 | W = 16: no DB star has two exception-free four-run ends; one such end pins the whole non-bad-end set. W = 15: two such ends with H ending at both V± are excluded | PROVED |
| 6.4 | Full exclusion of W = 17, 16 for DB stars | OPEN (residual list in §8) |
| 7.1 | Alternating endpoint costs E ≥ 4 (AE′); Alt–Alt path costs ≥ 8 | PROVED given AE′ inputs; credit version in §7 |
| 7.2 | SB, Alt paths, nonzero-slack all-8 points at W ≥ 15 | OPEN |

**Bottom line.** W = 17 and W = 16 are **not** excluded by this note. They are reduced to the residual list of §8.
The new tools are the four-run three-end lemma (5.1), the slope-adjacency constraint (1.2–1.3), and the H weight
budget with touches (4.5–4.6).

## 1. Accounting

**1.1 (PROVED).** NOTE3 (9) gives 2Λ = 2π + E, with E = 2U + ΣS° + 2K3 + 4K4 + Δ. For a 94, Λ = 6, so
N_nb = 2π = 12 − E and W = 18 − π = 12 + E/2. Hence:
- W = 17: E = 10, N_nb = 2;
- W = 16: E = 8, N_nb = 4;
- W = 15: E = 6, N_nb = 6.

Inputs W13 (all cases) and STAGE1_STATUS (W = 14 with U = 1, H = 1) exclude hard credit H = 1. So H ≥ 2 and
E = 2U + 2H ≥ 4 + 2U. (W13 (c1) §9 is not yet refereed.)

**1.2 (PROVED).** Order the lines by slope, cyclically. Every bad wedge joins two cyclically slope-adjacent lines
(given). So the bad-wedge graph G_W is a subgraph of the 18-cycle C18 on these adjacencies. It is a forest (NOTE3
§5), so it is C18 minus π ≥ 1 edges. A line's number of non-bad ends is 2 − deg_{G_W}, which equals the number of
removed C18-edges at it. So the lines with a non-bad end are exactly the endpoints of the removed edges.
- W = 17 (π = 1): the two non-bad ends lie on two distinct, slope-adjacent lines.
- W = 16 (π = 2): the four non-bad ends lie on the endpoints of two removed edges. A line with two non-bad ends is
  an isolated component.

**1.3 (PROVED).** The lines through a quad P appear in the cyclic slope order in the cyclic order of P's rays,
H, a, b, c. Both arcs of the slope cycle from a to c contain b or H. So a and c are not slope-adjacent. Likewise
H and b are not.

## 2. Half-lines at an all-8 point

**2.1 (PROVED).** Let P be any all-8 point. Each of its four lines has two half-lines from P, one per end. Distinct
half-lines give distinct line ends. At most N_nb of the 8 ends are non-bad. So at least 8 − N_nb are bad wedges:
- at least 6 at W = 17;
- at least 4 at W = 16;
- at least 2 at W = 15.

At W = 17, by 1.2–1.3, the non-bad ends among P's half-lines lie on at most two lines, and those lines are slope-
adjacent. So **at least two of H, a, b, c have both ends bad**.

## 3. The chain lemma

Walk along a line L from a vertex Q0 whose outgoing segment is double. Let X be the first later vertex whose
outgoing L-segment is not double.

**3.1 (PROVED).**
- **(a) X is L's last vertex.** Then L's end is non-bad: it is F if X is multiple, and an I-end if X is simple
  (the last segment is double).
- **(b) The outgoing segment XX′ is bounded and unused.**
  - If X is simple, it is a 2-fan. Its incoming double segment has a multiple other end (L1), and its
    continuation is bounded and unused. So it is a **touch block**, costing U ≥ 1, that is 2 in E.
  - If X is multiple, XX′ is a bounded unused first ray at a multiple point: **η0**, costing Δ ≥ 2 (NOTE3 (8)).
- **(c) The outgoing segment XX′ is single.** Call this a σ-break. Either X is a simple 3-fan, or X is multiple
  with exactly one face beside its outgoing ray.

A bad end has a single last segment (its corner triangle is on one side, an unbounded face on the other). So an L-
end reached by an unbroken double chain is never bad.

**3.2 (PROVED).** After a break of type (b), with X′ the next vertex:
- if L ends at X′, its last segment is unused, so the end is not bad (it is a G_Z end, or F if X′ is multiple);
- if X′ is multiple, X′→X is a bounded unused first ray at X′, which is another η0 (Δ ≥ 2, distinct by NOTE3 (8)).

So a bad end after a (b)-break needs X′ simple and at least one more vertex X″. That is weight ≥ 2 beyond X.

## 4. H at one end of a DB star (U ≥ 1 allowed)

**Inputs, all credit-free.**
- P is all-8 with the DB mask (I1).
- The kite (P, A+, T+, F+) is case-B K1: its caps are double, A+, F+, T+ are triples, and X+ is a simple kite
  centre.
- The exterior faces T+A+Y+ and T+F+Z+ exist, with Y+ ∈ a beyond A+ and Z+ ∈ c beyond F+ (W13_caseE §0).
- The ring at T+ is T+A+ (α+), T+X+ (H), T+F+ (φ+), T+Z+ (−α+), T+V+ (−H), T+Y+ (−φ+).
- (I6) wrong ray: Y+ simple ⇒ T+Y+, A+Y+ single; likewise for Z+.
- (P4) triple-cap continuation (STAGE2_TASK7 §2) and (I4) (W13_caseE §0).
- Costs: every M*, O*, H*, η0 event costs 2 Δ-tokens, and events on different faces or rays are disjoint
  (ALL8_NOTE5 (5)). A touch costs 2U = 2. A quad with S° ≥ 1 costs S° (≥ 2 by W13_caseBCD §1.3 when S° = 1;
  that lemma is not yet refereed). K3 costs 2.

Neither U nor π is used anywhere in §4.

**Fact 4.0.** T+V+ is double ⟺ T+Y+ and T+Z+ are both double. This is because the sectors (T+F+, T+Z+) and
(T+Y+, T+A+) are the faces T+F+Z+ and T+A+Y+.

### 4.1 T-break (PROVED)
Assume T+V+ is not double. By Fact 4.0, say T+Y+ is single (or T+Z+; that case is the mirror).
- **Event e1 on face TAY.** If Y+ is multiple, M* on T+Y+. If Y+ is simple, O* by (I6).
- **Case T+Z+ double.** Then face TZV exists and T+V+ is single. Lemma A (W13_caseE §4.1) applies:
  - V+ multiple ⇒ M* on T+V+;
  - V+ simple, Z+V+ single ⇒ O*(TZV);
  - V+ simple, Z+V+ double, Z+ triple ⇒ wrong ray (apex c∩H = P);
  - V+ simple, Z+V+ double, Z+ quad ⇒ a block from Z+ to simple V+. If Z+ had zero slack, this would be a kite
    block, and T+V+ would be double. So **S°(Z+) ≥ 1**.

  Z+ is multiple, because T+Z+ is double and (I6) holds. Event e2 lies on face TZV, which differs from TAY.
- **Case T+Z+ single.** There is a second event, on face TFZ. Then neither sector beside T+V+ is a face. Either H
  ends at T+ (an F-end, non-bad), or T+V+ is bounded and unused, which is η0 (a third event).

**Conclusion.** H ends at T+ non-bad; or E_+ ≥ 4 (events on two of the faces TAY, TFZ, TZV); or E_+ ≥ 2 plus
S°(Z+) ≥ 1 (mirror: S°(Y+) ≥ 1). This is the only kind of relaxation for which the cascade gives "≥ 2 hard
units".

From now on, T+V+ is double. So the faces T+Z+V+ and T+V+Y+ exist, Y+ and Z+ are multiple, and V+ is the next
H-vertex.

### 4.2 V+ simple (PROVED)
Let E be V+'s second line. The faces put Y+ and Z+ on E.

Suppose V+Y+ is double.
- If Y+ is a triple, its ring is Y+A+ (a), Y+T+ (φ+), Y+V+ (E), −a, …. The second face on Y+V+ has apex
  a ∩ H = P, which is on the wrong ray.
- If Y+ is a quad with zero slack, Y+V+ is a kite block. Lemma 2.1 of W13_caseE, steps 2–5, then gives a
  contradiction, or else V+'s kite has three quads (K3).

So V+Y+ is single unless S°(Y+) ≥ 1 or K3. The same holds for V+Z+.

With both single, V+ is a 2-fan whose continuation carries no triangle. **So H ends at V+ with an I-end, or V+ is a
touch centre (U).**

### 4.3 V+ a triple (PROVED)
V+ has lines H, e1 ∋ Y+ and e2 ∋ Z+. Its ring is VZ, VT, VY, −e2, −H, −e1.
- **VZ, VY.** If V+Z+ is single, TZV is an all-multiple face with a single edge: M* (2). Likewise for V+Y+.
  Otherwise the faces V+Z+W1+ and V+Y+W2+ exist.
- **Four-run** (neither (−e2, −H) nor (−H, −e1) is a face). The H-ray at V+ is unused. Either H ends at V+ (F,
  non-bad), or η0 (2).
- **Five-run.** Say the face V+SW1+ exists and (−e2, −H) does not. Then V+S is single.
  - **W1+ is multiple.** If W1+ were simple, Z+ and S would lie on one line ℓ through W1+.
    - If Z+ is a triple, the ring at Z+ (Z+F+, Z+T+, Z+V+ consecutive) gives ℓ = c, so S = c∩H = P (wrong ray).
    - If Z+ is a zero-slack quad, Z+F+, Z+T+, Z+V+ are three consecutive bridges, so Z+ is DB and the ray Z+W1+
      is a case-B block. Then W1+ is a case-B kite centre whose cap V+S must be double. ✗
    - So W1+ is multiple, unless S°(Z+) ≥ 1.
  - **The costs.**
    - S multiple ⇒ M*(V+W1+S), 2.
    - S simple, W1+S single ⇒ O*, 2.
    - S simple, W1+S double, W1+ triple: the ring at W1+ is W1Z (c), W1V (e1), W1S. The second face on W1S has
      apex c∩H = P (wrong ray). ✗
    - S simple, W1+S double, W1+ a zero-slack quad: then W1+S is a kite block, and V+S would be double. ✗
  - So **a five-run V+ costs ≥ 2** (M*/O*), or S° ≥ 1 at Z+ or W1+ (Y+, W2+ in the mirror).
- **Full.** S is the next H-vertex. The faces V+W2+S and V+SW1+ exist.

### 4.4 S after a full V+ (PROVED; this replaces STAGE2_TASK8 §9's use of U = 0)
Assume Y+ and Z+ are triples; otherwise S°(Y+) or S°(Z+) ≥ 1, by W13_caseE D3 and Lemma 2.1.
- **W1+ and W2+ are multiple.** A simple W1+ would put S on c, which is the wrong ray as in 4.3.
- **S simple** (lines H and k, with W1+, W2+ on opposite k-rays). Suppose SW1+ is double.
  - If W1+ is a triple, its ring is W1Z (c), W1V (e1), W1S (k). The second face on W1S has apex c∩H = P. ✗
  - If W1+ is a zero-slack quad, S is a kite centre with corners V+, W1+, R, W2+, where R is next on H.
    - If W2+ is a triple, (P4) at W2+ (exterior face V+Y+W2+ across the cap W2+V+) puts R on a. Then
      R = a∩H = P. ✗
    - If W2+ is a quad, then R is a quad (K3) or a triple.
    - If R is a triple, then by (I4) W1+ is alternating. But W1+Z+ and W1+V+ are consecutive double bridges. ✗
  - So SW1+ and SW2+ are single unless S° ≥ 1 at W1+/W2+, or K3. Then **S is a 2-fan: H ends at S (I-end), or S
    is a touch centre.** This is exactly where STAGE2_TASK8 §9 used U = 0.
- **S multiple:** OPEN (4.7).

### 4.5 Following H past a touch (PROVED)
Let S be a touch centre (from 4.2 or 4.4), and S′ the next H-vertex. SS′ is unused. By 3.2:
- If H ends at S′, its end is non-bad (G_Z).
- If S′ is multiple, η0 at S′ adds Δ ≥ 2.

So **a bad H+ end after a touch at S needs S′ simple and at least one more vertex S″**.

The same holds after η0 at a four-run V+, with S′ in place of S.

### 4.6 H weight budget (PROVED)
The H-vertices from V− to V+ are V−, T−, X−, P, X+, T+, V+, in that order (each is the next on H). Suppose T± are
triples, X± are simple and V± are triples. Then their weight Σ(m−1) is 2+2+1+3+1+2+2 = 13. Since n = 18, exactly
**4 further crossings** lie beyond V+ or beyond V−.

Minimal weight beyond V+ for each outcome at the + end (V+ a triple):

| outcome at + end | H+ end | weight beyond V+ | cost E_+ |
|---|---|---|---|
| four-run, H ends at V+ | non-bad (F) | 0 | 0 |
| four-run with η0 | bad possible | ≥ 2 (S′ simple, S″) | ≥ 2 |
| five-run | bad possible | ≥ 1 | ≥ 2, or S° ≥ 1 |
| full, S simple, I-end | non-bad (I) | 1 | 0 |
| full, S simple, touch | bad possible | ≥ 3 (S, S′, S″) | ≥ 2 |
| full, S multiple | OPEN | ≥ 2 | OPEN |

**Corollary 4.6′ (PROVED).** Suppose both ends are as in the table and the two weights sum to 4. Then H has two bad
ends only for these pairs:
- (η0, η0) with weights 2 + 2;
- (η0, five-run);
- (touch, five-run) with weights 3 + 1;
- (five-run, five-run);
- pairs involving "S multiple".

In particular, **two touches cannot make both H-ends bad** (3 + 3 > 4).

### 4.7 OPEN: S multiple after a full V+
In the zero corner, STAGE2_TASK8 §8 excludes S quad. Its proof needs U′ triple from §7 and the four-bridge
contradiction at M, all with zero-slack masks. STAR_CASES asserts "S never five-run" by analogy with §6, but this
has not been checked. With credit, neither has been redone. The weight is ≥ 2.

## 5. a and c at a four-run end: three forced non-bad ends

**Hypotheses (+ end).**
- T+V+ double;
- V+ a four-run triple;
- V+Y+ and V+Z+ double (otherwise M*, §4.3);
- Y+ and Z+ triples (otherwise S° ≥ 1 at Y+ or Z+; see below).

H's + end is then F at V+, or η0.

### 5.1 Lemma (PROVED): c ends at W1+ with an I-end, unless one of the following exceptions occurs at the + end
- (x1) M* on V+Z+W1+;
- (x2) O* on V+Z+W1+;
- (x3) a touch at W1+ (U);
- (x4) H* on the 3-fan at W1+;
- (x5) S° ≥ 1 at Z+, at M = α+∩e1 or at U+′;
- (x6) a failure of Z3 or B6 (M*, 2 each).

The mirror statement: a ends at W2+ unless the mirror exceptions occur (Y+, M′ = φ+∩e2, U+, Y3, B5).

*Proof.*
1. **W1+ = c∩e1 is the next vertex after Z+ on c.** Z+ is a triple, with ring Z+F+ (c), Z+T+ (α+), Z+V+ (e2), −c,
   −α+, −e2. The face V+Z+W1+ lies in (Z+V+, −c).
2. **V+W1+ is single.** Its only possible second face would lie in V+'s sector (−H, −e1), which is empty by the
   four-run.
3. **W1+ is simple.** Otherwise V+Z+W1+ is all-multiple with a single edge, which is (x1).
4. **Z+W1+ is double.** Otherwise both edges at the simple corner W1+ are single, which is O* (x2).
5. **The second face on Z+W1+** lies in Z+'s sector (−c, −α+). Its third vertex M is the first vertex on α+ beyond
   Z+. At the simple W1+ (ring W1Z, W1V, W1(−c), W1(−e1)), this face lies in (W1(−e1), W1Z). So M is also the first
   vertex on e1 beyond W1+: **M = α+ ∩ e1**.
6. **The sectors at W1+.**
   - (W1Z, W1V) is a face.
   - (W1(−e1), W1Z) is a face.
   - (W1V, W1(−c)) is not a face: its triangle would need V+'s empty sector (−H, −e1).
   - So W1+ is a 2-fan or a 3-fan. It is a 3-fan exactly when (W1(−c), W1(−e1)) is a face.
7. **2-fan.** The continuation of c beyond W1+ carries no triangle. If it is unbounded, c ends at W1+ with double
   last segment Z+W1+: an **I-end, non-bad**. If it is bounded, Z+W1+ is a touch block: (x3).
8. **3-fan.** Its origins are Z+ and M (M is multiple by L1). Its central cap is Z+M ⊂ α+.
   - If Z+M is single, the 3-fan has a single central cap: **H\*** (x4).
   - If Z+M is double, Z+'s sector (−α+, −e2) is a face Z+MU, where U is the first vertex on Z+→(−e2).
     - By Z3 (face F+Z+U+′ at F+), U = U+′ ∈ D+ ∩ e2. By B6 (face F+U+′B−), U+′ ∈ α−. If either fails, that is (x6).
     - **U+′ a triple** (D+, α−, e2). Its ring is U+′B− (α−), U+′F+ (D+), U+′Z+ (e2), −α−, …. So the face Z+MU+′
       lies in (U+′Z+, −α−), and **M ∈ α−** (Lemma M, + half).
       - At M the faces Z+MU+′, Z+W1+M and W1+NM (N = next vertex on c beyond W1+) make the rays MU+′ (α−),
         MZ (α+), MW1 (e1), MN consecutive.
       - If M is a triple, MN = M→(−α−). Then N ∈ c ∩ α− = Z−, which lies on c+, while N lies on c beyond W1+ (on
         c−). ✗
       - If M is a quad, its block MW1+ is a 3-fan block, so S°(M) ≥ 1 (zero-slack quads have only kite blocks):
         (x5).
     - **U+′ a zero-slack quad.** Its rays U+′B−, U+′F+, U+′Z+ are three consecutive bridges, so U+′ is DB, and the
       ray after U+′Z+ is a case-B block whose first vertex is a simple kite centre. But the face Z+MU+′ puts the
       multiple vertex M there. ✗ So S°(U+′) ≥ 1: (x5).

   Hence a 3-fan at W1+ needs (x4), (x5) or (x6). ∎

**Where the Y+/Z+ triple hypothesis enters.**
- If Y+ is a zero-slack quad, its three consecutive bridges Y+A+, Y+T+, Y+V+ make it DB. Then W2+ (on the next ray,
  a case-B block) is a kite centre, so V+W2+ is double, which contradicts the four-run.
- So a quad Y+ or Z+ at a four-run end has S° ≥ 1, which is included in (x5).

### 5.2 Cap lines and e-lines do not end at the star (PROVED)
Under §5's hypotheses:
- **φ+ does not end at Y+.** The face Y+W2+M′ (mirror of step 5) lies in Y+'s sector (−a, −φ+), so φ+ continues
  beyond Y+ to M′.
- **α+ does not end at Z+.** It continues to M.
- **e1 and e2 do not end at W1+, W2+.** e1 continues to M, and e2 to M′.
- **b does not end at B±** whenever B± are full.

In the full-V+ case, W1+ and W2+ are multiple. Then V+Z+W1+ is all-multiple, so M* makes Z+W1+ double, and its
second face again has third vertex on α+ beyond Z+. So the conclusions for α+ and φ+ still hold. Whether e1 and e2
continue beyond W1+ and W2+ is not determined. If one ends there, the end is at a multiple point, so it is F and
non-bad.

**Answer to the brief's question.** Near a rigid four-run end, exactly **a and c** are forced to end at end blocks
(at W2+, W1+). The cap lines are not forced. At a full end, nothing beyond H is forced locally (5.3, OPEN). The
credit needed to avoid each forced a/c end is one of (x1)–(x6). Each costs ≥ 2, except that an (x5) quad with
S° = 1 costs 1 + 1, the second unit from W13_caseBCD §1.3 (unrefereed).

### 5.3 Full end (OPEN)
At a full V+, W1+ is multiple. Its sectors (W1S, −c) and (−c, −e1) are not determined by the local faces. Triple
optimality only forces one of (W1S, −c) and (−e1, −k1). No forcing of c's end was found. The zero-corner branch
(4,0) forced a and c only through the global H count. That count is not available here.

## 6. Counting

### 6.1 Correction to the brief's cost premise (PROVED)
"Relaxing an end costs ≥ 2 hard units" is true only for a **T-break** (4.1: E_+ ≥ 4, or 2 plus a nonzero-slack quad).
H's end can be relaxed more cheaply:
- **η0 at a four-run V:** Δ = 2, which is one hard unit.
- **A touch at S:** U = 1, which is no hard unit but 2 in E.
- **A five-run V:** 2.

What makes these weaker is that they cost H weight (4.6), and a four-run end still forces a and c (5.1).

**Disjointness of the end costs (PROVED with one caveat).**
- Every + event in §§4–5 sits on a face, ray or vertex lying on H beyond T+, or on e1 or e2. These are Y+, Z+, V+,
  W1±, W2±, M, M′, U+, U+′, S and their faces.
- The − events sit on H beyond T− or on e3, e4.
- e1, …, e4 are four distinct lines (they meet H at V± and carry different apices). So distinct ends use distinct
  faces and edges, and ALL8_NOTE5 (5) adds their Δ-tokens.
- **Caveat:** an S°-event at a quad lying on one of e1, e2 and one of e3, e4 would be shared between the ends and is
  counted once.

### 6.2 W = 17 (E = 10, two non-bad ends on slope-adjacent lines)
- **(a) PROVED.** No DB star has a four-run end with none of (x1)–(x6) on either side. Otherwise a and c both have
  non-bad ends, but they are not slope-adjacent (1.2, 1.3).
  - Moreover, if H also ends at that V, then the two non-bad ends are H's and one of a's or c's. So the other of a, c
    carries an exception, which costs ≥ 2, or S° ≥ 1.
- **(b) PROVED.** H cannot have two non-bad ends: H would be an isolated component, so π ≥ 2.
  - So at least one end of H is relaxed: by a T-break (≥ 4, or 2 + S°), or by one of the 4.6 relaxations (≥ 2, or
    S° ≥ 1 at Y, Z or W).
- **(c) Consequence.** A W = 17 DB star with both ends standard (T± full, V± triples) has one of these:
  - a full end whose H-end is bad. By 4.4–4.6 this needs a touch at S (weight ≥ 3) or S multiple (OPEN, 4.7);
  - a five-run end (≥ 2);
  - a four-run end with η0 (≥ 2) plus an a/c exception (≥ 2).

  All of this is on top of the star rescue (hard credit ≥ 2, i.e. E_hard ≥ 4).
- **Not closed.** For example, the following fits E = 10:
  - one quiet full end (H I-end at S, weight 1);
  - the other end full with a touch (2, weight 3);
  - a rescue of cost 4.

  Closing it needs either a, c, b forcing at a full end (5.3) or an analysis of the rescue's location. **OPEN.**

### 6.3 W = 16 (E = 8) and W = 15 (E = 6)
- **(a) PROVED.** Suppose both ends of a DB star are exception-free four-run ends. Then a and c have two non-bad
  ends each, so {a} and {c} are isolated components.
  - **W = 16 (π = 2).** {a}, {c} and the remaining 16 lines give π ≥ 3, whatever H does (H's ends may be relaxed by
    η0). ✗
  - **W = 15 (π = 3).** If H also ends at both V± (no η0), H is a third isolated component, and the other 15 lines
    make π ≥ 4. ✗ With η0 at an end, W = 15 is **not** excluded.
- **(b) PROVED, W = 16.** If one end (say +) is an exception-free four-run end and H ends at V+, then by 1.2 the
  non-bad ends are H+, a+, c− and one more on a line x, and the removed C18-edges are {H, a} and {c, x}, or {H, c} and
  {a, x}. Hence:
  - a− and c+ are bad;
  - H− is bad unless x = H, which needs H slope-adjacent to both a and c;
  - b has both ends bad unless x = b.

  The − end must then make a− and c+ bad. At a four-run − end that costs ≥ 2 exceptions (5.1). At a full − end it is
  free so far (5.3 OPEN). If the − end is standard (T− full, V− a triple), the H weight beyond V+ is 0, so all 4 crossings beyond V± lie beyond V− (4.6).
- **(c) W = 15.** 6 non-bad ends allow one exception-free four-run end (3 forced) plus slack 3. **OPEN.**

## 7. Other all-8 clusters

### 7.1 Alternating endpoints (PROVED given W13_paths)
Steps 1 and 3–7 of Lemma AE are pure incidence. Step 2 (R± quad ⇒ alternating) uses only that R± has zero slack. So,
for each outward kite at X±:
- either T R± is single, giving v(X±) ≥ 2 (AE′);
- or R± is a quad with S° ≥ 1 (cost ≥ 1, or ≥ 2 with W13_caseBCD §1.3).

So **each alternating endpoint costs E ≥ 4** when S°(R±) = 0, and E ≥ 2 in general (≥ 4 using §1.3). The two
outward kites and the two R± are distinct. So:
- an Alt–Alt path costs ≥ 8 (with §1.3). At W = 16 that is the whole budget: U = 0, every other S°, K and Δ-token
  vanishes, and only the four outward kites carry Δ = 2 each.
- At W = 17 it leaves 2.

The non-bad-end analysis of a path's lines is **OPEN**. The chain lemma 3.1 applies to all four lines of each star.

### 7.2 Single-B stars
Lemma C (W13_caseBCD §2.2, no K3 or Δ input) puts a nonzero-slack quad on each of SQ2 and SQ6. These are two
distinct quads, costing E ≥ 2 (≥ 4 with §1.3). Paths with an SB endpoint therefore cost ≥ 4 at the SB end. **OPEN**
beyond this count.

### 7.3 Nonzero-slack all-8 points
Section 2.1 still applies: at W = 17 six of their eight half-lines must break (§3). Not analysed. **OPEN.**

## 8. Residual list and suggested next steps

**Open for W = 17 and 16 at a DB star:**
1. **S multiple after a full V (4.7).** Redo STAGE2_TASK8 §8 and the five-run claim at S with credit, costing each
   exception as in §4.
2. **a, c, b at a full end (5.3).** Is c's continuation beyond the multiple W1+ forced (double, or ending)? At W = 17,
   2.1 needs six of eight half-lines bad. So at a full end, a+ and c− must break somewhere beyond W2+ and W1+, and
   b must break beyond B±/G.
3. **Location of the rescue.** By W13_caseE §3, the rescue must break both routes. The route-specific checkpoints
   UY, UZ (and VY, VZ) do not affect §4. VY and VZ failures are M* events, already priced in 4.3. So a rescue
   placed on UY± and UZ± leaves both ends standard. Combine with 6.2(c) and 6.3(b).
4. **Paths and SB / nonzero-slack all-8 points (§7).**

**SAT pins available now (for the s1a W ≥ 13 probe, guarded by the DB-star cube):**
- **(four-run ⇒ a/c I-ends).** If V is a four-run triple and none of (x1)–(x6) occurs, then a ends at W2 with a
  double last segment, and c ends at W1 likewise. A cheaper pin: if V is four-run, W1 and W2 are simple
  (otherwise M*).
- **(slope pin, W = 17).** a and c do not both have non-bad ends, and H does not have two.
- **(touch pin).** After a touch at S on H, the next H-vertex is simple or carries η0.

## 9. Inputs used
- ALL8_NOTE3 §§4–5 and (8);
- ALL8_NOTE5 (5);
- W13_caseE §0 (I1)–(I6), (P4), Lemma A, Lemma 2.1, D3;
- STAGE2_TASK8 §§6, 9 (re-proved here without U = 0);
- Lemma M's + half (STAR_CASES);
- W13_caseBCD §1.3, §2.2;
- W13_paths AE/AE′;
- W13 and STAGE1_STATUS (hard credit ≥ 2).

No SAT run and no straight-line model check was made for this note. The orientation claims in 5.1 steps 1, 5 and 8
reuse rings already checked in the W13_caseE §8 model.

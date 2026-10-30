# W = 13, case (e): path clusters with one Δ-event

Hand proofs. They have not been refereed independently. Local file only.

**Result.**
- Case (e) means ΣS° = 0, K3 = K4 = 0, U = 0 and Δ = 2.
- In case (e) there is **no** path cluster:
  - no path with an alternating endpoint;
  - no path with k ≥ 3.
- Every quad is therefore an isolated double-B star.
- Two new lemmas do the work:
  - **Lemma AE:** at an alternating endpoint, both caps T R± are single, so **Δ ≥ 4**.
  - **Lemma SB:** the central neighbour of a single-B star is never alternating. This lemma is Δ-free.
- The proofs need only Δ ≤ 3. They make no assumption about how the Δ-units are split between events.
- U and π are never used.

---

## 0. Setting and the Δ budget

**Standing hypotheses (H).** These are taken from W13.md §1 (e):
- 18 proper pseudolines, each pair crossing once;
- multiplicity ≤ 4;
- structural class and triple optimality;
- S°_P = 0 at every quad;
- K3 = K4 = 0;
- Δ ≤ 3. Case (e) has Δ = 2.

The following inputs are Δ-free:
- **Mask classification:** zero slack ⇒ all-8 (STAGE2_TASK5 §2). The three masks are alternating, single-B (blocks 0, 3, 5) and double-B (blocks 0, 4). Each mask's blocks are all kite blocks (ALL8_NOTE3 §8).
- **Propagation lemma** (ALL8_NOTE3 §8): Q4 of a single-B star is a quad.
- **Task-5 path reduction** (STAGE2_TASK5 §4):
  - nonisolated components are paths on a line H;
  - interior stars are alternating; endpoints are alternating or single-B;
  - the baseline count is n ≥ 3k + 5 + b, so k ≤ 4.
- **Far-corner rule.**
- **Triple-cap continuation** (STAGE2_TASK7 §2).
- **Wrong-ray lemma** (STAGE2_TASK6 §2): "R triple ⇒ AR and TR are single". This is pure incidence. Its Δ-step is only the *next* sentence of §2.
- **B–B path exclusion** (STAGE2_TASK7 §3).

**Budget lemma.** By ALL8_NOTE5 (5):
- Δ ≥ 2η0 + |H*| + |M*| + |O*| + |B*| + V_K, and the token sets are pairwise disjoint.
- Every saturation statement used below fails only by producing one of these sets, worth ≥ 2:
  - a surplus cap on a case-A K1: v = 2(s−1) ≥ 2;
  - a single cap on a K2: v = 2s ≥ 2;
  - an O* triangle;
  - a single edge of an all-multiple triangle (M*);
  - a bounded unused first ray (η0).
- **Consequence:** two violations at distinct kites, triangles or edges give Δ ≥ 4.
- So with Δ ≤ 3, at most one saturation statement fails anywhere, and everything else is saturated.

---

## 1. Audit: where STAGE2_TASK6 §§2–6 and ALL8_NOTE6 §§5–6 use Δ = 0

Notation as in STAGE2_TASK6.
- An alternating endpoint P has inward quad B and outward triple T on H, and triples A and C on the axis K.
- Kite centres: X+ lies between T and A, X− between C and T. The other two are X_AB and X_BC.
- Star caps (the kite diagonals): c_TA ∋ T, X+, A; c_AB ∋ A, X_AB, B; c_BC ∋ B, X_BC, C; c_CT ∋ C, X−, T.
- Far corners: R+ = c_AB ∩ c_CT on PX+, and R− = c_BC ∩ c_TA on PX−.
- A case-B kite is (P, A, T, F). Its apices are Y = PA ∩ TF and Z = PF ∩ TA.

| # | Location | Δ = 0 is used for | Violating event (cost) |
|---|---|---|---|
| U1 | T6 §2 / N6 §2 | R± triple is impossible | outward kite is K1A with AR, TR both single, s = 2 (V_K, 2) |
| U2 | T6 §2–3 / N6 §3 | outward K2 caps are double; **T R± double** is what gets used | one single cap on an outward K2 (e_mix, 2) |
| U3 | T6 §3 "three axes" | T full, V simple and common to both D±, V a kite, T′ triple | not new: consequences of U1/U2 at **both** outward kites (T′ triple uses K3 = 0) |
| U4 | T6 §4 / N6 §4 | Y, Z multiple | O* at TAY or TFZ (2) |
| U5 | T6 §4 / N6 §4 | TAY, TFZ, PAB, PFC have all edges double, so A, F, T are full | M* on one of these triangles (2) |
| U6 | T6 §4 | "only one line E beyond T ⇒ Y, Z triple" | no Δ: S° = 0 (a quad has no single first ray) |
| U7 | T6 §5 | earliest-quad and cycle pins | U1, U2 |
| U8 | T6 §6 / N6 §6 | triangle P1 P2 P3, 24 incidences, n ≥ 21 | U1–U2 at the three edge kites; U4–U5 at the case-B Bi; k = 2 via N6 §5 |
| U9 | N6 §5 | n ≥ 3k + 11 (3 lines per alternating end, 2 per case-B end) | U1–U3 at each alternating end; U4–U5 at each case-B end |

Two things in this table matter for case (e):
- **Only the caps T R± matter at an alternating end.** A single cap A R± or C R∓ on a K2 is a legal one-event spend that breaks nothing above.
- **At a case-B end, the event can sit at Y, Z (O*) or on TAY, TFZ, PAB, PFC (M*).**

What one event does to the old counts:
- **Alternating endpoint (U1–U3, U8).** At the end that holds the event, §3 only yields the single axis D, so the 21-line count (U8) can no longer be run as written.
- **k = 3, b = 2 (U9).** A case-B end holding the event loses its two-line conclusion. The count 16 + 2 + 2 = 20 drops to 16 + 2 + (?), which is inconclusive.

§§2–3 replace these counts by incidence contradictions. §5 gives an independent count for k = 3, b = 2.

---

## 2. Lemma AE: at an alternating endpoint, T R+ and T R− are both single — PROVED

**Statement.** Assume (H) with Δ arbitrary. Let P be an alternating zero star whose bridge neighbours T, A, C are triple, with A and C adjacent to T. (Every alternating endpoint qualifies, with T the outward neighbour.) Then neither T R+ nor T R− is double.

**Ray orders.**
- **At P:** T, X+, A, X_AB, B, X_BC, C, X−.
- **At T** (lines H, c_TA, c_CT), the kite triangles give the cyclic order
  `T R−, T X−, T P, T X+, T R+, H+`,
  with T R− = −c_TA and T R+ = −c_CT. So **T R+ and T R− flank H+**:
  - the exterior face on T R+ lies in the sector (T R+, H+);
  - the exterior face on T R− lies in the sector (H+, T R−).
- **At R−:** the rays toward C (c_BC), X− (M2) and T (c_TA) are consecutive. Call them c, m′, t′. These are three of R−'s lines.

**Proof.** Suppose T R− is double.
1. **R− is a quad.** By the wrong-ray lemma, R− triple ⇒ T R− single. So R− is a quad.
2. **R− is alternating.** S°(R−) = 0, so R− is all-8. Its block toward X− is a kite with q = 2, flanked by bridges to the triples C and T.
   - It cannot be case B (that kite has q = 1).
   - It cannot be the block at position 3 or 5 of a single-B mask. Those blocks flank the central quad Q4 (propagation).
   - So R− is alternating. In the quad order (c, m′, t′, d, −c, −m′, −t′, −d), the fourth line D occupies block positions.
3. **The apex V.** The exterior face on T R− lies at R− in the sector (t′, d). Its apex V satisfies:
   - V is the first vertex on H+ from T;
   - V is the first vertex on R−'s block ray d, so V is **simple, with lines H and D, and a kite centre**.
4. **R+ lies on D.** The face across TV from TVR− is a triangle TVZ, because V is a kite, and Z is V's other neighbour on D.
   - At T this face lies in the sector (T R+, H+). So TZ runs along the ray T R+, and Z is the first vertex there: **Z = R+**.
   - Hence R+ ∈ D. D meets H at V, while M1, c_AB and c_CT meet H at P, B and T. So R+ has four distinct lines and is a quad.
5. **T′ lies on c_AB.** At R+ the rays a (toward A), m (toward X+) and t (toward T) are consecutive. Face TVR+ lies in the sector (t, d), so the quad order is (a, m, t, d, −a, …).
   - V's kite has fourth corner T′, the next vertex on H after V. Its triangle R+ V T′ lies at R+ in the sector (d, −a).
   - So **T′ ∈ c_AB**.
6. **T′ lies on c_BC.** Likewise, at R− the triangle R− V T′ lies in the sector (d, −c). So **T′ ∈ c_BC**.
7. **Contradiction.** c_AB ∩ c_BC = B, because B is on both kite diagonals at X_AB and X_BC. B lies on H on the far side of P from T, while T′ lies on H beyond T and V. Two distinct lines would cross twice.

Reflecting (A ↔ C, X+ ↔ X−) excludes T R+ double. ∎

**Corollary AE′.** Every alternating endpoint forces Δ ≥ 4.
- **Kite at X+.** Its caps PA and PT are double (P is all-8) and T R+ is single.
  - If R+ is a triple, the kite is case-A K1 with s = 2 (A R+ is also single, by the wrong-ray lemma), so v = 2.
  - If R+ is a quad, the kite is K2 with s ≥ 1, so v ≥ 2.
- **Kite at X−.** The same gives v ≥ 2.
- These are distinct kites, so V_K ≥ 4 by ALL8_NOTE5 (5).

So in case (e) (Δ = 2) **no alternating endpoint exists**, wherever the single event sits. In particular, an event placed at one outward kite does not help. The other outward kite is then saturated, and steps 1–7 run from it. This is the hint's "use the other outward kite".

**Remark (zero corner).** With Δ = 0, steps 1–7 apply directly. The triangle construction of STAGE2_TASK6 §§3, 6 is therefore vacuous:
- its "farther triple" T′_i lies on K_j ∩ K_k = c_AB ∩ c_BC = B_i, on the wrong side of P_i;
- so the 21-line count was not needed.

STAGE2_TASK6's conclusion is unaffected.

**Sanity check (scratch, orientation only).** I built a straight-line partial model: P = 0, T = (1, 0), A = (0, 1), B = (−3, 0), C = (0, −½), with D = R+R−. It reproduces:
- the order at T: X−, P, X+, R+, H+, R−;
- at R+: a, m, t, d, −a, …;
- at R−: c, m′, t′, d, −c, …;
- c_AB ∩ H = c_BC ∩ H = B.

---

## 3. Lemma SB: the central neighbour of a single-B star is not alternating — PROVED (Δ-free)

**Statement.** Assume (H) with Δ arbitrary. Let P be a single-B star. Label its rays 0–7:
- 0 → X_L, the case-B centre on H;
- 1 → A, 2 → B;
- 3 → X3, a kite;
- 4 → M, on H;
- 5 → X5, 6 → C, 7 → F.

M = Q4 is a quad (propagation). Then M is not alternating.

**Proof.**
1. **The kites and R's lines.**
   - The case-B kite (P, A, T_L, F) has T_L on H beyond X_L, and A triple.
   - The kite at X3 is (P, B, R, M), with P and R opposite on p3, and B and M opposite on the line d3 ∋ B, X3, M.
   - K3 = 0 makes B and R triples.
   - R's three lines are p3, ℓ = BR and g = RM. They are pairwise distinct: one checks this through their crossings with H, p2 and d3.
2. **ℓ meets H at T_L.**
   - Triple-cap continuation at A uses cap AP and the exterior face PAB, which exists because P is all-8. It puts B on a = A T_L.
   - a is a line through B, and B's lines are p2, d3 and ℓ. Now a ≠ p2, since a ∩ p1 = A ≠ P. Also a ≠ d3, since d3 ∩ H = M ≠ T_L.
   - So **ℓ = a, and ℓ ∩ H = T_L**. These are steps 1–2 of the STAGE2_TASK7 §3 chain.
3. **M's ray order.** M is all-8. The rays MP, MX3, MR are consecutive (triangles P X3 M and M X3 R), so its order is
   `MP (H), MX3 (d3), MR (g), m4, H away from P, …`
   with m4 its fourth line, at position 3.
4. **If M were alternating.** Position 1 is a block, so position 3 is a kite block. Let Y be the simple vertex there; its lines are m4 and e.
   - The triangles M R Y and M Y Q exist, with Q the first vertex on H beyond M.
   - R ∉ m4 and Q ∉ m4, so **R, Q ∈ e**.
5. **Contradiction.** e passes through R, so e ∈ {p3, ℓ, g}. These meet H at P, T_L and M respectively. None of them is Q, because H has the order T_L, X_L, P, M, Q. ∎

(The mirror orientation, with MX3 at position 7, is identical.)

The lemma uses K3 = 0 essentially: if R could be a quad, e could be R's fourth line. Partial straight-line model check: R's lines meet H at P, M and T_L. The scratch check reproduced this.

**Corollary SB′ (Δ-free). Under S° ≡ 0 and K3 = K4 = 0 there is no single-B star.**
1. M's bridge MP is flanked by the two kite blocks MX3 and MX5. The double-B mask has no such bridge, and Lemma SB rules out alternating. So M is single-B, with MP at its position 4.
2. So P is M's central neighbour, and {P, M} is a component with k = 2 and two case-B endpoints.
3. STAGE2_TASK7 §3 excludes such a component.

---

## 4. Sub-cases

| Path type | Status | Argument |
|---|---|---|
| k = 2, alternating – alternating | **PROVED** | AE′: Δ ≥ 4 at each end |
| k = 2, alternating – single-B | **PROVED** | AE′ at the alternating end (SB′ also applies) |
| k = 2, single-B – single-B | **PROVED** (elsewhere, Δ-free) | STAGE2_TASK7 §3 |
| k = 3, at least one alternating endpoint | **PROVED** | AE′ |
| k = 3, both endpoints single-B | **PROVED** | SB: the alternating interior star is the central neighbour of an endpoint. Independent count in §5 |
| k = 4, b ≤ 1 | **PROVED** | AE′ |
| k = 4, b = 2 | **PROVED** (Δ-free) | baseline 3·4 + 5 + 2 = 19 > 18 (also SB) |
| Triangle of alternating quads (STAGE2_TASK6 §6), with the event at an outward kite | **PROVED** | Not needed: AE′ excludes its first vertex. AE also shows the triangle is impossible even at Δ = 0 |

**Conclusion:** no path cluster survives in case (e). Every quad in a case-(e) 94 is an isolated double-B star, which is treated elsewhere.

**Nothing in this family is OPEN.**

Robustness:
- AE′ needs Δ ≤ 3. SB, SB′ and the B–B exclusion are Δ-free.
- None of the arguments uses U, π, triple optimality beyond the inputs above, or straightness.

---

## 5. Independent check for k = 3, b = 2 by line count

This section is not needed; it is a cross-check of SB.

**Lemma T-end.** Assume (H). If Δ ≤ 3, a case-B far triple T is not the last vertex of H.

*Proof.* Suppose it were. Then H+ at T is unbounded, so the sectors (−a, H+) and (H+, −f) are not triangles, and TY and TZ are single.
- If Y is multiple, TAY is all-multiple with a single edge: M* costs 2.
- If Y is simple, AY is single as well, by the wrong-ray step of STAGE2_TASK6 §4: O* costs 2.
- The same holds for Z with TFZ.
- These are disjoint, so Δ ≥ 4. ∎

**The count.**
- The baseline is 3·3 + 5 + 2 = 16 lines, all meeting H inside [T_L, T_R].
- Only one event exists, so at least one end has U4 and U5 intact. That end gets STAGE2_TASK6 §4's **two** further lines beyond its T. Here the mixed diagonals BQ and CQ become d3 and d5, which meet at the alternating middle star M ∉ D0.
- The other end gets **at least one** line beyond its T, by Lemma T-end.
- Total n ≥ 16 + 2 + 1 = **19 > 18**. **PROVED** (second proof).

---

## 6. Inputs relied on (for the referee)

- **Mask classification and all-8:** STAGE2_TASK5 §2, ALL8_NOTE3 §8.
- **Propagation lemma:** ALL8_NOTE3 §8 (used in AE step 2 and SB).
- **Wrong-ray lemma:** STAGE2_TASK6 §2, first paragraph only (Δ-free).
- **Triple-cap continuation:** STAGE2_TASK7 §2.
- **B–B exclusion:** STAGE2_TASK7 §3.
- **Disjoint residual bound (5)** and the v(X) table: ALL8_NOTE5 §3. Used only in AE′ and §5.

AE uses only the ray orders at T, R+ and R−, plus the one-crossing rule. SB uses only the incidences of R's three lines.

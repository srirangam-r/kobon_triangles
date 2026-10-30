# W = 13, cases (b), (c), (d) (hand analysis, 2026-10-03; local only)

## 0. Summary

| Case | Hypothesis (everything else zero, U = 0, π = 5) | Status |
|---|---|---|
| (b) | K3 = 1, ΣS° = 0, K4 = 0, Δ = 0 | **PROVED impossible** (§3) |
| (d) | ΣS° = 1, Δ = 1, K = 0 | **PROVED impossible** (§4) |
| (c2) | two quads with S° = 1 each, Δ = 0, K = 0 | **PROVED impossible** (§5) |
| (c1) | one quad P* with S° = 2, Δ = 0, K = 0 | **PROVED impossible** (§6 reduction + §9; needs a referee) |

The proofs rest on four new local lemmas (§2). They are short, and they also give a much shorter proof of Theorem 0
(§7). Notation is that of STAR_CASES.md, SOL_TASK8 Addenda 2–6 and STAGE2_TASK5–8:
- ray k of a quad is opposite ray k+4, and ℓ_k is the line carrying rays k and k+4;
- Q_k is the first vertex on ray k;
- masks: **Alt** = four kite blocks at odd rays; **SB** = blocks 0 (case B), 3 and 5; **DB** = case-B blocks 0 and 4;
- "zero-slack" means S° = 0. Such a quad is all-8 with one of these three masks (ALL8_NOTE3 §8, STAGE2_TASK5 §§1–2).

## 1. What survives one defect

**1.1 (PROVED) Every Δ-lemma used in Stage 2 gives Δ ≥ 2.** So each one stays valid when Δ ≤ 1, which covers all of
(b), (c) and (d). Check of each:
- η0: token plus slot, 2.
- e_mix (single cap of a kite with ≥ 2 quad corners): two endpoint tokens.
- K0 / case-A K1 saturation (an extra single cap): 2.
- M* (single edge of an all-multiple triangle): 2.
- O* (tokens at P on PX and at Q on QX): 2.
- STAGE2_TASK6 §2 (surviving K1A pair): 2.

B* is the only Note-5 class worth 1, and no Stage-2 argument uses it. U = 0 holds in every case, by W13 §1.

**1.2 (PROVED) What can fail.**
- (b): only "K3 = 0", and only at the one kite κ.
- (c), (d): only "S° = 0", and only at the defect quad(s).

In (d) the slack-1 quad is all-8, because a 7-type has S° ≥ 2 (STAGE2_TASK5 §2).

**1.3 (PROVED) Residual-token lemma.** Let P be a quad and PX a non-kite block (X simple with 2 or 3 triangles).
- Suppose X is a 2-fan (U/I) and neither ray of P adjacent to PX is a block. Then N_res holds a bounded token that no
  payment uses, so Δ ≥ 1.
  - Proof: ALL8_NOTE3 §3. A block with no adjacent block supplies two tokens and only one is reserved. The other
    lies on a bounded single edge, so it is not an end token.
- Suppose X is a 3-fan with partner Q, and the ray of P on the non-partner side (first vertex T1) is not a block.
  Then Δ ≥ 1.
  - Proof: the face PXT1 has its edge XT1 single, because X's fourth sector is not a triangle.
  - If PT1 is single, the token at P on PT1 is free. If PT1 is double, T1 is multiple and the token at T1 on T1X
    is free.
  - That face is the only triangle on its single edge. Its designated block PX has a quad origin, so it is paid
    from S_P, not by a token (H_4 sits in D_P).
  - No outer-triangle (H_3, U_3, I_3), kite or U4/I4 payment is attached to this face. QX is not an edge of it.
  - The token is bounded, so it is not in F.

In particular, the non-kite block of every S° = 1 mask (§2.5) has no adjacent block, so **every slack-1 quad
forces Δ ≥ 1.**

## 2. Four local lemmas

All ray-order steps use only the following facts:
- the 2m rays of an m-fold point have cyclic order L1+ … Lm+ L1− … Lm−;
- the two neighbours of a ray lie on two different lines;
- two lines cross once.

### 2.1 Lemma S: the strong form of ALL8_NOTE3 (14) (PROVED)
**Setting.**
- P is a quad with a case-B kite (P, Q7, R0, Q1) at ray 0, centre X0. All its caps are double, and Q1, Q7, R0 are
  triple.
- Sector (6,7) at P is a triangle.
- Ray 5 is a block whose end X5 has a triangle in its sector (X5Q6, −PX5). This holds when X5 is a kite centre, or a
  3-fan whose partner is Q6.

**Claim.** Q6 is not a triple. The mirror statement (ray 3, sector (1,2)) says Q2 is not a triple.

**Proof.** Write C67 for Q6's line through Q7.
- **Q7.** Its lines are ℓ7, the diagonal d0 = Q7X0Q1, and C67. The faces X0Q7R0, PQ7X0 and PQ6Q7 make
  Q7R0, Q7X0, Q7P, Q7Q6 four consecutive rays. So Q7R0 and Q7Q6 are opposite rays of C67.
- **Exterior apex.** The exterior face on the case-B cap Q1R0 has apex Y = ℓ1 ∩ C67. Y lies beyond Q1 away from P,
  and beyond R0 away from Q7 (this is the computation in ALL8_NOTE3 §8).
- **Q6, if triple.** Its lines are ℓ6, X5's second line c5, and C67. By the neighbour rule at ray Q6P (faces PX5Q6
  and PQ6Q7), Q6Q7 lies on the third line, so that line is C67.
- **The extra face at X5.** The face on the far side of X5Q6 has third vertex R on ℓ5 beyond X5:
  - the kite's far corner, if X5 is a kite;
  - the 3-fan's outer vertex, if X5 is a 3-fan.

  Its side Q6R uses Q6's remaining line, C67, on the ray opposite Q7.
- **Contradiction.** Along C67 the order is R, Q6, Q7, R0, Y. But R ∈ ℓ5 = ℓ1 and Y ∈ ℓ1, so C67 meets ℓ1 twice. ∎

Note 3 stated only "Q4 quad, or both Q2 and Q6 quad". Its own proof uses only the triple at Q6 (the far corner lies
on ℓ1 automatically). A scratch straight-line model confirms the orientation: with Q7 = (t, −t) and R0 = (r, 0),
the apex Y lies on ray 1 exactly when r < 2t, and then C67 ∩ ℓ1 lies on ray 1, not ray 5.

### 2.2 Lemma C: chains through single-B stars (PROVED)
Let S be a zero-slack SB star.

**Claim.** On each of the lines SQ2 and SQ6, beyond S, there is a quad that is **not** zero-slack.

**Proof.**
- By Lemma S, Q2 and Q6 are quads.
- **Suppose Q2 is zero-slack.** At Q2 the bridge Q2S has two neighbours:
  - the block to S's kite 3, which contains the two quads S and Q2, so it is not case-B;
  - the bridge Q2Q1 (face SQ1Q2), where Q1 is S's triple case-B corner.
- **Mask of Q2.** It is not Alt (a bridge sits next to a bridge). It is not DB (the adjacent block is not case-B).
  So Q2 is SB, with S at position 2 or 6.
- **Next quad.** Lemma S at Q2 makes the vertex opposite S, beyond Q2 on SQ2, a quad P′. The same two neighbours
  appear at P′:
  - Q2's kite containing Q2 and P′;
  - the bridge to Q2's case-B corner, from face Q2P′(Q2's Q7).
- **Induction.** The chain runs monotonically along one proper line, so it must stop at a quad that is not
  zero-slack.
- The line SQ6 is handled the same way. The two lines meet only at S. ∎

No K3 hypothesis is used.

### 2.3 Lemma A: an alternating kite with two triple flanks (PROVED)
**Setting.**
- P is a quad, and ray i is a kite block (kite K = (P, A, R, T), centre X).
- The flanks A = Q_{i−1} and T = Q_{i+1} are triple.
- The sectors around rays i±1 and i±2 are triangles, and rays i−2 and i+2 are blocks of any type.
- B = Q_{i−3} is opposite T, and C = Q_{i+3} is opposite A.

**Facts.** The block end X_{i−2} is simple. Its two faces PQ_{i−3}X_{i−2} and PX_{i−2}A put A, X_{i−2} and B on one
line c0. That line is A's third line (by the neighbour rule at AP), so the cap AR ⊂ c0. Likewise c2 ∋ T, C and
TR ⊂ c2.

**(a) R triple.** Then TR and AR are both single, so K is a K1 kite with ≥ 2 single caps, and Δ ≥ 2.
- This is STAGE2_TASK6 §2.
- The exterior apex of TR would be ℓ_T ∩ c0 = B, on the wrong side of P.
- The exterior apex of AR would be ℓ_A ∩ c2 = C, also on the wrong side.

**(b) R quad, and its ray after RT (on the side away from RX) is a kite block.** Contradiction. Call that kite
(R, T, F, N), with centre V.
- Its triangle RTV and K's triangle RTX lie on opposite sides of TR.
- At the triple T, the ray TR lies on c2 and TX on the diagonal, so TV lies on ℓ_T.
- So the diagonal T V N is ℓ_T, and N ∈ ℓ_T. Also N ∈ c0, because N is R's first vertex on c0 beyond R, away from A.
- Hence N = ℓ_T ∩ c0 = B. But c0 has the order B, X_{i−2}, A, R, N. ✗
- The mirror (the kite before RA) gives N′ = C. ✗

**Corollary A′.**
- In a regime with Δ ≤ 1 and no zero-slack SB star, the far corner R of such a kite is not zero-slack.
- Reason: R's block to X is a non-case-B kite block (K has ≥ 2 quads), flanked by the triple bridges RA and RT (both
  double by e_mix).
  - Not DB, since the block is not case-B.
  - Not SB, by Lemma S at R: the non-case-B kites of an SB star are flanked by a quad at position 2 or 6.
  - So R is Alt, which is excluded by (b).

This replaces the 21-line count of STAGE2_TASK6 §§3–6. Task 6 §3's own V-kite (T, R+, T′, R−) has T′ = R+'s
bridge neighbour on c0 and T′ ∈ H, so T′ = B, which is already the contradiction.

### 2.4 Lemma P: runs of alternating stars (PROVED)
**Setting.**
- K3 = K4 = 0, except that in (b) a single kite κ may be K3.
- Δ ≤ 1.
- Every quad outside a set 𝒟 (the defect quads) is zero-slack.
- No zero-slack SB star exists.

**Claim.** Every zero-slack Alt star P ∉ 𝒟 has exactly two quad neighbours, on opposite rays of one axis H. The one
exception is the middle corner of κ in (b).

**Proof.**
- Suppose a kite of P has two triple flanks. By Lemma A, its far corner is in 𝒟.
- The four far corners of P's kites are distinct points, lying on the rays ℓ1± and ℓ3±.
- Suppose instead a kite of P has two quad flanks. Then that kite has ≥ 3 quads, so it is κ.
- **Away from κ, with |𝒟| ≤ 1.** On the 4-cycle (Q0, Q2, Q4, Q6), the only pattern with no adjacent quad–quad
  pair and at most one adjacent triple–triple pair is quad–triple–quad–triple. ∎

**Run corollary.**
- A quad neighbour Q0 of such a star is flanked at P by two of P's kites, each with ≥ 2 quads. So Q0 is Alt or in
  𝒟; it cannot be SB or DB.
- Hence a maximal run of zero-slack Alt stars along H can end only at points of 𝒟, at both ends.
- **With |𝒟| ≤ 1 there are no zero-slack Alt stars at all.**

### 2.5 Mask lists (PROVED by hand; a scratch enumeration agrees)
Constraints (ALL8_NOTE2 §6, ALL8_NOTE3 §§1–2, STAGE2_TASK5 §§1–2):
- no three consecutive blocks;
- kite blocks have no adjacent block;
- a case-B block excludes blocks at ±2 and forces sectors i−2 to i+1;
- two case-B blocks must be opposite.

**S° = 1.** These are all-8 only:
- **(d-A)** Alt with exactly one non-kite block;
- **(d-B)** SB with one of blocks 3 and 5 non-kite.

  Five blocks give at most one kite (pattern 11011010), and c_B = 2 forces S° = 0.

**S° = 2 under Δ = 0.** Here every non-kite block must have an adjacent block on its token side (§1.3).
- The scratch enumeration (scratchpad `masks.py`) leaves 25 all-8 and 12 seven-type masks.
- They are listed in §6.4 with the further cuts.

## 3. Case (b): K3 = 1 is impossible (PROVED)
All quads are zero-slack, Δ = 0, K4 = 0, U = 0. Let κ = (Q_a, Q_b, Q_c, R) be the K3 kite, with R triple and Q_b
opposite R.

1. **No SB stars.** By Lemma C, every chain would need a quad that is not zero-slack, and there is none.
2. **The kite's quad corners are Alt.** They are not DB, because DB blocks are case-B K1 kites
   (STAGE2_TASK5 §3, ALL8_NOTE3 §1). They are not SB, by step 1.
3. **Q_b is impossible.**
   - Q_b is Alt, and its κ-block is flanked by the quads Q_a and Q_c (rays 0 and 2, say).
   - The kites at rays 3 and 7 already contain two quads each. So Q4 or Q6 being a quad would create a second K3;
     both are triple.
   - The kite at ray 5 then has triple flanks Q4 and Q6, and rays 3 and 7 are blocks.
   - Lemma A(a) gives Δ ≥ 2 if R5 is triple. Corollary A′ excludes R5 as a zero-slack quad. ✗ ∎

The proof does not need an all-8 point or the star theorem.

**Audit asked for in the brief.** The star chain uses K3 = 0 in exactly one place: STAGE2_TASK7 §4, the branch "one
of Y, Z is quad", where W is triple by K3 = 0. That branch is never needed:
- Let Y be a zero-slack quad with V simple. Then YV is a non-case-B kite block, because Z must also be quad (the
  wrong-ray argument).
- The two consecutive bridges YA and YT then force the mask SB (positions 1, 2, 3) or DB. In either case YU is a
  block.
- So U is simple. But U = D+ ∩ γ−, and neither of those lines contains Y. This is STAGE2_TASK8 §4's short proof.

Lemma P also shows that a Y-quad would have to be DB. Every other star input (Lemma R, Lemma M, Lemma Q, STAGE2_TASK8
§§3–4 and §7) involves only case-B kites or zero masks. **So the star theorem holds verbatim when K3 ≤ 1 (PROVED).**
In (b) it is not needed.

## 4. Case (d): ΣS° = 1 and Δ = 1 is impossible (PROVED)
Let P* be the quad with S° = 1. It is all-8 with mask (d-A) or (d-B), and 𝒟 = {P*}. K = 0.

**Structure.**
- Lemma C: there are no zero-slack SB stars, because P* lies on at most one of a star's two chain lines.
- Lemma P: there are no zero-slack Alt stars.
- So every zero-slack quad is DB, and every non-case-B kite has at most one quad corner that is not P*. Concretely:
  every kite of P* has its other three corners triple. A quad corner would be zero-slack with a non-case-B kite
  block, so it would be Alt or SB.

**(d-A).**
- P*'s kites lie at rays 1, 3 and 5. The non-kite block is at ray 7.
- The kite at ray 3 has triple flanks Q2 and Q4, a triple far corner, and blocks at rays 1 and 5.
- Lemma A(a) then gives Δ ≥ 2 > 1. ✗

**(d-B).**
- The case-B block is at ray 0, the kite at ray 3, and sector (1,2) is a triangle.
- Lemma S makes Q2 a quad. But Q2 is a corner of the non-case-B kite 3 of P*, so it would have to be triple. ✗ ∎

The proof uses only Δ ≤ 1, so it does not use where the Δ token sits. §1.3 shows that the token must be the
residual token of P*'s isolated non-kite block, so Δ = 1 is in fact forced by P*.

## 5. Case (c2): two slack-1 quads (PROVED impossible)
Each slack-1 mask has a non-kite block with no adjacent block, so §1.3 gives Δ ≥ 1. This contradicts Δ = 0. ∎

## 6. Case (c1): one quad P* with S° = 2, Δ = 0, K = 0 (OPEN, reduced)

### 6.1 Structure (PROVED)
Take 𝒟 = {P*}. Lemmas C and P give:
- (i) **There are no zero-slack SB stars and no zero-slack Alt stars.** So the quads are P* together with some DB
  stars, which may be absent.
- (ii) **Every kite of P* has its other three corners triple.** A quad corner would be zero-slack and would carry a
  non-case-B kite block, so it would be Alt or SB.
- (iii) **Every 3-fan partner of P* is triple.** A quad partner would carry a non-kite block, so it would not be
  zero-slack.
- (iv) **Kite types.** P*'s non-case-B kites are K1 case A, with exactly one single cap (saturation, Δ = 0). Every
  non-kite block of P* has an adjacent block on its token side (§1.3).
- (v) **If P* is a 7-type,** some all-8 point exists, and it is a DB star.

### 6.2 Cuts on P*'s mask (PROVED)
**(W) Two forced single caps.** Take a kite of P* at ray i, with triple flanks and a triple far corner (by (ii)).
- Lemma A(a) applies to each side separately:
  - if ray i−2 is a block, the cap TR is single;
  - if ray i+2 is a block, the cap AR is single.
- Both together give two single caps. ✗
- At a 7-type, a flank on an N ray already gives one single cap, so any forced single cap from Lemma A(a) is a
  second one. ✗

**(S) Lemma S at P*'s case-B kite.** If P* has a kite, or a 3-fan whose partner is Q6 (resp. Q2), at ray ±3 from the
case-B block, then that flank or partner is a quad. That contradicts (ii) and (iii). ✗

**(L) Common cap line.** This cut is for the pattern X X R K R R K R, where rays 0 and 1 are non-kite blocks and
the kites are at rays 3 and 6.
- The block ends X0 and X1 are simple. The faces PQ7X0, PX0X1 and PX1Q2 put Q7, X0, X1 and Q2 on one line c.
- By (ii), the flank Q2 of kite 3 and the flank Q7 of kite 6 are triple. For each, c is its line other than its P-line
  and its kite diagonal (the neighbour rule at the ray toward P). So the caps Q2R3 and Q7R6 both lie on c.
- R6 ∈ ℓ6 = ℓ2 (on ray 6), and Q2 ∈ ℓ2 (on ray 2), so c meets ℓ2 twice. ✗

**(T) Mask K R K R R K R R.**
- **Kite 0.** Ray 2 is a block, so Q7R0 is single (W), and therefore Q1R0 is double.
- **Kite 2.** Ray 0 is a block, so Q3R2 is single, and therefore Q1R2 is double.
- **The full triple Q1.** Its two exterior faces have a common apex Y1 on ℓ1 beyond Q1. Ray order at R0 and R2
  puts Y1 on C67 (R0's third line) and on C34 (R2's third line). So Y1 = C34 ∩ C67, on ray 1.
- **Kite 5.** Its flanks Q4 and Q6 are triple, with third lines C34 and C67, so its far corner is
  R5 = C34 ∩ C67 = Y1. But R5 lies on ray 5. ✗

### 6.3 Where P* can sit relative to a DB star (PROVED, modulo the W13 §4 input list)
The star theorem for a DB star D uses non-zero-mask information at exactly these 14 vertices:

    B±, Y±, Z±, V±, U±, U±′

Everything else it uses is one of:
- case-B kite corners, which are triple by definition;
- Δ-lemmas;
- the zero mask of D itself.

At each of the 14 positions, a quad P* has **three consecutive bridges**:
- **B:** toward A, D and C.
- **V:** toward Y, T and Z.
- **U:** toward B, A and Y.
- **Y (Z is symmetric):** toward U, A and T.
  - If YV is a block, U must still be multiple. A simple U would lie on Y's line, but U = D+ ∩ γ−, and neither
    line contains Y.

So **if P* is not one of D's 14 positions, D is excluded verbatim.**

### 6.4 The S° = 2 masks after all cuts
Format: rays 0–7. C = case-B kite, K = case-A kite, F = end, Hl/Hr = 3-fan with partner on ray i−1 / i+1,
R = bridge, N = single.

**All-8 (25 masks).**

| Masks | Fate |
|---|---|
| `C R R K R R R R` | ✗ (S) |
| `C R R Hl F R R R`, `C R R Hl Hr R R R` | ✗ (S) |
| `F F R F F R K R`, `F F R F Hr R K R`, `F F R Hl F R K R`, `F F R Hl Hr R K R`, `F F R K R K R R` | ✗ (W) |
| `F Hr R F Hr R K R`, `F Hr R Hl F R K R`, `F Hr R Hl Hr R K R`, `F Hr R K R Hl F R` | ✗ (W) |
| `F Hr R K R Hl Hr R`, `F Hr R K R K R R`, `F Hr R R K R K R` | ✗ (W) |
| `Hl Hr R Hl Hr R K R`, `Hl Hr R K R K R R`, `K R K R K R R R` | ✗ (W) |
| `F F R K R R K R`, `F Hr R K R R K R`, `Hl Hr R K R R K R` | ✗ (L) |
| `K R K R R K R R` | ✗ (T) |
| **`C R R F F R R R`, `C R R F Hr R R R`, `C R R R K R R R`** | **OPEN** |

**7-type (12 masks; missing sector between the two N rays).**

| Masks | Fate |
|---|---|
| `C R N N R K R R`, `C R R K N N R R`, `C R N N F Hr R R` | ✗ (S) |
| `F F N N K R K R`, `F F R K N N K R`, `F Hr R K N N K R`, `F Hr R K R K N N`, `Hl Hr R K N N K R` | ✗ (W) |
| `K N N K R K R R`, `K N N R K R K R` | ✗ (W) |
| `C R N N F F R R` | ✗ by (v) and §6.3: no three consecutive bridges, so no DB star can host P*, and no all-8 point survives |
| **`C R N N K R R R`** | **OPEN** |

### 6.5 Precisely what remains open in (c1)
A 94 with W = 13 survives only if there is exactly one non-zero quad P*, all other quads are DB stars (possibly
none), K = 0, Δ = 0, U = 0, and P* is one of:

- **(O1)** all-8 `C R R F F R R R`: case-B kite at ray 0, two adjacent end blocks at rays 3 and 4. The lines ℓ3 and
  ℓ0 end at X3 and X4. The bridges at rays 5, 6, 7 form a run of three.
- **(O2)** all-8 `C R R F Hr R R R`: as (O1), but X4 is a 3-fan with a triple partner Q5.
- **(O3)** all-8 `C R R R K R R R`: case-B kite at ray 0 and a case-A K1 kite at ray 4, with all corners triple.
- **(O4)** 7-type `C R N N K R R R`: case-B kite at ray 0, a K1A kite at ray 4 whose single cap is PQ3, missing
  sector (2,3). This occurs only together with a DB star D, with P* at one of D's 14 positions and its bridges
  5, 6, 7 serving as the run of three.

For (O1)–(O3), either:
- P* is the only quad (no all-8 point other than P*); or
- P* is a DB star's B, Y, Z, V or return, using its run of three bridges at rays 5–7 (or 1–3 in (O3)).

Available inputs at P*'s own case-B kite:
- STAGE2_TASK6 §4: the apices Y and Z are multiple, and A, F and T are full.
- STAGE2_TASK7 §§2 and 4.
- The cap-continuation lemma.

**Suggested next step:** a short ray-order chase at the full triple R0 and the I-ends X3, X4 for (O1)/(O2); for
(O3)/(O4), the triangle of caps C12, C67, C23, C56 around H.

## 7. Side results

**7.1 A shorter Theorem 0 (PROVED, given the star theorem).** Assume ΣS° = 0, K3 = K4 = 0 and Δ = 0.
- Lemma C: there are no SB stars.
- Lemma P (with 𝒟 = ∅): there are no Alt stars.
- So every quad is an isolated DB star, and the star theorem excludes it.

This bypasses STAGE2_TASK6 §§3–6 (alternating endpoints, the 21-line count) and STAGE2_TASK7 §3 (the B–B path).
The two are consistent: STAGE2_TASK5 §4 already wrote "Q2, Q6 triple" for an SB star, and Lemma S says exactly
that this is contradictory.

**7.2 The K3 audit (PROVED).** See §3. The only use of K3 = 0 in the star chain is the quad Y/Z branch of
STAGE2_TASK7 §4, and STAGE2_TASK8 §4's U-simple argument covers it.

**7.3 Caution on "Route 1 / Route 2".** Lemma R at U+′ uses U−′ ∈ e3, which is Pin 5 at Y−. Lemma R at U− uses
U+ ∈ e1, which is Pin 5 at Y+. So the Z-side route also reads Y±. A single defect at some Y can therefore touch
both routes. §6.3 handles this by listing the 14 positions directly, rather than relying on the route split.

## 8. Checks performed
- **Scratch mask enumeration** (scratchpad `masks.py`): it reproduces the zero-slack table (3 all-8 masks) and the
  S° = 1 list, and gives the S° = 2 list of §6.4.
  - It encodes these rules: no three consecutive blocks; isolated kite blocks; case-B exclusions at ±1, ±2;
    opposite case-B pairs; case-B forced sectors; and the §1.3 token constraint.
- **Lemma S orientation**: checked in an explicit straight-line model (§2.1).
- **Dataset scan for Lemma S** (scratchpad `strong14.py`): across 3,474 records plus the binding witnesses there
  are only 4 case-B kites, and none has a kite at ±3 from its case-B block. So the scan has **no positive
  coverage**, and the proof is by hand only.
- **No SAT run.** All other claims are hand ray-order arguments.

**Hand-proof dependencies:**
- ALL8_NOTE3 §§1–3 and §8 (the mask table and the case-B exterior apex);
- STAGE2_TASK5 §§1–3;
- STAGE2_TASK6 §2 (the wrong-ray single caps);
- STAGE2_TASK8 §4;
- the W13.md §4 input list for the star theorem;
- the Δ-lemmas of ALL8_NOTE3/5, each worth ≥ 2 (§1.1).

**Independent referee recommended** for Lemma S, Lemma A(b), Lemma C, and the residual-token lemma §1.3 (3-fan
part). These are new.

## 9. Closing (c1): O1–O4 are impossible (PROVED; hand proof, needs a referee)
This section supersedes the OPEN entries in §6.4 and §6.5.

**Setting.** P* has the case-B kite at ray 0. In star notation (SOL_TASK8 Addendum 2):
- A+ = Q1, F+ = Q7, T+ = R0;
- a = ℓ1, b = ℓ2, c = ℓ3 = ℓ7;
- α+ = A+T+ ∋ Q2, and φ+ = F+T+ ∋ Q6, from the faces P*Q1Q2 and P*Q6Q7.

The faces P*Q1Q2, P*Q5Q6 and P*Q6Q7 exist in all four masks. Δ = 0, so every O*/M* step holds. The only
zero-slack quads are DB stars (§6.1).

### 9.0 The + end is intact (PROVED)
These are STAGE2_TASK6 §4 and the W13_caseE.md D1–D7 chain. Every step uses only the + kite and Δ-lemmas, plus the
following replacements:
- **Y+ is not a quad.** If V+ is multiple, the DB U-simple argument applies (U+ lies on D+ and on the line through
  B+, and neither contains Y+). If V+ is simple, V+'s kite is case-B, so Z+ is triple and its cap gives W = c∩H = P*. ✗
  The same holds for Z+.
- **V+ is not a quad.** Lemma 2.2 of W13_caseE runs on the + corner alone.

Consequences:
- T+ is full.
- Y+ and Z+ are triples, with third lines e1 ∋ V+, U+ and e2 ∋ V+, U+′.
- V+ is a triple, with W1+ = c∩e1 beyond Z+ and W2+ = a∩e2 beyond Y+.
- A+ and F+ are full, with U+ the first vertex on A+→(−D+) and U+′ = D+∩α− next to Q6.
- **Q6 is triple.** This is STAGE2_TASK5 §3, mirrored. If Q6 were a DB quad, its case-B kite at F+ would have corner
  Z+, and the cap continuation would put the exterior apex at b∩α+ = Q2, on the wrong ray. This uses only the + kite
  and Q2 ∈ α+.
- **Q2 is triple** in O1–O3. In O1 and O2 the reason is that Q2X3 is single, because X3 is the end of c. In O3 it is
  the STAGE2_TASK5 §3 argument itself (exterior apex b∩φ+ = Q6, wrong ray).

### 9.1 Two "+ half" facts (PROVED)
Let λ be Q2's third line, so that U+ ∈ λ.

**Fact (+Y).** φ+ ∩ λ lies on φ+ beyond Y+.
- **U+ triple** (lines D+, λ, e1). The face across U+Y+ from A+Y+U+ lies in U+'s sector (U+Y+, −λ) and in Y+'s
  sector (−φ+, −e1). Its third vertex is φ+∩λ.
- **U+ quad** (zero-slack, so DB with bridges U+Q2, U+A+, U+Y+ at positions 1–3). That face is (U+Y+, block 4). Its
  third vertex is the case-B centre X′, which lies on Y+→(−φ+).
  - So the kite diagonal Y+X′ is φ+.
  - Its opposite corner, U+'s position 5, lies on −λ.
  - Hence φ+∩λ lies beyond X′, beyond Y+.

**Fact (+Z)** (mirror). α+ ∩ (Q6's line through U+′) lies on α+ beyond Z+.

### 9.2 O1 (`C R R F F R R R`) and O2 (`C R R F Hr R R R`) — PROVED impossible
**The line κ.**
- X3 and X4 are simple. The faces P*Q2X3, P*X3X4 and P*X4Q5 put Q2, X3, X4 and Q5 on one line κ.
- So λ = κ, because Q2 is triple with lines b, α+, κ.

**Q5 is triple.**
- In O1, X4 is the end of H, so Q5X4 is single and Q5 is not all-8.
- In O2, Q5 is the 3-fan partner, which is triple by §6.1(iii).
- So Q5 has the lines a, κ, and α− = Q5Q6. The neighbour rule at Q5P* applies.

**The face across Q5Q6.** The face P*Q5Q6 is all-multiple, so Q5Q6 is double (M*). The face on its far side has
third vertex N:
- at Q5 it lies in the sector (Q5Q6, −κ), so N ∈ κ beyond Q5;
- at Q6 (ring Q5, P*, Q7, −α−, −b, −φ+) it lies in the sector (−φ+, Q6Q5), so N ∈ φ+ beyond Q6, away from F+.

**Contradiction.** N = φ+∩κ, on φ+ before Q6. Fact (+Y) puts φ+∩κ on φ+ after Y+. The order on φ+ is
N, Q6, F+, T+, Y+, so the single point φ+∩κ would sit at both ends. ✗ ∎

### 9.3 O3 (`C R R R K R R R`) — PROVED impossible
**Setting.**
- The ray-4 kite (P*, C− = Q3, T− = R4, A− = Q5) is K1 case A.
- Its corners are triple, and its P*-caps are double (P* is all-8). So exactly one of C−T− and A−T− is single.
- The mask and the + kite are symmetric under the reflection that fixes rays 0 and 4 (y ↦ −y). So WLOG **C−T− is
  single**.

**The lines.**
- B+ = Q2 lies on γ− := line C−T−. By the neighbour rule at C−P*, the face P*Q2Q3 gives this. So λ = γ−.
- B− = Q6 = b∩φ+∩α−, with α− = A−T−.

**The − facts we need (Y side only).**
- **Y− = a∩γ− is multiple.** If not, O*: the second face on T−Y− would have apex a∩H = P*, and the second face on
  A−Y− would have apex D−∩γ− = C−. Both are on the wrong rays.
- **T−A−Y− is all-multiple.** So A−Y− and T−Y− are double, and the face T−Y−V− exists.
- **A− is full.** P*A−Q6 is all-multiple, so A−Q6 is double. This gives the faces A−Y−U−′ and A−U−′Q6, so
  U−′ = D−∩φ+ next to Q6.
- **Y− is not a quad.**
  - If V− is multiple, Y− is DB with Y−T− in the middle. Then Y−U−′ is a block, so U−′ is simple, but it lies on D−
    and φ+, neither of which contains Y−. ✗
  - If V− is simple, Y−V− is a case-B block. V−'s kite then has corner Z′ = first vertex on T−→(−α−), and its cap
    T−Z′ is double. So T−'s sector (T−Z′, T−C−) is a face, and C−T− is double. ✗
- **So Y− is a triple** with third line e3 ∋ V−, U−′. Y−U−′ is double (M*), so the sector (−γ−, −e3) at Y− is a
  face.
- **U−′ is triple** (Lemma R at U−′, which needs only the + side and Y−).
  - Suppose U−′ is a quad. It is DB with bridges U−′Q6, U−′A−, U−′Y−.
  - Its kite at Q6 has far corner U+′ (the face F+U+′Q6 exists). U+′ is a case-B far corner, so it is a triple, with
    lines D+, α−, e2.
  - The kite's axis d contains U−′ ∈ φ+. But D+∩φ+ = F+ and α−∩φ+ = Q6, so d = e2.
  - Its kite at Y− has far corner on a beyond Y− (from the Y− ring). That corner lies on e2∩a = W2+, which is beyond
    Y+. ✗

**(−Y).** At the triple U−′ (lines D−, φ+, e3), the face across U−′Y− lies in (U−′Y−, −φ+). So γ−∩φ+ lies on φ+
beyond U−′.

**Contradiction.** Fact (+Y) puts γ−∩φ+ beyond Y+. The order on φ+ is U−′, Q6, F+, T+, Y+. ✗ ∎

This is the Y-side route (Lemma M, second half). The broken Z− side is never used, and neither is Lemma R at U+:
both cases of Fact (+Y) give the same point.

### 9.4 O4 (7-type `C R N N K R R R`) — PROVED impossible
P* is not all-8, so by §6.3 it occupies one of a DB star D's 14 positions. It does so through its only run of three
bridges, rays 5, 6, 7, whose middle is Q6.

**The − end of P* is intact apart from the missing sector (2,3).**
- The kite caps C−T− and A−T− are double. The single cap is P*C−, on the N ray.
- **T− is full.** Y− and Z− are multiple (O*).
- **A− is full.** U−′ = D−∩φ+.
- The face C−Z−U− exists. U− is the first vertex on C−→(−D−).
- **Y− is triple.** The proof is as in §9.3, except that the V−-simple case now uses the wrong ray: W = a∩H = P*.
- **Z− is triple.**
  - If V− is multiple and Z− is DB, then Z−'s case-B kite at C− forces the face P*C−(C−'s first vertex on −γ−).
    That face would occupy P*'s missing sector (2,3). ✗
  - If V− is simple, use the wrong ray: W = c∩H = P*. ✗
- **V− is a triple** with the face V−Z−W1−, W1− = c∩e3 beyond Z−.
  - V− simple puts U−, U−′ ∈ E. Then E = D−, but D−∩H = X4 ≠ V−. ✗
  - V− quad is excluded by Lemma 2.2 on the A− side.

**U+′ and U−′ are triples.**
- U−′: as in §9.3.
- U+′: its kites at Q6 and at Z+ have far corners U−′ (lines D−, φ+, e3) and W1+. So d = e3 and W1+ ∈ e3∩c = W1−,
  which lies on the opposite side. ✗

**The ring at Q6** (lines b, α−, φ+), in cyclic order:

    P*, Q5, U−′, G6, U+′, Q7        (G6 = first vertex on −b)

**Each position fails:**
- **B_D.** The middle bridge would be D = Q6, but Q6 is triple. ✗
- **U_D or Y_D/Z_D.** The middle Q6 would be the case-B corner A_D (or F_D).
  - Matching A's ring (B, D, X, T, Y, U) against Q6's ring, with P* placed as U or Y, puts either the quad D or the
    simple centre X_D on U+′ or U−′.
  - Both of those are triples. ✗
- **V_D.** The middle Q6 would be T_D. Matching T's ring (A, X, F, Z, V, Y) puts X_D = G6 and {A_D, F_D} = {U+′, U−′}.
  - D's diagonal must then be a common line of U+′ (D+, α−, e2) and U−′ (D−, φ+, e3).
  - No two of these lines coincide: compare their crossings with H (X+, T+, T−, V±, X4), or their crossings at F+,
    Q6, A−. ✗ ∎

### 9.5 Status of W = 13
Combined with §§3–5 and case (e) (W13_caseE.md, now refereed): **every W = 13 subcase (b), (c1), (c2), (d) and (e)
is excluded.**

**Referee priorities:**
1. §9.3, the step "Y− not a quad when V− is simple".
2. §9.4, the ring matching at Q6, and "Z− not a quad", which uses the missing sector.
3. §9.2: Q5 is triple and N ∈ κ.

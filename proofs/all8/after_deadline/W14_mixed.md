# W = 14, U = 0, H = 2 with at least one non-Δ defect (hand analysis, 2026-10-03; local only)

## 0. Summary

π = 4, so Λ = 6 = π + U + H gives U + H = 2. Here U = 0 and H = ½ΣS° + K3 + 2K4 + ½Δ = 2. Write 𝒟 for the set of
**defect quads** (S° ≥ 1). A **Z-quad** is a quad with S° = 0, so it is all-8 with mask Alt, SB or DB.

| Case | Hypothesis (all other terms 0) | Status |
|---|---|---|
| (i) | K4 = 1 | **PROVED impossible** (§3.1) |
| (ii) | K3 = 2 | **PROVED impossible** (§3.2) |
| (iii) | K3 = 1, ΣS° = 2, Δ = 0 | **PROVED impossible** (§3.3) |
| (iv) | K3 = 1, ΣS° = 1, Δ = 1 | **PROVED impossible** (§3.3) |
| (v) | K3 = 1, Δ = 2 | **PROVED impossible** (§3.3) |
| (vi-a) | ΣS° = 4 in one quad, Δ = 0 | **OPEN**: 17 masks (§5.3) |
| (vi-b) | two quads with S° = 2, Δ = 0 | **OPEN**: 39 configurations (§5.4) |
| (vii-a) | ΣS° = 3 in one quad, Δ = 1 | **OPEN**: 8 masks (§5.3) |
| (vii-b) | S° = 2 + S° = 1, Δ = 1 | **OPEN**: one configuration up to reflection (§5.2) |
| (vii-c) | three slack-1 quads, Δ = 1 | **PROVED impossible** (each needs a token, §1) |
| (viii-a) | ΣS° = 2 in one quad, Δ = 2 | **OPEN**: 2 masks, plus W13's O1–O5 with one spare Δ-event (§5.3) |
| (viii-b) | two slack-1 quads, Δ = 2 | **PROVED impossible** (§5.1) |
| (ix) | ΣS° = 1, Δ = 3 | **PROVED impossible** (§4) |

ΣS° + Δ is even, and the slack splits are as listed. With Δ = 0 there are no slack-1 quads, so (vi) is {4} or {2,2}.
With Δ = 1 the splits are {3}, {2,1} or {1,1,1}.

**New general results (§2):**
- **Lemma K.** A kite with ≥ 3 quad corners forces an infinite walk of alternating stars, unless enough defect quads
  stop it.
- **Lemma D1.** With one defect quad there are no alternating or single-B zero stars, for any Δ ≤ 3.
- **Lemma D2.** With two defect quads, all alternating and single-B zero stars form a single run on the line P1P2,
  strictly between P1 and P2. The QTTT stars that the old Lemma P allowed are impossible.
- **Lemma TB** (generalised twin corners). Two adjacent quads with a common neighbour that flanks an outer kite at
  both of them are impossible.
- **Lemma AR.** An alternating run cannot end at a quad that has a kite three rays away from the run.
- **Lemma W (sector-line windows).** A first-layer cut that contains Lemmas S, A(a), (W), (L), (T) and two new cuts
  (3-fan partner, I-end). Combined with triple optimality (Lemma TO), it reduces the mask lists to those of §5.

Scratch scripts (mask enumeration and window checks only) are in
`/tmp/claude-1000/-home-nail-stuff-sundai-math/f347ce4a-d4f4-4a94-af92-82771133b18b/scratchpad/w14m/`. They are
described in §6.

---

## 1. Budget: what survives two defect units

**1.1 (W13_caseBCD §1.1).** Every Δ-lemma failure costs ≥ 2 residual tokens, and failures on different
edges/kites/faces are disjoint (ALL8_NOTE5 (5)). The Δ-lemmas are O*, M*, η0, e_mix, the K0/K1A saturation, the
K1A surplus V_K and H*.

**1.2 Slack-1 tokens.**
- A slack-1 quad is all-8 with one isolated non-kite block (W13_caseBCD §2.5). By §1.3 there, it carries a residual
  token on the single cap of one of its two block faces P X T.
- That face has a simple X, double PX and double PT, so it belongs to none of the NOTE5 (5) sets:
  - not O*, because PX is double;
  - not M*, because X is simple;
  - not B*, because PT is double;
  - not H*, because the token is not on a central 3-fan cap PQ;
  - not V_K and not η0.
- Different quads give different faces.
- So **Δ ≥ (number of slack-1 quads) + (any Δ-lemma failures)**.

**Consequences:**
- (vii-c) {1,1,1} needs Δ ≥ 3 > 1, so it is impossible.
- In (i)–(iv), (vi), (vii) and (viii-b), **every Δ-lemma holds**. In (viii-b) the budget Δ = 2 is used by the two
  slack-1 tokens.
- In (v), Δ = 2 permits exactly one failure.
- In (viii-a) and (ix), at most one failure (2 tokens) is possible. In (ix) one token is already P*'s.

**1.3 Inputs used** (all refereed or accepted):
- masks (ALL8_NOTE3 §8, STAGE2_TASK5 §§1–2);
- Lemma S, Lemma A, Lemma C (W13_caseBCD §2, refereed);
- first-row lemma: an Alt star has a quad bridge neighbour (NOTE3 §8; it is Δ-free);
- triple-cap continuation (STAGE2_TASK7 §2);
- star theorem with its 14 positions (W13.md §§3–4; W13_caseBCD §6.3); Theorem E (W13_caseE);
- pencil half-ray lemma (STAGE2_TASK6 §6);
- triple optimality (both alternating sector sums of every triple are ≥ 2).

---

## 2. General lemmas

Notation for an Alt Z-star P:
- the four bridge neighbours are Q0, Q2, Q4, Q6;
- the kite at an odd ray r has flanks Q_{r−1}, Q_{r+1} and far corner R_r;
- the **pattern** is the cyclic word of Q (quad) / T (triple) on (Q0, Q2, Q4, Q6);
- a kite with two quad flanks is a **QQ kite**, and one with two triple flanks is a **TT kite**.

### 2.1 Lemma TT (PROVED, Δ-free except for its cost)
Let P be an Alt Z-star and κ a TT kite at ray r. Then one of the following holds:
- R_r is a triple and κ is K1 case A with both far caps single, so V_K(κ) ≥ 2 and Δ ≥ 2;
- R_r ∈ 𝒟.

*Proof.*
- Rays r±2 are kite blocks, so Lemma A(a) applies on both sides and makes both far caps single when R_r is a
  triple.
- Suppose R_r is a quad not in 𝒟. Then it is all-8.
  - Its ray to X_r is a non-case-B kite block (κ contains P and R_r), flanked by the bridges to the triples Q_{r±1}.
  - DB is impossible, because its blocks are case B.
  - SB is impossible: by Lemma S, each non-case-B kite of an SB star has a quad flank at position 2 or 6.
  - Alt is impossible: its kite block next to R_rQ_{r+1} contradicts Lemma A(b). ∎

(This is W13's Corollary A′ without its Δ ≤ 1 hypothesis: zero slack already gives all-8.)

### 2.2 Lemma AN (PROVED)
Let Q be a quad bridge neighbour of an Alt Z-star P. Then Q ∈ 𝒟, or Q is an Alt Z-star, or Q is an SB Z-star with P
at its position 4.

In the last case, Q's kites 3 and 5 both contain Q, P and Q2 or Q6 (quads by Lemma S). So **K3 + K4 ≥ 2**.

*Proof.* At Q the bridge QP is flanked by P's two kites through Q. These are non-case-B kite blocks at Q. Among the
zero masks, only Alt, and SB at position 4, have such a bridge. ∎

**Corollary.** If K3 = K4 = 0, every SB Z-star has Q4 triple, and no Alt Z-star is adjacent to an SB Z-star.

### 2.3 Lemma C (refereed; restated)
Let S be an SB Z-star. On each ray of the line ℓ2(S) = Q6 S Q2 there is a maximal chain of SB Z-stars consisting of
consecutive vertices. Each chain ends at a point of 𝒟. The two ends are distinct, on opposite sides of S.

### 2.4 Walk lemma (PROVED)
A QTQT Alt Z-star has its two quad neighbours on opposite rays of one line H.

Walking from it along H through QTQT Alt Z-stars gives distinct, monotone vertices of H. So the walk stops at a vertex
that is one of:
- in 𝒟;
- an SB Z-star entered at position 4;
- an Alt Z-star whose pattern is not QTQT.

(It is not DB, by AN.)

**Pattern facts.** Every Alt pattern contains a Q (first-row lemma).
- No QQ and at most one TT forces QTQT. Put a Q at position 0; positions 2 and 6 are T; then position 4 must be Q.
- QQ pairs at P are exactly the kites with ≥ 3 quads that have P opposite a non-quad corner, or all four corners
  quads.

### 2.5 Lemma K (K3/K4 kites) (PROVED)
Let κ be a kite with quad corners c1, c2, c3 (cyclically) and c2 opposite the fourth corner c4. Assume:
- K3 + K4 = 1 (only κ);
- no SB Z-stars;
- each Alt Z-star has at most one TT kite.

**Claim B.** If c2 is an Alt Z-star, then c2 has a TT kite, at the ray opposite κ.
- Its 4-cycle contains c1 and c3 (the QQ pair from κ).
- A third quad would create a second kite with ≥ 3 quads.
- So the other two neighbours are triples, and the kite between them is TT.

**Claim A.** If c1 is an Alt Z-star, then 𝒟 contains a point of the line c2c1 beyond c1.
- At c1, κ's flanks are c2 (Q) and c4 (T). Put c2 at position 0′ and c4 at 2′.
- The neighbour at 6′ is a triple, since a quad there would make a second QQ kite.
- The neighbour at 4′ is a quad, since otherwise c1 has two TT kites.
- So c1 is QTQT with axis c2c1. Walk away from c2.
- Every walk star lies on c2c1 beyond c1. It is therefore not a corner of κ: c3 is not on c2c1, because c1 and c3 lie
  on different lines through c2.
- So a walk star has no QQ kite and at most one TT kite, hence it is QTQT.
- With no SB Z-stars the walk can stop only in 𝒟. ∎

### 2.6 Lemma D1 (one defect quad) (PROVED)
Assume K3 = K4 = 0, 𝒟 = {P*} and Δ ≤ 3. Then **there are no Alt and no SB Z-stars**. Consequently:
- every kite of P* has its other three corners triple;
- every 3-fan partner of P* is triple;
- every quad bridge neighbour of P* is a DB star, with P* at its position B±.

*Proof.*
- **SB stars.** None, by Lemma C: a star needs two points of 𝒟.
- **TT kites.** Each needs far corner P* or costs Δ ≥ 2. So a star has at most two TT kites, and two only if one of
  them costs Δ ≥ 2. At most one such costly kite exists in the arrangement.
- **QTTT.** So the only non-QTQT pattern is QTTT, and at most one star D0 has it. D0's far corners are P* on its ray
  3′ or 5′, and a triple.
  - Its quad neighbour q0 (ray 0′) is not P*: different lines through D0.
  - By AN, q0 is Alt, hence QTQT with axis ℓ0′(D0).
  - The walk from q0 away from D0 must end in 𝒟 = {P*}. But P* ∉ ℓ0′(D0). ✗
- **QTQT only.** So every Alt Z-star is QTQT. A walk in both directions would need two distinct points of 𝒟. ✗
- **The consequences.** A quad kite corner of P* would be a Z-quad with a non-case-B kite block, i.e. Alt or SB. A
  quad 3-fan partner would carry a non-kite block, so it would lie in 𝒟. A DB star's bridge neighbours other than B±
  are its case-B corners, which are triples. ∎

### 2.7 Lemma D2 (two defect quads) (PROVED)
Assume K3 = K4 = 0, 𝒟 = {P1, P2}, and that all Δ-lemmas hold. This is true in (vi-b), (vii-b) and (viii-b) by §1.

Then the Alt and SB Z-stars together form at most one **run**: consecutive vertices of the line L = P1P2, strictly
between P1 and P2, either all Alt (all QTQT) or all SB (a Lemma C chain).

*Proof.*
- **Patterns.** A TT kite has its far corner in 𝒟, by Lemma TT and V_K = 0. So the patterns are QTQT and QTTT, and
  a QTTT star has far corners P1, P2 on its rays 3′ and 5′.

- **QTTT is impossible.** Let D be QTTT, with quad neighbour Q0 at ray 0, triples Y2, Y4, Y6, and P1 at ray 3. Let
  d1, d3, d5 be the diagonals of its kites at rays 1, 3, 5.
  - The cap Y2P1 lies on Y2's third line d1, and the cap Y4P1 on Y4's third line d5.
  - So P1 ∈ ℓ3(D) ∩ d1 ∩ d5. These lines meet H = ℓ0(D) at D, Q0 and Y4.
  - P1, P2 ∉ H, and an SB end is excluded by the Corollary to AN. So the walk from Q0 along H ends at another QTTT
    star D″, whose own lines put P1 on three lines meeting H at D″, Q0″ and Y4″.
  - If Q0 ≠ D″, these give ≥ 5 distinct points of H, hence 5 lines through P1. ✗
  - If Q0 = D″:
    - d1 passes through D″, and P1 lies on d1 beyond Y2.
    - The order on d1 is D″, X1, Y2, P1. So P1 lies on D″'s ray through X1, which is a kite ray adjacent to D″D
      (ray 1″ or 7″).
    - But P1 is a TT far corner of D″, so it lies on ray 3″ or 5″. ✗

- **Runs.** So every Alt Z-star is QTQT. By the walk lemma and the Corollary to AN, both ends of its walk lie in 𝒟, so
  the walk runs from P1 to P2 along L. SB chains likewise end at P1 and P2 (Lemma C).
- **Uniqueness.** Both kinds of run start at P1's first vertex toward P2, so there is at most one run. ∎

### 2.8 Rescue lemma (PROVED; setting of D2)
Let ρ be the ray of Pi along L toward Pj. A kite of Pi containing a quad other than Pi is **rescued**. The only
possibilities are:

| type | rescued kites | forced rays at Pi |
|---|---|---|
| Alt(ρ): Alt run star Z1 at ray ρ | at ρ ± 1 | ρ = R, ρ ± 2 = R |
| SB(ρ, σ): SB run star S1 at ray ρ | at ρ + σ (S1's kite 3) | ρ + 2σ = R; ray ρ − σ goes to S1's case-B corner Q1 |
| adj(ρ): Pj is Pi's first vertex on ρ | the kites (if any) at ρ ± 1 | each such kite forces ρ = R and ρ ± 2 = R |
| far(ρ): Pj is the far corner of Pi's kite at ρ | at ρ | ρ ± 1 = R |
| none | — | — |

Every other kite of Pi is K1 with triple corners. A DB star is never a kite corner of Pi.
- Run stars beyond Z1 lie on ray ρ beyond a bridge, so they are not kite corners.
- In adj/far, Pj is on a single ray of Pi.
- e_mix = 0 makes every rescued kite's caps double. This gives the forced R rays.

### 2.9 Lemma TB (generalised twin corners) (PROVED)
**Setting.**
- P, P′ are adjacent quads: the edge PP′ lies on L with no vertex between them.
- Y is a common neighbour (face P P′ Y).
- At P the rays toward P′, Y and the centre of a kite κ are consecutive; at P′ the rays toward P, Y and the centre of
  a kite κ′ are consecutive.
- The corners of κ and κ′ other than P, P′ are triples. Write R, R′ for the far corners and T, T′ for the other
  flanks.
- P's sector between T and its next ray W (W is P's first vertex on L beyond P, away from P′) is present; likewise at
  P′.
- At least one of the caps YR, YR′ is double.

**Claim.** This is impossible.

*Proof.*
- Y is a triple with lines m1 = PY, m2 = P′Y and d. The diagonals of both κ and κ′ through Y are d: the ray to each
  centre is adjacent to the ray to P or P′ on the far side.
- Y's ring is P′, P, X, R, R′, X′, with R ∈ m2 and R′ ∈ m1. So R ≠ R′.
- The double cap gives the face Y R R′ (sector (YR, YR′)).
- At the triple R the exterior ray beside RY is the ray of RT's line t away from T. So R′ ∈ t, and t ∋ W because
  T's third line carries the face P T W.
- Symmetrically R ∈ t′ ∋ W′. So t = t′ = RR′ contains W and W′.
- But W, W′ lie on L on opposite outer sides, and t ≠ L because T ∉ L. ✗ ∎

**Special cases:**
- both kites case B (W13-style "twin case-B corners");
- an SB run star S1 next to Pi, when Pi has a case-B kite flanked by S1's case-B corner (SB(ρ, σ) with a C kite at
  ρ − 2σ).

### 2.10 Lemma AR (Alt-run end) (PROVED)
Assume Alt(ρ) at Pi, and suppose Pi has a K1 kite at ρ + 3 (or ρ − 3) whose flank Y_{ρ+2} is a triple. Then this is
impossible.

*Proof.*
- **R_{ρ+3} ∈ d_{ρ+1}.** The flank Y_{ρ+2}'s third line, relative to the kite at ρ+3, is the diagonal d_{ρ+1} of the
  rescued kite at ρ+1. So R_{ρ+3} ∈ d_{ρ+1}, on ray ρ+3.
- **Z1's opposite kite.** At Z1 (Alt), the kite block opposite X_{ρ+1} on d_{ρ+1} has flanks Z2 (on L) and
  R_{ρ−1} (the far corner of Pi's rescued kite at ρ−1).
- **The ring at R_{ρ−1}.** The triple R_{ρ−1} has rays toward Y_{ρ−2}, X_{ρ−1} and Z1 consecutive. Alternation puts
  that kite's centre on the ray opposite Y_{ρ−2}, and its far corner F on ℓ_{ρ−1} beyond R_{ρ−1}.
- **Contradiction.** So d_{ρ+1} meets ℓ_{ρ−1} = ℓ_{ρ+3} at F (ray ρ−1) and at R_{ρ+3} (ray ρ+3). ✗ ∎

### 2.11 Lemma W (sector-line windows) and Lemma TO (PROVED)
**Setting.** P is a quad, Y_j is the first vertex on ray j, and the sector (j, j+1) is a face P Y_j Y_{j+1} when
present. Its third side lies on the **sector line** s_j. A **window** is a set of four consecutive rays.

**W1.** If Y_j is simple (a block end), then s_{j−1} = s_j.

**W2.** Every s_j meets exactly the four rays of one window. This is the pencil half-ray lemma for four lines: a
pseudoline not through P crosses each pencil line once and ends in the antipodal sector, so it crosses its rays
monotonically. The window contains the rays of all named points of s_j.

**W3 (far corner on caps).** For a kite at r with triple flank Y_{r−1}, and sector (r−2, r−1) present:
- the rays of Y_{r−1} toward Y_{r−2}, P and X_r are consecutive;
- so the cap Y_{r−1}R_r lies on s_{r−2};
- hence R_r ∈ s_{r−2} on ray r, and likewise R_r ∈ s_{r+1}.

**W4 (exterior faces).** Suppose R_r and Y_{r+1} are triples and the cap Y_{r+1}R_r is double. Its exterior apex
lies on ray r+1 (beyond Y_{r+1}) and on s_{r−2} (at R_r, the exterior ray beside R_rY_{r+1} is −s_{r−2}). So s_{r−2}
meets ray r+1. Mirror for Y_{r−1}R_r.
- Case B: both far caps double.
- Case A with s single caps costs 2(s−1).

**W5 (3-fan).** For a 3-fan at r with triple partner Y_{r+1}:
- its third triangle X_r Y_{r+1} R′ has R′ on ray r beyond X_r;
- at the partner, the triangle uses the ray −s_{r+1};
- so s_{r+1} meets ray r. (Mirror for partner Y_{r−1}.) This gives Lemma S for 3-fans.

**W6 (I-ends).** For an F block at j (U = 0, so it is an I-end), ℓ_j has no vertex beyond X_j. So no line except
s_j meets ray j. Two opposite F blocks give ℓ_j only 5 crossings. ✗

**W7.** Two distinct lines share at most one point. For example, two far corners on the same two sector lines must
coincide.

**Lemma TO (triple optimality at first-layer triples).** Use it only when M* holds.

- **TO1.** Let a bridge triple Y_j have one of its outer edges single (the neighbour ray is F, or a 3-fan whose
  partner is not Y_j).
  - The alternating sums force the sector (−s_{j−1}, −ℓ_j) or (−ℓ_j, −s_j) at Y_j to be a face.
  - So some line crosses ray j beyond Y_j.
  - If W6 leaves no window through j (for example, F at j−1 and at j+1), this is impossible.
- **TO2.** At a K1-kite flank A = Y_{r−1}, the odd alternating sum is 1 + [AR double] + [edge A–Y_{r−2} double] ≥ 2.
  So **if AR is single, the edge AY_{r−2} is double.** This kills an F or a non-partner 3-fan at r−2.

The named cuts are special cases of W1–W7 and TO:
- Lemma S: windows of s6 from the C kite and from the kite at 5.
- Lemma A(a) and (W): W1 + W2 + W4.
- (L) is strengthened to **L′**: a kite with a triple flank Y_{r−1} and blocks at r−2, r−3 is impossible, because
  s_{r−2} then meets rays r−4..r−1 but must contain R_r.
- (T): W3 + W4 on s6 and s1.

**Worked example (TO1 + W6), `C R R F R F R R`.**
- Q4 is a triple between the two I-end caps, so its sectors beside Q4X3 and Q4X5 (away from P*) are not faces.
- Optimality then forces faces on both sides of Q4's ray beyond Q4 (ray 4), so a vertex lies on ray 4 beyond Q4.
- But every line other than X3's and X5's caps must avoid rays 3 and 5 (W6), and no window contains 4 while
  avoiding 3 and 5. ✗

---

## 3. The K-cases

### 3.1 (i) K4 = 1 (PROVED impossible)
Here 𝒟 = ∅ and Δ = 0, so there are no SB Z-stars (Lemma C).

1. A corner P of the K4 kite κ is a Z-quad with a non-case-B kite block, hence Alt.
2. κ is a QQ kite at P. A second QQ pair would be a second kite with ≥ 3 quads, so P's other two neighbours are
   triples.
3. The kite between them is TT. Lemma TT then requires Δ ≥ 2 or 𝒟 ≠ ∅. ✗ ∎

### 3.2 (ii) K3 = 2 (PROVED impossible)
Here 𝒟 = ∅, Δ = 0 and there are no SB Z-stars. So, by Lemma TT, no Alt star has a TT kite.

1. Let κ1 be a K3 kite with middle quad c2 (opposite the triple). c2 is Alt and has a QQ pair.
2. Patterns without TT and with a QQ pair are QQQT and QQQQ. QQQQ gives four kites with ≥ 3 quads.
3. So c2 is QQQT, and both K3 kites κ1, κ2 sit at c2, sharing the flank M. κ1 = (c2, Q0, R1, M) and
   κ2 = (c2, M, R3, Q4), with R1, R3 triples.
4. M is Alt. Its 4-cycle is c2 (Q), R1 (T), x, R3 (T). Since there is no TT, x is a quad. So M is QTQT with axis
   H = c2M.
5. Walk from M along H away from c2. Every walk vertex lies on H beyond M, hence it is not Q0 or Q4, which lie on the
   other line ℓ0(c2) through c2. So walk vertices are not corners of κ1, κ2: no QQ and no TT, hence QTQT. The walk
   never stops (𝒟 = ∅, no SB). ✗ ∎

### 3.3 (iii), (iv), (v) K3 = 1 (PROVED impossible)
**Hypotheses of Lemma K.**
- (iii) and (iv): 𝒟 = {P*}, Δ ≤ 1. A TT kite needs far corner P*, so each star has at most one TT kite.
- (v): 𝒟 = ∅, Δ = 2. One TT kite costs all of Δ, so there is at most one in total.
- In every case |𝒟| ≤ 1, so there are no SB Z-stars.
- c1, c2, c3 lie in 𝒟 or are Alt Z-stars. They are not DB, because κ is not case B.

**(v).** c1 is Alt. By Claim A, 𝒟 ≠ ∅. ✗

**(iii), (iv).**
- **If c2 ≠ P*:**
  - c2 is Alt. By Claim B and Δ ≤ 1, its TT kite has far corner P*, on c2's ray opposite κ.
  - So P* ∉ {c1, c3}, and c1 is Alt.
  - By Claim A, P* lies on the line c2c1. But P* lies on another line through c2. ✗
- **If c2 = P*:** c1 is Alt. By Claim A, a point of 𝒟 lies beyond c1 on c2c1. The only point of 𝒟 is c2, which is
  behind c1. ✗ ∎

(The proofs use neither the star theorem nor an all-8 point. They also give a two-line proof of W13 case (b).)

---

## 4. (ix) ΣS° = 1, Δ = 3 (PROVED impossible)

𝒟 = {P*}, and P* is all-8 with mask (d-A) or (d-B). By D1 (valid for Δ ≤ 3), P*'s kites have triple corners.
- **(d-A)** = `X R K R K R K R`. Each of the three kites has blocks at both ±2. So each has two single caps
  (Lemma A(a)) and V_K ≥ 6 > 3. ✗
- **(d-B)** = `C R R X R K R R` (or its mirror). Lemma S makes Q6 (resp. Q2), a corner of the kite at 5 (resp. 3),
  non-triple. But kite corners are triple. ✗ ∎

---

## 5. The slack cases with ΣS° ≥ 2

### 5.1 (viii-b) two slack-1 quads, Δ = 2 (PROVED impossible)
All Δ-lemmas hold (§1), and D2 and the rescue lemma apply.

**(d-A) at Pi.** Its kites at 2, 4, 6 each have blocks at ±2. An unrescued (K1) one would have two single caps by
Lemma A(a), so V_K ≥ 2, but V_K = 0. So all three must be rescued. At most two kites are rescued, and those are
adjacent to ρ. ✗

**(d-B) at Pi** (`C R R X R K R R`).
- **Q6 is a quad.** By Lemma S, Q6 is not a triple. It is a kite flank, so it is not DB. So Q6 is a run star or Pj
  adjacent at ρ = 6.
- **Alt(6)** needs a kite at 7. ✗ So the rescue is SB(6, −1) or adj(6).
- **X = Hl** (partner Q2) also makes Q2 a quad, on the opposite side of Pi along ℓ2. That side holds no run star and
  not Pj. ✗
- **SB(6, −1).** S1's case-B corner Q1(S1) is Y7, which flanks Pi's case-B kite. Lemma TB applies (both kites case
  B). ✗
- **adj(6).** Pj is also (d-B) with Pi at its ray 6, and the common neighbour Y7 flanks both case-B kites. Lemma TB
  applies. ✗ ∎

### 5.2 (vii-b) S° = 2 + S° = 1, Δ = 1 (OPEN, one configuration)
By §5.1, the slack-1 quad P2 is (d-B) with X ∈ {F, Hr} and rescue adj(6). The SB rescue dies by TB. So P1 (slack 2,
no token) is adjacent to P2 and shares exactly one kite with it, and the common neighbour Y is P2's case-B flank.

The window/TO/rescue enumeration leaves these candidates for P1, and every one except O3 dies:

| P1 candidate | fate |
|---|---|
| `C R R K R R R R` adj 2 | TB: Y is P1's case-B flank |
| `C R N N R K R R` adj 6 | TB |
| `F F R K R K R R` adj 2 | Y simple at P1 but triple at P2 |
| `F Hr R K R K R R` adj 2 | Y simple at P1 but triple at P2 |
| `C R R R K R R R` (O3 mask) adj 3 | **survives** (adj 5 is its mirror) |

**OPEN configuration (vii-b·1).**
- P1 = `C R R R K R R R`, with P2 at ray 3, the shared kite at 4 and Y = Y2.
- P2 = `C R R X R K R R` (X = F or Hr), with P1 at ray 6′, the shared kite at 5′ and Y = Y7′.

Forced incidences (proved):
- s1(P1) = P2's case-B diagonal, through R0, Y1, Y, X0′, Y1′.
- s5(P1) = s2′(P2), through Y6, Y5, R4, X3′, Y2′ (window {3, 4, 5, 6}).
- Y is full, and its sixth face is Y Y1 E_Y with E_Y = d0(P1) ∩ P2Y ∩ s1′(P2).

No contradiction found yet. Next step: a joint window check of both pencils.

### 5.3 One defect quad: (vi-a), (vii-a), (viii-a) (OPEN lists)
**What is proved.** By D1, every quad other than P* is a DB star.
- A DB star is excluded by the star theorem (Δ ≤ 1) or by Theorem E (one failure), unless P* occupies one of its 14
  positions (W13_caseBCD §6.3).
- At those positions P* has three consecutive bridges ("RRR").
- A 94 has an all-8 point. So **a 7-type P* must host a DB star through an RRR run.**

**What remains.** Applying the enumeration (§6) with W1–W7, TO (when no spare Δ ≥ 2), the dmin budget and the RRR
requirement leaves:

**(vi-a) S° = 4, Δ = 0: 17 masks.**
- all-8: `C R R R R R R R`, `F F R R Hl Hr R R`, `F F R R K R R R`, `F Hr R R Hl Hr R R`, `F Hr R R K R R R`,
  `F Hr R R R K R R`, `Hl Hr R R Hl Hr R R`, `Hl Hr R R K R R R`, `K R K R R R R R`, `K R R K R R R R`,
  `K R R R K R R R`;
- 7-type (must host): `C R N N R R R R`, `C R R N N R R R`, `F F N N K R R R`, `F Hr R R R K N N`,
  `K N N K R R R R`, `K N N R K R R R`.

**(vii-a) S° = 3, Δ = 1: 8 masks.** Every S° = 3 mask has a forced residual token (dmin ≥ 1), so Δ = 1 is used
exactly.
- all-8: `C R R F R R R R`, `C R R Hr R R R R`, `C R R R F R R R`, `C R R R Hl R R R`, `F F R Hr R K R R`,
  `F R R K R K R R`;
- 7-type (must host): `C R N N F R R R`, `C R N N Hr R R R`.

**(viii-a) S° = 2, Δ = 2: 7 masks.**
- No spare Δ: `C R R F R Hl R R` and `C R R Hr R Hl R R` (all-8, two forced tokens). New; the §9 technique (Facts
  (+Y), (+Z) on the intact case-B end) is the natural next step.
- Spare Δ-event of cost 2: O1, O2, O3, O4 of W13 §9, and O5 = `C R N N F F R R`. W13 §9 closes these at Δ = 0. Its
  steps use O*/M* (for example M* on Q5Q6 in §9.2, and Y3 inside Fact (+Y)). A single failure at one of those steps
  is not yet audited.
- O5 has no RRR run. It survives only if the Δ-event occurs at a DB star that P* hosts.

**Remark.** The high-slack all-8 masks (for example `K R R R K R R R`) pass every first-layer test, and an explicit
straight-line octagon realises their first layer. Excluding them needs second-layer faces (the outer faces of the
bridge triangles, triple optimality at the Q_j) or a global argument. P* may be the only quad.

### 5.4 (vi-b) two slack-2 quads, Δ = 0 (OPEN, 39 configurations)
**What is proved.** Lemma D2, rescue, W/TO at both quads, AR (all Alt runs die), TB, and the face-type matching at
common neighbours:
- an I-end neighbour of one quad is joined to the other by a single edge;
- a 3-fan neighbour is a block at the other quad only if that quad is its partner.

A pair of 7-types without a free RRR run has no all-8 point and is excluded.

O1–O5 are as in §5.3. "adj k" means the other quad is the first vertex on ray k; "SB k σ" and "far k" are as in §2.8.

**none–none (14 pairs).** All unordered pairs from {O1, O2, O3, O4, O5}, except O5–O5. Neither quad meets the
other's kites and they are not adjacent.
- W13 §9 excludes the all-8 member, unless the other quad sits at one of the non-adjacent vertices its §9 proof uses:
  the apices Y, Z, V, the returns U, U′ or the tips W1, W2, at either end.
- A 7-type member needs no host when the other member is all-8.

**SB runs (3).** O3 SB 3 +1 with O3 SB 3 +1; O3 SB 3 +1 with O3 SB 5 −1; O3 SB 5 −1 with O3 SB 5 −1. The chain of
SB stars on L has S1's case-B corner equal to O3's Y2 (resp. Y6).

**far–far (1).** O3 far 4 with O3 far 4: the ray-4 kites coincide, (P1, Y3, P2, Y5).

**adj–adj (21).**

    CRRKRRRR adj2 | O3 adj3          CRRKRRRR adj2 | O3 adj5          O3 adj3 | O3 adj3
    O3 adj3 | O3 adj5                O3 adj3 | CRNNRKRR adj6      O3 adj5 | O3 adj5
    O3 adj5 | CRNNRKRR adj6          KRKRKRRR adj1 | KRKRKRRR adj1    KRKRKRRR adj1 | KRKRKRRR adj3
    KRKRKRRR adj3 | KRKRKRRR adj3    O1 adj6 | O1 adj6                O1 adj6 | O2 adj6
    O1 adj6 | O4 adj6                O2 adj5 | O2 adj5                O2 adj5 | CRRHlFRRR adj2
    O2 adj5 | CRRHlHrRRR adj2        O2 adj5 | CRNNFHrRR adj6         O2 adj6 | O2 adj6
    O2 adj6 | O4 adj6                FHrRKRKRR adj2 | FHrRKRKRR adj2  O4 adj2(N) | O5 adj3(N)

The `K R K R K R R R` pairs share both kites, like a run of length 0. Lemma AR does not apply, because there is no
Alt star whose opposite kite could give a second meeting point.

---

## 6. Checks performed (scratch only; scratchpad `w14m/`)

- **`masks14.py`.** Enumerates all quad masks with S° = 1–4 (all-8 and 7-type) under these rules:
  - no three consecutive blocks; isolated kites;
  - case-B: ±2 exclusion, forced sectors, no N neighbour; two case-B blocks opposite;
  - a 3-fan partner is R or N.
  
  It computes the forced Δ (dmin): Lemma A(a) single caps, N caps, isolated F (1), 3-fan with a non-block
  non-partner side (1), H* (2).
  - It reproduces W13's lists: S° = 1 (5 masks), and S° = 2 with Δ = 0 (the 10 all-8 and 5 7-type masks remaining
    after (W)).
- **`layer1.py`, `layer1to.py`.** Apply W1–W7 and TO to the single-defect masks: 174 → 49 → 43. Adding RRR for
  7-types gives the §5.3 lists. TO is used only when the spare Δ is < 2.
- **`twodef.py`, `pairs*.py`, `final_vib.py`.**
  - Rescue enumeration for each defect quad, with window and TO checks in which rescued kites drop the constraints
    of their quad flank.
  - AR; pair matching (rescue type, edge type, number of shared kites, face types); TB.
  - Output: the lists of §§5.1–5.4.
- **Hand only.** Every PROVED statement in §§2–5.1 is a hand proof. The scripts only enumerate masks and window
  assignments, which a referee can recheck by hand from W1–W7.
- **Coverage caveat.** No dataset record contains these configurations. The lemmas have no positive sample coverage.

## 7. Referee priorities
1. **Lemma D2, the QTTT step:** the line count through P1, and the adjacent case Q0 = D″.
2. **Lemma TB:** the ring at Y, and why the far-cap lines through T and T′ pass through W and W′.
3. **Lemma K, Claim A:** the walk never meets κ's corners.
4. **Lemma AR:** the identification of the far corner F of Z1's opposite kite on ℓ_{ρ−1}.
5. **§1.2:** disjointness of slack-1 tokens from the NOTE5 (5) sets.
6. **W5 and TO2:** these are new first-layer constraints.

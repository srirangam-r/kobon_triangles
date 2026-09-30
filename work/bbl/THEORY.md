# A uniform route: generalized BBL charging (2026-09-29)

Goal: T ≤ 93 at n = 18 for all arrangements, triple points included. Equivalently Λ = n(n−2) − 3T ≥ 7,
hence Λ ≥ 9 (Λ ≡ 0 mod 3). The old route (master inequality 2Λ ≥ n + Φ, prove Φ ≥ −5) needs a global case
analysis over k; k ≥ 6 with bridges is open there. This route is **local and independent of k**.

## 1. Exact budget

  **Λ = Z + Σ_P c_P,   c_P = 3 − D_P − β_P/2.**

This is exact for triple points only (L1: D = Σ D_P + β). Here D_P counts the doubly used first segments at P
with a simple far end (blocks), and β_P the doubly used first segments at P whose far end is multiple (bridges).

For 4-fold points, c_P = 8 − D_P − β_P/2 ≥ 2 with 8 rays. That is ≥ 1/2 per line, so they are harmless and are
handled separately.

## 2. Findings from data

About 130k exactly evaluated arrangements (n = 14–22), plus 1.15M held-out walk classes at n = 18.

- **Cluster charge.** Connected components of the bridge graph have c(Q) = 3|Q| − ΣD_P − β(Q).
  - In every near-optimal set, c(Q) ≥ 3.
  - The only c(Q) = 2 case is a bent-pair cluster at Λ = 14.
  - W6 (7 points, 12 bridges, 9 lines, self-capped) has c = 3.
- **Density.** Σ_P c_P ≥ N_mult/3 in every set, where N_mult is the number of lines through a triple point.
  - Equality holds only for isolated X points and W6 (and disjoint unions of them).
  - The per-line version fails: Σ_{P∈L} c_P ≥ 1 is false on some lattice lines.
- **Records.** Every n = 14, 20, 22 record has β = 0.

## 3. The charging (generalized BBL)

BBL (arXiv 0706.0723, Thm 1.1, simple arrangements) proves Λ ≥ n/3. Their argument:
- A perfect line (all n − 2 segments used) has alternating triangles.
- So one end forces an unused segment on the extremity line.
- Each unused segment serves ≤ 2 such lines.

Generalization:

- **U:** each unused segment u gives 1/3 to its own line and 1/3 to the other line at each simple endpoint
  (a *touch*).
- **P:** each triple point P gives c_P/3 to each of its three lines.

So Σ_L q0(L) = Λ − (1/3)·Z_tr ≤ Λ.

**Target lemma: after local transfer rules, every line has charge ≥ 1/3.** Then Λ ≥ n/3, and
Λ ≡ n(n−2) (mod 3) gives:

| n | Λ ≥ | T ≤ | record | status |
|---|---|---|---|---|
| 10 | 5 | 25 | 25 | exact |
| 12 | 6 | 38 | 38 | exact |
| 14 | 6 | 54 | 54 | exact (54 uses triple points; only simple arrangements were proven before) |
| 16 | 8 | 72 | 72 | exact (new for non-simple) |
| 18 | 6 | 94 | 93 | equality case must be excluded |
| 20 | 9 | 117 | 117 | exact |

For clean lines the alternation survives. A clean line avoids triple points and caps no block. Its vertices are
simple, so no segment of it is doubly used (L1), and two consecutive triangles on one side would need a triple
apex capped by the line. So BBL's end argument applies: Z_L ≥ 1 or a touch.

## 4. Transfer rules so far (search/bbl_rules.py)

Every block [P, X] on axis ℓ with cap C has one Lemma-A status for the segment u of ℓ beyond X:

- **U:** u is unused, so ℓ owns 1/3 and C gets a touch.
- **M:** mutual pair. The face beyond X is a triangle, so [Q, X] is a block at some Q ∈ C capped by ℓ.
- **I:** u is unbounded.

These are the only possibilities (Lemma A). At an axis both statuses cannot be I.

- **R1 (cap rescue).** If C passes through no triple point and C has no touch at X (so the status is I), ℓ gives
  1/3 to C.
- **R2 (chain rule).**
  - Mutual pairs link block points into paths.
  - The axes' block surplus on a path is (#U − #I)/3.
  - Pass 1/3 along the path from a U end to each I end.
  - Implemented so far for X–X chains only.

Status on the data after R1 + R2:
- 0.5–5% of arrangements still have a deficient line.
- Remaining classes:
  - (a) chains whose mutual partner is not an X point (generalize R2 to all block points: mutual components);
  - (b) (I, I) chains: both ends unbounded; locally short by 2/3;
  - (c) lattice lines through (D, β) = (1, 5) points, which reach −1/3; they need a bridge rule.

## 4b. The unit lemma (the single remaining statement)

**Units.** Take the graph on triple points whose edges are:
- sharing a line;
- mutual pairs;
- sharing a pure cap (a cap line through no triple point).

A unit K is a connected component. Units are line-disjoint. Every non-clean line is either:
- a line through a triple point (L(K)), or
- a pure cap (PC(K)),

and it belongs to exactly one unit.

**Unit lemma (integer form).** For every unit K:

  3·#blocks(K) + 3·β(K) + |PC(K)| ≤ 6|K| + σ(K) + |U(K)| + Upc(K),

where:
- σ(K) is the number of links (consecutive triple points on a line);
- U(K) is the set of distinct segments u beyond U-status blocks;
- Upc(K) is the number of U-blocks with a pure cap.

Equality holds only if K is a single X point with sides (I, U).

Equivalently:

  Σ_{P∈K} c_P + (|U(K)| + Upc(K))/3 ≥ (|L(K)| + |PC(K)|)/3.

**Evidence.**
- 1.33M arrangements (n = 16, 18; T from 70 to 93, including 1.15M held-out walk classes).
- Every unit has slack ≥ 0, in multiples of 1/3.
- Every tight unit is a single (I, U) X point.
- Status "O" (used but not mutual) never occurs, consistent with Lemma A.
- Tools: search/bbl_unit.py --lineconn, search/bbl_point.py.

## 4c. Assembly: unit lemma ⇒ Λ ≥ n/3; at n = 18 ⇒ T ≤ 93

Portions: each unused segment has 3 portions (own line; the other line at each simple endpoint; a multiple endpoint
is waste). So Λ = Σ_P c_P + (#portions)/3.

The U-portions of K are:
- the own portions of U(K) (they go to axes in L(K));
- the X-endpoint portions of U-blocks with pure caps (they go to PC(K)).

These are disjoint across units: facing blocks share an axis, hence a unit.

Clean lines are in no unit. Each has a touch (L3), and those portions are not U-portions. So:

  Λ ≥ Σ_K [Σc + U-portions/3] + #clean/3 + rest/3 ≥ (#non-clean + #clean)/3 = n/3.

**n = 18, T = 94 (Λ = 6):** equality everywhere.
1. Every unit is tight, so it is a single (I, U) X point with 5 private lines.
2. Each clean line gets exactly one portion, a touch. So no unused segment lies on a clean line.
3. rest = 0, so every unused segment is some unit's U-segment. Hence Z = a (the number of X points).
4. Λ = Z + Σc = 2a = 6 gives a = 3.
5. The three X points are in different units, so no line joins two triple points (general position).
6. **Theorem H** then gives Λ ≥ 8. Contradiction.

So **unit lemma + L3 + Lemma A + Theorem H ⇒ K(18) = 93** for pseudoline arrangements with triple points.
4-fold points are still to be added to units: c_P ≥ 2 over 4 lines.

For even n in general: Λ ≥ n/3, giving K(14) = 54, K(16) = 72 and K(20) = 117 for all arrangements.

## 5. The n = 18 equality case

If the target lemma holds, a 94 has every line at exactly 1/3, with no waste anywhere:
- Z_tr = 0;
- each unused segment serves exactly 3 lines (own + 2 touches);
- no line has surplus.

Blanc's stronger fact for clean lines (a touch is forced, not just Z_L ≥ 1) already rules out large families. For
example, W6 + 9 clean lines needs 9 touches, so Z ≥ 5, not 3.

Plan: characterize the zero-slack structures, then run decisive pinned SAT on each.

## 6. Verification plan

- The per-line lemma is local: its charge depends on the line's zone, the six rays of the points on it and the
  points whose blocks it caps.
- It can be verified for n = 16 and 18 by SAT on the full pseudoline model with a local objective ("line 0 ends
  below 1/3"). That needs no hand proof of each rule.
- Soundness of the charging identity is algebra (Section 1).


## 7. Status of the unit lemma (2026-09-29, afternoon)

**Conservative form is false.**
- The adversarial walks (search/bbl_adversary.py) found mutual 2-chains of X points with both free sides I,
  at n = 10 and 11 (T = 17–20).
- Their conservative slack is −1.
- All their lines still reach 1/3 once every portion is counted.

**Extended form (the one the assembly needs).** For every unit K:

  3·Σ_{P∈K} c_P + Σ_{L∈D(K)} p_L ≥ |D(K)|

where p_L is the number of portions line L receives: own unused segments + touches. Portions are disjoint across
units, so the assembly in §4c is unchanged.

**Evidence for the extended form.**
- 0 violations in 1.33M arrangements and about 750k adversarial states (n = 8–18).
- The minimum extended slack observed is 1 (in thirds).
- **No unit is ever extended-tight.** If that is proved, Λ = 6 forces no units at all, hence a simple arrangement,
  hence Blanc.
- Lattice-like units (6+ bridges) have extended slack ≥ 7.

**Conservative slack by unit size (all data plus adversarial).**

| size | min conservative slack |
|---|---|
| 1 | 0 (single (I,U) X) |
| 2 | −1 ((I,I) chain only) |
| 3–7 | ≥ 1 |
| 8+ | ≥ 3 |

**Point-level discharging (search/bbl_dischargelp.py).**
- An LP over typed edges (mutual pair / bridge / link / shared pure cap) finds 50 rules.
- They put every point of 126k training arrangements within budget.
- On 1.15M held-out classes about 1.9% of points still end over budget, all in lattice patches.
- So typed local rules work for chains but not for lattices, where the balance is global along the patch boundary.

**Proof plan.**
- (a) Units of 1 point: proven by hand from Lemma A.
- (b) Units of ≤ 3–4 points: T14 SAT (search/unit_sat.py), decisive, at n = 10–18.
- (c) Units of any size: CP-SAT over closed sets S of unbounded size at n = 16 and 18, excluding (I,I)
  2-chains in conservative mode. This is the follow-up task. Lattices carry a large margin.
- (d) 4-fold points: to be added, either in SAT with allow_fourfold or by hand. c_P = 8 − D_P − β_P/2; caps
  through bridge far ends are not pure.


## 8. Planarity form of the unit lemma (bridged units)

N_P is the number of rays at P that are neither blocks nor bridges, so N_P + D_P + β_P = 6. Then:

  **conservative slack(K) = Σ_{P∈K} (N_P − 2D_P) + nb + U + Upc − PC.**

This is exact. Per point:
- X: 0;
- O1: +3;
- O0: +6;
- W6 hub: 0;
- W6 rim (1,3): 0;
- (1,5): −2;
- (2,2): −2;
- (2,1): −1;
- C (3,3): −6.

Only bridged points can be negative.

**Bridge graph.** Bridges are segments between consecutive vertices, so they do not cross. The bridge graph is a plane
graph, and its rotation comes from the ray order.

*Data:* every bounded face of every bridge graph is an arrangement triangle (4,800 faces), with κ_f = 0 and no
blocks.

Then, for a bridge component C with outer boundary length deg:
- Σ_{outer corners}(a_c − 3) = 6. This is exact, from Euler.
- Σ_{P∈C}(N_P − 2D_P) = Σ_corners (a_c − 1 − 3D_c) = 2·deg + 6 − 3·B_out.

*Data:* 3·B_out ≤ 2·deg + 6 for every component. Equality holds for W6 (6, 6) and for (12, 10) and (18, 14).

**Local credits at deficit corners.**
- A reflex corner (a = 2) holding a block has its cap cross both bounding bridge rays at their far ends Q0, Q2.
  Hence Q0, X, Q2 are consecutive on the cap: a non-bridge link (+1), and the cap is not pure.
- Proof route for bridged units:
  - a finite corner case analysis (a ≤ 6, N/B pattern, credits), checkable by small SAT;
  - plus the Euler identity;
  - plus a lemma that bounded bridge faces are arrangement triangles (or κ_f ≤ 0 with no blocks).


## 9. Decomposition of the unit lemma (2026-09-29, 13:00)

Conservative slack = Σ over bridge components of val(C) + Σ over unbridged points of (N − 2D + links/2 + U-credits − pure caps).

**(A) Bridge components.**
- Local value: val(C) = Σ_{P∈C}(N_P − 2D_P) + (non-bridge links at C)/2 + U(C) + Upc(C) − PC(C).
- Data: **val(C) ≥ 1 for all 6,461 components**. So no bridge component can occur in a 94.
- Proof route:
  - turning identity Σ(a_c − 3) = 6 on the outer boundary (bounded bridge faces are arrangement triangles in all data);
  - 15 corner types, 2 of them deficit: (2,'B') and (5,'BNNB');
  - nearest-positive discharging along the boundary cycle closes every component with reach ≤ 5 corners.
- Remaining work: prove the window lemmas (local SAT) and the "bounded bridge faces are triangles" lemma.

**(B) Unbridged points.**
- Values:
  - X: links/2 + U + Upc − PC. Isolated (U,U) gives 2; (I,U) gives 0; (Ip, M) gives −1/2; (M,M) gives +1; (M,U) gives +3/2.
  - O1: ≥ 2.
  - O0: 6.
- A mutual X-chain of m points totals m − 3, so only m = 2 is short (−1).
- A mutual partner inside a bridge component has val ≥ 1 to spare.

**(C) (I,I) 2-chain.** Needs the extended form (portions): T14, s = 2.

**(D) 4-fold points.**
- Own share: 3c_P − 4 − PC ≥ 1/2 in the worst case (D=3, β=5, PC=3). In all other cases it is ≥ 2.
- A block adjacent to a bridge ray has its cap through the bridge far end, so that cap is not pure.
- Always positive. Still to add to the corner analysis, which currently assumes 6 rays.

**Tight case (n = 18, Λ = 6).**
- Every piece must be tight.
- Bridge components (≥ 1) and 4-fold points (> 0) are excluded.
- X-chains of length ≥ 4 have slack > 0.
- A length-3 (I,I) chain is conservatively tight; T14 checks its extended slack.
- What remains is single (I,U) X units, hence a = 3, general position, and Theorem H.


## 10. Per-line form and the two-hop Hall lemma (2026-09-29, 15:00)

This replaces the unit lemma, whose units are unbounded, by a statement about one line and its two-hop neighbourhood.
The reference implementation and spec is search/bbl_hall.py.

**Ray split (exact).** Each triple point splits 3c_P = (3/2)(N_P − D_P) over its rays: an N ray carries +3/2, a
block ray −3/2, a bridge ray 0. With portions this gives

  **3Λ − n = Σ_L v_L + waste,  v_L = p_L − 1 + (3/2)(#N rays along L − #B rays along L)**

(search/bbl_line.py). The lattice interior is automatically neutral: bridge rays are 0, and a lattice line gets +3/2
at each end where it leaves the patch. Grouped per line, the zigzag boundaries of §8/§9 are positive (+3 per
reflex/convex pair), because each line carries the N ends of the far boundary to the blocks at the near one.

**Structural facts used by the rules** (proved by the triangle argument of §8):
- Two blocks at a triple point are never adjacent, and an N ray flanks at most one block.
- A block's flankers lie on its cap: F1, X, F2 are consecutive on C.
- The ray of C at a flanker toward X (a gap-end ray) never flanks a block.
- So the gap credit T1 and the flank credit F never compete for the same ray.

**Rules.**
- **T1 (cap gap):** a block whose flankers are both triple takes the gap-end N rays of its cap (3/2 each).
- **F:** an unserved block takes 1 from each N flank ray.
  - For X points this is the uniform split: each line gets c_P = 1.
  - For X-chains, each connector keeps 1 and pays the adjacent pure end cap.
- After T1 + F the only negative lines are:
  - pure caps of I-blocks;
  - axes in mutual structures.

  Their deficit is always covered by spare charge within two hops. search/bbl_s1.py has the fair-share version, which
  gives 0 negative lines on all data.

**Two-hop Hall lemma HL(ε).**
- Setup:
  - Relations between lines: a common triple point; axis ↔ cap; pure cap ↔ lines through the blocked point.
  - N2 = distance ≤ 2.
  - d_L = v_L − ε·[L through a triple point].
- Statement: every set S of negative lines has Σ_S d + Σ_{N2(S), d>0} d ≥ 0.
- By max-flow/min-cut this is equivalent to covering all deficits by transfers within two hops.
- Consequences:
  - HL(0) ⇒ Λ ≥ n/3.
  - HL(ε > 0) and a triple point ⇒ 3Λ − n > 0, so at n = 18 Λ ≥ 9 and T ≤ 93.
  - Simple arrangements are covered by Theorem H.

**Evidence.**
- 0 violations for ε = 0, 1/12, 1/6 on 128,827 arrangements:
  - all phi sets, n = 10–22, T up to 93;
  - adversarial sets (bad.jsonl, lineadv/pilot.jsonl).
- 0 violations at even n in the Hall-targeted annealing walks (search/bbl_lineadv.py HALL:1/6), which reach
  k = 29–32 triple points at n = 16, 18.
- ε = 1 fails (the single (I,U) X unit has total slack 1 over 3 lines). This is the planted test.
- **HL is false for odd n**, already for simple arrangements: BBL's end argument needs n − 2 even. The walks find these
  at n = 11, 13, as expected.
- By comparison, fixed typed LP weights (search/bbl_linelp.py) fit the training data but are broken by the adversary
  within about 150 moves. The principled rules plus two-hop Hall are not broken.

**More evidence (15:00).**
- Held-out: 0 violations of HL(1/6) on all 1,151,216 dpwalkc classes (n = 18). Together with the phi sets that is
  about 1.28M arrangements.
- Points of multiplicity ≥ 4 (search/bbl_hallm.py):
  - the word format now takes `g**` for a 4-fold point;
  - work/t3/mutate.push_through moves a line through a multiple point;
  - the ray split gives a bonus 3(m − 3) to each line through an m-fold point;
  - the exact identity 3Λ − n = Σ v + waste was asserted on every tested arrangement;
  - 0 even-n violations on about 47,000 arrangements with 4-fold points, and in multiplicity-aware annealing walks.

**Verification.**
- T15 (search/hall_sat.py, Sonnet 5.5 worker) encodes v_L, T1, F, the relations and ∃S on T14's UnitModel.
- T16 (search/multi_sat.py) does the same for any multiplicity. It validates against bbl_hallm.py with multiplicities
  up to 11.
- Query: ∃ arrangement ∃ S ∋ line 0 violating HL(1/6), for even n = 10–18.
- UNSAT at n = 18 proves T ≤ 93 for pseudoline arrangements with triple points only. Still open:
  - points of multiplicity ≥ 4: each line through an m-fold point gets a bonus 3(m − 3) in the ray split, but the
    model and rules must be extended;
  - an audit of the encoding.

## 11. SAT verification status and the order-parity obstacle (2026-09-29, 16:00)

**Workers.**
- T14 (search/unit_sat.py) is done: validated, decisive only for small cells (ext s=1 up to n=14).
- T15 (search/hall_sat.py): validated (0 mismatches on 738 arrangements, symtest 256/0, planted 85/85). But free solves
  are too slow: n=8 cubes take 20–46 s, and n=10/11 end UNKNOWN after 1200 s.
- T16 (search/multi_sat.py): validated for multiplicities up to 11. Its n=8 runs take 393–592 s.

**Diagnosis (search/l3_sat.py).** Even the simplest per-line fact is exponential for CDCL. The fact is L3: a clean line
of an even arrangement has a portion (BBL's end argument).

| n | free crossing order | line 0's crossing order fixed |
|---|---|---|
| 10 | 7.6 s | 0.0 s |
| 12 | 72 s | 0.1 s |
| 14 | 626 s | 0.1–0.2 s (also for 6 random orders) |

About 9× per two lines. So the cost is BBL's alternation-parity argument along a path whose order is itself a
variable. Explicit rank/position variables for line 0, with per-segment side variables and alternation clauses, did not
help (48–60 s at n=12). Any per-line or per-unit objective contains this parity reasoning, for the target line and for
every donor line.

**Consequence.** HL(ε) at n=18 cannot be certified by plain SAT on the χ model. Options:
1. **Axis encoding.** Cut the arrangement along line 0 into upper and lower wiring diagrams of pseudo-rays with
   complementary crossing sets. Labelling by crossing order on line 0 is then WLOG, and line 0's parity becomes trivial.
   Donor lines are still arbitrary.
2. **Hybrid proof.** Split the per-line parity arguments into local lemmas (fast SAT) plus a hand induction along the
   line. Needs a hand skeleton for HL: a classification of negative lines (pure I-caps with p = 0; axes with 2 blocks)
   and their donors.
3. **Other.** Direct proof or special-purpose DP along lines (1-D transfer matrices) for the line-global parts.

Strictness at ε = 0 (a lighter alternative to ε > 0):
- (a) Every nonempty set of negative lines has Hall sum ≥ 1. Min 1 on 76,584 even-n arrangements.
- (b) No triple point has all its 1-hop lines at exactly 0. 0 of 105,136.

(a) + (b) ⇒ 3Λ − n > 0 whenever a triple point exists, with far fewer negative lines than ε = 1/6.

## 12. Order-free parity lemmas and the Hall-layer experiments (2026-09-29, 17:45)

**Lemmas (search/parity_lemmas.py).** Let L be a line with no multiple point on it. Then all its vertices are simple
and, by L1, no segment of L is doubly used.
- **P1 (parity).** If no bounded segment of L is unused, then σ_first ⊕ σ_last = (n − 3) ⊕ #{vertices where L caps a
  block} (mod 2). Here σ is the side of the triangle on an end segment.
  - *Proof.* Each segment carries exactly one triangle. At an interior vertex V = L ∩ W:
    - two consecutive triangles on the same side share W's segment from V on that side;
    - so that segment is doubly used, its far end is multiple (L1), and it is a block with cap L;
    - conversely, a block capped at V puts both triangles on its side.
  - So the side flips exactly at interior vertices that L does not cap. An end vertex is never capped: one of the two
    faces there is unbounded. Telescoping over the n − 3 interior vertices gives the formula.
- **P2 (ends).** At a simple end vertex V = L ∩ N, suppose the end segment carries a triangle on side s only. Then
  N's first segment from V on side −s is unused (a touch on L) or unbounded.
  - *Proof.* Its two faces are the side −s face of L's end segment (not a triangle) and the face on L's unbounded ray.
- Encoded order-free: σ_first/σ_last are defined at the end vertices with no positions, and the cap XOR runs over
  labels.
- Soundness check: 448 real arrangements (n = 10–18, with triple points) stay satisfiable with the lemmas.
  Side-literal check: 0 mismatches in 39,486 rays (search/parity_check.py; T14's before() runs against the sweep).

**Effect on L3** (clean line with no portion; UNSAT for even n):

| n | plain | end parity only | P1 + P2 |
|---|---|---|---|
| 10 | 7.6 s | 5.0 s | 2.6 s |
| 12 | 72 s | 22 s | 12 s (7 s via parity_lemmas) |
| 14 | 626 s | 79 s | 22–29 s |
| 16 | — | — | 64 s |
| 18 | ~13 h projected | — | **155 s** |

- The general order-free XOR for all lines (P1g/P2g, with triple-point classes expanded) is sound but **slower**:
  828 s at n = 14, with n = 16 and 18 timing out at 1200 s. Dropped.

**Pure caps with p = 0** (the dominant negative family). From P1, P2 and the definitions, a pure cap C with p_C = 0
(n even):
- both end triangles lie on the same side, and the end lines have no vertices on the other side. If the end triangles
  were on opposite sides, the end lines would have to meet on both sides of C;
- C caps an odd number of blocks;
- every capped block has status **I**. A U-block would give a touch on C. An M-block's partner would be a triple point
  on C;
- every capped block is unserved, since its flankers lie on the pure cap.

**Hall-layer experiments.**
- CP-SAT (frozen copy of T15's model) at n = 8: 110 s at ε = 1/6, 80 s at strict ε = 0. The lemmas do not help at n = 8.
- Pure SAT with flat thermometers (search/hall_pure.py) is sound (planted ε = 1 is SAT and re-checks) but has 3M
  clauses at n = 8 and takes 233 s.
- T16's cube "line 0 simple and capping a block" (the pure-cap family) was UNKNOWN after 3600 s at n = 10. That cube
  is now being tried with the lemmas.
- Pure-cap cube (line 0 simple and capping a block), strict ε = 0, n = 10: UNSAT in 1285 s with free S, and in 117 s
  with S = {line 0}. The lemmas make no difference here.
- Explicit rules (data): the pure cap takes its unit from the best line through each capped I-block's point. This
  leaves 0 donors negative; the remaining negatives are axes. A greedy second rule (the axis takes from the lines
  through its points and the caps of its blocks) gives **0 negative lines on 35,335 even-n arrangements**. Making it
  structural (no value comparisons) is task T18.
- The minimising Hall set is a single line whenever the Hall sum is ≤ 2. Multi-line minimisers have sum ≥ 3.
- The single-donor sufficient condition fails for about 0.6% of negative lines, so full Hall (or explicit rules) is
  needed.
- Tightness query (b) (search/tight_run.py): n = 8 decisive UNSAT (5 cubes, 41–81 s).
- Local queries grow about 5× per two lines. Workers: T17 per-ray value model, T18 explicit rules, T19 decisive cubes
  at n = 10–16.

## 13. Plan: n-independent proof via explicit rules and a line automaton (2026-09-29, 19:00)

**Why SAT alone won't reach n = 18.** Every full-arrangement query grows about 10× per two lines:
- Hall, fixed S, pure-cap cube: 60–117 s at n = 10, and more than 32 min at n = 12;
- the tightness query (b): 40–80 s at n = 8, and more than 10 min at n = 10;
- L3 without lemmas.

The per-ray model (T17) and portfolios give only constant factors. A single CP-SAT worker is faster than 8 on the
loaded machine.

**Structure used by the plan (verified on data).**
- Per-ray net values after T1 and F:
  - N rays end at 0, 1/2 or 3/2;
  - served blocks end at 0 or 3/2;
  - unserved blocks with two N flanks end at +1/2; with one R flank, −1/2; with two R flanks, −3/2.
- Hence v_L ≥ −1 + p_L − ½·#(unserved NR blocks on L) − 3/2·#(unserved RR blocks on L).
- Unconditional structural rule for pure caps: every unserved I-block with a pure cap pays 1/k_C to it, from the axis,
  or from the connector when P's other block is M. No pure cap stays negative, and donors can pay without knowing the
  cap's p.
- Adding a greedy axis rule gives 0 negative lines on 35,335 even-n arrangements. T18 is making this rule structural.

**Proof plan.**
1. Explicit rules with local triggers (T18). A trigger on another line is taken worst-case by the donor.
2. Line automaton (T20):
   - exhaustive vertex types (an over-approximation), with local facts proven by hand;
   - a shortest-path DP gives the minimum final value of any line, for every length;
   - "final ≥ 0 for all lines" for all even n gives Λ ≥ n/3: T ≤ 54 at n = 14, 72 at n = 16, 94 at n = 18.
3. **Strictness at n = 18 by tight-type exclusion.**
   - Λ = 6 forces waste = 0 and final = 0 on every line.
   - The automaton marks the tight vertex types: those lying on some final-0 path of the right length.
   - A triple point's type is one configuration seen by all three of its lines. If no triple-point type can be tight on
     all three lines at once, a 94 has no triple point, and Theorem H excludes simple arrangements.
   - Data warning: value-greedy rules create zero points (93 triple points whose lines all end at 0). The rules must be
     structural for this step.
4. Multiplicities ≥ 4: extend the vertex types (bonus 3(m − 3) per line through an m-fold point).

## 14. Independent audit of the line automaton (A20, 2026-09-29, 23:15)

Tool: search/audit_automaton.py. Logs: work/eng/A20/. The subagent could not write its REPORT.md, so this section is
the record. **Verdict: no soundness bug.**
- **Local facts.** F1–F8 are sound for multiplicity ≤ 3; each proof was re-derived by hand, window formulas included.
  - Load-bearing: F3′ (forced sig) for M2 and F5 (end compatibility) for M1. M1 and M2 are unchanged with F2, F3, F4,
    F6, F7 dropped.
  - g = 0 fixing is sound for objectives whose v2 coefficient is ≥ 0 (all current uses).
  - ub-normalisation at interior triple frames is a coarsening, hence sound.
- **M1** holds for even n ≥ 4. The only failure is the trivial n = 2, where the line has one vertex. It was also
  re-derived by hand from F3 and F5. **M2** holds for all n.
- **Evidence.**
  - Exhaustive n = 2..7 (all 253,108 arrangements at n = 7, 1.8M lines).
  - About 0.15M sampled arrangements at n = 8..14, plus 6 Metropolis runs of 300k steps.
  - An independent exact-rational straight-line oracle up to n = 18 (44k arrangements) agrees with values().
  - 9/9 planted over-restrictions detected.
  - An independent block-centric DP matches all 59,772 windows. Bellman–Ford and potential certificates reproduce
    M1 = 1/0 and M2 = 0 halves. The −∞ cases come with explicit weight −4 cycles.
- **Caveats.** Soundness is relative to bbl_hall.values() as the spec. The window formulas are hand-derived and
  tested, not machine-checked. Multiplicity ≥ 4 is covered separately (T22).
- **Blanc-strength test** ($CLAUDE_JOB_DIR/tmp/blanc_auto.py, T20's automaton with a touches-only objective):
  - a clean line can have 0 *touches* for even n (the witness uses own unused segments instead);
  - its touches + own is ≥ 1.
  So Blanc's lemma (every line touches another line's unused segment) is not a consequence of the local facts. The
  route stays at 1/3 per line plus the n = 18 strictness step. The empirical Λ ≥ n/2 − 1 pattern (all even records up
  to n = 50) would need global arguments.

## 15. Line automaton for any multiplicity (T22, 2026-09-30)

search/line_automaton_m.py imports T20 unchanged. The subagent could not write its REPORT.md, so this section is the
record; logs and data are in work/eng/T22/.
- **Model.**
  - M frames are (bin, bout, hE, hW): 256 frames, valid for all m ≥ 4.
  - m enters only through the bonus 6(m−3) (halves) and the parity of m − 1. Classes m ≥ 6 are dominated by m − 2, so
    m = 4, 5 cover everything.
  - E and W sides are relaxed to be independent (sound).
- **Facts.**
  - F4 fails for m ≥ 4. F4′ (a run of consecutive blocks has length ≤ m − 2) is proven but not needed.
  - F3′ at m-fold points and the gap-ray facts are proven (module docstring).
- **Soundness: 0 failures.**
  - Structured even-n data: 122,680 lines, 39,367 through 4-fold points, 11,416 through 5-fold.
  - Random words with m ≤ 10: 237,934 lines; all 344 frames occur.
  - Triple-only regression: 357,546 lines. The M-side model equals T20 on 563,634 triple windows.
  - 11/11 mutations detected; an independent layered DP agrees.
- **Certified, all n, any multiplicity.**
  - M1 unchanged.
  - **v_L + ½·#RN3 + 3/2·#RR3 ≥ −1**, where RN3 and RR3 count unserved blocks at triple points. Blocks at m-fold points
    need no compensation.
  - Every m-fold vertex adds ≥ 3(m − 4) to v_L. Lines through an m-fold point with m ≥ 5 have
    v_L + comp ≥ 3m − 13.
  - Lines with no triple point have raw v_L ≥ −1.
- **Consequence.** Multiplicity ≥ 4 folds into the triple-point analysis. A rule set that closes the triple-point case
  and is expressible in these windows closes all multiplicities.

## 16. Rule LP obstructions, fact K1*, and SAT-proved local facts (2026-09-30)

**T21 interim (work/eng/T21/INTERIM.md).**
- Block-local rules (roles axis/cap/flank; 115 weights) in an LP whose separation oracle is the automaton DP: infeasible.
- The enriched automaton records the multiplicity of each triangle apex. It is validated on 127,673 arrangements.
- Main cut: the (2,4) "kite" `S[(1,1)(1,1)] | T[(1,1)(1,1) h(1,1)]`, with 2v = −6 per triple point. The lattice 2-cycles
  (zero-value payers) cannot fund it.
- Even with only the 5,421 windows seen in data allowed, the LP is infeasible with that catalogue. So window-level
  realizability is not enough. Either longer-range facts or richer rules are needed.

**Data (2.14M real lines, 127k even-n arrangements).**
- 2v_L ≥ −4 always.
- Unserved RR blocks occur on about 5 lines in total, never two on one line.
- #RN ≤ 4 per line.

So the automaton's unbounded deficits come from over-approximation.

**Fact K1\* (proved).** Setting: a triple point P on L with h[s] = 1. The sector (E s, W s) is a triangle P Y Z,
where Y and Z are the far ends of E s and W s. Its third side lies on a line c. Define
- rf(s) := bout[s] ∧ (Y simple ∨ (next vertex simple ∧ triangle on side s of its outgoing segment)),
- lf(s) := bin[s] ∧ (Z simple ∨ (previous vertex simple ∧ triangle on side s of its incoming segment)).

Then rf(s) ∧ lf(s) is impossible.

*Proof.*
- c avoids P and meets b at Y and a at Z. So it crosses L exactly once, either before Z or after Y.
- Case Y simple, on lines b and f. The ring at Y puts the h-triangle's side on f's other ray, so c = f. Since f
  passes through the next vertex X, c crosses L right of P.
- Case X simple with a triangle above [X, V′]. Then Y is triple, on b, C = W_X and c (F-T2). In the ring at Y, the
  rays of c flank both Y→P and Y→X. So the triangle X V′ Y has its side [Y, V′] on c, and c crosses L at V′.
- The left side is symmetric. Having both forcings would make c cross L twice.

The case where Y and Z are both simple is F-T3; the other three combinations are new. Data: 0 violations in 678k
occurrences of h[s] = 1. K1\* kills the (2,4)-kite cut and the (2,2)-kite cuts.

Consequence: an unserved RR block at P forces:
- X to be a 4-triangle simple vertex;
- the next vertex V′ to be triple, on c ∋ Y, Z and d ∋ Y′, Z′;
- at most one unserved RR block per triple point.

**Restriction principle (proof tool for local facts, all n).**
- Setting: a local pattern w along L, made of consecutive vertices with multiplicities, triangular faces, far-end
  multiplicities and unbounded flags. Let S be its witness lines: L, the lines through its vertices, the sides of its
  triangles, and the lines through its specified far ends.
- In the restriction A|S (drop all lines not in S), the positive part w⁺ survives. Consecutiveness, multiplicities,
  triangle faces, first vertices and unboundedness are all preserved.
- Hence: if w⁺ is unrealizable on K′ pseudolines for every K′ ≤ |S|, w is impossible for every n. Non-triangle and
  N information is dropped, which is sound.
- This turns small SAT queries into facts valid for all n. T23 is building search/automaton_facts.py to generate them
  from the LP cuts and from k-grams never seen in data. K1\* (≤ 8 witness lines) is its regression test.

**New rule family proposed (T1′, per-flanker serve).** Each triple flanker F of a block whose gap-end ray along C toward
X is N gives 3/2 from C to the axis. F and X are consecutive on C for any flanker, because the triangle P X F has its
side [X, F] on C.

**Fact K2 (kite, proved).**
- Setup. Let X be a simple vertex whose 4 faces are all triangles (on L: frame `S[(1,1)(1,1)]`). Then its
  neighbours form a complete quadrilateral with diagonals L and C:
  - P = a∩b and V′ = c∩d on L;
  - Y = b∩C and Y′ = a∩C on C.

  All four are triple.
- Kite sides and their outer triangles: [P,Y] ↔ h+(P), [Y,V′] ↔ h+(V′), [V′,Y′] ↔ h−(V′), [Y′,P] ↔ h−(P).
- Claim: the outer triangles of two opposite sides cannot both exist.
- Proof. The ring at Y puts the third side of the outer triangle on [P,Y] on c, with corner a∩c above L. The ring at
  Y′ puts the third side of the outer triangle on [V′,Y′] on a, with corner a∩c below L. Two lines meet only once.
- Frame form: at `S[(1,1)(1,1)]` between two triple frames, forbid prev.h[±] ∧ next.h[∓].

**Kite budget under K2** (per-ray nets after T1+F):

| bridge sides | kite total |
|---|---|
| 0 | +6 |
| 1 | +3 |
| 2 (adjacent) | 0 |

In the 2-bridge case the split is L −1, C −1, c +1, d +1.

**Kite rule KR.** Each N kite side gives 1/2 from its line to L and 1/2 to C. Visibility:
- L and C see all four side statuses in their window at X.
- The side's line sees 3 of the 4 triangles, so it pays in the worst case. That is affordable: without the 4th triangle
  both of its blocks are served, and it pays no F.

**T21 status (2026-09-30).** Exact rule certificates (denominator 12, DP minimum 2·final + 2 = 2 on all paths and
cycles) exist for two classes:
- bridge-free (rings NNNNNN, BNNNNN, BNNBNN; 16 rules);
- NB0 (no bridge ray adjacent to a block ray; 10 ring types).

Hence **Λ ≥ n/3 for these classes**. Files: work/eng/T21/rules_rfree.json, rules_nb0_.json, search/rule_ref.py.
- Full class with K1\* + K2: still infeasible (139 cuts). The core is zero-value lattice T–T cycles, whose flank line
  pays at every vertex, plus two small deficit lines.
- Bounded length (n − 1 ≤ 17) does not help.

**Fact K2g (from K2; forces the hidden gap-end bit).**
- Setting: a triple point A on L with bin[s] = bout[s] = h[s] = 1. Suppose E s is a block toward a simple Q, the far
  end R of W s is triple, and the next vertex B is triple with h[s](B) = 1 and bout[s](B) = 1.
- Claim: the block is served.
- Proof. Q has three triangles: ABQ, AQR and BQS. A 4th would make Q a kite whose opposite sides [B,S] and [R,A]
  both have outer triangles, which K2 forbids. So the gap-end ray [R,Q] is N.
- The mirror statement holds on the W side.
- This is the lattice 2-cycle with alternating apexes (T21's cut 1). Its blocks are served, so its flank line owes
  nothing. Data: 12 occurrences, 0 violations.

**Fact K3 (runs, proved; generalizes K1\*).**
- An s-link joins consecutive triple vertices T_i, T_{i+1} such that:
  - the triangle on side s of [T_i, T_{i+1}] has a triple apex A;
  - h[s] = 1 at both T_i and T_{i+1}.
- Shared third side. The ring at A puts the third sides of both h-triangles on A's third line f. So a maximal run of
  s-links shares one third-side line f, and f crosses L outside the run.
- Consequence: lf(s) anywhere in the run and rf(s) anywhere in the run are incompatible.
- Automaton form: one flag bit per side, carried along links.
- Data: 0 violations in about 660k runs, about 10k of them of length 2–8.
- K3 kills T21's deficit line cut 109 (n = 8). There the h-triangle at T3 would need a line through the two triple
  points W4∩W5∩a3 and W1∩a2∩b3, which share no line.

**Kite rule is required explicitly.**
- T21's core after K2g contains the kite deficits (cuts 11 and 66: two kites per period, each in the K2 case with two
  adjacent bridge sides, L and C at −1 each).
- Its rule families had no key that moves the surplus of the kite's N sides to L and C, so KR was added as an explicit
  family.

## 17. T21 final: class certificates (2026-09-30)

The subagent could not write REPORT.md, so this section is the record. Commands and status are in
work/eng/T21/certificates.json; code in search/rule_lp.py (rule family `SigCatalogue`) and search/rule_ref.py.

**Theorem (automaton-certified, all even n).** Take a pseudoline arrangement with simple and triple points only, all of
whose triple points have ring types in one of the classes below. Then every line ends with final ≥ 0 after the listed
rules, so Λ ≥ n/3. In particular T ≤ 54 at n = 14, T ≤ 72 at n = 16 and T ≤ 94 at n = 18.

| class | ring types | rules | facts needed |
|---|---|---|---|
| bridge-free | NNNNNN, BNNNNN, BNNBNN | 15, denominator 12 | none |
| NB0 (no bridge next to a block) | 10 types | 18, denominator 12 | none |
| C2 | NB0 + BNNNNR, BNNNRR, BRNNNR, BNNRRR, BRNNRR (15 types) | 46, denominator 6 | K1\*, K2 |

- **Checks.** The DP minimum of D·(2·final + 2) equals 2D exactly. Three independent verifications (exact
  Bellman–Ford, a layered DP to length 90, an SCC negative-cycle check). Every single-weight decrement is detected.
- **Data.**
  - 0 negative lines on 126k in-class phi/adv arrangements (99% of that corpus) and 266k in-class n = 18 dpwalkc
    arrangements.
  - Outside C2: 737 of 1,349 phi arrangements and 392 of 492 dpwalkc arrangements still have negative lines under these
    rules.
- **Rule family `SigCatalogue`.**
  - Payer and receiver are each one of the block's roles: axis, cap, or one of the two flank lines.
  - A rule cell is the full block signature.
  - What a role cannot see becomes a hidden variable of its own window, minimised adversarially.

**Remaining ring types:**
- c_P ≥ 0: BNNNBR, BNNBRR, BNNRBR;
- lattice defects with c_P < 0: BRRRRR, BRBRRR, BRRBRR, BRBRBR.

Full class with F4′, K1\*, K2, K2g and K3: infeasible, 239 cuts. The minimal core has 10 cuts (core_k123_full.txt):
- lattice payer cycles of BRRRRR/BRRBRR points;
- short deficit paths.

The c_P ≥ 0 union is infeasible too, with a 10-cut core on BNNBRR, BNNRBR and BNNRRR (core_k123_cge0.txt).

**Realizability (T23, pattern SAT, work/eng/T23/patsat.py).**
- K1 and K2 are UNSAT with 8 lines in 0.3 s. On 300 data k-grams: 298 SAT, 2 timeouts, 0 UNSAT.
- Unrealizable (exact whole-line SAT): cut 109 (n = 8, killed by K3) and cut 147 (n = 12). Cut 232 is also UNSAT.
- **Realizable:** cut 32 of the c ≥ 0 core, an n = 10 line with v_L = −3 (the data minimum is −2, so this is a large-n
  effect missing from the corpus). Witness `3 2 1 3* 2 1 0 5 4 3 7 6 5 4 3 1* 3 7* 5* 4 2* 0* 5 6* 5 4 2* 8 7`.
  - Line 0 passes through two (2,2) points of type BNNBRR, both of whose end segments are I-blocks.
  - Every other line has v ≥ 3. The third side of the h-triangles at both points (line 9) has v = 6.
  - So this family needs genuine payments. Even with T1′, T1″ and full N-flank residuals, line 0 stays at −1.
- Cuts 93 and 217 are also realizable, with v = 0 in their witnesses.

**Zero points under the C2 weights (n = 18 data, for the strict step).**
- Sample: about 14,100 in-class 93-arrangements, about 20,700 triple points. Every line ends with final ≥ 0.
- 46% of the lines through triple points end at exactly 0.
- About 29 zero points occur, i.e. triple points whose three lines all end at 0. They lie in about 17 arrangements.
  There are none at T = 92.
- Every zero point has type BNNRRR (c = ½) or RRRRRR (lattice interior, c = 0), and all are linked to other triple
  points. Isolated X points are never zero points.

Consequences:
- An ε-margin per line through a triple point is far off with these weights.
- A purely local exclusion of tight points fails, since real 93s contain zero points.
- The strict step therefore needs either re-optimised weights, or a global argument for tight lattice-type clusters
  (compare §9A: every bridge component has val ≥ 1 in data).

**Strict step plan: the extreme-point credit LP.**
- Sweep geometry. In a wiring diagram, let P be the leftmost point of a bridge component (minimum event id). All
  bridges at P point right, so its three left rays, which are consecutive in the ring, are non-bridge.
  Likewise for the rightmost point.
- Joint LP. Find rule weights w and credits τ(config, role) ≥ 0 such that:
  - every "extreme-type" configuration (three consecutive non-bridge rays) has Σ over its three lines of τ ≥ 1;
  - every line satisfies final_L ≥ ε·Σ_{P∈L} τ(P, L), with ε fixed, say 1/100.

  Both conditions are linear, and the automaton DP remains the separation oracle.
- Why it works. In a 94, every final is 0, so every τ on a line through an extreme point is 0, which contradicts
  Σ τ ≥ 1. Hence a 94 has no triple point, and Theorem H excludes simple arrangements.
- Data check (C2 weights, n = 18, T ≥ 92, in class):
  - singleton components (about 28k): at least one line is always > 0;
  - multi-point components (565): exactly one 7-point component has all three lines at 0 at both of its extreme
    points (ring type BNNRRR).

  So the weights must be re-optimised jointly with τ; C2's weights alone do not suffice.

## 18. Exact n = 18 loop (T25) and real deficits (2026-09-30)

**T23 facts.** search/automaton_facts.py holds 9 SAT-proved facts, P000–P008. They include K1\*, K2, F4′, and a
4-slot K3; the rest are simple-apex variants. Validation: 0 violations on 2.32M real lines.
- Sweeps: 2,899 unseen 2-gram patterns (789 UNSAT) and 1,195 cut windows (84 UNSAT). All reduce to the 9 facts.
- They kill only 1–3 cuts per LP core, so the remaining obstruction is payment, not local realizability.

**Deficit census.**
- Real lines with v ≤ −2 (after T1 + F): 28 at n = 8 (minimum −3) and 321 at n = 10.
- The dominant local type is a (2,2) point BNNBRR/BRRBNN, with L's two blocks pointing at a mutual pair.
- With T1″ a line with one such point sits at −½ in the rf case. Otherwise the point gives L +2.
- F′ (F takes all 3/2) is not a fixed option: about 38% of lines whose triple-point rays are all N have p = 0 and need
  the ½ residual.

**T25 (search/rule_lp_t25.py; flags --t1pp, --exactw 17).**
- The exact-weight-17 LP (n = 18 lines only) with all facts is infeasible, with or without T1″: 508 cuts, and 183 of
  them are negative at w = 0.
- Exact whole-line SAT at K = 18 (about 7 s each): 137 of 179 are real. Real 18-line arrangements have lines as low as
  v_L = −7/2 (after T1 + F + T1″). Stored in work/eng/T25/real_deficits.jsonl.
- An LP over the exact rows of 113 of these real arrangements (all 18 lines each) is **feasible** with 22 SigCatalogue
  rules. So real deficits are payable. The relaxed infeasibility comes from unrealizable words and loose hidden
  completions.
- Next: a CEGAR loop.
  - Real violated paths add all rows of their witness arrangement.
  - UNSAT paths give positive cores (window filters, or lead-generalised facts).
  - Frames-SAT but hidden-UNSAT cases give hidden-domain facts.

**Hand proofs of T23's SAT facts P000–P009** (search/automaton_facts.py).

The facts' proofs no longer depend on the patsat encoding.

Notation. At a triple point P, the lines are L, b (rays E+ and W−) and a (rays W+ and E−). "Apex simple" means that
the third corner of the triangle over a segment of L is a simple vertex.

- **P000** (T[h−] T[h+], [A,B] doubly used, both apexes simple).
  - The apexes are Q = b_A∩a_B above L and Q′ = a_A∩b_B below L.
  - The ring at the simple point Q puts the third side of h+(B) on b_A. So b_A meets b_B above L.
  - The ring at Q′ puts the third side of h−(A) on b_B. So b_A meets b_B again below L. Contradiction.
- **P001** (S T[h−], [X,P] doubly used, bottom apex simple).
  - The bottom apex is Z′ = b∩C (C is X's other line), and the ring at Z′ puts the third side of h−(P) on C. So C
    meets a below L.
  - The top triangle over [X,P] has its apex on C and on a, above L. Contradiction.
- **P002** is F-T3 (two adjacent blocks W−, E−).
- **P003** (T[h−] T[h(1,1)] T[h+], two doubly used segments, top apex of [A,B] and bottom apex of [B,C] simple).
  - The simple apexes force b_A∩b_B = S above L and b_B∩b_C = R below L.
  - R is also the bottom apex of [A,B], so R = a_A∩b_B∩b_C. The ring at R puts the third side of h−(A) on b_C, so b_A
    meets b_C below L.
  - Symmetrically, S = b_A∩b_B∩a_C, and the ring at S puts the third side of h+(C) on b_A, so b_A meets b_C above L.
    Contradiction.
- **P004** is K2.
- **P005** and **P008** follow from K3 if the middle apex is triple, and from K1\*/F-T3 if it is simple.
- **P006** and **P009** are K1\*.
- **P007** is F4′.

## 19. Revised plan (2026-09-30): margin, F5*, one strict LP

**Diagnosis.**
- The ⅓-per-line accounting gives Λ ≥ n/3 = 6 at n = 18, which is exactly the 94 bound. With zero margin, a
  separate and delicate strict step is needed.
- The per-line LP must also hold for arbitrarily poor arrangements, where real lines go down to −7/2.
- The empirical truth, Λ ≈ n/2 − 1, and Theorem H's ½ per line both come from Blanc's L3 (every clean line has a
  touch). Our automaton could not derive L3 locally.

**Fact F5\* (proved, 2 bits of state along L).**
- Statement: two different vertices of L cannot carry unbounded-ray flags on opposite sides.
- Proof: this is Blanc's step 5. If R_i has no crossing on side −s and R_j none on side s, they must meet on L, which
  is impossible for different vertices. At a single triple point both flags can occur, since its two lines meet there.
- F5 was the special case of the two end vertices only.
- Data: 0 violations on 1.07M lines (work/eng/f5star_check.py).
- **With F5\*, the automaton proves L3.** Clean lines at even n have at least 1 touch; at odd n the minimum is 0, as
  expected. Before, the minimum was 0 at even n too.

**Plan.**
1. Add F5\* to the LP automata. It is global along L, so it also tightens non-clean lines, whose stretch and parity
   arguments now see one-sidedness.
2. Portion split a as an LP variable. Each unused segment gives a to its owner and (1 − a)/2 to each touched line,
   with a ∈ [0, ⅓]. With a = 0, clean lines get at least ½ through L3. This is the master-inequality accounting,
   with a margin of ⅙ per clean line.
3. Triangle-count direction α′. The quantity 3s_L − 1 − v_L, with s_L = n − 2 − tri_L, sums to the waste, which is
   ≥ 0. So adding α′·(3s − 1 − v) to every line is valid for any α′ ≤ 1. This gives a free LP column.
4. **One strict LP at n = 18.** Require every line to end with final ≥ 3ε, i.e. q ≥ ⅓ + ε. Feasibility gives
   Λ > 6, hence T ≤ 93, with no separate strict step. If it fails only on tight non-clean lines, use the τ-credits of
   §17 instead of a uniform ε.
5. Keep the CEGAR loop and the exact cell domains for the payer looseness.
6. Fallback: for residual ring types, a SAT search for tight structures at n = 18.

**Status and consequences (2026-09-30, 02:40).**
- The uniform strict target (every line ≥ ⅓ + ε) is infeasible on the real 93 rows (3,168 arrangements).
  - Targeted τ-credits, even keyed on full point configurations, also give ε = 0.
  - Blocking set: 11 real lines in 7 arrangements (a pure cap and a flank line at an X point; BNNRRR/BNNBRR bridge
    lines).
  - The sums are not the obstruction (each 93 has Σ ≥ 7.5); the slack is unroutable in SigCatalogue.
- **Clean-line bound.** Fix the portion split at a = 0. If the certificate holds (all lines ≥ ⅓), L3 gives every
  clean line ≥ ½. Hence **Λ ≥ 6 + c/6**, where c is the number of clean lines. So any n = 18 arrangement with a clean
  line has Λ > 6, i.e. T ≤ 93. Only arrangements in which every line meets a triple point or caps a block need a
  separate strict argument. (T25 is running the C2 certificate at a = 0.)
- Full class:
  - each of the 7 non-C2 ring types alone makes the exact-17 LP infeasible;
  - CEGAR stalled with a DP minimum of −8 to −14, and after projecting away the I-flag u its violators are real
    18-line arrangements;
  - next: a batch real-row LP on the whole n = 18 corpus, which decides whether SigCatalogue hits a wall on real data.
- Disproved by data: "every non-C2 arrangement has a triangle face with three triple vertices" (BNNRBR-type points,
  for example, can avoid one).

**Partial theorem (2026-09-30, T25).**
- **Certificate.** C2 at exact weight 17 is feasible with the portion split fixed at a = 0 (with F5\*, cell domains
  and α′ = ¼). It is exact: D = 8, DP minimum 16 = 2D, 64 rules (work/eng/T25/rules_C2_a0.json).
- **Consequence.** Every n = 18 pseudoline arrangement with simple and triple points only, all of C2 ring types, and
  **at least one clean line**, has Λ ≥ 6 + c/6 > 6, hence T ≤ 93.
- Caveats: multiplicity ≥ 4 is not included, and the LP code is unaudited.
- **Remaining for C2.** Arrangements in which every line meets a triple point or caps a block. These are about 7% of
  the real n = 18 93s, so the case is not rare.

**Batch real-row LP.**
- All 345k triple-point n = 18 arrangements of the corpus (dpwalkc run1, work/phi) plus 521 SAT-generated deficit
  arrangements reduce to only 8,586 distinct rows. That LP is feasible in SigCatalogue (full class, ε = 0).
- So the catalogue has no wall on real data. The DP at those weights finds violators down to −8.3; most are real lines
  outside the corpus (poor arrangements). CEGAR continues from these rows.

**Remark.** Adding "T ≥ 94" to the primal gives a column d·(tri − 47/3) + δ. This is the same as the α′ direction
plus a uniform ε, which is already shown infeasible on real rows. Nothing new.

**Strict step: the no-clean split (2026-09-30, 03:10).**
- Case (i), at least one clean line: the a = 0 certificate plus L3 gives Λ ≥ 6 + c/6 > 6.
- Case (ii), no clean line: clean paths cannot occur. Delete them from the automaton and require every remaining line
  to end with final ≥ 3ε, using separate weights.
- Necessary test on real rows (T ≥ 93, n = 18, no clean line; script work/eng/T25/nc_eps_lead.py):
  - C2: 106 distinct rows, max ε = 1/15;
  - full class: 254 rows, max ε ≈ 0.027.
- T25 is running the automaton version (C2 first).
- Consequence if feasible: C2 needs both cases, and both would then be settled, giving T ≤ 93 at n = 18 for the whole
  C2 class. Note that the "no clean line" arrangements are about 7% of the real 93s.

**NC strict core and the X-axis lemma (2026-09-30, 03:40).**
- The NC C2 uniform-strict LP is infeasible with a tiny core, all of one family: a pure cap zigzag with p = 0 and
  v = −1 caps the I-block of an isolated X point, whose lines' paths are tight.
- Every core path is realizable, and the real rows give a large ε. So this is payer/receiver decoupling.
- **X-axis lemma (automaton-proved with F5\*).** A line whose only multiple points are X-axis points, and which caps
  nothing, has ≥ 2 portions at even n. Without F5\* the automaton bound is 1.
- Data: isolated X axes with an I-block always have p ∈ {2, 3} (20k cases); without an I-block, p ≥ 3.
- So the axis can pay the pure cap, provided own portions are valued (a > 0; in the NC case there are no clean lines
  to protect). Scripts: work/eng/xaxis_dp.py, work/eng/f5star_check.py.

**Routing wall and exact-coupling rule families (2026-09-30, 04:40).**
- T25 plugged in all facts (P000–P009, K4 = P000). Adding any single non-C2 type to C2 is still infeasible. The minimal
  cores have 11 (BNNNBR) to 61 (BNNBRR) cuts.
- The core paths are real 18-line lines (exact SAT with the DP's own sig choice). So the obstruction is routing: e.g.
  the cell (RXXXR, pR = 1, tL = tR = 1) is paid by T-chain lines and received by S-T-S caps, with opposite signs.
- NC C2 strict with a = ⅓: the X-point core disappears, but the next core is BNNRRR chains, again decoupling.
- Fix under test, adding routes without adding looseness:
  - **SV cells**: at a simple vertex, keyed on its 4 face bits, which both lines see;
  - **TRI cells**: at a triangle, keyed on its 3 vertex multiplicities, which all three side lines see through the
    enriched apex flags.

## 20. KEY RESULT: full-class certificate at n = 18 (T25, 2026-09-30, 05:00)

**Certificate.**
- Command: `search/rule_lp_t25.py lp --class full --split --alpha --celldom --wr --sv --tri --pt --eps 0`
- Defaults: F4′, K1\*, K2, K2g, K3, T1″, F5\*, exact weight 17.
- Exact: denominator D = 16, layered-DP minimum of D(2·final + 2) = 32 = 2D.
- Parameters: a = 0, α′ = ½. Rules: work/eng/T25/rules_FC_full.json (60 block cells plus 7 SV/TRI/PT rules).
- **Theorem (computer-assisted).** Every pseudoline arrangement of 18 lines with points of multiplicity ≤ 3 has every
  line at final ≥ 0. Hence Λ ≥ 6, i.e. **T ≤ 94**.
- **With a clean line.** Since a = 0, L3 gives every clean line a *base* value ≥ ½. The SV/TRI rules can make clean
  lines pay, so the bound needs δ := the minimum final over clean paths to be > 0. Then Λ ≥ 6 + cδ/3 > 6 and every
  such arrangement with a clean line has **T ≤ 93**. (δ is being checked by T25.)

**The decisive ingredient.** The exact-coupling families, whose cells are fully visible to every party:
- SV cells at simple vertices (4 face bits);
- TRI cells per triangle side (vertex multiplicities);
- PT cells at triple points (6 sector bits).

With facts P000–P009 but without these families the LP is infeasible; with them and without those facts it is
feasible. (An earlier "infeasible" result for single additions came from the ring,oth key projection, which merged
X-point cells with others.)

**Remaining for K(18) = 93.**
1. Arrangements with no clean line (the strict step). Next: the NC strict LP with the new families.
2. Points of multiplicity ≥ 4 (T22 automaton extension, or a separate counting argument).
3. Validation and audit. T25 is running a planted test, the full corpus with exact weights, and an independent DP.

**Validation of FC (T25, work/eng/T25/full_check.py, planted_test.py).**
- Exact weights on all 345,073 triple-point n = 18 arrangements of the corpus (6,211,314 lines): minimum final 0,
  zero negative lines.
- Every rule column is conserved in every arrangement, and Σ_L final ≤ 3Λ − n holds everywhere.
- Planted test: 68/68 single-weight decrements (−1/D) are detected. A second DP implementation gives the same per-n
  minima.
- δ (minimum final over clean paths) = 0 at the FC weights. The zigzag clean line pays SV/TRI rules.
- Next:
  - re-solve with clean paths ≥ δ > 0 (runs FD: δ = 1/6; FD24: δ = 1/24);
  - the no-clean strict runs (ε = 1/60, 1/120, 1/240).

**FD24: the clean-line half of the strict step is DONE (T25, 2026-09-30).**
- Certificate: full class, exact weight 17, final ≥ 0 on every path **and final ≥ 1/24 on every clean path**.
- Exact: D = 144, main DP minimum 288 = 2D, clean-only DP minimum 300 (so the minimum clean final is 1/24).
- Rules: work/eng/T25/rules_FD24_full.json (123 block rules + 8 SV/TRI/PT rules, α′ = 11/24, a = 0).
- Command: `rule_lp_t25.py lp --class full --split --alpha --celldom --wr --sv --tri --pt --eps 0 --cleandelta 1/24`.
- **Theorem (computer-assisted).** Every 18-line pseudoline arrangement with points of multiplicity ≤ 3 and at least
  one clean line has 3Λ − 18 ≥ 1/24. Hence Λ ≥ 9 and **T ≤ 93**.

**Remaining for K(18) = 93:**
- (a) Arrangements with no clean line (NC strict LP running; ε = 1/240 is at DP minimum −0.04).
- (b) Multiplicity ≥ 4.
- (c) Audit.

Simple arrangements are covered by Theorem H, and also by (a)'s complement, since there every line is clean.

**NC strict status (T25 note 13).**
- Uniform ε with the portion split free: infeasible already on C2. The core is the isolated X-point cluster: a pure-cap
  zigzag at v = −1 plus two X-point line paths with base v = 0, where the SV/TRI/PT routes cancel exactly. All four
  paths are real.
- The axis path's value at a = 0 hides its ≥ 2 own unused segments (X-axis lemma). Since the NC case has no clean
  lines, a = ⅓ is free there. Next test: NC with SV/TRI/PT and a fixed at ⅓.
- FD24 full-corpus check: 6.2M lines, zero negative, all columns conserved.
- T25 has started the multiplicity ≥ 4 extension (M frames, apex class ≥ 4, facts guarded to exactly-triple
  neighbours).

**NC strict: switch to targeted credits (2026-09-30).**
- Uniform ε fails even at a = ⅓. The zero-slack combination is pure caps (v = −1), tight flank lines, and a rich line
  (v = 6.5) through six X points that pays six caps. Uniform ε would force every one of them strict.
- A strict step only needs one positive line per extreme point.
- Necessary test with extreme-point τ-credits (fine keys) on no-clean real 93s (script
  work/eng/T25/nc_rows_tau_lead.py plus real_tau_lp.py):
  - C2: max ε = 0.176;
  - full: max ε = 0.128;

  for a = 0 and a = ⅓ alike (uniform ε gave 0.067 and 0.027).
- T25 is running the automaton version: NC, all families, τ-credits.
- Validity: an NC arrangement has a triple point, hence a bridge component, hence an extreme point.

**NC strict, attempt 3: credit on lines through ≥ 2 triple points.**
- τ-credits at point configurations fail in the automaton, because the credit column cannot tell a rich line from a
  tight X-axis line in the same configuration.
- New key: the path-level feature k_L ≥ 2, a DP counter. Validity: an NC arrangement in general position is excluded by
  Theorem H; otherwise some line has k ≥ 2.
- Real test (NC 93s, all non-GP; work/eng/T25/nc_k2_lead.py): max ε = 0.159 (C2) and 0.109 (full). The variant
  crediting k_L − 1 gives 0.064 and 0.045.
- T25 found that only K3 is needed among the facts for the ε = 0 certificate. F4′, K1\*, K2, K2g, F5\* and P000–P009
  are each removable. This simplifies the multiplicity extension.
- Previously refereed (old route): no 94 with k ≤ 5 triple points, in GP, or with k = 6 and β = 0.

**NC strict: per-line credits exhausted; switch to tight structure (2026-09-30).**

Three per-line strict formulations fail in the automaton, each on a zero-slack cluster of real paths:

| credit | blocking cluster |
|---|---|
| uniform ε | X-point cluster |
| τ at extreme-point configurations | X-point cluster (rich vs. tight lines share a column) |
| lines with k ≥ 2 | bridge-pair lines (two consecutive BNNRRR points) |

Real rows allow ε ≈ 0.1–0.18 each time. The per-line relaxation cannot route the strictness.

**New approach.**
- In a 94, Σ final = 0, so every line is exactly tight under FD24, under FC, and under every ε = 0 certificate.
- The tight lines form a regular language, the tight edges of the DP.
- Plan: intersect the tight window sets of several certificates. A 94 must consist entirely of always-tight lines.
  If that set is small, exclude it by counting or by a targeted SAT search. T25 is running the census.

## 21. Structure of a hypothetical 94 (multiplicity ≤ 3), from joint tightness (T25 note 18)

In a 94, every line is exactly tight (final = 0) under every ε = 0 certificate. Take the five exact certificates
FD24, FC, FS1, FS2, FS3; each line must be tight under all of them. Consequences:
- **Z = 0.** On jointly tight paths, the number of own unused segments is exactly 0 and so is the number of touches.
  So a 94 has no unused bounded segment. Hence 3T = S + D with S = 288 − 3t, so **D = 3t − 6** and **Σ_P c_P = 6**.
- **No clean lines** (FD24), and all k_L ∈ {0, …, 8} occur on jointly tight paths.
- **Only 13 jointly tight point types**, i.e. each of the three lines has a tight window.

  | type | ring | c_P |
  |---|---|---|
  | X | NNBNNB | 1 (two variants) |
  | | RNNBNN | 3/2 |
  | | RRRRNN | 1 |
  | | RRRNNB | ½ (two variants) |
  | | RRBNNB | 0 (two variants) |
  | | NNRBRB | 0 |
  | | RRRRRR | 0 |
  | | BRRRRR | −½ |
  | | RRRBRB | −1 |
  | | RBRBRB | −3/2 |

- Types with a run of three consecutive non-bridge rays, i.e. those that can be the extreme point of a bridge
  component: RRRNNB, RRBNNB, X, RNNBNN, NNRBRB.
- Old refereed results still apply: k ≥ 6 triple points, not in general position, and β > 0 if k = 6.

**Next.** Compute the exact always-tight window set. For each window, ask whether some certificate makes it strict,
i.e. keeps every path through it at final ≥ δ. If no triple-point window survives, a 94 has no triple point, and
Theorem H applies. If only types without a non-bridge 3-run survive, no bridge component has an extreme point, which
is again a contradiction.

**Always-tight set, first pass (T25 note 19; work/eng/T25/group_results.txt).**
- Method: for each (point configuration, role) group of intersection-tight T windows, one LP asks for final ≥ 1/1000
  on every path through the group (a DP flag), final ≥ 0 elsewhere, FC columns. Feasible means that point type cannot
  occur in a 94: under that certificate its line is strict, contradicting Σ final = 0.
- **9 of the 13 jointly tight types are excluded.**
- Survivors:
  - NNNNNN/111111 (ring RRRRRR, c = 0);
  - NNNSSS/111011 (ring RRRNNB, c = ½);
  - two X variants NSSNSS/011011 and NSSSSS/011011 (c = 1).
- The strictness margins have so far been checked in floating point only; exact verification is pending.

**Endgame.**
- A component made only of RRRRRR points has no extreme point, so it is impossible.
- If RRRNNB is excluded (per-window tests running), every triple point is an isolated X point. Then Σ c_P = 6 gives
  k = 6 with β = 0, which is excluded by the old refereed result; general position is Theorem H.
- Otherwise, the turning identity gives each component at least 6 RRRNNB corners (Σ c ≥ 3 per component), leaving a
  short list of structures.

**Single-window tests (T25, 153 LPs, work/eng/T25/single_results.txt).** No role of the four surviving types is fully
excluded:
- RRRNNB: r0 28/52 windows strictable, r1 0/16, r2 24/40;
- X variants: 16/24 on one role, 0 on the others;
- RRRRRR: 0/7.

**Decisive next LP (restricted to P5).**
- A certificate excluding a 94 only needs validity on the lines that can occur in a 94: P5, the paths tight under all
  five certificates, which is the common-tight subgraph (3,574 edges, 161 terminals).
- LP: final ≥ 0 on P5 and final ≥ δ on P5 paths with a triple point. Feasible means a 94 has no triple point, and
  Theorem H applies.
- Otherwise iterate: new certificates shrink P5, then retest.

**Restricted strict LP over P5: infeasible** (cores of 5–8 jointly tight, real paths). The per-line method is
exhausted; the remaining step is 2-D.

**Flower reduction (lead, 2026-09-30).** In a 94 (multiplicity ≤ 3), the bridge components use only RRRRRR (all 6
sectors triangles) and RRRNNB (sectors 111011) points; X points have no bridges.
- Let R(K) be the union of the triangles between consecutive bridges at the points of a component K.
  - RRRRRR has 6 such sectors, so it is an interior vertex (t = 6).
  - RRRNNB has exactly 2 adjacent ones, so it is a boundary vertex with t = 2 (no pinches).
- Gauss–Bonnet for triangulated surfaces: Σ_int (6 − t) + Σ_bdry (3 − t) = 6χ. Every boundary term is +1 and
  every interior term is 0, so χ = 1 (a disk) and **exactly 6 boundary RRRNNB points**.
- Counting for a disk triangulation with 6 degree-3 boundary vertices and I interior degree-6 vertices: the interior
  subgraph has 3I − 3 edges, and planarity (≤ 3I − 6 for I ≥ 3, or ≤ C(I, 2)) forces I = 1.
- So every bridge component is a **flower**: a centre O of type RRRRRR and six RRRNNB corners P_i, using 9 lines
  (3 through O, 6 hexagon-edge lines ℓ_i ∋ P_i, P_{i+1}). Its Σ c = 3.
- With Σ c_P = 6: either **6 X points** (closed: C16/C26/C29), **1 flower + 3 X points**, or **2 flowers**.
- Data: no real arrangement (about 8,200 components) has a component made only of these two types.
- The tight set contains only chiral centre windows: opposite corners on each line through O have their outer single
  triangle on opposite sides.
- Next: a finite consistency problem. Choose jointly tight windows for all 21 line–vertex incidences of a flower,
  consistent along lines and at shared points, each extendable to a full P5 path. If this is infeasible, flowers are
  impossible and multiplicity ≤ 3 is closed.

**Multiplicity ≥ 4 (T27, search/rule_lp_t25m.py).**
- Sanity check without the ≥ 4-fold apex class (`--nomult --noapex3`): reproduces FC exactly (D = 16).
- With apex class 3, i.e. triangle apexes that are ≥ 4-fold, the LP was infeasible. The witnesses were pure caps whose
  block has a ≥ 4-fold apex, with no rules available there.
- Fix: TRI cells with three vertex classes S/T/M. Triangles with two or more M vertices carry no transfer.
- With the fix, `--nomult` including apex class 3 is feasible: exact, D = 32 (work/eng/T27/rules_S3.json).
- Running now: the full multiplicity graph with M4/M5 frames, then the FD24 target and a conservation check on T22
  data.

**Flower check (T25).** At the window level it is satisfiable: 8 solutions, with the chirality free per antipodal pair
of corners. Next: cross-line consistency at the six star tips Y_i = ℓ_{i−1} ∩ ℓ_{i+1}. By Lemma A with Z = 0, each
corner's block at a tip is either mutual with the adjacent corner (opposite chirality) or its axis ends there.

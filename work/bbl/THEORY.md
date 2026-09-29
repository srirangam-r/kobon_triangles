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

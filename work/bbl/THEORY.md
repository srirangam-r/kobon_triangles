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

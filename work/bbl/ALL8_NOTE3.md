# ALL8_NOTE3 — quadruple end payments and the remaining global surplus

## Status

**Partial result. Inequality (7′) of `SOL_TASK3.md` is still unproved. No counterexample to it is given here.**

There are new proved payments and a new exact line-end/path identity. They remove the lead's bad-`I_4` category. They do not yet give the required constant surplus. Explicit counterexamples below refute intermediate shortcuts, not `Lambda >= 7`.

Files consulted: `SOL_TASK3.md`, `ALL8_NOTE2.md`, `k1_pay_check.py`, `ends_check.py`, and `THEORY.md` §§24–27. The checker is `note3_check.py`. Independent subagent review was attempted but **neither child started**; see §11. Thus no claim here has an independent subagent-review verdict.

Unless otherwise specified, the target setting is 18 proper planar pseudolines, each pair crossing once, multiplicity at most four, quadruples all-8 or 7-type, at least one all-8, and both alternating triple sector sums at least two. All credit quantities use doubled (`2 Lambda`) units.

## 1. Baseline and a correction to the task's expanded formula

The lead's corrected `K_1` identity is

\[
 C=2\Lambda=2R+N_*^\circ+2U_3+I_3+U_4
       +\sum_P S_P^\circ+2K_3+4K_4.                 \tag{1}
\]

Here `R=Z-(U_3+U_4)/2`; `N_*^circ` is the number of remaining `N`-ray tokens after the Note 2 payments and the case-A `K_1` payments. If `c_B(P)` counts case-B `K_1` kites paid from `P`, then

\[
 S_P^\circ=8-D_P-k_P-2c_B(P).
\]

**Algebraic correction:** the sentence beginning “Equivalently” in `SOL_TASK3.md` has an extra `U_4`. The correct expansion of (1) is

\[
 C=2Z+U_3+I_3+N_*^\circ+\sum_P S_P^\circ+2K_3+4K_4.       \tag{2}
\]

The unexpanded target (7′) is unaffected. In particular `Z<=6` in a 94 remains valid.

### Check of the lead's `K_1` payment

**Proved.** In case A, select a singly used cap edge. Its two multiple-endpoint `N`-tokens have one incident triangle, at this particular four-fan centre. They cannot be Note 2 outer-triangle tokens (two-/three-fan centres), or `K_0` tokens. A selected token determines its unique kite triangle and centre, so distinct case-A kites do not reuse it.

For case B write the kite corners as `P,Q,R,S`, with `P` quadruple and the others triple. The exterior triangle along `PQ` has third vertex `Y` on the fourth pencil axis at `P` and on `QR`, beyond `Q` away from `R`. This follows from the cyclic ray order at the triple `Q`: the exterior neighbour of `QP` is the outward ray of `QR`, not the diagonal `QS`. The exterior triangle along `RS` has apex `QR intersect PS`, on `PS` beyond `S` away from `P`.

If `PY` were a block, `Y` would be simple. Its cap would be `QR`, and the other triangle along `PY` would require `QR` to meet the ray of `PS` opposite to `S`. Its unique intersection with `PS` is on the wrong ray, by the preceding paragraph. Contradiction. The symmetric argument excludes the block two rays on the other side of `PX`.

Thus a case-B block excludes other blocks at distances `±1,±2`. At an all-8 the vertices `Y` are necessarily multiple; at a 7-type the next sector may be absent, in which case `PY` can be singly used. **The conclusion needed for payment is “not a block”, not an unconditional claim that `Y` is multiple.**

Kite blocks are isolated. With one case-B block at ray `i`, the only other possible block positions are `i+3,i+4,i+5`. They cannot all be blocks by §2 below. Therefore `D_P<=3`, `k_P<=D_P`, and `S_P>=2`. Two case-B positions have cyclic distance three or four; their exclusions leave just those two block positions, giving `D_P=k_P=2`, `S_P=4`. Three case-B positions cannot fit around eight rays. This proves `S_P>=2c_B(P)` and hence (1) with nonnegative terms.

## 2. No three consecutive quadruple blocks

**Proved.** Suppose three consecutive rays from a quadruple `P` are blocks. Their four triangular sectors share one cap line: at each intervening simple block endpoint, the cap is the unique line other than its pencil axis. The outer rays of this four-sector interval are opposite rays of the fourth pencil axis. Consequently the shared cap would meet that axis at two different vertices, one on either side of `P`. This contradicts one crossing per line pair.

No maximality assumption is used. This is the quadruple analogue of the accepted “no consecutive triple blocks”.

## 3. Fresh `N` payments for all quadruple touch/end blocks

**Proved.** Fix a quadruple-origin touch or end block `PX`, and either of its triangles `PXT`. The cap edge `XT` is singly used because `X` is a two-fan centre.

Use the following rule:

- If `PT` is single, take the token at `P` on `PT`.
- If `PT` is double and `T` is multiple, take the token at `T` on `TX`.
- If `PT` is double and `T` is simple, this triangle gives no token: `PT` is another block.

Both triangles cannot fail: failure on both sides would make `PX` the middle of three consecutive blocks, contradicting §2. Thus every such block supplies at least one token. An isolated block supplies two.

**Non-reuse.** Every selected segment is singly used, so it identifies one triangular face. If its other multiple endpoint is `T`, that face has unique simple corner `X` and unique double side `PX`. If the selected segment is `PT` with `T` simple, then `T` is a one-fan corner, since `PT` and `TX` are both single; `X` is the two-fan corner. Thus the face again identifies `X` and the quadruple origin `P`. The token cannot be one of the old outer-triangle tokens, whose origin is triple. Nor can it be a selected `K_0` or case-A `K_1` token, whose simple corner is a four-fan centre. Different quadruple blocks cannot select the same token.

Choose exactly one such token per quadruple touch/end block and reserve it. Then

\[
 N_*^\circ\ge U_4+I_4,
 \qquad N_{\rm res}:=N_*^\circ-U_4-I_4\ge0.             \tag{3}
\]

Combining (2) and (3) gives the useful exact, uniform identity

\[
 \boxed{C=2Z+U+I+N_{\rm res}+\sum_P S_P^\circ+2K_3+4K_4.}    \tag{4}
\]

The particular token choices do not change the numerical value of `N_res`. They matter for verifying disjointness. These are actual bounded single-edge tokens, not abstract subsidies from the quadruple budget.

## 4. All non-wedge ends are paid, and an exact end identity

Let `F` count ends at multiple vertices, and `G_Z` count ends assigned to unused-edge endpoint slots by the lead's classification. Let `W` count **vertices**, not ends, which are bad wedges. Each bad wedge accounts for two ends.

**Proved classification/payment.**

1. A multiple end has a free unbounded `N`-ray token. All selected tokens in the old and new payments are bounded; these end tokens are distinct and are among `N_res`.
2. A simple end whose last segment is double is an end block. Triple origins use the explicit `I_3` credit; quadruple origins use the reserved token of §3. Each end block has exactly one such end.
3. At any other simple end on `L`, consider a nontriangular face beside the incoming segment. If the adjacent ray of the other line is bounded, that segment is unused: its opposite face is incident to the unbounded outgoing ray of `L`. Assign this unused segment's endpoint slot.
4. If no such bounded unused segment exists, the other line also ends there, and the opposite bounded face is triangular. This is precisely a bad wedge.

There are two slots per unused edge. At a simple endpoint at most one end of the *other* line can use that slot. A touch block also takes one endpoint slot on its unused continuation, and different touches take different slots. A touch centre has all four rays bounded (two bounded cap edges, its bounded incoming block, and its bounded continuation), so its slot cannot simultaneously serve a line end. Hence

\[
 G_Z\le 2Z-U,
 \qquad F\le N_{\rm res}.                              \tag{5}
\]

Also the exact end count is

\[
 F+I+G_Z=2n-2W.
\]

Define

\[
 \Delta=(2Z-U-G_Z)+(N_{\rm res}-F)\ge0.                 \tag{6}
\]

Substitution in (4), without dropping any credit, gives

\[
 \boxed{C=2(n-W)+2U+\sum_P S_P^\circ+2K_3+4K_4+\Delta.} \tag{7}
\]

Thus all `I_4` ends are paid. The remaining end difficulty is genuinely the bad wedges and global redistribution, not an unpaid local quadruple end.

### A further residual-credit bound

Let `eta_0` count **bounded unused first rays at multiple points**, counted separately at their endpoints. **Proved:**

\[
 \Delta\ge2\eta_0.                                    \tag{8}
\]

Such a ray gives an `N`-token on an unused edge. None of the old payments, `K_1` case-A payments, or §3 reservations uses a zero-use edge, so it remains in `N_res` and is not an unbounded end token. Its unused-edge endpoint slot is at a multiple vertex, so it is neither a touch slot nor a simple end's unused slot. These are two distinct credits in the two summands of (6). Different rays give different tokens and endpoint slots, including when an unused edge joins two multiple points.

In the structural class, these rays can only be at triples. A locally optimal four-consecutive-sector triple has one empty ray; if that ray is bounded, it contributes at least two units to `Delta`.

## 5. The bad-wedge graph is a forest of paths at even `n`

Put a graph on the `n` arrangement lines; join two lines when their crossing is a bad wedge. It is simple and has maximum degree two.

**Same-side lemma (proved).** If both ends of `L` are bad wedges, their corner triangles lie on the same side of `L`. Indeed let the other endpoint lines be `M_1,M_2`. Each has all its other vertices on its bounded ray, on the side of `L` indicated by that corner triangle. If the indicated sides differed, the unique crossing `M_1 intersect M_2` would have to lie on both sides of `L`. It cannot lie on `L`, since the endpoint vertices are simple.

**Forest lemma (proved).** Suppose the graph has a cycle of `k` lines. Trace the closed curve made of the segments of those lines between their two wedge endpoints; it may self-intersect. Fix one cycle line `L`. The chain of the remaining segments starts and finishes on the same side of `L`, by the same-side lemma. Its nonadjacent segments cross `L` exactly `k-3` times, counted with multiplicity at concurrent crossings; all these crossings lie between both lines' extreme vertices. Hence `k-3` is even and `k` is odd.

If a line outside the cycle exists, it crosses every cycle segment once, so traversal of the closed curve changes its side of that outside line `k` times. A closed curve must change sides an even number of times. Thus `k` would be even, contradiction. The simple wedge vertices cannot be concurrent with that outside line; coincident crossings in segment interiors are counted once for each traversed segment and cause no parity problem.

Therefore a cycle must contain every arrangement line, and its length must be odd. At even `n` there is no cycle. Write

\[
 \pi=n-W
\]

for the number of path components, including isolated lines. In particular `pi>=1`. For `n=18`, (7) becomes the exact identity

\[
 \boxed{\Lambda=\pi+U+\tfrac12\sum_P S_P^\circ+K_3+2K_4+
                       \tfrac12\Delta.}               \tag{9}
\]

This is a reduction, **not yet** the desired lower bound.

## 6. What a 94 must now satisfy

**Proved necessary conditions.** A 94 has

\[
 \pi+U+K_3+2K_4\le6,
 \qquad \sum_P S_P^\circ+\Delta
       =2(6-\pi-U-K_3-2K_4),                           \tag{10}
\]

as well as `Z<=6`. Thus `W>=12`. The sufficient subcase

\[
 \pi+U+K_3+2K_4\ge7
\]

is closed by (9) and the congruence `Lambda == 0 mod 3`.

In particular the `pi=6` case of a 94 would require

\[
 U=0,\quad S_P^\circ=0\text{ for every quadruple},\quad
 K_3=K_4=0,\quad\Delta=0.                             \tag{11}
\]

Every unused-edge slot would then serve a good unused end, and every token of `N_res` would be unbounded. There can be no bounded empty multiple ray by (8). Every locally optimal four-consecutive-sector triple must have its empty ray unbounded. At a zero-slack quadruple all its blocks are kite blocks (see the mask analysis in §8), so in this case there are no quadruple touch, end, or three-fan blocks.

The exact remaining obligation, in these terms, is

\[
 2\pi+2U+\sum_P S_P^\circ+2K_3+4K_4+\Delta\ge13.        \tag{12}
\]

Showing (12) for `pi<=6` still requires geometric information not supplied by nonnegativity or the forest lemma. No per-line ownership rule proving this is asserted here.

## 7. Correct parity inventory: simple cap steps cannot be omitted

**Proved.** Suppose every bounded segment on `L` is singly used, both ends are bad wedges, and triple optimality holds. A quadruple in the structural class cannot be on such a line: at an all-8 or 7-type at least one of the two opposite axis rays is double.

At an interior triple, put its sector bits cyclically as `s_0,...,s_5`, with the chosen axis rays numbered 0 and 3. Single use gives `s_0+s_5=s_2+s_3=1`. A same-side step would give either `s_0=s_2=1,s_3=s_5=0` or the reverse. In the first case the odd alternating sum is at most one, and in the second the even sum is at most one. Both contradict optimality. Thus the sides **flip** at this triple.

At a simple interior vertex the sides flip unless the two triangles are on the same side of `L`. In that exceptional case their shared ray on the other axis is double; its other endpoint is multiple by L1, while the opposite ray has zero use. The vertex is exactly a touch/end block centre with cap line `L`. Conversely every such centre is a same-side simple step on its cap line.

Let `t_L` count triples on `L`, and `f_L` count these simple same-side cap steps. There are `n-1-t_L` vertices and `n-3-t_L` interior vertices on `L`. The two corner triangles are on the same side, so the number of flips is even. Therefore

\[
 t_L+f_L\equiv n-3\pmod2;\qquad
 \boxed{t_L+f_L\text{ is odd when }n\text{ is even}.}    \tag{13}
\]

A line with only simple vertices need **not** alternate if the rest of the arrangement has multiple points: it can cap a block. The simple-arrangement BBL assertion is not contradicted; its whole-arrangement simplicity hypothesis excludes these cap steps. A triple also changes the number of vertices on a line, so parity cannot be inferred from `n-2` bounded segments when triples are present.

### Explicit counterexample to the naive even-`n` perfect-line claim

The lead's `n=12` witness from `work/eng/oth/smalln/s_n12_l9_o1.txt` is

```text
1 4 6 5 6 4 3 8 10 9 7* 9* 6 4* 6** 5 3 2 3 4 5* 1 0 1 3 2 3 4 5 6* 8* 10 7 8 9 1 8 5* 3 2 3 4 5 6 7 8 3
```

It satisfies the structural class, contains an all-8, and satisfies triple optimality. It has `T=37, Lambda=9`. Line 7 has only simple vertices, all ten bounded segments singly used, and two bad-wedge ends. Its triangle-side sequence is

```text
- + - - + - + - + -
```

The same-side step is event 6, an `I_3` centre from event 13, capped by line 7. Thus its two corner triangles are on the **same**, not opposite, side. This refutes a parity lemma based only on evenness and simplicity *on the line*. It is not an 18-line counterexample to (7′).

## 8. Zero-slack all-8 patterns: there is a third branch

**Proved mask classification.** At an all-8 with `S_P^circ=0`, precisely these possibilities survive the basic local restrictions:

| `D_P` | `k_P` | `c_B(P)` | block pattern |
|---:|---:|---:|---|
| 4 | 4 | 0 | four alternating kite blocks |
| 3 | 3 | 1 | relative positions `0,3,5`; position 0 is case B |
| 2 | 2 | 2 | two case-B blocks at cyclic distance 3 or 4 |

This is a classification of local masks, not of arrangements. The first row follows from `D+k=8`, isolation of kite blocks, and no three consecutive blocks. In the second row the distance-two exclusions give `D<=3`, while zero slack requires `D+k=6`, hence three isolated kites at `0,3,5`. With two case-B blocks the exclusions leave just those two blocks and `S=4`, which is entirely consumed. The 569-mask exhaustive check independently verifies these deductions; there are respectively 2, 8, and 12 labelled zero masks. At a 7-type, zero corrected slack likewise requires all its blocks to be kite blocks; without case B its uncorrected slack is at least two, and with case B the preceding bounds force `D=k` whenever the corrected slack is zero.

**First row, proved additional restriction:** at least one first multiple neighbour is quadruple. If all four were triple, the far corners of opposite kites would be the intersection of the same two opposite cap lines. They cannot lie on opposite pencil rays. This is the accepted opposite-kite/far-corner argument.

**Second row, proved additional restriction:** let `Q_1,Q_2,Q_4,Q_6,Q_7` be the first multiple neighbours on those relative rays. Then

\[
 Q_4\text{ is quadruple, or both }Q_2,Q_6\text{ are quadruple}. \tag{14}
\]

Proof: `Q_1,Q_7` and the far corner `R_0` of the case-B kite are triple. Let `C_ab` denote the star cap through consecutive neighbours `Q_a,Q_b`. Then `R_0=C_12 intersect C_67`. The exterior triangle along `Q_1 R_0` has apex `Y=(P Q_1) intersect C_67`, beyond `Q_1` away from `P`: all other combinations of the incident triple lines pass through the kite centre or another intervening vertex.

If `Q_4,Q_6` were both triple, the far-corner rule for the kite on ray 5 would place its far corner at `C_24 intersect C_67`, also on `P Q_1`. This is the same intersection `Y`, but that far corner lies on ray 5, opposite to ray 1. Contradiction. Hence `Q_4` or `Q_6` is quadruple. Applying the same argument to the exterior edge `Q_7 R_0` and the kite on ray 3 gives `Q_2` or `Q_4` quadruple. Together these are (14).

**Third row must not be omitted.** It is geometrically realizable in the structural class. Start with lines `ax+by+c=0`:

```text
(1,0,0), (0,1,0), (1,-1,0), (1,1,0),
(1,0,-1), (1,0,1), (2,1,-3), (-2,1,-3),
(2,1,3), (-2,1,3), (0,1,5).
```

Apply `lines2gens.transform` with parameters `1/97,1/89`, followed by the shear implemented in the checker. This makes the projective parallel intersections finite and produces the proper 11-line wiring word

```text
0 4 5 4 1 2* 6* 4* 3 1* 0 8 6* 3** 1* 8* 6* 5 3* 2 5* 0* 4 7 8 7 3 6
```

It has `T=26,Z=8,Lambda=21`, one all-8 (event 13), two case-B `K_1` kites there, and `S_13^circ=0`. **It fails triple optimality at other vertices**, so it does not refute the target class with that extra hypothesis. It does refute dropping the third branch on purely structural/geometric grounds. Whether optimality excludes this branch or forces enough external credit remains open here.

## 9. An 18-line counterexample to `Q>=7` and component cost `>=6`

Take the lead's 10-line minimum word

```text
1 0 4 6 7 5* 4 3 1* 3** 6* 8 2 0 7 5* 3* 5 6 7 6 4 2 1 2 3 4 5 6 0
```

Append the eight descending strings `h,h-1,...,0` for `h=9,...,16`. This is an explicit 18-line pseudoline arrangement: the prefix reverses the ten old tracks, and each appended string moves the next new track past every preceding track. Each old-new and new-new pair crosses once, and no old-old pair crosses again.

Exact re-evaluation gives

\[
 T=33,\quad Z=184,\quad\Lambda=189,\quad
 2R=367,\quad 2Q=11.
\]

It has exactly one all-8, no other quadruple, and satisfies every triple optimality condition. Its six multiple points form one bridge component (and one line-connected multiple component), whose total cost is **5**. Thus

- `Q>=7` is false even at `n=18` in the task's structural/optimality class;
- a general mixed-component cost bound `>=6` is also false there.

The huge unused-edge residual is not disposable. This example does **not** satisfy `T=94` or global lexicographic maximality, and says nothing against a rule that explicitly assumes those additional conditions. It is not a counterexample to the desired inequality.

## 10. Reproducible checks and a bounded SAT probe

Run from the repository root:

```bash
python work/bbl/note3_check.py \
  work/eng/lattice/lattice18.jsonl \
  work/eng/lattice/lattice_family.jsonl \
  work/eng/lattice/mixed_all.jsonl \
  work/phi/gallery18.jsonl
```

Exact stdout is saved in `work/bbl/all8_work/note3_check.out`. The checker asserts token-level disjointness, the fresh quadruple payment, slot capacities, (7), (8), even-`n` forest acyclicity, and (13) on eligible lines. It also checks all pairs and the final permutation of the explicit wiring words. Its use of existing `arr.py`, Note 2 face helpers, and the lead's old-token routine is documented in the imports; this is not a wholly independent implementation of the arrangement parser.

The dataset checks are evidence, not classification: they include nonstructural arrangements and sampling repetitions across sources (identical words are deduplicated), and skip multiplicities above four. The stronger parity assertion is checked only where its hypotheses hold. The geometric double-case-B example deliberately fails optimality. No minimum over all arrangements is inferred.

The new `all8_work/ends_probe.py` adds triple optimality and the necessary cut `W>=12` to the existing 18-line `T=94` class encoding, retaining lazy pair clauses. It independently reconstructs and checks any accepted SAT model. Pinned validation command:

```bash
python work/bbl/all8_work/ends_probe.py --validate --seconds 120 \
  --out work/bbl/all8_work/ends_validate
```

This returned `SAT_VERIFIED` for the §9 witness (`T=33,Lambda=189,W=4`), with 118219 variables, 807128 clauses, zero conflicts and two decisions. Artifacts: `ends_validate.log`, `ends_validate/result.json`, and `ends_validate/witness.json`.

Unrestricted command:

```bash
python -u work/bbl/all8_work/ends_probe.py --seconds 300 \
  --out work/bbl/all8_work/ends18
```

Artifacts: `ends18.log` and `ends18/result.json` when terminal. It builds 255647 variables and 1081039 clauses. Its result is recorded below after the dependency barrier. An `UNKNOWN` result is neither SAT nor UNSAT. An `UNSAT_UNCERTIFIED` result would require an encoding audit and a separately checked DRAT proof before being used as an exclusion.

## 11. Delegation and remaining work

Two fresh, read-only mathematical subagents were authorized and requested: an endpoint-payment audit and an independent surplus attack. Both failed **before starting** because the host package did not provide `@earendil-works/pi-agent-core/node`. Workflow `2338ebed-5862-4fb1-9026-e15de8d83c3f` is terminal with two failed launches and no review artifacts. No runner fallback was attempted.

The state is captured in `all8_work/note3_delegation_blocker.json` and `all8_work/note3_partial_diff.patch`: repository/cwd `/home/nail/stuff/sundai_math`, shared dirty checkout, branch `hills/kobon-triangles`, HEAD `bfab7f866b6e1fac20f090a7790152707d18c546`. These failures are not mathematical evidence.

**Still open:** prove (12), equivalently (7′), for the remaining `pi<=6` cases. A useful next finite case is (11), including the double-case-B zero-slack branch and the restriction that no locally optimal four-fan triple has a bounded empty ray. One must also control triple parity compression and simple cap steps in any per-line ownership proof. Paying debts, counting endpoints, or checking examples alone does not establish the strict surplus over `C=12`.

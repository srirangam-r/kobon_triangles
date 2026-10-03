# All-8 Note 5 — allocation, end reconciliation, and zero-star boundaries

**Task 5 remains partial. Neither (B) nor the global zero-credit all-8
exclusion is proved. There is no UNSAT certificate and no counterexample
to the desired `T<=93`.** The new results are an exact accounting of the
missing Stage 1 step, explicit sample allocations, additional disjoint
residual-token payments, and local Stage 2 reductions.

The lead's `SOL_TASK5.md` accepts Note 4's (UI) and (H) lemmas. Those and
the accepted Note 3 identities are inputs here. The new local derivations
below have not yet been reviewed by the lead. At the user's request,
`stage2_zero_credit` worked **only on Stage 2**, in parallel with the
main agent's allocation/accounting work. Its detailed report is
`STAGE2_TASK5.md`; its checker is `stage2_quad_check.py`. The main agent
audited its ray-order arguments before incorporating the reductions.

Throughout, there are 18 proper pseudolines, each pair crosses once,
multiplicity is at most four, quadruples are in the structural class,
and both alternating triple sector sums are at least two where that
hypothesis is used. Credit units are those of

\[
\Lambda=288-3T=\pi+E/2,\qquad
E=2U+C_q+\Delta_Z+\Delta_N,
\quad C_q=\sum_P S_P^\circ+2K_3+4K_4.
\]

Here `pi=18-W`, with W counting bad-wedge **vertices**, and

\[
\Delta_Z=2Z-U-G_Z,\qquad \Delta_N=N_{\rm res}-F,
\qquad F+I+G_Z=2\pi.
\]

All displayed credit summands are nonnegative. The intended Stage 1
inequality is `(B): E>=18-3*pi`. Only after proving B can a 94 be
reduced to `pi=6,E=0`; this reduction is not assumed in Stage 1.

## 1. Exact Stage 1 accounting: O2Q is not the whole trade-off

Let J count lines with two bad-wedge ends. Let Q0 count such lines with
**no bounded unused segment**, including those with double segments.
Set

\[
H_Z=J-Q_0,
\]

the number of two-W-end lines having an unused segment. This is a line
count, not Z. Let sigma be the number of isolated vertices of the
bad-wedge forest. Its nontrivial path components give the exact identity

\[
J=18-2\pi+\sigma.                                      \tag{1}
\]

Indeed a nontrivial path of m vertices has m−2 degree-two vertices;
isolated lines have none. Define two balances

\[
c=2I+2U+\Delta_N-Q_0,\qquad
r=\pi+\sigma+\Delta_Z+C_q-2I-H_Z.
\]

**Proved algebraic identity:**

\[
\boxed{c+r=E-18+3\pi.}                                \tag{2}
\]

This follows by adding the balances, using `Q0+HZ=J`, and substituting
(1). Thus O2Q is `c>=0`, whereas the missing end reconciliation is
`r>=-c`. The stronger shortcut `r>=0` is false. In particular, the
unspent O2Q labels cannot be discarded before doing end accounting.
Equation (2) identifies the obligation; it is not a proof of B.
On every 93, `Lambda=9`, so its B slack is identically pi. B's passes
on that dataset are automatic from the forest, not evidence for a
universal allocation/end proof.

**Eligible counterexample to `r>=0`: 93 record 8383.**

```text
T=93, Lambda=9, pi=3, U=1, I=3
Delta_N=10, Delta_Z=0, C_q=0
J=12, Q0=11, HZ=1, sigma=0
c=7, r=-4, B_slack=c+r=3
word_valid=True, structural_class=True, triple_optimality=True
```

All ten residual tokens there are the five single central three-fan
caps' endpoint tokens. The full word and geometry are saved in
`all8_work/note5_93/eligible_reconciliation_minimum.json`. Negative r
occurs on 910 of all 14,376 reconstructed 93s, including 263 of the
13,718 eligible records. The minimum is −4. It also occurs on 83 eligible
earlier-dataset records, minimum −3.

An equivalent direct allocation target, without using I as new credit,
is

\[
J\le E+\pi+\sigma.                                   \tag{3}
\]

By (1), (3) is exactly B. An O2Q proof must therefore supply a joint
allocation/end argument, not merely rename its two I labels as E-credit.

## 2. Explicit O2Q sample allocations and a failed incident rule

`note5_allocation.py` reconstructs the **actual bounded residual N
tokens**. It takes all N-ray tokens, removes the accepted old payments,
the case-A K1 payments, exactly one Note 3 reservation per quad-origin
U/I block, and the multiple-end tokens. The remaining set has exactly
`Delta_N` elements. Removed payment sets are checked disjoint.

For the candidate allocation, each U/I block has two distinct formal
labels, origin and cap. Together with the physical residual tokens,
there are exactly `2I+2U+Delta_N` resources. These labels are counting
resources, **not additional E-credit**. The demand set is every Q0 line;
it is computed before the eligibility filter.

Three precisely specified reachability rules are tested:

1. **Incident.** An origin label or N token can pay a pencil line through
   its multiple origin. A cap label can pay its cap line only.
2. **Bridge/mutual.** Join multiple vertices when a double bridge connects
   them, or they are block origins at the same mutual three-/four-fan
   simple centre. An origin label or N token can pay any pencil line in
   its component. A cap label can pay its cap line or any pencil line in
   a component meeting that cap line at a multiple vertex.
3. **Line-connected.** Add component links between consecutive multiple
   vertices along any arrangement line, even across gaps or single
   segments; retain the same resource rule.

A bipartite maximum matching supplies an actual injection or an explicit
Hall obstruction. The full injections are in each `allocations.jsonl`.
The component transport rule and its universal Hall inequality remain
**unproved**. Matching all samples is not a proof that geometric payment
can always be routed this way.

| Input cohort | Records / eligible | Incident failures, all / eligible | Bridge/mutual failures | Line-connected failures |
|---|---:|---:|---:|---:|
| 93 data | 14376 / 13718 | 59 / 26 | 0 | 0 |
| Earlier datasets | 3445 / 2259 | 0 / 0 | 0 | 0 |
| Binding witnesses | 29 / 29 | 0 / 0 | 0 | 0 |

Every failed incident matching has deficit one. The first eligible
failure, record 2478, has

```text
T=93, pi=1, U=1, I=1, Delta_N=12, Q0=14, P0=0
incident matching=13/14
Hall lines={0,1,2,7,8}
reachable resources=4 residual N tokens
```

The four tokens are `(origin,edge)` equal to
`(39,(12,4)), (65,(12,6)), (67,(11,5)), (92,(11,7))`.
Thus five demanded lines share only four incident resources. The full
word, matching, and Hall set are in
`all8_work/note5_alloc93/incident_eligible_first_failure.json`.
This refutes **that ownership rule**, not O2Q. There are no perfect lines
in this example; the extra double lines in Q0 must genuinely be covered.

## 3. A larger disjoint residual-token lemma

The following strengthens the accepted (H) bound. Its proof uses only
the accepted payment rules and uniqueness of a single edge's triangle.
All tokens below are bounded and survive every old/new payment and the
end removal.

Define the following token sets:

- `eta0`: one N token for each bounded unused first ray at a multiple.
- `H*`: the two endpoint tokens of each **single** central cap joining
  the multiple origins of a three-fan centre. Unlike the earlier h,
  no perfect-line incidence is required.
- `M*`: both endpoint tokens of every single edge of an all-multiple
  triangular face.
- `O*`: for a triangle with multiple P,Q and simple X, where PX and QX
  are both single, the tokens at P on PX and Q on QX; also both tokens
  on PQ if PQ is single.
- `B*`: if X is a two-fan U/I centre at origin P, Q is the other multiple
  vertex of one of its triangles, and PQ is single, the token at **Q**
  on PQ.

For a kite let s be its number of single cap edges and q its number of
quadruple corners. Its unspent cap-token contribution is

\[
v(X)=
\begin{cases}
2(s-2), &q=0,\\
2(s-1), &q=1,\ s>0\quad\text{(case A)},\\
0, &q=1,\ s=0\quad\text{(case B)},\\
2s, &q\ge2.
\end{cases}
\]

The accepted K0 rule ensures `s>=2`. Write `V_K=sum_X v(X)`.

**Proved disjoint-payment bound:**

\[
\boxed{\Delta_N\ge
\eta_0+|H^*|+|M^*|+|O^*|+|B^*|+V_K.}                  \tag{4}
\]

Since the eta0 endpoint slots also survive, Note 3 gives

\[
\boxed{\Delta\ge
2\eta_0+|H^*|+|M^*|+|O^*|+|B^*|+V_K.}                \tag{5}
\]

**Proof.** Unused rays are untouched by all single-edge payments. For
H*, the central three-fan face is not an old outer payment face. For M*,
there is no simple payment centre at all. In O*, the simple corner has
a one-triangle fan, since both incident edges are single; no two-/three-
or four-fan payment uses that face (an opposite isolated fan does not
change this). For B*, the old triple payment, or a quad reservation,
can take the token at P on PQ, not the token at Q. The unique double
side PX and unique simple centre identify which endpoint is paid.

At a kite, the old rule spends exactly two complete single-cap endpoint
pairs at K0 or one at case-A K1, and none at q>=2. All other single cap
tokens survive: their unique triangular face has the kite's four-fan
centre, not a U/I or three-fan centre. Different kites do not reuse a
single cap edge.

The contexts just listed are disjoint. A single token determines its
unique triangle; within a two-fan face the unspent endpoint is specified.
The unused tokens have no triangle. Quad U/I reservations have their
own two-fan centre and cannot intersect any of these sets. Finally, all
tokens here are bounded, unlike F's end tokens. This proves (4).
The eta0 slots are distinct from all touch/simple-end slots, proving (5).

The checker now reconstructs the residual set explicitly and verifies
**set inclusion and pairwise disjointness**, not merely the numerical
bound. For kites it checks that exactly `v(X)` cap tokens survive.
Both bounds pass all three input cohorts, with minimum residual slack
zero in each. This is corroboration of the local proof, not a global
credit lower bound.

## 4. Two safe perfect-line reductions; the bridge argument still stops

**Perfect cap-edge kite lemma.** In the eligible class, a kite whose cap
edge lies on a perfect interior line has at least three single cap
edges, so contributes at least two units to `Delta_N`.

For a cap PQ on a perfect line, P,Q cannot be quadruple. At each triple,
Note 4's accepted `011011`/`110110` calculation puts its two double rays
on the kite-block axis and makes the other two axes single. Thus the
other cap at P and the other cap at Q are single, in addition to PQ.
These are three distinct kite caps. Its q is at most two. Formula (4)
leaves at least two tokens whether q=0,1,2. In particular no such kite
exists when E=0. The datasets contain no eligible perfect cap-edge kite,
so this particular branch has no positive sample coverage.

**Opposite I lemma.** If a triple has end blocks on both opposite rays
of one axis, then n=5. That line has exactly the three vertices
`simple end — triple — simple end`: both block segments are first
segments, and the continuations are unbounded. It meets two other lines
at the triple and one at each simple end, giving n−1=4. This requires
neither triple optimality nor E=0.

Consequently, in the E=0 regime a perfect-line triple P must have a
double **bridge** on at least one of its two double-axis rays. Otherwise
both rays are blocks; U is excluded, H by the accepted (H) lemma, K by
the perfect cap-edge kite lemma, and two I blocks by the opposite I
lemma.

There is a further valid first step. Let PQ be that bridge and PQX its
incident triangle on the perfect line through P. PX is single. X cannot
be multiple, by M*; if QX were single, O* would give residual credit.
Hence X is simple and QX double. The perfect axis at X has two single
rays, so X is a two-fan U/I centre with cap equal to the perfect line.
U=0 makes it I. Its origin Q must be triple, since zero-slack quadruples
have only kite blocks.

**This does not prove that perfect lines have no triples.** The other
cap neighbour of X can be simple. In that case its triangle's single
Q-end token is legitimately consumed by the I payment; B* supplies no
other multiple token. A proposed propagation to three alternating I
blocks therefore has a missing step. We do not assert it.

## 5. The raw four-sector-fork shortcut is refuted

The proposed shortcut was: at a triple Q, a double bridge QP whose two
incident triangle apices X,Y are simple block centres, with PX,PY
single, forces exactly four consecutive triangular sectors at Q and an
empty opposite bridge ray. It is false even with global triple
optimality.

Binding witness 1 (`work/eng/oth/wit3/wit_sat.jsonl`) has

```text
n=18, T=57, pi=17, U=6, I=3, Delta_N=23, Delta=188
word_valid=True, structural_class=True, triple_optimality=True
Q=60, P=70, simple tips X=61 and Y=69 (both U)
Q sector bits=[1,0,1,1,1,1]
opposite bridge ray=(11,-1), bounded, use=1
```

The complete word and geometry are preserved in
`all8_work/note5_witnesses/raw_fork_first_counterexample.json`.
The binding cohort contains ten raw forks, five not four-sector. The
93 cohort contains 28, all ineligible and all not four-sector; eligible
93 records alone would have hidden the counterexample. Extra concurrency
at opposite cap corners can supply another triangular sector. Neither
global optimality nor a sample absence repairs the missing assertion.

The checker records this conjecture's failures without aborting. Its
`failures=0` field refers to asserted identities/payment bounds, **not**
to the raw fork or to `r>=0`.

## 6. Stage 2: independently audited local quadruple reductions

Detailed incidence and ray-order proofs are in `STAGE2_TASK5.md` §§1–4.
They give the following new reductions, not the requested final
contradiction.

**Two case-B blocks must be opposite.** The earlier distance-three-or-
four alternative can be sharpened. Put case-B blocks on rays 0 and 3.
Their triple corners Q1,Q2 share a cap C also containing the two far
kite corners R0,R3. The case-B exterior triangle along R3Q4 requires
`C intersect (P Q4)` beyond Q4 away from P. But PQ4 is PR0, since rays
0 and 4 are opposite, and its intersection with C is R0 on the wrong
ray. This is impossible. The argument also works at a 7-type point.

**Every zero-slack quadruple is all-8; every 7-type has corrected slack
at least two.** Case-B exterior triangles force four adjacent sectors
per block. Opposite case-B blocks cover all eight. In the remaining
zero masks, alternating four blocks or blocks 0,3,5 with case B at 0
also force all eight. For slack one with one case B, the remaining two
blocks are either adjacent (then neither is a kite, too little k), or
on rays 3 and 5 (again all eight sectors). The no-case-B 7-type bound
is the accepted uncorrected bound. Thus slack zero and one are excluded.

**An opposite-double-case-B star has no zero-slack quadruple first
neighbour.** At a possible quad neighbour B, the rays to the two adjacent
triple corners and to P are three consecutive bridge rays. The local
zero mask must itself be opposite-double-case-B. Its new far corner is
forced onto the old case-B exterior cap. The new exterior triangle at B
then has apex E across P, while it requires the fourth-axis ray at B
away from P. P intervenes on the alleged triangle edge. This contradicts
adjacency. The full labelling is in the subagent's §3; that ray-order
step, not just the sample checker, is essential.

With three prescribed consecutive bridge rays the exhaustive local
mask enumeration has **80** configurations, slack counts

```text
{0:1, 2:9, 3:9, 4:21, 5:19, 6:15, 7:5, 8:1}
```

and unique zero mask `B=K=CB={0,4}`. Thus such a quad neighbour in fact
has corrected slack at least two. This finite enumeration proves the
claim about these explicit local masks, not arrangement realizability.

**Global zero-slack cluster reduction.** Assume every quadruple has
zero slack and K3=K4=0. The quad first-neighbour graph consists of:

- isolated opposite-double-case-B stars; or
- collinear paths of k=2,3,4 quadruples, whose interior stars are
  alternating and whose endpoints are alternating or single-case-B.

In an alternating star, at least one bridge neighbour is quadruple by
the accepted far-corner argument. At most two can be, since adjacent
quad bridge neighbours make K3/K4; if two, they are opposite. A
single-case-B star has exactly its central opposite neighbour quadruple
by accepted propagation and K3/K4 exclusion. Thus a nonisolated component
continues along one proper line H and cannot cycle.

If b is its number of single-case-B endpoints, distinct line counting
gives

\[
\boxed{n\ge3k+5+b.}                                   \tag{6}
\]

There are H and 3k other pencil lines, four additional axes at the two
triple boundary vertices on H, and b diagonals at the intervening simple
case-B centres. Their intersections with H distinguish the groups.
At n=18, k<=4 and a four-quad path has b<=1. An isolated double-case-B
star uses at least ten lines, not more than eighteen; it remains a real
branch, not a discarded case.

The remaining solver pins are explicit in `STAGE2_TASK5.md` §5. In a
mixed path, interior and inward-end kites are K2 (all caps double under
Delta=0). An alternating endpoint has two outward K1A kites (exactly
one single cap each); a case-B endpoint has one outward K1B kite (all
caps double). These outward kites must not all be incorrectly pinned
as K2. The boundary still needs to force U, corrected slack, or Delta>0.

## 7. Exact checker outputs and reproduction

The new checkers use the accepted arrangement parser and Note 3 face/
payment helpers; they are not independent parsers. All metrics inputs
below are completed `tradeoff_check.py` outputs. The new payment checker
ran first on the complete 93 input and then on the other cohorts; after
adding explicit residual-set inclusion checks it was rerun on all three.

| Payment/accounting cohort | Records / eligible | Residual-bound failures | Negative r, all / eligible | Eligible E=0 / with all-8 |
|---|---:|---:|---:|---:|
| 93 data | 14376 / 13718 | 0 | 910 / 263 | 1130 / 0 |
| Earlier datasets | 3445 / 2259 | 0 | 200 / 83 | 1130 / 0 |
| Binding witnesses | 29 / 29 | 0 | 0 / 0 | 0 / 0 |

The 1130 zero-credit records are simple 93 arrangements (`pi=9`), not
the proposed 94 corner (`pi=6`). The cohorts overlap; these counts are
not a combined count of distinct arrangements. There is **no globally
zero-credit all-8 example** to exercise that conditional branch.

Exact allocation summaries and full injections:

```text
all8_work/note5_alloc93/summary.json; allocations.jsonl
all8_work/note5_alloc_gallery/summary.json; allocations.jsonl
all8_work/note5_alloc_witnesses/summary.json; allocations.jsonl
token_reconstruction_errors=0 in every cohort
```

Exact payment/accounting summaries and per-record inventories:

```text
all8_work/note5_93/summary.json; records.jsonl
all8_work/note5_gallery/summary.json; records.jsonl
all8_work/note5_witnesses/summary.json; records.jsonl
failures=0 in every cohort (asserted claims only)
```

The Stage 2 targeted checker used 3474 supplied records, checked 2450
in the structural class, and explicitly skipped 1024 outside it:

```text
quadruples=97; seven_type_points=52; zero_slack_points=6
double_case_B_points=1; double_case_B_quad_first_neighbours=1
globally_zero_slack_quad_arrangements=0
sample_failures=0
```

Exact result: `all8_work/stage2_quad_summary.json`. The neighbour claim
has only one exercised sample, with positive neighbour slack. None of
these samples constitutes the global Stage 2 contradiction.

Run from the repository root (change output names to retain old runs):

```bash
python3 -m py_compile work/bbl/note5_check.py \
  work/bbl/note5_allocation.py work/bbl/stage2_quad_check.py

python3 work/bbl/note5_allocation.py \
  work/bbl/all8_work/tradeoff_rebuilt93/metrics.jsonl \
  --out work/bbl/all8_work/note5_alloc93
python3 work/bbl/note5_allocation.py \
  work/bbl/all8_work/tradeoff_gallery/metrics.jsonl \
  --out work/bbl/all8_work/note5_alloc_gallery
python3 work/bbl/note5_allocation.py \
  work/bbl/all8_work/tradeoff_all8_witnesses/metrics.jsonl \
  --out work/bbl/all8_work/note5_alloc_witnesses

python3 work/bbl/note5_check.py \
  work/bbl/all8_work/tradeoff_rebuilt93/metrics.jsonl \
  --out work/bbl/all8_work/note5_93
python3 work/bbl/note5_check.py \
  work/bbl/all8_work/tradeoff_gallery/metrics.jsonl \
  --out work/bbl/all8_work/note5_gallery
python3 work/bbl/note5_check.py \
  work/bbl/all8_work/tradeoff_all8_witnesses/metrics.jsonl \
  --out work/bbl/all8_work/note5_witnesses

python3 work/bbl/stage2_quad_check.py \
  --out work/bbl/all8_work/stage2_quad_summary.json \
  work/eng/oth/wit3/wit_sat.jsonl \
  work/eng/lattice/lattice18.jsonl work/eng/lattice/lattice_family.jsonl \
  work/eng/lattice/mixed_all.jsonl work/phi/gallery18.jsonl
```

## 8. Remaining obligations

Stage 1 needs a universal disjoint allocation (including Q0's double
lines) **and** the joint reconciliation in (2), or a direct proof of
(3). The bridge/mutual matchings are a tested candidate, not Hall's
inequality for the entire class.

Stage 2 needs a boundary contradiction for the isolated opposite-double-
case-B star and the k=2,3,4 collinear paths. Slot/token saturation and
the six bad-wedge paths have not yet supplied it. No asserted lemma
eliminates all triples from perfect lines. B, the strict all-8 A, and
the exclusion of a 94 remain open.

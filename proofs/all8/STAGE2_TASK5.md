# Task 5 Stage 2 — independent zero-slack quadruple audit

Stage 2 remains incomplete. The results below are conditional on the
zero-credit hypotheses of `SOL_TASK5.md`; they do not prove Stage 1 (B),
and they do not turn the sample checks into an exclusion of a 94.

The accepted inputs are Note 3's payments, mask classification, far-corner
and case-B exterior-triangle rules, and its zero-slack propagation lemma.
The zero-credit assumptions are

\[
U=0,\quad S_P^\circ=0\text{ at every quadruple},\quad
K_3=K_4=0,\quad\Delta=0,
\]

in the structural class with triple optimality, 18 proper pseudolines,
and each pair crossing once. The proofs in §§1–3 actually need fewer of
these hypotheses, as specified. No straightness or metric convexity is
used: all ordering claims concern adjacent rays, proper rays, and unique
line intersections.

## 1. Two case-B blocks are opposite

**Proved local reduction.** Note 3 permits cyclic distances three or four
between two case-B blocks. Distance three is impossible, including at a
7-type point.

Let the two blocks have rays 0 and 3 at a quadruple P. Write their kite
corners as `(P,Q1,R0,Q7)` and `(P,Q2,R3,Q4)`, where R0 and R3 are on rays
0 and 3, respectively; Q1,Q7,Q2,Q4 are triple. A case-B block at i forces
sectors i−2,i−1,i,i+1: its two kite sectors and the exterior triangles on
the two P-incident cap edges. Thus the triangle P Q1 Q2 exists even if
one of P's eight sectors is absent elsewhere.

Its cap C=Q1 Q2 is also Q1 R0 and Q2 R3. At each triple this follows from
the two other axes being its P-axis and its kite diagonal, and from the
triangle using the ray opposite to the far-corner cap. In particular C
contains R0,Q1,Q2,R3 in that order, or the reverse order.

The case-B exterior triangle along R3 Q4 has apex

\[
C\cap(PQ4),
\]

on PQ4 beyond Q4 away from P, by the accepted exterior-triangle rule.
But ray 4 is opposite ray 0, so PQ4 is P R0 and its unique intersection
with C is R0. R0 lies on the opposite ray. This is a contradiction.

Consequently two case-B blocks must be opposite. Their forced four-sector
intervals cover all eight sectors, so their quadruple is all-8.

## 2. Every zero-slack quadruple is all-8

**Proved local reduction.** The accepted mask classification gives only
`(D,k,c_B)=(4,4,0),(3,3,1),(2,2,2)` at zero corrected slack. Without case B,
four alternating kite blocks force all eight sectors. With one case B,
the blocks at 0,3,5 and the exterior sectors forced by block 0 also force
all eight. With two case B, §1 forces them opposite and again all eight.

Thus a 7-type point cannot have zero corrected slack. The stronger local
bound `S_P^circ >= 2` at a 7-type follows from the same block restrictions:
without case B the accepted uncorrected bound is two; with one case B,
`D<=3`, and a total `D+k=5` would require three blocks with precisely two
isolated kite blocks. If the two non-case-B blocks are adjacent, neither
is a kite, so k=1. If they are not adjacent, the allowed zero-near-case-B
positions are 3 and 5, making all eight sectors present. The two-case-B
case is all-8 by §1. This rules out corrected slack one as well as zero
at a 7-type point.

## 3. A double-case-B zero star cannot adjoin another zero star

**Proved local reduction.** Let P have its two case-B blocks on opposite
rays 0 and 4. Denote its six first multiple neighbours, cyclically, by

\[
A=Q_1,\ B=Q_2,\ C=Q_3,\ D=Q_5,\ E=Q_6,\ F=Q_7.
\]

The corners A,C,D,F are triple. Only B and E could be quadruple. Let R0
and R4 be the far corners of the two kites. The cap lines are

\[
c_{AB}=A B R0,\quad c_{BC}=B C R4,\quad
c_{DE}=D E R4,\quad c_{EF}=E F R0.
\]

Suppose B is quadruple with zero corrected slack. At B the triangles PBA
and PBC make the rays toward A,P,C three consecutive rays with multiple
first endpoints. Neither the alternating zero mask nor the single-case-B
zero mask has three consecutive such bridge rays. Hence B also has the
opposite-double-case-B zero mask, with BP in the middle of one of its
three-bridge runs.

Consider its kite adjacent to the BA ray, and call its centre Y. At the
triple A, the triangle BAY is on the opposite side of AB from PBA. Its
ray AY is therefore the old kite diagonal opposite the old centre X0.
This follows from ray adjacency: the other direction on PA is separated
from AB by that diagonal, so cannot bound BAY.

Let Z be the new kite's corner opposite B. At A, its cap AZ uses the PA
ray away from P. The old case-B exterior triangle on A R0 already has
first vertex

\[
Z=(PA)\cap c_{EF}
\]

on that ray. It must be the same Z. In particular Z is triple, because
the kite at B is case B. Call W the new kite's other corner adjacent to B.
It lies on c_BC on the ray opposite C. The cap WZ is c_EF: at the triple Z,
the axes PA and BY already serve as one cap and the kite diagonal, leaving
its existing c_EF axis as the other cap.

Now the exterior triangle on BW must use B's fourth pencil axis BP and
the opposite cap WZ=c_EF. Its apex is necessarily

\[
E=(BP)\cap c_{EF}.
\]

At B the required fourth-axis ray is away from P: the ray toward P lies
between BA and BC, whereas BW points opposite BC and the exterior ray
beside BW is the opposite BP ray. Yet E lies on ray 6 at P, opposite B on
ray 2. B-to-E therefore runs through P. This is the wrong ray, and also
cannot be a bounded triangle edge because P intervenes. Contradiction.

The same argument handles E. Therefore every quadruple first neighbour
of a double-case-B zero-slack P has positive corrected slack. In fact it
has slack at least two: the exhaustive local mask check with three
prescribed consecutive bridge rays has no slack-one mask, and its unique
zero mask is the double-case-B mask just excluded.

## 4. The remaining mixed zero stars form short collinear paths

This reduction uses all quadruple slacks zero and `K_3=K_4=0`, but does
not need `Delta=0` or `pi=6`.

Construct the graph of quadruple first neighbours. Double-case-B stars
are isolated by §3. In an alternating star, at most two bridge neighbours
are quadruple: adjacent quadruple bridge neighbours would put three
quadruple corners in their intervening kite. If there are two, they are
on opposite rays of the same axis. At least one exists by the accepted
opposite-kite far-corner argument.

In a single-case-B star with blocks 0,3,5, the accepted propagation lemma
makes Q4 quadruple. Its kites on rays 3 and 5 then make Q2 and Q6 triple,
since otherwise one would have three quadruple kite corners. Its other
two neighbours Q1,Q7 are the case-B triple corners. Thus Q4 is its unique
quadruple neighbour.

Every nonisolated component is consequently a path on one proper line
H; its interior stars are alternating and its endpoints are alternating
or single-case-B. A cycle is impossible: continuation always uses the
same H and distinct vertices would have to be ordered cyclically on a
proper line. The component has k>=2 vertices.

Its pencils contain exactly 1+3k distinct lines: H, plus three other
axes through each vertex. Any repetition of another axis would intersect
H twice. At each end, extend along H to the first triple boundary vertex;
an alternating endpoint reaches it directly, and a single-case-B endpoint
first crosses its simple case-B centre. The two boundary triples supply
four additional distinct cap lines. Each single-case-B endpoint also
supplies its kite diagonal through its simple centre. All these lines
are distinct from one another and the pencils, since they meet H at
different boundary vertices or centres.

Writing b for the number of single-case-B endpoints gives

\[
n\ge 3k+5+b.
\]

For n=18 the remaining mixed components therefore have k=2,3,4; if k=4,
then b<=1. The other branch is an isolated opposite-double-case-B star.
Its pencil, two kite diagonals, and four cap axes at the two H-boundary
triples use at least ten lines. This is a finite family of cluster types,
not a contradiction: the boundary triples and remaining lines still
need to be shown to force U, corrected slack, or Delta.

## 5. Concrete local solver pins

The residual cases can be pinned using line names rather than opaque
sector sums:

- Isolated double-B: P has mask `BRRRBRRR`; all eight sectors; opposite
  simple kite centres on one pencil axis; six first multiple neighbours
  all triple; both kites are K1B and all eight of their cap segments are
  double. No quadruple first neighbour is permitted.
- Mixed path: choose k in {2,3,4}, a common H, and b endpoint case-B flags
  satisfying `3k+5+b<=18`. Each interior star has alternating four kite
  blocks and its H-neighbours quadruple. Each endpoint has its inward
  H-neighbour quadruple and outward H-neighbour triple, directly for an
  alternating endpoint or after a K1B centre for a case-B endpoint.
  All other first multiple neighbours are triple. All interior kites
  and both inward kites at each endpoint are K2. An alternating endpoint
  has two outward K1A kites; a case-B endpoint has one outward K1B kite.
  K3/K4 are prohibited. Delta=0 pins K2 and K1B cap edges double, and
  exactly one single cap at each K1A. Every all-multiple triangular face
  also has all edges double.

These are suggested necessary constraints for the lead's arrangement
solver, not a supplied SAT implementation or an UNSAT certificate.

## 6. Perfect-line caution and verification

The proposed raw fork assertion, "two simple blocks around a double
bridge force exactly four consecutive sectors at its triple endpoint,"
is false. The main agent found globally triple-optimal counterexamples
among the binding witnesses. Extra lines through the opposite cap
vertices can create a fifth sector. Hence no conclusion that perfect
lines contain no triples is asserted here; any repaired argument must
use actual Delta=0 saturation at those extra multiple cap vertices.

`stage2_quad_check.py` independently reconstructs with accepted Note 3
helpers, checking opposite case-B positions, positive neighbour slack,
and the 7-type slack. Its tiny mask enumeration fixes rays 1,2,3 as
bridges and applies isolation, no-three-consecutive-blocks, case-B
distance-two exclusions, and opposite case-B placement. It finds exactly
80 labelled configurations: slack counts
`{0:1,2:9,3:9,4:21,5:19,6:15,7:5,8:1}`. The unique zero mask is
`B=K=CB={0,4}`. This exhaustively proves the local absence of slack one
under these explicit constraints; it does not enumerate arrangements.

The targeted check used the 29 binding witnesses and the four earlier
datasets (3,445 supplied records), with no 93 reconstruction repeated:

```text
arrangements_checked=2450
skipped_outside_structural_class=1024
quadruples=97
seven_type_points=52
zero_slack_points=6
double_case_B_points=1
double_case_B_quad_first_neighbours=1
globally_zero_slack_quad_arrangements=0
globally_zero_credit_all8_arrangements=0
sample_failures=0
```

The skipped records are explicitly outside the structural class needed
for the local mask arguments. Triple optimality is not a hypothesis of
the new §§1–3 local lemmas, so it is not used as a sample filter. The
double-case-B neighbour claim is exercised once, on a positive-slack
neighbour; no globally zero-slack or zero-credit quadruple arrangement
occurs in this run. These are sample passes and limited coverage, not a
global impossibility proof.

```bash
python -m py_compile work/bbl/stage2_quad_check.py
python work/bbl/stage2_quad_check.py \
  --out work/bbl/all8_work/stage2_quad_summary.json \
  work/eng/oth/wit3/wit_sat.jsonl \
  work/eng/lattice/lattice18.jsonl work/eng/lattice/lattice_family.jsonl \
  work/eng/lattice/mixed_all.jsonl work/phi/gallery18.jsonl
```

The exact output is `all8_work/stage2_quad_summary.json`. The checker does
not assert the unproved perfect-no-triple or raw four-sector-fork claims.

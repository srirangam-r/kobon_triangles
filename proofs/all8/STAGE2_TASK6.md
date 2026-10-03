# Task 6 Stage 2 — alternating zero stars require at least 21 lines

**New conditional hand exclusions: alternating zero stars are impossible
at n=18, and every mixed first-neighbour path has exactly two quadruples.**
The remaining types are an isolated opposite-double-case-B star or a
two-quad path with both endpoints single case B. Stage 2 is not complete.
Stage 1 is outside this subagent's scope.

The assumptions are those of Stage 2: proper pseudolines with one
crossing per pair, multiplicity at most four, the accepted structural
class and triple optimality, every corrected quadruple slack zero,
`K3=K4=0`, `U=0`, and `Delta=0`. We use the accepted Note 3/5 payment
rules and the Task 5 first-neighbour path reduction. No Stage 1 inequality
is assumed or proved here.

## 1. Correction to the old outward-kite pins

An alternating endpoint P has one inward quadruple first neighbour B,
one outward triple first neighbour T on the same axis H, and two other
triple first bridge neighbours A,C on another axis. Its two outward
kites have adjacent triple corners `(A,T)` and `(T,C)`.

Their far corners need not be triple: the first-neighbour graph does
not see a quadruple opposite P across a kite centre. Thus Task 5's pin
"both outward kites are K1A" was not established by its path reduction.
The correct possibilities before saturation are K1A or K2. The fourth
axis at a quadruple far corner can create an exterior triangular face
which is impossible at a triple far corner. We must not use the triple
far-corner proof without this distinction.

The first-neighbour path description and its original baseline line
count `n>=3k+5+b` do not depend on that erroneous far-corner pin and
remain usable. A single-case-B endpoint's outward kite is genuinely
K1B, by the definition of its case-B block.

## 2. A triple far corner gives two surplus single caps

Consider the outward kite `(P,A,R,T)`, with simple centre X, adjacent
corners A,T triple, and far corner R on the proper ray PX beyond X.
Write

\[
c_0=BA,\quad c_1=AT,\quad c_2=TC,\quad c_3=CB
\]

for the star's four cap sides. The accepted far-corner rule gives

\[
R=c_0\cap c_2,
\]

so AR lies on c0 and TR on c2. (Each cap side can contain an intervening
simple kite centre; naming it by its multiple endpoints denotes its
line, not necessarily one bounded edge.)

If R is triple, **both AR and TR are singly used**.

At T, the rays toward P, X, and R are consecutive. The exterior ray
beside TR is therefore H away from P. At the triple R, the exterior
triangle would have to use AR's axis: its other axis through X is the
kite diagonal, lying on the interior side. The alleged exterior apex is
`H intersect c0=B`. But B lies across P from T, on the wrong ray. Hence
TR has no exterior triangular face.

Similarly, at A the exterior ray beside AR is PA away from P. Its
alleged apex is `PA intersect c2=C`; A and C are opposite first bridge
rays at P, so C is again on the wrong ray. Thus AR has no exterior
triangular face either. Each edge has its kite triangle and is single.

The kite is K1A, with P its sole quadruple corner and at least two
single caps. Its payment consumes only one complete endpoint-token
pair. The other pair survives, contributing at least two to Delta_N
by Note 5's accepted surplus-kite lemma. Therefore R cannot be triple
under Delta=0.

This proves the corrected zero-credit pin: **both outward far corners
of every alternating endpoint are quadruple, and both outward kites
are K2 with all caps double.**

## 3. An alternating endpoint needs a new axis beyond its boundary

Keep the same kite, now with R quadruple. Three of its axes are the
diagonal PR and the cap axes c0,c2. Denote its fourth axis by D.

Delta=0 forces all K2 cap edges double, in particular TR. At T the
exterior triangle along TR must use H away from P, as in §2. At R,
using c0 would yield the same impossible apex B across P; the diagonal
through X is on the interior side. Consequently the exterior triangle
can only close using D. Its apex is

\[
Y=H\cap D,
\]

**strictly beyond T on H, away from the path**. This is an ordinary
adjacency/ray-order argument: its side TY has no intervening vertex.
No metric convexity, straight-line theorem, or extra concurrency
assumption is used.

Recall the baseline set of `3k+5+b` lines in a mixed component:

- H and the three other pencil axes through each of its k quadruples;
- the two non-H axes at each of the two triple boundary vertices;
- the kite diagonal at each of its b single-case-B endpoint centres.

Every one of these lines other than H meets H at a path quadruple,
one of its boundary triples, or an intervening case-B centre. These
vertices all lie in the closed interval between the two boundary triples.
But D meets H strictly outside that interval, at Y. Unique pair crossing
therefore makes D distinct from every baseline line.

Thus each alternating endpoint forces at least one additional line.
If both endpoints are alternating, their additional lines are distinct:
one crosses H beyond one boundary, the other beyond the opposite boundary,
and a proper pseudoline cannot cross H twice.

There are `2-b` alternating endpoints, so the corrected line count is

\[
\boxed{n\ge3k+5+b+(2-b)=3k+7.}
\]

For k=4 this is n>=19, a contradiction at n=18. This closes the entire
four-quad mixed-path type, including both possible endpoint patterns:
the old bound already excluded b=2; b=1 needs its alternating endpoint's
one additional line, and b=0 needs the two distinct additional lines.

For k=2 and k=3 the same proof gives n>=13 and n>=16, respectively;
these are not contradictions at n=18.

### An alternating endpoint actually needs three additional axes

The one-axis argument can be strengthened. Write R−,R+ for P's two
outward far quadruples. Each has a mixed K2 block toward P flanked by
two triple bridge neighbours. It cannot be double case B. It cannot be
single case B either: the accepted global single-case-B propagation
makes its central neighbour quadruple, and each non-case-B kite block
adjoins that central quadruple, whereas this kite has both adjacent
corners triple. Thus R−,R+ are alternating zero stars.

At each R, label the block toward P as ray 0. Its adjacent cap rays are
1 and 7, with triple first endpoints. Its fourth axis is therefore on
rays 2 and 6, both block rays. This controls the exterior apex, rather
than merely counting its axis.

At T the rays toward P, its two outward kite centres X−,X+, and the two
far corners R−,R+ are five distinct double rays. The cap toward each R
is opposite the centre ray from the other outward kite. Hence T is a
full six-sector triple. Let V be its first vertex on H away from P.
The exterior triangles on TR− and TR+ both have this same apex V, by
first-ray adjacency. At each R, RV lies on its fourth axis, which has
just been shown to be a block axis. Thus V is simple and both R−V,R+V
are double. The two fourth axes coincide in V's unique non-H axis D.

At V the rays toward T,R−,R+ are three double rays on its two simple
axes, forcing all four sectors. V is a kite centre. Its fourth corner
T', beyond V on H, is multiple by the simple-double-edge rule. It cannot
be quadruple, since its kite already contains R−,R+ quadruple and K3=0.
Thus T' is triple.

There are at least **three** additional lines meeting H beyond the old
boundary T: D at V and the two non-H axes at the farther T'. They are
distinct from each other and the entire baseline, by their different
intersections with H. In particular, a triple exterior apex V would
contradict the alternating block-axis requirement at R±.

## 4. A case-B endpoint needs two new axes beyond its boundary

Let P be a single-case-B endpoint, with outward simple case-B centre X,
far triple T on H, and inward quadruple first neighbour Q. Write A,F
for the two adjacent triple corners of the outward kite. Write B,C for
the next triple first neighbours toward Q, so its two inward K2 kite
diagonals are BQ and CQ. These are distinct and meet H at Q.

The exterior triangles on the far cap edges TA and TF have apices

\[
Y=(PA)\cap(TF),\qquad Z=(PF)\cap(TA),
\]

beyond A and F away from P, respectively.

If Y is simple, its two sides AY and TY are single. An exterior triangle
on TY would require H away from P at T, but Y's other axis PA meets H
at P, on the wrong ray. An exterior triangle on AY would require the
old kite diagonal AXF at A away from X, but its intersection with YT's
cap axis TF is F, again on the wrong ray (through X). Thus the triangle
TAY has two single simple-adjacent sides and supplies the accepted O*
residual tokens. Delta=0 forbids this. Similarly Z cannot be simple.

Consequently Y,Z are multiple, and the all-multiple triangles TAY,TFZ
have all edges double. Together with the original case-B kite and its
near exterior faces, this makes each of A,F,T a full six-sector triple.
For example at A the five rays toward P,X,T,B,Y are all double; those
five rays force all six sector bits. The same count applies at F and T.

In particular T has a double first segment TV on H away from P. Suppose
only one arrangement line E crosses H beyond T. All baseline lines meet
H inside the boundary interval, so E is an additional line. Its crossing
V with H is simple and is H's last vertex on that end. Hence V has exactly
the two triangular sectors beside VT, an I centre at T. Its other axis
is E, and its two first cap neighbours are precisely Y,Z; VY,VZ are
single. A zero-slack quadruple is all-8 and cannot have such a single
first ray, so Y,Z must be triple. Their third axis is E.

Since A is full, its first ray on AXF away from X has a vertex U and
the two faces AYU and ABU. At B the exterior neighbour of BA is its
mixed-kite diagonal BQ, on the ray away from Q. Thus

\[
U=(AXF)\cap(BQ).
\]

The triangle AYU, on the side of AY opposite TAY, must use Y's third
axis E; hence U also lies on E. The identical argument at F yields

\[
U'=(AXF)\cap(CQ)\in E.
\]

These vertices are distinct: if they coincided, BQ and CQ would meet
the old diagonal AXF at their unique mutual crossing Q, but AXF meets
H at X, not Q. Thus E meets AXF at two distinct vertices, a contradiction.

Therefore **at least two distinct arrangement lines cross H beyond T**.
Both are additional to the baseline. The argument allows those lines
to meet H at the same multiple vertex; it counts lines, not crossing
vertices. Additional axes for the opposite endpoint are distinct because
they cross H beyond the opposite boundary.

Combining one extra line for each alternating endpoint with two for each
case-B endpoint gives the stronger uniform conditional count

\[
\boxed{n\ge3k+5+b+(2-b)+2b=3k+7+2b.}
\]

In particular k=3,b=2 requires n>=20 and is excluded at n=18. The
remaining three-quad cases require n>=16 for b=0 and n>=18 for b=1;
the latter has an exact line inventory but no contradiction here. For
k=2 the bounds are 13,15,17 for b=0,1,2 respectively.

Replacing the alternating endpoint's one line by the three just proved
gives the final uniform conditional count

\[
\boxed{n\ge3k+5+b+3(2-b)+2b=3k+11.}
\]

Thus **k=3 requires at least 20 lines and k=4 at least 23**, independently
of endpoint types. Both mixed-path types are excluded at n=18. A two-quad
path needs at least 17 lines, leaving only one line beyond its required
baseline/boundary inventory, but no contradiction is supplied for it.

The first part (simple external apex gives two single sides) also applies
to an isolated double-case-B star's two outer far triples. The same
one-extra-line contradiction applies there with BQ,CQ replaced by the
two cap axes meeting the opposite far triple on H. This gives at least
four additional axes beyond its ten-line baseline, so n>=14. It is not
an exclusion at n=18.

## 5. Other rigorous constraints, not completed exclusions

Choose the globally earliest quadruple in any allowed wiring sweep.
It cannot be alternating at Delta=0. Its quadruple first neighbours
would have to be right-going; opposite neighbours cannot both be so,
making it an alternating endpoint. Its outward H-ray is left-going.
Among the two adjacent outward kite rays at least one is left-going,
since the left-going rays form four consecutive rays at a quadruple.
That kite's far corner precedes P, so is triple by the choice of P.
Section 2 gives positive residual credit. The same argument after
reversing the sweep shows that the latest quadruple is also case-B type.
This does not exclude every alternating endpoint: its outward far
quadruple can belong to another, earlier component.

There is also a useful cycle restriction. At an outward quadruple R
of an alternating endpoint, its mixed K2 block is flanked by the two
triple bridge neighbours A,T. R cannot have the double-case-B zero mask.
The accepted single-case-B propagation makes that mask's central first
neighbour quadruple; each non-case-B kite would adjoin that quadruple,
which is impossible for this kite with both adjacent corners triple.
Thus R is alternating. Of its two remaining first bridge neighbours,
at least one is quadruple by the accepted far-corner argument; both
cannot be, because they adjoin a common kite and would make K3. Therefore
R is itself an alternating endpoint.

Under Delta=0 every alternating endpoint has two distinct outward
quadruple kite corners. The same shared kite is outward at each end.
Hence the graph joining opposite quadruple corners of those outward
K2 kites is a simple graph of degree two on the alternating endpoints:
its components are cycles of length at least three. The stronger boundary
construction in §3 supplies the third outward K2 kite linking R−,R+.
Every component is therefore a **triangle** of alternating endpoints.
Its three vertices belong to three distinct first-neighbour components:
a pair already shares its kite axis and cannot share another axis H.
This is a necessary pin, not itself a parity contradiction. Proper line
extensions beyond the quadruple vertices prevent importing Note 3's
bad-wedge cycle argument.

## 6. Alternating endpoints require at least 21 lines

The preceding boundary construction closes more than long first-neighbour
paths. Suppose there is an alternating endpoint P. Its two far quadruples
and the new outward kite centre V form its opposite-K2 triangle. Name the
triangle's quadruples P1,P2,P3 and its central full triple T. Each of its
three edge kites has T as one opposite triple corner and another triple
as its other corner.

We first identify the first-neighbour axes correctly. An initial far
quadruple R has adjacent triple bridge neighbours A,T. Its possible
quadruple first neighbour lies opposite A or opposite T. The newly forced
outward kite at V makes the neighbour opposite A the farther triple T'.
Thus the quadruple first neighbour is necessarily opposite T. Applying
this around the triangle shows that each Pi has its first-neighbour path
axis

\[
H_i=TP_i,
\]

and its inward quadruple neighbour Bi on the ray of Hi **away from T**.
The three Pi belong to different first-neighbour components: a pair
already shares its kite axis and cannot also share another proper axis.
Since k>=3 is excluded by `n>=3k+11`, each Pi--Bi component has k=2.
Each Bi is an alternating or single-case-B endpoint.

The central triangle has nine distinct axes:

\[
\mathcal L_0=\{H_1,H_2,H_3\}\cup
             \{P_1P_2,P_2P_3,P_3P_1\}\cup
             \{K_1,K_2,K_3\},
\]

where Ki is Pi's fourth pencil axis, besides Hi and its two kite-edge
axes. Any coincidence between axes belonging to two Pi would make their
shared line their already distinct kite-edge axis. The three Hi are
distinct at T, and none of the edge or Ki axes contains T. This proves
the nine axes are distinct; it uses only one crossing per pair.

For a fixed Hi, every axis of this nine-line set other than Hi meets Hi
at one of these vertices:

- Pi, for its two incident kite-edge axes and Ki;
- T, for the other two Hj;
- the simple centre Vi of the opposite edge kite, beyond T away from Pi;
- the farther triple T'_i, for the other two Kj,Kk, also beyond T away
  from Pi, since T'_i is the fourth corner of that opposite edge kite.

Thus **none of the other eight central axes crosses Hi beyond Pi away
from T**.

On that outer ray, the component Pi--Bi contributes at least eight
distinct non-Hi axes:

1. The three other pencil axes at Bi.
2. The two non-Hi axes at its outer boundary triple Ti.
3. If Bi is alternating, at least three additional axes beyond Ti by
   §3. If Bi is single case B, its centre's kite diagonal plus at least
   two additional axes beyond Ti by §4, again three.

These eight axes are distinct by their Hi intersections: at Bi, at Ti,
at the possible case-B centre, or strictly beyond Ti. None is central,
by the preceding inventory. Across the three rays this gives at least
24 distinct **line/ray incidences**, not a claim of 24 different lines.

At the full triple T the rays toward P1,P2,P3 alternate; its other three
rays point toward the three simple edge-kite centres. Any line outside
the central set is outside T's three-axis pencil and meets exactly
three consecutive rays at T, by the accepted pencil half-ray lemma.
Such an interval contains at most two of the three alternating selected
rays. Hence any new line can supply at most two of those 24 incidences.
At least twelve new lines are required, besides the nine central axes:

\[
\boxed{n\ge9+24/2=21.}
\]

This contradicts n=18. **No alternating endpoint exists.** A nonendpoint
alternating star would be an interior vertex of a path of length at
least three, already excluded by §4. Therefore there are no alternating
zero-slack quadruples anywhere in the n=18 zero-credit regime.

The surviving global quadruple components are exactly isolated
opposite-double-case-B stars and two-quad single-case-B--single-case-B
paths. Their lower line counts are 14 and 17, respectively. Those
counts alone do not exclude them at n=18.

## 7. Checker scope and exact output

`stage2_note6_check.py` keeps triple and quadruple far corners separate.
For an actual triple far corner it checks the two single caps; for an
actual quadruple far corner with double TR it checks that its fourth
axis meets H beyond T. It also exhaustively checks the local zero-mask
step for a mixed kite block with two prescribed triple neighbours,
using the accepted single-case-B central-neighbour propagation. Its
unique remaining mask is alternating.

The input is the 29 saved binding witnesses, four earlier datasets,
and five saved/extended cores: the ten-line isolated double-B core,
its n=18 extension, CORE10 and its n=18 extension, and PARITY12. These
core checks preserve their actual eligibility; no triple-optimality
claim is made for the isolated double-B core.

The initial targeted run checked 2455 structural-class arrangements
and skipped 1024 outside the structural class. It encountered **zero
alternating endpoint stars of the required zero-slack type**. Thus the
new hand boundary lemmas have no positive sample coverage in this
cohort; the mask check is exercised, but no sample pass is advertised
as a proof of the k=4 exclusion.

The final checker also tests the simple external-apex lemma at every
case-B kite, whether or not its quadruple has zero corrected slack.
Unlike the alternating-endpoint branch, this has actual saved-core
coverage. The exact final counts are in the summary below.

```text
arrangements_checked=2455
skipped_outside_structural_class=1024
alternating_endpoint_stars=0
case_B_kites=7
case_B_simple_external_apices_two_single_caps=8
case_B_multiple_external_apices=6
failures=0
mixed_zero_mask_check: unique survivor BRBRBRBR, no case B
```

Final command and output:

```bash
python -m py_compile work/bbl/stage2_note6_check.py
python work/bbl/stage2_note6_check.py \
  --out work/bbl/all8_work/stage2_note6 \
  work/eng/oth/wit3/wit_sat.jsonl \
  work/eng/lattice/lattice18.jsonl work/eng/lattice/lattice_family.jsonl \
  work/eng/lattice/mixed_all.jsonl work/phi/gallery18.jsonl
```

`all8_work/stage2_note6/summary.json` and `boundary_details.json` contain
the exact counts and any exercised local instances. There is no SAT
certificate here. The hand proof in §§2–3, under the explicit zero-credit
hypotheses, is the reason the four-quad type is excluded.

The remaining hand obligation is the isolated double-case-B boundary
or a two-quad single-case-B--single-case-B path.
Extra multiple cap vertices force the outward boundary triples full,
but the new line count still leaves enough axes in these remaining cases.

## 8. Short final push on the surviving two-quad type

For a single-case-B--single-case-B path, the baseline has thirteen lines:
H and six other quadruple pencil axes, four boundary-triple cap axes,
and two old case-B kite diagonals. The boundary proof adds at least
two lines on each outer H-ray, giving seventeen. At n=18 there is only
one line beyond this required inventory. This is a concrete tight
line inventory for the lead's remaining solver case.

It is not safe to assert that exactly two axes crossing H beyond a
boundary T must concur. If their H crossings V,W are simple and ordered
after T, TV can be a three-fan block: one other double block VY, a
single continuation VW, and a single outer cap YW. U=0 does not by
itself exclude this, since the continuation is used, not unused.
The central three-fan cap TY may be double, so H* gives no free tokens;
the Y-end token on YW can be consumed by its legitimate old outer
three-fan payment. A terminal wedge or an unused-slot end at W then
requires further global end analysis. This is a local obstruction to
the proposed concurrence shortcut, not a claimed global zero-credit
arrangement or a counterexample to the desired theorem.

No hand contradiction for that seventeen-line inventory, or for the
isolated double-B fourteen-line inventory, is supplied in this report.

# All-8 Note 6 — closing the long paths and all alternating endpoints

**New hand exclusions in Stage 2:** every mixed first-neighbour path
with k>=3 quadruples is impossible at n=18, and every alternating
endpoint is impossible at n=18. The remaining zero-credit shapes are
an isolated opposite-double-case-B star, or a two-quad path whose two
endpoints are single-case-B. **The complete proof is still open:**
Stage 1 (B) is not proved, nor are those two remaining Stage 2 shapes
excluded. No new SAT/UNSAT certificate is claimed here.

The lead's `SOL_TASK6.md` accepts the Task 5 reductions and asks for a
closed stage or hand boundary cases. The existing user-authorized
Stage 2 subagent continued only that work, while the main agent pursued
the allocation/locality route. We developed and cross-audited the hand
counts below. Detailed Stage 2 notation and verification are in
`STAGE2_TASK6.md`. These new proofs await the lead's review.

## 1. Setting, and an important correction to the old solver pins

Use the accepted identities

\[
\Lambda=288-3T=\pi+E/2,\qquad
E=2U+C_q+\Delta_Z+\Delta_N,
\quad C_q=\sum_P S_P^\circ+2K_3+4K_4,
\]

with `pi=18-W`, W counting bad-wedge vertices. Stage 1 seeks

\[
J\le E+\pi+\sigma,                                    \tag{B'}
\]

where J counts two-W-end lines and sigma counts isolated wedge-forest
lines. This is exactly B, since `J=18-2*pi+sigma`.

All Stage 2 proofs below are **conditional** on

\[
U=0,\quad S_P^\circ=0\text{ at every quadruple},\quad
K_3=K_4=0,\quad\Delta=0.                              \tag{Z}
\]

They use the proper-pseudoline, pairwise-one-crossing setting and the
accepted structural/optimality class. B would reduce a 94 to Z with
pi=6; that reduction remains unproved. The new hand counts themselves
do not need pi=6 or the six wedge paths.

Task 5's first-neighbour graph remains valid: nonisolated quadruple
components are collinear paths; their interior stars are alternating,
and their endpoints alternating or single-case-B. Double-case-B stars
are isolated. Its baseline distinct-line count is

\[
n\ge3k+5+b,                                           \tag{4}
\]

with b the number of single-case-B endpoints. All baseline lines meet
the path axis H at a path quad, a boundary triple, or a case-B centre,
inside the closed interval between the two outer boundary triples.

**Correction:** an alternating endpoint's outward kite far corner was
not proved triple. It can be quadruple, and then the kite is K2 with
opposite quad corners. That corner is not connected to the endpoint
in the *first-neighbour* graph, because a simple kite centre intervenes.
Thus the old outward-K1A pin was too strong. A fourth axis at the far
quad can close a face forbidden at a triple far corner. Any SAT result
using the old pin must be interpreted for that restricted model, not
as an exclusion of the whole path type.

The corrected analysis below first rules out the triple far corner
under Z, then uses the required extra axes at the quadruple far corner.

## 2. Alternating boundary: triple far corners leave surplus

Let P be an alternating endpoint. Its inward first neighbour B is
quadruple; its outward neighbour T on H is triple. Its two other first
bridge neighbours A,C are triple and opposite on one axis through P.
Write the star cap lines as

\[
c_0=BA,\quad c_1=AT,\quad c_2=TC,\quad c_3=CB.
\]

These are supporting lines: a cap side can contain a simple kite
centre between its named multiple endpoints. Consider the outward
kite `(P,A,R,T)`, with centre X. The accepted far-corner rule gives

\[
R=c_0\cap c_2.
\]

**Lemma. If R is triple, AR and TR are both single.** At T the exterior
ray beside TR is H away from P. At R the only exterior cap axis is AR:
the diagonal through X points into the kite, and its intersection with
H is P, with X intervening. The other candidate apex is
`H intersect AR=B`, across P from T. It is on the wrong ray. Thus TR
has no exterior triangle. At A the analogous apex is
`PA intersect TR=C`, opposite A across P. Hence AR is single too.
This uses triple ray adjacency and unique line intersection, not
straightness or angle inequalities.

The kite is K1A. Only one single-cap endpoint-token pair is spent by
its payment; the second survives. Thus `Delta_N>=2`. Under Z, R must
instead be quadruple. Both outward kites are consequently K2 with
opposite quad corners, and **all their caps are double**.

This lemma deliberately does not apply the triple-corner argument
when R is quadruple. There its fourth axis is a new candidate.

## 3. Alternating boundary: three new lines, not just one

Let R+,R− be the two outward far quads. At either R, its mixed kite
block toward P is flanked by the two triple bridge neighbours at that
kite's adjacent corners. R cannot be double-case-B. It cannot be
single-case-B either: the accepted central-quad propagation would put
a quad next to every non-case-B kite there, whereas this kite has two
adjacent triple corners. Hence R is alternating. Its two remaining
bridge directions cannot both have quad first neighbours, since that
would create K3 in their intervening kite. At least one does by the
accepted far-corner argument. Therefore R is an alternating endpoint.

At R three axes are already fixed: its diagonal RP and the two cap
axes RA,RT. Its fourth axis D is a **block axis** in its alternating
mask. Since TR is double, its exterior triangle at T uses H away from
P. At R the old cap RA would give the wrong apex B, and the diagonal
RP would give P. The face must therefore close at

\[
V=H\cap D,\qquad V\text{ beyond T away from P}.
\]

V is the first vertex of R on that block ray, so V is **simple**.
The two outward cap faces have the same V, since it is the first
H-vertex beyond T. Thus their fourth axes coincide in one line D,
with R+,V,R− on that line.

At T, the rays to P, the two old kite centres, and R+,R− are five
double rays; they force all six sectors and hence TV double. At V,
TV and both VR± are double, forcing all four sectors. Therefore V
is a kite. Its next H-corner T' beyond V is multiple; K3=0 forces
T' triple, since the other two corners R± are quadruple.

The line D at V and the two non-H axes at T' are three distinct lines
crossing H strictly beyond the original boundary T. None is a baseline
line of (4). Axes forced beyond opposite endpoints are distinct because
one proper line cannot cross H twice.

**Conclusion:** each alternating endpoint needs at least **three**
additional lines. Also P,R+,R− are the three corners of an
opposite-K2 triangle, not merely an unconstrained mutual cycle.

## 4. Case-B boundary: at least two additional lines

Here P is a single-case-B endpoint, Q its inward quad neighbour, X
its outward case-B kite centre, and T the far triple on H. Its outward
kite is `(P,A,T,F)`, A,F triple. Let B,C be the next triple first
neighbours toward Q; the inward-kite diagonals BQ,CQ meet at Q.
The old exterior faces along TA,TF have apices

\[
Y=(PA)\cap(TF),\qquad Z=(PF)\cap(TA).
\]

If Y were simple, AY and TY would both be single. An exterior TY
triangle would use H away from P, but its candidate meets H at P.
An exterior AY triangle would use the old diagonal AXF away from X,
but that diagonal meets TF at F on the wrong ray. Thus TAY would
have two single sides at its simple corner, leaving the Note 5 O*
tokens. Z is excluded symmetrically. Under Z, Y,Z are multiple.

All edges of the all-multiple triangles TAY,TFZ are double. Combined
with the existing case-B faces this makes A,F,T full six-sector
triples. In particular T's first outgoing H-segment TV is double.

Suppose only one arrangement line E crosses H beyond T. Its crossing
V is simple and last on H, hence an I centre at T. Its cap neighbours
are Y,Z and VY,VZ are single. Zero-slack quads are all-8 and cannot
have a single first ray, so Y,Z are triple and their third axis is E.

Full A supplies the two faces AYU and ABU on its old diagonal AXF
away from X. At B the required axis is BQ, so

\[
U=(AXF)\cap(BQ)\in E.
\]

Membership in E follows from the exterior AY face at the triple Y.
Full F likewise gives

\[
U'=(AXF)\cap(CQ)\in E.
\]

U and U' are distinct: BQ and CQ meet at Q, whereas AXF meets H at
X, not Q. Thus E would cross AXF twice. Contradiction. At least two
distinct lines cross H beyond T, additional to the baseline.

This counts lines, not vertices; two such lines may meet H concurrently.
The same argument applies to each end of an isolated double-case-B
star, replacing BQ,CQ by the two caps meeting the opposite far triple
on H. That star needs at least `10+4=14` lines, not yet a contradiction.

## 5. Closed: every mixed path with k>=3

Combining (4) with three extra lines per alternating end and two per
case-B end gives the new conditional bound

\[
\boxed{n\ge3k+5+b+3(2-b)+2b=3k+11.}                   \tag{5}
\]

Consequently k=3 needs at least 20 lines and k=4 at least 23. **Both
entire path types are excluded at n=18**, for all endpoint choices.
A two-quad path needs at least 17; the line count alone does not close it.

The excluded branches are proved by the hand boundary counts, not by
the absence of matching sample arrangements or a claimed SAT result.

## 6. Closed: all alternating endpoints at n=18

Suppose an alternating endpoint exists. Sections 2–3 construct three
quad alternating endpoints P1,P2,P3 around a full central triple O.
They are joined pairwise across the three opposite-K2 kite centres.
Let `H_i=OP_i` and let K_i be the other bridge axis at P_i.

An incidence detail is important. At a far quad R, the original kite
initially leaves two possible inward directions. The new kite at V
makes the opposite-A bridge neighbour the far triple T'; it cannot
be the inward quad neighbour. Thus the first-neighbour path at R
is on RO. So each P_i's inward quad B_i lies on H_i **away from O**.

There are exactly nine distinct central pencil axes:

- the three H_i through O;
- the three axes of the opposite-K2 edges P_iP_j;
- the three other bridge axes K_i.

They are distinct because two lines through different P_i,P_j would
already share those points with their cycle-edge axis. For each fixed
H_i, every other central-axis crossing lies at P_i or toward O:
the other H's meet it at O, the opposite cycle edge at its kite centre
V_i beyond O, and the other K's at the far triple T'_i beyond V_i.
**None of these nine axes crosses the ray beyond P_i away from O.**

By §5, each component P_i--B_i is now a two-quad path. On the selected
ray of H_i beyond P_i it requires at least eight distinct non-H axes:

1. three other pencil axes at B_i;
2. two axes at that path's outer boundary triple;
3. if B_i is alternating, three additional axes beyond that boundary;
   if B_i is case-B, its centre diagonal and two additional boundary
   axes instead.

These eight are distinct on this ray and none belongs to the nine
central axes. Hence the three selected rays require at least 24
incidences with **new** arrangement lines.

The selected rays OP1,OP2,OP3 alternate around the six-ray pencil at
O: its other three rays are blocks to the opposite-edge kite centres,
and triple blocks cannot be consecutive. An outside line crosses
three consecutive pencil rays (the accepted half-pencil lemma), so
it can meet at most two selected rays. It follows that at least
`24/2=12` new lines are required, in addition to the nine central axes:

\[
\boxed{n\ge9+12=21.}                                  \tag{6}
\]

This contradicts n=18. **Every alternating-endpoint subtype is now
excluded.** Interior-only alternating paths cannot survive either,
since a finite nonisolated path has endpoints. Thus the only remaining
mixed type is a two-quad path with two single-case-B endpoints.

## 7. Stage 1: proved payment locality, a sharper Hall target

This section does not assume Z. Let C be a bridge/mutual component
of multiple vertices: double bridges join their ends, and origins at
a common three-/four-fan simple centre are joined.

**Payment-locality lemma.** Every accepted old/new N payment charged
to an origin or kite in C takes its token at a multiple vertex in C.
For an outer-triangle payment the token is either at its origin P,
or at T when PT is a double bridge, which joins P,T. The same holds
for the quad U/I reservation. At a K0 or case-A K1, all kite corners
are joined through their common four-fan centre. Three-fan origins
are joined likewise. End-token removal is local to its multiple root.
Thus there is no need to enlarge these components merely to keep
the payments local.

Let `d_C` be the number of actual bounded residual N tokens rooted
in C, so `sum d_C=Delta_N`. Put

\[
M_C=U_C+I_C+d_C.                                      \tag{7}
\]

These are C's **flexible** resources: one origin label per U/I block
and its residual tokens. Give every U/I block its separate cap label,
which is permitted to pay only its own cap line. Let A_UI be the set
of all U/I cap lines, and let

\[
D_C=\{L\in Q_0:\ L\text{ contains a vertex of }C,
                         \ L\notin A_{UI}\}.
\]

The sharper local candidate is

\[
\boxed{|D_C|\le M_C\quad\text{for every component }C.} \tag{LC}
\]

**LC is unproved.** Payment locality alone does not establish enough
capacity; deleting that distinction would repeat the gap in Stage 1.

**Conditional Hall theorem (proved).** LC implies O2Q and Hall's
condition even with cap labels fixed to their own cap lines.

First cover every demanded U/I cap line with one of its own cap labels.
Different lines take distinct labels. Any remaining Q0 line meets a
multiple point: if it had only simple vertices, L1 excludes doubles,
so it would be a perfect line; Note 3 parity would force a U/I cap
step, contrary to its being outside A_UI. Assign each remaining line
to one component it meets. Component C receives at most `|D_C|` lines;
by LC its origin labels and residual tokens can pay them injectively.
Resources of different components are disjoint. This constructs the
full injection, and hence proves Hall for every subset of demands.

This reachability is a **subset** of Note 5's bridge/mutual rule: no
cap label is moved through unrelated components on its cap line.
The original larger reachability is therefore unnecessary *if LC
can be proved*. Even this would leave end reconciliation for B.

## 8. New Stage 1 checks: a narrower allocation passes all samples

`note6_check.py` reconstructs the accepted residual set and tests:

- `cap_strict`: origin labels and N tokens move in their native
  bridge/mutual component; each cap label stays on its cap line;
- `native_pool`: additionally allow a cap label to pay a pencil
  line of its origin's component;
- the local capacity LC, and the stronger variant removing only
  cap lines whose blocks originate in C;
- the total native capacity `2(U_C+I_C)+d_C` against C's Q0 pencil
  lines and its Q0 pencil-plus-native-cap footprint.

| Cohort | Records / eligible | Components, all / eligible | cap_strict failures | LC failures |
|---|---:|---:|---:|---:|
| 93 | 14376 / 13718 | 17614 / 16027 | 0 | 0 |
| Earlier datasets | 3445 / 2259 | 9334 / 2255 | 0 | 0 |
| Binding witnesses | 29 / 29 | 59 / 59 | 0 | 0 |

Both allocation schemes and every listed local candidate have zero
failures on these cohorts. Minimum LC slack is zero in the 93/earlier
cohorts and one in the binding cohort. These tests are new candidates,
not a rerun claiming to prove B from its automatic 93 passes.

Sample-sharp example: 93 record 1 has one triple component, U_C=2,
I_C=d_C=0, and two demanded pencil lines plus two cap-only lines.
Its two origin labels cover the pencil lines and two cap labels cover
the caps. Native footprint slack and LC slack are zero. Exact word
and injection: `all8_work/note6_93/all_footprint_minimum.json`.

The main checker's alternating-K1 branch has zero exercised kites
in these inputs. The Stage 2 checker likewise encounters no zero-slack
alternating endpoint star. The hand proof, not these empty branches,
supports §§2–6.

## 9. Exact outputs, verification, and the remaining obligations

New main outputs are

```text
all8_work/note6_93/summary.json; records.jsonl (14376 records)
all8_work/note6_gallery/summary.json; records.jsonl (3445 records)
all8_work/note6_witnesses/summary.json; records.jsonl (29 records)
asserted_failures=0 in all three
```

They save per-component lines, actual native/flexible capacities, both
matching injections, and minimum words. Sources overlap, so the tables
are not a count of distinct arrangements across cohorts.

The Stage 2 targeted checker uses the earlier 3474 supplied records
plus five saved/extended cores. It checks 2455 structural-class
arrangements and explicitly skips 1024 outside the class. Its local
mask check leaves exactly the alternating zero mask for a mixed block
with two prescribed adjacent triple neighbours. It also tests the
simple-apex lemma on actual case-B kites; exact final counts are in
`all8_work/stage2_note6/summary.json`, with local details in
`boundary_details.json`. No globally zero-credit all-8 certificate or
SAT result is generated by these sample checkers.

Reproduce from the repository root:

```bash
python3 -m py_compile work/bbl/note6_check.py \
  work/bbl/stage2_note6_check.py
python3 work/bbl/note6_check.py \
  work/bbl/all8_work/tradeoff_rebuilt93/metrics.jsonl \
  --out work/bbl/all8_work/note6_93
python3 work/bbl/note6_check.py \
  work/bbl/all8_work/tradeoff_gallery/metrics.jsonl \
  --out work/bbl/all8_work/note6_gallery
python3 work/bbl/note6_check.py \
  work/bbl/all8_work/tradeoff_all8_witnesses/metrics.jsonl \
  --out work/bbl/all8_work/note6_witnesses
python3 work/bbl/stage2_note6_check.py \
  --out work/bbl/all8_work/stage2_note6 \
  work/eng/oth/wit3/wit_sat.jsonl \
  work/eng/lattice/lattice18.jsonl work/eng/lattice/lattice_family.jsonl \
  work/eng/lattice/mixed_all.jsonl work/phi/gallery18.jsonl
```

Stage 1 still requires a proof of LC (or another Hall/direct-B argument)
and reconciliation. The exact missing balance remains

\[
c+r=E-18+3\pi,\quad
c=2I+2U+\Delta_N-Q_0,\quad
r=\pi+\sigma+\Delta_Z+C_q-2I-(J-Q_0).
\]

The shortcut `r>=0` stays refuted by Note 5's eligible record 8383.
Even a proof of O2Q cannot discard its unused slack or turn I labels
into new E-credit.

**Reduced Stage 2 hand/SAT workload:** only the isolated double-case-B
star (now requiring n>=14) and the two-quad, two-case-B-end path
(requiring n>=17) remain. New pins for the latter include multiple
far-cap exterior apices, full six-sector boundary triples, and at
least two distinct axes crossing H beyond each boundary. E=0 saturation
and U=0 must be enforced on those extra axes, not just inside the star.
Neither remaining type is excluded by this note. The six wedge paths
have not yet been used to finish them. Thus `K(18)=93` is not claimed.

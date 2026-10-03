# Task 7 Stage 2 — the B–B path is excluded; stronger star pins

**New hand result: the two-quad single-case-B/single-case-B path is
impossible. Only the isolated opposite-double-case-B star remains in
Stage 2.** The first H-vertex beyond either far case-B triple must now
be multiple. This is stronger than merely requiring two further axes.
The isolated star itself is not excluded; Stage 1 is outside this track.

The existing Stage 2 subagent developed the cap-continuation argument,
the B–B contradiction, the multiple-apex argument, and the targeted
checker. The main agent independently audited those arguments and
assembled this report. These new proofs await the lead's review.
No new SAT or checked UNSAT certificate is claimed.

## 1. Assumptions and accepted inputs

There are 18 proper pseudolines, each pair crossing once, multiplicity
at most four, in the accepted structural/optimality class. The zero
corner assumptions are

\[
 U=0,\quad\Delta=0,\quad S_P^\circ=0\text{ for every quad},
 \quad K_3=K_4=0.
\]

Task 6's accepted hand proofs exclude long mixed paths and all
alternating endpoints. Thus every remaining quad cluster is either
an isolated double-case-B star or a two-quad path with two single-B
endpoints. At a single-B endpoint its case-B axis is the path axis H,
pointing outward. Its other bridge neighbours are triple. All mixed
kite caps are double under zero residual credit.

For a case-B kite `(P,A,T,F)` with centre X, all its corners except P
are triple. Its far exterior apices are

\[
 Y=(PA)\cap(TF),\qquad Z=(PF)\cap(TA).
\]

Accepted Task 6 proves Y,Z multiple, all edges of TAY and TFZ double,
and A,F,T full six-sector triples. The existing solver full-corner
pin implements some of these consequences. We use them, not a claim
that every arbitrary case-B kite has full corners without zero credit.

## 2. Proved: triple-cap continuation

**Lemma.** Let V be a triple corner of a kite `(M,V,N,O)` with simple
centre X. If the cap VM has an exterior triangle with apex E, then
E lies on VN's axis, beyond V away from N.

The rays VM,VX,VN are consecutive: the kite supplies triangles MVX
and NVX. At a triple the six cyclic rays are

```text
VM, VX, VN, -VM, -VX, -VN.
```

The exterior sector beside VM uses `-VN`, not either diagonal ray.
Thus its apex belongs to VN and lies on the opposite ray from N.
There is no fourth axis to provide another candidate. This is a
local cyclic-order proof, valid for pseudolines, not a metric angle
or straight-line argument. The symmetric statement holds for VN.

The checker exercises 975 actual triple-cap continuations. This
supports the local lemma, not the existence or exclusion of a sampled
global B–B path.

## 3. Proved: the two-quad B–B path is impossible

Suppose P,Q are its two quads on H. Write T_L,T_R for their outward
case-B far triples, on opposite sides of the path. At P number the
single-B rays so the case-B block is ray 0 and the other kite blocks
are rays 3 and 5. Its first bridge neighbours are

```text
ray1 A; ray2 B; ray4 Q; ray6 C; ray7 F.
```

The outward case-B kite is `(P,A,T_L,F)`. The inward mixed kites are
`(P,B,R,Q)` and `(P,Q,S,C)`. Their opposite corners R,S are first
bridge neighbours of Q, hence triple by the accepted zero-path
reduction (equivalently, K3=0 forbids a third quad in either kite).

At Q its outward kite is `(Q,E,T_R,G)`, with E adjacent to R and G
adjacent to S in Q's bridge order. Because both quads are all-8, the
following are actual triangular faces, not merely named incidences:

\[
 PAB,\quad PFC,\quad QRE,\quad QSG.
\]

Apply §2 four times to the first chain.

1. At A, PAB is exterior to cap PA of P's outward kite. Thus B lies
   on AT_L, beyond A away from T_L.
2. At B, the same PAB is exterior to PB of the mixed kite `(P,B,R,Q)`.
   Thus A lies on BR, beyond B away from R.
3. At R, QRE is exterior to QR of that mixed kite. Thus E lies on RB,
   beyond R away from B.
4. At E, QRE is exterior to QE of Q's outward case-B kite. Thus R
   lies on ET_R, beyond E away from T_R.

Consequently the one supporting cap line has order

\[
 T_L\;--\;A\;--\;B\;--\;R\;--\;E\;--\;T_R.
\]

In particular it contains both T_L and T_R. It is not H, since AT_L
is a non-H cap at the triple T_L. Yet H also contains both distinct
vertices T_L,T_R. Two proper pseudolines would cross twice. Contradiction.

The other chain through F,C,S,G gives the same contradiction on a
second cap line, but is not needed. Kite-centre subdivisions on the
diagonals do not affect this argument: §2 uses the cap ray, never
the diagonal across an intervening centre.

**Conclusion:** the complete two-quad B–B type is excluded under the
Stage 2 assumptions. It does not need the 17-line inventory or the
six bad-wedge paths. ∎

## 4. Proved: the first outer H-apex V is multiple

This argument applies to either end of an isolated double-B star;
it also applies to the already excluded path boundary. Use the
outward kite `(P,A,T,F)` and apices Y,Z from §1. Let D0 be its old
diagonal AXF.

Full A and F force their next diagonal vertices U,U', away from X.
For a star, let b,c be the distinct old cap axes meeting the opposite
far triple T' on H. For a path they are the mixed-kite diagonals BQ,CQ.
The accepted Task 6 continuation argument gives

\[
 U=D0\cap b,\qquad U'=D0\cap c,
\]

and faces AYU,FZU'. These two vertices are distinct: b,c meet at T'
(or Q), whereas D0 meets H at X, a different vertex.

Since T is full, its first H-vertex V beyond T exists, TV is double,
and the exterior triangles on TY,TZ have this same apex V.

Suppose V simple. Then Y,V,Z lie on its unique non-H line E.

**If both Y,Z are triple,** E is the third axis at each. Face AYU
must use E at Y: its old other cap intersects D0 at F, on the wrong
ray from A. Similarly FZU' uses E at Z. Thus both U,U' belong to E,
which would meet D0 twice. Impossible.

**If one is quad,** its double segment to simple V is a block. All
zero-quad blocks end at kite centres, so V must be a kite, with
corners `(T,Y,W,Z)` and W beyond V on H. If the other side corner,
say Z, were triple, the kite cap ZW would use Z's remaining axis PF.
Then W would be `PF intersect H=P`, behind T and V, not beyond V.
This is the wrong ray. Hence both Y,Z are quad.

Now K3=0 forces W triple. At Y and Z the mixed K2 block toward V is
flanked by triple first neighbours T,W. The accepted Task 6 mask
lemma makes both quads alternating zero stars, already excluded at
n=18. This is impossible too.

All simple-V possibilities are excluded. Therefore **V is multiple**.
It can be triple or quad; this proof does not justify pinning one
multiplicity unconditionally. ∎

This repairs the former concurrency gap using the global alternating
exclusion. U=0 alone would not have ruled out a simple three-fan V.

## 5. Separate SAT pin list: proved local implications

Use the lead's `ENCODING.md` conventions. A vertex V represented as
`r^s` has `Mult(V)=zp[r,s]`, `Quad(V)=zp2[r,s]`. To express a triple
use **both** `zp[r,s]` and `not zp2[r,s]`. For direction d write

```text
A+(L,x,c)=A[L,x,c]; A-(L,x,c)=A[L,c,x].
```

These are immediate-next literals, not arbitrary order relations.
Every implication below is guarded by the selected zero-star/case-B
kite and the adjacency literals identifying its named vertices. They
are clause schemata for the lead, not claims of a newly validated
implementation in the SAT code.

### Pin 1: multiple far-cap exterior apices

```text
case-B boundary guard => Mult(Y) and Mult(Z).
```

**Proof:** if Y were simple, AY and TY would both be single by the
accepted wrong-ray argument. The one-fan triangle TAY then supplies
surviving O* tokens, contradicting Delta=0. The same applies to Z.
This is an accepted Task 6 lemma restated as a useful star pin.

### Pin 2: all six far-cap exterior segments are double

```text
same guard => Use2(TA), Use2(AY), Use2(YT),
              Use2(TF), Use2(FZ), Use2(ZT).
```

**Proof:** after Pin 1, TAY and TFZ are all-multiple triangular faces.
Accepted zero-credit saturation makes every side of such a face
double. The first two are already case-B caps; the four exterior
sides are the useful additional consequences.

### Pin 3: first H-vertex beyond T is multiple — new

If T is represented on H as `H^t`, V as `H^v`, and d points away
from P, use

```text
case-B boundary guard AND A^d(H,t,v) => zp[H,v].
```

**Proof:** exactly §4. Full T guarantees a double first H-segment.
A simple V would either force both distinct return vertices onto one
axis, or make a K2 kite with two forbidden alternating quads. Do not
strengthen this to `zp2[H,v]` or its negation.

### Pin 4: exterior H triangles and their segments

```text
same guard AND next_H(T,V) => triangles TVY, TVZ,
                             Use2(TV), Use2(VY), Use2(VZ).
```

**Proof:** the triangles are the exterior faces along TY,TZ, whose
double use fixes T's outgoing H-neighbour as their shared apex.
Pin 3 makes their three vertices multiple, so the new sides are
double by all-multiple saturation. If a face literal is inconvenient,
encode the corresponding three pairwise next-vertex incidences and
Use2 literals using the concurrency aliases already in the model.

### Pin 5: conditional return-axis concurrency

```text
same guard AND Triple(Y) => U lies on the axis YV AND Mult(U).
same guard AND Triple(Z) => U' lies on the axis ZV AND Mult(U').
```

**Proof:** at triple Y the exterior faces TYV and AYU use its unique
third axis, so Y,V,U are collinear. U also belongs to the distinct
old lines D0,b. The YV axis crosses H at V beyond T, whereas b crosses
H at the opposite old far triple T'; thus they are distinct, and U
is at least triple. The Z/U' proof is symmetric. Do not impose this
common-axis condition at a quad Y or Z: a fourth axis is available.

In concurrency literals, write `Y=a^f`, with `a=PA`, `f=TF`.
For a representative third axis e at Y, the guarded assertions are
`z[a,f,e]`, `z[H,v,e]`, `z[D0,b,e]`. Use three distinct identifiers
in each concurrency literal; a repeated representative is an identity
handled by the existing vertex aliases. Enumerate the permitted
third-axis representatives rather than choosing one without a guard.
The symmetric pin replaces b with c and uses Z's two old axes.

### Pin 6: multiplicity branches at V — new short consequences

```text
same guard AND Quad(V) => V has double-B zero mask,
                         VT is the middle ray of a three-bridge run,
                         Triple(Y) and Triple(Z).
```

**Proof:** Pin 4 gives three consecutive first bridge rays VY,VT,VZ.
The zero-quad mask classification leaves only the double-B mask for
such a run. Its zero-star quad-neighbour exclusion makes Y,Z triple.
Guard the mask by the actual ray ordering, not an arbitrary rotation.

If V is triple, it has at least three consecutive double rays and
therefore has mask `111100`, `111110`, or full. In the four-run
branch its unused ray is H away from T. Eta0=0 makes that ray
**unbounded**. Thus that branch pins V as H's last vertex on that
end, rather than excluding it. This is a proved conditional end pin,
not an assumption that V is full.

The previously proved two-extra-axes bound remains valid. Pin 3
now forces at least two of those axes to concur at the first V;
if V is quad it has at least three extra axes there. Neither fact
alone excludes an 18-line star.

## 6. Checks, coverage, and remaining gaps

`stage2_task7_check.py` compiled and completed the five saved/extended
cores plus 3,474 supplied records. Exact summary:

```text
arrangements=3479
structural_class_arrangements=2455; outside_class=1024
triple_cap_continuations=975
full_case_B_return_axis_checks=4
full_case_B_first_H_apices=1
full_case_B_simple_first_H_apices=0
zero_single_B_quad_neighbour_pairs=0
failures=0
```

The forbidden-motif checker explicitly requires opposed case-B axes
at P,Q and triple other corners of both shared mixed kites. Local
slack at P,Q alone is not silently treated as global zero credit.

The single full exterior H-apex instance is binding witness 29 and
is triple. There is **no positive sample coverage** of a zero B–B
path or of the forbidden simple-V branch. The hand proofs, not
the empty checker branches, exclude those cases. Pin 6 is a hand
mask consequence; no actual globally zero star is supplied as a test.

Outputs are `all8_work/stage2_task7/summary.json` and
`return_details.json`. Reproduce:

```bash
python3 -m py_compile work/bbl/stage2_task7_check.py
python3 work/bbl/stage2_task7_check.py \
  --out work/bbl/all8_work/stage2_task7 \
  work/eng/oth/wit3/wit_sat.jsonl \
  work/eng/lattice/lattice18.jsonl work/eng/lattice/lattice_family.jsonl \
  work/eng/lattice/mixed_all.jsonl work/phi/gallery18.jsonl
```

**Remaining obligation:** exclude the isolated opposite-double-B star.
Its accepted inventory has ten core axes and at least two additional
axes beyond each far triple, hence at least 14 lines. The new multiple
V pins and return-axis incidences constrain those axes further, but
no contradiction with n=18 or the six bad-wedge paths is established
here. The lead's SAT campaign is still partial and has no checked
proof covering all remaining star cubes. This report does not finish
Stage 2 or `K(18)=93`.

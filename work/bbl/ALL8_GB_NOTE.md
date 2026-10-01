# All-8: exact boundary accounting and a closed star subcase

**Status: partial, not a proof excluding every 94.** This note gives (i) an exact
Gauss--Bonnet reduction that eliminates full triple points and kite centres from
the accounting, (ii) a geometric unused-edge lemma and a closed four-point star
subcase, and (iii) a counterexample to the proposed component-only bound >6.
The general boundary inequality below is still unproved.

Do not interpret the lattice-shaped LP cores as a classification theorem:
THEORY.md does not prove that all hypothetical 94s are lattice patches.

## 1. Normalize the triangle surface

Take a disjoint copy of every bounded triangular face and glue two sides exactly
when they represent the same doubly used segment. At an arrangement vertex,
identify corners belonging to the same contiguous fan of triangles, **not**
corners belonging to separate fans. Denote this normalized planar surface by M,
and its Euler characteristic by chi. It can have several components and holes.
In particular, an all-simple triangle is a separate disk.

For a vertex v, let t(v) be its number of triangular sectors. If it is not full,
let r(v) be the number of cyclic runs of 1s in its sector word. Set r=0 if t=0.
A full vertex has one interior copy in M; a non-full vertex has r boundary
copies, one for each fan. Let F be the number of full vertices of all
multiplicities. Then

    chi = T - D + F.                                      (1)

Indeed M has T faces and 3T-D edges. Gluing corners along the double edges gives
3T-2D+F vertices: each full vertex contributes the one cyclic-gluing correction.
Thus (1) follows by Euler. Equivalently, count the fan copies directly.

At an interior vertex with t incident triangles use curvature 6-t; at a
boundary fan of length k use curvature 3-k. Combinatorial Gauss--Bonnet gives

    sum(interior curvatures) + sum(boundary curvatures) = 6 chi.    (2)

## 2. An exact identity using only the boundary and all-8 points

Assume multiplicity <=4. Write A for the number of full 4-fold vertices (all-8).
For k=1,2,3 let s_k count boundary fans of length k at **simple** vertices.
Thus a simple vertex with two opposite triangles contributes twice to s_1.
Full simple vertices (kite centres) are not included in the s_k.

For every non-full triple vertex, including one with t=0, put

    w_3(v) = 3 + (7r(v)-3t(v))/2.

For every non-full 4-fold vertex put

    w_4(v) = 8 + (7r(v)-3t(v))/2.

Then the following is an exact equality:

    sum_P c_P = -6 chi + 2A
                + sum(non-full triples) w_3(v)
                + sum(non-full 4-folds) w_4(v)
                + 2s_1 + s_2/2 - s_3.                    (3)

In the actual remaining class, each non-full 4-fold point is 7-type:
t=7, r=1, hence w_4=1. If J is the number of 7-type points and

    B = sum(non-full triples) w_3(v) + 2s_1 + s_2/2 - s_3,

then

    Lambda = Z - 6 chi + 2A + J + B.                      (4)

Full triple-point costs and interior kite-centre costs have **disappeared**.
No lattice assumption, pair lemma, or maximality assumption is used in (3).

### Proof of (3)

Let K be the number of full simple vertices; let b be the total number of
blocks. At a non-full m-fold point the number of double rays is t-r, so

    N = 2m-t+r.

At a full point N=0. The ray-cost formulas give

    sum c = (sum_multiple N)/2 - b/2 + 4*(number of 4-fold points).    (5)

A simple fan of length 1,2,3 has respectively 0,1,2 double rays;
a full simple vertex has 4. Every block has exactly one simple endpoint, so

    b = 4K + s_2 + 2s_3.                                  (6)

Let C_m be the total boundary curvature at non-full multiple points:

    C_m = sum(non-full multiples) (3r-t).

Equation (2), with full triple curvature 0 and all-8 curvature -2, becomes

    6 chi = 2K - 2A + C_m + 2s_1 + s_2.                   (7)

Insert (6) into (5) and eliminate 2K with (7). A non-full triple contributes
(3r-t)+(6-t+r)/2 = w_3. A non-full 4-fold contributes the same boundary
expression plus its +4 in (5), giving w_4. A full 4-fold contributes
4-2=2. This proves (3).

### Precisely what remains for the general discharging route

A sufficient and, by (4), equivalent boundary statement is

    Z + B >= 6 chi + 7 - 2A - J                           (8)

for n=18 in the remaining class when A>=1. This is a boundary-only formulation
of the missing lemma, **not an established inequality**.

There are actual negative boundary terms: a one-hole triple (t=5,r=1)
has w_3=-1, and a simple three-triangle fan contributes -1. Thus replacing
boundary charge by a nonnegative quantity is invalid. Nor may one set chi=1
without controlling the components and holes. Isolated all-simple triangles
contribute +6 to B and +1 to chi, cancelling exactly in (4).

## 3. A proved geometric touch lemma

**Lemma.** Let P be all-8 with exactly three multiple first vertices Q_1,Q_2,Q_3,
and suppose these three vertices are triple points. If n>=8, then Z>=1.
This lemma does not require the pair lemma.

**Proof.** The eight apex triangles form a disk. At each simple first vertex
the two boundary edges are on its unique cap line. A multiple first vertex must
be a cap change: otherwise a third line through that vertex cuts one of the two
adjacent triangles. Consequently the boundary, with simple subdivision
vertices suppressed, is the triangle Delta=Q_1 Q_2 Q_3 on three distinct cap
lines. P is inside Delta. The core uses seven lines: the four through P and
these three cap lines.

On the line a_i=P Q_i let X_i be its crossing with the opposite side
Q_j Q_k. The opposite-to-Q_i ray at P is a block P X_i, and X_i is simple.
This block is not mutual. Its cap neighbours are either simple subdivision
vertices or Q_j,Q_k. A simple neighbour cannot be a mutual partner (L1).
For a triple neighbour Q_j the already-present triangle uses the line P Q_j.
The only remaining line through Q_j is Q_i Q_j; it meets a_i at Q_i, but
P lies strictly between Q_i and X_i. Hence it cannot close a triangle beyond
X_i. The same argument applies to Q_k.

Choose any line L outside the seven-line core. It avoids the closed triangle
Delta, since its interior is tiled by the eight triangular faces and its
boundary vertices cannot acquire another incident line. Its intersection
with each a_i is therefore either beyond Q_i or beyond X_i. The three
Q_i-rays are alternating rays of the three-line pencil at P. A pseudoline
crossing each pencil line exactly once must meet three consecutive pencil
rays: traverse its sectors; reversing direction in the sector cycle would
recross the last pencil line. Thus L cannot meet all three Q_i-rays. It meets
some ray beyond X_i, making the segment immediately beyond X_i bounded.
Lemma A and non-mutuality make that segment unused. QED.

## 4. A closed star subcase

**Proposition.** In the remaining class, suppose P is all-8 and its bridge
component consists of P and exactly three triple vertices. Then that component
has cost exactly 6 and Z>=1. In particular Lambda>=7 if the sum of the costs
outside the component is nonnegative; this includes the case in which these
four points are the only multiple vertices.

**Proof.** The component is a three-leaf star: P has beta=3, D=5, c_P=3/2.
Each leaf Q has beta=1. The six allowed all-8/triple words, starting just after
the ray Q->P and canonicalized under reversal, are

    100111, 101101, 101111, 110011, 110111, 111111.

Two consecutive block rays at a triple point are impossible: their common cap
would have to meet the third line through the triple point twice. With beta=1,
this eliminates all the displayed words except 101101 and 110011.

The word 110011 would make both cap segments at Q directed into Delta blocks.
At least one of their first neighbours lies on a pencil line through another
corner of Delta. (The fourth pencil line cannot be the immediate neighbour on
both sides of the Q-ray.) For that neighbour the putative extra triangle is
blocked by P, just as in the preceding lemma. Thus 110011 is impossible.
Each leaf has word 101101: its unique block is opposite Q->P, N=4, and c_Q=3/2.
The component costs 4*(3/2)=6. The touch lemma supplies Z>=1. QED.

**Gap to the general case:** this does not bound the charge of larger bridge
components, or compensate negative triple costs in other components. It is
not permissible to infer that every other component has nonnegative cost
without a separate proof.

## 5. Component cost >6 is false even in the stated n=18 class

The suggested shortcut "a bridge component containing all-8 has cost >6"
is false without accounting for Z or imposing additional conditions.
An explicit straight-line arrangement in the class has one all-8 point and
three triple points, all in one bridge component, each of cost 3/2. Thus its
component cost is **6**, not >6. Its pair patterns are all
(11111111,101101), so the pair lemma does not remove it.

Here are its lines, written as (a,b,c) for ax+by+c=0:

    (0,1,0), (1,0,0), (1,1,-6), (1,-1,0),
    (1,2,-6), (2,1,-6), (4,-5,2),
    (-3,6,214), (15,12,4), (-6,7,-222),

together with

    (7+i, 1, 1000000+101*i^3),  i=0,...,7.

There are no parallel pairs. The checker uses the shear x'=x+y/37 only to
avoid a vertical sweep line. The arrangement has T=29, Z=195, Lambda=201.
It is **not** a counterexample to the desired global bound. It shows why
unused-edge/boundary charge cannot be dropped from an all-8 discharging proof.

## 6. Reproducibility

    python work/bbl/all8_boundary_check.py \
      work/eng/lattice/lattice18.jsonl \
      work/eng/lattice/lattice_family.jsonl \
      work/eng/lattice/mixed_all.jsonl

The checker constructs the normalized surface by explicit corner gluing and
checks (1) and (3) in exact half-integer/integer arithmetic. It also checks the
explicit witness's sector words and pair patterns. Result: **1,069 identity
checks, zero failures**; 18 input records are in-class all-8 arrangements.
These are sanity checks, not a computational proof of (8).

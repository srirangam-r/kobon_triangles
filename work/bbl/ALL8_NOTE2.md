# All-8, second note: injective payments and the remaining boundary deficit

**Status: partial. The inequality Lambda >= 7 is NOT proved here, and no
counterexample to that inequality has been found.** The global SAT experiment
returned UNKNOWN. This note does prove new local payment lemmas, a nonnegative
cost theorem for pure-triple *line-connected* components, and a strengthened
closed star subcase. It also gives an explicit counterexample to an
unconditional first-neighbourhood touch/N-charge lemma.

Inputs: `SOL_TASK2.md`, `ALL8_BRIEF.md`, `ALL8_GB_NOTE.md`, and THEORY §27.
The distinction between the following two classes is important:

* the **structural class**: 18 pseudolines, multiplicity <= 4, only all-8 and
  7-type quadruples, the allowed consecutive quadruple/triple pair patterns;
* a hypothetical **maximal 94**: additionally T=94 and the stated local
  (T, number-of-vertices) optimality.

The example below belongs to the structural class; it is not a maximal 94.
The payment proofs need neither T=94 nor optimality. Statements using the
allowed pair patterns explicitly say so.

## 1. Notation

A ray of a multiple vertex is B, R, or N as in the brief. N-ray tokens have
value 1/2. A token is identified by its vertex and its first segment/ray, not
merely by its supporting line. Let

    Ntot = sum_{multiple P} N_P = sum_{triples P} N_P + 2J

in the structural class. A kite is a simple vertex with four triangular
sectors. Its four multiple neighbours, in cyclic order, are its corners.
Write K_q for the number of kites with exactly q quadruple corners,
q=0,1,2,3,4. Thus K_0 is a triple-only kite; K_1,...,K_4 are mixed kites.

Write U_3,I_3 for the numbers of touch/end blocks whose multiple origin is
triple, and U_4,I_4 for their quadruple-origin counterparts. H_3,H_4 count
mutual blocks ending at a simple three-triangle fan, according to the
multiplicity of their origin. H_3 is a *block count*, not a fan count.

For a quadruple P, let k_P be its number of blocks ending at kite centres,
and put

    S_P = 8 - D_P - k_P.

Finally U=U_3+U_4, and R=Z-U/2 >= 0. Here R is a residual scalar, not a
bridge-ray count. From the established identity,

    2 Lambda = 2Z + Ntot + 8(A+J) - b.                 (1)

Everything below involving half-integers is checked using doubled integers.

## 2. PROVED: triple blocks cannot be consecutive

Suppose P is triple and two consecutive rays P->X and P->Y are blocks.
The triangle between them has third side XY on a cap line C. Since X,Y are
simple, the other triangles on PX and PY also have their third sides on C.
Their remaining vertices lie on the two opposite rays of the third pencil
line at P. They are distinct. Thus C meets that pencil line twice, a
contradiction. This proof does not require maximality.

An immediate consequence used repeatedly: if P is triple and PXT is a
triangle with PX a block, then PT cannot be another block. If PT is doubly
used, T is therefore multiple.

## 3. PROVED: every triple-only kite has at least two singly used cap edges

**Lemma.** Let X be a kite with four triple corners P,Q,R,S in cyclic order.
Each of the opposite pairs {PQ,RS} and {QR,SP} contains a singly used edge.
In particular at least two cap edges are singly used.

**Proof.** The diagonals PR and QS are the two lines through X. The four side
lines PQ,QR,RS,SP are distinct. At P the three lines are PQ,PS,PR, and at Q
they are PQ,QR,QS.

If PQ has a triangle on its other side, its third vertex must be the
intersection of one of {PS,PR} with one of {QR,QS}. The PR/QR candidate is R,
but the segment PR contains X, so it cannot be a side of that face. The
PS/QS candidate is S and is ruled out in the same way. The PR/QS candidate
is X, on the already occupied side. Thus the only possible exterior third
vertex is

    Y = PS intersect QR.

For PQY to be that triangle, Y must be beyond P on PS, away from S, and
beyond Q on QR, away from R. For an exterior triangle on the opposite edge
RS, the same Y must instead be beyond S on PS, away from P, and beyond R
on QR, away from Q. These conditions cannot both hold: Y cannot be beyond
both ends of the segment PS. Therefore PQ and RS cannot both be doubly
used. Each already borders an interior kite triangle, so one is singly
used. Interchanging the roles of the two opposite pairs proves the other
assertion. QED.

The argument uses only pseudoline crossing uniqueness and face adjacency;
there is no straight-line or convex-angle assumption.

**Payment.** Choose two of these single cap edges. Both endpoints of each
are triple vertices with an N-ray along that edge. The four distinct N-ray
tokens pay the four kite blocks, total value 2. No assertion that a mixed
kite has two single cap edges is made.

For orientation: a six-line example of such a kite is the wiring word

    2* 0* 2 3* 1* 0 3

with n=6, T=6, Z=0, Lambda=6. Its four corners are triple. This is not an
18-line counterexample. It verifies that triple-only kites genuinely occur,
and hence cannot simply be omitted from the payment calculation.

## 4. PROVED: injective N-payments for triple-origin fans and non-mutual blocks

### 4.1 The outer-triangle rule

Consider a triangle PXT with P triple, PX a block, and TX singly used.
There is a canonical available N-token:

* if PT is singly used, take the token at P on PT;
* if PT is doubly used, T is multiple by §2; take the token at T on TX.

Both are bounded single-edge N-tokens. Notice that T may be 7-type, not
necessarily triple. This is why the correct resource is Ntot, including
2J, rather than just sum_triples N.

### 4.2 Three-triangle fans

Suppose PX ends at a simple three-fan X. The two mutual blocks at X have
origins P and Q. Their common triangle is PQX. The other triangle adjacent
to PX is PXT, and its edge TX is singly used. The outer-triangle rule pays
the block PX with one N-token. Apply this to every triple-origin mutual
block at a three-fan.

### 4.3 Touch and end blocks

If PX is a touch or end block, X has exactly its two P-apex triangles:
call them PXT and PXV. Its two cap edges XT and XV are singly used.
The outer-triangle rule supplies one token from each of these two triangles.
Thus a triple-origin touch/end block supplies **two distinct** N-tokens.
Only one token would be needed to pay its block debt. Keeping both in the
accounting leaves extra credit. Touches are also paid by unused segments;
that is intentional, not a double counting of an N-token.

### 4.4 Why these payments, together with §3, are injective

Every token just used is on a singly used bounded segment. That segment has
exactly one incident triangular face, which identifies the payment context.

* A selected cap edge in §3 has a kite centre as its simple corner. Its two
  endpoint tokens are used only for that kite.
* An outer triangle at a three-fan has that three-fan as its simple corner
  and only one block from that corner in that triangle. If its other corner
  T is simple, PT is single, and both PT and TX are single. This triangle is
  consequently a one-fan at T; T cannot furnish another block in it.
* The same reasoning applies to the two triangles of a touch/end two-fan:
  each has only the one block PX from its designated simple corner. A
  simple T is again a one-fan in this triangle.

If T is multiple, the other possible N-token at T on a single PT is not
selected by the rule. If PT is double, the selected token is the unique
multiple-end token of TX. Hence the unique triangular face, the fan type
of X, and the chosen multiple endpoint identify the charged block/kite.
A token cannot be selected twice. Distinct endpoint tokens of the same
single edge are different resources, each worth 1/2.

**Theorem (injective payment inequality).** For every arrangement of
multiplicity at most four,

    Ntot >= H_3 + 2(U_3+I_3) + 4K_0.                  (2)

All the asserted resources in (2) have been explicitly and injectively
selected. This is a proved inequality, not an empirical fit. Set

    N_* = Ntot - H_3 - 2(U_3+I_3) - 4K_0 >= 0.        (3)

N_* is a global remaining ray count. In particular it need not be
localized to the first neighbourhood of an all-8 point.

## 5. PROVED: pure-triple line-connected components have nonnegative cost

Join two multiple vertices whenever some arrangement line contains both,
even if they are not consecutive. This defines **line-connected
components**, which are generally larger than bridge components.

**Theorem.** If a line-connected component C contains only triple vertices,
then

    sum_{P in C} c_P >= (U_C+I_C)/2 >= 0.              (4)

Here U_C,I_C count blocks with origin in C.

**Proof.** Every N-token used for a block originating at P is either at P,
or at a multiple T sharing the line PT with P. Thus it stays in C.
The corners of a kite are connected by their cap lines, so every kite
having a corner in C has all four corners in C and is triple-only. The
origins of the two blocks of a three-fan share the line PQ, so they too
belong to the same component.

The injective construction restricted to C therefore gives

    sum_C N >= H_C + 2(U_C+I_C) + 4K_C
             = b_C + U_C + I_C.

Since sum_C c=(sum_C N-b_C)/2, (4) follows. QED.

**Important limits.** This does NOT prove nonnegative cost for each
bridge component. Nor does it prove nonnegative cost for line-connected
components containing quadruples. Those distinctions are essential.
For a wholly multiplicity-at-most-three arrangement it gives the genuine
but weaker global bound sum c >= (U+I)/2; it does not by itself prove the
sharp 18-line triangle bound.

## 6. PROVED: quadruple kite-block capacity

**Lemma.** At any quadruple P,

    S_P = 8-D_P-k_P >= 0.                             (5)

**Proof.** A kite block cannot have an adjacent block ray. Otherwise the
triangle between the two block rays has simple other vertices X,Y, with
X a full kite centre. Its edge XY is then doubly used, contradicting L1
(a double edge must have a multiple endpoint). Map every kite block ray
to its following cyclic ray. These are distinct non-block rays. Hence
k_P <= 8-D_P. QED.

For a 7-type P there are six consecutive double-ray positions. Divide
these into three adjacent pairs. In a pair, the weight

    (#block rays) + (#kite-block rays)

is at most two: if there is a kite block, the other position is not a
block; otherwise two ordinary blocks give weight two. Thus D_P+k_P <=6,
and S_P>=2 for a 7-type point. The weaker (5) suffices for the next identity.

## 7. PROVED exact reduction: the only remaining negative cell term is K_1

Combining (1)--(5) gives the exact identity

    2 Lambda = 2R + N_* + 2U_3 + I_3 + U_4
               + sum_{quadruple P} S_P
               + 2K_3 + 4K_4 - 2K_1.                (6)

**Derivation.** Partition the block count as

    b = H_3+H_4+U_3+U_4+I_3+I_4 + 4K_0
        + 4(K_1+K_2+K_3+K_4).

Insert (3) and 2Z=2R+U_3+U_4 into (1). This first gives

    2 Lambda = 2R+N_*+2U_3+I_3+8(A+J)
               -H_4-I_4-4(K_1+K_2+K_3+K_4).

Also

    sum_quad k_P = K_1+2K_2+3K_3+4K_4,
    sum_quad D_P = sum_quad k_P + H_4+U_4+I_4.

Substitute these in the definition of sum S_P. A mixed kite with q
quadruple corners contributes 2q-4, giving (6).

Every term on the right of (6) except **-2K_1** is nonnegative. Triple-only
kites, triple-origin three-fans, and triple-origin end blocks are no longer
unpaid negative terms. A two-quadruple kite balances exactly in this
accounting. Three/four-quadruple kites have positive credit.

### Precisely the still-open inequality

The target is now equivalent to

    2R + N_* + 2U_3 + I_3 + U_4 + sum S_P + 2K_3 + 4K_4
        >= 14 + 2K_1.                                (7)

**OPEN.** No proof of (7) for all structural-class arrangements with A>=1
has been obtained. Two separate obligations remain: paying the one-quadruple
kite deficit, and establishing the constant boundary surplus 14. Merely
showing all block debts can be paid would establish only Lambda>=0, not
Lambda>=7. Merely omitting -2K_1 is also invalid.

For example the complete, proved subcase

    K_3 + 2K_4 - K_1 >= 7

is closed by (6), without needing any additional N_* or R. It does not
cover all arrangements. In a hypothetical 94, the left side of (7) would
be exactly 12+2K_1. This is an exact remaining constraint, not a
classification of such arrangements.

The old normalized-surface identity remains valid:

    Lambda = Z - 6chi + 2A + J + B.

Equation (7) is a further *proved charging reduction* of the same global
problem. Nothing here assumes chi=1 or assumes nonnegative boundary B.

## 8. PROVED generalized pencil-touch lemma, and a strengthened star subcase

For an m-fold P let E(P) consist of its non-mutual block rays, and C(P) of
their cap lines. Put

    h(P) = min_{cyclic m-consecutive ray sets H} |E(P) intersect H|.

**Lemma.** If there is an arrangement line W outside the pencil at P and
outside C(P), then Z>=h(P). Every end-block ray lies in one m-consecutive
half-pencil.

**Proof.** As W traverses the sectors of the pencil, every crossing moves
one step in the sector cycle. A reversal would recross the just-crossed
pencil line. Because W crosses each pencil line once, its m intersections
therefore lie on m consecutive rays, one from each axis.

If it meets a selected non-mutual block ray, it cannot cross inside the
block's first segment: that would cut one of its two triangular faces.
It cannot meet the simple far vertex, since W is not its cap line. Its
intersection is thus beyond that vertex. The block continuation is
bounded and unused. Selected rays are on distinct axes and give distinct
unused segments. There are at least h(P) of them. None of the selected
rays can be an end block, so all end-block rays lie in the complementary
m-consecutive half-pencil. QED.

Here |C(P)|<=2m, so m+|C(P)|<=3m<=12<18 for m<=4. Such a W always exists.
This proof is independent of the number and multiplicities of P's bridge
neighbours. It does not claim h(P)>0 when all P's blocks are mutual.

**Closed star subcase.** Suppose there is exactly one line-connected
component containing quadruples, and it consists of one all-8 P and
three triples. Then Lambda>=8, hence Lambda>=9 and T<=93.

**Proof.** It is the three-leaf bridge star from `ALL8_GB_NOTE.md` §4.
The allowed pair lemma and that note's checked star argument give each
leaf word 101101: its only block is opposite the ray toward P; all its
cap-line rays are N. The component has cost 6. Its first-vertex boundary
is the cap triangle from that note's §3.

All five P-blocks are non-mutual. Any multiple mutual partner on their
caps would have to be a leaf, but the leaves have no cap-line blocks;
simple partners are excluded by L1.

Each side of the cap triangle meets the opposite ray of the pencil axis
through its third corner. Following that boundary shows that the three
corner rays alternate with their opposites in the three-line subpencil.
The fourth pencil axis inserts rays in two opposite sectors of this
six-sector pencil, necessarily in two distinct corner gaps. Their cyclic gaps among all eight
rays are therefore 2,3,3. Every four-consecutive-ray set contains at most
two corner rays, hence at least two of the five non-mutual block rays.
Thus h(P)>=2 and Z>=2. All other line-connected components contain only
triples, so (4) gives nonnegative total cost outside this star. Consequently
Lambda>=2+6=8. QED.

This replaces the old unproved outside-cost assumption by a concrete
line-component hypothesis. It does not extend to larger mixed components
or to an arbitrary bridge-star embedded in a larger line-connected component.

## 9. COUNTEREXAMPLE: positive local touch/N ownership at every all-8 point

The following unconditional extension is **false**:

> Every all-8 point has either a touch block or a positive N-ray at one
> of its multiple first vertices.

An explicit structural-class arrangement is the wiring word

    5 6 7 8 5 6 7 5 6 5 9 14 10 8 0 1 2 3 0 1 2 0 1 0 4 5
    6* 8* 10* 12* 14* 16 11 3 4* 6* 8** 11** 14* 7 10 13
    2* 4** 7** 10** 13* 3 6 9 1* 3** 6** 9* 11* 13 5
    0 1* 3* 5* 7* 9* 11 12 2 6 8 7 0* 3 4 5 6 3 4 5 3 4 3

Generator i reverses tracks i,i+1; i* reverses three tracks, i** four.
Labels and event indices are those of `work/t3/arr.py`. It has

    n=18, T=74, Z=34, Lambda=66.

At event P=44 the ray word is RBRBRBRB. Its four multiple first vertices
are 43,36,45,52, all all-8. Their ray words are respectively

    RRRBRBRB, RRRBRBRB, RBRBRRRB, RBRBRRRB.

Thus none has any N-ray. P's four blocks end at kite centres 39,40,49,48,
so all are mutual, no continuation is unused, h(P)=0, and S_P=8-4-4=0.
The checker verifies the structural class, including the pair patterns.
The word is also record 1 of `work/eng/lattice/lattice18.jsonl`.

This refutes the displayed first-neighbourhood assertion, including its
beta>=4/all-8-neighbour specialization. It does **not** refute a non-local
assignment of boundary charge, an assertion requiring global maximality,
or Lambda>=7. There are 34 unused segments elsewhere. The correct pencil
lemma explicitly excludes mutual rays; deleting that exclusion is precisely
the invalid local step.

## 10. PROVED necessary triple optimality condition

Resolving a triple into three simple crossings has two cyclic options.
Each creates one small triangle and adds an edge to exactly one of the
two alternating three-sector sets. A formerly triangular affected sector
ceases to be triangular; an unaffected sector is unchanged; a formerly
nontriangular affected sector cannot become triangular by adding an edge.
Thus the triangle changes are

    Delta T = 1 - (s_0+s_2+s_4),
    Delta T = 1 - (s_1+s_3+s_5).

Each resolution replaces one vertex by three. Lexicographic optimality
therefore requires both alternating sums to be at least two. This leaves
16 labelled sector words. This is a necessary condition only: it is not a
complete classification of maximal arrangements. It was not imposed in
the two unrestricted SAT probes reported below.

## 11. Exact computational records

These computations check the proofs and expose invalid shortcuts; none is
a finite exhaustive proof of (7).

### 11.1 Geometric/payment checker

Script: `work/bbl/note2_check.py`. It constructs faces from wiring words,
checks actual selected N-ray tokens for non-reuse, checks the opposite-edge
kite lemma, the pure-triple component theorem, equations (2) and (6), and
the pencil-touch/end-half-pencil statements. It includes the explicit
wiring examples above and checks h=2 for the earlier component-cost-6
star witness. Source data are unchanged.

Command, from the repository root:

```bash
python work/bbl/note2_check.py \
  work/eng/lattice/lattice18.jsonl \
  work/eng/lattice/lattice_family.jsonl \
  work/eng/lattice/mixed_all.jsonl \
  work/phi/gallery18.jsonl
```

Exact stdout is also saved at
`work/bbl/all8_work/note2_check_extended.out`:

```text
Triple perturbations: [((1, 0, 1, 0, 1, 0), 1, 2), ((0, 1, 0, 1, 0, 1), 1, 2)]
Irreducible triple words: ['111100', '110110', '011110', '111110', '111001', '101101', '111101', '110011', '011011', '111011', '100111', '110111', '001111', '101111', '011111', '111111']
Triple sector-word checks: 64; failures=0
Closed-star witness: {'component_cost': 6, 'pencil_h': 2, 'proven_Lambda_lower': 8, 'actual_Lambda': 201}
Perfect-star counterexample: {'n': 18, 'T': 74, 'Z': 34, 'Lambda': 66, 'structural_class': True, 'P': 44, 'ring': 'RBRBRBRB', 'multiple_first': [43, 36, 45, 52], 'touch_at_P': 0, 'first_multiple_N': 0, 'gens': '5 6 7 8 5 6 7 5 6 5 9 14 10 8 0 1 2 3 0 1 2 0 1 0 4 5 6* 8* 10* 12* 14* 16 11 3 4* 6* 8** 11** 14* 7 10 13 2* 4** 7** 10** 13* 3 6 9 1* 3** 6** 9* 11* 13 5 0 1* 3* 5* 7* 9* 11 12 2 6 8 7 0* 3 4 5 6 3 4 5 3 4 3'}
Six-line triple-corner kite: {'n': 6, 'gens': '2* 0* 2 3* 1* 0 3', 'T': 6, 'Z': 0, 'Lambda': 6, 'counts': {'K_0': 1, 'C_pure': 1, 'N_total': 16, 'N_star': 12, 'S_4': 0, 'U_4': 0}}
Payment checks: 3446 arrangements; failures=0
Pencil-touch checks: 18979 points; 265 all-8 points; failures=0
Payment totals: {'C_pure': 1253, 'H_T': 4600, 'I_T': 845, 'K_0': 45, 'K_mixed': 447, 'K_q1': 239, 'K_q2': 138, 'K_q3': 55, 'K_q4': 15, 'N_star': 56532, 'N_total': 78534, 'S_4': 8313, 'U_4': 1723, 'U_T': 7766}
```

The 3,446 records include arrangements outside the all-8 structural class;
the local payment lemmas hold for them too. `C_pure` counts checked
pure-triple line components. Point and arrangement counts include repeated
records, not necessarily nonisomorphic arrangements. Payment identity checks
exclude input multiplicity >4. This dataset does not certify a global
minimum of Lambda in the all-8 class.

### 11.2 Global T=94 SAT experiment: UNKNOWN

Script: `work/bbl/all8_work/global_sat.py`, built on `patsat_m.py` and
`classsat.py`; outputs in `work/bbl/all8_work/global18/`.

```bash
python -u work/bbl/all8_work/global_sat.py --seconds 1800 \
  --out work/bbl/all8_work/global18
```

Exact log (`work/bbl/all8_work/global18.log`):

```json
{"event": "built", "variables": 251915, "clauses": 1057588, "seconds": 0.49007511138916016}
{"result": "UNKNOWN", "seconds": 2611.1223895549774, "lazy_clauses": 0, "variables": 251915, "clauses": 1057588, "statistics": {"restarts": 5117, "conflicts": 2898307, "decisions": 9714343, "propagations": 27269794623}, "validation": false}
```

The interrupt took longer than the nominal budget. This run produced
neither a model nor an UNSAT certificate. In particular no DRAT proof was
obtained or checked. The construction and known-model validation are not
an encoding-completeness audit.

### 11.3 Stronger Q>=7 probe: also UNKNOWN

Let Q=Lambda-R. Discarding R>=0 and proving Q>=7 would be sufficient, but
that stronger claim is **unproved**. Script:
`work/bbl/all8_work/q_probe.py`. It builds the structural-class model and
uses a signed weighted-adder CNF for 2Q<=13. It has no T=94 requirement.
SAT outputs are accepted only after conversion to an actual wiring word,
independent face/count checks, and the lazy pair-pattern checks.

The adder was exhaustively tested on all assignments of 42 small signed
weighted instances:

```bash
python work/bbl/all8_work/q_probe.py --self-test
```

Exact output:

```text
Weighted-adder exhaustive assignment checks: 1524 ; failures=0
```

The pinned 18-line witness from `ALL8_GB_NOTE.md` §5, run with
`--validate --bound 18 --seconds 120 --out work/bbl/all8_work/q_validate`,
was SAT and reconstructed as an arrangement with T=29, Q=9. Its exact
verified decomposition was

```json
{"K": 0, "H": 0, "U": 6, "I": 2, "residual2": 384, "Q2": 18, "Lambda": 201, "A": 1, "J": 0}
```

The reconstructed arrangement and final solver result are retained in
`work/bbl/all8_work/q_validate/witness.json` and `result.json` (including
the reconstructed word and solver statistics). Exact validation stdout is
saved at `work/bbl/all8_work/q_validate.log`. This is a validation example,
not evidence that all admissible models are correct.

Unrestricted command:

```bash
python -u work/bbl/all8_work/q_probe.py --n 18 --bound 13 --seconds 300 \
  --out work/bbl/all8_work/q18
```

Exact stdout (`work/bbl/all8_work/q18.log`):

```json
{"event": "built", "n": 18, "bound": 13, "variables": 223535, "clauses": 1267493}
{"result": "UNKNOWN", "seconds": 300.0810778141022, "n": 18, "bound": 13, "lazy_clauses": 0, "statistics": {"restarts": 890, "conflicts": 362541, "decisions": 10046013, "propagations": 4922725385}}
```

No counterexample to Q>=7 and no proof of Q>=7 resulted. UNKNOWN does not
strengthen either theorems or empirical lower bounds.

## 12. What can and cannot enter THEORY

**Proved in this note:** the opposite-edge obstruction for triple-only
kites; the injective N-payment inequality (2); nonnegative cost of
pure-triple line-connected components; the quadruple slack bound (5);
the exact signed-cell identity (6); the pencil-touch lemma; the specified
line-component star subcase; the necessary alternating-sector triple
optimality condition.

**Explicitly false:** positive touch/N credit in the first neighbourhood
of every all-8 point, without a restriction excluding the perfect mutual
star of §9.

**Still open:** (7), hence Lambda>=7 in the general all-8 case; Q>=7;
nonnegative cost for arbitrary bridge components or mixed line-components;
a complete classification or exclusion of one-quadruple kite configurations.

The specific unresolved global step is now (7), not the payment of
triple-only kites or triple-origin end/three-fan blocks. A boundary theorem
must pay 2K_1 and still retain the constant surplus 14. No assertion of
such a theorem is made here.

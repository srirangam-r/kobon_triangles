# All-8 Note 7 — larger LC families and direct wedge payments

**Stage 1 remains open.** New hand proofs establish LC for every
bridge/mutual component consisting entirely of `110110` triples, of
any size, and for every component of size two in the structural class.
They do not cover the larger components containing five-/six-sector
triples or quadruples, and do not prove end reconciliation.

**Stage 2 progress:** the independent Track 2 report `STAGE2_TASK7.md`
excludes the two-quad single-B/single-B path by a cap-continuation
contradiction. Only the isolated opposite-double-case-B star remains.
It also supplies a stronger proved star pin: the first vertex beyond
either far case-B triple on H is multiple. These new hand arguments
await the lead's review; no new SAT/UNSAT certificate is claimed.

Inputs read: `SOL_TASK7.md`, `STAGE1_ISOLATED.md`, and the accepted
Note 2–6 definitions/payments. The main agent pursued Stage 1; the
existing user-authorized subagent continued only Stage 2. Each new
result below is explicitly labelled proved, checked, or open.

## 1. The exact direct target

Write

\[
 C_q=\sum_P S_P^\circ+2K_3+4K_4,
 \qquad \Delta_N=N_{\rm res}-F,
 \qquad \Delta_Z=2Z-U-G_Z.
\]

The accepted identities give

\[
2\Lambda=2Z+U+I+N_{\rm res}+C_q,
\qquad \Lambda=\pi+E/2,\quad W=18-\pi.
\]

Thus the lead's reformulation is exact:

\[
\boxed{(B)\quad W\le 2Z+U+I+N_{\rm res}+C_q.}       \tag{1}
\]

For a direct injection its resources are:

- both endpoint slots of every bounded unused segment;
- **one**, not two, formal label per U/I block;
- the actual remaining N tokens **before** removal of multiple ends;
- the corrected quad-slack and K3/K4 units.

No I label is added to E. The numerical slack of (1) is
`E-18+3*pi`. On a 93 this is automatically pi; numerical passes alone
still do not prove the allocation.

Throughout the new LC proofs, n>=6, every pair of proper pseudolines
crosses once, quadruples are in the accepted structural class, and
the alternating triple sector sums are at least two.

## 2. Proved: a componentwise capacity identity for pure triples

Let C contain only triples, v=|C|. Let e count its double bridges,
and F_C its unbounded N rays. Let B_C count all its block rays.
Payment locality, accepted in Task 7, keeps all charges inside C.
Every mutual kite in C is K0: a quad corner would itself belong to C.
There are no mixed-kite or quad-reservation payments at C.

The old charges number

\[
 2(U_C+I_C)+H_C+4K_{0,C}
 =B_C+U_C+I_C.
\]

Subtracting those charges and the F_C end tokens gives

\[
\boxed{M_C=U_C+I_C+d_C
 =\sum_{P\in C}N_P-B_C-F_C.}                         \tag{2}
\]

This is an exact identity, not a Hall argument.

Triple optimality leaves the following sector masks, up to dihedral
symmetry. With four sectors, the two zero sectors must lie in different
alternating classes, hence are adjacent or opposite.

| Mask | Number of double rays | Number of N rays |
|---|---:|---:|
| 110110 | 2 | 4 |
| 111100 | 3 | 3 |
| 111110 | 4 | 2 |
| 111111 | 6 | 0 |

If their counts in C are a,b,c,d respectively, double rays are blocks
or the two ends of its e bridges. Equation (2) becomes

\[
\boxed{M_C=2a-2c-6d+2e-F_C
 =2v+2e-2b-4c-8d-F_C.}                              \tag{3}
\]

This explains why an unrestricted per-vertex argument cannot treat
five-/six-sector triples as if they were isolated `110110` triples.
Their bridge network, not just their own tokens, must supply capacity.

## 3. Proved: LC for every all-110110 component

**Theorem.** If every vertex of C is a triple with sector mask
dihedrally equivalent to `110110`, then `|D_C|<=M_C`.

Each such vertex has four bounded single rays and two opposite double
rays. Consequently F_C=0, `B_C+2e=2v`, and (2) yields

\[
\boxed{M_C=2v+2e.}                                  \tag{4}
\]

Let L(C) be C's set of pencil lines. Each component link joins vertices
sharing an arrangement line: a double bridge uses its own axis, a
three-fan uses the central cap, and adjacent/opposite kite corners use
a cap/diagonal. A spanning-tree ordering therefore adds at most two
new lines with each triple after the first:

\[
|L(C)|\le3+2(v-1)=2v+1.                             \tag{5}
\]

There are three cases.

**A. e>0.** Equations (4)–(5) give

\[
 M_C\ge2v+2\ge |L(C)|+1\ge |D_C|+1.
\]

This is a strict LC bound without having to identify a single-ray
charging vertex on every demanded line.

**B. e=0 and U_C+I_C>0.** A touch block's axis contains its unused
continuation, so is not Q0. An end block's axis has an I end rather
than two W ends, so is not Q0 either. Thus at least one line of L(C)
is excluded from D_C. Then `|D_C|<=2v=M_C`.

**C. e=0 and U_C+I_C=0.** All 2v blocks are mutual. Let h count
three-fan centres and k count K0 centres. Then `2h+4k=2v`, or
`h+2k=v`. Select the central cap edge of each three-fan and all four
cap edges of each K0. These are distinct singly used bounded edges
joining vertices of C: their unique incident triangles identify their
simple fan centres. Their count is

\[
h+4k=v+2k.
\]

If a pencil line L contains r_L vertices of C, it supports at most
`r_L-1` selected edges, because its ordered vertices form a path.
Also `sum r_L=3v`. Hence

\[
3v-|L(C)|=\sum_L(r_L-1)\ge v+2k,
\qquad |L(C)|\le2v-2k\le M_C.
\]

All cases prove LC. This includes the lead's isolated-triple case,
but does not assume isolation or U=0. ∎

**Checked:** exact capacities, bridge counts, selected mutual cap
edges, and the casewise inequalities pass the new checker. Among
eligible components, this proves LC for 15,878 in the 93 cohort,
2,254 in the earlier cohort, and 29 in the binding cohort. Of these,
261, 88, and 9 respectively are non-isolated. The all-mutual branch
has one exercised component in the unfiltered earlier cohort, but
none in its eligible subset; it is a hand proof, not an empirical
inference from that absence.

## 4. Proved: LC for every size-two component

**Theorem.** A size-two component in the structural class contains
two triples and satisfies LC. This adds the possible four-run partner
to §3's family.

A quad in such a component could have at most one bridge ray: the
other multiple vertex shares only one axis with it. At an all-8 quad,
seven remaining double rays would be blocks; at a 7-type, five of a
six-ray consecutive double run would be blocks. Either forces three
consecutive quad blocks, forbidden by the accepted lemma. Thus the
two vertices P,Q are triples.

If there is no double bridge, every double ray at either vertex is a
block. The isolated-triple mask argument still applies locally:
no consecutive triple blocks plus optimality forces `110110`. Section
3 covers this case, even though the vertices may be mutually joined.

Otherwise PQ is the sole bridge. A triple with one bridge ray cannot
have mask `111110`: the other three double rays would be blocks in a
four-ray consecutive run. Nor can it be full, with five block rays.
Thus each endpoint is `110110` or `111100`. In the latter, the bridge
is the middle of the three double rays, and the two flanking rays are
blocks.

**Two four-run endpoints are impossible.** Let X,Y be their shared
simple triangle tips on the two sides of PQ. Both PX,PY and QX,QY
would be blocks. At P the outer triangle beside PX has third vertex
`R=(PY) intersect (QX)`. At X, XR must run beyond X away from Q.
At Q the outer triangle beside QY has the same third vertex R, but
requires R on QX beyond Q away from X. A point cannot lie beyond
both ends of QX. This is a wrong-ray contradiction, not a straight-line
argument.

It remains to consider P four-run and Q opposite-four. Here QX,QY
are single. If X were a mutual fan, its other block origin would lie
on the continuation of QX beyond X away from Q, so would be a third
multiple vertex in C. A kite also has more than these two origins.
Therefore both flanking blocks at P are U/I.

Their two axes are not Q0, as in §3B. The remaining axis PQ has an
unused first ray opposite Q, either bounded (so the line has an unused
segment) or unbounded (so P is a multiple end). It is not Q0 either.
**No pencil line through P is demanded.** At most Q's two non-PQ axes
remain in D_C. Equation (3) gives `M_C=4-F_C>=3`, since only P's one
empty ray can be unbounded. Hence `|D_C|<=2<M_C`. ∎

**Checked:** 39 eligible size-two components in the 93 cohort, six
in the earlier cohort, and nine in the bindings. Three binding
components exercise the new mixed four-run/opposite-four branch
(records 4, 20, 24); the others are already covered by §3.

**LC still open:** the larger mixed-sector pure-triple components and
components containing quads. After §§3–4 and the lead's size-one lemma,
the tested eligible cohorts leave 149, one, and 27 components outside
the newly proved families, respectively. This is sample coverage,
not a classification of every possible unresolved component.

## 5. Proved: a disjoint partial direct wedge payment

Let X be a bad wedge with corner triangle XAB. Both XA,XB are single;
different X have different corner triangles. The following local
payments jointly form an injection into the resources of (1).

**Two multiple corners.** The O* lemma leaves the tokens at A on AX
and B on BX free. Choose one, deterministically. Its single edge's
unique triangle identifies the wedge, so different wedges cannot
reuse it.

**One triple corner A, AB single.** The other corner B is simple,
with BA,BX both single. Its fan in this triangle has only one sector
(an opposite isolated fan is harmless). The token at A on AX cannot
be an outer-fan or kite payment and survives. Again its triangle
identifies X.

**One triple corner A, AB double, B a U/I centre.** Its outer-triangle
rule spends A's token on AX, but use this block's **single** formal
U/I label instead. One block cannot have bad-wedge tips in both of
its triangles when n>=6: its cap line would have exactly the three
simple vertices `X--B--X'`, meeting just three other lines and forcing
n=4. Thus labels are not reused.

**One triple corner A, AB double, B a three-fan centre with single
central cap AQ.** Use the surviving token at A on AQ, from the
accepted H* lemma. Each origin has only one outer triangle at this
centre, so at most one wedge takes that endpoint token. The other
origin can use the other endpoint. The central triangle is not a
wedge's corner triangle, hence these tokens do not collide with the
first two cases.

**One quad corner A.** Its single first ray AX rules out all-8, so A
is 7-type. Accepted Task 5 gives `S_A^circ>=2`. There are only two
single first rays at A, and hence at most two such wedges. Assign
them distinct corrected-slack units. The two-multiple case already
uses its free tokens instead, so does not spend these units.

A four-fan cannot occur in the AB-double case because BX is single.
Consequently the only wedge types not covered here are:

1. **all three corners simple**;
2. **one triple A and a three-fan B whose central cap AQ is double**.

All selected N tokens are bounded and survive into Delta_N, hence
also N_res. Their face contexts are disjoint from each other; formal
U/I labels and quad units are separate resources. This proves the
partial injection, but not that the remaining wedges are payable. ∎

**Checked, eligible inputs:**

| Cohort | All wedges | Paid by this lemma | All-simple gap | Double-H gap |
|---|---:|---:|---:|---:|
| 93 | 151357 | 27362 | 123779 | 216 |
| Earlier | 24844 | 2487 | 22357 | 0 |
| Bindings | 120 | 27 | 88 | 5 |

These are resource-level checks, not just a comparison of total budgets.
The eligible inputs do not exercise the one-quad branch; its proof
uses the accepted 7-type corrected-slack bound. Ten such wedges occur
in the unfiltered earlier cohort, which is not silently promoted to
the structural/optimality class.

## 6. Checked and refuted: three tempting locality rules

### 6.1 Every noncap Q0 line has a both-single multiple — false

The lead suggested trying to charge each Q0 line to a vertex where
both of its first rays are single. This premise is not universal.

**Exact eligible counterexample: 93 record 26.**

```text
T=93, pi=1, U=1, I=1, Delta_N=12, Q0=14, E=16
noncap Q0 lines with no both-single multiple: 4,6,13,15,16
line : sole multiple vertex : first segment uses
4    : 66                   : 2,2
6    : 86                   : 2,2
13   : 90                   : 2,2
15   : 79                   : 2,2
16   : 62                   : 2,2
```

All five vertices have `110110` sectors, so §3 covers their components
without this false premise. Complete word and geometry are saved in
`all8_work/note7_93/eligible_no_single_pair_first_failure.json`.
The restricted both-single matching fails on 356 eligible 93 records,
82 earlier records, and eight bindings. These failures refute the
charging rule, not LC.

### 6.2 Resources only at the wedge's corner vertices — false

Even allowing multiple-root resources to move inside bridge/mutual
components does not fix all-simple corner triangles. On eligible
93 record 1 the corner-incident graph covers only three of 11 wedges.
Its Hall set consists of wedge vertices `{0,1,2,3,4,5,6,7}` with no
reachable resources. The word and full Hall obstruction are saved in
`note7_93/eligible_corner_incident_first_failure.json`.

The precise tested graph gives a Z slot to a wedge sharing its
endpoint, U/I labels to wedges sharing the origin/centre, corrected
quad units to wedges sharing the quad, and N tokens only to wedges
using that exact corner token. Its bridge/mutual variant pools the
multiple-root choices in their native component. Both fail on all
13,718 eligible 93 records. This is why a direct proof must transport
resources through simple vertices too.

### 6.3 Pool only through shared simple fan vertices — false

Join triangular faces if they share a simple vertex, including
opposite isolated fans. Attach a surviving single-edge N token to its
unique triangle, a U/I label to its centre, and a Z slot/other vertex
resource to its root's triangles. Pooling inside these components
still omits transport through the multiple bridge geometry.

**Exact eligible counterexample: binding record 5.**

```text
T=62, pi=12, U=5, I=1, Delta_N=30, E=180
wedges=6; matching covers4
Hall wedges={0,1}; reachable resources=0
wedge0 corner triangle={0,2,19}
wedge1 corner triangle={1,2,18}
```

The full word and injection are in
`note7_witnesses/eligible_simple_fan_pool_first_failure.json`.
There are also 140 eligible 93 failures, total deficit 449. Simple-fan
pooling passes all eligible earlier inputs, demonstrating why that
cohort alone would miss the gap.

## 7. Checked only: a wider direct transport graph

For each resource, take all pencil lines at its roots:

- a Z slot's endpoint;
- a U/I block's origin and centre;
- an N_res token's multiple root, even for an unbounded token;
- a corrected-slack quad, or all four corners for a K3/K4 bonus unit.

Permit the resource to cover wedge X when one of those pencil lines
is one of X's two endpoint lines. This is `wedge_line_pool` in the
checker. A universal Hall theorem for this graph would prove (B).
**That Hall theorem is open.** The graph is an explicit new target,
not a hand proof of physical transport.

The checker also freezes every payment from §5 and tests only the
unresolved wedges against the resources left over. This is
`locked_wedge_line_pool`. **The frozen extension rule is refuted:**
the locally valid partial injection cannot always be extended in
this particular transport graph without exchanging some payments.

| Cohort | Records, all / eligible | Free matching failures, all / eligible | Frozen matching failures, all / eligible |
|---|---:|---:|---:|
| 93 | 14376 / 13718 | 0 / 0 | 254 / 219 |
| Earlier | 3445 / 2259 | 0 / 0 | 84 / 71 |
| Bindings | 29 / 29 | 0 / 0 | 0 / 0 |

**Exact eligible counterexample to the frozen rule: 93 record 39.**

```text
T=93, pi=4, U=5, I=1, Delta_N=0, E=10, W=14
four local payments fixed; ten wedges remain; matching covers9
Hall wedges={3,9}; sole reachable resource=(U,origin132,centre134)
```

The complete word, four frozen payments, and Hall set are saved in
`note7_93/eligible_locked_wedge_line_pool_first_failure.json`.
Earlier gallery record 39 is the same arrangement and obstruction;
do not count those as independent counterexamples.

Thus §5 is a proved partial payment, **not** a safe irreversible first
step for §7. A completion needs exchanges, a broader transport rule,
or a separate proof for the remaining demands. It must not consume a
second copy of a U/I label or an already used central-cap token. All
recorded matchings are actual injections or explicit Hall obstructions.

## 8. Verification, files, and the remaining proof obligations

`note7_check.py` rebuilds the actual tokens from the accepted routines,
asserts the exact direct budget and pure-triple identities, audits
the new LC families and the partial wedge injection, and records every
conjectural allocation failure with a full word. It checks all records
before applying structural/triple-optimality eligibility.

Outputs (cohort sources overlap):

```text
all8_work/note7_93/{summary.json,records.jsonl}       14376 records
all8_work/note7_gallery/{summary.json,records.jsonl}   3445 records
all8_work/note7_witnesses/{summary.json,records.jsonl}   29 records
```

Reproduce:

```bash
python3 -m py_compile work/bbl/note7_check.py
python3 work/bbl/note7_check.py \
  work/bbl/all8_work/tradeoff_rebuilt93/metrics.jsonl \
  --out work/bbl/all8_work/note7_93
python3 work/bbl/note7_check.py \
  work/bbl/all8_work/tradeoff_gallery/metrics.jsonl \
  --out work/bbl/all8_work/note7_gallery
python3 work/bbl/note7_check.py \
  work/bbl/all8_work/tradeoff_all8_witnesses/metrics.jsonl \
  --out work/bbl/all8_work/note7_witnesses
```

The precise remaining Stage 1 alternatives are:

- prove LC for the larger mixed-sector/quad components **and** reconcile
  `r>=-c`; or
- complete the direct wedge injection, paying the two unresolved
  categories with exchanges of §5's local choices or broader transport,
  possibly by a proved version of §7's **unfrozen** Hall rule.

The old exact balance remains

\[
c+r=E-18+3\pi,
\quad c=2I+2U+\Delta_N-Q_0,
\quad r=\pi+\sigma+\Delta_Z+C_q-2I-(J-Q_0).
\]

`r>=0` remains refuted by eligible 93 record 8383. Neither the new
LC families nor the sample wedge matchings discharge reconciliation.
No completed Stage 1, excluded isolated double-B star, or proof of
`K(18)=93` is claimed.

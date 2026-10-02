# Touch/mutual/end decomposition and the pencil-touch lemma

**Status:** the full inequality is not yet proved. This note records an exact
payment decomposition and a proved generalized touch lemma. A separate global
SAT probe is running; a timeout/UNKNOWN is not a result.

The setting is n=18, multiplicity <=4, all 4-fold points of 7-type or all-8,
and at least one all-8 point. The pair lemma applies when explicitly used.
Let A,J count all-8 and 7-type points, and let b count blocks. The target is

    Z + sum_triple N/2 + 4A + 5J >= 7 + b/2.              (T)

## 1. Exact payment decomposition

At the simple far endpoint X of a block P X, exactly two, three, or four of
X's sectors are triangles. Classify the block as follows:

* U (touch): exactly two triangles at X; the continuation of its axis beyond
  X is bounded and unused.
* I (end): exactly two triangles at X; that continuation is unbounded.
* M (mutual): three or four triangles at X; a triangle beyond X pairs the
  block with a block on its cap, by Lemma A.

These alternatives partition the blocks. Let K count simple kite centres
(four triangular sectors), H count simple three-triangle vertices, and use U,I
also for the counts of the first two kinds. Then

    b = U + I + 2H + 4K.                                  (1)

A three-triangle vertex receives precisely two blocks, both mutual; a kite
receives four, all mutual. A two-adjacent-triangle vertex receives one block.
Opposite two-triangle vertices receive no blocks.

For an unused edge e let tau(e) be the number of touch blocks using its
endpoints. Each simple endpoint can support at most one such block on e's
line, so tau(e)<=2, and sum_e tau(e)=U. Therefore

    R = Z - U/2 = sum_unused e (1-tau(e)/2) >=0.            (2)

This pays every touch block without double-spending. However R must not be
silently discarded: it includes unused edges with zero touch blocks, and a
half-unit from each unused edge with exactly one touch block.

The target is now **exactly**

    R + sum_triple N/2 + 4A + 5J >= 7 + 2K + H + I/2.     (3)

In fact the left minus the nonconstant terms on the right equals Lambda.
A sufficient strengthening is Q>=7, where

    Q = sum_triple N/2 + 4A + 5J - 2K - H - I/2,
    Lambda = R + Q.                                       (4)

Q>=7 has not been proved here; neither has (3).

## 2. Pencil-touch lemma (does not require three triple neighbours)

This lemma works at an arbitrary m-fold point P.

Let E(P) be the set of its **non-mutual** block-ray indices, cyclically ordered
as 0,...,2m-1. Let C(P) be the set of their cap lines. Define

    h(P) = min_i |E(P) intersect {i,i+1,...,i+m-1}|,        (5)

with indices modulo 2m.

**Lemma.** If there is a line W that is neither through P nor in C(P), then
at least h(P) distinct unused edges are continuations of blocks at P.
In particular Z>=h(P).

A sufficient condition for W to exist is

    n > m + |C(P)|.                                      (6)

For n=18 and m<=4 this is automatic: |C(P)|<=2m, so at most
3m<=12 lines are excluded. No pair lemma, neighbour multiplicity restriction,
or all-8 hypothesis is required for the lemma itself.

**Proof.** Delete all lines except the m-line pencil at P and W. As W is
traversed it crosses each pencil line once, avoiding P. The sectors of a pencil
form a cycle of length 2m. W cannot reverse direction in this sector cycle:
its first reversed step would recross the pencil line of its previous step.
Consequently its m intersection points lie on m consecutive rays, a set H.

For each r in E(P) intersect H, let X be the simple far endpoint of the block.
W cannot meet its axis strictly between P and X (X is the first vertex).
It cannot meet it at X, since the two lines at X are the axis and its cap,
and W is neither. Thus W meets the axis strictly beyond X. The continuation
beyond X is bounded. Non-mutuality and Lemma A make it unused.

The m rays of H belong to m distinct pencil lines, so these unused edges are
distinct. Their count is at least |E(P) intersect H|>=h(P). QED.

**End-ray corollary.** Under the same existence condition, the end-block rays
at P are contained in m consecutive rays. Indeed they avoid H, and the
complement of H is another set of m consecutive rays.

This supplies a checkable local obstruction on **all** end-block directions
at a multiple point, not merely on two opposite end blocks.

## 3. Consequences at an all-8 point

In the n=18 class, h(P) is available unconditionally at every all-8 point.
In particular:

* If its non-mutual blocks meet every four-consecutive-ray set, then Z>=1.
* If every such set contains at least two non-mutual blocks, then Z>=2.
* If Z=0, all non-mutual blocks are ends, confined to four consecutive rays.
  Since an all-8 point cannot have three consecutive block rays, at most
  three of its blocks can be non-mutual. Thus beta=3 (five blocks) forces
  at least two mutual blocks; beta=4 (four blocks) forces at least one.

These are necessary conditions, not the desired global charge estimate.
They explain what any zero-touch candidate must force into kite/partner sites.

The three-leaf bridge-star subcase in ALL8_GB_NOTE.md can be strengthened.
The pair lemma forces each triple leaf to have its unique block opposite its
ray toward P. None of P's five blocks is therefore mutual. Its three bridge
rays point toward the corners of the enclosing cap triangle. No four-ray
half-pencil contains all three corner rays (restrict to the three corner
axes, where they alternate). Thus each four-ray half contains at least two
of P's five non-mutual blocks, giving h(P)>=2. The component costs 6, so

    Lambda >= 8 + sum(costs outside this component).       (7)

Outside costs still need control in the general situation.

## 4. What has and has not been validated

    python work/bbl/all8_block_check.py \
      work/eng/lattice/lattice18.jsonl \
      work/eng/lattice/lattice_family.jsonl \
      work/eng/lattice/mixed_all.jsonl

This checks (1)--(4), the half-pencil intersection statement, the end-ray
corollary, and (5) at every multiple point in the input arrangements.
The earlier direct checks covered 15,708 multiple points, 265 of them all-8,
with no failures; 392 had positive h(P), including six all-8 points.
These inputs include arrangements outside the reduced class, which is fine
for the pencil-touch lemma but is not evidence for the general target (T).

The lemma is often silent on the lattice interiors because their blocks are
mutual. **The remaining proof obligation is global control of 2K+H+I/2 in
(3), including unused-edge residual R and boundary triples' N charge.**
No argument treating all these costs as already paid has been established.

## 5. Global SAT probe

all8_work/global_sat.py uses the existing T27 signotope/triangle model,
all bad-word constraints with 6-type forbidden, existence of an all-8 point
without pinning its slope labels, exactly 94 triangles, and lazy pair clauses.
It is a search/certificate route, not an assumption in the arguments above.
The explicit 18-line component-cost=6 witness was pinned to its crossing
orders and returned SAT with exactly 29 triangles and no pair violations.
Any UNSAT must be proof-checked and the new encoding independently audited
before it can be called a solution. Any SAT must be converted to an actual
arrangement and its face count checked. UNKNOWN proves nothing.

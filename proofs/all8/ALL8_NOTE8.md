# All-8 Note 8 — Stage 1, the unfrozen Hall target

**Work in progress; Stage 1 remains open.** This Track 1 note is being
written while the main agent prioritises the last double-case-B star.
Inputs are `SOL_TASK8.md`, `STAGE1_ISOLATED.md`, `ALL8_NOTE7.md`, and the
accepted Note 2–6 payment definitions. No new completed trade-off proof
or SAT certificate is claimed.

## 1. Exact target and the no-freezing rule

The exact direct resource budget is

\[
R=2Z+U+I+N_{\rm res}+C_q=2\Lambda,
\qquad W=18-\pi.
\]

Thus an injection of bad-wedge vertices into these resources proves
`E>=18-3*pi`. Each U/I block supplies **one** direct label, not two;
the I label is part of this exact resource accounting, not new E-credit.
`N_res` includes the unbounded multiple-end tokens.

The accepted Note 7 partial wedge payments must not be frozen before
solving the remaining direct allocation: their extension in the
`wedge_line_pool` graph is false (eligible 93 record 39).

## 2. Proved: Hall is exactly a line-subset inequality

Let G_W be the bad-wedge graph on the 18 arrangement lines. A bad
wedge is an edge joining its two endpoint lines. For a direct resource
r, let P(r) be the set of all pencil lines through its roots, with the
same roots as Note 7: a Z endpoint; a U/I origin and centre; an N_res
multiple root; a corrected-slack quad; or the four corners of a K3/K4
bonus unit. Define

\[
\rho(S)=\#\{r:P(r)\cap S\ne\varnothing\}.
\]

Then the **unfrozen** wedge-line transport graph satisfies Hall if and
only if

\[
\boxed{|E(G_W[S])|\le\rho(S)\quad
       \hbox{for every set S of arrangement lines}.} \tag{H-S}
\]

For necessity, take all wedge edges induced by S. Their reachable
resources are a subset of the resources counted by rho(S), so Hall
implies the displayed bound. For sufficiency, let A be any subset of
wedge demands and S the union of their endpoint lines. Its resource
neighbourhood is exactly the set counted by rho(S), while
`A subset E(G_W[S])`. Thus `|A|<=|E(G_W[S])|<=rho(S)`.
This is a graph-theoretic equivalence, not a proof of the geometric
inequality (H-S).

The bad-wedge graph is a forest of paths in the accepted 18-line
setting. Therefore one may write the left side as `|S|-k(S)`, where
k(S) counts all components, including isolated vertices, of the
induced forest. Sets containing no induced wedge edge are automatic.
An attempted proof still has to control the **union** of roots' pencils,
not a sum of separate line capacities, which would count a resource
multiple times.

## 3. Proved: LC with one four-run triple, any component size

**Theorem.** Let C be a bridge/mutual component consisting of one
triple P with mask `111100` and a triples with mask `110110`. Then
`|D_C|<=M_C`. This allows any a, not just the accepted size-two case.
The structural and triple-optimality hypotheses are those of Note 7.

Let e be the number of double bridges of C, u its number of U/I
blocks, h its number of mutual three-fan centres, k its number of K0
centres, and F its number of unbounded N rays. The accepted pure-triple
identity is

\[
M_C=2a+2e-F.                                         \tag{2}
\]

Only P can have an unbounded first ray: each ray at an opposite-four
triple is beside a triangle, and the four-run triple has exactly one
ray beside two missing sectors. Thus `F<=1`. Also `e>=1`: P has three
consecutive double rays, and they cannot all be blocks.

All component links join vertices sharing an arrangement line, so a
spanning-tree ordering gives

\[
|L(C)|\le3+2a.                                      \tag{3}
\]

**Case e>=2.** Equation (2) gives `M_C>=2a+3>=|L(C)|`, proving LC.

**Case e=1.** The sole bridge joins P to an opposite-four triple Q.
At P it is the middle of the three consecutive double rays: otherwise
the two other double rays would be consecutive blocks. Denote its
supporting line by L. The opposite ray at P is unused. If bounded it
contains an unused segment; if unbounded P is a multiple end on L.
Either way `L notin Q0`, hence `L notin D_C`.

If F=0, equations (2)–(3) and this one excluded line give
`|D_C|<=2a+2=M_C`. If F=1 and some U/I block has an axis A different
from L, that axis also lies outside Q0 (a touch has an unused segment,
an end block gives a non-W end). The two exclusions give
`|D_C|<=2a+1=M_C`.

It remains to treat **F=1 with every U/I axis equal to L**. The block
count is `B_C=2a+1`, so

\[
u+2h+4k=2a+1;                                      \tag{4}
\]

in particular u is positive and odd. Select the h central cap edges
of the three-fans and all 4k cap edges of the K0 centres. Every selected
cap is **single**. At least one endpoint is an opposite-four triple;
its block toward the fan centre and its ray toward the other cap
endpoint are consecutive. A double cap would therefore give two
consecutive double rays at a `110110` vertex, impossible. Selected
caps are distinct: their unique incident triangles identify their fan
centres. Together with the bridge PQ, there are `1+h+4k` selected,
distinct elementary edges between vertices of C.

P has no U/I block on L, since its only double ray on L is the bridge.
Q has at most one. Every other U/I origin has at most two blocks, so
there are at least `(u-1)/2` distinct U/I origins besides P,Q on L.
Each is isolated in the selected-edge graph on L: both its first rays
on its U/I axis L are double, whereas all selected cap edges are
single; it is not an endpoint of PQ.

For a pencil line A containing r_A vertices of C, the selected edges
on A are edges in the ordered path of those vertices. Hence their
count is at most `r_A-1`. On L the isolated origins improve this by
at least `(u-1)/2`: the graph has the component containing PQ and that
many additional isolated components. Summing over pencil lines,

\[
\begin{aligned}
3(a+1)-|L(C)|
 &=\sum_A(r_A-1)\\
 &\ge1+h+4k+(u-1)/2\\
 &=a+1+2k,\qquad\text{by (4)}.
\end{aligned}
\]

Therefore `|L(C)|<=2a+2-2k`; after excluding L,

\[
|D_C|\le2a+1-2k\le2a+1=M_C.
\]

This closes the final branch and proves the theorem. All edges used
for the compression are actual consecutive-vertex segments; no
straight-line angle or extra transport assumption is used. ∎

## 4. Proved: LC with one five-run triple, any component size

**Theorem.** LC also holds when C consists of one triple P of type
`111110` and a opposite-four (`110110`) triples.

Every ray at these vertices is beside a triangle, hence F=0. The
five-run vertex has four consecutive double rays; at most two can
be nonconsecutive blocks, so `e>=2`. The capacity identity is

\[
M_C=2a-2+2e,\qquad |L(C)|\le2a+3.                    \tag{5}
\]

If e>=3, capacity dominates all pencil lines. If e=2 and there is
a U/I block, its excluded axis gives `|D_C|<=2a+2=M_C`.

If e=2 and every block is mutual, the block count is 2a, hence
`h+2k=a`. As in §3, all h central three-fan caps and all 4k kite
caps are single: each cap has an opposite-four endpoint. Those
distinct cap edges and the two distinct bridges are elementary
edges between C's vertices. Summing their ordered-line compression,

\[
3(a+1)-|L(C)|\ge2+h+4k=a+2+2k.
\]

Thus `|L(C)|<=2a+1-2k<=2a+2=M_C`. This proves the remaining branch
and LC. ∎

## 5. Still open

The new reduction (H-S) does not yet give a geometric Hall proof.
Alternatively, the LC route still needs the larger mixed-sector/quad
components and the independent end reconciliation. Accepted Note 7
LC families and its exact counterexamples remain unchanged.

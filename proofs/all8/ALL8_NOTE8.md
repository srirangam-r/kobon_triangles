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

## 3. Still open

The new reduction (H-S) does not yet give a geometric Hall proof.
Alternatively, the LC route still needs the larger mixed-sector/quad
components and the independent end reconciliation. Accepted Note 7
LC families and its exact counterexamples remain unchanged.

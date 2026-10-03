# Task 8 Stage 2 — excluding a quad first outer apex

**Live handoff; updated during the Task 8 run.** A new conditional hand
proof excludes a quadruple first outer H-apex V. Consequently both
first outer apices of an isolated double-B star must be triple. The
triple branches and the whole star remain open at this checkpoint.
The proof below awaits the lead's review. No new SAT result is claimed.

The main agent prioritizes Stage 2. The existing Stage 2 subagent
independently audits this work; a separate subagent pursues Stage 1
and owns `ALL8_NOTE8.md`. A background reader watches the lead's
`SOL_TASK*.md`, `STAGE1_*.md`, and `LEAD*.md` files every ten seconds.

## 1. Assumptions and correction to the suggested H-chain

Use all accepted Task 6–7 zero-corner reductions: proper pairwise-once
pseudolines, n=18, multiplicity <=4, triple optimality, U=Delta=0,
every corrected quad slack zero, K3=K4=0. All remaining quads are
isolated opposite-double-case-B stars. Full case-B corners, multiple
exterior apices, and multiple first outer H-apices are accepted inputs.

There is a direction issue in the suggested chain in `SOL_TASK8.md`.
If V is quad, VT is the **middle bridge** of a three-bridge run at V.
Therefore H is V's bridge axis, not its case-B block axis. The next
H-vertex after V is a multiple bridge neighbour, not a case-B centre
X'. The proposed repeated sequence `P,X,T,V,X',T''` must not be used
as a pin. The contradiction below uses the correct transverse star.

Along any arrangement line L the exact crossing budget is
`sum_{vertices on L}(multiplicity-1)=17`, not 17 distinct vertices.

## 2. Setting up the return vertex

Let P be the original double-B star. Its positive case-B kite is
`(P,A,T,F)`, with centre X and axis H=PT. Put D0=AXF. Let

\[
Y=(PA)\cap(TF),\qquad Z=(PF)\cap(TA),
\]

and let V be the first H-vertex beyond T. By accepted Task 7,
Y,Z,V are multiple and the faces TVY,TVZ are all-multiple, hence double.

Let b,c be the original opposite-side cap axes, meeting H at the
negative far triple T_minus. Full A,F supply return vertices

\[
U=D0\cap b,\qquad U'=D0\cap c,
\]

with faces ABU,AYU and FCU',FZU' (B,C are the original next bridge
neighbours toward the negative side). If Y is triple, its third axis
is e=YV=YU; if Z is triple, its third axis is g=ZV=ZU'. This is the
accepted return-axis pin, not an assumption at quad Y or Z.

## 3. New hand exclusion: V cannot be quadruple

Assume V quad. Its three consecutive bridge neighbours Y,T,Z force
the double-B zero mask with VT the middle bridge. The quad-neighbour
exclusion makes Y,Z triple. They are diagonal corners of V's two
case-B kites and are consequently **full** by the accepted case-B
boundary lemma.

Consider the case-B kite at V adjacent to Y. Write it as
`(V,Y,R,F_v)`, centre X_v, where F_v is the bridge neighbour opposite
Z at V. Triple-cap continuation across VY, whose exterior face is
VYT, puts the other cap YR on TY's axis TF, away from T. The kite
diagonal YX_v is therefore PA, away from old A. At Y the cyclic rays
are, in one orientation,

```text
old A (PA), old T (TF), V (e),
new centre X_v (opposite PA), new far R (opposite TF), U (opposite e).
```

Because Y is full, the sector between R and U is the actual
all-multiple face **YRU**. Triple-cap continuation at R puts its
side RU on the new far cap

\[
\ell=RF_v.
\]

The near exterior face at F_v makes this same cap contain V's
opposite middle bridge neighbour T_v on H, beyond V away from T.
In particular, the following are four distinct supporting axes at U:

| Axis at U | Its crossing with H |
|---|---|
| D0 | old centre X |
| b | old negative far triple T_minus |
| e | V |
| ell | T_v, strictly beyond V |

Unique pair crossing makes them distinct, so U is a quadruple.

Faces ABU and AYU give three consecutive **bridge** rays UB,UA,UY
at U. Its zero mask must therefore be double-B, with UA the middle
bridge and the fourth axis ell its case-B **block axis**. But the
face YRU supplies a bounded edge UR on ell with R multiple; all-
multiple saturation makes UR double. Thus ell is a **bridge** ray
at U, contradicting the required block axis.

Hence V is not quadruple. This proof applies independently to both
ends of the old star and uses no straight-line geometry. ∎

## 4. Immediate solver pin and remaining task

With T represented as H^t, V as H^v and d pointing outward:

```text
zero-star boundary guard AND A^d(H,t,v) =>
    zp[H,v] AND NOT zp2[H,v].
```

The positive `zp` is the accepted Task 7 pin; the negative `zp2` is
new. The implication is guarded by the full global zero-corner
assumptions, not an arbitrary case-B kite in a nonzero arrangement.

Both V endpoints are now triple, with mask 111100, 111110 or full.
The four-run branch is terminal on H by eta0=0. Further triple-branch
proofs, checks, and pins will be appended here. The isolated double-B
star itself is not yet excluded.

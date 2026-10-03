# Task 8 Stage 2 — excluding a quad first outer apex

**Live handoff; updated during the Task 8 run.** Two new conditional
hand proofs exclude quadruple first outer H-apices V and quadruple
far-cap side apices Y,Z. A third proof excludes the five-run triple V.
Thus all six exterior apices at the two ends of an isolated double-B
star are triple, and at least one V is full. The full-triple branch
and the whole star remain open at this checkpoint. The lead has
accepted §3 and encoded `--vtriple`; §§4 and 6 have been independently
cross-audited and await review. No new SAT result is claimed.

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

Fix the following ten-line normal form. P's pencil is H,p,q,r, with
A on p, F on q, and middle bridge B on r. The opposite kite is
`(P,C,T_minus,D)`, centre X_minus and diagonal D1=C X_minus D,
where C is on q opposite F and D is on p opposite A. Put

```text
a=TA, f=TF, b=T_minus C, c=T_minus D,
B=r intersect a intersect b, E=r intersect f intersect c.
```

Thus b,c are the original opposite-side cap axes, meeting H at the
negative far triple T_minus. Full A,F supply return vertices

\[
U=D0\cap b,\qquad U'=D0\cap c,
\]

with faces ABU,AYU and FEU',FZU'. If Y is triple, its third axis
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

## 4. New hand exclusion: Y and Z cannot be quadruple

Use the normal form in §2. The opposite exterior apex paired with C
is `Ybar=q intersect c`, with old return `J=D1 intersect a` and first
opposite H-apex Vbar. We call the return J to avoid confusing it with
either old kite centre.

Assume Y quad. Its three consecutive first bridge rays YA,YT,YV
force its zero mask to be double-B. Face AYU occupies the adjacent
sector before YA; hence YU is a **block** ray. Thus U is a simple
kite centre. Its four corners are `(Y,A,B,W)`, with W beyond U on D0.
At triple B, cap continuation puts the new cap BW on its remaining
axis r, so `W=D0 intersect r`. This is a case-B kite of Y; its other
three corners A,B,W are consequently triple and full. The axis YW
is e=YV, whereas YU is b. In particular Y's axes are p,f,b,e.

At newly full B the cyclic rays are

```text
A (a), P (r), C (b), J (opposite a), W (opposite r), U (opposite b).
```

Full B supplies faces BWJ and BCJ. Old full C already fixes BCJ and
CYbarJ, with J on D1 beyond C away from X_minus. Triple-cap
continuation at W, across BW, puts J on W's other cap WY=e. Thus

```text
J lies on D1, a, e,
whose H crossings are X_minus, T, V, respectively.
```

These three axes are distinct, so J is multiple. If Ybar were quad,
the same three-bridge mask argument would make its return J simple.
Therefore Ybar is triple. The accepted return-axis pin puts J on
h=Ybar Vbar. Its H crossing is Vbar, distinct from all three above.
Consequently J is quad.

But the actual faces BWJ, BCJ, CYbarJ give **four consecutive bridge
rays** JW,JB,JC,JYbar on its four distinct axes e,a,D1,h. All these
edges are double by all-multiple saturation. The zero double-B mask
has no run of four consecutive bridges. Contradiction.

Hence Y is triple. Reflection proves the result for Z, and the same
argument at the opposite kite proves its two exterior side apices
triple. No triple-only continuation has been applied at J. ∎

## 5. Immediate solver pins and remaining task

With T represented as H^t, V as H^v and d pointing outward:

```text
zero-star boundary guard AND A^d(H,t,v) =>
    zp[H,v] AND NOT zp2[H,v].
```

The positive `zp` is the accepted Task 7 pin; the negative `zp2` is
new. Also, for each of the four side apices:

```text
zero-star boundary guard => Triple(Y), Triple(Z)
    [at each end; Triple means zp AND NOT zp2].
```

The implications are guarded by the full global zero-corner
assumptions, not an arbitrary case-B kite in a nonzero arrangement.
In particular the previously conditional return-axis pins are now
unconditional within this guard: every return U is multiple and lies
on its side-apex/outer-apex supporting line.

Both V endpoints are now triple, with mask 111100, 111110 or full.
The four-run branch is terminal on H by eta0=0. The lead's new
Addendum 1 excludes both ends being four-run: then the entire H order
is `Vbar,T_minus,X_minus,P,X,T,V`, consuming only
`2+2+1+3+1+2+2=13` of the required 17 weighted crossings. Therefore
at least one endpoint is five-run or full. This is now the only
remaining multiplicity branch; the suggested quad lattice
propagation is contradicted locally by §3 before it can iterate.

Section 6 now excludes five-run too. Consequently at least one
endpoint is full. The isolated double-B star itself is not yet
excluded.

## 6. New hand exclusion: V cannot have five sectors

Assume V is a five-run triple. One of its two outer rays is double;
write its first vertex W. The opposite outer ray is single, and the
first outgoing H-edge VS is single. A fifth triangular sector forces
S to exist beyond V. Reflect if needed so that W is opposite Y on
e=VY. By §4 Z is triple, and the mandatory face VZW puts

```text
W=q intersect e, with W beyond Z on q away from F.
```

The extra fifth face is VWS. If W were simple, Z and S would lie on
its unique other axis q. Then S would be `q intersect H=P`, on the
wrong H-ray. Therefore W is multiple.

Since VS is single, S cannot be multiple: the all-multiple face VWS
would make VS double. Thus S is simple. If WS were single too, the
one-fan triangle VWS would have its two simple-adjacent sides single
and supply surviving O* credit, contrary to Delta=0. Hence WS is
double.

W cannot be quad: a double block from quad W to simple S must end
at a zero-quad kite centre S, making SV double as well. Thus W is
triple. At W the actual faces VZW and VWS give consecutive rays

```text
WZ (q), WV (e), WS (k), -q, -e, -k.
```

The second triangle on the double edge WS must consequently use
the opposite q-ray at W. At simple S it uses the H-ray away from V.
Its apex would be `q intersect H=P`, which lies behind V, not beyond
S away from V. This is impossible for proper pairwise-once lines.

The reflected five-run orientation has the same contradiction.
Therefore V has either four sectors or all six sectors. ∎

Additional solver pin, with the same zero-star guard:

```text
Triple(V) => mask(V) is 111100 or full; never 111110.
both endpoints => at least one is full.
```

As with all pins here, rotate/reflect the masks using the actual
ordered rays and adjacency aliases. No implementation or new SAT
certificate is asserted.

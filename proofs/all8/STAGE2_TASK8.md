# Task 8 Stage 2 — excluding a quad first outer apex

**Live handoff; updated during the Task 8 run.** Two new conditional
hand proofs exclude quadruple first outer H-apices V and quadruple
far-cap side apices Y,Z. A third proof excludes the five-run triple V.
Thus all six exterior apices at the two ends of an isolated double-B
star are triple, and at least one V is full. The full-triple branch
and the whole star remain open at this checkpoint. The lead has
accepted §§3,4,6 and encoded `--vtriple` and `--ttriple`. Further
cross-audited pins are in §§7–9; an important qualification to the
lead's Addendum 5 is in §10. No new SAT result is claimed.

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

**Accepted by the lead.** Its shorter independent proof is useful:
quad Y would make its adjacent return U simple, on Y's fourth axis.
But U lies on D0 and b; neither contains Y (`D0 intersect p=A`,
`b intersect p=the opposite exterior side apex`). No third axis is
available at simple U. The following longer cross-audit independently
recovers a forbidden four-bridge return.

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

## 7. New pin: at least one return on each old diagonal is triple

The four returns are already multiple. Suppose U on D0 is quad.
Its actual faces ABU,AYU give the three consecutive bridges B,A,Y,
so it is double-B. Consider its kite adjacent B. At B the exterior
face UBA puts its other cap BR on a, away from A; the kite diagonal
is r. Write d for this kite's block axis at U, R for its far triple,
and F_u for its other diagonal corner, on e opposite Y.

B is now full. Its face BCR and old full C identify
`R=D1 intersect a`, the opposite old return, which is therefore
triple. Its three axes are a,D1,d, so its other kite cap RF_u is D1.
Full U supplies the exterior face UF_uJ0, where J0 is U's opposite
middle bridge on D0 away from A. Triple-cap continuation at F_u
puts J0 on RF_u=D1. Therefore

```text
Quad(U) => J0=D0 intersect D1 lies beyond U away from A.
Quad(U') => the same J0 lies beyond U' away from F.
```

But D0 has order `U,A,X,F,U'`. These two rays are disjoint, so the
two assertions cannot both hold. At least one of U,U' is triple.
The same proof holds for the two returns on D1. This does **not**
yet prove every return triple. ∎

## 8. New hand exclusion: the next vertex S after full V is not quad

Let W=q intersect e and K=p intersect g be the two outer tips. Full
V gives faces VZW,VWS,VSK,VKY. Both W,K are multiple: a simple W
would put S on q and hence S=P, on the wrong ray, and similarly K.
Thus ZW and YK are double by all-multiple saturation. Together with
their four previously known double first rays these make Z,Y full.

Suppose S quad. Its three consecutive bridges W,V,K force the
double-B mask; W,K are full triples. By §7 choose U' triple and use
the W side, or choose U triple and reflect the whole argument.

S's kite adjacent W has diagonal q, far triple R, cap WR=e, and
other diagonal corner F_s opposite K. At full W its cyclic rays are

```text
Z (q), V (e), S (SW), new centre (-q), R (-e), M (-SW).
```

Full W gives ZWM. Full Z fixes M on a and also gives ZU'M.
Triple U', whose known axes are D0,c,g, forces M onto c. Full W
also gives WRM; triple-cap continuation at R puts M on the other
new far cap ell=RF_s. Full S and triple F_s put S's next H-neighbour
T_s, beyond S away from V, on this same cap. Thus M lies on four
distinct axes a,c,SW,ell, with distinct H crossings T,T_minus,S,T_s.
Consequently M is quad.

The actual faces U'ZM,ZWM,WRM force four consecutive bridge rays
MU',MZ,MW,MR. This contradicts the zero double-B mask. Therefore
S is **simple or triple**, not quad. ∎

## 9. New terminal pin: simple S is an I-end on H

Continue with full V. W,K are multiple and Y,Z full as in §8.
Assume S simple, so its other supporting line k contains W,S,K.

If SW were double and W triple, the two faces VZW,VWS give cyclic
rays WZ(q),WV(e),WS(k). The other WS face would join the opposite
q-ray at W to the opposite H-ray at S, forcing apex P=q intersect H
beyond S. This is the same wrong-ray contradiction as §6.

If SW were double and W quad, S would be a zero-quad kite centre,
with corners `(V,W,R,K)` and far R beyond S on H. A triple K would
put KR on its remaining axis p, forcing R=P on the wrong ray; hence
K is quad. K3=0 makes R triple. At W the mixed K2 kite block is
flanked by triples V,R, forcing the already excluded alternating
zero mask. Thus SW cannot be double. Symmetrically SK is single.

S is therefore a two-fan: SV double, SW and SK single, its opposite
H-ray unused. If that ray were bounded, SV would be a touching U
block, contrary to U=0. Hence S is the last H-vertex and SV is an
I-end block. ∎

Together with the 17 weighted H-crossings, this forces **at least one
full V whose next S is triple**: if every full V ended at a simple
S, the total would be at most `13+1+1=15`, not 17. This is the
remaining target; no exclusion of that S-triple continuation is
claimed yet.

## 10. Input audit: Addendum 5 needs triple-return guards

The lead's full B± conclusion is valid. However the asserted
concurrencies `G=b intersect e1 intersect e4` and the corresponding
G' require the involved returns to be **triple**, not just multiple.
The main agent and independent auditor agree on this qualification.

At a triple U, the exterior sector across UB indeed uses the ray
opposite UY=e. At a quad U, the three bridges UB,UA,UY force a
double-B mask, and that exterior sector instead uses its **fourth
block axis d**. The next old r-neighbour beyond B can then be the
simple centre `r intersect d` of U's new kite, while `r intersect e`
is the distinct opposite triple corner. These must not be aliased.

Therefore retain the 14 distinct baseline axes and their crossings
with H,p,q, but do not impose G/G' concurrency or use their asserted
triple rows without guards. Either first exclude all quad returns,
or split this geometry into the triple and quad return branches.
Section 7 currently excludes only both returns on one diagonal
being quad, not every quad return individually.

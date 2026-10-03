# Stage 1: the local capacity inequality LC for isolated multiple points

**Status: proved (hand proof, not refereed). Partial progress on Stage 1; LC for larger components and the end
reconciliation remain open.**

## Setting

An arrangement of n ≥ 6 pseudolines (n = 18 in the application). Assumptions:
- the arrangement lies in the structural class, and every triple point satisfies triple optimality (both alternating
  sector sums ≥ 2);
- the definitions and accepted rules are those of `ALL8_NOTE2.md` to `ALL8_NOTE6.md`;
- a *component* is a bridge/mutual component (`ALL8_NOTE6.md` §7). Double bridges join their two multiple ends, and
  the origins of blocks ending at a common simple three-fan or four-fan (kite) centre are joined.

LC is the inequality |D_C| ≤ M_C = U_C + I_C + d_C (`ALL8_NOTE6.md` §7):
- D_C is the set of demanded lines meeting C, i.e. lines with two bad-wedge ends, no unused bounded segment, and not
  the cap line of any U/I block;
- U_C + I_C counts the touch and end blocks with origin in C;
- d_C counts the bounded residual N tokens at vertices of C.

## Lemma (isolated triples)

Let P be a triple point that forms a component by itself. Then:
- **(a)** The sector pattern at P is `110110`. One line ℓ through P carries blocks on both of its rays at P, and the
  four rays of the other two lines are singly used and bounded.
- **(b)** Both blocks end at simple two-fan centres, so each is a touch (U) or end (I) block. At least one is a touch
  block.
- **(c)** The four tokens at P are exactly the tokens spent by the two blocks' outer-triangle payments. Hence d_P = 0
  and M_{P} = 2.
- **(d)** ℓ is not a demanded line, so |D_{P}| ≤ 2 = M_{P}. **LC holds for every component of size 1.**
- **(e)** U ≥ the number of isolated triples. In particular, if U = 0 then every triple has a double bridge or is
  the origin of a mutual three-/four-fan block.

In a 94 every fourfold point is all-8 or of type 11111110 (structure theorem and the 11101110 exclusion). By "no three
consecutive quadruple blocks" (`ALL8_NOTE3.md` §2), such a point has a double bridge. So in a 94 every component of
size 1 is a triple, and (d) covers all of them.

## Proof

**(a)**
- P has no double bridge, so every double ray at P is a block, i.e. a double first segment ending at a simple vertex.
- Two blocks at a triple are never consecutive (`ALL8_NOTE2.md` §2). So no three cyclically consecutive sectors at P
  are triangles.
- Suppose no two consecutive sectors were triangles. Then the triangular sectors would form an independent set in
  the 6-cycle. Such a set has at most 3 elements, and with 3 it is a whole alternating class. Either way one
  alternating sum is ≤ 1, contradicting triple optimality.
- Hence some ray j is double: s_{j−1} = s_j = 1, and by the above s_{j−2} = s_{j+1} = 0.
- Optimality then forces the rest:
  - the class {j−1, j+1, j+3} gives 1 + 0 + s_{j+3} ≥ 2, so s_{j+3} = 1;
  - the class {j, j+2, j+4} gives 1 + s_{j+2} + 0 ≥ 2, so s_{j+2} = 1.
- So the pattern is 110110. Rays j and j+3 (one line ℓ) are double and the other four rays are single.
- Every ray is adjacent to a triangular sector. A sector adjacent to an unbounded ray is an unbounded face, so every
  ray at P is bounded.

**(b)**
- The centre X of the block on ray j is simple, and the two triangles of P beside ray j have X as a vertex.
- If X had a third triangle, X would have a second double ray. By L1 that ray ends at a multiple vertex Q, so P and Q
  would be origins at a common three-fan centre, joined in one component.
- If X had four triangles (a kite centre), all four corners would be joined at the common four-fan centre.
- Both contradict isolation. So X is a two-fan whose two triangles lie beside XP, on the same side of the cap line.
  The continuation of ℓ beyond X has no triangle on either side.
- If that continuation is bounded, it is unused and the block is a touch block. Otherwise it is an end block.
- If both blocks were end blocks, ℓ would have exactly the three vertices X, P, X′, giving n = 5 (opposite-I lemma,
  `ALL8_NOTE5.md` §4).

**(c)**
- The triangle of sector j has vertices P, X and the first vertex T on ray j+1. PT is single, so the outer-triangle
  rule (`ALL8_NOTE2.md` §4.1, §4.3) charges the token of P on ray j+1. Likewise sector j−1 charges ray j−1 = j+5.
- The block on ray j+3 charges rays j+2 and j+4. These four tokens are distinct and are all the bounded tokens at P.
- By payment locality (`ALL8_NOTE6.md` §7), a payment charged to another component takes its token in that
  component, so nothing else is charged at P.
- So d_P = 0, U_P + I_P = 2, and M_{P} = 2.

**(d)**
- By (b), ℓ carries a touch block. Its unused continuation is a bounded unused segment of ℓ, so ℓ is not demanded.
- So D_{P} ⊆ {the other two lines}.

**(e)** By (b), each isolated triple is the origin of a touch block. Distinct origins give distinct blocks. ∎

## Data check

The note6 component records contain no component of size 1 that is not a triple. Every component of size 1 is a
triple with M = 2:
- 15,617 in the 93 corpus;
- 2,166 in the earlier datasets;
- 20 in the binding witnesses.

These are about 97% of all eligible components, and they include every component on which LC is tight. Components of
size ≥ 2 have LC slack ≥ 1 in every dataset.

The inequality U ≥ #isolated triples holds on all eligible records, with 0 violations:
- 13,718 in the 93 corpus;
- 2,259 in the earlier datasets;
- 29 in the binding witnesses.

It is tight on 4,088 of them.

## What remains for Stage 1

- **LC for components of size ≥ 2.** These are triples and fourfold points joined by double bridges or mutual fans.
  The data leave at least one unit of slack, so a cruder local argument may suffice.
- **The end reconciliation** r ≥ −c (`ALL8_NOTE5.md` §1). LC, and with it O2Q, does not by itself give (B).

# Shared-line cases at n = 18: status (third round, partial)

Referee verdicts (see notes.md): the three-triple-point proof is correct, and Theorem H
(general position) is correct.

## (1) t >= 7 triple points with shared lines (no 4-fold points)

**Setup.** Let b(P) be the number of blocks at P, and e(P) the number of doubly used
bridges ending at P. Then D = sum_P (b(P) + e(P)/2) and S = 288 - 3t. A 94 needs
B + beta - Z >= 3t - 6. Equivalently:

  **(*)  sum_P [ b(P) + e(P)/2 - 2 ] >= t - 6 + Z >= 1.**

**Lemma C (proven): what each kind of point can contribute to (*).**
Write c(P) = b(P) + e(P)/2 - 2.
- *Two disjoint blocks (axis point):* e(P) > 0 only through triangular faces PQR whose
  three vertices are multiple, one in each non-cap sector (Lemma B). So c(P) <= 0 if P
  lies in no such face, and c(P) <= 2 otherwise.
- *Bent point toward Q:* the doubly used segment [P,Q] gives e >= 1. Any further bridge
  end needs a cap line through Q and a second multiple point (proof of Lemma B). So
  c(P) <= 1/2 without such a cap line, and c(P) <= 3/2 with it.
- *One block:* c(P) <= e/2 - 1. Every bridge end needs a multiple first vertex on that
  ray. So c(P) > 0 needs at least 3 bridge ends.
- *No blocks:* c(P) <= e/2 - 2, so c(P) > 0 needs at least 5 multiple neighbours.
- *Three blocks (centroid type):* this needs three multiple first vertices; c(P) = 5/2.

**Consequence (proven).** A 94 with t >= 7 must contain enough "bridge-rich" points to make
the sum in (*) at least t - 6 + Z. Only these can contribute:
- triangular faces whose three vertices are multiple;
- bent pairs;
- 1-block or 0-block points with many multiple neighbours;
- centroid-type points.

In particular, **t >= 7 is impossible in each of these cases:**
- beta = 0. Here D <= 2t, so 3T <= 288 - t <= 281.
- No bent point, no centroid point, no triangular face with three multiple vertices, and
  no point with at least 3 bridge ends. Then every c(P) <= 0 < 1.

**Not proven.** Mixed configurations built from bent pairs and multiple-vertex faces, where
(*) might hold. Killing them needs a lower bound on Z (for example unused back segments at
bent points), which I did not finish.

**Tested.** Every gallery arrangement with t >= 7 has beta = 0:
- n = 18: t = 7 (40 arrangements), t = 8 (17);
- n = 20: t = 7, 8;
- n = 22: t = 7-9.

So (*) never comes close in known arrangements. Note that the n = 18, t = 8 arrangements
have Z = 0, so every axis point in them is killed by mutual pairs. Mutual pairs are
therefore common, not exotic.

## (2) Stalled 4-point case, (3) R2, (4) R3

No progress this round; all three remain open as described in general.md section 6.

The t = 8, Z = 0 examples above suggest (2) is genuinely hard: in real 93s, mutual pairs
can kill Lemma A at every point. The missing credit must therefore come from somewhere
other than cap touches.

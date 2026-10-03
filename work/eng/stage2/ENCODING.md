# Stage-2 encoding notes (stage2_sat.py, run_cube.py)

Lines are labelled 0..17 by slope. Model = classsat/patsat_m signotope model (z/pz/ng per triple) + ends_probe.augment.

(a) Literals
- z[key3(a,b,c)] : lines a,b,c concurrent. zp[i,j]: vertex i^j is multiple. zp2[c,L]: vertex L^c is >=4-fold
  (>=2 further lines through it). No 5-fold, so zp2 means exactly 4-fold.
- A[L,x,c] : on line L, vertex L^x is immediately followed (increasing position, direction '+') by the vertex L^c,
  distinct vertices, nothing between. A[L,c,x] is the '-' direction. Same vertex for any representative line x, x'
  with z[L,x,x'].
- kite[p,q] : p^q simple and all four sectors triangular (kite centre).
- kr[L,x,d] (d=+1/-1) : the far end of the ray (L,d) from the vertex L^x is a kite centre
  = OR_c ( A[L,x,c] (d=+1) or A[L,c,x] (d=-1)  and kite[min(L,c),max(L,c)] ). Hence that ray is a kite block.
- cb[L,x,d] : as kr, and in addition that kite has exactly one 4-fold corner (so it is P, the vertex L^x)
  and all four cap edges are doubly used (case-B K1 kite). cb implies kr.
- Use/Use2[r,i,j] : segment of r between vertices r^i, r^j has a triangle on >=1 / both sides (exact, over all
  representatives of both end vertices). c10 (per quad Q, guarded by conc(Q)): sum_over_8_rays kr + cb = 4.

(b) Pin far(mm, quadf) in run_cube.py
Ray index mm in 0..7 follows quad_ring order: mm<4 is (quad[mm], +), mm>=4 is (quad[mm-4], -).
For ray (L,d) take x = min(quad \ {L}) (any other line of the quad is at the same vertex P).
far = OR_{c not in {L,x}} ( A[L,x,c] (d=+1) / A[L,c,x] (d=-1)  AND  (zp2[L,c] if quadf else NOT zp2[L,c]) ).
For a non-block ray (mask char '.', double first segment because all 8 sectors are triangles) the far end is
multiple, so far(.,False) means "first multiple neighbour is exactly triple", far(.,True) means 4-fold.
Mask chars: K kite block, C case-B kite block, '.' bridge ray. Pins used (sound only given the cited lemmas):
double-B (C..., two opposite C): six '.' rays all triple. single-B (blocks C at i, K at i+3, i+5): ray i+4 quad,
other '.' rays triple. alternating endpoint: exactly one of the four '.' rays quad (WLOG endpoint). The old K1A pin
was never used.

(c) Second quad
Yes. kr, cb, kite, nq1, dall, cq, D and sec exist for ALL pairs/(L,x,d), and c10/conc(Q) exist for ALL 3060 quads
(S2.gq only in guard mode). So for a path P-Q on line H with Q = {H, a,b,c} unknown, one can state pins on Q as a
disjunction over quads, or fix Q's lines in a finer cube (z units on its 4 triples, kr/cb units on its 8 rays via
kr[L,min(Q\L),d]; the mask of Q for a single-B/single-B path is the 180-degree-related single-B mask with its
Q4 ray = the ray toward P). Nothing extra needs to be built.

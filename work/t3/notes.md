# Three triple points: T <= 93 (18 lines, no 4-fold point, no 3 mutually parallel)

Identity: 2Z = sum_L kappa(L) + Z_tr (kappa(L) = touches at simple endpoints attributed to the other line
L through that endpoint; Z_tr = triple endpoints of unused segments). With B blocks, beta doubly used
bridges (segment between two consecutive triple points), x blocks whose cap is a triple line, sigma =
9 - #triple lines: clean >= 9 + sigma - B + x.  T <= 93 follows from Cred >= need, where
Cred = 2Z - sum_clean kappa and need = 3B + 2beta - x - 14 - sigma.

Lemma A (cap touch). P has 2 disjoint blocks, axis a, cap point X = X_{p+1}, cap C.  If the face beyond X
on side s is a triangle, then [X,V_s] (on C) is doubly used, so V_s is a triple point Q, C passes through Q,
and a caps a block of Q with middle [Q,X] ("mutual pair").  Otherwise l_{p+1} is unused (if bounded) and is
touched at X by C (not clean).  At least one of l_{p+1}, l_{p-2} is bounded.  So each type-X point gives one
touch by a cap line unless it has a triple-capped block.

Lemma B (bridges).  If P has two disjoint blocks, no bridge at P is doubly used unless PQR is a triangular
face with all three vertices triple.  A bent pair (blocks sharing ray P->Q) has both caps through Q.

Case analysis: see report.  Empirical: lemmas.py (gallery, 5516 arrangements), walk.py (flip/collapse/expand
random walks, ~1000 k=3 arrangements): no failures.

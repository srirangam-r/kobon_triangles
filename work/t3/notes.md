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

## Referee3 verdict (23:20 UTC): CORRECT, with two steps to spell out
(a) sigma = 0, B = 6, x >= 3: mutual pairs are impossible when sigma = 0, because V_s lies on
    another line through P, so V_s = Q would put P and Q on one line. Hence every point gets
    its Lemma A credit (credA >= 3) and va >= 3 - x, so 6 - x >= need = 4 - x.
(b) sigma = 3, beta = 3, B = 6 cannot occur. PQR is a face, so no point is bent. Every point
    then has its third line as axis, with caps a_Q and a_R. P's cap a_Q meets PR beyond P,
    while R's cap a_Q meets PR beyond R, which is a contradiction (also for pseudolines).
Empirical: 100,214 n=18 pseudoline arrangements with exactly 3 triple points, zero failures;
max T 93, min Lambda 9. Case (b) was checked by hand only (no samples with sigma = 3,
beta >= 2). Details in work/referee3/.

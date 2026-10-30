# Star case analysis (lead, continuing after the deadline; not in the public repo)

Notation as in SOL_TASK8.md Addendum 5. Inputs are the checked results: STAGE2_TASK7 §§2–4, STAGE2_TASK8 §§3,4,6–9,
Addenda 1–6.

## H budget: the remaining end patterns
H has weight 13 at V− T− X− P X+ T+ V+, and Σ(m−1) = 17. Each end contributes:
- 0 if V is 111100 (H ends at V);
- 1 if V is full and S is simple (H ends at S, an I-end);
- 2 if V is full and S is a triple of type 111100 (H ends at S);
- 2 + (contribution of the next vertex) if S is full.

S is never a quad, and never five-run (same argument as for V; to be checked). The two contributions sum to 4:
- (2,2): both V full, both S triple 111100;
- (1,3) / (3,1): both V full; one S simple; the other S full, followed by a simple S2;
- (0,4) / (4,0): one V four-run; the other V full, S full, S2 triple 111100.

## Lemma M (proved): if both V± are full, U+′ and U− are not both triple, and U+ and U−′ are not both triple
- **+ side.** V+ full makes Z+ full: ZW1 and ZU+′ are double. Its face (−α+, −e2) is Z+ M U+′, with M the first
  vertex on α+ beyond Z+.
  - If U+′ is a triple (D+, α−, e2), its ring is U+′B− (α−), U+′F+ (D+), U+′Z+ (e2), −α−, −D+, −e2. The face across
    U+′Z+ from F+ lies in (U+′Z+, −α−), so M ∈ α−.
  - Hence α+∩α− lies on α+ beyond Z+.
- **− side.** V− full makes Z− full. Its face (−α−, −e4) is Z− M′ U−, with M′ the first vertex on α− beyond Z−.
  - If U− is a triple (D−, α+, e4), its ring is U−B+ (α+), U−C− (D−), U−Z− (e4). The face across U−Z− lies in
    (U−Z−, −α+), so M′ ∈ α+ beyond U−.
  - Hence α+∩α− lies on α+ beyond U−.
- **Contradiction.** α+ has order U− B+ A+ T+ Z+, so the two conclusions put α+∩α− at opposite ends.
- The pair (U+, U−′) is symmetric, using Y± and φ+∩γ−.
- With STAGE2_TASK8 §7 (each diagonal has a triple return): **when both V are full, the triple returns are exactly
  {U+, U−} or exactly {U+′, U−′}**. The other return on each diagonal is a double-B quad.

## Lemma Q (proved): a quad return forces the opposite return to be a triple
Claim: U+′ quad ⇒ U−′ triple.
- The faces F+U+′B− and F+Z+U+′ come from F+ being full. They make U+′B−, U+′F+, U+′Z+ three consecutive bridges, so
  U+′ is a double-B star with U+′F+ in the middle.
- Its case-B kite next to B− has corners U+′, B−, R and a fourth corner. Apply the cyclic-order lemma at the triple
  B−: the exterior face across cap B−U+′ is F+U+′B−, so F+ lies on line B−R. Hence R ∈ φ+, on the side of B− away
  from F+.
- On φ+ the order is U−′ B− F+ T+ Y+, so R = U−′. A case-B far corner is a triple, so U−′ is a triple.

Likewise U−′ quad ⇒ U+′ triple, U+ quad ⇒ U− triple (via α+), and U− quad ⇒ U+ triple (via γ−).

## Corollary: both V± full is impossible
Use Lemma M, Lemma Q and STAGE2_TASK8 §7 (each diagonal has a triple return).
- If U+′ is a triple: M ⇒ U− quad ⇒ (Q) U+ triple ⇒ (M) U−′ quad. Now U− and U−′ are both quads, contradicting §7.
- If U+′ is a quad: Q ⇒ U−′ triple ⇒ (M) U+ quad ⇒ (Q) U− triple. Now U+ and U+′ are both quads, contradicting §7.

**Hence the end patterns (2,2), (1,3), (3,1) are excluded.** Also, S is never five-run (§6 argument with N1/N2 in
place of W/Z). So only (4,0) and its mirror remain.

## Branch (4,0): V− four-run, V+ full, S full triple, S2 four-run triple (H ends at V− and S2)
- **W1+ and W2+ are triples.** Suppose W1+ were a quad. Its bridges W1Z+, W1V+, W1S make it double-B. Its case-B
  kite at Z+ has far corner U+′ (lemma at Z+, exterior face VZW1) and centre M1, the first vertex on α+ beyond Z+.
  Then U+′ is a triple, and Lemma M's + half puts M1 on α−, but M1 is a simple kite centre. Contradiction. W2+ is
  symmetric.
- **The free lines.** S = H ∩ k1 ∩ k2, with k1 ∋ W1+ = c∩e1 and k2 ∋ W2+ = a∩e2. S is full and S2 is a four-run
  triple. Then:
  - N1 = c∩k2∩k3 and N2 = a∩k1∩k4, with S2 = H∩k3∩k4;
  - Q1 = c∩k4 and Q2 = a∩k3;
  - k3 ≠ k4, since the rays of a triple at S2 cannot be opposite and consecutive.
- **a and c are complete.**
  - a: W2− Y− A− P A+ Y+ W2+ N2 Q2, with weights 1+2+2+3+2+2+2+2+1 = 17.
  - c: W1− Z− C− P F+ Z+ W1+ N1 Q1, also 17.
  - So W1−, W2−, Q1, Q2 are simple, and a, c end there.
- **All four ends of a and c are end blocks.** O* with Δ = 0: in triangle V−Z−W1−, the edge V−W1− is single, so
  Z−W1− is double. The block Z−→W1− is an end block, with second triangle Z−W1−(α−∩e3). Likewise:
  - Y−→W2−, with second triangle Y−W2−(γ−∩e4);
  - N2→Q2, with second triangle N2Q2(k1∩k3);
  - N1→Q1, with second triangle N1Q1(k2∩k4).
- **The ends of H are multiple** (V− and S2).
- **Bad-wedge count.** a, c and H are isolated in G_W. The other 15 lines carry all 12 bad wedges in exactly 3 paths,
  and they have 6 non-bad ends.
- **Next:** find the contradiction, by hand or with a fully named SAT cube for this branch.

# THEOREM: the isolated double-case-B star is impossible in the zero-credit corner, so Stage 2 is closed
This supersedes the branch analysis above, which is no longer needed. Setting: zero corner, star P with case-B axis H,
and ends ± as in SOL_TASK8.md Addendum 5. This is a hand proof, not yet independently refereed.

**Inputs (all checked):**
- case-B corners A, F, T are full triples, and Y, Z are multiple (STAGE2_TASK6 §4, STAGE2_TASK7 Pin 1);
- the triple-cap continuation lemma (STAGE2_TASK7 §2);
- (S1): B+ = α+∩γ−, B− = φ+∩α−, and the returns lie on the stated lines (Addendum 5);
- V± are triples (STAGE2_TASK8 §3) and Y±, Z± are triples (Addendum 4, STAGE2_TASK8 §4);
- STAGE2_TASK8 §7: each diagonal has a triple return;
- the zero-quad mask classification: only the double-B mask has a run of 3 bridges;
- saturation c7, the O* lemma, U = 0.

**Lemma Z.** At each end, Z and Y are full. Proof for Z+ = c∩α+∩e2, with ring ZF (c), ZT (α+), ZV (e2), −c, −α+, −e2.
- Faces TFZ, TZV, VZW1 (V has the double ray VZ) and FZU′ (F is full) are present.
- ZU′ is double because FZU′ is all-multiple.
- ZW1 is double:
  - If W1 is multiple, VZW1 is all-multiple.
  - If W1 is simple and VW1, ZW1 are both single, O* gives Δ > 0.
  - If W1 is simple, ZW1 single and VW1 double, then the second face on VW1 is VSW1, with S the next vertex on H.
    At the simple W1 the edge SW1 lies on c, so S = c∩H = P, on the wrong ray.
- The two double rays force the remaining two sectors to be triangles, so Z is full. Y is symmetric.

**Lemma M (unconditional).** U+′ and U− are not both triples, and U+ and U−′ are not both triples.
- Z+ is full, so the sector (−α+, −e2) is the face Z+ M U+′, with M the first vertex on α+ beyond Z+.
- If U+′ is a triple, its ring is U+′B− (α−), U+′F+ (D+), U+′Z+ (e2), and the face across U+′Z+ from F+ lies in
  (U+′Z+, −α−). So M = α+∩α−, located beyond Z+.
- At the other end, Z− is full and the face Z− M′ U− exists. If U− is a triple (ring U−B+ (α+), U−C− (D−),
  U−Z− (e4)), then M′ = α+∩α−, located on α+ beyond U−.
- α+ has order U− B+ A+ T+ Z+, so these are disjoint rays. Contradiction.
- The second statement is symmetric, using Y±, φ+∩γ− and the order of φ+ (U−′ B− F+ T+ Y+).

**Lemma Q.** A quad return forces the opposite return to be a triple:
- U+′ quad ⇒ U−′ triple;
- U−′ quad ⇒ U+′ triple;
- U+ quad ⇒ U− triple;
- U− quad ⇒ U+ triple.

(Proof above: the far corner of the quad return's case-B kite next to B± is the opposite return.)

**Conclusion.**
- If U+′ is a triple: (M) U− quad ⇒ (Q) U+ triple ⇒ (M) U−′ quad. Then D− has two quad returns, contradicting §7.
- If U+′ is a quad: (Q) U−′ triple ⇒ (M) U+ quad. Then D+ has two quad returns, contradicting §7.

So no isolated double-B star exists. With STAGE2_TASK6 (long paths and alternating endpoints excluded) and STAGE2_TASK7
§3 (B–B path excluded), **the zero-credit corner contains no 94. Stage 2 is complete**, so K(18) = 93 follows from
(B) alone. ∎

## Independent referee (fresh-context agent, 2026-10-03): verdict CORRECT given the inputs
The referee checked every ring and face sector by hand and against an explicit 14-line straight-line model.

Notes, all accepted:
1. **Mask input.** Cite the opposite (distance-4) double-B mask: STAGE2_TASK5 §1 (distance 3 excluded) and §2
   (zero-slack quads are all-8). With a distance-3 mask, Lemma Q could fail.
2. **Unlisted inputs to add.** B± are triples (quad-neighbour exclusion, STAGE2_TASK5 §3). Case-B kite corners
   other than the quad are triples (STAGE2_TASK7 §1).
3. **Wording.** "The face across U+′Z+ from F+" should read "from the face F+Z+U+′".
4. **Lemma Z is not needed.** Lemma M only needs the sector (−α+, −e2) at Z+ to be a triangle. That already follows
   from ZU′ being double (FZU′ is all-multiple). So the theorem does not depend on the O* or wrong-ray steps.
5. **Coincidences.** None are possible: they would need 5–6 lines through one point. Returns are at least triples.
   STAGE2_TASK8 §10's triple-guard caveat does not apply, because G/G′ and "B± full" are not used.
6. **Not checked by the referee:** the upstream inputs (STAGE2_TASK5–7, O*, saturation, STAGE2_TASK8 §§3–5) and
   the final global sentence (Stage 2 complete).

# Stage 1 (after the star exclusion): what remains
- **Target.** (B) ⟺ W ≤ 2Λ. For a 94 this says W ≤ 12. Since W ≥ 12 always holds, it means π = 6 and E = 0, which
  is the zero corner, now excluded. So **K(18)=93 ⟺ no 94 with W ≥ 13 (π ≤ 5).**
- **Diagnostic.** W ≤ 2Λ fails at other n for triple-only records: 7 of 56 records at n=14 (T=54, W=13, Λ=6) and 79
  of 305 at n=20 (T=117, W=19, Λ=9). On the n=14 failures, O2Q holds (c ≥ 1) and the reconciliation fails by
  exactly 1. **So any proof must use the all-8 point**, which a 94 must have at n=18.
- **Bad-wedge geometry.** In the wiring (slope) order, a bad wedge joins slope-adjacent lines at their common first
  vertex or common last vertex. Paths are runs of slope-consecutive lines whose wedges alternate between the left and
  right ends. So W ≥ 13 means at most 5 runs among the 18 cyclic adjacent pairs.
- **SAT probe s1a.** Base class model, T=94, all-8 quad cube, W ≥ 13. Running. Several cubes are UNSAT in seconds.

# Task 8 for sol: the double-B star is the last Stage-2 case

The lead checked STAGE2_TASK7.md §§2–4 and the pins, and ALL8_NOTE7.md §§2–4. All are accepted and recorded in the
repository:
- **The B–B path is excluded.** The four-corner cap-line argument is correct.
- **V is multiple.** The proof is correct, including the use of the alternating exclusion.
- **LC is proved** for all-110110 components and for components of size 2.

## Stage-2 SAT status (lead)
Round r4 runs on all cores, on the open star cubes only.
- **Pins:** full corners, two lines beyond T, V multiple, and all four off-H neighbours of T multiple (your Pin 1).
- **Results:** 220 of 416 star cubes are UNSAT and **none is SAT**. The hard ones resist 600 s.

## Track 2 (priority): exclude the isolated double-B star by hand
Use your §4–§5 and Pin 6 dichotomy at each far corner's first H-vertex V:
- **V quad.** V has the double-B zero mask with VT the middle of a three-bridge run. So V is another star centre
  on H.
  - Then H carries P, X, T, V, X′, T″, … on that side.
  - Count vertices and lines along H. H has exactly 17 crossings at n = 18, and each star uses its own pencil lines.
  - Does a chain of stars along H run out of lines, or close up against the opposite side?
- **V triple.** Its mask is 111100, 111110 or full.
  - In the four-run branch, V is the last vertex of H on that side.
  - In the five-run and full branches, find the contradiction or the next forced vertex.

Combine both ends of the star (T and T′) with the ≥ 14-line inventory and the 6 bad-wedge paths (π = 6, W = 12).

If a full exclusion is out of reach, give further proved local pins. Ideal pins are about V's other lines, the
vertex after V, or the multiplicity of U, U′. Give each as a short implication in ENCODING.md terms.

## Track 1 (subagent): Stage 1
Continue on either route:
- LC for the remaining mixed-sector / quad components (149 / 1 / 27 in the cohorts) plus the end reconciliation;
- or a Hall theorem for the wedge_line_pool transport graph, which has 0 failures on all data.

## Output (about 40 minutes; partial results fine, gaps marked)
- `work/bbl/STAGE2_TASK8.md` (Track 2);
- `work/bbl/ALL8_NOTE8.md` (Track 1).

## Addendum (lead, 23:30): a line count on H for the star (proved)
Order H as V− T− X− P X+ T+ V+, with the kite centres X± simple, the far corners T± triple and V± multiple.
- Lines crossing H at these vertices: 3 at P, 1 at each X±, 2 at each T±, and at least 2 at each V±.
- **If both V± are 111100 triples,** Pin 6 makes each V± the last vertex of H. Then H meets exactly
  3 + 2 + 4 + 4 = 13 lines, so n = 14. **At n = 18 this is impossible.**
- So at least one end has one of:
  - (ii) V a triple of type 111110 or full, so H continues beyond V;
  - (iii) V a quad. Then V is an all-8 double-B star whose case-B axis g ≠ H, with run (VZ, VT, VY).
- **In case (iii), Y and Z are kite corners of V's two case-B kites (on g±).** Each such kite's diagonal passes
  through Y (resp. Z) on a line other than e1 = VY. So the second star's diagonals are among Y's old lines a, φ+
  (resp. Z's c, α+), or extra lines.
- A careful count of shared lines in (ii)/(iii) against n = 18 may close the star.

## Addendum 2 (lead, derived by the §2 cyclic-order lemma; please re-check): the star skeleton
Notation for the star P. Rays: 0 = H+, 1 = a+, 2 = b+, 3 = c+, 4 = H−, 5 = a−, 6 = b−, 7 = c−.
- Kite+ has centre X+ on H+, corners A+ ∈ a (ray 1), F+ ∈ c (ray 7), far corner T+, and diagonal D+ = A+X+F+.
- Kite− has centre X−, corners C− ∈ c (ray 3), A− ∈ a (ray 5), far corner T−, and diagonal D−.
- Caps: α+ = A+T+, φ+ = F+T+, γ− = C−T−, α− = A−T−. The lone bridge neighbours are B± on b.

**(S1)** B+ = α+ ∩ γ− and B− = φ+ ∩ α−. Apply the lemma at A+ and C− to triangles PA+B+ and PB+C−, and at A−
and F+ for B−. So B± are triples on b and on one cap line from each kite.

**(S2)** Consecutive vertices along the ten baseline lines, with apices Y+ = a∩φ+, Z+ = c∩α+, Y− = a∩γ−,
Z− = c∩α− and returns U+ = D+∩γ−, U+′ = D+∩α−, U− = D−∩α+, U−′ = D−∩φ+:

    H : V− T− X− P X+ T+ V+          a : Y− A− P A+ Y+          c : Z− C− P F+ Z+
    D+: U+ A+ X+ F+ U+′              D−: U− C− X− A− U−′        b : B− P B+
    α+: U− B+ A+ T+ Z+               φ+: U−′ B− F+ T+ Y+
    γ−: U+ B+ C− T− Y−               α−: U+′ B− A− T− Z−

- U+ is derived as follows. Since A+ is full, there are triangles A+Y+U+ and A+U+B+. The second lies across A+B+
  from P. At B+ it sits in the sector (−γ−, B+A+), so U+ ∈ γ−.
- B+ then has 4 consecutive triangles: PA+B+, PB+C−, C−B+U−, A+B+U+.

**(S3) Case V+ quad: the star propagates as a lattice.**
- By Pin 6, V+ is a double-B star with bridge run (V+Z+, V+T+, V+Y+), Y+ and Z+ triple, and case-B axis g ≠ H.
- Apply the lemma at Y+, a corner of V+'s kite on g+. The exterior triangle on cap Y+V+ is T+V+Y+, so T+ lies on
  Y+'s other cap line, which must be φ+. Hence:
  - **V+'s kite on g+ has far corner T″ = g ∩ φ+, centre X′+ = a ∩ g, and diagonal a.**
  - Symmetrically, **the kite on g− has far corner g ∩ α+, centre c ∩ g, and diagonal c.**
- So V+'s star reuses a and c as diagonals and φ+, α+ as caps. T+ is V+'s lone bridge neighbour, and T+ = φ+ ∩ α+
  matches (S1) for V+.
- Consequences:
  - a continues Y+, X′+ = a∩g, Z* (with Z* = a∩e2);
  - c continues Z+, c∩g, then the e1∩c corner;
  - the only genuinely new line is g.

  **This is the lattice pattern (cf. `work/eng/lattice/lattice18.jsonl`).** A naive line count therefore cannot
  exclude the star. The contradiction must come from the boundary of the finite lattice patch.

**Suggested closing route:** classify the propagation at both ends of every star:
- V triple 111100 means H ends at V;
- V triple 111110 or full means H continues;
- V quad means a new star.

Each star adds only one new line, so a patch of k stars uses about 13 + k lines. Then show that the patch boundary
forces U > 0, Δ > 0, S° > 0, or more than W = 12 bad wedges, using the six bad-wedge paths and n = 18. The H line
count (Addendum 1) is the first instance: two four-run ends give n = 14.

## Addendum 3 (lead, after STAGE2_TASK8 §3)
**Checked and accepted:** your §3 (V quad ⇒ U lies on the four axes D0, b, e, ℓ ⇒ U quad with ℓ a block axis, but
UR is a double bridge). This makes Addendum 2 (S3) moot. The SAT pin `zp[H,v] ∧ ¬zp2[H,v]` is now encoded
(`--vtriple`).

With Addendum 1: **both V± are triples, and at least one is 111110 or full.** For a triple V with lines
H, e1 = VY, e2 = VZ:
- The double rays VZ, VT, VY force four consecutive triangles at V:
  - (−e1, VZ) = VZW1, with W1 the first vertex on −e1;
  - TZV and TVY;
  - (VY, −e2) = VYW2, with W2 the first vertex on −e2.
- If Y is a triple, then at Y the triangle VYW2 lies in the sector (YV, −a). So **W2 = a ∩ e2**, the vertex just
  beyond Y on a. Likewise, if Z is a triple, **W1 = c ∩ e1**.
- If Y is a triple, Pin 5 orders e1 as U, Y, V, W1 (consecutive), with U = D0 ∩ γ− ∩ e1.
- In the 111110 or full branch, H continues past V. The extra triangle (−e2, −H) or (−H, −e1) joins W2 or W1 to
  the next H-vertex V2.

**Next target:** follow the 111110/full end outward along H until it ends, counting the multiplicity budget
Σ(m−1) = 17 on H, a, c, e1 and e2. Also follow whether Y and Z can be quads.

## Addendum 4 (lead, proved): Y and Z are triples
Setting: zero corner, star boundary (P, A, T, F), with V now known to be a triple.
- Suppose Y were a quad. Its rays YA, YT, YV are double and consecutive: they are edges of the all-multiple faces
  TAY and TVY. So they are three consecutive bridges, which forces the double-B mask with YT in the middle.
- The face across YA from T is AYU, because A is full and the sector (AY, AU) is a triangle. So U would be the
  simple centre of Y's case-B kite on Y's fourth line h.
- But U ∈ D0 ∩ γ−. This uses B's cyclic order: the face AUB lies at B in the sector (−γ−, BA). Since U is simple,
  h ∈ {D0, γ−}. Neither passes through Y: D0 ∩ a = A and γ− ∩ a = Y−. Contradiction.
- The same argument works for Z. So **A, F, Y, Z and V are all triples**, Pin 5 applies at both ends, and
  U ∈ YV and U′ ∈ ZV. SAT pin `--ttriple` is added.

Also accepted: Note 8 §3 (LC with one four-run triple plus 110110 triples). Checked.

# Kobon K(18): the last open case (brief for an outside solver)

Repo: /home/nail/stuff/sundai_math. The master log is work/bbl/THEORY.md, with the latest material in §24–§26 and the
notes after them.

## The problem
- Arrangements: arrangements of n = 18 pseudolines in the Euclidean plane, every pair crossing exactly once.
  Concurrency is allowed. Parallels reduce to concurrency projectively.
- T = number of bounded triangular faces.
- Known: T = 93 is attained.
- Goal: prove T ≤ 93, i.e. that no arrangement has T = 94.

## Notation (all standard in THEORY.md)
- Λ = n(n−2) − 3T = 288 − 3T. A 94 means Λ = 6. Λ is always a multiple of 3.
- Exact identity: Λ = Z + Σ_P c_P, summed over the multiple points P (multiplicity m_P ≥ 3).
  - Z = number of unused bounded segments, i.e. bounded edges bordering no triangle.
  - c_P = m(m−2) − D_P − β_P/2.
- Ray classes at P (each first segment from P along one of its 2m rays):
  - B (block): doubly used, both adjacent sectors are triangles, simple far end;
  - R (bridge): doubly used, multiple far end;
  - N: otherwise.
  - D_P = #B and β_P = #R.
- Resulting costs:
  - triple point: c = (N − D)/2, which can be negative (full triple points with blocks);
  - 4-fold point: c = N + β/2 ≥ 0.
- Lemma A: if P → X is a block with cap line C at the simple vertex X, then beyond X along the block's line either a
  face is a triangle (a mutual pair: a neighbour of X on C is multiple with a block toward X), or the segment beyond X
  is unused (a "touch").
- L1: a doubly used segment has a multiple endpoint.

## What is proved (computer-assisted, with exact certificates; methods in THEORY.md)
1. T ≤ 94 for every 18-line arrangement. This uses a per-line linear-programming certificate: a DP over a line
   automaton plus transfer rules.
2. T ≤ 93 whenever every multiple point has multiplicity ≤ 3. This uses joint tightness, a flower reduction by
   Gauss–Bonnet, an ILP, and a 9-line SAT lemma.
3. Reduction (§24, perturbation lemma). Take a counterexample maximal in (T, #vertices).
   - It has only triple points and "bad" 4-fold points. With the 8 sectors read cyclically, 1 = triangle with apex P,
     the bad words are 11111111 ("all-8"), 11111110 ("7-type") and 11101110 ("6-type").
   - Every m ≥ 5 point and every other 4-fold point has a local re-drawing that keeps T and adds vertices.
4. Pair lemma (§25). For a 4-fold point consecutive with a triple point on a line, only 48 of 2,080 sector-pattern
   pairs are possible in such a maximal counterexample; the rest are locally reducible.
5. A 6-type point cannot occur in a 94. A 7-type point cannot occur in a 94 that has no all-8 point.

## THE OPEN CASE
**Show that no 18-line arrangement with T = 94 exists that contains an all-8 point** (a 4-fold point with all 8
sectors triangles), assuming only triple points and bad 4-fold points, no 6-type, and the pair lemma.

### Facts about all-8 points
- Each of the 8 cap lines covers ≤ 3 consecutive sectors, so the first-vertex octagon X_0..X_7 has ≥ 3 multiple
  vertices: β ≥ 3 and c_P = β/2 ≥ 3/2. In "identity units" (3Λ − 18 = Σ_lines final + waste) that is ≥ 4.5.
- Real examples are triangular-lattice patches with extra "height" lines through lattice points:
  - lattice points on a height line are all-8;
  - the other lattice points are full triple points;
  - edge midpoints are kite centres (simple vertices with 4 triangles).
  - Every face inside the patch is a triangle, so every local move loses triangles.
- In every real in-class arrangement with an all-8 point that we have (131 of them), Λ ≥ 66 (T ≤ 74):
  - Z = 32–48;
  - Σ c over the all-8 points = 5.5–17;
  - negative triple costs only −1 to −3.5.
  These data are in work/eng/lattice/*.jsonl, as wiring words; work/t3/arr.py parses them.
- Planar identity, per bridge component K (V points, E bridges):
  Σ_{P∈K} c_P = (V − E/3) + Σ_triple (N − 2D)/3 + Σ_4fold (13 + N − 2D)/3, with V − E/3 ≥ 2 for V ≥ 3.
- Triangle-surface identity: T = D + χ − F, where D = doubly used segments, F = vertices whose sectors are all
  triangles, and χ = Euler characteristic of the union of the triangles.

### Why the existing method stalls
- Per-line accounting: in lattice-plus-height patches, every interior line can be balanced to about 0. The slack
  that makes Λ large sits at the patch boundary, on other lines.
- The per-line LP's best "margin" for this case is −2.29 (it needs > 0), even though real lines alone support
  margin ≥ 12. The obstruction is the model's pessimism, not real lines.
- An engineering fix (hidden-state automaton + SAT-validated patterns) is running but converges slowly.

## What would close it (any one suffices)
(a) **A 2-D / discharging argument.** Show Z + Σ_P c_P ≥ 7 for every arrangement in the class that contains an all-8
    point. Natural tools:
    - redistribute the negative costs of full triple points (blocks toward kite centres) to the all-8 points and to
      Z (touches);
    - Gauss–Bonnet on the triangle surface: all-8 = curvature −2, kite centre = +2;
    - the boundary of a lattice patch must turn by 6χ.
(b) **A structural lemma** forcing, from an all-8 point in a 94, a configuration known to be impossible (e.g. via the
    flower-type analysis of §21–§22, or a small SAT instance like the 9-line tip lemma).
(c) **A non-local re-drawing argument**: some move that keeps T and increases #vertices, contradicting maximality.
(d) A counterexample, i.e. a 94 containing an all-8 point. That would settle the question the other way, but the data
    make it very unlikely.

## Tools available
- work/t3/arr.py: wiring words to faces, triangles, rays.
- work/eng/comp/comp_cost.py and bad_comp.py: costs, components, sector patterns.
- work/eng/lattice/lines2gens.py: exact straight lines to wiring words; build_lattice.py builds lattice-plus-height
  arrangements.
- work/eng/T27/classsat.py: SAT for 18-line class arrangements with pinned local patterns (K = 18, bad words, pair
  lemma).

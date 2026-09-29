
# Task T20: n-independent verification of per-line lemmas with a line automaton (new files: search/line_automaton.py, work/eng/T20/*; ≤ 3 cores)

**Why.** Every SAT query on full arrangements grows about 10× per two lines: the Hall query, L3, the tightness query.
n = 18 is out of reach that way.

But each per-line argument is a chain along one line. BBL's proof (work/bbl/THEORY.md section 12, lemmas P1/P2) uses
only:
- local facts at consecutive vertices. At a simple vertex, consecutive triangles on the same side force a block capped
  by L there;
- end facts. At an end vertex, the end line's segment on the other side is unused or unbounded;
- one compatibility condition between the two ends: the end lines M and N cannot have unbounded rays on opposite sides
  of L.

**Method.**
- Model a line L as a sequence of vertices V_1 … V_m with the segments between them.
- A *vertex type* is the local configuration at a vertex as seen from L:
  - simple vertex (L ∩ W): which of the 4 faces are triangles; W's two segments at V (unused / used / doubly used /
    unbounded); whether L caps a block there;
  - triple vertex (L, a, b): the 6 sectors, the 6 ray statuses (N/B/R), block statuses (U/M/I), served flags, flank
    types, and everything search/bbl_hall.py `values()` attributes to L at that vertex (see THEORY section 12 for the
    per-ray split).
- Consecutive types must agree on the segment between them.
- Enumerate the types *exhaustively*, as an over-approximation. Realizability is not needed for soundness, but every
  local fact you impose must be a proven implication (write each proof in your report).
- A shortest-path DP over the automaton, tracking the state needed for the end conditions and the parity of the length,
  gives the minimum of a per-line quantity over all "locally consistent" lines of every length.
- Detect negative cycles. Zero-weight cycles are expected (lattice interiors).

**Milestones.**
- **M1.** L3 for all even n: a clean line (no multiple point, caps no block) receives ≥ 1 portion. The DP should show
  that the minimum portion count is ≥ 1 for all odd lengths m = n − 1, and that it can be 0 for odd n.
- **M2.** Certified lower bounds for v_L (after T1 and F), for all n. Examples:
  - the minimum of v_L + ½·#(unserved RN blocks on L) + 3/2·#(unserved RR blocks on L) (should be ≥ −1);
  - lower bounds for lines of given local features, such as the axis of an X point whose other block is U.
  - Any transfer whose trigger lies on another line must be taken worst-case (nondeterministically).
- **M3** (if time allows; needs task T18's rules in search/bbl_rules2.py when it appears). Verify that every line ends
  ≥ 0 after those rules, for all even n.

**Soundness validation (mandatory).**
- Every line of every even-n arrangement in work/phi/*.jsonl, work/bbl/lineadv/pilot.jsonl and gallery n = 10–18 must
  be a path in your automaton.
- The quantities computed along it must equal the Python reference (search/bbl_hall.py values(), portions).
- Report coverage: how many distinct vertex types occur in data versus how many are enumerated.

Output: search/line_automaton.py and work/eng/T20/REPORT.md, with the list of local facts and their proofs, and the
DP results per milestone.

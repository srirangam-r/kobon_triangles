
# Task T21: design transfer rules with the line automaton in the loop (new files: search/rule_lp.py, work/eng/T21/*; ≤ 4 cores)

Read work/eng/T20/REPORT.md in full, and search/line_automaton.py.

**What T20 proved (all n, multiplicity ≤ 3).**
- A clean line gets ≥ 1 portion for even n.
- For every line, v_L + ½·#(unserved RN blocks) + 3/2·#(unserved RR blocks) ≥ −1.
- Raw v_L is unbounded below along the "kite" line: triple and simple vertices alternate, with four triangles at each
  simple vertex. Its deficit sits in unserved blocks whose gap-end rays are blocks.

**Goal.** Find transfer rules between lines such that every line ends with final_L ≥ 0 for every even n, certified by
the automaton.
- final_L = v_L + (received) − (paid).
- This proves Λ ≥ n/3: T ≤ 54 at n = 14 and T ≤ 72 at n = 16 for arrangements with triple points and no 4-fold point.
  These are new results.

**Method: LP with automaton separation.**
- **Rule language.** A rule is (trigger κ, payer role, receiver role, weight w ≥ 0).
  - κ is a local configuration at a triple point P, or at a simple vertex X: sector bits, ray statuses, flank types,
    served flags, whatever the frames expose.
  - Roles are lines through P (axis, flank lines, …) or the cap of a block at P, identified relative to κ.
- **Soundness of the coupling.**
  - The payer's automaton must count the payment whenever κ *may* hold in its window: worst case, triggered.
  - The receiver's automaton counts it only when κ *surely* holds: worst case, not triggered.
  - So prefer triggers that are fully visible to both lines, such as the sector configuration at P (visible to all
    three lines of P). Write out, for each rule, why both automata see it.
- **LP.**
  - Variables: the rule weights.
  - Constraints: for every automaton path of odd length m = n − 1 (even n), final ≥ 0.
  - Separation: T20's DP. Find the most negative path for the current weights and add its constraint.
  - Iterate until the DP minimum is ≥ 0 (certificate) or the LP is infeasible (report the obstruction paths).
- **Start small.** Candidate rule families:
  - the existing T1 and F;
  - payments to unserved RN/RR blocks from their flank lines or their cap;
  - payments at 4-triangle simple vertices from the four "side" lines of the complete quadrilateral;
  - pure-cap support: every unserved I-block pays its cap, from the axis or the connector.
- **Data check.** The rules must also keep every line of real arrangements ≥ 0. Compute finals on work/phi/*.jsonl
  as a cross-check; implied if the automaton is sound, but cheap to confirm.

**Stretch (only if the LP succeeds).** The n = 18 strict step (work/bbl/THEORY.md section 13):
- mark tight frames (on a final-0 path of length 17 − #triple points);
- check whether some triple-point configuration can be tight on all three of its lines.

Output: search/rule_lp.py and work/eng/T21/REPORT.md. The report gives the rule list with weights, the certificate
(DP minima), or the obstruction if infeasible.

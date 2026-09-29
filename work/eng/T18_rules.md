
# Task T18: explicit local transfer rules that replace the Hall step (new files: search/bbl_rules2.py, work/eng/T18/*; ≤ 4 cores)

**Goal.** Find explicit transfer rules, applied after T1 and F (search/bbl_hall.py, ε = 0), such that every line ends
≥ 0. Every rule must be triggered by *local* structure only:
- point ray patterns, block statuses U/M/I, served flags, flank types;
- "a pure cap has p = 0", which is allowed: pure caps have no multiple point, and search/parity_lemmas.py handles their
  parity.

Do not use conditions on other lines' final values ("take from the line with the largest value" is not allowed). A
donor's total must be checkable by a single-line SAT query: "line 0's value minus the requests it receives < 0".

**Leads.**
- A rule for deficient pure caps is almost done. The cap C (value −1, capping k blocks, all unserved I-blocks) takes 1/k
  per block b = [P, X]:
  - from the axis, when P is an X point whose other block is U;
  - from the connector, when the other block is M. The connector is the line of the flank ray pointing to the
    mutual partner;
  - still undecided for other point types (BNNNNN, BNNRNN and rarer).
- Negative axes (values −1/2 … −2) are mostly:
  - bridge runs with unserved blocks at both ends, each with one R flank and one Ns flank;
  - (2,2) points NBRRBN with two mutual blocks.
- The spare usually sits on the I-block's non-pure cap, or on lines through the mutual block's point.
- Data tools: /home/nail/.claude/jobs/f347ce4a/tmp/rules3.py, structdonor.py, negaxis.py (read-only; copy what you
  need).

**Validation.**
- 0 negative lines on all even-n records of work/phi/*.jsonl, work/dpwalkc/run1/cls_w*.jsonl (1.15M) and
  work/bbl/adv/bad.jsonl.
- Run annealing adversaries against your rules on 4 cores:
  - start from `search/bbl_lineadv.py` (read it; write your own copy with your rules; even n only);
  - seeds: gallery n = 10–18, work/phi/bridge93.jsonl, work/bbl/lineadv/pilot.jsonl.
- Iterate until the adversary finds nothing in ≥ 1 hour of 4-core walks.

**Deliver.**
- search/bbl_rules2.py: a reference implementation with a precise docstring. It is the spec for a later SAT check.
- work/eng/T18/REPORT.md: the rule list with a short justification of each rule, the validation numbers and the
  adversary effort.

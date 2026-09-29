# Task T4: fast combinatorial local search generator

Write a fast local search over pseudoline arrangements (wiring diagrams or signotopes) that generates many DISTINCT
near-optimal arrangements. Targets:
- n=17 with T >= 82;
- n=18 with T >= 91;
- including "bridge-rich" ones: at least 2 doubly used segments between two triple points (see geometry() in
  search/test_k5L_layer.py for a checker).

**Method:**
- Moves: triangle flips (mutations of a simple triangle) and local rerouting of one wire. Allow creating and
  removing triple points.
- Exact triangle counting, incremental if possible. Aim for ≥ 1,000 evaluations per second.

**Output:** samples with their chi or wiring words to work/pls/*.jsonl, plus stats of T, k and bridges.

**Deliverables:** search/pls.py and work/eng/T4/REPORT.md. The parent will feed the samples to one-line and
two-line extension to 18 lines.

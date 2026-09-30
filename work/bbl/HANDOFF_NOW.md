# Handoff (2026-09-30, before compaction)

**Route.** Explicit transfer rules plus an n-independent line automaton (THEORY.md §13–15).

**Proven for all n** (automaton, independently audited):
- M1: clean lines get ≥ 1 portion for even n ≥ 4;
- M2: v_L + ½·#RN3 + 3/2·#RR3 ≥ −1 for every line, any multiplicity. RN3/RR3 are unserved blocks at triple points
  with one or two bridge flanks. Blocks at m-fold points need no compensation.

Obstruction: the "kite" line, alternating triple points and 4-triangle simple vertices. It is realizable, so no
local fact removes it.

**Missing.** Transfer rules making every line final ≥ 0 for all even n, gives Λ ≥ n/3, hence K(14)=54, K(16)=72
(new for non-simple arrangements), T ≤ 94 at n=18. Then the n=18 strictness by tight-type exclusion.

**Next action (agreed with the user).** The lead does the rule-design thinking; agents encode and run.
- Read the rule agent's obstruction cuts in work/eng/T21/*.log ("--- cut k:") and work/eng/T21/INTERIM.md if present.
- Design rule families (who pays for kite and other RN/RR deficits), then send them to the rule agent via
  SendMessage.

**Running s55-engineer agents.**
- Rule design: search/rule_lp.py, work/eng/T21.
- Obstruction triage: search/automaton_facts.py, work/eng/T23.

Stopped: n=18 strictness machinery (T24). Relaunch once rules exist.

**Key code.**
- search/line_automaton.py (T20): frames, windows, `exact_vec`, `options`, `Graph(allow, feat, cnt, edge_allow)`,
  `solve(graph, obj, parity)`.
- search/line_automaton_m.py (T22), search/audit_automaton.py (A20).
- Reference values: search/bbl_hall.py.

**Preferences.**
- Use Agent with s55-engineer (not claude -p), several in parallel.
- Kill slow runs early.
- Push only on request.

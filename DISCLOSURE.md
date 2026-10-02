# Authorship, AI use and compute

**Author:** Raj Harshit Srirangam. He directed the work, chose the problems and the strategy, relayed tasks between
systems, and takes responsibility for the claims.

**AI systems used.**

| System | Role |
|---|---|
| Claude Opus 5.5 (Anthropic), in Claude Code | Lead: mathematics, proof design, the per-line certificate method, checking every proof before acceptance, writing the paper and documentation |
| Claude Sonnet 5.5 (Anthropic), as subagents | Software engineering (automaton, LP/DP, SAT encodings, enumerations, checkers) and independent audits; the independent checker in `checker/` |
| GPT 6.1 (OpenAI) | Theory notes on the all-8 case: injective payments, the bad-wedge forest lemma and the credit identity (`proofs/all8/`). Every step was checked before use. |

**How the claims were checked.**
- Computational claims carry exact certificates (rational LP weights checked by exact DP; DRAT proofs for SAT
  exclusions).
- Some results were re-derived independently by separate code.
- The multiplicity ≤ 3 chain passed an independent audit.
- Hand proofs were checked step by step before entering `proofs/`.
- **No human referee and no proof assistant** has checked the work yet.

**Compute.**
- One workstation (24 cores, 62 GB RAM). Re-verifying all six main DP certificates takes about 20 min with under
  10 GB RAM. Building the certificates (LP cutting-plane loops) took up to about an hour each, at up to about 30 GB.
- SAT runs used kissat/CaDiCaL, with drat-trim for proof checking.
- The competition construction was scored on the AutoLab platform; see `evaluation/`. Rented cloud compute
  (about $4) produced no results used here.

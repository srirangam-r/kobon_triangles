# Shrinking the Kobon Gap: Theorems, Solvers and AI Referees on the 18-Line Problem

Proofs plus a SAT solver narrow where a 94-triangle, 18-line Kobon arrangement could exist.

- **Start here:** [`SUMMARY.md`](SUMMARY.md). It covers results, methods, each claim's
  verification status, and next steps.
- **Proofs:**
  - [`work/proof_k2.md`](work/proof_k2.md): at most 2 triple points;
  - [`work/proof_general.md`](work/proof_general.md): Theorem G, even n, general position;
  - [`work/t3/`](work/t3/): 3 triple points, Theorem H, and shared-line work.
- **Decoupled loop ledger:** [`work/loop/ledger.md`](work/loop/ledger.md), with claims in
  `work/loop/claims/` and verdicts in `work/loop/verdicts/`.
- **Code:** [`search/`](search/).
  - `kobon_sat.py`: SAT models (signs per triple, defect budget, Blanc claims, case
    constraints).
  - `prove.py`, `cnc.py`: case splitting, with DRAT-checked proofs.
  - Exact local search tools.
- **Scored arrangements:** `submissions/` and `reports/`, from the AutoLab hill
  `alejandrozu/kobon-triangles`.

**Status caveat.** The proofs were refereed by independent AI agents with extensive exact
testing. They have not had human expert review or formal (Lean) verification. Claims marked
"proposed" in the ledger are unrefereed.

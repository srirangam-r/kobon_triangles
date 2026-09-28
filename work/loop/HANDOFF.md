# Loop handoff brief (for fresh generator / verifier agents)

**Problem.** Can 18 lines have 94 bounded triangular faces (Kobon)? The best known is 93. Identity:
3T = S − Z + D, with S = n(n−2) − Σ k(k−2). A 94 at k triple points needs D − Z ≥ 3k − 6 (C34).

**Authoritative state.** `work/loop/ledger.md`: one row per claim, with status proposed / refereed-correct /
refereed-fixed / refuted and the solver tag. Claims are in `work/loop/claims/Cnn.md` (A* = AutoLab 7+ stream,
S* = engineering). Verdicts are in `work/loop/verdicts/`. Overview: `SUMMARY.md`.

**Closed (refereed).** k ≤ 4 (C1–C4, C25); general position (Theorem H); k = 5 and k = 6 with β = 0 (C14–C33, solver
cubes DRAT-verified); no centroid at k = 5 (C41) or k = 6 (C55–C59). 4-fold points: non-rich ones reduce to triple
points (C51); rich ones never help (C52).

**Open frontier.**
- k = 5, β > 0: 28 rigid graphs (work/t3/k5_exceptions.jsonl, refereed C37–C50). Every graph needs ≥ 1 local exception
  (E2, C50 (ii), C50 (i)).
  - Solver attempt: search/build_k5g.py + work/k5g/cubes.jsonl (35 exception-position cubes); see AUDIT_k5g.md.
- k = 6, β > 0: 1,910 centroid-free graphs (kN_fixed2.py). C61 is proposed. 124 graphs survive all known credits.
  - C35/C38 at k = 6 require k = 5 closed.
- t ≥ 7: A01–A03 refereed-fixed, A04–A05 proposed (high-m residue; lower m open).

**Tools.**
- search/kobon_sat.py (signotope model: before(r,i,j) = ng[sorted] if i < j else pz[sorted]; left-to-right order).
- build_k6z / build_k5 / build_k5b (build(dz)) / build_k5g, wedge_cubes*.py, k5_cubes.py, drat_cubes.py (DRAT),
  lrat_pipeline.py (cake_lpr, not yet built here).
- work/t3/profile_ilp.py and kN_fixed2.py: discharging read-out (which feature kills the most graphs).

**Rules and pitfalls (learned the hard way).**
- New cube variables must start above the base CNF **header nv**: an id collision invalidated one run (AUDIT_k6z).
- Cubes with first(0,1) die on the symmetry break χ(0,1,2) ≠ −1 (the "easy half"). Genuine cubes have line 0 meeting 17 first.
- Only necessary conditions go into the solver. State each clause's justification; the verifier audits encodings before
  any result counts.
- A lemma that uses C35/C38 at k needs k − 1 closed; say so explicitly.
- Generator: never referee your own claims; write concise claim files plus a "proposed" ledger row.
- Verifier: change only ledger status cells; test with exact or mutated arrangements (work/referee4/*); ≤ 4 cores.
- Hand-backs ≤ 150 words. The solver only wins once theory makes a configuration rigid (β = 0 via line ends at
  infinity; k = 5 B = 10 via C32).

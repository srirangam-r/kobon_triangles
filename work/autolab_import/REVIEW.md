# Review of AutoLab deliverables (2026-09-28)

| experiment | deliverable | decision |
|---|---|---|
| b292aca7 (7+ round 2) | A01–A03 revised (apply referee fixes; A03 supersedes), A04, A05, a_gap.py, a_gap_profiles.jsonl | **merged**; A04/A05 proposed, unrefereed |
| c7cee43b (symmetry) | symmetry.py, lexleader.py, test_symmetry.py, S01, opt-in `lex_prefix` in kobon_sat.py | **merged**. The kobon_sat.py change is opt-in (default off); a k6z2 rebuild is byte-identical (md5 940edb01edc4); test_symmetry.py passes (16 fixtures, 1,720 actions). S01 proposed, unrefereed; speed-up not measured |
| 6a72490 (verified checker, from failed 88079604) | lrat_pipeline.py, test_lrat_pipeline.py, tools/build_proof_tools.py (pinned cake_lpr/kissat/drat-trim), validation on small instances (VERIFIED_UNSAT) | **merged** (new files). The tool build refuses to replace our existing tools/kissat and tools/drat-trim directories, so the checker is not yet built here. Build it into a separate cache or tools dir before use |
| b11a4d5c (residue encoding) | none of its own: its build_k5b.py and C35 verdict equal our seed; its ledger is an older snapshot | **rejected** (nothing to merge). The 28-graph residue encoding is still to do |
| 62d8e60c | commit not fetchable | superseded by 6a72490 |

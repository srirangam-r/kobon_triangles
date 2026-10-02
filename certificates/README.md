# Proof certificates for the Kobon problem K(18)

Claim chain (see `work/bbl/STATUS_K18.md`, `work/bbl/THEORY.md` §20-§27): T <= 94 for every arrangement of 18 lines or
pseudolines; a 94 is excluded in every case except arrangements that contain an all-8 point (open). This directory
packages the certificates and the commands that re-verify them from a fresh clone. Nothing here is a Lean or other
formal proof; the exact trusted base is listed under "Known limitations".

## Quick start

```bash
git clone <repo> && cd <repo>
python3 tools/build_proof_tools.py          # kissat, drat-trim, cake_lpr (needs git, gcc, make, network); skip if you have the binaries
certificates/verify_cheap.sh                # about 9 minutes, 1.1 GB peak RAM; prints PASS/FAIL per verifier, exit code 1 on any mismatch
certificates/verify_certs.sh                # about 20 minutes, up to 8.3 GB RAM (uv + python peak); the multiplicity >= 4 exact certificates
python3 certificates/check_manifest.py      # sizes and sha256 of every file in MANIFEST.txt
```

Needs `uv` (https://docs.astral.sh/uv/), `xz`, Python 3.13. All Python runs use
`uv run --no-project --python 3.13 --with-requirements requirements.txt python ...`; the pinned versions are in
`requirements.txt` (numpy 2.2.6, scipy 1.16.3, networkx 3.6.1, python-sat 1.9.dev15, python-flint 0.9.0, ortools 9.15.6755,
matplotlib 3.10.8; the plain `--with numpy --with scipy --with networkx --with python-sat` resolution gave the same
numpy/scipy/networkx/python-sat on 2026-10-02). External tools: kissat 4.0.4 (rev 8af8e56f), drat-trim (rev 2e3b2dc0),
both pinned in `tools/proof_tools.lock.json`; cadical 3.0.1 (`tools/cadical/build/cadical`, only used through python-sat's
cadical153 in `regen.py`); T28's cube proofs were produced with cadical 1.9.5 per THEORY §22.
Logs of 2026-10-02: `certificates/logs/` = runs in the original working tree (the cheap suite as it was then, plus `ONLY=...` re-runs of the
steps added later, and all six exact certificates `cert_*.log` with `max_rss_kb`); `certificates/logs/fresh_copy/` = a complete run of the
final `verify_cheap.sh` (all steps PASS, 8 min 44 s, 1,060,184 kB peak RSS in `_time_cheap.txt`) and of `verify_certs.sh fcm25` from a fresh copy
of exactly the MANIFEST files (see below). The scripts can be started from anywhere inside the clone; they `cd` to the repository root, so a
LOGDIR argument is taken relative to the repository root (or absolute). `ONLY='step1 step2' certificates/verify_cheap.sh` runs a subset.

Files to commit: `awk '/^## OPTIONAL/{exit} !/^#/ && NF {print $3}' certificates/MANIFEST.txt | xargs git add -f` (188 files, 63.5 MB; `work/` is in
`.gitignore`). The OPTIONAL section (90 MB of corpus files) is only needed for `a30_defs_check`, which is skipped without it.

## Claims and how to verify them

Runtimes are wall clock on the development machine (24 cores shared with other jobs, one core used at a time).
"re-run" means executed on 2026-10-02 with the command shown and the key line found; "indexed" means not re-run (reason given).

| # | Claim | Certificate files | Verify command (repo root) | Expected key line | Time / RAM | Status |
|---|---|---|---|---|---|---|
| 1 | T <= 94 for multiplicity <= 3 (per-line LP weights, D = 16) | `work/eng/T25/rules_FC_full.json` (published table), `work/eng/T25/elim/state_2.pkl` (certs[1] = FC), graph via `work/eng/A30/elim/export_graph.py` | `certificates/verify_cheap.sh` (steps `fc_export`, `a30_export_graph`, `a30_audit_elim`) = `python certificates/check_fc_export.py`; `python work/eng/A30/elim/export_graph.py full work/eng/A30/elim/g_full.pkl`; `python work/eng/A30/elim/audit_elim.py` | `FC D= 16 graph=full min=32 need>=32 final_min=0 unused_keys=0 OK`; `rules_FC_full.json identical to the audited certificate: True` | 28 s + 9 s; 1.1 GB | re-run OK. The DP is A30's independent exact-integer DP (`dplib.py`), not T25's code |
| 2 | T <= 93 for multiplicity <= 3: the A30 audit, items 1-5 | item 1 tip lemma: `work/eng/T28/cert/lemma_*.cnf` + `.drat.xz`, `work/eng/A30/tip_cnf.py`; item 2 elimination: `work/eng/A30/elim/*` (certs68.pkl, g_a0.pkl, extra_certs.pkl) and `work/eng/T25/elim/state_{0,2}.pkl`; item 3 soundness: `work/eng/A30/soundness.py`; item 4 ILP: `work/eng/A30/ilp/*`, `work/eng/T25/elim/ilp*.py`; item 5 proof reviews: no code | `certificates/verify_cheap.sh`, steps `t28_tip_drat`, `a30_tip_own_drat`, `a30_tip_validate`, `a30_audit_elim`, `a30_audit_elim2`, `a30_soundness`, `a30_ident`, `a30_defs_check`, `a30_cpsat_*` | item 1: ten `s VERIFIED` (T28's proofs) and four `s VERIFIED` (A30's own encoding); item 2: `FD24 D= 144 ... min=288 need>=288 ... OK`, `strict-on-own-window OK: 55 of 55`, `CONSISTENT (all certs valid); tight edges 3464, terminals 161, windows 1154` and, for the 68 certificates, `tight edges 380, terminals 24, windows 205` + `equal: True  |w68 - a2|= 0  |a2 - w68|= 0`; item 3: `[rand seed 11] ... 'arr': 3000` with no `viol`; item 4: `f2shared status INFEASIBLE`, `aggregated total count range: [12, 12]` (f2disjoint), `[6, 6]` (f1), `all feasible triples: [(0, 0, 6), (1, 6, 3), (2, 12, 0)]`, ident `'F8_ok': 6881`; identities `'B==C': 7500` | each 1-100 s, in total about 5 min; 1.1 GB | items 1, 2, 4: re-run OK. Item 3: re-run on a 3,000-arrangement sample (2 processes); the full 130k-arrangement run is indexed (logs `work/eng/A30/sound_*.log`, about 1 h). Item 5 (written proof review): no code. `extremes.py` is not part of the suite: it demonstrates A30's finding that the LP box for the special columns is not a sufficient validity condition (it reports `VIOLATION` by design) |
| 3 | 6-X-point case: 2,841 cubes UNSAT, DRAT-verified | `work/eng/T28/x6cert/summary.json`, per-cube records `work/eng/T28/x6cert/*.jsonl`, cube list `work/eng/T28/x6_all.json`, generator `work/eng/T28/x6_cubes.py`, `search/flower_sat.py` | `python certificates/check_x6_cert.py` (records) and `python work/eng/T28/x6_drat.py OUT.jsonl 0 1 certificates/x6_sample.json` (3 sample cubes re-solved with kissat and re-checked with drat-trim; both in `verify_cheap.sh`: `x6_records`, `x6_sample`) | `cubes in x6_all.json: 2841; verified directly: 2840; verified via 17 sub-cubes: 1; not verified: 0`; three records with `'kissat_rc': 20` and `'verified': True` | 0 s; 7 s; 1.1 GB | records re-checked, 3 of 2,841 cubes re-run OK. Full re-run (`x6_drat.py OUT.jsonl 0 1 work/eng/T28/x6_all.json`, split over cores with start/stride) is indexed: about 3 s per easy cube, the hard cube (u = 2, S = (0,17)) is replaced by 17 sub-cubes (`x6_split28.json`); estimated 3 h on one core |
| 4a | Perturbation lemma (§24): only triple and bad 4-fold points in a (T,V)-maximal counterexample | `work/eng/pert/pert.py`, validation `validate_pert.py`; independent re-derivation `work/eng/pert2/faces_indep.py`, `pert_indep.py`; window code `work/eng/pert2/window.py` | `verify_cheap.sh` steps `validate_pert`, `pert_indep`, `faces_agree` | `4-fold points checked: 597 agree: 597 disagree: 0 patterns: 26`; `m=6 options 686 uncovered patterns 0`, `m 7 best score (t_loc - affected) 0` ... `m 17 ... 18`; `faces agreement: 1945 words compared, 0 mismatches` | 3 s, 18 s, 1 s | re-run OK |
| 4b | Pair lemma (§25): of 2,080 (4-fold, triple) patterns only 48 allowed | `work/eng/pert2/pair_PQ_all.json`, `pair_PQ_all.py`, independent `pair_indep.py`; validation `validate_pair2.py` | `verify_cheap.sh` steps `pair_PQ_all`, `pair_indep`, `validate_pair2` | `canonical patterns 2080 excluded 2032 allowed 48` and the regenerated JSON is byte-identical; `agree with pair_PQ_all.json: True | diff excluded 0 diff allowed 0`; `excluded pairs tested 643: reducible 643, FAIL 0; allowed-pattern pairs 2943` | 1 s, 1 s, 75 s | re-run OK (the earlier validation `validate_pair.py`, 127 pairs, is indexed) |
| 5 | T <= 94 for all arrangements (multiplicity >= 4 allowed), per-line LP, slack 1/4 (D = 16) | `work/eng/T27/cegar/w_FCM25.pkl`, `CERT_FCM25.txt` (statement and assumptions), `pats.json`, `work/eng/pert2/pair_PQ_all.json` | `certificates/verify_certs.sh certificates/logs fcm25`  (= `PAIRLEM=1 python work/eng/T27/verify_exact_cert.py work/eng/T27/cegar/w_FCM25.pkl 16 lp --class full --split --alpha --wr --sv --tri --pt --splitm --mb --wmax 1000 --projall AC,AL,LC,LR --pats work/eng/T27/cegar/pats.json --eps=-1/12`) | `exact DP min D*(2*final+2) = 24.0  target * D = 24.0  OK: True`; per-unit minima `{2: 720.0, 3: 696.0, ..., 16: 48.0, 17: 24.0}` | 136-170 s; 3.9 GB (uv + python) | re-run OK. Much faster than the 30-40 min / 30 GB expected: the graph is the reduced one without hidden-state tags (that variant, `--hidstate`, is for the open all-8 analysis and was not run) |
| 6a | No 94 with a 6-type bad point (margin 3; 9/8 without celldom) | `work/eng/oth/w_mw6.pkl`, `w_mw6_nocdy.pkl` (D = 16) | `certificates/verify_certs.sh certificates/logs mw6 mw6_nocdy` (`MWORD=6 PAIRLEM=1 [NOCELLDOM=1] python work/eng/T27/verify_exact_cert.py w.pkl 16 lp <common flags> --guarded --mvar --eps 0`) | `exact DP min D*(2*final+2) = 32.0  target * D = 32.0  OK: True`; per-unit list equal to `lp_mw6.log` | 219 s, 231 s; 8.3 GB | re-run OK. The commands are reconstructed (the original run lines were not recorded); the per-unit minima reproduce the original LP logs exactly |
| 6b | No 94 with a 7-type point and no all-8 point (margin 7/10), with and without celldom | `work/eng/oth/w_mw7_no8x.pkl`, `w_mw7_no8x_nocd.pkl` (D = 288) | `certificates/verify_certs.sh certificates/logs mw7_no8x mw7_no8x_nocd` (`MWORD=7 BADWORDS=67 [NOCELLDOM=1] PAIRLEM=1 ... --guarded --mcredit 5/2 --eps=-1/30`) | `exact DP min D*(2*final+2) = 520.0  target * D = 518.4  OK: True` | 216 s, 214 s; 8.0 GB | re-run OK, same remark |
| 6c | No 94 without (triple, 4-fold) adjacency (strict) | `work/eng/T27/cegar/w_TMXs.pkl` (D = 48) | `certificates/verify_certs.sh certificates/logs tmxs` (`TMX=1 PAIRLEM=1 python certificates/verify_exact_cert_strict.py w_TMXs.pkl 48 lp <common flags> --eps 0 --mstrict 1/24`; checks both the plain and the M-strict graph) | `exact DP min D*(2*final+2) = 96.0  target * D = 96.0  OK: True` and `second graph (M-strict) exact DP min = 100.0  target2 * D = 100.0  OK: True` | 195 s; 5.4 GB | re-run OK. `verify_exact_cert_strict.py` is new (the old `verify_exact_cert.py` does not check the second graph) |
| 7 | DRAT-verified CNFs: T27's four CEGAR frame patterns (`pats.json` entries 0-3) and the class-UNSAT all-8 core pattern | `work/eng/oth/drat_pats/regen.py` (writes `pat0..3.cnf` from `pats.json`; `pat2.cnf` is in the manifest, the other three are regenerable and byte-identical), `work/eng/T27/{patsat_m,sat_path}.py`, `work/eng/oth/core4/r_cnf/r_0.cnf` | `verify_cheap.sh` steps `pat_regen` (regenerate, cadical153 UNSAT, compare pat2.cnf) and `kissat_pat2` (`tools/kissat/build/kissat -q work/eng/oth/drat_pats/pat2.cnf`). Full DRAT check (not run): `kissat CNF PROOF; drat-trim CNF PROOF` | `0 vars 109927 clauses 633897 cadical: UNSAT` (and pats 1-3: `111884/640352`, `110216/632317`, `115388/657621`), `pat2.cnf regenerated byte-identical`; kissat `s UNSATISFIABLE`, exit code 20 | regen 3 min; kissat on pat2 20-28 s; drat-trim 4-16 min per CNF with a proof of about 1 GB | regen and kissat on pat2 re-run OK. Full drat-trim checks indexed (logged on 2026-10-01: pat0..3 `s VERIFIED` in 251 / 384 / 254 / 731 s, r_0 in 947 s; proofs discarded because of their size). `r_0.cnf` was not re-solved (generated by `work/eng/T27/class_run.py` / `class_cegar_driver.py`; the class solve took about 19 min, `work/eng/oth/core4/run.log`) |
| 8 | Checkers for the open all-8 analysis (sol's NOTE2, NOTE3; lead's K_1 payment, line ends) | `work/bbl/note2_check.py`, `note3_check.py`, `k1_pay_check.py`, `ends_check.py`; inputs `work/eng/lattice/{lattice18,lattice_family,mixed_all}.jsonl`, `work/phi/gallery18.jsonl`, `work/eng/oth/wit3/wit_sat.jsonl` | `verify_cheap.sh` steps `note2_check`, `note3_check`, `k1_pay_check`, `ends_check` (e.g. `python work/bbl/note2_check.py work/eng/lattice/lattice18.jsonl work/eng/lattice/lattice_family.jsonl work/eng/lattice/mixed_all.jsonl work/phi/gallery18.jsonl`) | note2: `Payment checks: 3446 arrangements; failures=0`, `Pencil-touch checks: 18979 points; 265 all-8 points; failures=0`, stdout byte-identical to `work/bbl/all8_work/note2_check_extended.out`; note3 (with `wit_sat.jsonl` as 5th input): `Dataset checks: {... 'arrangements': 3474 ...} failures=0`; k1: `arrangements 3445 K_1 kites: case A 238 case B 1 failures 0`; ends: `... violations 0` | 12 s, 13 s, 9 s, 1 s; 1.1 GB | re-run OK. These verify the lemmas on data, they are not exhaustive proofs. note3's stdout equals `git show HEAD:work/bbl/all8_work/note3_check.out`; the uncommitted working-tree copy of that file differs (it records 3,445 arrangements, K1B 1) |

Common flags of the 6x rows: `--class full --split --alpha --wr --sv --tri --pt --splitm --mb --wmax 1000 --projall AC,AL,LC,LR --pats work/eng/T27/cegar/pats.json`.

## What the exact checks do

`verify_exact_cert.py` rebuilds the line-automaton product graph with the same flags as the LP run, rounds every stored
weight to an integer over D (asserting that this is exact), and runs an exact integer layered DP: every path has
D*(2*final+2) >= target*D, so `final >= -eps0` on every line. `Sum final + waste = 3*Lambda - 18`, `waste >= 0`, and
`3*Lambda - 18` is a multiple of 9, which gives Lambda >= 6, i.e. T <= 94 (THEORY §20, §26). For row 1 the same inequality is
also checked by A30's independent DP (`dplib.py`), which shares only the graph topology with T25's code.

## Edits made to existing files for reproducibility (paths only)

Only hard-coded or cwd-relative path lines were changed, to compute the repository root from `__file__`
(`Path(__file__).resolve().parents[k]`). The list of edited files is in `certificates/EDITED_FILES.txt`.

## Known limitations

* No Lean or other proof-assistant formalisation. The verifiers are Python programs; their exactness is integer arithmetic
  (numpy int64, Fractions), but the code was not formally verified.
* The SAT encodings (`patsat_m`, `classsat`, the A30 tip encoding `tip_cnf.py`, `flower_sat.build_X6`) are validated against
  real arrangements (160+ pinned cases; about 4,950 exact arrangements for the tip encoding) but not formally verified.
  DRAT proves that a CNF is unsatisfiable, not that the CNF encodes the geometric statement.
* Hand proofs, not machine checked: the guarded facts at 4-fold apexes (K3 and F4' used only where the apex is exactly
  triple; validated on 543k real lines, 0 violations), the 5th CEGAR pattern (`pats.json` entry 4 is a hand fact), the cube-defining
  lemmas E2-E5 and the block lemma of the 6-X case (hand-derived from Z = 0; no real arrangement has Z = 0, so they cannot be
  tested on data), the special-column identities B = C and A = 3C/2 for multiplicity >= 4 ("a proof for M is outstanding",
  CERT_FCM25.txt), the perturbation lemma's reduction (§24, exhaustive local re-drawings, validated on 597 real points and independently
  re-derived but not proved in the model), and the model soundness chain for M windows (validated on data).
* The pair lemma (§25) and the perturbation lemma are computations (window enumerations), cross-checked by an independent
  implementation (`faces_indep.py`, `pair_indep.py`, `pert_indep.py`) but not DRAT- or proof-checked.
* The A30 independent audit covers multiplicity <= 3 only (rows 1-2). The multiplicity >= 4 certificates (rows 5-6) were re-verified
  today with the *same* code base that produced them (`verify_exact_cert.py` rebuilds the graph with `search/rule_lp_t25m.py`); there is
  no independent audit of that graph construction yet (STATUS_K18.md, verification debts).
* The commands for rows 6a-6c are reconstructed from the LP logs and THEORY; they reproduce the stored DP minima exactly
  (identical per-unit lists), but the original command lines were not recorded.
* The open case (an all-8 point) is not covered; row 8 only checks lemmas used in the partial analysis.

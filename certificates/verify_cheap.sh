#!/bin/bash
# Cheap verifiers of the Kobon K(18) proof certificates (about 6 minutes, < 2 GB RAM, 1 core at a time).
# usage: [ONLY='name1 name2'] certificates/verify_cheap.sh [LOGDIR]      (default LOGDIR = certificates/logs; ONLY runs a subset)
# Runs every verifier, saves its exact stdout to LOGDIR/<name>.log, greps the expected key lines and exits nonzero on any mismatch.
# Needs: uv, xz, and tools/kissat/build/kissat + tools/drat-trim/drat-trim (python tools/build_proof_tools.py builds them).
set -u
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
LOG=${1:-$ROOT/certificates/logs}
mkdir -p "$LOG"
TMP=$(mktemp -d "${TMPDIR:-/tmp}/kobon_verify.XXXXXX")
PY="uv run --no-project --python 3.13 --with-requirements $ROOT/requirements.txt python"
KISSAT=$ROOT/tools/kissat/build/kissat
DRAT=$ROOT/tools/drat-trim/drat-trim
IN4="work/eng/lattice/lattice18.jsonl work/eng/lattice/lattice_family.jsonl work/eng/lattice/mixed_all.jsonl work/phi/gallery18.jsonl"
FAIL=0
export ROOT PY KISSAT DRAT IN4 TMP LOG

# run NAME 'shell command' 'expected1' 'expected2' ...   expected = fixed string; 're:PATTERN' = extended regex; '!:STRING' = must NOT occur
run() {
  local name=$1 cmd=$2; shift 2
  if [ -n "${ONLY:-}" ]; then case " $ONLY " in *" $name "*) ;; *) return ;; esac; fi
  local t0=$(date +%s)
  bash -c "$cmd" > "$LOG/$name.log" 2>&1
  local rc=$? ok=1 e
  for e in "$@"; do
    case "$e" in
      re:*) grep -aEq -- "${e#re:}" "$LOG/$name.log" || { ok=0; echo "   missing (regex): ${e#re:}"; } ;;
      '!:'*) grep -aFq -- "${e#!:}" "$LOG/$name.log" && { ok=0; echo "   forbidden line present: ${e#!:}"; } ;;
      *) grep -aFq -- "$e" "$LOG/$name.log" || { ok=0; echo "   missing: $e"; } ;;
    esac
  done
  [ $rc -ne 0 ] && { ok=0; echo "   exit code $rc"; }
  if [ $ok = 1 ]; then echo "PASS  $name  ($(( $(date +%s)-t0 ))s)"; else echo "FAIL  $name  ($(( $(date +%s)-t0 ))s) see $LOG/$name.log"; FAIL=1; fi
}

for b in "$KISSAT" "$DRAT"; do [ -x "$b" ] || { echo "missing $b: run python tools/build_proof_tools.py"; exit 2; }; done

# ---- THEORY 24/25: perturbation lemma and pair lemma -------------------------------------------------------
run pair_PQ_all "mkdir -p $TMP/pq && cd $TMP/pq && $PY $ROOT/work/eng/pert2/pair_PQ_all.py && cmp pair_PQ_all.json $ROOT/work/eng/pert2/pair_PQ_all.json && echo 'pair_PQ_all.json IDENTICAL to the stored file'" \
  "canonical patterns 2080 excluded 2032 allowed 48" "pair_PQ_all.json IDENTICAL to the stored file"
run pair_indep "$PY work/eng/pert2/pair_indep.py" \
  "independent: patterns 2080 excluded 2032 allowed 48" "agree with pair_PQ_all.json: True | diff excluded 0 diff allowed 0"
run pert_indep "$PY work/eng/pert2/pert_indep.py" \
  "m=6 options 686 uncovered patterns 0" "m 7 best score (t_loc - affected) 0" "m 17 best score (t_loc - affected) 18"
run faces_agree "$PY certificates/check_faces_agree.py" "faces agreement: 1945 words compared, 0 mismatches"
run validate_pert "$PY work/eng/pert/validate_pert.py" "4-fold points checked: 597 agree: 597 disagree: 0 patterns: 26"
run validate_pair2 "$PY work/eng/pert2/validate_pair2.py" "excluded pairs tested 643: reducible 643, FAIL 0; allowed-pattern pairs 2943"

# ---- THEORY 27: checkers for the open all-8 analysis -------------------------------------------------------
run note2_check "$PY work/bbl/note2_check.py $IN4 > $TMP/note2.out; cat $TMP/note2.out; cmp $TMP/note2.out work/bbl/all8_work/note2_check_extended.out && echo 'IDENTICAL to all8_work/note2_check_extended.out'" \
  "Payment checks: 3446 arrangements; failures=0" "Pencil-touch checks: 18979 points; 265 all-8 points; failures=0" "Triple sector-word checks: 64; failures=0" "IDENTICAL to all8_work/note2_check_extended.out"
run note3_check "$PY work/bbl/note3_check.py $IN4 work/eng/oth/wit3/wit_sat.jsonl" \
  "Zero-slack local enumeration: {'configurations': 569, 'shapes': {'(2, 2, 2)': 12, '(3, 3, 1)': 8, '(4, 4, 0)': 2}, 'failures': 0}" \
  "'arrangements': 3474" "'W': 30623" "failures=0"
run k1_pay_check "$PY work/bbl/k1_pay_check.py $IN4" "arrangements 3445 K_1 kites: case A 238 case B 1 failures 0"
run ends_check "$PY work/bbl/ends_check.py $IN4" "arrangements 3445 {'bad-wedge': 61006, 'good-token': 4780, 'good-unused': 57307, 'bad-I4': 83, 'good-I3': 844} violations 0"

# ---- THEORY 20-23: multiplicity <= 3 (FC certificate T <= 94, A30 independent audit) ------------------------
run a30_export_graph "$PY work/eng/A30/elim/export_graph.py full work/eng/A30/elim/g_full.pkl" "saved "
run a30_audit_elim "$PY work/eng/A30/elim/audit_elim.py" \
  "bounds violations: 0" "re:^FC +D= +16 graph=full min=32 need>=32 final_min=0 unused_keys=0 +OK" "re:^FD24 +D= +144 graph=full min=288 need>=288 final_min=0 unused_keys=0 +OK" \
  "strict-on-own-window OK: 55 of 55" "CONSISTENT (all certs valid); tight edges 3464, terminals 161, windows 1154" "!:FAIL" "!:INCONSISTENT"
run a30_audit_elim2 "$PY work/eng/A30/elim/audit_elim2.py" \
  "CONSISTENT (all certs valid); tight edges 380, terminals 24, windows 205" "equal: True  |w68 - a2|= 0  |a2 - w68|= 0" "!:FAIL" "!:INCONSISTENT"
run a30_soundness "$PY work/eng/A30/soundness.py rand 3000 11 2" "[rand seed 11]" "'arr': 3000" "!:viol" "!:Traceback"
run a30_ident "$PY work/eng/A30/ilp/ilp_identities.py rand 800 21" "[rand seed 21] {'F3_columns_seen': 232, 'F8_ok': 6881, 'F8_skipped_line_ends_at_point': 2121, 'arr': 800, 'simple_vertices': 95394, 'triple_points': 9002}"
[ -f work/phi/near18.jsonl ] || echo "SKIP  a30_defs_check (needs work/phi/{near18,dpwalk2_18,dpwalk93}.jsonl, 90 MB, not in the minimal manifest)"
[ -f work/phi/near18.jsonl ] && run a30_defs_check "$PY work/eng/A30/defs_check.py" "{'arr': 7500, 'B==C': 7500, 'A==1.5C': 7500, 'V0+1.5C==3Lam-n': 7500, 'sum s == Lambda': 7500, 'C==direct triple-endpoint count': 7500"
run a30_cpsat_f2shared "$PY work/eng/A30/ilp/cpsat_ilp.py f2shared" "f2shared status INFEASIBLE"
run a30_cpsat_f2disjoint "$PY work/eng/A30/ilp/cpsat_ilp.py f2disjoint" "hexagon-line groups (C0/C2 tags), aggregated total count range: [12, 12]"
run a30_cpsat_f1 "$PY work/eng/A30/ilp/cpsat_ilp.py f1" "hexagon-line groups (C0/C2 tags), aggregated total count range: [6, 6]"
run a30_cpsat_f0 "$PY work/eng/A30/ilp/cpsat_ilp.py f0" "f0 status OPTIMAL"
run a30_cpsat_free "$PY work/eng/A30/ilp/cpsat_free.py" "all feasible triples: [(0, 0, 6), (1, 6, 3), (2, 12, 0)]"

# ---- THEORY 20 / 22: the published FC rule table is the audited certificate; stored 6-X cube records are complete ----
run fc_export "$PY certificates/check_fc_export.py" "rules_FC_full.json identical to the audited certificate: True"
run x6_records "$PY certificates/check_x6_cert.py" "cubes in x6_all.json: 2841; verified directly: 2840; verified via 17 sub-cubes: 1; not verified: 0" "x6 certificate records consistent: True"

# ---- THEORY 22: tip lemma, DRAT (T28's 10 proofs, and A30's independent encoding in 4 variants) --------------
run t28_tip_drat "for c in work/eng/T28/cert/lemma_*.cnf; do b=\$(basename \$c .cnf); xz -dc work/eng/T28/cert/\$b.drat.xz > $TMP/\$b.drat; echo \$b \$($DRAT \$c $TMP/\$b.drat -t 1000 | grep -ao 's VERIFIED\|s NOT VERIFIED'); done" \
  "re:^lemma_000_tips03 s VERIFIED" "re:^lemma_000_tips03_min s VERIFIED" "re:^lemma_001_tips03 s VERIFIED" "re:^lemma_010_tips25 s VERIFIED" "re:^lemma_011_tips14 s VERIFIED" \
  "re:^lemma_100_tips14 s VERIFIED" "re:^lemma_101_tips25 s VERIFIED" "re:^lemma_110_tips03 s VERIFIED" "re:^lemma_111_tips03 s VERIFIED" "re:^lemma_111_tips03_min s VERIFIED" "!:NOT VERIFIED"
run a30_tip_own_drat "$PY work/eng/A30/mkcnf.py && for v in m0_s0 m0_s1 m1_s0 m1_s1; do c=work/eng/A30/drat/own_\$v.cnf; $KISSAT -q \$c $TMP/\$v.drat | grep -a '^s '; echo \$v \$($DRAT \$c $TMP/\$v.drat -t 1000 | grep -ao 's VERIFIED\|s NOT VERIFIED'); done" \
  "re:^m0_s0 s VERIFIED" "re:^m0_s1 s VERIFIED" "re:^m1_s0 s VERIFIED" "re:^m1_s1 s VERIFIED"
run a30_tip_validate "$PY work/eng/A30/tip_validate.py 11 600" "'axiom_fail': 0" "'mismatch': 0" "'both_ends': 0"

# ---- THEORY 22 note: 6-X case, 3 sample cubes of 2,841 (kissat + drat-trim) --------------------------------
run x6_sample "$PY work/eng/T28/x6_drat.py $TMP/x6_sample.jsonl 0 1 certificates/x6_sample.json" \
  "{'u': 0, 'idx': 0, 'S': [], 'split': None, 'kissat_rc': 20," "{'u': 2, 'idx': 4, 'S': [0, 9], 'split': None, 'kissat_rc': 20," "{'u': 4, 'idx': 1, 'S': [0, 1, 2, 5], 'split': None, 'kissat_rc': 20," "'verified': True" "!:'verified': False"

# ---- THEORY 26: one DRAT-checked CEGAR frame pattern, kissat only (the 4 proofs take 4-12 min each with drat-trim) ---
run kissat_pat2 "$KISSAT -q work/eng/oth/drat_pats/pat2.cnf; echo kissat_exit=\$?" "s UNSATISFIABLE" "kissat_exit=20"

# regenerate the four CNFs of T27's CEGAR frame patterns from pats.json (cadical153 must answer UNSAT; ~3 min) and compare pat2.cnf with the stored file
run pat_regen "cp work/eng/oth/drat_pats/pat2.cnf $TMP/pat2.orig && $PY work/eng/oth/drat_pats/regen.py && cmp work/eng/oth/drat_pats/pat2.cnf $TMP/pat2.orig && echo 'pat2.cnf regenerated byte-identical'" \
  "re:^0 vars 109927 clauses 633897 cadical: UNSAT" "re:^1 vars 111884 clauses 640352 cadical: UNSAT" "re:^2 vars 110216 clauses 632317 cadical: UNSAT" "re:^3 vars 115388 clauses 657621 cadical: UNSAT" "pat2.cnf regenerated byte-identical"

rm -rf "$TMP"
if [ $FAIL = 0 ]; then echo "ALL CHEAP VERIFIERS PASSED"; else echo "SOME VERIFIERS FAILED"; exit 1; fi

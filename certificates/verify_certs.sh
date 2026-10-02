#!/bin/bash
# Exact re-verification of the multiplicity >= 4 LP certificates (each: rebuild the DP graph, round the stored weights to
# integers / D, run the exact integer DP; about 3-5 minutes and 2-4 GB RAM each, about 25 minutes in total, single core).
# usage: certificates/verify_certs.sh [LOGDIR] [NAME ...]    NAME in fcm25 mw6 mw6_nocdy mw7_no8x mw7_no8x_nocd tmxs (default: all)
set -u
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
LOG=${1:-$ROOT/certificates/logs}; shift 2>/dev/null
mkdir -p "$LOG"
WANT=${*:-fcm25 mw6 mw6_nocdy mw7_no8x mw7_no8x_nocd tmxs}
PY="uv run --no-project --python 3.13 --with-requirements $ROOT/requirements.txt python -u"
COMMON="--class full --split --alpha --wr --sv --tri --pt --splitm --mb --wmax 1000 --projall AC,AL,LC,LR --pats work/eng/T27/cegar/pats.json"
FAIL=0
# runcert NAME ENV... -- script weights D flags...   (expected: "OK: True" line(s) printed by the verifier)
runcert() {
  local name=$1; shift
  case " $WANT " in *" $name "*) ;; *) return ;; esac
  local t0=$(date +%s)
  /usr/bin/time -f "max_rss_kb=%M" -o "$LOG/cert_$name.time" env PAIRLEM=1 "$@" > "$LOG/cert_$name.log" 2>&1
  local rc=$?
  if [ $rc = 0 ] && grep -aq "OK: True" "$LOG/cert_$name.log" && ! grep -aq "OK: False" "$LOG/cert_$name.log" && ! grep -aq "FAILED" "$LOG/cert_$name.log"; then
    echo "PASS  cert_$name  ($(( $(date +%s)-t0 ))s, $(cat $LOG/cert_$name.time | tail -1))"; grep -a "exact DP min" "$LOG/cert_$name.log" | sed 's/^/      /'
  else echo "FAIL  cert_$name  see $LOG/cert_$name.log"; FAIL=1; fi
}
# THEORY 26: T <= 94 for every arrangement (multiplicity >= 4 allowed); expected "exact DP min D*(2*final+2) = 24.0  target * D = 24.0  OK: True"
runcert fcm25 $PY work/eng/T27/verify_exact_cert.py work/eng/T27/cegar/w_FCM25.pkl 16 lp $COMMON --eps=-1/12
# THEORY 26: no 94 with a 6-type bad point (margin 3; without celldom margin 9/8)
runcert mw6 MWORD=6 $PY work/eng/T27/verify_exact_cert.py work/eng/oth/w_mw6.pkl 16 lp $COMMON --guarded --mvar --eps 0
runcert mw6_nocdy MWORD=6 NOCELLDOM=1 $PY work/eng/T27/verify_exact_cert.py work/eng/oth/w_mw6_nocdy.pkl 16 lp $COMMON --guarded --mvar --eps 0
# THEORY 26: no 94 with a 7-type point and no all-8 point (margin 7/10), with and without celldom
runcert mw7_no8x MWORD=7 BADWORDS=67 $PY work/eng/T27/verify_exact_cert.py work/eng/oth/w_mw7_no8x.pkl 288 lp $COMMON --guarded --mcredit 5/2 --eps=-1/30
runcert mw7_no8x_nocd MWORD=7 BADWORDS=67 NOCELLDOM=1 $PY work/eng/T27/verify_exact_cert.py work/eng/oth/w_mw7_no8x_nocd.pkl 288 lp $COMMON --guarded --mcredit 5/2 --eps=-1/30
# THEORY 25: no 94 without (triple, 4-fold) adjacency; strict certificate (second graph: paths through an M4 frame have final >= 1/24 - checked too)
runcert tmxs TMX=1 $PY certificates/verify_exact_cert_strict.py work/eng/T27/cegar/w_TMXs.pkl 48 lp $COMMON --eps 0 --mstrict 1/24
[ $FAIL = 0 ] && echo "ALL CERTIFICATES VERIFIED" || { echo "SOME FAILED"; exit 1; }

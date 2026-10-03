#!/bin/bash
# usage: prove_k.sh K i   : kissat + drat-trim on cnf_K$K/pat$i.cnf (proof file deleted after check)
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$HERE/../../.." && pwd)
K=$1; i=$2; d=$HERE/cnf_K$K; f=$d/pat$i.cnf
{ /usr/bin/time -v "$ROOT/tools/kissat/build/kissat" -q "$f" "$d/pat$i.drat" ; } > "$HERE/log_kissat_K${K}_pat$i.log" 2>&1
timeout 3000 "$ROOT/tools/drat-trim/drat-trim" "$f" "$d/pat$i.drat" -t 3000 > "$HERE/log_dratcheck_K${K}_pat$i.log" 2>&1
tail -3 "$HERE/log_dratcheck_K${K}_pat$i.log" | grep -i "verified\|s " >> "$HERE/log_kissat_K${K}_pat$i.log"
rm -f "$d/pat$i.drat"

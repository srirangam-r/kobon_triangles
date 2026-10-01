#!/bin/bash
# CEGAR loop for the all-8 case (lead): LP with margin >= 1/100 -> core -> class SAT (K=18, bad words, pair lemma) -> UNSAT patterns -> repeat
cd /home/nail/stuff/sundai_math
D=work/eng/oth/loop
PATS=${1:-work/eng/oth/pats_c1.json}
for k in $(seq 1 12); do
  echo "=== round $k $(date +%H:%M) pats=$(python3 -c "import json;print(len(json.load(open('$PATS'))))")" >> $D/driver.log
  env PAIRLEM=1 MWORD=78 BADWORDS=78 EPSX=1 DELTAMAX=200 timeout 5000 uv run --no-project --with numpy --with scipy --with networkx --with python-sat python -u search/rule_lp_t25m.py lp --class full --split --alpha --wr --sv --tri --pt --splitm --mb --wmax 1000 --projall AC,AL,LC,LR --par 4 --time-limit 4800 --pats $PATS --core --guarded --eps 0 --mvar --mvarmargin 1/100 --save $D/w_r$k.pkl --dump $D/cuts_r$k.json > $D/lp_r$k.log 2>&1
  if grep -q "exact certificate: denominator [0-9]" $D/lp_r$k.log; then echo "CERTIFICATE round $k" >> $D/driver.log; grep "exact cert" $D/lp_r$k.log >> $D/driver.log; exit 0; fi
  grep -E "core size" $D/lp_r$k.log | cut -c1-300 >> $D/driver.log
  if ! grep -q "core size" $D/lp_r$k.log; then echo "no core (rationalisation failed?)" >> $D/driver.log; exit 1; fi
  timeout 7000 uv run --no-project --with numpy --with scipy --with networkx --with python-sat python -u work/eng/T27/class_run.py $D/cuts_r$k.json $D/lp_r$k.log $D/cls_r$k 16 1500 >> $D/driver.log 2>&1
  NEW=work/eng/oth/loop/pats_r$((k+1)).json
  python3 - "$PATS" "$D/cls_r$k.json" "$NEW" >> $D/driver.log <<'PY'
import json, sys
p = json.load(open(sys.argv[1])); r = json.load(open(sys.argv[2])); n0 = len(p)
for x in r:
    if x["cls"] == "UNSAT":
        p.append({"preds": x["preds"], "src": x["s"][:200], "core": x.get("core"), "cnf": x.get("cnf"), "class": True})
json.dump(p, open(sys.argv[3], "w"))
print("new UNSAT patterns", len(p) - n0, "classes", {c: sum(1 for x in r if x["cls"] == c) for c in set(x["cls"] for x in r)})
PY
  if [ "$(python3 -c "import json;print(len(json.load(open('$NEW'))))")" = "$(python3 -c "import json;print(len(json.load(open('$PATS'))))")" ]; then echo "STALLED round $k (no new UNSAT)" >> $D/driver.log; exit 2; fi
  PATS=$NEW
done

#!/bin/bash
# wait for the n=16 bridge extension, then run the top-17 bridge-preserving cores on the same 18 workers
cd /home/nail/stuff/sundai_math
until [ -f work/lns/push/ext16_bridges/summary.json ]; do sleep 60; done
echo "- $(date -u +%H:%M) n=16 bridge extension done: $(python3 -c "import json; d=json.load(open('work/lns/push/ext16_bridges/summary.json')); print(d['done'], 'calls', d['UNSAT'], 'UNSAT', d['SAT'], 'SAT')"). Starting top-17 bridge-preserving cores (T16 66-67)." >> work/lns/PROGRESS.md
uv run --no-project --with python-sat python work/lns/push/run_ext.py --seeds work/lns/push/cores16_bridge_a.json --workers 18 --out work/lns/push/cores16_bridge_a --deadline-min 900 >> work/lns/push/cores16_bridge_a.out 2>&1
echo "- $(date -u +%H:%M) top-17 cores done: $(python3 -c "import json; d=json.load(open('work/lns/push/cores16_bridge_a/summary.json')); print(d['done'], 'calls', d['UNSAT'], 'UNSAT', d['SAT'], 'SAT')")." >> work/lns/PROGRESS.md

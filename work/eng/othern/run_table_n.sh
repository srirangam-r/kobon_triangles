#!/bin/bash
# usage: run_table_n.sh n   -> exports the FC graph at W=n-1, runs the exact DP with the FC weights, logs, deletes the graph
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$HERE/../../.." && pwd); cd "$ROOT"
n=$1; W=$((n-1)); g=$HERE/g_W$W.pkl
PY="uv run --no-project --with numpy --with scipy --with networkx --with python-sat python"
S=$(date +%s)
$PY work/eng/othern/export_graph_n.py full $g --exactw $W > $HERE/log_table_export_n$n.log 2>&1
$PY work/eng/othern/check_w.py $g $W work/eng/T25/elim/state_2.pkl 1 > $HERE/log_table_dp_n$n.log 2>&1
echo "wall $(( $(date +%s)-S )) s" >> $HERE/log_table_dp_n$n.log
rm -f $g

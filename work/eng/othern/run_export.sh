#!/bin/bash
# usage: run_export.sh W [extra flags]  -> g_W{W}[_nocd].pkl
cd "$(dirname "$0")/../../.."
W=$1; shift
uv run --no-project --with numpy --with scipy --with networkx --with python-sat python work/eng/othern/export_graph_n.py full work/eng/othern/g_W$W$SUF.pkl --exactw $W "$@"

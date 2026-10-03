#!/bin/bash
# usage: run_table_all.sh n1 n2 ...   sequential
HERE=$(cd "$(dirname "$0")" && pwd)
for n in "$@"; do [ -f $HERE/log_table_dp_n$n.log ] && grep -q "wall" $HERE/log_table_dp_n$n.log && continue; $HERE/run_table_n.sh $n; done

#!/bin/bash
# usage: run.sh <cnf> <timeout_s>  -> appends "<cnf>: SAT|UNSAT|timeout <secs>" to results.log, model to <cnf>.model
f=$1; lim=$2; t0=$(date +%s.%N)
timeout $lim ../../tools/kissat/build/kissat -q $f > $f.model; rc=$?
t1=$(date +%s.%N); v=timeout; [ $rc = 10 ] && v=SAT; [ $rc = 20 ] && v=UNSAT
[ "$v" = SAT ] || rm -f $f.model
echo "$f: $v $(echo "$t1 - $t0" | bc | cut -c1-7)s" >> results.log

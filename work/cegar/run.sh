#!/bin/sh
# CEGAR probe: SAT-seeking solves of the k=5, beta>=1 instances (k5b, k5b2), 4 seeds each, 2 h cap.
# Any SAT model is a pseudo-94 satisfying every encoded (refereed) constraint: either a real 94 or a target lemma.
cd /home/nail/stuff/sundai_math
for inst in k5b k5b2; do for seed in 1 2 3 4; do
  ( timeout 7200 tools/kissat/build/kissat --sat --seed=$seed work/$inst/$inst.cnf > work/cegar/${inst}_s$seed.out 2>&1; echo "exit $?" >> work/cegar/${inst}_s$seed.out ) &
done; done
wait; echo ALL DONE > work/cegar/done

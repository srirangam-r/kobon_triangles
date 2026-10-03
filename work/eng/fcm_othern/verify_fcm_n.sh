#!/bin/bash
# usage: verify_fcm_n.sh W   (W = n-1; n=14 -> 13; n=18 -> 17 reproduces the certified line)
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$HERE/../../.." && pwd); cd "$ROOT"
W=${1:-13}
PAIRLEM=1 uv run --no-project --python 3.13 --with-requirements requirements.txt python -u work/eng/T27/verify_exact_cert.py work/eng/T27/cegar/w_FCM25.pkl 16 lp \
 --class full --split --alpha --wr --sv --tri --pt --splitm --mb --wmax 1000 --projall AC,AL,LC,LR --pats work/eng/T27/cegar/pats.json --eps=-1/12 --exactw $W \
 > "$HERE/log_verify_W$W.log" 2>&1

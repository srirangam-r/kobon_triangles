#!/bin/sh
# One official attempt: commit everything in scope, score it, print the report summary.
#   search/run.sh <NNN-slug> <submission_dir> <n> "<commit description>"
set -eu
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")/.."
git add -A search submissions reports journal.html .gitignore
git commit -q -m "hills/kobon-triangles: $4" -m "Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>" || true
hills eval "$2" -H kobon-triangles -p n="$3" -o "reports/$1.json" > /dev/null 2> "${EVAL_LOGS:-/tmp}/eval-$1.log" || true
python3 - "$1" <<'PY'
import json, sys
r = json.load(open(f"reports/{sys.argv[1]}.json"))
print(sys.argv[1], "passed" if r["passed"] else "FAILED", r["metrics"], r["params"], r["submission_git"], (r["details"] or {}).get("error"))
PY

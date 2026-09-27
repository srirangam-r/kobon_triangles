#!/bin/sh
# Release all AutoLab rentals for the climb once rental spend reaches the cap (default $75).
# Run every 5 minutes by the systemd user timer kobon-rental-guard.timer.
CAP="${1:-75}"
export PATH="$HOME/.local/bin:$PATH"
TOK=$(autolab --url https://app.autolab.ai token 2>/dev/null | tail -1)
SPEND=$(curl -s -m 30 -H "Authorization: Bearer $TOK" https://app.autolab.ai/api/v1/projects/srirangam-r/kobon-triangles-18/compute \
  | python3 -c "import json,sys; print(json.load(sys.stdin).get('spend_usd') or 0)" 2>/dev/null)
echo "$(date -u +%FT%TZ) rental spend \$${SPEND:-?} cap \$$CAP"
if [ -n "$SPEND" ] && python3 -c "import sys; sys.exit(0 if float('$SPEND') >= float('$CAP') else 1)"; then
  autolab --url https://app.autolab.ai compute stop --project srirangam-r/kobon-triangles-18
  echo "cap reached: rentals released"
fi

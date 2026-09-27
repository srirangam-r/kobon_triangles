#!/bin/sh
# Run one search job on an AutoLab node with its own Python deps (numpy, numba).
#   sh search/job.sh --minutes 30 --seed 1
set -eu
export PATH="$HOME/.local/bin:$PATH"
command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh
uv run --no-project --python ">=3.11" --with numpy --with numba python search/job.py "$@"

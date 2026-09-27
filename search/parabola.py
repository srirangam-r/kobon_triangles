"""The hill's baseline family at any n: tangents 2*i*x - y - i*i = 0 to y = x^2.

    python3 search/parabola.py <n> <submission_dir>
"""
import json
import sys
from pathlib import Path

n, out = int(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
(out / "solution.json").write_text(json.dumps({"lines": [[2 * i, -1, -i * i] for i in range(n)]}) + "\n")

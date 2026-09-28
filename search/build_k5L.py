"""k5L base: the audited k5g instance (build_k5g.build_g) plus the label layer (search/k5L_layer.py) and a forward
counter on the canonical slacks s(r,i,j), so a cube can cap Z <= B + beta - 9 for its graph (D-count, C34 (a);
Z <= sum s since every unused segment has a canonical slack). Per-graph cubes: search/k5L_cubes.py.
Layer semantics are checked on real arrangements by search/test_k5L_layer.py.

    uv run --no-project --with python-sat python search/build_k5L.py work/k5L/k5L.cnf
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_k5g import build_g  # noqa: E402
from build_k5b import n  # noqa: E402
from k5L_layer import add_labels, upper  # noqa: E402

KZ = 6  # counter outputs ZR[1..KZ]; the k5g base already has sum s <= 5


def main():
    out = sys.argv[1]
    cnf, pool, g = build_g(zmax=5)
    base_top = pool.top
    ids = add_labels(cnf, pool, n, g["z"], g["tri"], g["blk"], g["F"], g["G"], nlab=5)
    zr = upper(cnf, pool, list(g["s"].values()), KZ, "LZr")
    ids["ZR"] = {str(j): zr[j] for j in range(1, KZ + 1)}
    ids["top"] = pool.top
    ids["k5g_top"] = base_top
    cnf.to_file(out)
    json.dump(ids, open(Path(out).with_suffix(".ids.json"), "w"))
    print(f"{out}: vars {pool.top}, clauses {len(cnf.clauses)} (k5g part: vars {base_top})")


if __name__ == "__main__":
    main()

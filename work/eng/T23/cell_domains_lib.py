"""helper for T25: cell domains.  from cell_domains_lib import AXIS_CELLS, cell_ok
AXIS_CELLS: set of cells (ring5 tuple, u, pL, pR, tL, tR, oth tuple) realizable as the block signature seen from the axis line."""
import json
from pathlib import Path
_D = json.load(open(Path(__file__).resolve().parent / "cell_domains.json"))
AXIS_CELLS = set((tuple(c[0]), c[1], c[2], c[3], c[4], c[5], tuple(c[6])) for c in _D["axis_cells"])
def cell_ok(cell):
    return cell in AXIS_CELLS

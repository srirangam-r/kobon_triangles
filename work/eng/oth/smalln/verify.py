import sys, json
sys.path.insert(0, "work/eng/oth"); sys.path.insert(0, "work/t3"); sys.path.insert(0, "work/eng/comp")
import importlib.util
spec = importlib.util.spec_from_file_location("k1", "work/eng/oth/k1_scan.py")
src = open("work/eng/oth/k1_scan.py").read().split("files = [")[0]
ns = {}; exec(src, ns)
from arr import Arr
from bad_comp import tri_sectors
for line in sys.stdin:
    d = json.loads(line)
    if d.get("result") != "SAT": continue
    a = Arr(d["gens"], d["n"])
    words = ["".join(map(str, tri_sectors(a, P))) for P, ev in enumerate(a.events) if len(ev) == 4]
    print(d["n"], "T", a.T(), "Lambda", d["n"] * (d["n"] - 2) - 3 * a.T(), "inclass", ns["inclass"](a), "quad words", words)

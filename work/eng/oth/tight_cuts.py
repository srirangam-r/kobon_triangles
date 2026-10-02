# List the cuts that are tight at the final LP weights (binding DP paths), focusing on paths through M vertices.
import json, pickle, sys
from collections import Counter
dump = json.load(open(sys.argv[1])); w = pickle.load(open(sys.argv[2], "rb"))
W = {repr(k): v for k, v in w.items()}
rows = []
for c in dump:
    val = c["v2"] + sum(x * W.get(k, 0.0) for k, x in c["counts"].items())
    tgt = c["target"] if c.get("target") is not None else 2.0
    rows.append((val - tgt, c))
rows.sort(key=lambda t: t[0])
tight = [c for s, c in rows if s < 1e-6]
print("cuts", len(dump), "tight", len(tight), "tight with EPSM", sum(1 for c in tight if any("EPSM" in k for k in c["counts"])))
def short(fr):
    return fr.replace("EFrame", "").replace("MF", "M")[:60]
for c in [c for c in tight if any("EPSM" in k for k in c["counts"])][:int(sys.argv[3]) if len(sys.argv) > 3 else 6]:
    print("--- v2", c["v2"], "EPSM", {k: x for k, x in c["counts"].items() if "EPS" in k}, "len", len(c["windows"]))
    for win in c["windows"]:
        print("     ", " | ".join(short(t) for t in win)[:230])

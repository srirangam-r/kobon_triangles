# Make T22 arrangements clean (section 24 class): split every M5+ point and every non-bad 4-fold point into
# simple crossings (any local rearrangement is a valid arrangement); keep those that still contain a bad 4-fold point.
import sys, json, glob
sys.path.insert(0, ".")
from build_lattice import clean
sys.path.insert(0, "/home/nail/stuff/sundai_math/work/t3"); sys.path.insert(0, "/home/nail/stuff/sundai_math/work/eng/comp")
from arr import Arr
from bad_comp import tri_sectors, canon, BAD
out = []; seen = set()
for f in sorted(glob.glob("/home/nail/stuff/sundai_math/work/eng/T22/gen_*.jsonl")):
    for line in open(f):
        d = json.loads(line)
        if d.get("n", 18) != 18: continue
        g = clean(d["gens"]); a = Arr(g, 18)
        nb = sum(1 for P, ev in enumerate(a.events) if len(ev) == 4 and canon(tri_sectors(a, P)) in BAD)
        if nb == 0 or g in seen: continue
        seen.add(g); out.append({"n": 18, "gens": g, "T": a.T(), "nbad": nb, "src": f.split("/")[-1]})
with open("t22_clean.jsonl", "w") as fh:
    for o in out: fh.write(json.dumps(o) + "\n")
print("clean arrangements with a bad 4-fold point:", len(out), "T max", max(o["T"] for o in out))

"""Consistency check of the 6-X-point certificate (THEORY section 22 note): every one of the 2,841 cubes of work/eng/T28/x6_all.json has a
record in work/eng/T28/x6cert/*.jsonl with kissat exit 20 (UNSAT) and drat-trim VERIFIED; the one cube whose drat-trim run timed out
(u = 2, S = (0,17)) is covered by 17 verified sub-cubes F(0,s), s = 1..17 (work/eng/T28/x6_split28.json).  Per-u counts must equal summary.json.
This checks the stored records; re-running a cube is  x6_drat.py OUT.jsonl 0 1 LIST.json  (see certificates/verify_cheap.sh)."""
import json, glob, sys, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "work/eng/T28"
recs = collections.defaultdict(list)
for f in sorted(glob.glob(str(D / "x6cert/*.jsonl"))):
    for l in open(f):
        if l.strip():
            r = json.loads(l)
            recs[(r["u"], r["idx"], tuple(r["S"]), json.dumps(r.get("split")))].append(r)
good = lambda k: any(r["verified"] and r["kissat_rc"] == 20 for r in recs.get(k, []))
cubes = json.load(open(D / "x6_all.json"))
summ = json.load(open(D / "x6cert/summary.json"))
per_u = collections.Counter(); direct = split = 0; bad = []
for u, idx, S, *_ in cubes:
    k = (u, idx, tuple(S), "null")
    if good(k): direct += 1; per_u[u] += 1; continue
    subs = [(u, idx, tuple(S), json.dumps([["F", 0, s]])) for s in range(1, 18)]
    if (u, idx, list(S)) == (2, 8, [0, 17]) and all(good(x) for x in subs): split += 1; per_u[u] += 1
    else: bad.append((u, idx, S))
print(f"cubes in x6_all.json: {len(cubes)}; verified directly: {direct}; verified via 17 sub-cubes: {split}; not verified: {len(bad)}")
print("per-u counts:", dict(sorted(per_u.items())), "; summary.json:", summ["verified_per_u"], "total", summ["total"])
ok = not bad and len(cubes) == summ["total"] == 2841 and {int(k): v for k, v in summ["verified_per_u"].items()} == dict(per_u) and not summ["failed"]
print("x6 certificate records consistent:", ok)
sys.exit(0 if ok else 1)

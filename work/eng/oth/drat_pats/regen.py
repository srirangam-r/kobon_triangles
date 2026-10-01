# Regenerate the n=18 SAT instances behind the CEGAR frame patterns (work/eng/T27/cegar/pats.json, entries with a core)
# as DIMACS with the core elements as unit clauses; UNSAT of each file is the soundness claim of that pattern.
import sys, json
ROOT = "/home/nail/stuff/sundai_math"
sys.path.insert(0, ROOT + "/search"); sys.path.append(ROOT + "/work/t3"); sys.path.append(ROOT + "/work/eng/T27"); sys.path.insert(0, ROOT + "/work/eng/T23")
import sat_path as SP, patsat_m as P
from pysat.solvers import Solver
pats = json.load(open(ROOT + "/work/eng/T27/cegar/pats.json"))
for i, x in enumerate(pats):
    if not x.get("core"):
        print(i, "no core (hand fact)"); continue
    s = x["src"].split(": ", 1)[1]
    fr = SP.parse(s)
    pat = P.pattern_from_frames(fr, None)
    core = [tuple(e) for e in x["core"]]
    els = [e for e in pat.elements() if tuple(e) in set(core)]
    assert len(els) == len(core), (i, len(els), len(core))
    B, sel = P.build(pat, 18, els)
    cls = [list(c) for c in B.cl] + [[sel[e]] for e in els]
    nv = max(abs(l) for c in cls for l in c)
    with Solver(name="cadical153", bootstrap_with=cls) as sv:
        r = sv.solve()
    fn = f"{ROOT}/work/eng/oth/drat_pats/pat{i}.cnf"
    with open(fn, "w") as fo:
        fo.write(f"p cnf {nv} {len(cls)}\n")
        for c in cls: fo.write(" ".join(map(str, c)) + " 0\n")
    print(i, "vars", nv, "clauses", len(cls), "cadical:", "SAT" if r else "UNSAT", "->", fn, flush=True)

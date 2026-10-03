"""Re-prove the CEGAR frame patterns (work/eng/T27/cegar/pats.json entries with a core) at K lines.
For every entry: rebuild the restricted pattern exactly as cegar_m.work() did (restrict_m on the src path with the stored core), check that its
frame predicates equal the stored 'preds' (so the SAT instance proves exactly the predicate the DP uses), build the CNF on K lines with every
soft element of the restricted pattern as a unit clause, and write DIMACS.   usage: regen_k.py K [outdir]"""
import sys, json, hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3].as_posix()
sys.path.insert(0, ROOT + "/search"); sys.path.append(ROOT + "/work/t3"); sys.path.append(ROOT + "/work/eng/T27"); sys.path.insert(0, ROOT + "/work/eng/T23")
import sat_path as SP, patsat_m as P, cegar_m as CM
from pysat.solvers import Solver
K = int(sys.argv[1])
out = Path(sys.argv[2] if len(sys.argv) > 2 else Path(__file__).resolve().parent / f"cnf_K{K}")
out.mkdir(parents=True, exist_ok=True)
pats = json.load(open(ROOT + "/work/eng/T27/cegar/pats.json"))
for i, x in enumerate(pats):
    if not x.get("core"):
        print(i, "no core (hand fact)"); continue
    fr = SP.parse(x["src"].split(": ", 1)[1])
    pat = P.pattern_from_frames(fr, None)
    core = [tuple(e) for e in x["core"]]
    els = [e for e in pat.elements() if tuple(e) in set(core)]
    assert len(els) == len(core), (i, len(els), len(core))
    rp, lo, hi = CM.restrict_m(pat, els)
    preds = CM.preds_of(rp)
    assert json.loads(json.dumps(preds)) == x["preds"], (i, "preds mismatch")
    rels = rp.elements()
    nmin = 1 + sum(1 if k == "S" else 2 if k == "T" else 3 for k, h in rp.slots)
    B, sel = P.build(rp, K, rels)
    cls = [list(c) for c in B.cl] + [[sel[e]] for e in rels]
    nv = max(abs(l) for c in cls for l in c)
    with Solver(name="cadical153", bootstrap_with=cls) as sv:
        r = sv.solve()
    fn = out / f"pat{i}.cnf"
    with open(fn, "w") as fo:
        fo.write(f"p cnf {nv} {len(cls)}\n")
        for c in cls: fo.write(" ".join(map(str, c)) + " 0\n")
    h = hashlib.sha256(fn.read_bytes()).hexdigest()
    print(f"{i} slots {[k for k, _ in rp.slots]} (frames {lo}..{hi}) min lines {nmin} K {K} vars {nv} clauses {len(cls)} cadical: {'SAT' if r else 'UNSAT'} sha256 {h} {fn.name}", flush=True)

"""Local tightness query (b) for the n = 18 equality case (work/bbl/THEORY.md section 11):
   exists an arrangement (triple points, no 4-fold point) with a triple point P such that every line through P or
   1-hop related to a line through P has value v = 0 exactly (eps = 0, after T1 and F)?
UNSAT, together with strict HL(0), gives 3 Lambda - n > 0 whenever a triple point exists.
Cubes: P's label triple over T14's orbit representatives (search/unit_sat.cube_reps).

    python search/tight_run.py --n 10 [--cube i:j] [--workers 1] [--out f.jsonl]
"""
import argparse
import json
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.append(str(ROOT / "work/t3"))
import hall_model_frozen as hs  # noqa: E402
from unit_sat import cube_reps  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--cube")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--tlimit", type=float, default=3600)
    ap.add_argument("--out")
    o = ap.parse_args()
    n = o.n
    t0 = time.time()
    hm = hs.HallModel(n, Fr(0), 1)
    um, f = hm.um, hm.f
    reps = cube_reps(n)
    sel = range(len(reps))
    if o.cube:
        a, b = o.cube.split(":")
        sel = range(int(a), min(int(b), len(reps)))
    # CP model with the integer d_L variables only (no Hall layer): build_cp adds the layer, so build by hand
    cp = hs.CP(f.nv)
    for cl in f.clauses():
        cp.clause([hs.lit(x) for x in cl])
    dv = []
    for L in range(n):
        terms, c = hm.dwork(L)
        lo, hi = hm.bounds(L)
        v = cp.nint(lo, hi)
        cp.linear([x - 1 for x, _ in terms] + [v], [w for _, w in terms] + [-1], -c, -c)
        dv.append(v)
    print(f"n={n}: {f.nv} vars, built {time.time() - t0:.1f}s, {len(reps)} cubes", flush=True)
    out = open(o.out, "a") if o.out else None
    for ci in sel:
        rep = reps[ci][0]
        extra = [[um.z[rep]]]
        # every line through P, or 1-hop related to one, has d = 0 (scaled)
        t = rep
        for M in range(n):
            near = M in t or None
            if near:
                extra.append(("fix0", M, None))
            else:
                for l in t:
                    extra.append(("fix0", M, hm.rel1[l, M]))
        cm_extra, lin = [], []
        for e in extra:
            if isinstance(e, list):
                cm_extra.append(e)
            else:
                lin.append(e)
        from ortools.sat.python import cp_model
        cm = cp_model.CpModel()
        cm.proto.copy_from(cp.proto)
        for cl in cm_extra:
            cm.proto.constraints.add().bool_or.literals.extend([hs.lit(x) for x in cl])
        for (_, M, cond) in lin:
            x = cm.GetIntVarFromProtoIndex(dv[M])
            if cond is None:
                cm.Add(x == 0)
            else:
                cm.Add(x == 0).OnlyEnforceIf(cm.GetBoolVarFromProtoIndex(hs.lit(cond)))
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = o.tlimit
        solver.parameters.num_workers = o.workers
        t1 = time.time()
        st = solver.Solve(cm)
        res = {cp_model.OPTIMAL: "SAT", cp_model.FEASIBLE: "SAT", cp_model.INFEASIBLE: "UNSAT"}.get(st, "UNKNOWN")
        rec = dict(n=n, cube=ci, rep=list(rep), result=res, secs=round(time.time() - t1, 1))
        if res == "SAT":
            sol = list(solver.ResponseProto().solution)
            val = lambda v: sol[v - 1] > 0  # noqa: E731
            rec["word"] = hs.word_from_chi(um.chi_from_model(val), n)
        print(json.dumps(rec), flush=True)
        if out:
            out.write(json.dumps(rec) + "\n")
            out.flush()


if __name__ == "__main__":
    main()

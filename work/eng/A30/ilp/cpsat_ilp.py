"""A30 item 4: re-solve T25's ILP5 model with OR-tools CP-SAT (second solver).  The model rows come from T25's builder (ilp5.model);
the solver is independent of HiGHS.  Coefficients are rationalised and every row is scaled to integers exactly.
usage: cpsat_ilp.py MODE   MODE in f2shared, f2disjoint, f1, f0"""
import sys, pickle, collections, time, math
from fractions import Fraction as F
ROOT = __import__("pathlib").Path(__file__).resolve().parents[4].as_posix()
sys.path.insert(0, ROOT + "/search"); sys.path.append(ROOT + "/work/t3"); sys.path.insert(0, ROOT + "/work/eng/T25/elim")
import __main__
import rule_lp as RL
__main__.EFrame = RL.EFrame
import numpy as np
import ilp5 as I5
from ortools.sat.python import cp_model

mode = sys.argv[1]
workers = int(sys.argv[2]) if len(sys.argv) > 2 else 1
argv = {"f2shared": ["2", "--flowers", "2", "--minT4", "1"],
        "f2disjoint": ["2", "--flowers", "2", "--noT4"],
        "f1": ["2", "--flowers", "1"],
        "f0": ["2", "--flowers", "0"],
        "free": ["2"]}[mode]
a = I5.get_args(argv)
M = I5.build(a)
m = I5.model(a, M)
ROWS, var, Q = m["ROWS"], m["var"], m["Q"]
nv = len(var)
print("model:", nv, "vars,", len(ROWS), "rows, Q =", Q, flush=True)

def build_cp(extra=None):
    cp = cp_model.CpModel()
    X = [cp.NewIntVar(0, 400, f"v{i}") for i in range(nv)]
    for q in range(Q):
        cp.Add(X[var[("x", q)]] <= 18)
    for (co, lo, hi) in ROWS:
        fr = {k: F(x).limit_denominator(12) for k, x in co.items()}
        assert all(abs(float(fr[k]) - co[k]) < 1e-9 for k in co), "coefficient not rational with small denominator"
        den = 1
        for v in fr.values(): den = den * v.denominator // math.gcd(den, v.denominator)
        expr = sum(int(v * den) * X[k] for k, v in fr.items())
        lo_, hi_ = lo, hi
        if lo_ == hi_:
            cp.Add(expr == int(round(F(lo_).limit_denominator(12) * den)))
        else:
            if lo_ > -1e18: cp.Add(expr >= int(math.ceil(F(lo_).limit_denominator(12) * den)))
            if hi_ < 1e18: cp.Add(expr <= int(math.floor(F(hi_).limit_denominator(12) * den)))
    return cp, X

def solve(cp, obj=None, sense=None, tl=600):
    if obj is not None:
        (cp.Maximize if sense == "max" else cp.Minimize)(obj)
    s = cp_model.CpSolver()
    s.parameters.num_workers = workers
    s.parameters.max_time_in_seconds = tl
    st = s.Solve(cp)
    return s, st

t0 = time.time()
cp, X = build_cp()
s, st = solve(cp)
print(mode, "status", s.StatusName(st), f"{time.time()-t0:.1f}s", flush=True)
if mode in ("f1", "f2disjoint") and st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    # tag-group ranges: min and max of the total count of each line SHAPE tag group
    sigs = collections.defaultdict(list)
    for q in range(Q): sigs[I5.signature_tags(M, q)].append(q)
    print("tag groups:", len(sigs), flush=True)
    rows = []
    for sgn, qs in sorted(sigs.items(), key=lambda t: str(t[0])):
        rng = []
        for sense in ("min", "max"):
            cp2, X2 = build_cp()
            tot = sum(X2[var[("x", q)]] for q in qs)
            s2, st2 = solve(cp2, tot, sense, tl=300)
            rng.append(int(round(s2.ObjectiveValue())) if st2 == cp_model.OPTIMAL else s2.StatusName(st2))
        rows.append((sgn, len(qs), rng))
        print(f"tags={list(sgn)}: {len(qs)} types, total count range (CP-SAT) {rng}", flush=True)
    pickle.dump(rows, open(f"{ROOT}/work/eng/A30/ilp/ranges_{mode}.pkl", "wb"))

if mode in ("f1", "f2disjoint"):
    hexq = [q for sgn, qs in sigs.items() if sgn and all(t.startswith(("C0", "C2")) for t in sgn) for q in qs]
    rng = []
    for sense in ("min", "max"):
        cp2, X2 = build_cp()
        tot = sum(X2[var[("x", q)]] for q in hexq)
        s2, st2 = solve(cp2, tot, sense, tl=300)
        rng.append(int(round(s2.ObjectiveValue())))
    print("hexagon-line groups (C0/C2 tags), aggregated total count range:", rng)

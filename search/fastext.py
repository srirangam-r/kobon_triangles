"""Reduced SAT model for extending a fixed pseudoline arrangement by new lines (the free part only).

Adding lines only splits faces, so T(new) = T(base) - #(old triangles cut by a new line) + #(new triangles, each
with a side on a new line). The base signs are constants; the variables are the signs of triples that contain a
new line. Constraints:
  * one value per free triple; signotope axioms (kobon_sat.allowed4, no 4-fold point) on quadruples with a new line;
  * adjacency A(r,i,j) -> i precedes j on r with nothing strictly between (one-directional, as in build_defect);
  * a new triangle tri(t) -> not concurrent and its three pairs adjacent (the hill's triangle rule);
  * an old triangle survives -> no new line crosses any of its sides strictly between its vertices;
  * sum(survive) + sum(tri) >= target; the model's chi(0,1,2) != -1 break when (0,1,2) is free.
Same semantics as kobon_sat.build_defect restricted to the free part, without its redundant constraints.
Any SAT answer is re-counted exactly with count_general.

    python search/fastext.py selftest    # compare with recorded full-model answers (n=17 -> 18, targets 93/94)
"""
import json
import sys
import time
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
from kobon_sat import allowed4, count_general  # noqa: E402
from pysat.card import CardEnc, EncType  # noqa: E402
from pysat.formula import IDPool  # noqa: E402
from pysat.solvers import Solver  # noqa: E402

N = 18
ALLOWED = allowed4()
BAD4 = [v for v in product((-1, 0, 1), repeat=4) if v not in ALLOWED or v == (0, 0, 0, 0)]


class Ext:
    def __init__(self, chi0, n0, R, f, target, n=N, base_tris=None, card=True):
        self.n, self.R = n, tuple(R)
        self.old = [x for x in range(n) if x not in self.R]
        inv = {x: i for i, x in enumerate(self.old)}
        self.fixed = {}
        for t in combinations(self.old, 3):
            self.fixed[t] = f * chi0[tuple(inv[x] for x in t)]
        self.pool = IDPool()
        self.cls = []
        self.var = {}
        for t in combinations(range(n), 3):
            if t in self.fixed:
                continue
            vs = {v: self.pool.id(("x", t, v)) for v in (-1, 0, 1)}
            self.var[t] = vs
            self.cls += [[vs[-1], vs[0], vs[1]], [-vs[-1], -vs[0]], [-vs[-1], -vs[1]], [-vs[0], -vs[1]]]
        R_ = set(self.R)
        for q in combinations(range(n), 4):
            if not R_ & set(q):
                continue
            a, b, c, d = q
            ts = [(b, c, d), (a, c, d), (a, b, d), (a, b, c)]
            for v in BAD4:
                cl, sat = [], False
                for t, val in zip(ts, v):
                    e = self.eq(t, val)
                    if e is True:
                        continue
                    if e is False:
                        sat = True
                        break
                    cl.append(-e)
                if not sat:
                    self.cls.append(cl)
        self.A = {}
        count = []
        tris = base_tris if base_tris is not None else [tuple(sorted(t)) for t in count_general(n0, chi0)]
        for t0 in tris:  # old triangles (old labels) -> survive literals
            t = tuple(self.old[i] for i in t0)
            s = self.pool.id(("surv", t))
            a, b, c = t
            for r, i, j in ((a, b, c), (b, a, c), (c, a, b)):
                if self.before(r, i, j) is False:
                    i, j = j, i
                for L in self.R:
                    b1, b2 = self.before(r, i, L), self.before(r, L, j)
                    if b1 is False or b2 is False:
                        continue
                    self.cls.append([-s] + [-x for x in (b1, b2) if x is not True])
            count.append(s)
        for t in self.var:  # new triangles
            v = self.pool.id(("tri", t))
            self.cls.append([-v, -self.var[t][0]])
            a, b, c = t
            dead = False
            for r, i, j in ((a, b, c), (b, a, c), (c, a, b)):
                lits = [x for x in (self.adj(r, i, j), self.adj(r, j, i)) if x is not False]
                if True in lits:
                    continue
                if not lits:
                    dead = True
                    break
                self.cls.append([-v] + lits)
            if dead:
                self.cls.append([-v])
                continue
            count.append(v)
        if (0, 1, 2) in self.var:  # the model's 180-degree symmetry break chi(0,1,2) != -1
            self.cls.append([-self.var[0, 1, 2][-1]])
        elif self.fixed.get((0, 1, 2)) == -1:
            self.cls.append([])
        self.count = count
        self.target = target
        if card:
            self.cls += CardEnc.atleast(lits=count, bound=target, vpool=self.pool, encoding=EncType.seqcounter).clauses

    def eq(self, t, v):
        if t in self.fixed:
            return self.fixed[t] == v
        return self.var[t][v]

    def before(self, r, i, j):
        t = tuple(sorted((r, i, j)))
        return self.eq(t, -1 if i < j else 1)

    def adj(self, r, i, j):
        key = (r, i, j)
        if key in self.A:
            return self.A[key]
        b = self.before(r, i, j)
        if b is False:
            self.A[key] = False
            return False
        conds = []
        for w in range(self.n):
            if w in (r, i, j):
                continue
            b1, b2 = self.before(r, i, w), self.before(r, w, j)
            if b1 is False or b2 is False:
                continue
            if b1 is True and b2 is True:
                self.A[key] = False
                return False
            conds.append([-x for x in (b1, b2) if x is not True])
        a = self.pool.id(("A", key))
        if b is not True:
            self.cls.append([-a, b])
        for c in conds:
            self.cls.append([-a] + c)
        self.A[key] = a
        return a

    def solve_cpsat(self, workers=1, time_limit=None):
        """OR-tools CP-SAT on the same clauses with the count as one linear constraint (build with card=False)."""
        from ortools.sat.python import cp_model
        m = cp_model.CpModel()
        top = self.pool.top
        x = [None] + [m.NewBoolVar(f"v{i}") for i in range(1, top + 1)]
        lit = lambda l: x[l] if l > 0 else x[-l].Not()
        for c in self.cls:
            m.AddBoolOr([lit(l) for l in c])
        m.Add(sum(x[l] for l in self.count) >= self.target)
        sv = cp_model.CpSolver()
        sv.parameters.num_workers = workers
        if time_limit:
            sv.parameters.max_time_in_seconds = time_limit
        st = sv.Solve(m)
        if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            chi = dict(self.fixed)
            for t, vs in self.var.items():
                chi[t] = next(v for v, i in vs.items() if sv.Value(x[i]))
            return chi
        if st == cp_model.INFEASIBLE:
            return None
        return "UNKNOWN"

    def solve(self, solver="cadical153"):
        with Solver(name=solver, bootstrap_with=self.cls) as sv:
            if not sv.solve():
                return None
            m = set(x for x in sv.get_model() if x > 0)
        chi = dict(self.fixed)
        for t, vs in self.var.items():
            chi[t] = next(v for v, x in vs.items() if x in m)
        return chi


def selftest():
    sys.path.insert(0, str(ROOT / "work/lns/push"))
    from run_lns import chi_from_word
    import glob
    bases = {Path(f).name: chi_from_word(json.load(open(f))["gens"], 17)
             for f in glob.glob(str(ROOT / "tools/external/kobon-solutions/gallery/data/17/*.json"))}
    for target in (93, 94):
        recs = [json.loads(l) for f in glob.glob(str(ROOT / f"work/ext/n17_t{target}_s*.jsonl")) for l in open(f)]
        agree = disagree = 0
        t0 = time.time()
        for r in recs:
            chi0 = bases[r["base"]]
            e = Ext(chi0, 17, r["ranks"], r["sign"], target)
            chi = e.solve()
            got = "SAT" if chi is not None else "UNSAT"
            if chi is not None:
                T = len(count_general(N, chi))
                assert T >= target, (r["base"], r["ranks"], T)
            if got == r["res"]:
                agree += 1
            else:
                disagree += 1
                print("DISAGREE", target, r["base"], r["ranks"], r["sign"], "full:", r["res"], "fast:", got, flush=True)
        dt = time.time() - t0
        full = sum(r["secs"] for r in recs)
        print(f"target {target}: {agree} agree, {disagree} disagree over {len(recs)} calls; fast total {dt:.1f}s "
              f"vs full-model total {full:.0f}s ({full / max(dt, 1e-9):.0f}x)", flush=True)


if __name__ == "__main__":
    if sys.argv[1:] == ["selftest"]:
        selftest()

# Frozen copy of search/hall_sat.py (T15, validated 0 mismatches on 738 arrangements) taken 2026-09-29 17:00, used by
# search/hall_pure.py so that it does not depend on the running worker. Do not edit.
"""SAT / CP-SAT verifier for the two-hop Hall lemma HL(eps) (specification: search/bbl_hall.py).

Question: for given n, eps, hops, is there an arrangement of n pseudolines (triple points allowed, no 4-fold point) and a
nonempty set S of lines with d_L < 0 for all L in S and  sum_{L in S} d_L + sum_{M in N2(S), d_M > 0} d_M < 0 ?
UNSAT proves HL(eps) at that n.

The model reuses search/unit_sat.py's UnitModel (chi variables, ray statuses N/B/R, blocks, unused segments, touches)
and adds, all as full equivalences (so that with chi fixed every quantity is determined):
  * line values  s*v_L  after rule T1 (cap gap) and rule F (flank), served flags, 1-hop relation, 2-hop relation;
  * the Hall layer (CP-SAT): S, demands d_L = s*(v_L - eps [L on a triple point]), the deficit constraint.
Everything is scaled by s = lcm(2, denominator of eps).

    python search/hall_sat.py validate [--per-n K]      # fixed-chi comparison with bbl_hall.py (v, d, served, rel, HL)
    python search/hall_sat.py symtest                   # label invariance of v, d, N2 under the 4n end-circle symmetries
    python search/hall_sat.py planted                   # eps=1 violators (bad.jsonl, pilot.jsonl) + free SAT n=10 / n=11
    python search/hall_sat.py solve --n 12 --eps 1/6 [--cube i:j] [--out f.jsonl]
"""
import argparse
import json
import math
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.append(str(ROOT / "work/t3"))  # NB: work/t3/inspect.py shadows the stdlib -> never insert first
import unit_sat as us  # noqa: E402
from unit_sat import UnitModel, word_from_chi  # noqa: E402
import symmetry  # noqa: E402

BIG = 10 ** 9


# ---------------------------------------------------------------------- the model
class HallModel:
    """UnitModel (without the closed set S) + line values, relations.  self.vterms[L] = [(var, weight)] with
    s*v_L = vconst + sum weight*[var];  s*d_L = s*v_L - epsw*[zl[L]]."""

    def __init__(self, n, eps=Fr(1, 6), hops=2, noF=False, extras=()):
        self.n, self.eps, self.hops, self.noF = n, Fr(eps), hops, noF
        um = self.um = UnitModel(n, closure=False, extras=extras)
        f = self.f = um.f
        R = range(n)
        sc = self.scale = math.lcm(2, self.eps.denominator)
        HH, ONE = 3 * sc // 2, sc
        self.epsw = int(self.eps * sc)
        z, zp, zl, usg, before = um.z, um.zp, um.zl, um.usg, um.before
        vt = self.vterms = [[] for _ in R]
        # ---- portions p_L: own unused segments + touches
        for M in R:
            oth = [x for x in R if x != M]
            for i in oth:
                for j in oth:
                    if i == j:
                        continue
                    u = usg[M, i, j]
                    vt[M].append((u, ONE))
                    vt[i].append((f.AND([u, -zp[M, i]]), ONE))
                    vt[j].append((f.AND([u, -zp[M, j]]), ONE))
        # ---- ray statuses
        Nray = self.Nray = {}
        for (t, l, d) in um.rays:
            Nray[t, l, d] = f.AND([z[t], -um.Dv[t, l, d], -um.Rv[t, l, d]])
            vt[l].append((Nray[t, l, d], HH))
            vt[l].append((um.Dv[t, l, d], -HH))
        # ---- blocks (direction merged), flankers
        B3 = self.B3 = {}
        for t in um.trip:
            for l in t:
                for c in R:
                    if c not in t:
                        B3[t, l, c] = f.OR([um.blkP[t, l, 1, c], um.blkP[t, l, -1, c]])
        Ncq = {}
        for c in R:
            for a in R:
                if a == c:
                    continue
                for d in (1, -1):
                    Ncq[c, a, d] = f.OR([Nray[us.key3(a, c, m), c, d] for m in R if m not in (a, c)])
        Nxc = {}                    # ray on c at the triple point a^c pointing towards l^c is N
        for c in R:
            for a in R:
                for l in R:
                    if len({a, c, l}) == 3:
                        Nxc[c, a, l] = f.OR([f.AND([before(c, a, l), Ncq[c, a, 1]]),
                                             f.AND([before(c, l, a), Ncq[c, a, -1]])])
        self.served = {}
        for t in um.trip:
            for l in t:
                a, b = [x for x in t if x != l]
                for c in R:
                    if c in t:
                        continue
                    B = B3[t, l, c]
                    ga = f.AND([B, zp[b, c], Nxc[c, a, l]])
                    gb = f.AND([B, zp[a, c], Nxc[c, b, l]])
                    sv = self.served[t, l, c] = f.OR([ga, gb])
                    for g in (ga, gb):                              # T1: cap gives 3/2 to axis
                        vt[l].append((g, HH))
                        vt[c].append((g, -HH))
                    if noF:
                        continue
                    for x in (a, b):                                # F: unserved block takes 1 from each N flank ray
                        for (bef, d) in ((before(x, l, c), 1), (before(x, c, l), -1)):
                            u = f.AND([B, -sv, bef, Nray[t, x, d]])
                            vt[l].append((u, ONE))
                            vt[x].append((u, -ONE))
        self.vconst = -ONE
        # ---- number of triple points on line 0 (for cubes): cnt_up[k] <- (count >= k+1), cnt_dn[k] -> (count >= k+1)
        zs0 = [z[t] for t in um.by_l[0]]
        self.cnt_up = us._tot(f, zs0, 5, True)
        self.cnt_dn = us._tot(f, zs0, 5, False)
        # ---- relations
        blockAt = {}
        for t in um.trip:
            for c in R:
                if c not in t:
                    blockAt[t, c] = f.OR([B3[t, l, c] for l in t])
        rc = {}
        for L in R:
            for M in R:
                if L != M:
                    rc[L, M] = f.AND([-zl[M], f.OR([blockAt[t, M] for t in um.by_l[L] if M not in t])])
        r1 = self.rel1 = {}
        for L in R:
            for M in R:
                if L < M:
                    r1[L, M] = r1[M, L] = f.OR([zp[L, M], um.Bk[L, M, 1], um.Bk[L, M, -1], um.Bk[M, L, 1],
                                                um.Bk[M, L, -1], rc[L, M], rc[M, L]])
        if hops == 1:
            self.rel2 = r1
        else:
            r2 = self.rel2 = {}
            for L in R:
                for M in R:
                    if L < M:
                        r2[L, M] = r2[M, L] = f.OR([r1[L, M]] + [f.AND([r1[L, K], r1[K, M]]) for K in R
                                                                 if K not in (L, M)])

    # ---- values from a model / bounds
    def dwork(self, L):
        """(terms, const) of s*d_L"""
        return self.vterms[L] + [(self.um.zl[L], -self.epsw)], self.vconst

    def bounds(self, L):
        terms, c = self.dwork(L)
        return c + sum(w for _, w in terms if w < 0), c + sum(w for _, w in terms if w > 0)

    def evald(self, val, L):
        terms, c = self.dwork(L)
        return c + sum(w for v, w in terms if val(v))

    def evalv(self, val, L):
        return self.vconst + sum(w for v, w in self.vterms[L] if val(v))


# ---------------------------------------------------------------------- CP-SAT wrapper and the Hall layer
class CP:
    def __init__(self, nbool):
        from ortools.sat.python import cp_model
        self.cm = cp_model.CpModel()
        self.proto = self.cm.proto
        for _ in range(nbool):
            self.proto.variables.add().domain.extend([0, 1])

    def nint(self, lo, hi):
        v = self.proto.variables.add()
        v.domain.extend([lo, hi])
        return len(self.proto.variables) - 1

    def nbool(self):
        return self.nint(0, 1)

    def clause(self, lits):
        self.proto.constraints.add().bool_or.literals.extend(lits)

    def linear(self, vs, cs, lo, hi, enforce=()):
        c = self.proto.constraints.add()
        c.linear.vars.extend(vs)
        c.linear.coeffs.extend(cs)
        c.linear.domain.extend([lo, hi])
        if enforce:
            c.enforcement_literal.extend(enforce)


def add_layer(cp, n, dv, dlo, dhi, rel2, inS):
    """Hall layer.  dv[L]: int var index of d_L (domain [dlo,dhi]); inS[L]: proto literal (index of a bool var);
    rel2[(L, M)]: proto literal or True/False (M in N2(L)).  Constraint: d<0 on S, sum_S d + sum_{N2(S), d>0} d <= -1
    (S nonempty: the caller).  The relaxations sd >= d*[in S], w >= d*[nb] are exact at the optimum, so the model is
    satisfiable iff a violation exists."""
    R = range(n)
    sd, w, nb = [], [], []
    for L in R:
        cp.linear([dv[L]], [1], -BIG, -1, enforce=[inS[L]])
        s_ = cp.nint(min(0, dlo[L]), 0)
        cp.linear([s_, dv[L]], [1, -1], 0, BIG, enforce=[inS[L]])
        cp.linear([s_], [1], 0, 0, enforce=[~inS[L]])
        w_ = cp.nint(0, max(0, dhi[L]))
        nbL = cp.nbool()
        if dhi[L] > 0:
            cp.linear([w_, dv[L]], [1, -1], 0, BIG, enforce=[nbL])
        sd.append(s_)
        w.append(w_)
        nb.append(nbL)
    for L in R:
        for M in R:
            if L == M or rel2[L, M] is False or dhi[M] <= 0:
                continue
            cl = [~inS[L], nb[M]]
            if rel2[L, M] is not True:
                cl.append(~rel2[L, M])
            cp.clause(cl)
    cp.linear(sd + w, [1] * (2 * n), -BIG, -1)


def lit(l):
    return l - 1 if l > 0 else l


def sum_tree(cp, terms, const, fanout):
    """IntVar equal to const + sum w*x, built as a tree of small linear constraints (cheaper propagation/explanations
    than one huge constraint); returns (var index, lo, hi)"""
    items = []                                    # (var, weight, lo, hi) with lo/hi the range of weight*var
    for x, w in terms:
        items.append((x, w, min(0, w), max(0, w)))
    while True:
        nxt = []
        for i in range(0, len(items), fanout):
            ch = items[i:i + fanout]
            lo = sum(a for _, _, a, _ in ch)
            hi = sum(b for _, _, _, b in ch)
            if len(items) <= fanout:
                lo, hi = lo + const, hi + const
            v = cp.nint(lo, hi)
            cp.linear([x for x, _, _, _ in ch] + [v], [w for _, w, _, _ in ch] + [-1],
                      -(const if len(items) <= fanout else 0), -(const if len(items) <= fanout else 0))
            nxt.append((v, 1, lo, hi))
        if len(nxt) == 1:
            return nxt[0][0], nxt[0][2], nxt[0][3]
        items = nxt


def build_cp(hm, fix_line0=True, tree=0, tmin=0):
    """CP-SAT model of the whole problem (proto), returns (cp, inS, dv)"""
    f, n = hm.f, hm.n
    cp = CP(f.nv)
    for cl in f.clauses():
        cp.clause([lit(x) for x in cl])
    dv, dlo, dhi = [], [], []
    for L in range(n):
        terms, c = hm.dwork(L)
        if tree:
            v, lo, hi = sum_tree(cp, [(x - 1, w) for x, w in terms], c, tree)
        else:
            lo, hi = hm.bounds(L)
            v = cp.nint(lo, hi)
            cp.linear([x - 1 for x, _ in terms] + [v], [w for _, w in terms] + [-1], -c, -c)
        dv.append(v)
        dlo.append(lo)
        dhi.append(hi)
    inS = [cp.nbool() for _ in range(n)]
    rel2 = {(L, M): lit(hm.rel2[L, M]) for L in range(n) for M in range(n) if L != M}
    add_layer(cp, n, dv, dlo, dhi, rel2, inS)
    cp.clause(inS)
    if fix_line0:
        cp.clause([inS[0]])
    if tmin:                                     # test guidance only (NOT used in production): at least tmin triangles
        tv = [x - 1 for x in hm.um.tri.values()]
        cp.linear(tv, [1] * len(tv), tmin, BIG)
    return cp, inS, dv


def sign_prefix(hm, k=4):
    """lex-leader for the half-turn (chi -> -chi, all labels and derived quantities kept): among the first k triples the
    first nonzero chi is positive."""
    um = hm.um
    ts = um.trip[:k]
    return [[-um.ng[t]] + [um.pz[u] for u in ts[:i]] for i, t in enumerate(ts)]


def solve_cp(proto, extra_clauses=(), tlimit=3600, workers=1, seed=0, log=False, params=None):
    from ortools.sat.python import cp_model
    cm = cp_model.CpModel()
    cm.proto.copy_from(proto)
    for cl in extra_clauses:
        cm.proto.constraints.add().bool_or.literals.extend([lit(x) for x in cl])
    solver = cp_model.CpSolver()
    p = solver.parameters
    p.max_time_in_seconds = tlimit
    p.num_workers = workers
    p.random_seed = seed
    p.log_search_progress = log
    for k, v in (params or {}).items():
        setattr(p, k, v)
    st = solver.Solve(cm)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        sol = list(solver.ResponseProto().solution)
        return "SAT", (lambda v: sol[v - 1] > 0), sol, solver.WallTime()
    if st == cp_model.INFEASIBLE:
        return "UNSAT", None, None, solver.WallTime()
    return "UNKNOWN", None, None, solver.WallTime()


# ---------------------------------------------------------------------- reference side
_R = {}


def ref_imports():
    if _R:
        return _R
    import bbl_hall
    from arr import Arr
    from bbl_rules import Charge
    from cluster import records
    from dpwalk2 import chi_from_word
    _R.update(bbl_hall=bbl_hall, Arr=Arr, Charge=Charge, records=records, chi_from_word=chi_from_word)
    return _R


class Ref:
    """reference quantities of a wiring word (all exact rationals)"""

    def __init__(self, word, n, eps, noF=False):
        r = ref_imports()
        self.word, self.n = word, n
        self.a = r["Arr"](word, n)
        self.ch = r["Charge"](self.a)                      # ValueError on 4-fold points
        bh = r["bbl_hall"]
        self.val, self.served = bh.values(self.ch, noF)
        self.rel1 = bh.relation(self.ch, 1)
        self.rel2 = bh.relation(self.ch, 2)
        self.eps = eps
        self.d = {L: self.val[L] - (eps if self.ch.onl[L] else 0) for L in self.val}
        self.tn = lambda e: tuple(sorted(self.a.events[e]))

    def deficit(self, hops=2):
        return ref_imports()["bbl_hall"].hall_deficit(self.ch, self.eps, hops)[0]

    def f_of(self, S, hops=2):
        """sum_S d + sum_{N2(S), d>0} d   (S a set of lines)"""
        rel = self.rel2 if hops == 2 else self.rel1
        nb = set().union(*(rel[L] for L in S)) if S else set()
        return sum(self.d[L] for L in S) + sum(self.d[M] for M in nb if self.d[M] > 0)


def gather(per_n):
    """arrangements for validation: list of (source, n, word)"""
    us._ref_imports()
    out = us.gather(per_n)
    recs = ref_imports()["records"]
    for name in ("work/bbl/lineadv/pilot.jsonl", "work/bbl/adv/bad.jsonl"):
        seen = set()
        for r in recs(str(ROOT / name)):
            g = r["gens"] if isinstance(r["gens"], str) else " ".join(r["gens"])
            if g not in seen:
                seen.add(g)
                out.append((Path(name).stem + "!", r.get("n"), g))
    return out


# ---------------------------------------------------------------------- fixed-chi validation
class Checker:
    """fixed-chi comparison of every derived quantity with the reference (pysat, incremental)"""

    def __init__(self, n, eps, noF=False):
        from pysat.solvers import Solver
        self.n, self.eps = n, Fr(eps)
        self.hm = HallModel(n, eps, noF=noF)
        self.solver = Solver(name="cadical195", bootstrap_with=list(self.hm.f.clauses()))

    def model(self, chi):
        ass = self.hm.um.chi_lits(chi)
        if not self.solver.solve(assumptions=ass):
            return None
        mod = self.solver.get_model()
        return lambda v: mod[v - 1] > 0

    def compare(self, ref, chi):
        hm, n, sc = self.hm, self.n, self.hm.scale
        val = self.model(chi)
        if val is None:
            return ["UNSAT for real chi"]
        bad = []
        for L in range(n):
            v = hm.evalv(val, L)
            if Fr(v, sc) != ref.val[L]:
                bad.append(f"v[{L}] {Fr(v, sc)} vs {ref.val[L]}")
            d = hm.evald(val, L)
            if Fr(d, sc) != ref.d[L]:
                bad.append(f"d[{L}] {Fr(d, sc)} vs {ref.d[L]}")
        for (P, i, l, dd, X, C), s in ref.served.items():
            t = ref.tn(P)
            if val(hm.served[t, l, C]) != s:
                bad.append(f"served {t} {l} {C}: {val(hm.served[t, l, C])} vs {s}")
        nb = sum(1 for k, v in hm.B3.items() if val(v))
        if nb != len(ref.ch.blk):
            bad.append(f"#blocks {nb} vs {len(ref.ch.blk)}")
        for L in range(n):
            for M in range(n):
                if L != M:
                    if val(hm.rel1[L, M]) != (M in ref.rel1[L]):
                        bad.append(f"rel1 {L} {M}")
                    if val(hm.rel2[L, M]) != (M in ref.rel2[L]):
                        bad.append(f"rel2 {L} {M}")
        return bad


def layer_verdict(n, ref, hops=2):
    """Hall layer alone with the *reference* d and relation as constants: SAT iff some S violates HL"""
    cp = CP(0)
    sc = math.lcm(2, ref.eps.denominator)
    dvals = [int(ref.d[L] * sc) for L in range(n)]
    assert all(Fr(dvals[L], sc) == ref.d[L] for L in range(n))
    dv = [cp.nint(x, x) for x in dvals]
    inS = [cp.nbool() for _ in range(n)]
    rel = ref.rel2 if hops == 2 else ref.rel1
    rel2 = {(L, M): (M in rel[L]) for L in range(n) for M in range(n) if L != M}
    add_layer(cp, n, dv, dvals, dvals, rel2, inS)
    cp.clause(inS)
    res, val, sol, _ = solve_cp(cp.proto, workers=1)
    S = [L for L in range(n) if sol[inS[L]]] if sol else None
    return res, S


def run_validate(args):
    import collections
    arrs = gather(args.per_n)
    print(f"{len(arrs)} candidate arrangements", flush=True)
    byn = collections.defaultdict(list)
    for src, n, w in arrs:
        byn[n if n else ref_imports()["Arr"](w).n].append((src, w))
    tot = mism = nviol = 0
    per_src = collections.Counter()
    ntrip = nblk = 0
    viol_src = collections.Counter()
    for n in sorted(byn):
        if args.n and n != args.n:
            continue
        t0 = time.time()
        epss = (Fr(1, 6), Fr(1))
        chk = {e: Checker(n, e) for e in epss}
        chi_from_word = ref_imports()["chi_from_word"]
        print(f"n={n}: model {chk[epss[0]].hm.f.nv} vars {chk[epss[0]].hm.f.ncl} clauses, built {time.time() - t0:.1f}s",
              flush=True)
        seen = set()
        for src, w in byn[n]:
            if (src, w) in seen:
                continue
            seen.add((src, w))
            errs = []
            skipped = False
            for eps, ck in chk.items():
                try:
                    ref = Ref(w, n, eps)
                except ValueError:
                    skipped = True
                    break
                chi = chi_from_word(w, n)
                errs += [f"eps={eps}: {e}" for e in ck.compare(ref, chi)[:3]]
                dfc = ref.deficit()
                res, S = layer_verdict(n, ref)
                if (res == "SAT") != (dfc > 0):
                    errs.append(f"eps={eps}: layer {res} vs deficit {dfc}")
                if res == "SAT":
                    nviol += 1
                    viol_src[(src, str(eps))] += 1
                    if ref.f_of(set(S)) >= 0 or any(ref.d[L] >= 0 for L in S):
                        errs.append(f"eps={eps}: layer witness S={S} not violating in reference")
            if skipped:
                continue
            tot += 1
            per_src[src] += 1
            ntrip += len(ref.a.triples)
            nblk += len(ref.ch.blk)
            if errs:
                mism += 1
                print(f"MISMATCH {src} n={n}: {errs[:4]}\n   {w[:120]}", flush=True)
        print(f"n={n} done {time.time() - t0:.0f}s; cumulative arrangements {tot}, triple points {ntrip}, blocks {nblk}, "
              f"(arr, eps) violations {nviol}, mismatching arrangements {mism}", flush=True)
    print(f"VALIDATE: {tot} arrangements ({dict(per_src)}), {ntrip} triple points, {nblk} blocks, "
          f"{nviol} (arrangement, eps) HL violations {dict(viol_src)}, {mism} mismatching arrangements")


def run_mutant(args):
    """sensitivity of the fixed-chi comparison: the model without rule F must (i) agree with the reference values(noF=True)
    and (ii) DISAGREE with the reference that has rule F on the arrangements where F fires"""
    import collections
    chi_from_word = ref_imports()["chi_from_word"]
    us._ref_imports()
    arrs = [a for a in gather(args.per_n) if a[1] and a[1] <= args.maxn]
    byn = collections.defaultdict(list)
    for src, n, w in arrs:
        byn[n].append(w)
    agree = disagree = tot = 0
    for n in sorted(byn):
        ck = Checker(n, Fr(1, 6), noF=True)
        for w in byn[n]:
            try:
                r_nof, r_f = Ref(w, n, Fr(1, 6), noF=True), Ref(w, n, Fr(1, 6))
            except ValueError:
                continue
            chi = chi_from_word(w, n)
            tot += 1
            agree += not ck.compare(r_nof, chi)
            disagree += bool(ck.compare(r_f, chi))
        print(f"n={n}: {tot} arrangements, model(noF)==ref(noF): {agree}, model(noF)!=ref(F): {disagree}", flush=True)
    print(f"MUTANT: model(noF) agrees with ref(noF) on {agree}/{tot}; differs from ref(F) on {disagree}/{tot} "
          f"(arrangements where rule F fires)")


# ---------------------------------------------------------------------- symmetry test
def run_symtest(args):
    import random
    rng = random.Random(7)
    arrs = [a for a in gather(args.per_n) if a[1] and a[1] <= args.maxn]
    rng.shuffle(arrs)
    done = bad = 0
    chi_from_word = ref_imports()["chi_from_word"]
    for src, n, w in arrs:
        for eps in (Fr(1, 6), Fr(1)):
            try:
                ref = Ref(w, n, eps)
            except ValueError:
                break
            chi = chi_from_word(w, n)
            acts = list(symmetry.actions(n))
            for g in rng.sample(acts, 4):
                chi2 = g.apply(chi, n)
                w2 = word_from_chi(chi2, n)
                if w2 is None:
                    print("no word for transformed chi", src, n)
                    continue
                r2 = Ref(w2, n, eps)
                perm = g.permutation(n)             # new label -> old label
                ok = all(r2.val[i] == ref.val[perm[i]] and r2.d[i] == ref.d[perm[i]] for i in range(n))
                ok = ok and all({perm[j] for j in r2.rel2[i]} == ref.rel2[perm[i]] and
                                {perm[j] for j in r2.rel1[i]} == ref.rel1[perm[i]] for i in range(n))
                ok = ok and (r2.deficit() > 0) == (ref.deficit() > 0) and r2.a.T() == ref.a.T()
                done += 1
                if not ok:
                    bad += 1
                    print("SYMMETRY MISMATCH", src, n, g, w[:80])
        if done >= args.count:
            break
    print(f"SYMTEST: {done} transformed arrangements, {bad} mismatches")


# ---------------------------------------------------------------------- witnesses / planted / solve
def witness_info(hm, val, n, eps):
    """chi, word and reference re-check of a model"""
    from kobon_sat import count_general
    chi = hm.um.chi_from_model(val)
    word = word_from_chi(chi, n)
    info = dict(n=n, word=word, T=len(count_general(n, chi)), eps=str(eps))
    if word is None:
        info["ref"] = "no wiring word"
        return info
    try:
        ref = Ref(word, n, Fr(eps))
    except ValueError as e:
        info["ref"] = f"reference error {e}"
        return info
    info["ref_deficit"] = str(ref.deficit())
    info["ref_violated"] = bool(ref.deficit() > 0)
    info["model_d"] = [hm.evald(val, L) for L in range(n)]
    info["ref_d"] = [str(ref.d[L] * hm.scale) for L in range(n)]
    return info


def run_planted(args):
    """(a) fixed chi: every arrangement of bad.jsonl / pilot.jsonl (eps=1, expected UNSAT: the current bbl_hall.py finds no
    violation there) and a sample of arrangements that DO violate HL (gallery / walks / bridge93 / cal16 at eps=1, odd n at
    eps=1/6): the model must be SAT with a violating S re-checked in Python, and UNSAT on the non-violators;
    (b) free chi (guided by a triangle-count lower bound): eps=1 at n=10 and eps=0 at n=11 must find a violation."""
    import collections
    r = ref_imports()
    cases = []                                   # (label, n, eps, word)
    for name in ("work/bbl/adv/bad.jsonl", "work/bbl/lineadv/pilot.jsonl"):
        seen = set()
        for x in r["records"](str(ROOT / name)):
            g = x["gens"] if isinstance(x["gens"], str) else " ".join(x["gens"])
            if g not in seen:
                seen.add(g)
                cases.append((Path(name).stem, x.get("n"), Fr(1), g))
    us._ref_imports()
    quota = collections.Counter()
    for src, n, w in gather(30):
        if not n or n > args.maxn or src.endswith("!") or src == "bad":
            continue
        for eps in (Fr(1), Fr(1, 6)):
            key = (n, str(eps))
            try:
                ref = Ref(w, n, eps)
            except ValueError:
                continue
            viol = ref.deficit() > 0
            kk = (key, viol)
            if quota[kk] < args.per:
                quota[kk] += 1
                cases.append((src + ("+" if viol else "-"), n, eps, w))
    byk = {}
    for lab, n, eps, w in cases:
        byk.setdefault((n, eps), []).append((lab, w))
    ok = tot = nviol = 0
    out = open(args.out, "a") if args.out else None
    for (n, eps), lst in sorted(byk.items()):
        hm = HallModel(n, eps)
        cp, inS, dv = build_cp(hm, fix_line0=False)
        print(f"n={n} eps={eps}: {len(lst)} arrangements, model {hm.f.nv} vars", flush=True)
        for lab, w in lst:
            try:
                ref = Ref(w, n, eps)
            except ValueError:
                continue
            chi = r["chi_from_word"](w, n)
            expect = ref.deficit() > 0
            res, val, sol, secs = solve_cp(cp.proto, [[x] for x in hm.um.chi_lits(chi)], tlimit=900)
            tot += 1
            nviol += expect
            good = (res == "SAT") == expect
            S = None
            if res == "SAT":
                S = sorted(L for L in range(n) if sol[inS[L]])
                good = good and ref.f_of(set(S)) < 0 and all(ref.d[L] < 0 for L in S)
            ok += good
            print(f"  {lab} n={n} eps={eps} T={ref.a.T()}: model {res} ({secs:.1f}s) S={S} expected "
                  f"{'SAT' if expect else 'UNSAT'} -> {'ok' if good else 'MISMATCH'}", flush=True)
            if out:
                out.write(json.dumps(dict(kind="planted", label=lab, n=n, eps=str(eps), word=w, result=res, S=S,
                                          expected=expect, ok=bool(good), secs=round(secs, 1))) + "\n")
                out.flush()
    print(f"PLANTED (fixed chi): {ok}/{tot} as expected ({nviol} violators)", flush=True)
    for n, e, tmin in ((10, Fr(1), args.t10), (11, Fr(0), args.t11)):
        hm = HallModel(n, e)
        cp, inS, dv = build_cp(hm, tmin=tmin)
        res, val, sol, secs = solve_cp(cp.proto, sign_prefix(hm), tlimit=args.tlimit, workers=args.workers)
        print(f"FREE n={n} eps={e} (T>={tmin}): {res} in {secs:.1f}s", flush=True)
        if res == "SAT":
            info = witness_info(hm, val, n, e)
            info["S"] = [L for L in range(n) if sol[inS[L]]]
            info["kind"] = f"free n={n} eps={e} T>={tmin}"
            print(json.dumps(info), flush=True)
            if out:
                out.write(json.dumps(info) + "\n")


def cube_list(hm, kind):
    """list of (name, extra clauses) covering all cases.  'tp': number of triple points on line 0 = 0, 1, 2, >=3"""
    if kind == "none":
        return [("all", [])]
    if kind == "tp":
        up, dn = hm.cnt_up, hm.cnt_dn
        return [("tp0", [[-up[0]]]), ("tp1", [[dn[0]], [-up[1]]]), ("tp2", [[dn[1]], [-up[2]]]), ("tp3+", [[dn[2]]])]
    raise SystemExit(f"unknown cube scheme {kind}")


def run_solve(args):
    n, eps = args.n, Fr(args.eps)
    t0 = time.time()
    hm = HallModel(n, eps, args.hops)
    cp, inS, dv = build_cp(hm, tree=args.tree)
    print(f"n={n} eps={eps} hops={args.hops}: model {hm.f.nv} bool vars {hm.f.ncl} clauses, built {time.time() - t0:.1f}s",
          flush=True)
    cubes = cube_list(hm, args.cubes)
    sel = range(len(cubes))
    if args.cube:
        a, b = args.cube.split(":")
        sel = range(int(a), min(int(b), len(cubes)))
    out = open(args.out, "a") if args.out else None
    for ci in sel:
        name, cls = cubes[ci]
        t1 = time.time()
        res, val, sol, secs = solve_cp(cp.proto, sign_prefix(hm) + cls, tlimit=args.tlimit, workers=args.workers,
                                       seed=args.seed, params={"linearization_level": args.lin})
        rec = dict(n=n, eps=str(eps), hops=args.hops, cube=ci, name=name, result=res, secs=round(time.time() - t1, 1))
        if res == "SAT":
            rec["witness"] = witness_info(hm, val, n, eps)
            rec["witness"]["S"] = [L for L in range(n) if sol[inS[L]]]
        print(json.dumps(rec), flush=True)
        if out:
            out.write(json.dumps(rec) + "\n")
            out.flush()


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate")
    v.add_argument("--per-n", type=int, default=30)
    v.add_argument("--n", type=int, default=0)
    st = sub.add_parser("symtest")
    st.add_argument("--per-n", type=int, default=12)
    st.add_argument("--count", type=int, default=200)
    st.add_argument("--maxn", type=int, default=16)
    mu = sub.add_parser("mutant")
    mu.add_argument("--per-n", type=int, default=12)
    mu.add_argument("--maxn", type=int, default=14)
    pl = sub.add_parser("planted")
    pl.add_argument("--workers", type=int, default=1)
    pl.add_argument("--maxn", type=int, default=13)
    pl.add_argument("--per", type=int, default=3, help="violators and non-violators per (n, eps)")
    pl.add_argument("--t10", type=int, default=25, help="triangle guidance for the free n=10 eps=1 test")
    pl.add_argument("--t11", type=int, default=32, help="triangle guidance for the free n=11 eps=0 test")
    pl.add_argument("--tlimit", type=float, default=1800)
    pl.add_argument("--out")
    so = sub.add_parser("solve")
    so.add_argument("--n", type=int, required=True)
    so.add_argument("--eps", default="1/6")
    so.add_argument("--hops", type=int, default=2)
    so.add_argument("--cubes", default="none")
    so.add_argument("--cube", help="i:j cube index range (default all)")
    so.add_argument("--tlimit", type=float, default=3600)
    so.add_argument("--workers", type=int, default=1)
    so.add_argument("--seed", type=int, default=0)
    so.add_argument("--tree", type=int, default=0)
    so.add_argument("--lin", type=int, default=0, help="CP-SAT linearization_level")
    so.add_argument("--out")
    args = ap.parse_args()
    {"validate": run_validate, "symtest": run_symtest, "mutant": run_mutant, "planted": run_planted, "solve": run_solve}[args.cmd](args)


if __name__ == "__main__":
    main()

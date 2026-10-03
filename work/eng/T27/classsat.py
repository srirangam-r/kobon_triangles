"""class-constrained path SAT (T27): patsat_m's chi model + the reduction-class constraints, GLOBAL on all K lines:
  * no point of multiplicity >= 5; every 4-fold point has a BAD sector word (at most two non-triangle sectors, opposite if two)
  * every consecutive (4-fold P, exactly triple Q) pair on any line has a canonical sector pattern in the 48 ALLOWED (THEORY section 25), enforced lazily:
    each violated tuple found in a model adds one sound clause (conc(P) & Q triple & adjacent & the 14 sector literals) and the solver is re-run.
Sector variables S[p,q,type] (p < q, labels = slope order): a triangular face with corner p^q; types pp (both + rays), mm, qp (q+, p-), pq (q-, p+).
Ring of a quad i<j<k<l: rays i+ j+ k+ l+ i- j- k- l-, sector m between ray m and m+1; ring of a triple a<b<c: a+ b+ c+ a- b- c-."""
import sys, json, itertools, time
ROOT = __import__("os").path.abspath(__import__("os").path.join(__import__("os").path.dirname(__file__), "../../.."))
sys.path.insert(0, ROOT + "/search"); sys.path.append(ROOT + "/work/t3"); sys.path.append(ROOT + "/work/eng/T27"); sys.path.insert(0, ROOT + "/work/eng/T23")
import patsat_m as P
from pysat.solvers import Solver
_AL = None


def allowed():
    global _AL
    if _AL is None:
        d = json.load(open(ROOT + "/work/eng/pert2/pair_PQ_all.json"))
        _AL = {tuple(x) for x in d["allowed"]}
    return _AL


def add_class(B):
    K = B.K
    R = range(K)
    z = B.z
    key3 = P.key3
    # no 5-fold
    for five in itertools.combinations(R, 5):
        B.cl.append([-z[key3(*t)] for t in itertools.combinations(five, 3)])
    S = B.S = {}
    for p, q in itertools.combinations(R, 2):
        pp, mm, qp, pq = [], [], [], []
        for c in R:
            if c in (p, q):
                continue
            t = B.tri3(p, q, c)
            pp.append(B.AND([t, B.before(p, q, c), B.before(q, p, c)]))
            mm.append(B.AND([t, B.before(p, c, q), B.before(q, c, p)]))
            qp.append(B.AND([t, B.before(q, p, c), B.before(p, c, q)]))
            pq.append(B.AND([t, B.before(q, c, p), B.before(p, q, c)]))
        S[p, q, "pp"], S[p, q, "mm"], S[p, q, "qp"], S[p, q, "pq"] = B.OR(pp), B.OR(mm), B.OR(qp), B.OR(pq)
    # bad words at every quad
    for quad in itertools.combinations(R, 4):
        ts = [-z[key3(*t)] for t in itertools.combinations(quad, 3)]
        ring = quad_ring(B, quad)
        for j in range(8):
            for k in range(j + 1, 8):
                if (k - j) != 4:
                    B.cl.append(ts + [ring[j], ring[k]])
    return B


def quad_ring(B, quad):
    i, j, k, l = quad
    S = B.S
    return [S[i, j, "pp"], S[j, k, "pp"], S[k, l, "pp"], S[i, l, "qp"], S[i, j, "mm"], S[j, k, "mm"], S[k, l, "mm"], S[i, l, "pq"]]


def triple_ring(B, tr):
    a, b, c = tr
    S = B.S
    return [S[a, b, "pp"], S[b, c, "pp"], S[a, c, "qp"], S[a, b, "mm"], S[b, c, "mm"], S[a, c, "pq"]]


def chi_of(B, Ms):
    return {t: (0 if B.z[t] in Ms else (1 if B.pz[t] in Ms else -1)) for t in B.trip}


def vertices_on(B, chi, r):
    """vertices of line r left to right: list of frozensets of the OTHER lines through the vertex"""
    import functools
    key3 = P.key3
    oth = [x for x in range(B.K) if x != r]

    def cmp(i, j):
        v = chi[key3(r, i, j)]
        if v == 0:
            return 0
        bef = (v == -1) if i < j else (v == 1)
        return -1 if bef else 1
    oth.sort(key=functools.cmp_to_key(cmp))
    out = []
    for x in oth:
        if out and cmp(next(iter(out[-1])), x) == 0:
            out[-1].add(x)
        else:
            out.append({x})
    return [frozenset(v) for v in out]


def listing(bits, rho, sense):
    n = len(bits)
    return "".join(str(int(bits[(rho + i) % n])) if sense == 1 else str(int(bits[(rho - 1 - i) % n])) for i in range(n))


def pair_violations(B, Ms, chi=None):
    """list of violated (P, Q, r) tuples of the model: dicts with the data of the clause"""
    chi = chi or chi_of(B, Ms)
    AL = allowed()
    out = []
    for r in range(B.K):
        vs = vertices_on(B, chi, r)
        for a in range(len(vs) - 1):
            for (Pv, Qv, pfirst) in ((vs[a], vs[a + 1], True), (vs[a + 1], vs[a], False)):
                if len(Pv) != 3 or len(Qv) != 2:
                    continue
                quad = tuple(sorted(Pv | {r})); tr = tuple(sorted(Qv | {r}))
                ringP = quad_ring(B, quad); ringQ = triple_ring(B, tr)
                bP = [1 if x in Ms else 0 for x in ringP]; bQ = [1 if x in Ms else 0 for x in ringQ]
                mP, mQ = quad.index(r), tr.index(r)
                rhoP = mP if pfirst else mP + 4          # ray P->Q: r+ if Q is to the right of P
                rhoQ = (mQ + 3) if pfirst else mQ        # ray Q->P
                x = (listing(bP, rhoP, 1), listing(bQ, rhoQ, 1)); y = (listing(bP, rhoP, -1), listing(bQ, rhoQ, -1))
                canon = min(x, y)
                if canon not in AL:
                    out.append(dict(r=r, quad=quad, tr=tr, P=Pv, Q=Qv, pfirst=pfirst, ringP=ringP, ringQ=ringQ, bP=bP, bQ=bQ, canon=canon))
    return out


def violation_clause(B, v):
    r, quad, tr = v["r"], v["quad"], v["tr"]
    key3 = P.key3
    cl = [-B.z[key3(*t)] for t in itertools.combinations(quad, 3)]
    others = [x for x in tr if x != r]
    cl.append(-B.z[tr]); cl.append(B.zp2[r, others[0]])
    xP = next(iter(v["P"])); yQ = next(iter(v["Q"]))
    cl.append(-(B.A[r, xP, yQ] if v["pfirst"] else B.A[r, yQ, xP]))
    for lit, b in zip(v["ringP"] + v["ringQ"], v["bP"] + v["bQ"]):
        cl.append(-lit if b else lit)
    return cl


def lazy_solve(sv, B, assumptions, deadline=None, max_iter=100000, stats=None):
    """incremental solve with the lazy pair clauses; returns (True, Ms) | (False, None) | (None, None) on timeout"""
    it = 0
    while True:
        if deadline is not None and time.time() > deadline:
            return None, None
        res = P._solve(sv, assumptions, None if deadline is None else max(1, int(deadline - time.time()))) if False else sv.solve(assumptions=assumptions)
        if not res:
            return False, None
        Ms = set(x for x in sv.get_model() if x > 0)
        vio = pair_violations(B, Ms)
        if not vio:
            return True, Ms
        for v in vio:
            c = violation_clause(B, v)
            sv.add_clause(c); B.cl.append(c)
        it += 1
        if stats is not None:
            stats["lazy_iters"] = it; stats["lazy_clauses"] = stats.get("lazy_clauses", 0) + len(vio)
        if it > max_iter:
            return None, None

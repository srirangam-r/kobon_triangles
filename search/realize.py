#!/usr/bin/env python3
"""Realize a pseudoline arrangement (chi, possibly with triple points) by integer straight lines.

    realize <chi.json> <out_solution.json>        (python search/realize.py ...)

chi.json may hold  {"n":18,"chi":{"i,j,k":v,...}} | {"chi":[[i,j,k,v],...]} | a bare {"i,j,k":v} dict |
{"gens":"1 3 5 ...","n":18} (wiring word, converted with the same convention as run_lns.chi_from_word).
The output is {"lines": [[a,b,c],...]} with a x + b y + c = 0, exactly the hill's solution.json.  Line i is
the chi index i (slopes ascending in i), and the result is verified exactly before it is written:
  * chi3_from_lines (exact Fractions) reproduces the input chi on every triple, zeros included;
  * the hill's own count_triangles (.autolab eval.py, when present) and quick_check's counter agree with
    count_general(n, chi).
The exit code is 0 only when all of these hold.

Method.  Line y = m x + q is the dual point P = (m, q); chi(i,j,k) is the orientation sign of P_i P_j P_k
(m ascending) and chi = 0 means collinear.
 1. numeric: hinge loss on every scale-free orientation, equality for concurrencies, margin pushed up, restarts.
 2. exact: the concurrencies are collinear dual triples.  A construction plan (seed points free, points built
    as joins/meets of earlier ones, points on one known line get a free parameter t) is chosen so that every
    concurrency holds *identically*; a leftover incidence is closed by solving one coordinate exactly
    (linear or a rational root of the gcd of the leftover polynomials).  The seeds are re-optimized for
    margin in that parametrization, rounded to short fractions, and the result checked exactly.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import random
import sys
import time
from fractions import Fraction
from itertools import combinations
from math import gcd
from pathlib import Path

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")  # stay within the 3-core budget
import numpy as np  # noqa: E402
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "search"))
from kobon_sat import chi3_from_lines, count_general  # noqa: E402

MAX_COEF = 10 ** 30


# ----------------------------------------------------------------------------------------------- input
def chi_from_word(gens, n):
    """Same convention as work/lns/push/run_lns.chi_from_word (copied: that module is not importable cheaply)."""
    wires = list(range(n))
    slot_of = list(range(n))
    chi = {}
    for tok in gens.split():
        g = int(tok.rstrip("*"))
        w = 3 if tok.endswith("*") else 2
        block = wires[g:g + w]
        for i, k in combinations(sorted(block), 2):
            for j in range(i + 1, k):
                chi[i, j, k] = 0 if j in block else (1 if g > slot_of[j] else -1)
        block.reverse()
        wires[g:g + w] = block
        for s in range(g, g + w):
            slot_of[wires[s]] = s
    return chi


def parse_chi(obj, n=None):
    if isinstance(obj, dict) and "gens" in obj:
        n = obj.get("n") or n
        if n is None:
            n = max(int(t.rstrip("*")) + (3 if t.endswith("*") else 2) for t in obj["gens"].split())
        return n, chi_from_word(obj["gens"], n)
    raw = obj["chi"] if isinstance(obj, dict) and "chi" in obj else obj
    chi = {}
    if isinstance(raw, dict):
        for key, v in raw.items():
            t = tuple(int(x) for x in key.replace("(", "").replace(")", "").split(","))
            chi[tuple(sorted(t))] = int(v)
    else:
        for i, j, k, v in raw:
            chi[tuple(sorted((i, j, k)))] = int(v)
    if isinstance(obj, dict) and obj.get("n"):
        n = obj["n"]
    n = n or 1 + max(max(t) for t in chi)
    if len(chi) != n * (n - 1) * (n - 2) // 6 or any(v not in (-1, 0, 1) for v in chi.values()):
        raise ValueError("chi must give a value in {-1,0,1} for every triple i<j<k")
    return n, chi


# ---------------------------------------------------------------------------------------------- clusters
def concurrency_clusters(n, chi):
    """Maximal sets of >=3 concurrent lines; raises if the zero pattern is not a partial linear space."""
    pair_pts = {}
    for (i, j, k), v in chi.items():
        if v == 0:
            for a, b in ((i, j), (i, k), (j, k)):
                pair_pts.setdefault((a, b), set()).update((i, j, k))
    clusters = {frozenset(s) for s in pair_pts.values()}
    for c in clusters:
        for t in combinations(sorted(c), 3):
            if chi[t] != 0:
                raise ValueError(f"inconsistent concurrency: {sorted(c)} but chi{t}!=0")
    for c1, c2 in combinations(clusters, 2):
        if len(c1 & c2) >= 2:
            raise ValueError(f"two concurrency points share two lines: {sorted(c1)} {sorted(c2)}")
    return sorted(clusters, key=lambda c: sorted(c))


# ------------------------------------------------------------------------------------ numeric machinery
class Triples:
    def __init__(self, n, chi):
        keys = sorted(chi)
        self.n = n
        self.I = np.array([k[0] for k in keys])
        self.J = np.array([k[1] for k in keys])
        self.K = np.array([k[2] for k in keys])
        self.s = np.array([chi[k] for k in keys], dtype=float)
        self.zero = self.s == 0
        self.keys = keys

    def scaled_det(self, m, q):
        """D_ijk / (longest side)^2 : scale-free orientation in [-1/2, 1/2]."""
        dx1, dy1 = m[self.J] - m[self.I], q[self.J] - q[self.I]
        dx2, dy2 = m[self.K] - m[self.I], q[self.K] - q[self.I]
        det = dx1 * dy2 - dx2 * dy1
        l2 = np.maximum.reduce([dx1 ** 2 + dy1 ** 2, dx2 ** 2 + dy2 ** 2,
                                (dx2 - dx1) ** 2 + (dy2 - dy1) ** 2])
        return det / np.maximum(l2, 1e-300)


def _det_grad(T, m, q):
    """d = det/l2 and its gradient wrt [m_i,m_j,m_k,q_i,q_j,q_k] for every triple."""
    mi, mj, mk, qi, qj, qk = m[T.I], m[T.J], m[T.K], q[T.I], q[T.J], q[T.K]
    det = (mj - mi) * (qk - qi) - (mk - mi) * (qj - qi)
    dgd = np.stack([qj - qk, qk - qi, -(qj - qi), mk - mj, -(mk - mi), mj - mi], axis=1)
    a = (mj - mi) ** 2 + (qj - qi) ** 2
    b = (mk - mi) ** 2 + (qk - qi) ** 2
    c = (mk - mj) ** 2 + (qk - qj) ** 2
    which = np.argmax(np.stack([a, b, c]), axis=0)
    l2 = np.maximum(np.maximum(a, b), c)
    l2 = np.maximum(l2, 1e-300)
    gl = np.zeros_like(dgd)
    for w, (p1, p2) in enumerate(((0, 1), (0, 2), (1, 2))):  # pairs (i,j) (i,k) (j,k)
        sel = which == w
        pm = np.stack([mi, mj, mk], axis=1)
        pq = np.stack([qi, qj, qk], axis=1)
        dm = (pm[:, p2] - pm[:, p1])[sel]
        dq = (pq[:, p2] - pq[:, p1])[sel]
        gl[sel, p1] = -2 * dm
        gl[sel, p2] = 2 * dm
        gl[sel, 3 + p1] = -2 * dq
        gl[sel, 3 + p2] = 2 * dq
    d = det / l2
    grad = dgd / l2[:, None] - (det / l2 ** 2)[:, None] * gl
    return d, grad


def normalize(m, q):
    """Gauge: allowed affine maps (m,q)->(a m+b, c q+d m+e), a,c>0 keep every chi.  Whiten within them."""
    m = (m - m.mean()) / (m.std() + 1e-300)
    A = np.vstack([m, np.ones_like(m)]).T
    coef, *_ = np.linalg.lstsq(A, q, rcond=None)
    q = q - A @ coef
    q = q / (q.std() + 1e-300)
    return m, q


def _residual_jac(T, mu, w_eq, gap):
    n = T.n

    def jac(z):
        m, q = z[:n], z[n:]
        d, g = _det_grad(T, m, q)
        coef = np.where(T.zero, w_eq, np.where(mu - T.s * d > 0, -T.s, 0.0))
        rows = np.arange(len(T.keys))
        J = np.zeros((len(T.keys) + n - 1, 2 * n))
        cols = np.stack([T.I, T.J, T.K, n + T.I, n + T.J, n + T.K], axis=1)
        for c in range(6):
            J[rows, cols[:, c]] += coef * g[:, c]
        act = np.diff(m) < gap
        for i in np.nonzero(act)[0]:
            J[len(T.keys) + i, i] += 1.0
            J[len(T.keys) + i, i + 1] -= 1.0
        return J
    return jac


def _residual_fn(T, mu, w_eq, gap):
    n = T.n

    def f(z):
        m, q = z[:n], z[n:]
        d = T.scaled_det(m, q)
        r = np.where(T.zero, w_eq * d, np.maximum(0.0, mu - T.s * d))
        return np.concatenate([r, np.maximum(0.0, gap - np.diff(m))])
    return f


def margin_of(T, m, q):
    d = T.scaled_det(m, q)
    nz = ~T.zero
    mm = float((T.s[nz] * d[nz]).min()) if nz.any() else 1.0
    return mm, float(np.abs(d[T.zero]).max()) if T.zero.any() else 0.0, float(np.diff(m).min())


def initial_guess(n, rng, kind):
    if kind == 0:  # points near a convex parabola
        m = np.sort(rng.uniform(-1, 1, n))
        q = m ** 2 * rng.uniform(0.5, 2) + rng.normal(0, 0.15, n)
    elif kind == 1:
        m = np.sort(rng.normal(0, 1, n))
        q = rng.normal(0, 1, n)
    else:  # cubic-ish / S curve
        m = np.sort(rng.uniform(-1, 1, n))
        q = m ** 3 * 2 + rng.normal(0, 0.2, n)
    return m, q


def push_margin(x0, factory, evaluate, iters=25, nfev=120, jacf=None):
    """Raise the hinge margin mu while `evaluate(x) -> (margin, ok)` stays feasible; returns (x, margin)."""
    best_x = np.asarray(x0, dtype=float)
    best, ok = evaluate(best_x)
    if not ok:
        return best_x, best
    mu = max(best, 1e-5) * 2
    for _ in range(iters):
        res = least_squares(factory(mu), best_x, method="trf", xtol=1e-13, ftol=1e-13, gtol=1e-13, max_nfev=nfev,
                            jac=jacf(mu) if jacf else "2-point")
        mm, ok = evaluate(res.x)
        if ok and mm > best:
            best_x, best = res.x, mm
            mu = max(mu, mm) * 1.5
        else:
            mu = (mu + best) / 2
            if mu < best * 1.03:
                break
    return best_x, best


def numeric_solve(n, chi, seed=0, tries=200, time_limit=120.0, verbose=False, push=True):
    """Dual points (m, q) satisfying every chi sign with the largest margin found; None on failure."""
    T = Triples(n, chi)
    rng = np.random.default_rng(seed)
    t0 = time.time()

    def evaluate(z):
        mm, zz, gg = margin_of(T, z[:n], z[n:])
        return mm, (mm > 0 and zz < 1e-6 and gg > 0)

    for attempt in range(tries):
        if time.time() - t0 > time_limit:
            break
        m, q = initial_guess(n, rng, attempt % 3)
        z = np.concatenate([m, q])
        for mu in (1e-5, 1e-4):
            z = least_squares(_residual_fn(T, mu, 30.0, 1e-3), z, method="trf", xtol=1e-14, ftol=1e-14,
                              gtol=1e-14, max_nfev=300, jac=_residual_jac(T, mu, 30.0, 1e-3)).x
            z = np.concatenate(normalize(z[:n], z[n:]))
        mm, ok = evaluate(z)
        if verbose:
            print(f"  attempt {attempt}: margin {mm:.2e} ok={ok}", flush=True)
        if not ok:
            # equalities are only soft: one polish with a stronger weight before giving up on this start
            z = least_squares(_residual_fn(T, 1e-5, 1e3, 1e-3), z, method="trf", xtol=1e-15, ftol=1e-15,
                              gtol=1e-15, max_nfev=300, jac=_residual_jac(T, 1e-5, 1e3, 1e-3)).x
            mm, ok = evaluate(z)
            if not ok:
                continue
        if push:
            z, mm = push_margin(z, lambda mu: _residual_fn(T, mu, 1e3, 1e-3), evaluate,
                                jacf=lambda mu: _residual_jac(T, mu, 1e3, 1e-3))
        m, q = normalize(z[:n], z[n:])
        return m, q, mm, attempt
    return None


# ---------------------------------------------------------------------------------------- exact machinery
class Poly:
    """Univariate polynomial over Fractions (index = power); supports ring ops with ints/Fractions/floats-free."""
    __slots__ = ("c",)

    def __init__(self, c):
        c = [Fraction(x) for x in c]
        while len(c) > 1 and c[-1] == 0:
            c.pop()
        self.c = c or [Fraction(0)]

    @staticmethod
    def lift(x):
        return x if isinstance(x, Poly) else Poly([x])

    def __add__(self, o):
        o = Poly.lift(o)
        L = max(len(self.c), len(o.c))
        return Poly([(self.c[i] if i < len(self.c) else 0) + (o.c[i] if i < len(o.c) else 0) for i in range(L)])
    __radd__ = __add__

    def __neg__(self):
        return Poly([-x for x in self.c])

    def __sub__(self, o):
        return self + (-Poly.lift(o))

    def __rsub__(self, o):
        return Poly.lift(o) - self

    def __mul__(self, o):
        o = Poly.lift(o)
        r = [Fraction(0)] * (len(self.c) + len(o.c) - 1)
        for i, a in enumerate(self.c):
            if a:
                for j, b in enumerate(o.c):
                    r[i + j] += a * b
        return Poly(r)
    __rmul__ = __mul__

    @property
    def deg(self):
        return len(self.c) - 1

    def is_zero(self):
        return not any(self.c)

    def __call__(self, x):
        r = Fraction(0)
        for a in reversed(self.c):
            r = r * x + a
        return r

    def divmod(self, d):
        r = list(self.c)
        q = [Fraction(0)] * max(1, len(r) - len(d.c) + 1)
        while len(r) >= len(d.c) and any(r):
            k = len(r) - len(d.c)
            f = r[-1] / d.c[-1]
            q[k] = f
            for i, b in enumerate(d.c):
                r[i + k] -= f * b
            r.pop()
        return Poly(q), Poly(r or [0])


def poly_gcd(a, b):
    while not b.is_zero():
        a, b = b, a.divmod(b)[1]
    return a


def is_zero(x):
    return x.is_zero() if isinstance(x, Poly) else x == 0


def cross(u, v):
    return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])


def dot(u, v):
    return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]


class BadPlan(Exception):
    pass


def make_plan(n, clusters, rng, seed_bias=0.0):
    """Random construction order.  ops: ('seed',x) ('online',x,cluster,a,b) ('join',c,a,b) ('meet',x,c1,c2)."""
    known, unknown, lines, ops = set(), set(range(n)), {}, []
    while unknown:
        progress = True
        while progress:
            progress = False
            for ci, c in enumerate(clusters):
                kn = sorted(c & known)
                if ci not in lines and len(kn) >= 2:
                    a, b = rng.sample(kn, 2)
                    lines[ci] = (a, b)
                    ops.append(("join", ci, a, b))
                    progress = True
            for x in sorted(unknown):
                inc = [ci for ci in lines if x in clusters[ci]]
                if len(inc) >= 2:
                    c1, c2 = rng.sample(inc, 2)
                    ops.append(("meet", x, c1, c2))
                    known.add(x)
                    unknown.discard(x)
                    progress = True
        if not unknown:
            break
        onl = [x for x in sorted(unknown) if any(x in clusters[ci] for ci in lines)]
        if onl and rng.random() >= seed_bias:
            x = rng.choice(onl)
            ci = rng.choice([ci for ci in lines if x in clusters[ci]])
            ops.append(("online", x, ci) + lines[ci])
        else:
            x = rng.choice(sorted(unknown))
            ops.append(("seed", x))
        known.add(x)
        unknown.discard(x)
    return ops


def plan_params(ops):
    """Parameter slots: [(op_index, coordinate)] ; seeds give (m,q), online points one affine parameter u."""
    out = []
    for oi, op in enumerate(ops):
        if op[0] == "seed":
            out += [(oi, 0), (oi, 1)]
        elif op[0] == "online":
            out.append((oi, 0))
    return out


def _norm(p):
    """Scale a homogeneous point to W = 1 unless it carries a symbolic parameter."""
    if any(isinstance(c, Poly) for c in p):
        return p
    w = p[2]
    if w == 0 or (isinstance(w, float) and abs(w) < 1e-12):
        raise BadPlan("point at infinity")
    return (p[0] / w, p[1] / w, w / w)


def build(n, clusters, ops, values=None, target=None):
    """values: one ring element per slot (float / Fraction / Poly); or target=(m*,q*) float arrays from which the
    slot values are read off.  Returns (points, lines, used_values), points/lines homogeneous."""
    pts, lines, k, used = {}, {}, 0, []
    for op in ops:
        kind = op[0]
        if kind == "seed":
            v = [target[0][op[1]], target[1][op[1]]] if target is not None else values[k:k + 2]
            used += list(v)
            p = (v[0], v[1], 1)
            k += 2
        elif kind == "online":
            _, x, ci, a, b = op
            A, B = pts[a], pts[b]
            if target is not None:
                d = np.array([B[0] - A[0], B[1] - A[1]], dtype=float)
                u = float(np.dot([target[0][x] - A[0], target[1][x] - A[1]], d) / np.dot(d, d))
            else:
                u = values[k]
            used.append(u)
            k += 1
            p = tuple((1 - u) * B[2] * A[i] + u * A[2] * B[i] for i in range(3))
        elif kind == "join":
            _, ci, a, b = op
            lines[ci] = cross(pts[a], pts[b])
            continue
        else:
            _, x, c1, c2 = op
            p = cross(lines[c1], lines[c2])
        if kind == "seed" and not any(isinstance(c, Poly) for c in p):
            p = (p[0], p[1], type(p[0])(1))
        else:
            p = _norm(p)
        pts[op[1]] = p
    return pts, lines, used


def residual_polys(n, clusters, ops, values):
    """Non-identically-zero incidence residuals dot(line_c, P_p) with ring elements from `values`."""
    pts, lines, _ = build(n, clusters, ops, values)
    res = []
    for ci, c in enumerate(clusters):
        for p in c:
            r = dot(lines[ci], pts[p])
            if not is_zero(r):
                res.append((ci, p, r))
    return res


def rand_fracs(rng, k):
    return [Fraction(rng.randint(-40, 40), rng.randint(3, 17)) + Fraction(rng.randint(1, 97), 101) for _ in range(k)]


def analyse_plan(n, clusters, ops, rng):
    """Return None (bad) or dict(closure=None|slot index) : every incidence identically true, or true for one
    exact value of one parameter (common root of the leftover polynomials, degree exactly 1)."""
    slots = plan_params(ops)
    try:
        vals = rand_fracs(rng, len(slots))
        res = residual_polys(n, clusters, ops, vals)
    except (BadPlan, ZeroDivisionError):
        return None
    left = [(ci, p) for ci, p, _ in res]
    if not res:
        return {"closure": None, "leftovers": []}
    involved = sorted({oi for oi in range(len(ops))})
    for j in rng.sample(range(len(slots)), len(slots)):
        try:
            v2 = list(vals)
            v2[j] = Poly([0, 1])
            polys = [Poly.lift(r) for _, _, r in residual_polys(n, clusters, ops, v2)]
        except (BadPlan, ZeroDivisionError):
            continue
        polys = [p for p in polys if not p.is_zero()]
        if not polys or max(p.deg for p in polys) > 60:
            continue
        g = polys[0]
        for p in polys[1:]:
            g = poly_gcd(g, p)
        if g.deg == 1:
            return {"closure": j, "leftovers": left}
    return None


# ------------------------------------------------------------------------------- chart optimisation / exact
def _float_points(n, clusters, ops, theta):
    pts, lines, _ = build(n, clusters, ops, values=list(theta))
    m = np.array([pts[x][0] for x in range(n)], dtype=float)
    q = np.array([pts[x][1] for x in range(n)], dtype=float)
    return m, q, pts, lines


def chart_factory(n, clusters, ops, T, leftovers):
    BIG = 10.0

    def make(mu, w_eq=1e3, gap=1e-3):
        def f(theta):
            try:
                m, q, pts, lines = _float_points(n, clusters, ops, theta)
                if not (np.all(np.isfinite(m)) and np.all(np.isfinite(q))):
                    raise BadPlan("nonfinite")
            except (BadPlan, OverflowError, ZeroDivisionError):
                return np.full(len(T.keys) + n - 1 + len(leftovers), BIG)
            d = T.scaled_det(m, q)
            r = np.where(T.zero, 0.0, np.maximum(0.0, mu - T.s * d))
            ex = []
            for ci, p in leftovers:
                L = np.array(lines[ci], dtype=float)
                ex.append(w_eq * dot(L, pts[p]) / (np.linalg.norm(L[:2]) + 1e-300))
            return np.concatenate([r, np.maximum(0.0, gap - np.diff(m)), np.array(ex)])
        return f
    return make


def chart_evaluate(n, clusters, ops, T, leftovers):
    def ev(theta):
        try:
            m, q, pts, lines = _float_points(n, clusters, ops, theta)
            if not (np.all(np.isfinite(m)) and np.all(np.isfinite(q))):
                return -1.0, False
        except (BadPlan, OverflowError, ZeroDivisionError):
            return -1.0, False
        nz = ~T.zero
        d = T.scaled_det(m, q)
        mm = float((T.s[nz] * d[nz]).min())
        return mm, (mm > 0 and np.diff(m).min() > 0)
    return ev


def frac_lines(pts_exact, n):
    """Homogeneous exact dual points (m,q,1) -> primitive integer lines [a,b,c]: m x - y + q = 0."""
    out = []
    for x in range(n):
        X, Y, W = pts_exact[x]
        m, q = Fraction(X) / Fraction(W), Fraction(Y) / Fraction(W)
        L = m.denominator * q.denominator // gcd(m.denominator, q.denominator)
        a, b, c = int(m * L), -L, int(q * L)
        g = gcd(gcd(abs(a), abs(b)), abs(c))
        out.append([a // g, b // g, c // g])
    return out


def exact_check(lines, n, chi):
    """Exact chi of integer lines (index order = slope order required) versus the wanted chi."""
    order, got = chi3_from_lines(lines)
    if order is None or order != list(range(n)):
        return False, "slopes not strictly ascending in index order"
    bad = [t for t in chi if got[t] != chi[t]]
    return (not bad), (f"{len(bad)} chi values differ, first {bad[:3]}" if bad else "")


def exact_from_theta(n, clusters, ops, closure, leftovers, theta, chi, denominators, verbose=False):
    slots = len(theta)
    for D in denominators:
        vals = [Fraction(float(x)).limit_denominator(D) for x in theta]
        try:
            if closure is not None:
                v2 = list(vals)
                v2[closure] = Poly([0, 1])
                pts_s, lines_s, _ = build(n, clusters, ops, values=v2)
                polys = [Poly.lift(dot(lines_s[ci], pts_s[p])) for ci, p in leftovers]
                polys = [p for p in polys if not p.is_zero()]
                if polys:
                    g = polys[0]
                    for p in polys[1:]:
                        g = poly_gcd(g, p)
                    if g.deg != 1:
                        continue
                    vals[closure] = -g.c[0] / g.c[1]
            pts, lines, _ = build(n, clusters, ops, values=vals)
            for ci, p in leftovers:  # closure must really have removed every leftover incidence
                if dot(lines[ci], pts[p]) != 0:
                    raise BadPlan("incidence not closed")
            il = frac_lines(pts, n)
        except (BadPlan, ZeroDivisionError):
            continue
        if any(abs(v) > MAX_COEF for l in il for v in l):
            if verbose:
                print(f"    D={D}: coefficients exceed 1e30", flush=True)
            continue
        ok, why = exact_check(il, n, chi)
        if verbose:
            print(f"    D={D}: {'OK' if ok else why}", flush=True)
        if ok:
            return il, D
    return None, None


# ------------------------------------------------------------------------------------------- verification
def _hill_eval():
    p = ROOT / ".autolab" / "hills" / "kobon-triangles" / "eval.py"
    if not p.is_file():
        return None
    spec = importlib.util.spec_from_file_location("hill_eval", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _quick_check_count(lines):
    sys.path.append(str(ROOT / "tools" / "external" / "kobon-solutions"))
    from verification.quick_check import count_triangles as qc_count, geometry_rows
    fl = [(Fraction(a, -b), Fraction(c, -b)) for a, b, c in lines]  # y = (-a/b) x + (-c/b)
    rows, par = geometry_rows(fl)
    return qc_count(rows), len(par)


def verify_all(lines, n, chi):
    """Full independent check; returns dict(ok, triangles, ...) and never trusts the construction."""
    info = {"ok": False}
    okc, why = exact_check(lines, n, chi)
    info["chi_exact"] = okc
    if not okc:
        info["error"] = why
        return info
    want = len(count_general(n, chi))
    info["triangles_chi"] = want
    hill = _hill_eval()
    if hill is not None:
        info["triangles_hill"] = len(hill.count_triangles([hill._normalize(tuple(l)) for l in lines]))
    qc, par = _quick_check_count(lines)
    info["triangles_quick_check"], info["parallel_pairs"] = qc, par
    counts = {info.get("triangles_hill", want), qc, want}
    info["ok"] = len(counts) == 1 and par == 0 and all(type(v) is int and abs(v) <= MAX_COEF for l in lines for v in l)
    if not info["ok"]:
        info["error"] = f"triangle counts disagree: {sorted(counts)}"
    return info


# ------------------------------------------------------------------------------------------------ driver
SEED_BIAS = 0.15  # chance of choosing a free seed over a parametrised point on a known line (diversifies plans)
DENOMS = [2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 100, 128, 256, 512, 1000, 2048, 5000, 10 ** 4, 3 * 10 ** 4,
          10 ** 5, 10 ** 6, 10 ** 7, 10 ** 8, 10 ** 10, 10 ** 12]


def candidate_plans(n, clusters, m, q, rng, want=6, attempts=400, verbose=False):
    """Viable construction plans whose chart contains the numeric solution (m, q)."""
    if not clusters:
        return [([("seed", x) for x in range(n)], {"closure": None, "leftovers": []})]
    seen, out = set(), []
    for _ in range(attempts):
        ops = make_plan(n, clusters, rng, seed_bias=SEED_BIAS)
        key = tuple(ops)
        if key in seen:
            continue
        seen.add(key)
        info = analyse_plan(n, clusters, ops, rng)
        if info is None:
            continue
        try:
            pts, lines, theta = build(n, clusters, ops, target=(m, q))
        except (BadPlan, ZeroDivisionError):
            continue
        dev = max(math.hypot(pts[x][0] - m[x], pts[x][1] - q[x]) for x in range(n))
        if verbose:
            print(f"  plan params={len(theta)} closure={info['closure']} left={len(info['leftovers'])} dev={dev:.1e}",
                  flush=True)
        if dev > 1e-2:
            continue
        out.append((dev + 0.01 * (info["closure"] is not None), ops, info))
        if len(out) >= want:
            break
    out.sort(key=lambda t: t[0])
    return [(ops, info) for _, ops, info in out]


def realize(n, chi, seed=0, time_limit=900.0, verbose=False):
    clusters = concurrency_clusters(n, chi)
    T = Triples(n, chi)
    rng = random.Random(seed)
    t0 = time.time()
    rnd = 0
    while time.time() - t0 < time_limit:
        rnd += 1
        num = numeric_solve(n, chi, seed=seed * 1000 + rnd, tries=60, time_limit=max(10.0, time_limit / 4),
                            verbose=verbose)
        if num is None:
            if verbose:
                print(f"round {rnd}: numeric stage found no drawing", flush=True)
            continue
        m, q, margin, att = num
        if verbose:
            print(f"round {rnd}: numeric drawing margin {margin:.2e} (start {att}), {len(clusters)} concurrency points",
                  flush=True)
        for ops, info in candidate_plans(n, clusters, m, q, rng, verbose=verbose):
            closure, left = info["closure"], info["leftovers"]
            _, _, theta = build(n, clusters, ops, target=(m, q))
            theta = np.array(theta, dtype=float)
            fac = chart_factory(n, clusters, ops, T, left)
            ev = chart_evaluate(n, clusters, ops, T, left)
            # settle onto the chart exactly (leftover incidences are soft equalities), then maximise margin
            theta = least_squares(fac(1e-5), theta, method="trf", xtol=1e-14, ftol=1e-14, gtol=1e-14,
                                  max_nfev=200).x
            theta, mm = push_margin(theta, fac, ev)
            if verbose:
                print(f"  chart margin {mm:.2e}", flush=True)
            if mm <= 0:
                continue
            lines, D = exact_from_theta(n, clusters, ops, closure, left, theta, chi, DENOMS, verbose=verbose)
            if lines is not None:
                return lines, {"round": rnd, "margin": mm, "denominator": D, "plan_params": len(theta),
                               "closure": closure, "clusters": [sorted(c) for c in clusters],
                               "seconds": round(time.time() - t0, 1)}
    return None, {"error": "no exact realization found", "seconds": round(time.time() - t0, 1)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("chi", help="chi.json (see module doc)")
    ap.add_argument("out", help="output solution.json ({\"lines\": [[a,b,c],...]})")
    ap.add_argument("--n", type=int)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--time-limit", type=float, default=900.0)
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args(argv)
    n, chi = parse_chi(json.load(open(a.chi)), a.n)
    lines, info = realize(n, chi, seed=a.seed, time_limit=a.time_limit, verbose=a.verbose)
    if lines is None:
        print("FAILED:", info, file=sys.stderr)
        return 1
    v = verify_all(lines, n, chi)
    print(json.dumps({**info, **v}))
    if not v["ok"]:
        print("VERIFICATION FAILED, not writing", file=sys.stderr)
        return 2
    Path(a.out).write_text(json.dumps({"lines": lines}) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

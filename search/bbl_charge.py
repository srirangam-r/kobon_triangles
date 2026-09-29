"""Generalized BBL charging: every line should end with charge >= 1/3, which gives Lambda >= n/3.

Exact budget:  Lambda = Z + sum_P c_P,  c_P = 3 - D_P - beta_P/2  (triple points only).
Base charges (each unused segment u gives 1/3 to its own line and 1/3 to each line touching it at a simple endpoint;
each triple point gives c_P/3 to each of its lines):
    q0(L) = Z_L/3 + kappa(L)/3 + sum_{P on L} c_P/3,      sum_L q0(L) <= Lambda.
Transfers (to find): at a triple point P of type tau, an amount w[tau, x -> y] moves from the line with role x at P to the
line with role y (a line through P, or a cap line of one of P's blocks). Point type = the six ray statuses
N (first segment not doubly used) / B (doubly used, simple far end) / R (doubly used, multiple far end = bridge), up to
the dihedral symmetries; a role is the line's position in that pattern.

    python search/bbl_charge.py stats <in>...           # deficient lines under the base charge
    python search/bbl_charge.py lp <in>... [--out rules.json]
"""
import argparse
import collections
import json
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.append(str(ROOT / "work/t3"))
from arr import Arr, rays, first_seg, far_end, touches  # noqa: E402
from cluster import records  # noqa: E402

THIRD = F(1, 3)


def dihedral(p):
    """all images of a 6-tuple under rotations and reflections, with the index map"""
    out = []
    for r in range(6):
        for s in (1, -1):
            idx = [(s * i + r) % 6 for i in range(6)]
            out.append((tuple(p[j] for j in idx), idx))
    return out


def point_type(st):
    return min(img for img, _ in dihedral(st))


def role(st, i):
    """role of the line on rays i, i+3: canonical pattern seen from that line (ray i first; flips allowed)"""
    best = None
    for start in (i, (i + 3) % 6):
        for s in (1, -1):
            img = tuple(st[(start + s * j) % 6] for j in range(6))
            best = img if best is None or img < best else best
    return best


def analyze(a, with_ids=False):
    """base charges and incidences. Returns (q0 list, incidences list per line, Lambda)."""
    n = a.n
    trip = set(a.triples)
    if any(len(e) > 3 for e in a.events):
        raise ValueError("4-fold point")
    info = {}
    Dp = collections.Counter()
    bp = collections.Counter()
    for P in a.triples:
        rs = rays(a, P)
        st, capl = [], []
        for r in rs:
            fs = first_seg(a, P, r)
            if fs is None or len(a.t[fs[0]][fs[1]]) != 2:
                st.append("N")
                capl.append(None)
                continue
            X = far_end(a, P, r)
            if X in trip:
                st.append("R")
                capl.append(None)
                bp[P] += 1
            else:
                st.append("B")
                capl.append(a.other(X, r[0]))
                Dp[P] += 1
        info[P] = (rs, st, capl)
    c = {P: 3 - Dp[P] - F(bp[P], 2) for P in a.triples}
    kap = collections.Counter(t[2] for t in touches(a))
    q0 = []
    inc = [[] for _ in range(n)]
    for L in range(n):
        ZL = sum(1 for s in a.t[L] if not s)
        q = F(ZL, 3) + F(kap[L], 3) + sum((c[P] for P in a.rows[L] if P in c), F(0)) / 3
        q0.append(q)
    for P, (rs, st, capl) in info.items():
        tau = point_type(st)
        for i in range(3):
            L = rs[i][0]
            inc[L].append((tau, ("line",) + role(st, i)) + ((P,) if with_ids else ()))
        for i in range(6):
            if st[i] == "B":
                # cap role: pattern read from the block's centre ray (reflections allowed)
                img = min(tuple(st[(i + s * j) % 6] for j in range(6)) for s in (1, -1))
                inc[capl[i]].append((tau, ("cap",) + img) + ((P,) if with_ids else ()))
    lam = n * (n - 2) - 3 * a.T()
    assert sum(q0) <= lam, (sum(q0), lam)
    return q0, inc, lam


def load(inputs, limit=10 ** 9):
    sigs = collections.Counter()
    ex = {}
    cnt = 0
    for inp in inputs:
        seen = set()
        for r in records(inp):
            g = r["gens"] if isinstance(r["gens"], str) else " ".join(r["gens"])
            if g in seen:
                continue
            seen.add(g)
            try:
                a = Arr(g, r.get("n"))
                q0, inc, lam = analyze(a)
            except ValueError:
                continue
            cnt += 1
            for L in range(a.n):
                s = (q0[L], tuple(sorted(inc[L])))
                sigs[s] += 1
                ex.setdefault(s, (g, L))
            if cnt >= limit:
                break
    return sigs, ex, cnt


def final_charges(q0, inc, rules):
    """apply transfer rules: rules[(tau, x, y)] = w; a line with role x at a point of type tau gives w to the line
    (or cap) with role y at the same point, once per such partner."""
    n = len(q0)
    q = list(q0)
    by_point = collections.defaultdict(list)     # (point id) -> [(line, role)]
    for L in range(n):
        for (tau, rl, pid) in inc[L]:
            by_point[(tau, pid)].append((L, rl))
    for (tau, pid), mem in by_point.items():
        for (L1, x) in mem:
            for (L2, y) in mem:
                if (L1, x) == (L2, y):
                    continue
                w = rules.get((tau, x, y))
                if w:
                    q[L1] -= w
                    q[L2] += w
    return q


def check(a):
    rules = {}
    for r in json.load(open(a.rules)):
        rules[(tuple(r["tau"]), tuple(r["frm"]), tuple(r["to"]))] = F(r["w"]).limit_denominator(1000)
    bad = collections.Counter()
    ex = {}
    cnt = 0
    mins = collections.Counter()
    for inp in a.inputs:
        seen = set()
        for r in records(inp):
            g = r["gens"] if isinstance(r["gens"], str) else " ".join(r["gens"])
            if g in seen:
                continue
            seen.add(g)
            try:
                ar = Arr(g, r.get("n"))
                q0, inc, lam = analyze(ar, with_ids=True)
            except ValueError:
                continue
            cnt += 1
            q = final_charges(q0, inc, rules)
            mins[min(q) >= THIRD] += 1
            for L in range(ar.n):
                if q[L] < THIRD:
                    key = (q0[L], tuple(sorted((t, rl) for t, rl, _ in inc[L])))
                    bad[key] += 1
                    ex.setdefault(key, (g, L, q[L]))
            if cnt >= a.limit:
                break
            if cnt % 100000 == 0:
                print(f"  ... {cnt}", flush=True)
    print(f"{cnt} arrangements; all lines >= 1/3 in {mins[True]}, violated in {mins[False]}")
    for k, v in bad.most_common(15):
        g, L, qq = ex[k]
        print(f"  {v:6d} final {qq}  q0={k[0]}  inc={k[1]}\n      line {L} of {g[:70]}...")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["stats", "lp", "check"])
    ap.add_argument("--rules", help="rules json for check mode")
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--out")
    ap.add_argument("--limit", type=int, default=10 ** 9)
    ap.add_argument("--slack", action="store_true")
    a = ap.parse_args()
    if a.mode == "check":
        return check(a)
    sigs, ex, cnt = load(a.inputs, a.limit)
    print(f"{cnt} arrangements, {len(sigs)} distinct line signatures")
    low = [(s, v) for s, v in sigs.items() if s[0] < THIRD]
    print(f"deficient signatures (q0 < 1/3): {len(low)} covering {sum(v for _, v in low)} lines")
    for s, v in sorted(low, key=lambda x: -x[1])[:25]:
        print(f"  {v:7d}  q0={s[0]}  inc={s[1]}")
    if a.mode == "stats":
        return
    # LP: variables w[(tau, from_role, to_role)] >= 0 for roles co-occurring at a point type
    roles_at = collections.defaultdict(set)
    for (q, inc), _ in sigs.items():
        for tau, rl in inc:
            roles_at[tau].add(rl)
    var = {}
    for tau, rls in roles_at.items():
        for x in rls:
            if x[0] != "line":
                continue  # caps only receive
            for y in rls:
                if y != x:
                    var[(tau, x, y)] = len(var)
    print(f"{len(var)} transfer variables over {len(roles_at)} point types")
    import numpy as np
    from scipy.optimize import linprog
    from scipy.sparse import lil_matrix
    rows = list(sigs)
    A = lil_matrix((len(rows), len(var)))
    b = np.zeros(len(rows))
    for ri, (q, inc) in enumerate(rows):
        # q + sum_in w - sum_out w >= 1/3   ->   -sum_in + sum_out <= q - 1/3
        cnt_inc = collections.Counter(inc)
        for (tau, rl), m in cnt_inc.items():
            for (t2, x, y), vi in var.items():
                if t2 != tau:
                    continue
                if y == rl:
                    A[ri, vi] -= m
                if x == rl:
                    A[ri, vi] += m
        b[ri] = float(q - THIRD)
    # minimize total transfer (sparsest rule set); with --slack, add one slack per signature and minimise
    # count-weighted slack first (which signatures cannot be fixed by point-local transfers)
    if a.slack:
        from scipy.sparse import hstack, identity
        m = len(rows)
        A2 = hstack([A.tocsr(), -identity(m, format="csr")]).tocsr()
        cvec = np.concatenate([1e-4 * np.ones(len(var)), np.array([sigs[r] for r in rows], dtype=float)])
        res = linprog(cvec, A_ub=A2, b_ub=b, bounds=[(0, 3)] * len(var) + [(0, None)] * m, method="highs")
        if res.status == 0:
            sl = res.x[len(var):]
            bad = [(rows[i], sl[i]) for i in range(m) if sl[i] > 1e-9]
            print(f"unfixable signatures: {len(bad)} covering {sum(sigs[r] for r, _ in bad)} lines")
            for r, v in sorted(bad, key=lambda t: -sigs[t[0]])[:20]:
                g, L = ex[r]
                print(f"  {sigs[r]:6d} short by {v:.4f}  q0={r[0]}  inc={r[1]}\n        example line {L} of {g[:80]}...")
            res.x = res.x[:len(var)]
            res.status = 0
    else:
        res = linprog(np.ones(len(var)), A_ub=A.tocsr(), b_ub=b, bounds=(0, 3), method="highs")
    print("LP status:", res.status, res.message)
    if res.status == 0:
        used = [(k, res.x[i]) for k, i in var.items() if res.x[i] > 1e-9]
        print(f"{len(used)} nonzero transfers:")
        for (tau, x, y), w in sorted(used, key=lambda t: -t[1]):
            print(f"  {w:.4f}  type {''.join(tau)}:  {''.join(x[1:])}({x[0]}) -> {''.join(y[1:])}({y[0]})")
        if a.out:
            json.dump([dict(tau="".join(t), frm=list(x), to=list(y), w=w) for (t, x, y), w in used], open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()

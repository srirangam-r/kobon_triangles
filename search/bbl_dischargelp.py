"""LP search for point-level discharging rules that prove the conservative unit lemma (budget 6 per triple point).

cost(P) is search/bbl_point.costs. Edges between triple points: 'mut' (mutual pair), 'bri' (bridge), 'lnk' (consecutive
triple points on a line, not a bridge), 'cap' (blocks sharing a pure cap). A rule w[(tau_from, tau_to, edge)] >= 0 moves
charge along every such edge. Point type tau = ray pattern (N/B/R, up to symmetry) + sorted block statuses
(I/U/M with p/t = pure/triple cap). Points in 2-point units of type (IpMt, IpMt) are exempt (handled by the extended lemma).

    python search/bbl_dischargelp.py <in>... [--out rules.json] [--depth 1]
"""
import argparse
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.append(str(ROOT / "work/t3"))
from arr import Arr  # noqa: E402
from cluster import records  # noqa: E402
from bbl_rules import Charge  # noqa: E402
from bbl_point import costs  # noqa: E402
from bbl_unit import units  # noqa: E402
from bbl_charge import point_type  # noqa: E402


def graph(ch, st):
    a, trip = ch.a, ch.trip
    E = []
    for b, s in st.items():
        if s == "M":
            for b2 in ch.blk:
                if b2 is not b and b2[4] == b[4] and b2[2] == b[5]:
                    E.append((b[0], b2[0], "mut"))
    for L in range(a.n):
        r = a.rows[L]
        ps = [i for i, v in enumerate(r) if v in trip]
        for x, y in zip(ps, ps[1:]):
            kind = "bri" if (y == x + 1 and len(a.t[L][x]) == 2) else "lnk"
            E.append((r[x], r[y], kind))
            E.append((r[y], r[x], kind))
    bycap = collections.defaultdict(set)
    for b in ch.blk:
        if not ch.onl[b[5]]:
            bycap[b[5]].add(b[0])
    for ps in bycap.values():
        for p in ps:
            for q in ps:
                if p != q:
                    E.append((p, q, "cap"))
    return E


def collect(inputs, limit):
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
                ch = Charge(Arr(g, r.get("n")))
            except ValueError:
                continue
            cnt += 1
            cost, sig, st = costs(ch)
            tau = {P: "".join(point_type(ch.st[P])) + ":" + "".join(sorted(sig[P])) for P in ch.a.triples}
            us, _ = units(ch, True)
            exempt = set()
            for K in us:
                if len(K) == 2 and sorted(tau[P].split(":")[1] for P in K) == ["IpMt", "IpMt"]:
                    exempt |= K
            E = graph(ch, st)
            out = collections.defaultdict(list)
            inn = collections.defaultdict(list)
            for p, q, k in E:
                out[p].append((tau[q], k))
                inn[q].append((tau[p], k))
            for P in ch.a.triples:
                if P in exempt:
                    continue
                s = (tau[P], cost[P], tuple(sorted(out[P])), tuple(sorted(inn[P])))
                sigs[s] += 1
                ex.setdefault(s, g)
            if cnt >= limit:
                break
    return sigs, ex, cnt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--out")
    ap.add_argument("--limit", type=int, default=10 ** 9)
    a = ap.parse_args()
    sigs, ex, cnt = collect(a.inputs, a.limit)
    rows = list(sigs)
    print(f"{cnt} arrangements, {len(rows)} point signatures; over budget: "
          f"{sum(v for s, v in sigs.items() if s[1] > 6)} points")
    var = {}
    for (t, c, outs, inns) in rows:
        for (t2, k) in outs:
            var.setdefault((t, t2, k), len(var))
    import numpy as np
    from scipy.optimize import linprog
    from scipy.sparse import lil_matrix, hstack, identity
    m = len(rows)
    A = lil_matrix((m, len(var)))
    b = np.zeros(m)
    for i, (t, c, outs, inns) in enumerate(rows):
        # final = c - sum_out w + sum_in w <= 6
        for (t2, k) in outs:
            A[i, var[(t, t2, k)]] -= 1
        for (t2, k) in inns:
            A[i, var[(t2, t, k)]] += 1
        b[i] = 6 - float(c)
    A2 = hstack([A.tocsr(), -identity(m, format="csr")]).tocsr()
    cvec = np.concatenate([1e-5 * np.ones(len(var)), np.array([sigs[r] for r in rows], dtype=float)])
    res = linprog(cvec, A_ub=A2, b_ub=b, bounds=[(0, 6)] * len(var) + [(0, None)] * m, method="highs")
    print("LP:", res.message)
    sl = res.x[len(var):]
    bad = [(rows[i], sl[i]) for i in range(m) if sl[i] > 1e-9]
    print(f"unfixable signatures: {len(bad)} covering {sum(sigs[r] for r, _ in bad)} points")
    for r, v in sorted(bad, key=lambda z: -sigs[z[0]])[:12]:
        print(f"  {sigs[r]:6d} short {v:.3f}  {r[0]} cost {r[1]}  out={r[2][:6]}")
    used = sorted(((k, res.x[i]) for k, i in var.items() if res.x[i] > 1e-9), key=lambda z: -z[1])
    print(f"{len(used)} nonzero rules")
    for (t, t2, k), w in used[:40]:
        print(f"  {w:.4f}  {t} --{k}--> {t2}")
    if a.out:
        json.dump([dict(frm=t, to=t2, edge=k, w=w) for (t, t2, k), w in used], open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()

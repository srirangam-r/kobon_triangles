"""Per-line form of the unit lemma with cap-gap transfers.

Conservative slack of a unit K, per line:  sum_{L in L(K)} [3(r_L - B_L) - 1] + U + Upc - PC,
r_L = runs of triple points along L (maximal bridge paths; all triple points on L lie in K), B_L = block rays along L.

Cap gap: a block b = [P, X] on the axis l with cap C whose two flank rays at P end at triple points F1, F2. Then F1, X, F2
are consecutive on C, so C has a gap (non-bridge link) at X, i.e. one extra run. Rule T1: that gap pays 3 to l.
A gap claimed by two blocks (4 triangles around X) pays only one of them.

After T1:  v_L = 2 + 3 (free gaps of L) - 3 (uncompensated blocks on L) + credits,
credits (cons): +1 per distinct u of U-blocks on L; pure caps: -1 + #U-blocks capped.  (ext): p_L instead.

    python search/bbl_gap.py <in>... [--extended] [--show 30]
"""
import argparse
import collections
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.append(str(ROOT / "work/t3"))
from arr import Arr, rays, far_end  # noqa: E402
from cluster import records  # noqa: E402
from bbl_rules import Charge  # noqa: E402
from bbl_unit import units  # noqa: E402
from bbl_point import costs  # noqa: E402
from bbl_adversary import portions, ext_slack  # noqa: E402


def analyze(ch, ext=False):
    a, trip = ch.a, ch.trip
    st = ch.side_status()
    rec = portions(ch)
    # runs and gaps
    runs, gaps = {}, {}
    for L in range(a.n):
        r = a.rows[L]
        ps = [i for i, v in enumerate(r) if v in trip]
        nbr = sum(1 for x, y in zip(ps, ps[1:]) if y == x + 1 and len(a.t[L][x]) == 2)
        runs[L] = len(ps) - nbr
        gaps[L] = [(r[x], r[y]) for x, y in zip(ps, ps[1:]) if not (y == x + 1 and len(a.t[L][x]) == 2)]
    # cap gaps
    claim = {}
    comp = {}
    for b in ch.blk:
        (P, i, l, d, X, C) = b
        rs = rays(a, P)
        F1, F2 = far_end(a, P, rs[(i - 1) % 6]), far_end(a, P, rs[(i + 1) % 6])
        comp[b] = False
        if F1 in trip and F2 in trip:
            r = a.rows[C]
            i1, ix, i2 = a.pos[C][F1], a.pos[C][X], a.pos[C][F2]
            assert sorted([i1, ix, i2]) == [min(i1, i2), ix, max(i1, i2)] and abs(i1 - i2) == 2, "cap gap shape"
            key = (C, X)
            if key not in claim:
                claim[key] = b
                comp[b] = True
    used_gaps = collections.Counter(C for (C, X) in claim)
    ukey = {}
    for b, s in st.items():
        if s == "U":
            (P, i, l, d, X, C) = b
            ix = a.pos[l][X]
            ukey[b] = (l, ix if d == 1 else ix - 1)
    v = {}
    info = {}
    Bl = collections.Counter(b[2] for b in ch.blk)
    Bc = collections.Counter(b[2] for b in ch.blk if comp[b])
    for L in range(a.n):
        if ch.onl[L]:
            v[L] = 3 * runs[L] - 1 - 3 * Bl[L] + 3 * Bc[L] - 3 * used_gaps[L]
    pcs = set(b[5] for b in ch.blk if not ch.onl[b[5]])
    for C in pcs:
        v[C] = F(-1)
    if ext:
        for L in v:
            v[L] += rec[L]
    else:
        for u in set(ukey.values()):
            v[u[0]] += 1
        for b in ukey:
            if b[5] in pcs:
                v[b[5]] += 1
    for L in v:
        info[L] = dict(runs=runs[L], free=len(gaps[L]) - used_gaps[L], B=Bl[L], unc=Bl[L] - Bc[L],
                       pure=L in pcs, p=rec[L])
    return v, info, st, comp


def line_sig(ch, L, st, comp, info):
    a = ch.a
    seq = []
    for P in ch.onl[L]:
        rs = rays(a, P)
        s = ""
        for d in (-1, +1):
            i = rs.index((L, d))
            t = ch.st[P][i]
            if t == "B":
                b = next(b for b in ch.blk if b[0] == P and b[1] == i)
                t = ("b" if comp[b] else "B") + st[b]
            s += t
        seq.append(s)
    capped = [("c" if comp[b] else "u") + st[b] for b in ch.blk if b[5] == L]
    f = info[L]
    return f"{' '.join(seq) or '-'} | caps {','.join(sorted(capped))} | free {f['free']} p {f['p']}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--extended", dest="ext", action="store_true")
    ap.add_argument("--show", type=int, default=30)
    ap.add_argument("--limit", type=int, default=10 ** 9)
    o = ap.parse_args()
    dist = collections.Counter()
    bad = collections.Counter()
    ex = {}
    cnt = 0
    for inp in o.inputs:
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
            v, info, st, comp = analyze(ch, o.ext)
            # sanity: per-unit sums equal the unit slacks
            ch._rec = portions(ch)
            cost, _, _ = costs(ch)
            us, _ = units(ch, True)
            for K in us:
                D = set(L for P in K for L in ch.a.events[P]) | set(
                    b[5] for b in ch.blk if b[0] in K and not ch.onl[b[5]])
                s = sum(v[L] for L in D)
                ref = ext_slack(ch, K) if o.ext else 6 * len(K) - sum(cost[P] for P in K)
                assert s == ref, (g, s, ref)
            for L, x in v.items():
                dist[x] += 1
                if x < 0:
                    k = (str(x), line_sig(ch, L, st, comp, info))
                    bad[k] += 1
                    ex.setdefault(k, g)
            if cnt >= o.limit:
                break
    print(f"{cnt} arrangements ({'ext' if o.ext else 'cons'}); v_L distribution:",
          {str(k): n for k, n in sorted(dist.items())})
    print(f"negative lines: {sum(bad.values())} in {len(bad)} signatures")
    for k, n in bad.most_common(o.show):
        print(f"  {n:7d}  v={k[0]:>4}  {k[1]}")


if __name__ == "__main__":
    main()

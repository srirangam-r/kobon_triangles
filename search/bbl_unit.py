"""Unit lemma test. Units = components of the graph on triple points whose edges are bridges and mutual pairs.
For a unit K with lines L(K) (through its points) and pure caps PC(K) (caps of its blocks avoiding all triple points):
    slack(K) = sum_{P in K} c_P + (1/3) sum_{U-blocks b of K} (1 + [cap(b) pure]) - (|L(K)| + |PC(K)|)/3  >= 0 ?
Also reports the extended slack that adds the units' other own unused segments and touches (lines of L(K) only).

    python search/bbl_unit.py <in>...
"""
import collections
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.append(str(ROOT / "work/t3"))
from arr import Arr  # noqa: E402
from cluster import records  # noqa: E402
from bbl_rules import Charge  # noqa: E402
from bbl_charge import point_type  # noqa: E402


def units(ch, lineconn=False):
    a, trip = ch.a, ch.trip
    adj = collections.defaultdict(set)
    if lineconn:  # also link triple points sharing a line, or whose blocks share a pure cap
        for L in range(a.n):
            ps = ch.onl[L]
            for x, y in zip(ps, ps[1:]):
                adj[x].add(y); adj[y].add(x)
        bycap = collections.defaultdict(list)
        for b in ch.blk:
            if not ch.onl[b[5]]:
                bycap[b[5]].append(b[0])
        for ps in bycap.values():
            for x, y in zip(ps, ps[1:]):
                adj[x].add(y); adj[y].add(x)
    for L in range(a.n):
        r = a.rows[L]
        for e in range(len(r) - 1):
            if len(a.t[L][e]) == 2 and r[e] in trip and r[e + 1] in trip:
                adj[r[e]].add(r[e + 1]); adj[r[e + 1]].add(r[e])
    st = ch.side_status()
    for b, s in st.items():
        if s == "M":
            for b2 in ch.blk:
                if b2 is not b and b2[4] == b[4] and b2[2] == b[5]:
                    adj[b[0]].add(b2[0]); adj[b2[0]].add(b[0])
    seen, out = set(), []
    for P in a.triples:
        if P in seen:
            continue
        comp, stack = set(), [P]
        seen.add(P)
        while stack:
            q = stack.pop(); comp.add(q)
            for r2 in adj[q]:
                if r2 not in seen:
                    seen.add(r2); stack.append(r2)
        out.append(comp)
    return out, st


LINECONN = "--lineconn" in sys.argv
if LINECONN:
    sys.argv.remove("--lineconn")


def main():
    dist = collections.Counter()
    worst = {}
    tight = collections.Counter()
    cnt = 0
    for inp in sys.argv[1:]:
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
            us, st = units(ch, LINECONN)
            a_ = ch.a
            useg = collections.Counter()
            ukey = {}
            for b, s_ in st.items():
                if s_ == "U":
                    (P, i, l, d, X, C) = b
                    ix = a_.pos[l][X]
                    ukey[b] = (l, ix if d == 1 else ix - 1)
                    useg[ukey[b]] += 1
            mdem = collections.Counter()
            dem = []
            for K in us:
                LK = set(L for P in K for L in ch.a.events[P])
                PC = set(b[5] for b in ch.blk if b[0] in K and not ch.onl[b[5]])
                dem.append(LK | PC)
                for L in LK | PC:
                    mdem[L] += 1
            for K, DK in zip(us, dem):
                LK = set(L for P in K for L in ch.a.events[P])
                blocks = [b for b in ch.blk if b[0] in K]
                PC = set(b[5] for b in blocks if not ch.onl[b[5]])
                if LINECONN:
                    Uc = len(set(ukey[b] for b in blocks if st[b] == "U")) + sum(1 for b in blocks if st[b] == "U" and not ch.onl[b[5]])
                else:
                    Uc = sum(F(1, useg[ukey[b]]) + (not ch.onl[b[5]]) for b in blocks if st[b] == "U")
                slack = sum(ch.c[P] for P in K) + F(Uc) / 3 - sum(F(1, 3 * mdem[L]) for L in DK)
                shape = (len(K), "".join(sorted("".join(point_type(ch.st[P])) for P in K))[:60],
                         "".join(sorted(st[b] for b in blocks)))
                dist[slack] += 1
                if slack not in worst or len(K) < worst[slack][0][0]:
                    worst[slack] = (shape, g)
                if slack == 0:
                    tight[shape] += 1
    print(f"{cnt} arrangements; unit slack distribution (lowest first):",
          [(str(k), v) for k, v in sorted(dist.items())[:10]])
    for k in sorted(worst)[:6]:
        print(f"  slack {k}: e.g. unit {worst[k][0]}\n      {worst[k][1][:100]}")
    print("tight unit shapes:", dict(tight.most_common(10)))


if __name__ == "__main__":
    main()

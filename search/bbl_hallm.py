"""Two-hop Hall lemma with points of any multiplicity (extends search/bbl_hall.py; identical on triple-only arrangements).

An m-fold point P (m >= 3) has 2m rays; statuses N / B / R as before (R: doubly used, far end multiple).
c_P = m(m-2) - D_P - beta_P/2, and 3 c_P = (3/2)(N_P - D_P) + 3m(m-3): the ray split plus a bonus 3(m-3) to each
of its m lines. Flank rays of a block on ray i: rays i-1, i+1 (mod 2m). T1, F, relations, HL as in bbl_hall.py, with
"triple" read as "multiple" (multiplicity >= 3).

    python search/bbl_hallm.py <in>... [--eps 1/6] [--push K] [--seed S]
--push K applies up to K random push-through moves (work/t3/mutate.push_through: a line moved through a multiple point)
to each input arrangement, creating 4-fold and higher points, and tests every intermediate arrangement.
"""
import argparse
import collections
import inspect  # noqa: F401  (stdlib module first: work/t3/inspect.py shadows it)
import random
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.append(str(ROOT / "work/t3"))
from arr import Arr, rays, first_seg, far_end, touches  # noqa: E402
from cluster import records  # noqa: E402

H = F(3, 2)


class Multi:
    def __init__(self, a):
        self.a = a
        mult = self.mult = {P: len(ev) for P, ev in enumerate(a.events) if len(ev) >= 3}
        self.st, self.blk = {}, []
        for P in mult:
            st = []
            for i, r in enumerate(rays(a, P)):
                fs = first_seg(a, P, r)
                if fs is None or len(a.t[fs[0]][fs[1]]) != 2:
                    st.append("N")
                    continue
                X = far_end(a, P, r)
                if X in mult:
                    st.append("R")
                else:
                    st.append("B")
                    self.blk.append((P, i, r[0], r[1], X, a.other(X, r[0])))
            self.st[P] = st
        self.onl = [[P for P in a.rows[L] if P in mult] for L in range(a.n)]
        self.rec = collections.Counter()
        for L in range(a.n):
            self.rec[L] += sum(1 for s in a.t[L] if not s)
        for (u, X, L) in touches(a):
            self.rec[L] += 1
        self.lam = a.n * (a.n - 2) - 3 * a.T()


def values(ch):
    a, mult = ch.a, ch.mult
    val = {L: F(ch.rec[L]) - 1 for L in range(a.n)}
    for P, m in mult.items():
        for i, r in enumerate(rays(a, P)):
            s = ch.st[P][i]
            val[r[0]] += H if s == "N" else -H if s == "B" else 0
        for L in a.events[P]:
            val[L] += 3 * (m - 3)
    served = {}
    for b in ch.blk:
        (P, i, l, d, X, C) = b
        rs = rays(a, P)
        k = len(rs)
        F1, F2 = far_end(a, P, rs[(i - 1) % k]), far_end(a, P, rs[(i + 1) % k])
        got = F(0)
        if F1 in mult and F2 in mult:
            for Q in (F1, F2):
                dq = 1 if a.pos[C][X] > a.pos[C][Q] else -1
                j = rays(a, Q).index((C, dq))
                if ch.st[Q][j] == "N":
                    got += H
        val[C] -= got
        val[l] += got
        served[b] = got > 0
    for b in ch.blk:
        if served[b]:
            continue
        (P, i, l, d, X, C) = b
        rs = rays(a, P)
        k = len(rs)
        for f in ((i - 1) % k, (i + 1) % k):
            if ch.st[P][f] == "N":
                val[rs[f][0]] -= 1
                val[l] += 1
    return val, served


def relation(ch, hops=2):
    a = ch.a
    rel = collections.defaultdict(set)
    for P in ch.mult:
        for L in a.events[P]:
            rel[L] |= set(a.events[P]) - {L}
    for b in ch.blk:
        rel[b[2]].add(b[5])
        rel[b[5]].add(b[2])
        if not ch.onl[b[5]]:
            for L in a.events[b[0]]:
                if L != b[5]:
                    rel[b[5]].add(L)
                    rel[L].add(b[5])
    if hops == 2:
        rel = {L: set().union(rel[L], *(rel[M] for M in rel[L])) - {L} for L in range(a.n)}
    return {L: rel.get(L, set()) for L in range(a.n)}


def hall_deficit(ch, eps=F(0), hops=2):
    import networkx as nx
    val, served = values(ch)
    rel = relation(ch, hops)
    d = {L: val[L] - (eps if ch.onl[L] else 0) for L in val}
    G = nx.DiGraph()
    G.add_node("s")
    G.add_node("t")
    need = F(0)
    for L, x in d.items():
        if x > 0:
            G.add_edge("s", L, capacity=x)
        elif x < 0:
            G.add_edge(L, "t", capacity=-x)
            need += -x
            for M in rel[L]:
                if d[M] > 0:
                    G.add_edge(M, L)
    if need == 0:
        return F(0), val, d
    return need - F(nx.maximum_flow_value(G, "s", "t")).limit_denominator(10 ** 6), val, d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--eps", default="1/6")
    ap.add_argument("--push", type=int, default=0)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--limit", type=int, default=10 ** 9)
    o = ap.parse_args()
    from mutate import push_through
    eps = F(o.eps)
    rng = random.Random(o.seed)
    tot = bad = 0
    bym = collections.Counter()
    for inp in o.inputs:
        cnt = 0
        for r in records(inp):
            g = r["gens"] if isinstance(r["gens"], str) else " ".join(r["gens"])
            a = Arr(g, r.get("n"))
            chain = [a]
            for _ in range(o.push):
                cur = chain[-1]
                opts = [(P, w) for P, ev in enumerate(cur.events) if len(ev) >= 3 for w in range(cur.n)
                        if w not in ev]
                rng.shuffle(opts)
                nxt = None
                for P, w in opts[:200]:
                    wd = push_through(cur, P, w)
                    if wd is not None:
                        nxt = Arr(wd, cur.n)
                        break
                if nxt is None:
                    break
                chain.append(nxt)
            for b in chain:
                ch = Multi(b)
                dfc, val, d = hall_deficit(ch, eps)
                waste = sum(1 for L in range(b.n) for e, sd in enumerate(b.t[L]) if not sd
                            for X in (b.rows[L][e], b.rows[L][e + 1]) if not b.is_simple(X))
                assert 3 * ch.lam - b.n == sum(val.values()) + waste, ("identity", sum(val.values()), waste, ch.lam)
                tot += 1
                bym[max(ch.mult.values(), default=2)] += 1
                if dfc > 0 and b.n % 2 == 0:
                    bad += 1
                    print("VIOLATION", b.n, b.T(), str(dfc), " ".join(str(len(e)) for e in b.events if len(e) > 3))
            cnt += 1
            if cnt >= o.limit:
                break
    print(f"{tot} arrangements (by max multiplicity {dict(bym)}), eps={eps}: even-n Hall violations {bad}")


if __name__ == "__main__":
    main()

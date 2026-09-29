"""Exact D-count by bridge clusters.

  Lambda = Z + sum_P c_P,   c_P = 3 - D_P - beta_P/2     (triple points only; L1: D = sum D_P + beta)

D_P = doubly used first segments at P with a simple far end, beta_P = doubly used segments at P whose other end is
multiple (bridges). A cluster is a connected component of the bridge graph; its charge is
c(Q) = 3|Q| - sum_Q D_P - beta(Q). Prints, per input set, the distribution of cluster charges by cluster shape and
checks the identity on every arrangement.

    python search/cluster.py <in.jsonl|dir-glob> [...] [--n N]
"""
import argparse
import collections
import glob
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT / "work/t3"))
from arr import Arr  # noqa: E402


def clusters(a, faces=False):
    n = a.n
    trip = set(a.triples)
    Dp = collections.Counter()
    adj = collections.defaultdict(set)
    beta = 0
    bset = set()
    for L in range(n):
        r = a.rows[L]
        for e in range(len(r) - 1):
            if len(a.t[L][e]) != 2:
                continue
            X, Y = r[e], r[e + 1]
            mx, my = X in trip, Y in trip
            if len(a.events[X]) > 3 or len(a.events[Y]) > 3:
                raise ValueError("4-fold point")
            if mx and my:
                beta += 1
                bset.add((min(X, Y), max(X, Y)))
                adj[X].add(Y)
                adj[Y].add(X)
            elif mx:
                Dp[X] += 1
            elif my:
                Dp[Y] += 1
            else:
                raise AssertionError("L1 violated: doubly used segment with two simple ends")
    if faces:  # also join the three vertices of every all-multiple triangular face
        for f in a.tris:
            vs = set()
            for (x, e, side) in f:
                vs.update(a.rows[x][e:e + 2])
            if len(vs) == 3 and all(v in trip for v in vs):
                for v in vs:
                    adj[v].update(vs - {v})
    seen, out = set(), []
    for P in a.triples:
        if P in seen:
            continue
        comp, stack = [], [P]
        seen.add(P)
        while stack:
            q = stack.pop()
            comp.append(q)
            for r in adj[q]:
                if r not in seen:
                    seen.add(r)
                    stack.append(r)
        b = sum(1 for q in comp for r in adj[q] if q < r and (q, r) in bset)
        d = sum(Dp[q] for q in comp)
        shape = tuple(sorted((Dp[q], sum(1 for r in adj[q] if (min(q, r), max(q, r)) in bset)) for q in comp))
        out.append(dict(size=len(comp), bridges=b, D=d, c=3 * len(comp) - d - b, shape=shape))
    Z = a.Z()
    lam = n * (n - 2) - 3 * a.T()
    assert lam == Z + sum(c["c"] for c in out), (lam, Z, out)
    return Z, lam, out


def records(path):
    files = sorted(glob.glob(path)) if any(ch in path for ch in "*?") or Path(path).is_dir() else [path]
    if Path(path).is_dir():
        files = sorted(glob.glob(str(Path(path) / "*.json*")))
    for f in files:
        if f.endswith(".jsonl"):
            for l in open(f):
                try:
                    r = json.loads(l)
                except json.JSONDecodeError:
                    continue
                if r.get("gens"):
                    yield r
        else:
            d = json.load(open(f))
            if isinstance(d, list):
                yield from (x for x in d if x.get("gens"))
            elif d.get("gens"):
                yield d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--n", type=int)
    ap.add_argument("--limit", type=int, default=10 ** 9)
    ap.add_argument("--faces", action="store_true", help="join clusters through all-multiple triangular faces too")
    a = ap.parse_args()
    for inp in a.inputs:
        cnt = 0
        minc = collections.Counter()      # (size>=2?) charge distribution of bridged clusters
        worst = {}
        lamZ = collections.Counter()
        seen = set()
        maxsize = {}
        for r in records(inp):
            g = r["gens"] if isinstance(r["gens"], str) else " ".join(r["gens"])
            if g in seen:
                continue
            seen.add(g)
            try:
                ar = Arr(g, a.n or r.get("n"))
                Z, lam, cl = clusters(ar, a.faces)
            except ValueError:
                continue
            cnt += 1
            br = [c for c in cl if c["size"] > 1]
            iso = [c for c in cl if c["size"] == 1]
            lamZ[(lam, Z, len(iso), tuple(sorted(c["c"] for c in br)))] += 1
            for c in br:
                minc[c["c"]] += 1
                maxsize[c["c"]] = max(maxsize.get(c["c"], 0), c["size"])
                key = c["c"]
                if key not in worst or c["size"] < worst[key]["size"]:
                    worst[key] = dict(c, lam=lam, Z=Z, gens=g)
            if cnt >= a.limit:
                break
        print(f"== {inp}: {cnt} arrangements")
        print("  bridged-cluster charge c(Q) distribution:", dict(sorted(minc.items())))
        print("  largest cluster at each charge:", dict(sorted(maxsize.items())))
        for k in sorted(worst)[:4]:
            w = worst[k]
            print(f"   c={k}: smallest cluster size {w['size']} bridges {w['bridges']} D {w['D']} shape {w['shape']} "
                  f"(Lambda {w['lam']}, Z {w['Z']})")
        top = sorted(lamZ.items(), key=lambda kv: (kv[0][0], -kv[1]))[:12]
        print("  (Lambda, Z, #isolated, bridged-cluster charges): count  [lowest Lambda first]")
        for k, v in top:
            print("   ", k, v)


if __name__ == "__main__":
    main()

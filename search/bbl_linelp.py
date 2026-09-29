"""LP search for per-line transfer rules on top of the cap-gap per-line form (search/bbl_gap.py, extended mode).

Relations carried by each block b = [P, X] (axis l, cap C):
  F  from the line of each flank ray of b (the rays next to b at P) to l;
  C> from l to C;   C< from C to l.
Types: block type = comp/uncomp + status U/M/I + cap pure/triple + sorted flank types (Ns, Nt, Rt: status N/R, far end
simple/triple); F relations also record which flank they come from. Target: every line ends >= 0.

    python search/bbl_linelp.py train <in>... --out rules.json
    python search/bbl_linelp.py test <in>... --rules rules.json [--show 20]
"""
import argparse
import collections
import json
import sys
from fractions import Fraction as F
from pathlib import Path

try:  # import before work/t3 (its inspect.py shadows the stdlib) enters sys.path
    import numpy as np
    from scipy.optimize import linprog
    from scipy.sparse import lil_matrix, hstack, identity
except ImportError:
    np = None

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.append(str(ROOT / "work/t3"))
from arr import Arr, rays, far_end  # noqa: E402
from cluster import records  # noqa: E402
from bbl_rules import Charge  # noqa: E402
from bbl_gap import analyze, line_sig  # noqa: E402


def ray_tokens(ch, st, comp, P):
    a, trip = ch.a, ch.trip
    rs = rays(a, P)
    bl = {b[1]: b for b in ch.blk if b[0] == P}
    tok = []
    for i, r in enumerate(rs):
        s = ch.st[P][i]
        if s == "N":
            fe = far_end(a, P, r)
            tok.append("N" + ("o" if fe is None else "t" if fe in trip else "s"))
        elif s == "R":
            tok.append("R")
        else:
            b = bl[i]
            tok.append("B" + st[b] + ("c" if comp[b] else "u") + ("t" if ch.onl[b[5]] else "p"))
    return tok


def point_relations(ch, st, comp):
    """('P', canonical point type, role from, role to) from each line through P to each other line through P"""
    a = ch.a
    out = []
    for P in a.triples:
        tok = ray_tokens(ch, st, comp, P)
        imgs = []
        for start in range(6):
            for sg in (1, -1):
                imgs.append((tuple(tok[(start + sg * j) % 6] for j in range(6)), start, sg))
        best = min(im for im, _, _ in imgs)
        rs = rays(a, P)
        roles = {}
        for i in range(3):
            roles[rs[i][0]] = min((sg * (i - start)) % 3 for im, start, sg in imgs if im == best)
        pt = "".join(best)
        for A in roles:
            for B in roles:
                if A != B:
                    out.append((("P", pt, roles[A], roles[B]), A, B))
    return out


def relations(ch, st, comp):
    a, trip = ch.a, ch.trip
    out = []   # (key, donor line, recipient line)
    if KINDS and "P" in KINDS:
        out += point_relations(ch, st, comp)
    for b in ch.blk:
        (P, i, l, d, X, C) = b
        rs = rays(a, P)
        ft = []
        for f in ((i - 1) % 6, (i + 1) % 6):
            fe = far_end(a, P, rs[f])
            ft.append(ch.st[P][f] + ("t" if fe in trip else "s"))
        bt = ("c" if comp[b] else "u") + st[b] + ("t" if ch.onl[C] else "p") + "/" + "".join(sorted(ft))
        if "F" in KINDS:
            for k, f in enumerate(((i - 1) % 6, (i + 1) % 6)):
                out.append((("F", bt, ft[k]), rs[f][0], l))
        if "C" in KINDS:
            out.append((("C>", bt), l, C))
            out.append((("C<", bt), C, l))
    return out


KINDS = {"F", "C"}


def gather(inputs, limit):
    for inp in inputs:
        seen = set()
        cnt = 0
        for r in records(inp):
            g = r["gens"] if isinstance(r["gens"], str) else " ".join(r["gens"])
            if g in seen:
                continue
            seen.add(g)
            try:
                ch = Charge(Arr(g, r.get("n")))
            except ValueError:
                continue
            v, info, st, comp = analyze(ch, True)
            rel = relations(ch, st, comp)
            ins, outs = collections.defaultdict(list), collections.defaultdict(list)
            for k, dn, rc in rel:
                if dn in v and rc in v:
                    outs[dn].append(k)
                    ins[rc].append(k)
            yield g, ch, v, st, comp, info, ins, outs
            cnt += 1
            if cnt >= limit:
                break


def train(o):
    sigs = collections.Counter()
    for g, ch, v, st, comp, info, ins, outs in gather(o.inputs, o.limit):
        for L in v:
            sigs[(v[L], tuple(sorted(ins[L])), tuple(sorted(outs[L])))] += 1
    rows = list(sigs)
    var = {}
    for (_, ins, outs) in rows:
        for k in ins + outs:
            var.setdefault(k, len(var))
    print(f"{sum(sigs.values())} lines, {len(rows)} signatures, {len(var)} relation types; "
          f"negative before: {sum(c for s, c in sigs.items() if s[0] < 0)}")
    m = len(rows)
    A = lil_matrix((m, len(var)))
    b = np.zeros(m)
    for i, (v0, ins, outs) in enumerate(rows):
        # v0 + sum_in w - sum_out w >= 0   <=>   -sum_in w + sum_out w <= v0
        for k in ins:
            A[i, var[k]] -= 1
        for k in outs:
            A[i, var[k]] += 1
        b[i] = float(v0)
    A2 = hstack([A.tocsr(), -identity(m, format="csr")]).tocsr()
    cvec = np.concatenate([o.eps * np.ones(len(var)), np.array([sigs[r] for r in rows], dtype=float)])
    res = linprog(cvec, A_ub=A2, b_ub=b, bounds=[(0, 6)] * len(var) + [(0, None)] * m, method="highs")
    print("LP:", res.message)
    sl = res.x[len(var):]
    bad = [(rows[i], sl[i]) for i in range(m) if sl[i] > 1e-9]
    print(f"unfixable signatures: {len(bad)} covering {sum(sigs[r] for r, _ in bad)} lines")
    for r, s in sorted(bad, key=lambda z: -sigs[z[0]])[:10]:
        print(f"  {sigs[r]:6d} short {s:.3f} v={r[0]} in={r[1][:4]} out={r[2][:4]}")
    used = sorted(((k, res.x[i]) for k, i in var.items() if res.x[i] > 1e-7), key=lambda z: (z[0][0], -z[1]))
    print(f"{len(used)} nonzero rules")
    for k, w in used:
        print(f"  {w:.4f}  {k}")
    if o.out:
        json.dump([dict(key=list(k), w=w) for k, w in used], open(o.out, "w"), indent=1)


def test(o):
    W = {tuple(r["key"]): F(r["w"]).limit_denominator(12) for r in json.load(open(o.rules))}
    dist = collections.Counter()
    bad = collections.Counter()
    ex = {}
    narr = nbad = 0
    for g, ch, v, st, comp, info, ins, outs in gather(o.inputs, o.limit):
        narr += 1
        fin = {L: v[L] + sum(W.get(k, 0) for k in ins[L]) - sum(W.get(k, 0) for k in outs[L]) for L in v}
        neg = [L for L in fin if fin[L] < 0]
        nbad += bool(neg)
        for L in fin:
            dist[min(fin[L], 3)] += 1
        for L in neg:
            k = (str(fin[L]), line_sig(ch, L, st, comp, info), tuple(sorted(ins[L])))
            bad[k] += 1
            ex.setdefault(k, g)
    print(f"{narr} arrangements; {nbad} with a negative line; final distribution (capped at 3):",
          {str(k): c for k, c in sorted(dist.items())})
    for k, c in bad.most_common(o.show):
        print(f"  {c:6d} fin={k[0]} {k[1]}\n         in={k[2]}")
        if o.examples:
            print("         ex:", ex[k])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["train", "test"])
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--out")
    ap.add_argument("--rules")
    ap.add_argument("--limit", type=int, default=10 ** 9)
    ap.add_argument("--eps", type=float, default=1e-4)
    ap.add_argument("--show", type=int, default=20)
    ap.add_argument("--examples", action="store_true")
    ap.add_argument("--kinds", default="F,C", help="relation kinds: F (flank), C (cap), P (point split)")
    o = ap.parse_args()
    KINDS.clear()
    KINDS.update(o.kinds.split(","))
    train(o) if o.mode == "train" else test(o)


if __name__ == "__main__":
    main()

"""Annealing adversary against the per-line lemma (search/bbl_linelp.py rules): minimise the smallest final line value.
Writes every arrangement reaching a negative line to <out.jsonl> (deduplicated by wiring word).

    python search/bbl_lineadv.py <out.jsonl> <seed> <steps> <T> <rules.json> <kinds> <start.jsonl...> [--pick K]
"""
import inspect  # noqa: F401  (load the stdlib module before work/t3, whose inspect.py shadows it, enters sys.path)
import json
import math
import random
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.append(str(ROOT / "work/t3"))
from arr import Arr  # noqa: E402
from mutate import random_move  # noqa: E402
from bbl_rules import Charge  # noqa: E402
from bbl_gap import analyze  # noqa: E402
import bbl_linelp  # noqa: E402
from cluster import records  # noqa: E402


def hall_score(a, eps):
    """(violation?, score): score = -10 * Hall deficit + min over negative lines L of (d_L + spare within 2 hops)"""
    import bbl_hall
    ch = Charge(a)
    dfc, val, d = bbl_hall.hall_deficit(ch, eps, 2)
    rel = bbl_hall.relation(ch, 2)
    loc = [d[L] + sum(d[M] for M in rel[L] if d[M] > 0) if d[L] < 0 else d[L] for L in d if ch.onl[L] or d[L] < 0]
    return dfc > 0, -10 * dfc + (min(loc) if loc else F(20))


def finals(a, W):
    if W == "S1":
        import bbl_s1
        return bbl_s1.s1(Charge(a))[0]
    ch = Charge(a)
    v, info, st, comp = analyze(ch, True)
    ins, outs = {L: 0 for L in v}, {L: 0 for L in v}
    for k, dn, rc in bbl_linelp.relations(ch, st, comp):
        if dn in v and rc in v:
            w = W.get(k, 0)
            outs[dn] += w
            ins[rc] += w
    return {L: v[L] + ins[L] - outs[L] for L in v}


def score(fin):
    if not fin:
        return F(99)
    m = min(fin.values())
    return m - F(1, 10) * sum(1 for x in fin.values() if x <= F(1, 2))


def main():
    out, seed, steps, T, rules, kinds = sys.argv[1:7]
    seed, steps, T = int(seed), int(steps), float(T)
    srcs = [s for s in sys.argv[7:] if not s.startswith("--")]
    pick = int(sys.argv[sys.argv.index("--pick") + 1]) if "--pick" in sys.argv else 4
    srcs = [s for s in srcs if not s.isdigit()]
    bbl_linelp.KINDS.clear()
    bbl_linelp.KINDS.update(kinds.split(","))
    if rules.startswith("HALL"):
        W = ("HALL", F(rules.split(":")[1]) if ":" in rules else F(0))
    elif rules == "S1f":  # canonical scheme: T1 + F + one round of two-hop fair sharing, no ordered rescue/pool
        import bbl_s1
        bbl_s1.POOL, bbl_s1.FAIR, bbl_s1.HOPS, bbl_s1.NORESCUE = 0, 1, 2, True
        W = "S1"
    elif rules.startswith("S1"):  # principled scheme: S1[:pool rounds]
        import bbl_s1
        bbl_s1.POOL = int(rules.split(":")[1]) if ":" in rules else 1
        W = "S1"
    else:
        W = {tuple(r["key"]): F(r["w"]).limit_denominator(24) for r in json.load(open(rules))}
    rng = random.Random(seed)
    starts = [r for s in srcs for r in records(s)]
    rng.shuffle(starts)
    fh = open(out, "a")
    found = set()
    for r in starts[:pick]:
        g = r["gens"] if isinstance(r["gens"], str) else " ".join(r["gens"])
        try:
            a = Arr(g, r.get("n"))
            cur = hall_score(a, W[1])[1] if isinstance(W, tuple) else score(finals(a, W))
        except (AssertionError, ValueError):
            continue
        n = a.n
        low = None
        for it in range(steps):
            w = random_move(a, rng, p_collapse=0.35, p_expand=0.25)
            if w is None:
                continue
            try:
                b = Arr(w, n)
                if any(len(ev) > 3 for ev in b.events):
                    continue
                if isinstance(W, tuple):
                    viol, s = hall_score(b, W[1])
                    fin = {0: F(-1) if viol else s}
                else:
                    fin = finals(b, W)
                    s = score(fin)
            except (AssertionError, ValueError):
                continue
            if s < cur or rng.random() < math.exp(-(float(s) - float(cur)) / T):
                a, cur = b, s
                m = min(fin.values()) if fin else 99
                if low is None or m < low:
                    low = m
                    print(f"seed {seed} n {n} it {it} min line {m} T {a.T()} k {len(a.triples)}", flush=True)
                if fin and m < 0 and w not in found:
                    found.add(w)
                    fh.write(json.dumps(dict(n=n, gens=w, T=a.T(), minline=str(m))) + "\n")
                    fh.flush()
    print(f"seed {seed} done, {len(found)} negative arrangements", flush=True)


if __name__ == "__main__":
    main()

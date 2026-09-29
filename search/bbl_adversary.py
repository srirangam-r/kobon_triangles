"""Falsification search for the unit lemma (search/bbl_unit.py, line-connected form).

Random flip / collapse / expand walks (work/t3/mutate.py), no T bias. mode 'random' accepts every valid move;
mode 'adv' hill-climbs to minimise the smallest unit slack (and, at ties, maximises the number of mutual pairs and
I-status blocks). Any unit with slack < 0, or a tight unit that is not a single X point, is written to <out>.

    python search/bbl_adversary.py <out.jsonl> <seed> <steps> <mode> <start.json>...
"""
import collections
import json
import random
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.insert(1, str(ROOT / "work/t3"))
from arr import Arr  # noqa: E402
from mutate import random_move  # noqa: E402
from bbl_rules import Charge  # noqa: E402
from bbl_point import costs  # noqa: E402
from bbl_unit import units  # noqa: E402
from bbl_charge import point_type  # noqa: E402


def portions(ch):
    """portions received by each line: own unused segments + touches (1 each, in thirds)"""
    a = ch.a
    rec = collections.Counter()
    for L in range(a.n):
        rec[L] += ch.Z[L]
        rec[L] += len(ch.touch[L])
    return rec


def ext_slack(ch, K):
    """3 * [sum c_P + (portions to D(K))/3 - |D(K)|/3], D(K) = lines through K + pure caps of K's blocks"""
    a = ch.a
    D = set(L for P in K for L in a.events[P]) | set(b[5] for b in ch.blk if b[0] in K and not ch.onl[b[5]])
    rec = ch._rec
    return 3 * sum(ch.c[P] for P in K) + sum(rec[L] for L in D) - len(D)


def evaluate(a):
    ch = Charge(a)
    ch._rec = portions(ch)
    cost, sig, st = costs(ch)
    us, _ = units(ch, True)
    worst = None
    bad = []
    for K in us:
        sl = ext_slack(ch, K) if EXT else 6 * len(K) - sum(cost[P] for P in K)
        single_x = len(K) == 1 and "".join(point_type(ch.st[next(iter(K))])) == "BNNBNN"
        if sl < 0 or (sl == 0 and (EXT or not single_x)):
            bad.append((str(sl), len(K), sorted("".join(point_type(ch.st[P])) + ":" + "".join(sorted(sig[P])) for P in K)))
        worst = sl if worst is None else min(worst, sl)
    nm = sum(1 for s in st.values() if s == "M")
    ni = sum(1 for s in st.values() if s == "I")
    return (worst if worst is not None else F(99)), nm, ni, bad


EXT = "--ext" in sys.argv
if EXT:
    sys.argv.remove("--ext")


def main():
    out, seed, steps, mode = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    starts = sys.argv[5:]
    rng = random.Random(seed)
    fh = open(out, "a")
    stats = collections.Counter()
    for s in starts:
        a = Arr(json.load(open(s))["gens"])
        n = a.n
        cur = evaluate(a)
        for it in range(steps):
            w = random_move(a, rng, p_collapse=0.4, p_expand=0.2)
            if w is None:
                continue
            b = Arr(w, n)
            if any(len(ev) > 3 for ev in b.events):
                continue
            try:
                ev = evaluate(b)
            except (AssertionError, ValueError) as e:
                stats["eval_error"] += 1
                continue
            stats["states"] += 1
            if ev[3]:
                stats["BAD"] += 1
                fh.write(json.dumps(dict(n=n, gens=w, T=b.T(), k=len(b.triples), bad=ev[3])) + "\n")
                fh.flush()
            if mode == "random":
                a, cur = b, ev
            else:
                # strict hill-climb on the smallest unit slack; ties broken toward more mutual pairs / I blocks;
                # restart from the start arrangement when stuck
                key_b = (ev[0], -ev[1], -ev[2])
                key_a = (cur[0], -cur[1], -cur[2])
                if key_b <= key_a:
                    a, cur = b, ev
                    stuck = 0
                else:
                    stuck = locals().get("stuck", 0) + 1
                    if stuck > 400:
                        a = Arr(json.load(open(s))["gens"])
                        cur = evaluate(a)
                        stuck = 0
            if it % 2000 == 0:
                print(f"{s[-30:]} it {it} T {a.T()} k {len(a.triples)} minslack {cur[0]} M {cur[1]} I {cur[2]} {dict(stats)}",
                      flush=True)
    print("done", dict(stats))


if __name__ == "__main__":
    main()

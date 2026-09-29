"""Diagnostic / lemma L3 by SAT: in an arrangement of n pseudolines (triple points allowed, no 4-fold point), a clean
line (no triple point on it, caps no block) receives a portion (own unused bounded segment or a touch).
Query: exists an arrangement where line 0 is clean and p_0 = 0. Expected UNSAT for even n (BBL's end argument), SAT
for odd n.

    python search/l3_sat.py <n> [--solver cadical195]
"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.append(str(ROOT / "work/t3"))
from unit_sat import UnitModel  # noqa: E402


def build(n):
    m = UnitModel(n, closure=False)
    f, R = m.f, range(n)
    usg, zp, zl, Bk = m.usg, m.zp, m.zl, m.Bk
    f.add([-zl[0]])                                          # no triple point on line 0
    for l in R:
        if l != 0:
            for d in (1, -1):
                f.add([-Bk[l, 0, d]])                        # line 0 caps no block
    for i in R:
        for j in R:
            if i != j and 0 not in (i, j):
                f.add([-usg[0, i, j]])                       # no own unused segment
    for M in R:
        if M == 0:
            continue
        for j in R:
            if j in (0, M):
                continue
            for (i, k) in ((0, j), (j, 0)):
                f.add([-usg[M, i, k], zp[M, 0]])             # no touch on 0 (unused segment of M, simple end on 0)
    return m


def add_positions(m, alternation=False):
    """position layer for line 0 (all its crossings simple): pos[i][k] = the k-th crossing of line 0 is with line i;
    side[k] = the triangle over segment k (between crossings k and k+1) lies above line 0. Optional alternation clauses
    (valid for a clean line: two consecutive segments never carry triangles on the same side)."""
    from unit_sat import _tot
    f, n, R = m.f, m.n, range(m.n)
    oth = [i for i in R if i != 0]
    ge = {}
    for i in oth:
        lits = [m.before(0, j, i) for j in oth if j != i]
        up = _tot(f, lits, n - 1, True)
        dn = _tot(f, lits, n - 1, False)
        for k in range(1, n - 1):
            v = f.new()
            if k - 1 < len(up):
                f.add([-up[k - 1], v])
            if k - 1 < len(dn):
                f.add([-v, dn[k - 1]])
            else:
                f.add([-v])
            ge[i, k] = v
    pos = {}
    for i in oth:
        for k in range(n - 1):
            a = ge[i, k] if k >= 1 else f.TRUE
            b = ge.get((i, k + 1), None)
            pos[i, k] = f.AND([a, -b]) if b is not None else a
    for k in range(n - 1):
        f.add([pos[i, k] for i in oth])
    side, used = {}, {}
    for k in range(n - 2):
        ups, dns = [], []
        for i in oth:
            for j in oth:
                if i == j:
                    continue
                t = m.tri3(0, i, j)
                ups.append(f.AND([pos[i, k], pos[j, k + 1], t, m.before(i, 0, j)]))
                dns.append(f.AND([pos[i, k], pos[j, k + 1], t, -m.before(i, 0, j)]))
        side[k] = f.OR(ups)
        used[k] = f.OR(ups + dns)
    if alternation:
        for k in range(n - 3):
            f.add([-side[k], -side[k + 1], -used[k], -used[k + 1]])
            f.add([side[k], side[k + 1], -used[k], -used[k + 1]])
    return pos, side, used


def main():
    n = int(sys.argv[1])
    solver = sys.argv[sys.argv.index("--solver") + 1] if "--solver" in sys.argv else "cadical195"
    t0 = time.time()
    m = build(n)
    if "--pos" in sys.argv or "--alt" in sys.argv:
        add_positions(m, "--alt" in sys.argv)
    if "--fixorder" in sys.argv:          # diagnostic only (not WLOG): line 0 meets lines 1, 2, ..., n-1 in this order
        for i in range(1, n - 1):
            m.f.add([m.before(0, i, i + 1)])
    if "--randorder" in sys.argv:         # diagnostic: a random crossing order on line 0 (may be unrealizable)
        import random
        rng = random.Random(int(sys.argv[sys.argv.index("--randorder") + 1]))
        sig = list(range(1, n))
        rng.shuffle(sig)
        for x, y in zip(sig, sig[1:]):
            m.f.add([m.before(0, x, y)])
    from pysat.solvers import Solver
    s = Solver(name=solver, bootstrap_with=list(m.f.clauses()))
    t1 = time.time()
    r = s.solve()
    print(f"n={n}: {'SAT' if r else 'UNSAT'}  build {t1 - t0:.1f}s solve {time.time() - t1:.1f}s  vars {m.f.nv}",
          flush=True)


if __name__ == "__main__":
    main()

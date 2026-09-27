"""Exhaust "fixed base + 2 free lines" with SAT.

Base: a gallery arrangement on n-2 lines, as a wiring-diagram word (labels = slope order).
Two new pseudolines A < B are slotted into the slope order at every pair of positions;
the base's chi is passed as solver assumptions, and the chi of every triple involving
A or B is free (3-valued, so the new lines may pass through base crossings and make
triple or higher points). The CNF is the concurrency-allowing relaxation
(kobon_sat.build_general without its symmetry clause), so UNSAT for every position
pair means: no arrangement of straight lines -- indeed no pseudolines -- with >= T
triangles contains this base once two lines are deleted.

    uv run --no-project --with python-sat python search/base2.py selftest
    uv run --no-project --with python-sat python search/base2.py run <T> <out.jsonl> <base.json>... [--workers W]
"""
import json
import sys
import time
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "work" / "research2"))
sys.path.insert(0, str(HERE.parent / "tools" / "external" / "kobon-solutions"))
from kobon_sat import build_general, count_general  # noqa: E402


def chi_from_word(gens, n):
    """Wire labels = initial slots (slope order); g = adjacent swap, g* = 3-wire reversal.
    (Same construction as work/research2/regress_chi.py.)"""
    wires = list(range(n))
    slot_of = list(range(n))
    chi = {}
    for tok in gens.split():
        g = int(tok.rstrip("*"))
        w = 3 if tok.endswith("*") else 2
        block = wires[g:g + w]
        for i, k in combinations(sorted(block), 2):
            for j in range(i + 1, k):
                chi[i, j, k] = 0 if j in block else (1 if g > slot_of[j] else -1)
        block.reverse()
        wires[g:g + w] = block
        for s in range(g, g + w):
            slot_of[wires[s]] = s
    return chi


def value_lits(z, p, t, v):
    return [z[t]] if v == 0 else ([-z[t], p[t]] if v == 1 else [-z[t], -p[t]])


_state = {}


def init(n, target):
    cnf, z, p, tri = build_general(n, target)
    cnf.clauses.pop()  # drop the 180-degree symmetry clause: the base fixes orientation itself
    _state.update(solver=Solver(name="cadical195", bootstrap_with=cnf.clauses), z=z, p=p, n=n, target=target)


def assumptions_for(base_chi, positions):
    n, z, p = _state["n"], _state["z"], _state["p"]
    labels = [x for x in range(n) if x not in positions]  # base line i -> labels[i]
    lits = []
    for (i, j, k), v in base_chi.items():
        lits += value_lits(z, p, (labels[i], labels[j], labels[k]), v)
    return lits


def solve_base(args):
    name, base_chi = args
    n = _state["n"]
    t0 = time.time()
    sat_positions = []
    for positions in combinations(range(n), 2):
        if _state["solver"].solve(assumptions=assumptions_for(base_chi, positions)):
            model = set(l for l in _state["solver"].get_model() if l > 0)
            chi = {t: (0 if _state["z"][t] in model else (1 if _state["p"][t] in model else -1)) for t in _state["z"]}
            sat_positions.append({"positions": positions, "recount": len(count_general(n, chi))})
            break  # one witness is enough for this base
    return {"base": name, "sat": sat_positions, "seconds": round(time.time() - t0, 1)}


def load_base(path):
    d = json.loads(Path(path).read_text())
    gens = d["gens"]
    n = 1 + max(int(t.rstrip("*")) + (2 if t.endswith("*") else 1) for t in gens.split()) - 1
    return gens, n


def selftest():
    """Delete two lines from a real 18-line 93 and check the solver rebuilds a 93 around the rest."""
    import glob
    g18 = sorted(glob.glob(str(HERE.parent / "tools/external/kobon-solutions/gallery/data/18/*.json")))[0]
    gens = json.loads(Path(g18).read_text())["gens"]
    chi18 = chi_from_word(gens, 18)
    print("gallery 18 file:", Path(g18).name, "recount:", len(count_general(18, chi18)))
    init(18, 93)
    for drop in [(0, 17), (3, 9), (5, 6)]:
        keep = [x for x in range(18) if x not in drop]
        base = {(a, b, c): chi18[keep[a], keep[b], keep[c]] for a, b, c in combinations(range(16), 3)}
        t0 = time.time()
        ok = _state["solver"].solve(assumptions=assumptions_for(base, drop))
        print(f"  delete lines {drop}: rebuild 93 at the true positions -> {'SAT' if ok else 'UNSAT (BUG)'} ({time.time() - t0:.1f}s)")
    init(18, 94)
    keep = [x for x in range(18) if x not in (0, 17)]
    base = {(a, b, c): chi18[keep[a], keep[b], keep[c]] for a, b, c in combinations(range(16), 3)}
    t0 = time.time()
    ok = _state["solver"].solve(assumptions=assumptions_for(base, (0, 17)))
    print(f"  same base, target 94 at those positions -> {'SAT' if ok else 'UNSAT'} ({time.time() - t0:.1f}s)")


def main():
    if sys.argv[1] == "selftest":
        selftest()
        return
    target, out = int(sys.argv[2]), Path(sys.argv[3])
    files = [a for a in sys.argv[4:] if not a.startswith("--")]
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 8
    files = [f for f in files if f != str(workers)]
    jobs = []
    for f in files:
        gens, _ = load_base(f)
        nb = 16
        jobs.append((Path(f).stem, chi_from_word(gens, nb)))
    with Pool(workers, initializer=init, initargs=(nb + 2, target)) as pool, out.open("a") as fh:
        for r in pool.imap_unordered(solve_base, jobs):
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            if r["sat"]:
                print("SAT witness:", r, flush=True)


if __name__ == "__main__":
    main()

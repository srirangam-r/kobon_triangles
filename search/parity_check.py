"""Soundness check of the redundant lemmas in search/parity_lemmas.py: with chi fixed to a real arrangement, the model
plus the lemma clauses must stay satisfiable. Uses assumptions, so one model per n serves many arrangements.

    python search/parity_check.py <in>... [--per-n K]
"""
import collections
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.append(str(ROOT / "work/t3"))
import unit_sat  # noqa: E402
from unit_sat import UnitModel, ref_word_chi  # noqa: E402
unit_sat._ref_imports()
from parity_lemmas import add_parity_lemmas, add_general_parity, add_general_ends  # noqa: E402
from cluster import records  # noqa: E402


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    per = int(sys.argv[sys.argv.index("--per-n") + 1]) if "--per-n" in sys.argv else 10 ** 9
    per = per if "--per-n" not in args else per
    byn = collections.defaultdict(list)
    for inp in args:
        if inp.isdigit():
            continue
        for r in records(inp):
            g = r["gens"] if isinstance(r["gens"], str) else " ".join(r["gens"])
            n = r.get("n") or (1 + max(int(t.rstrip("*")) + 1 + t.count("*") for t in g.split()))
            if "**" in g:
                continue
            if len(byn[n]) < per:
                byn[n].append(g)
    from pysat.solvers import Solver
    tot = bad = 0
    for n in sorted(byn):
        t0 = time.time()
        m = UnitModel(n, closure=False)
        add_parity_lemmas(m)
        add_general_parity(m)
        add_general_ends(m)
        s = Solver(name="cadical195", bootstrap_with=list(m.f.clauses()))
        nb = 0
        for g in byn[n]:
            chi = ref_word_chi(g, n)
            ok = s.solve(assumptions=m.chi_lits(chi))
            tot += 1
            if not ok:
                bad += 1
                nb += 1
                print("LEMMA VIOLATED", n, g, flush=True)
        print(f"n={n}: {len(byn[n])} arrangements, {nb} violations ({time.time() - t0:.0f}s)", flush=True)
    print(f"TOTAL {tot} arrangements, {bad} violations")


if __name__ == "__main__":
    main()

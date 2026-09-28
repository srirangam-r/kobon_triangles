"""Symmetric constructive search (not a proof tool): the pseudoline model kobon_sat.build_defect(n, target, KMAX)
plus invariance chi = g.chi for each generator g of an end-circle symmetry group (search/symmetry.py).
A combinatorial symmetry of a line arrangement (rotation, reflection) is such an action, so a symmetric T >= target
arrangement satisfies the CNF (the model's chi(0,1,2) != -1 break is compatible: -chi is symmetric too).
Generators: R<s> = Action(start=s) (rotation: ends shifted by s), M<s> = Action(start=s, mirror=True).
Writes the CNF; solve with kissat. Decode a model with --decode <cnf> <kissat stdout>.

    uv run --no-project --with python-sat python search/sym94.py <n> <target> <gens,comma> <out.cnf> [kmax]
"""
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kobon_sat import build_defect  # noqa: E402
from symmetry import Action  # noqa: E402


def parse(g):
    return Action(start=int(g[1:]), mirror=(g[0] == "M"))


def main():
    n, target, gens, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3].split(","), sys.argv[4]
    kmax = int(sys.argv[5]) if len(sys.argv) > 5 else 3 * n
    cnf, z, pz, ng, tri, budget = build_defect(n, target, kmax, alternate=True, card="cardnetwrk")
    assert budget >= n, "line-0 rules of build_defect would conflict with symmetry"
    val = {0: z, 1: pz, -1: ng}
    for g in gens:
        for t, (src, f) in parse(g).signed_map(n).items():  # chi[t] = f * chi[src]
            for v in (0, 1, -1):
                a, b = val[v][t], val[f * v][src]
                if a != b:
                    cnf.extend([[-a, b], [a, -b]])
    cnf.to_file(out)
    print(f"{out}: n={n} target={target} gens={gens} vars {cnf.nv} clauses {len(cnf.clauses)}")


if __name__ == "__main__":
    main()

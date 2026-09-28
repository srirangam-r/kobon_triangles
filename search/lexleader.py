"""Optional lex leaders for the three-one-hot chi encoding in build_defect.

Order is 0 < +1 < -1, NOT numeric order: orbit minima then satisfy
chi(0,1,2) != -1, since the half-turn negates all nonzero signs.
Default to the line-0 stabilizer. Full-group use requires that the rest
of the caller's formula has no additional label-specific constraints.
"""
from itertools import combinations

from symmetry import actions

VALUE_ORDER = (0, 1, -1)


def lex_leader_holds(chi, n, prefix, *, fixed_line0=True):
    """Reference predicate, for tests (not an arrangement scoring function)."""
    triples = list(combinations(range(n), 3))[:prefix]
    rank = {v: i for i, v in enumerate(VALUE_ORDER)}
    lhs = tuple(rank[chi[t]] for t in triples)
    return all(lhs <= tuple(rank[g.apply(chi, n)[t]] for t in triples)
               for g in actions(n, fixed_line0=fixed_line0))


def add_lex_leaders(cnf, z, positive, negative, prefix, *, fixed_line0=True):
    """Append equivalence-based prefix comparisons; return allocation metadata.

    Assumes exactly one of z[t],positive[t],negative[t] for each triple.
    Uses cnf.pool when supplied; reserves above BOTH its top and cnf.nv.
    Caller must use the same pool afterwards (or start above cnf.nv).
    prefix=0 is a literal no-op. No existing clauses are changed.
    """
    if not isinstance(prefix, int) or isinstance(prefix, bool) or prefix < 0:
        raise ValueError("prefix must be a nonnegative integer")
    n = 1 + max(max(t) for t in z)
    triples = list(combinations(range(n), 3))
    if set(z) != set(triples) or set(positive) != set(z) or set(negative) != set(z):
        raise ValueError("expected complete triple dictionaries")
    if prefix > len(triples):
        raise ValueError("prefix exceeds number of triples")
    before = cnf.nv
    clauses_before = len(cnf.clauses)
    if prefix == 0:
        return dict(prefix=0, comparisons=0, new_variables=0, new_clauses=0)
    from pysat.formula import IDPool
    pool = getattr(cnf, "pool", None)
    if pool is None:
        pool = IDPool(start_from=before + 1)
        cnf.pool = pool
    if pool.top < before:
        pool.occupy(pool.top + 1, before)
    allocation_start = max(before, pool.top)
    codes = {0: z, 1: positive, -1: negative}
    comparisons = 0
    for g in actions(n, fixed_line0=fixed_line0):
        mapping = g.signed_map(n)
        selected = triples[:prefix]
        if all(mapping[t] == (t, 1) for t in selected):
            continue
        comparisons += 1
        previous = None  # empty prefix is equal
        for index, t in enumerate(selected):
            src, factor = mapping[t]
            lhs = [codes[v][t] for v in VALUE_ORDER]
            rhs = [codes[factor*v][src] for v in VALUE_ORDER]
            guard = [] if previous is None else [-previous]
            for i in range(3):
                for j in range(i):
                    cnf.append(guard + [-lhs[i], -rhs[j]])
            if index + 1 == len(selected):
                break
            equal = pool.id(("lexleader", allocation_start, comparisons, index))
            if previous is not None:
                cnf.append([-equal, previous])
            for x, y in zip(lhs, rhs):
                cnf.append([-equal, -x, y])
                cnf.append(guard + [-x, -y, equal])
            previous = equal
    return dict(prefix=prefix, comparisons=comparisons,
                new_variables=max(before, pool.top) - allocation_start,
                new_clauses=len(cnf.clauses) - clauses_before,
                fixed_line0=fixed_line0)

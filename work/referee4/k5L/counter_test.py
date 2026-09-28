"""Referee (AUDIT_k5L): brute-force the two counters of search/k5L_layer.py.
counter(): out[j] <-> (sum >= j) for every input assignment; upper(): (sum >= j) -> out[j], and out[j] can be
false whenever sum < j (so -ZR[Zmax+1] is satisfiable iff sum s <= Zmax)."""
import sys
from itertools import product
sys.path.insert(0, '/home/nail/stuff/sundai_math/search')
from k5L_layer import counter, upper
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver
bad = 0; cases = 0
for m in range(1, 7):
    for K in range(1, 5):
        for fn in ('counter', 'upper'):
            pool, cnf = IDPool(), CNF()
            xs = [pool.id(('x', i)) for i in range(m)]
            out = (counter if fn == 'counter' else upper)(cnf, pool, xs, K, 'c')
            with Solver(bootstrap_with=cnf.clauses) as sv:
                for bits in product((0, 1), repeat=m):
                    asm = [x if b else -x for x, b in zip(xs, bits)]; s = sum(bits)
                    for j in range(1, K + 1):
                        cases += 1
                        can_t, can_f = sv.solve(assumptions=asm + [out[j]]), sv.solve(assumptions=asm + [-out[j]])
                        want = (s >= j, s < j) if fn == 'counter' else (True, s < j)
                        if (can_t, can_f) != want: bad += 1; print('BAD', fn, m, K, bits, j, can_t, can_f)
print('cases', cases, 'bad', bad, 'PASS' if bad == 0 else 'FAIL')

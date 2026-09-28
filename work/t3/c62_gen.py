"""SAT-generated test arrangements for the C62-C65 lemma tests (work/t3/c62_tests.check).
Premise families (labels 0..4 = the five triple points of the small-n base in c62_local_sat.py):
  2F3 : 2-F face (0,1,2), 0 and 1 type X, 2 one block, and a third bridge 2-3        (lemma G, e(Q) = 3)
  2F  : 2-F face (0,1,2) with 0, 1 type X and 2 one block                            (lemma G premise)
  twinX: twin faces (0,2,3), (1,2,3) with 0 type X                                  (lemma T controls)
  bent : a bent point 0 whose partner 1 lies in a face (1,2,3)                        (lemma BP controls)
Each model is decoded to a wiring word, checked, then blocked (clause on its triangle set).
    uv run --no-project --with python-sat python work/t3/c62_gen.py N FAMILY COUNT"""
import sys, time, random
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/t3')
import c62_local_sat as M
from pysat.solvers import Solver
from collections import Counter
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee')
from arr import from_tokens
sys.path.append('/home/nail/stuff/sundai_math/work/t3')
from c62_tests import check

n, fam, cnt = int(sys.argv[1]), sys.argv[2], int(sys.argv[3])
cnf, pool, g = M.base(n)
ids = M.add_labels(cnf, pool, n, g['z'], g['tri'], g['blk'], g['F'], g['G'], nlab=5)
I = lambda name, *k: ids[name][",".join(map(str, k))]
X = lambda i: [I('GE2', i), I('AX', i)]
O1 = lambda i: [I('GE1', i), -I('GE2', i)]
fams = {
    '2F3': X(0) + X(1) + O1(2) + [I('BR', 0, 1), I('BR', 0, 2), I('BR', 1, 2), I('FC', 0, 1, 2), I('BR', 2, 3)],
    '2F': X(0) + X(1) + O1(2) + [I('BR', 0, 1), I('BR', 0, 2), I('BR', 1, 2), I('FC', 0, 1, 2)],
    'twinX': X(0) + [I('FC', 0, 2, 3), I('FC', 1, 2, 3)],
    'bent': [I('GE2', 0), -I('AX', 0), I('BR', 0, 1), I('FC', 1, 2, 3)],
}
units = fams[fam]
st, bad = Counter(), []
with Solver(name='cadical153', bootstrap_with=cnf.clauses) as sv:
    for it in range(cnt):
        t = time.time()
        if not sv.solve(assumptions=units):
            print(it, 'UNSAT', f'{time.time()-t:.1f}s', flush=True); break
        m = sv.get_model()
        toks = M.decode(n, m, g)
        A = from_tokens(toks, n, complete=False)
        check(A, st, bad, f'{fam}{it}')
        pos = set(x for x in m if x > 0)
        sv.add_clause([-v if v in pos else v for v in g['tri'].values()] + [-v if v in pos else v for v in g['z'].values()])
        print(it, 'SAT', f'{time.time()-t:.1f}s', ' '.join(toks), flush=True)
for k in sorted(st, key=str): print(st[k], k)
print('FAILS', len(bad))
for b in bad[:20]: print('  ', b)

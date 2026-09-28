"""Lemma-level small-n SAT checks for C62-C65 on the exact base of c62_local_sat.py (5 triple points,
labels 0..4). Each lemma premise+negated-conclusion must be UNSAT; each control (a weakened premise) should be SAT
at some n, which shows the premise is not vacuous at that n.
    uv run --no-project --with python-sat python work/t3/c62_lemma_sat.py N [test ...]"""
import sys
import time
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/t3')
import c62_local_sat as M  # noqa: E402
from pysat.solvers import Solver  # noqa: E402

n = int(sys.argv[1])
only = sys.argv[2:]
cnf, pool, g = M.base(n)
ids = M.add_labels(cnf, pool, n, g['z'], g['tri'], g['blk'], g['F'], g['G'], nlab=5)
I = lambda name, *k: ids[name][",".join(map(str, k))]
bL = lambda i, a, C: pool.id(('LblkL', i, a, C))
lab = lambda i, L: pool.id(('Ll', i, L))


def capthru(i, j):
    """some block of label i has its cap line through label j"""
    v = pool.id(('capthru', i, j))
    ws = []
    for x in range(n):
        for C in range(n):
            if C != x:
                w = pool.id(('ctw', i, j, x, C))
                cnf.extend([[-w, bL(i, x, C)], [-w, lab(j, C)]])
                ws.append(w)
    cnf.append([-v] + ws)
    return v


def allcapsthru(i, j):
    """every block of label i has its cap line through label j"""
    v = pool.id(('allcaps', i, j))
    for x in range(n):
        for C in range(n):
            if C != x:
                cnf.append([-v, -bL(i, x, C), lab(j, C)])
    return v


def covers(i, j):
    """label i has a block whose cap triangle has vertex j: block line a, line L = ij, cap C through j, tri(a,L,C)"""
    v = pool.id(('covers', i, j))
    ws = []
    for a in range(n):
        for C in range(n):
            if C == a:
                continue
            for L in range(n):
                if L in (a, C):
                    continue
                w = pool.id(('covw', i, j, a, C, L))
                cnf.extend([[-w, bL(i, a, C)], [-w, lab(i, L)], [-w, lab(j, L)], [-w, lab(j, C)],
                            [-w, g['tri'][M.S(a, L, C)]]])
                ws.append(w)
    cnf.append([-v] + ws)
    return v


X = lambda i: [I('GE2', i), I('AX', i)]
O1 = lambda i: [I('GE1', i), -I('GE2', i)]
V = lambda i: [I('GE2', i), -I('AX', i)]
face2F = X(0) + X(1) + O1(2) + [I('FC', 0, 1, 2)]
tests = {
    # C65 (converging caps)
    'C65 two vertices cover toward the third (UNSAT)': lambda: [I('FC', 0, 1, 2), covers(0, 2), covers(1, 2)],
    'C65 face with two type-X vertices (UNSAT)': lambda: [I('FC', 0, 1, 2)] + X(0) + X(1),
    'C65 control: one vertex covers toward the third': lambda: [I('FC', 0, 1, 2), covers(0, 2)],
    'C65 control: covers toward different vertices': lambda: [I('FC', 0, 1, 2), covers(0, 2), covers(1, 0)],
    'C65 control: face with one type-X vertex': lambda: [I('FC', 0, 1, 2)] + X(0),
    # C62
    'C62 crossed caps (UNSAT)': lambda: [I('FC', 0, 2, 3), I('FC', 1, 2, 3), capthru(0, 2), capthru(1, 3)],
    'C62 control: parallel caps': lambda: [I('FC', 0, 2, 3), I('FC', 1, 2, 3), capthru(0, 2), capthru(1, 2)],
    'C62 control: one X third vertex': lambda: X(0) + [I('FC', 0, 2, 3), I('FC', 1, 2, 3)],
    # C63
    'C63 fan with a block (UNSAT)': lambda: [I('FC', 0, 1, 2), I('FC', 0, 2, 3), I('FC', 0, 3, 4), I('BR', 0, 1), I('BR', 0, 4), I('GE1', 0)],
    'C63 control: fan, blockless': lambda: [I('FC', 0, 1, 2), I('FC', 0, 2, 3), I('FC', 0, 3, 4), I('BR', 0, 1), I('BR', 0, 4)],
    'C63 control: fan, one outer bridge, block': lambda: [I('FC', 0, 1, 2), I('FC', 0, 2, 3), I('FC', 0, 3, 4), I('BR', 0, 1), I('GE1', 0)],
    # C64
    'C64 bent partner in face (UNSAT)': lambda: V(0) + [allcapsthru(0, 1), I('FC', 1, 2, 3), I('BR', 1, 2), I('BR', 1, 3)],
    'C64 control: one face side doubly used': lambda: V(0) + [allcapsthru(0, 1), I('FC', 1, 2, 3), I('BR', 1, 2)],
    'C64 control: bent point': lambda: V(0) + [allcapsthru(0, 1)],
    # C65
    '2-F face + bridge to a type-X U (UNSAT, C65)': lambda: face2F + [I('BR', 2, 3)] + X(3),
    '2-F face + bridge to a one-block U (UNSAT, C65)': lambda: face2F + [I('BR', 2, 3)] + O1(3),
    '2-F face with e(Q)=4 (UNSAT, C65)': lambda: face2F + [I('BR', 2, 3), I('BR', 2, 4)],
    '2-F face (UNSAT, C65)': lambda: face2F,
}
units = {k: f() for k, f in tests.items() if not only or any(o in k for o in only)}
with Solver(name='cadical153', bootstrap_with=cnf.clauses) as sv:
    for name, u in units.items():
        t = time.time()
        r = sv.solve(assumptions=u)
        line = f'n={n} {name}: {"SAT" if r else "UNSAT"} ({time.time() - t:.1f}s)'
        if r:
            try:
                line += ' word: ' + ' '.join(M.decode(n, sv.get_model(), g))
            except Exception as ex:  # noqa: BLE001
                line += f' decode failed {ex!r}'
        print(line, flush=True)

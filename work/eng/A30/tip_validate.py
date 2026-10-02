"""A30: validate tip_cnf.py axioms/statement predicates against exact real line arrangements.
For each real arrangement: (1) fix all sl/lt/gt variables to their true values -> axioms must be SAT (necessity);
(2) each statement predicate (triangle face, end-at-tip, concurrency) must be SAT under the assumptions iff it is
geometrically true (exact rational arithmetic)."""
import sys, random, itertools, copy
from pysat.formula import CNF
from fractions import Fraction as F
sys.path.insert(0, __import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + '/work/eng/A30')
import tip_cnf as T
from pysat.solvers import Solver

rnd = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
NREAL = int(sys.argv[2]) if len(sys.argv) > 2 else 300

def line_through(p, q):
    (x1, y1), (x2, y2) = p, q
    if x1 == x2: return None
    s = F(y2 - y1) / (x2 - x1)
    return (s, y1 - s * x1)          # y = s x + k

def mk_flower(kind):
    # directions d_i at roughly increasing angles
    if kind == 'convex':
        dirs = [(rnd.randint(4, 12), rnd.randint(0, 3)), (rnd.randint(1, 6), rnd.randint(3, 8)), (-rnd.randint(1, 6), rnd.randint(3, 8))]
        ts = [rnd.randint(1, 9) for _ in range(6)]
        P = []
        for i in range(6):
            d = dirs[i % 3]
            sg = 1 if i < 3 else -1
            P.append((sg * ts[i] * d[0], sg * ts[i] * d[1]))
    else:  # fully random
        dirs = [(rnd.randint(-9, 9), rnd.randint(-9, 9)) for _ in range(3)]
        P = []
        for i in range(6):
            t = rnd.choice([-1, 1]) * rnd.randint(1, 9)
            d = dirs[i % 3]
            P.append((t * d[0], t * d[1]))
    sh = rnd.randint(-5, 5); sh2 = rnd.randint(-5, 5)
    tr = lambda p: (p[0] + sh * p[1], p[1] + sh2 * p[0] + 0 * p[1])
    O = (0, 0)
    pts = [tr(p) for p in P]
    m = [line_through((0, 0), pts[i]) for i in range(3)]
    l = [line_through(pts[i], pts[(i + 1) % 6]) for i in range(6)]
    lines = m + l
    if any(x is None for x in lines): return None
    sl = [x[0] for x in lines]
    if len(set(sl)) < 9: return None
    return lines

def mk_random(kind):
    # random lattice-ish lines with many concurrencies
    lines = []
    pts = [(rnd.randint(-4, 4), rnd.randint(-4, 4)) for _ in range(6)]
    tries = 0
    while len(lines) < 9 and tries < 100:
        tries += 1
        p, q = rnd.sample(pts, 2) if rnd.random() < 0.8 else ((rnd.randint(-4, 4), rnd.randint(-4, 4)), rnd.choice(pts))
        ln = line_through(p, q)
        if ln is None: continue
        if ln in lines or any(ln[0] == x[0] for x in lines): continue
        lines.append(ln)
    return lines if len(lines) == 9 else None

def crossx(la, lb):   # x coordinate of crossing
    return (lb[1] - la[1]) / (la[0] - lb[0])

def geom(lines):
    """returns dict of truth values"""
    n = 9
    X = {(a, b): crossx(lines[a], lines[b]) for a in range(n) for b in range(n) if a != b}
    return X

def has4(X):
    for r in range(9):
        for grp in itertools.combinations([i for i in range(9) if i != r], 3):
            if X[r, grp[0]] == X[r, grp[1]] == X[r, grp[2]]: return True
    return False

def assumptions(e, lines, X):
    A = []
    for x, y in itertools.combinations(range(9), 2):
        A.append(e.sl[x, y] if lines[x][0] < lines[y][0] else -e.sl[x, y])
    for (r, b, c), v in e.lt.items():
        xb, xc = X[r, b], X[r, c]
        A.append(v if xb < xc else -v)
        A.append(e.gt[r, b, c] if xb > xc else -e.gt[r, b, c])
    return A

def tri_truth(lines, p, q, r):
    verts = []
    for a, b in ((p, q), (p, r), (q, r)):
        x = crossx(lines[a], lines[b]); y = lines[a][0] * x + lines[a][1]
        verts.append((x, y))
    if len(set(verts)) < 3: return False
    # sides must be unbroken: no other line strictly separates two vertices
    for d in range(9):
        if d in (p, q, r): continue
        vals = [lines[d][0] * x + lines[d][1] - y for x, y in verts]
        if any(v > 0 for v in vals) and any(v < 0 for v in vals): return False
    return True

def end_truth(lines, X, A, Y, Q, simple):
    if X[A, Q] == X[A, Y]: return False
    fwd = X[A, Q] < X[A, Y]
    for d in range(9):
        if d in (A, Y, Q): continue
        if fwd and X[A, d] > X[A, Y]: return False
        if (not fwd) and X[A, d] < X[A, Y]: return False
        if simple and X[A, d] == X[A, Y]: return False
    return True

NACT = [0]
stats = dict(arr=0, axiom_fail=0, tri=[0, 0], end=[0, 0], mismatch=0, both_ends=0, conc_true=0)
for it in range(NREAL):
    kind = rnd.choice(['convex', 'convex', 'rand', 'lattice'])
    lines = mk_flower(kind) if kind != 'lattice' else mk_random(kind)
    if lines is None: continue
    X = geom(lines)
    if has4(X): continue
    stats['arr'] += 1
    e0 = T.Enc()
    A = assumptions(e0, lines, X)
    with Solver(name='cadical195', bootstrap_with=e0.cnf.clauses) as s:
        if not s.solve(assumptions=A):
            stats['axiom_fail'] += 1; print('AXIOM FAIL', kind, lines); continue
    if kind == 'lattice':
        continue
    sol = Solver(name='cadical195', bootstrap_with=e0.cnf.clauses)
    # statement predicates
    def check(build, truth, key):
        scratch = copy.copy(e0); scratch.cnf = CNF(); build(scratch)
        act = e0.nv + 1 + NACT[0]; NACT[0] += 1
        for c in scratch.cnf.clauses: sol.add_clause(c + [-act])
        sat = sol.solve(assumptions=A + [act])
        sol.add_clause([-act])
        stats[key][0 if truth else 1] += 1
        if sat != truth:
            stats['mismatch'] += 1; print('MISMATCH', key, truth, sat, lines)
    # flower concurrency truth
    def conc(x, y, z): return X[x, y] == X[x, z]
    if not (conc(0, 1, 2) and all(conc(T.M(i), T.L(i - 1), T.L(i)) for i in range(6))):
        continue
    stats['conc_true'] += 1
    for i in range(6):
        check(lambda e, i=i: e.triangle_face(T.M(i), T.M(i + 1), T.L(i)), tri_truth(lines, T.M(i), T.M(i + 1), T.L(i)), 'tri')
    endt = {}
    for j in range(6):
        for mirror in (False, True):
            for simple in (False, True):
                Ax, Yx, Qx = (T.L(j - 1), T.L(j + 1), T.L(j)) if not mirror else (T.L(j + 1), T.L(j - 1), T.L(j))
                tr = end_truth(lines, X, Ax, Yx, Qx, simple)
                endt[j, mirror, simple] = tr
                check(lambda e, j=j, mirror=mirror, simple=simple: e.ends_at_tip(j, mirror, simple), tr, 'end')
    # both ends together with all inner triangles true?
    if all(tri_truth(lines, T.M(i), T.M(i + 1), T.L(i)) for i in range(6)):
        for j in range(3):
            for mirror in (False, True):
                if endt[j, mirror, False] and endt[j + 3, mirror, False]:
                    stats['both_ends'] += 1; print('BOTH ENDS on real flower with 6 inner triangles!', lines)
    sol.delete()
print(stats)

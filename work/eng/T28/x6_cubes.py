"""6-X-point case (k=6, all type X, Z=0): cubes on the circular structure of the 36 line ends.
Ray p in Z_36: p<18 = left end (first vertex) of line p, p>=18 = right end (last vertex) of line p-18; the cyclic order of the
rays at infinity is p = 0..35.  Each ray is either a singleton (I-end: the line ends, the crossing line continues) or half of a
wedge (two adjacent rays whose lines end at their common vertex).  With u singletons S (u = 12 - 2m <= 6, all arcs between them
even) the complement is tiled by dominoes uniquely.  Cubes are S up to translation of Z_36 (rotating the plane).
usage: x6_cubes.py list u            -> number of classes
       x6_cubes.py run u start stride [budget] out.jsonl"""
import sys, json, time, itertools
sys.path.insert(0, __import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + '/search')
N = 36

def classes(u):
    """canonical (under translation) u-subsets of Z_36 with all gaps even; returns sorted tuples"""
    if u == 0:
        return [()]
    seen = set(); out = []
    total = N - u
    # gaps g_1..g_u (number of dominoes between consecutive singletons) sum to total/2
    half = total // 2
    def comps(k, s):
        if k == 1:
            yield (s,); return
        for a in range(s + 1):
            for rest in comps(k - 1, s - a):
                yield (a,) + rest
    for h in comps(u, half):
        pos = [0]
        for g in h[:-1]:
            pos.append(pos[-1] + 1 + 2 * g)
        S = tuple(pos)
        # canonical under translation: min over rotations of the sorted tuple
        best = min(tuple(sorted((x + t) % N for x in S)) for t in range(N))
        if best not in seen:
            seen.add(best); out.append(best)
    return sorted(out)

def dominoes(S):
    """list of (p, p+1) wedge pairs tiling the complement of S on Z_36"""
    Sset = set(S)
    if not S:
        return [(2 * i, 2 * i + 1) for i in range(N // 2)]
    doms = []
    used = set(Sset)
    for s in S:
        p = (s + 1) % N
        while p not in used:
            q = (p + 1) % N
            assert q not in used, "odd arc"
            doms.append((p, q)); used.add(p); used.add(q)
            p = (q + 1) % N
    assert len(used) == N
    return doms

def cube_clauses(M, S):
    n = M.n
    cl = []
    for (p, q) in dominoes(S):
        Lp, Lq = p % 18, q % 18
        assert Lp != Lq
        kp = 'F' if p < 18 else 'G'
        kq = 'F' if q < 18 else 'G'
        cl.append([M.ext_var(kp, Lp, Lq)])
        cl.append([M.ext_var(kq, Lq, Lp)])
    for s in S:
        L = s % 18
        kind = 'F' if s < 18 else 'G'
        cl.append([M.ext_var(kind, L, x) for x in range(n) if x != L])       # the end vertex exists
        for x in range(n):
            if x == L: continue
            cl.append([-M.ext_var(kind, L, x), -M.ext_var('F', x, L)])      # not a wedge: the crossing line does not end there
            cl.append([-M.ext_var(kind, L, x), -M.ext_var('G', x, L)])
    return cl

if __name__ == '__main__':
    if sys.argv[1] == 'list':
        for u in (0, 2, 4, 6):
            print(u, len(classes(u)))
    elif sys.argv[1] == 'run':
        u, start, stride = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        budget = int(sys.argv[5]) if len(sys.argv) > 5 and sys.argv[5] != '0' else None
        out = sys.argv[6]
        cl = classes(u)
        import flower_sat as F
        from pysat.solvers import Solver
        t0 = time.time()
        M = F.build_X6(anchor=False, flip_break=False)
        print(f'built {M.cnf.nv} vars {len(M.cnf.clauses)} clauses {time.time()-t0:.0f}s', flush=True)
        solver = Solver(name='cadical195', bootstrap_with=M.cnf.clauses)
        for idx in range(start, len(cl), stride):
            S = cl[idx]
            t1 = time.time()
            g = M.pool.id(("cubeguard", u, idx))
            for c in cube_clauses(M, S):
                solver.add_clause([-g] + c)
            if budget: solver.conf_budget(budget)
            r = solver.solve_limited(assumptions=[g]) if budget else solver.solve(assumptions=[g])
            res = {None: 'UNKNOWN', True: 'SAT', False: 'UNSAT'}[r]
            row = {'u': u, 'idx': idx, 'S': S, 'status': res, 's': round(time.time() - t1, 1)}
            if r:
                row['result'] = F.verify_model(M, solver.get_model())
                print('!!!! SAT', json.dumps(row)[:1500], flush=True)
            solver.add_clause([-g])
            open(out, 'a').write(json.dumps(row) + '\n')
            print(row['u'], idx, S, res, row['s'], flush=True)

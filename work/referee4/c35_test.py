"""Referee4: C35 splitting lemma + its SAT sector-class table, with the solver's own before() semantics.
For every triple point P = {A<B<C} (a 'g*' token of the sweep word):
  * classify each triangle face at P by the C35 table (directions of L on x and y via before(x, L, y));
  * check no triangle falls in a non-adjacent 'mixed pair';
  * resolve the triple crossing both ways ('g g+1 g' and 'g+1 g g+1'), recount T', and check
    {T'_1, T'_2} == {T + 1 - t_even, T + 1 - t_odd}.
usage: python3 c35_test.py N SEED"""
import json, random, sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee'); sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee4')
from arr import from_tokens
from mutate import simple_tris, contract, flip
from c17_test import chi_from_arr, sat_before
GAL = Path('/home/nail/stuff/sundai_math/tools/external/kobon-solutions/gallery/data')
EVEN = {frozenset([('A', 'L'), ('B', 'L')]), frozenset([('C', 'L'), ('A', 'R')]), frozenset([('B', 'R'), ('C', 'R')])}
ODD = {frozenset([('B', 'L'), ('C', 'L')]), frozenset([('A', 'R'), ('B', 'R')]), frozenset([('C', 'R'), ('A', 'L')])}


def check(A, st, bad, tag):
    n = A.n
    if any(m > 3 for m in A.mult) or A.tokens is None:
        return
    chi = chi_from_arr(A)
    before = lambda r, i, j: sat_before(chi, r, i, j)
    toks = A.tokens
    # map each triple point to its token index (events are created in token order)
    tok_of = {}
    for ti, tok in enumerate(toks):
        pass
    ev_tok = [ti for ti, tok in enumerate(toks)]  # event e = token index e (one event per token)
    for P in A.triples:
        a_, b_, c_ = sorted(A.ev[P])
        name = {a_: 'A', b_: 'B', c_: 'C'}
        te = to = 0
        for t in A.tris:
            if P not in t:
                continue
            others = [v for v in t if v != P]
            x = A.common_line(P, others[0]); y = A.common_line(P, others[1])
            L = A.common_line(others[0], others[1])
            y_on_x = [w for w in A.ev[P] if w != x][0]
            dx = 'L' if before(x, L, y_on_x) else 'R'
            x_on_y = [w for w in A.ev[P] if w != y][0]
            dy = 'L' if before(y, L, x_on_y) else 'R'
            key = frozenset([(name[x], dx), (name[y], dy)])
            if key in EVEN:
                te += 1
            elif key in ODD:
                to += 1
            else:
                bad.append(f'{tag} triangle in a non-adjacent mixed pair {sorted(key)}')
        st['points'] += 1
        # split both ways
        ti = P  # event id == token index
        tok = toks[ti]
        assert tok.endswith('*')
        g = int(tok[:-1])
        Ts = set()
        for rep in ([str(g), str(g + 1), str(g)], [str(g + 1), str(g), str(g + 1)]):
            new = toks[:ti] + rep + toks[ti + 1:]
            B = from_tokens(new, n, complete=False)
            Ts.add(B.T)
        pred = {A.T + 1 - te, A.T + 1 - to}
        if Ts != pred:
            bad.append(f'{tag} split FAIL T={A.T} te={te} to={to} got={sorted(Ts)}')
        st[('min(t_even,t_odd)', min(te, to))] += 1


def worker(args):
    wid, N, seed = args
    rng = random.Random(seed * 7919 + wid); st = Counter(); bad = []
    files = [f for s in ('10', '12', '14', '16', '18', '18-1', '20') for f in sorted((GAL / s).glob('*.json'))]
    for it in range(N):
        f = rng.choice(files); n = int(f.parent.name.split('-')[0])
        try:
            A = from_tokens(json.load(open(f))['gens'].split(), n)
            for _ in range(rng.choice([0, 1, 3, 6, 10])):
                s = simple_tris(A)
                if s: A = contract(A, rng.choice(s))
            for _ in range(rng.choice([0, 0, 2, 8])):
                s = simple_tris(A)
                if s: A = flip(A, rng.choice(s))
            A = from_tokens(A.tokens, n, complete=False)  # normalise so event id == token index
        except (ValueError, AssertionError, IndexError):
            continue
        st['arr'] += 1
        try:
            check(A, st, bad, f'w{wid}i{it}')
        except (AssertionError, ValueError, IndexError) as ex:
            bad.append(f'assert {ex!r}')
    return st, bad


if __name__ == '__main__':
    N, seed = int(sys.argv[1]), int(sys.argv[2])
    st = Counter(); bad = []
    with Pool(4) as pool:
        for s, b in pool.imap_unordered(worker, [(w, N, seed) for w in range(4)]):
            st.update(s); bad += b
    for k_ in sorted(st, key=str):
        print(st[k_], k_)
    print('FAILS', len(bad))
    for b in bad[:10]:
        print('  ', b[:200])

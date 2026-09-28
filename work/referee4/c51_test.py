"""Referee4: C51 k-fold (4-fold) split lemma on random pseudoline arrangements with 4-fold points.
Random sweeps with 2-, 3- and 4-wire reversals give arrangements with 4-fold points.  For every 4-fold
point P and each of its 4 lines, both resolutions that 'move' that line off P (leaving a triple point)
are built explicitly in the sweep word; check {T'_1, T'_2} == {T + 2 - t(G_j), T + 2 - t(G'_j)},
G_j = {s_{j-1}, s_{j+1}, s_{j+2}, s_{j+4}} with the ray order a+,b+,c+,d+,a-,b-,c-,d- (a+ = top-left wire's
left ray).  Also checks the combinatorial 'rich' claim (t = 6, all 8 gaining sets >= 3 => gaps opposite)."""
import random, sys
from collections import Counter
from itertools import combinations
from multiprocessing import Pool
sys.path.insert(0, '/home/nail/stuff/sundai_math/work/referee')
from arr import Arr


def build(tokens, n):
    """tokens: list of (g, w). Wiring diagram with generic w-wire reversals."""
    wires = list(range(n))
    ev, evg, evw, evpos = [], [], [], []
    rows = [[] for _ in range(n)]
    for g, w in tokens:
        blk = wires[g:g + w]
        assert blk == sorted(blk), 'bad token'
        pos = [0] * n
        for p, x in enumerate(wires):
            pos[x] = p
        e = len(ev)
        ev.append(frozenset(blk)); evg.append(g); evw.append(w); evpos.append(pos)
        for x in blk:
            rows[x].append(e)
        wires[g:g + w] = blk[::-1]
    assert wires == list(range(n))[::-1], 'incomplete'

    def side(e, L):
        p = evpos[e][L]
        if p < evg[e]:
            return 1
        if p >= evg[e] + evw[e]:
            return -1
        raise ValueError
    return Arr(n, ev, rows, side)


def random_sweep(n, rng, p4=0.15, p3=0.15):
    wires = list(range(n)); toks = []
    while wires != list(range(n))[::-1]:
        r = rng.random()
        w = 4 if r < p4 else (3 if r < p4 + p3 else 2)
        cands = [g for g in range(n - w + 1) if wires[g:g + w] == sorted(wires[g:g + w])]
        if not cands:
            cands = [g for g in range(n - 1) if wires[g] < wires[g + 1]]; w = 2
        g = rng.choice(cands)
        toks.append((g, w)); wires[g:g + w] = wires[g:g + w][::-1]
    return toks


def resolutions(g, q):
    """two token sequences replacing a 4-reversal at g that move the wire at block index q."""
    S = lambda o: (g + o, 2); Tr = lambda o: (g + o, 3)
    return {0: ([S(0), S(1), S(2), Tr(0)], [Tr(1), S(0), S(1), S(2)]),
            3: ([S(2), S(1), S(0), Tr(1)], [Tr(0), S(2), S(1), S(0)]),
            1: ([S(0), Tr(1), S(0), S(1)], [S(1), S(2), Tr(0), S(2)]),
            2: ([S(2), Tr(0), S(2), S(1)], [S(1), S(0), Tr(1), S(0)])}[q]


def sector_counts(A, P):
    lines = sorted(A.ev[P])            # before P: top to bottom = sorted labels
    ray_index = {}
    for k, L in enumerate(lines):
        ray_index[(L, 'left')] = k       # a+, b+, c+, d+ = left rays in label order
        ray_index[(L, 'right')] = k + 4  # a-, b-, c-, d-
    t = [0] * 8
    for tri in A.tris:
        if P not in tri:
            continue
        o = [v for v in tri if v != P]
        r = []
        for v in o:
            L = A.common_line(P, v)
            r.append(ray_index[(L, 'left' if A.idx[L][v] < A.idx[L][P] else 'right')])
        i, j = sorted(r)
        if j - i == 1:
            t[i] += 1
        elif (i, j) == (0, 7):
            t[7] += 1
        else:
            raise AssertionError('triangle at P between non-adjacent rays')
    return t


def gaining(j):
    return {(j - 1) % 8, (j + 1) % 8, (j + 2) % 8, (j + 4) % 8}


def worker(args):
    wid, N = args
    rng = random.Random(4242 + wid); st = Counter(); bad = []
    for it in range(N):
        n = rng.choice([8, 9, 10, 11, 12])
        toks = random_sweep(n, rng)
        try:
            A = build(toks, n)
        except (AssertionError, ValueError):
            st['build_error'] += 1; continue
        st['arr'] += 1
        for P, (g, w) in enumerate(toks):
            if w != 4:
                continue
            st['4fold'] += 1
            t = sector_counts(A, P)
            st[('t(P)', sum(t))] += 1
            for q in range(4):
                Ts = set()
                for seq in resolutions(g, q):
                    B = build(toks[:P] + seq + toks[P + 1:], n)
                    Ts.add(B.T)
                G = gaining(q)                  # line = block wire q, whose left ray has index q
                Gc = set(range(8)) - G
                pred = {A.T + 2 - sum(t[s] for s in G), A.T + 2 - sum(t[s] for s in Gc)}
                st['line_tests'] += 1
                if Ts != pred:
                    bad.append(f'FAIL n={n} q={q} t={t} T={A.T} got={sorted(Ts)} pred={sorted(pred)}')
    return st, bad


if __name__ == '__main__':
    # combinatorial check of the 'rich' residue claim
    parts = [(gaining(j), set(range(8)) - gaining(j)) for j in range(4)]
    for gaps in combinations(range(8), 2):
        ok = all(len(set(gaps) & G) <= 1 and len(set(gaps) & Gc) <= 1 for G, Gc in parts)
        if ok and (gaps[1] - gaps[0]) % 8 != 4:
            print('RICH CLAIM FAIL: non-opposite gaps', gaps)
    print('rich-claim check done')
    st = Counter(); bad = []
    with Pool(4) as pool:
        for s, b in pool.imap_unordered(worker, [(w, int(sys.argv[1])) for w in range(4)]):
            st.update(s); bad += b
    for k in sorted(st, key=str):
        print(st[k], k)
    print('FAILS', len(bad))
    for b in bad[:10]:
        print('  ', b)

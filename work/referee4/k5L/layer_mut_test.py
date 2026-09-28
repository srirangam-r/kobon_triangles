"""Referee (AUDIT_k5L, Q1): k5L label-layer semantics on MUTATED pseudoline arrangements rich in bent points,
bridges, O1b points, mutual apexes and line-end cap points (greedy triangle contractions of gallery arrangements,
work/referee/mutate.py).  Ground truth is computed with the independent referee toolkit work/referee/arr.py
(ray cycles, blocks, doubly used edges), NOT with the author's harness.  Model literals z/pz/ng from chi of the
sweep word, tri from the referee's face list (cross-checked against kobon_sat.count_general).
Checks per arrangement (labels fixed to the triple points):
  * two-directional GE1, GE2, AX, TB, BR: forced to the geometric value (both polarities tested);
  * one-directional FC, CPE, MUT, E2, E1: geometric truth => satisfiable with the indicator true;
  * joint: all two-directional values plus every true one-directional indicator asserted at once => SAT;
  * geometry facts: no 2-block point with blocks on adjacent rays; every block's two cap triangles share cap C;
    type map (axis->GE2&AX, bent->GE2&-AX, b1->GE1&-GE2 with TB <-> triple apex).
    uv run --no-project --with python-sat python work/referee4/k5L/layer_mut_test.py N_PER_WORKER SEED"""
import json, random, sys
from collections import Counter
from itertools import combinations, permutations
from multiprocessing import Pool
from pathlib import Path
ROOT = Path('/home/nail/stuff/sundai_math')
sys.path.insert(0, str(ROOT / 'work/referee')); sys.path.insert(0, str(ROOT / 'search'))
from arr import from_tokens
from mutate import simple_tris, contract, flip
from base2 import chi_from_word
from kobon_sat import count_general
from k5L_layer import add_labels, S
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver
GAL = ROOT / 'tools/external/kobon-solutions/gallery/data'


def info(A, P):
    cr, bl = A.blocks(P)
    br = [far for (w, d, edge, far) in cr if edge is not None and len(A.usage.get(edge, ())) == 2 and A.mult[far] >= 3]
    mids = sorted(b['i'] for b in bl)
    if len(bl) == 2:
        dd = (mids[1] - mids[0]) % 6
        typ = 'axis' if dd == 3 else ('bent' if dd in (2, 4) else 'adjacent')
    else:
        typ = {0: 'b0', 1: 'b1', 3: 'b3'}.get(len(bl), 'b%d' % len(bl))
    return cr, bl, br, typ


def truth_of(A):
    P = A.triples
    lines = [set(A.ev[e]) for e in P]
    I = {e: i for i, e in enumerate(P)}
    k = len(P)
    ends = {w: {A.rows[w][0], A.rows[w][-1]} for w in range(A.n)}
    blocks, brs, typ = {}, {}, {}
    facts = Counter()
    for i, e in enumerate(P):
        cr, bl, br, ty = info(A, e)
        blocks[i] = [(b['ray'][0], b['cap'], b['X'], b['apexes']) for b in bl]
        facts['capok ' + str(all(b['capok'] for b in bl))] += 1
        brs[i] = {I[f] for f in br}
        typ[i] = ty
    tr = {}
    for i in range(k):
        bs = blocks[i]
        tr['GE1', (i,)] = len(bs) >= 1
        tr['GE2', (i,)] = len(bs) >= 2
        tr['AX', (i,)] = any(b1[0] == b2[0] for b1, b2 in combinations(bs, 2))
        tr['TB', (i,)] = any(ap is not None and A.mult[ap] >= 3 for b in bs for ap in b[3])
        tr['CPE', (i,)] = any(X in ends[w] for (w, C, X, _) in bs)
        tr['MUT', (i,)] = any((C, w) in {(w2, C2) for j in range(k) if j != i for (w2, C2, _, _) in blocks[j]} for (w, C, X, _) in bs)
    for i, j in combinations(range(k), 2):
        assert (j in brs[i]) == (i in brs[j])
        tr['BR', (i, j)] = j in brs[i]
    vt = {frozenset(t) for t in A.tris}
    for i, j, l in combinations(range(k), 3):
        tr['FC', (i, j, l)] = frozenset((P[i], P[j], P[l])) in vt
    mids = {i: {w for (w, _, _, _) in blocks[i]} for i in range(k)}
    for W, Q in permutations(range(k), 2):
        tr['E2', (W, Q)] = any(X in ends[w] and C in mids[Q] for (w, C, X, _) in blocks[W])
    for p, r in combinations(range(k), 2):
        for q in range(k):
            for s in range(k):
                if len({p, r, q, s}) < 4: continue
                tr['E1', (p, r, q, s)] = any(bq != m and bq in mids[q] for m in lines[p] & lines[r] & lines[s] for bq in lines[s])
    return tr, typ, facts


def check(A, st):
    n = A.n
    if any(m > 3 for m in A.mult) or len(A.triples) < 3: return
    toks = ' '.join(A.tokens)
    chi = chi_from_word(toks, n)
    # geometric triangles as line triples
    tris = set()
    for t in A.tris:
        ls = set()
        for u, v in combinations(t, 2): ls.add(A.common_line(u, v))
        tris.add(tuple(sorted(ls)))
    cg = set(tuple(sorted(t)) for t in count_general(n, chi))
    if cg != tris: st['TRI MISMATCH (model vs referee)'] += 1; return
    pool, cnf = IDPool(), CNF()
    trip = list(combinations(range(n), 3))
    z = {t: pool.id(('zero',) + t) for t in trip}; pz = {t: pool.id(('pos',) + t) for t in trip}
    ng = {t: pool.id(('neg',) + t) for t in trip}; tri = {t: pool.id(('tri',) + t) for t in trip}
    for t in trip:
        v = chi[t]
        cnf.extend([[z[t] if v == 0 else -z[t]], [pz[t] if v == 1 else -pz[t]], [ng[t] if v == -1 else -ng[t]],
                    [tri[t] if t in tris else -tri[t]]])
    bf = lambda r, i, j: ng[S(r, i, j)] if i < j else pz[S(r, i, j)]
    blk = {}
    for t in trip:  # exactly build_k5b.add_dz (->) + build_k5g.build_g (<-)
        for a_ in t:
            b_, c_ = [y for y in t if y != a_]
            for C in range(n):
                if C in t: continue
                v = pool.id(('blk', t, a_, C))
                cnf.extend([[-v, z[t]], [-v, tri[S(a_, b_, C)]], [-v, tri[S(a_, c_, C)]], [-z[t], -tri[S(a_, b_, C)], -tri[S(a_, c_, C)], v]])
                blk[t, a_, C] = v
    first = lambda L, R: [x for M in range(n) if M not in (L, R) for x in (-bf(L, M, R), -z[S(L, R, M)])]
    last = lambda L, R: [x for M in range(n) if M not in (L, R) for x in (-bf(L, R, M), -z[S(L, R, M)])]
    def conj(name, lits):
        v = pool.id(name); cnf.extend([[-v, x] for x in lits]); cnf.append([v] + [-x for x in lits]); return v
    F = {(L, R): conj(('gF', L, R), first(L, R)) for L, R in permutations(range(n), 2)}
    G = {(L, R): conj(('gG', L, R), last(L, R)) for L, R in permutations(range(n), 2)}
    k = len(A.triples)
    ids = add_labels(cnf, pool, n, z, tri, blk, F, G, nlab=k)
    for i, e in enumerate(A.triples):
        cnf.append([ids['p'][','.join(map(str, (i, *sorted(A.ev[e]))))]])
    tr, typ, facts = truth_of(A)
    st.update(facts)
    two = {'GE1', 'GE2', 'AX', 'TB', 'BR'}
    with Solver(name='cadical153', bootstrap_with=cnf.clauses) as sv:
        if not sv.solve(): st['BASE UNSAT'] += 1; return
        joint = []
        for (name, key), val in tr.items():
            v = ids[name][','.join(map(str, key))]
            pos = sv.solve(assumptions=[v])
            if name in two:
                neg = sv.solve(assumptions=[-v])
                st[f'{name} {"ok" if (pos, neg) == (val, not val) else "MISMATCH"}'] += 1
                joint.append(v if val else -v)
            elif val:
                st[f'{name} true: {"sound" if pos else "UNSOUND"}'] += 1
                joint.append(v)
            else:
                st[f'{name} false: {"loose" if pos else "tight"}'] += 1
        st['JOINT ' + ('sat' if sv.solve(assumptions=joint) else 'UNSAT')] += 1
    for i in range(k):
        ty = typ[i]; st['type ' + ty] += 1
        g1, g2, ax, tb = (tr[x, (i,)] for x in ('GE1', 'GE2', 'AX', 'TB'))
        ok = {'axis': g2 and ax, 'bent': g2 and not ax, 'b1': g1 and not g2, 'b0': not g1}.get(ty, True)
        if ty == 'adjacent': ok = False
        if ty == 'b1': st['b1 ' + ('O1b' if tb else 'O1a')] += 1
        if not ok: st['TYPE MAP FAIL ' + ty] += 1
    st['arrangements'] += 1; st[('k', min(k, 9))] += 1


def score(A):
    if any(m > 3 for m in A.mult): return -1
    sc = 0
    for P in A.triples:
        cr, bl, br, typ = info(A, P)
        sc += 10 * (typ == 'bent') + 2 * len(br) + 3 * (len(bl) == 1 and any(A.mult[ap] >= 3 for b in bl for ap in b['apexes'] if ap is not None))
        sc += 2 * sum(b['X'] in (A.rows[b['ray'][0]][0], A.rows[b['ray'][0]][-1]) for b in bl)
    return sc


def worker(args):
    wid, N, seed = args
    rng = random.Random(seed * 7919 + wid); st = Counter(); bad = []
    files = [f for s in ('10', '11', '12', '13', '14', '15', '16') for f in sorted((GAL / s).glob('*.json'))]
    for it in range(N):
        f = rng.choice(files); n = int(f.parent.name.split('-')[0])
        try:
            A = from_tokens(json.load(open(f))['gens'].split(), n)
            for _ in range(rng.choice([0, 2, 6])):
                s = simple_tris(A)
                if s: A = flip(A, rng.choice(s))
            for step in range(rng.choice([5, 7, 9])):
                s = simple_tris(A)
                if not s: break
                best, bs = None, -2
                for t in rng.sample(s, min(12, len(s))):
                    try: B = contract(A, t)
                    except (ValueError, AssertionError, IndexError): continue
                    sc = score(B) + rng.random()
                    if sc > bs: best, bs = B, sc
                if best is None: break
                A = best
                if 3 <= len(A.triples) <= 7 and step % 2 == 1:
                    try: check(A, st)
                    except (AssertionError, ValueError, IndexError) as ex: bad.append(repr(ex)[:200]); st['exception'] += 1
        except (ValueError, AssertionError, IndexError):
            continue
    return st, bad


if __name__ == '__main__':
    N, seed = int(sys.argv[1]), int(sys.argv[2])
    st = Counter(); bad = []
    with Pool(4) as pool:
        for s, b in pool.imap_unordered(worker, [(w, N, seed) for w in range(4)]):
            st.update(s); bad += b
    for k_ in sorted(st, key=str): print(k_, st[k_])
    for b in bad[:10]: print('  exc', b)
    fail = [k_ for k_ in st if any(x in str(k_) for x in ('MISMATCH', 'UNSOUND', 'UNSAT', 'FAIL', 'capok False', 'TRI MISMATCH'))]
    print('FAIL' if fail else 'PASS', fail)

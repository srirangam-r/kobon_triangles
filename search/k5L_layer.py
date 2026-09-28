"""Label layer for the per-graph k=5, beta>0 encoding (k5L): names the five triple points 0..4 and defines, on
top of model literals (z, tri, blk, F, G), indicators that a cube can fix to one residue graph of
work/t3/k5_exceptions.jsonl (types, bridge graph, faces, exception sites).

Definitions (exactly one p(i,t) per label; labels <-> the triple points, a bijection):
  l(i,L)        <-> label i lies on line L
  blkL(i,a,C)   <-> label i has a block with middle line a and cap C       (blk(t,a,C) of k5g, t = label i)
  GE1/GE2(i)    <-> label i has >= 1 / >= 2 blocks
  AX(i)         <-> two blocks of label i share their middle line (type X/F; bent = GE2 and not AX)
  TB(i)         <-  a block of i has a triple apex b∩C (b the other line of i on that side)   [O1b]
                ->  some block of i has a triple apex                                        (both directions)
  BR(i,j)       <-> on some line r through i and j, >= 2 triangles tri(r,x,y) with x a line of i, y a line of j
                    (= the segment [i,j] is a doubly used bridge)
  FC(i,j,k)     ->  the lines ij, jk, ik bound a triangle (an all-multiple face ijk)
  CPE(i)        ->  some block of i has its cap point as an end vertex of the block line   [C50 (ii) / E2 form]
  MUT(i)        ->  some block (a,C) of i is mutual: another label has a block on C capped by a  [C50 (i)]
  E2(W,Q)       ->  W has a block (a,C) with C a block middle line of Q, cap point an end of a  [C43 E2]
  E1(P,R,Q,s)   ->  label s lies on the line PR and on a block middle line of Q               [C43 E1]
One-directional indicators (->) are only ever asserted true by cubes, so they are necessary conditions.
"""
from itertools import combinations, permutations

from pysat.card import CardEnc, EncType

S = lambda *x: tuple(sorted(x))


def counter(cnf, pool, lits, K, name):
    """Full-equivalence sequential counter: returns out[1..K] with out[j] <-> (sum of lits >= j)."""
    prev = [True] + [False] * K
    for m, x in enumerate(lits):
        cur = [True] + [None] * K
        for j in range(1, K + 1):
            a, b = prev[j], prev[j - 1]
            if b is False:
                cur[j] = a
                continue
            v = pool.id((name, m, j))
            if a is not False:
                cnf.append([-a, v])
            cnf.append([-x, v] if b is True else [-x, -b, v])
            cnf.append([-v] + ([a] if a is not False else []) + [x])
            if b is not True:
                cnf.append([-v] + ([a] if a is not False else []) + [b])
            cur[j] = v
        prev = cur
    out = [None]
    for j in range(1, K + 1):
        if prev[j] is False:
            v = pool.id((name, "false", j))
            cnf.append([-v])
            prev[j] = v
        out.append(prev[j])
    return out


def upper(cnf, pool, lits, K, name):
    """Forward (one-directional) counter: returns out[1..K] with (sum of lits >= j) -> out[j]."""
    prev = [None] * (K + 1)
    for m, x in enumerate(lits):
        cur = [None] * (K + 1)
        for j in range(1, K + 1):
            v = pool.id((name, m, j))
            if prev[j]:
                cnf.append([-prev[j], v])
            if j == 1:
                cnf.append([-x, v])
            elif prev[j - 1]:
                cnf.append([-x, -prev[j - 1], v])
            cur[j] = v
        prev = cur
    return prev


def add_labels(cnf, pool, n, z, tri, blk, F, G, nlab=5):
    trip = list(combinations(range(n), 3))
    lines = range(n)
    labs = range(nlab)
    ids = {}
    # --- labels: a bijection between labels and triple points
    p = {(i, t): pool.id(("Lp", i, t)) for i in labs for t in trip}
    for i in labs:
        cnf.append([p[i, t] for t in trip])
        cnf.extend(CardEnc.atmost(lits=[p[i, t] for t in trip], bound=1, vpool=pool, encoding=EncType.seqcounter).clauses)
    for t in trip:
        cnf.append([-z[t]] + [p[i, t] for i in labs])
        for i in labs:
            cnf.append([-p[i, t], z[t]])
        for i, i2 in combinations(labs, 2):
            cnf.append([-p[i, t], -p[i2, t]])
    lab = {(i, L): pool.id(("Ll", i, L)) for i in labs for L in lines}
    for i in labs:
        for L in lines:
            cnf.append([-lab[i, L]] + [p[i, t] for t in trip if L in t])
        for t in trip:
            for L in t:
                cnf.append([-p[i, t], lab[i, L]])
    # --- blocks per label
    bL = {}
    for i in labs:
        for a in lines:
            for C in lines:
                if C == a:
                    continue
                v = pool.id(("LblkL", i, a, C))
                bL[i, a, C] = v
                cnf.extend([[-v, lab[i, a]], [-v, -lab[i, C]]])
                for t in trip:
                    if a in t and C not in t:
                        cnf.append([-v, -p[i, t], blk[t, a, C]])
                        cnf.append([-p[i, t], -blk[t, a, C], v])
    GE1, GE2, AX = {}, {}, {}
    for i in labs:
        out = counter(cnf, pool, [bL[k] for k in bL if k[0] == i], 2, ("Lnb", i))
        GE1[i], GE2[i] = out[1], out[2]
        c2 = [counter(cnf, pool, [bL[i, a, C] for C in lines if C != a], 2, ("Lax", i, a))[2] for a in lines]
        AX[i] = pool.id(("LAX", i))
        cnf.append([-AX[i]] + c2)
        cnf.extend([[-c, AX[i]] for c in c2])
    # --- triple apex (O1b)
    t2 = {}
    for x, y in combinations(lines, 2):
        v = pool.id(("Ltrip2", x, y))
        t2[x, y] = t2[y, x] = v
        cnf.append([-v] + [z[S(x, y, w)] for w in lines if w not in (x, y)])
    for t in trip:
        for x, y in combinations(t, 2):
            cnf.append([-z[t], t2[x, y]])
    TB = {}
    for i in labs:
        TB[i] = pool.id(("LTB", i))
        ws = []
        for a, b, C in permutations(lines, 3):
            cnf.append([-bL[i, a, C], -lab[i, b], -t2[b, C], TB[i]])
            w = pool.id(("LTBw", i, a, b, C))
            cnf.extend([[-w, bL[i, a, C]], [-w, lab[i, b]], [-w, t2[b, C]]])
            ws.append(w)
        cnf.append([-TB[i]] + ws)
    # --- bridges between labels
    BR = {}
    for i, j in combinations(labs, 2):
        per_r = []
        for r in lines:
            bws = []
            for x in lines:
                for y in lines:
                    if len({r, x, y}) < 3:
                        continue
                    w = pool.id(("Lbw", i, j, r, x, y))
                    parts = [lab[i, r], lab[i, x], lab[j, r], lab[j, y], tri[S(r, x, y)]]
                    cnf.extend([[-w, q] for q in parts])
                    cnf.append([w] + [-q for q in parts])
                    bws.append(w)
            per_r.append(counter(cnf, pool, bws, 2, ("Lbr", i, j, r))[2])
        v = pool.id(("LBR", i, j))
        cnf.append([-v] + per_r)
        cnf.extend([[-c, v] for c in per_r])
        BR[i, j] = v
    # --- all-multiple faces
    FC = {}
    for i, j, k in combinations(labs, 3):
        v = pool.id(("LFC", i, j, k))
        ws = []
        for a, b, c in permutations(lines, 3):  # a = line ij, b = line jk, c = line ik
            w = pool.id(("LFCw", i, j, k, a, b, c))
            parts = [lab[i, a], lab[j, a], lab[j, b], lab[k, b], lab[i, c], lab[k, c], tri[S(a, b, c)]]
            cnf.extend([[-w, q] for q in parts])
            ws.append(w)
        cnf.append([-v] + ws)
        FC[i, j, k] = v
    # --- exceptions
    ce = {}
    for (i, a, C), v in bL.items():
        w = pool.id(("Lce", i, a, C))
        cnf.extend([[-w, v], [-w, F[a, C], G[a, C]]])
        ce[i, a, C] = w
    CPE, MUT = {}, {}
    for i in labs:
        CPE[i] = pool.id(("LCPE", i))
        cnf.append([-CPE[i]] + [ce[k] for k in ce if k[0] == i])
        MUT[i] = pool.id(("LMUT", i))
        mus = []
        for a in lines:
            for C in lines:
                if C == a:
                    continue
                w = pool.id(("Lmu", i, a, C))
                cnf.append([-w, bL[i, a, C]])
                cnf.append([-w] + [bL[j, C, a] for j in labs if j != i])
                mus.append(w)
        cnf.append([-MUT[i]] + mus)
    bl = {}
    for Q in labs:
        for C in lines:
            v = pool.id(("Lbl", Q, C))
            cnf.append([-v] + [bL[Q, C, C2] for C2 in lines if C2 != C])
            bl[Q, C] = v
    E2 = {}
    for W, Q in permutations(labs, 2):
        v = pool.id(("LE2", W, Q))
        ws = []
        for a in lines:
            for C in lines:
                if C == a:
                    continue
                w = pool.id(("Le2", W, Q, a, C))
                cnf.extend([[-w, ce[W, a, C]], [-w, bl[Q, C]]])
                ws.append(w)
        cnf.append([-v] + ws)
        E2[W, Q] = v
    E1 = {}
    for P, R in combinations(labs, 2):
        for Q in labs:
            for s_ in labs:
                if len({P, R, Q, s_}) < 4:
                    continue
                v = pool.id(("LE1", P, R, Q, s_))
                ws = []
                for m in lines:
                    for bq in lines:
                        if bq == m:
                            continue
                        w = pool.id(("Le1", P, R, Q, s_, m, bq))
                        cnf.extend([[-w, q] for q in (lab[P, m], lab[R, m], lab[s_, m], lab[s_, bq], bl[Q, bq])])
                        ws.append(w)
                cnf.append([-v] + ws)
                E1[P, R, Q, s_] = v
    key = lambda k: ",".join(map(str, k))
    ids.update(GE1={key((i,)): GE1[i] for i in labs}, GE2={key((i,)): GE2[i] for i in labs},
               AX={key((i,)): AX[i] for i in labs}, TB={key((i,)): TB[i] for i in labs},
               BR={key(k): v for k, v in BR.items()}, FC={key(k): v for k, v in FC.items()},
               CPE={key((i,)): CPE[i] for i in labs}, MUT={key((i,)): MUT[i] for i in labs},
               E2={key(k): v for k, v in E2.items()}, E1={key(k): v for k, v in E1.items()},
               p={key((i, *t)): v for (i, t), v in p.items()})
    return ids

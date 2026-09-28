"""Metropolis walk over pseudoline arrangements (flip / collapse / expand), collecting
arrangements with few triple points and high T, then testing the lemmas and the k=3
inequality  need = 3B + 2beta - x - 14 - sigma <= CredA + [sigma=0]*va.

python3 walk.py <out.jsonl> <seed> <steps> <start files...>
"""
import json, random, sys, collections, glob
sys.path.insert(0, '.')
from arr import *
from mutate import random_move
from lemmas import check, point_info, kappa


def config_numbers(a):
    T = a.triples
    info = {P: point_info(a, P) for P in T}
    trip_lines = set().union(*[a.events[P] for P in T]) if T else set()
    tl = collections.Counter(L for P in T for L in a.events[P])
    sigma = sum(v - 1 for v in tl.values() if v > 1)
    B = sum(len(info[P]['blocks']) for P in T)
    x = sum(1 for P in T for _, c in info[P]['blocks'] if c in trip_lines)
    D = a.D()
    beta = D - B
    return info, trip_lines, sigma, B, x, beta


def k3_test(a, stats):
    info, trip_lines, sigma, B, x, beta = config_numbers(a)
    stats_local = {}
    s2 = collections.Counter()
    r = check(a, s2, None)
    for k_, v in s2.items():
        if 'FAIL' in k_:
            stats[k_] += v
    need = 3 * B + 2 * beta - x - 14 - sigma
    va = 0
    caps = {c for P in a.triples for _, c in info[P]['blocks']}
    kap, ztr = kappa(a)
    for P in a.triples:
        ax = info[P]['axis']
        if ax is not None and ax not in caps and not any(Q != P and ax in a.events[Q] for Q in a.triples):
            va += 1
    cred = r['credA'] + (va if sigma == 0 else 0)
    clean = [L for L in range(a.n) if L not in trip_lines and L not in caps]
    cred_true = 2 * a.Z() - sum(kap[L] for L in clean)
    stats['k3 need<=cred' if need <= cred else 'k3 need>cred FAIL'] += 1
    stats['k3 need<=cred_true' if need <= cred_true else 'k3 need>cred_true FAIL'] += 1
    return need, cred, B, beta, x, sigma


if __name__ == '__main__':
    out, seed, steps = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    starts = sys.argv[4:]
    rng = random.Random(seed)
    stats = collections.Counter()
    seen = set()
    fh = open(out, 'a')
    for s in starts:
        d = json.load(open(s))
        a = Arr(d['gens'])
        n = a.n
        T0 = a.T()
        for it in range(steps):
            w = random_move(a, rng, p_collapse=0.35, p_expand=0.15)
            if w is None:
                continue
            b = Arr(w, n)
            if any(len(ev) > 3 for ev in b.events):
                continue
            k = len(b.triples)
            # accept if not much worse; keep k small-ish
            if b.T() < T0 - 4 or k > 6:
                continue
            if b.T() < a.T() and rng.random() > 0.3:
                continue
            a = b
            if w in seen:
                continue
            seen.add(w)
            s2 = collections.Counter()
            if k <= 6 and n % 2 == 0:
                check(a, s2, None)
                for k_, v in s2.items():
                    if 'FAIL' in k_ and k_ != 'chain FAIL':
                        stats[k_] += v
                        print('FAIL', k_, w, flush=True)
                stats['checked k=%d' % k] += 1
            if k == 3:
                need, cred, B, beta, x, sigma = k3_test(a, stats)
                stats[('cfg', sigma, B, beta)] += 1
                if need > cred:
                    print('k3 FAIL', need, cred, w, flush=True)
                if B >= 5:
                    fh.write(json.dumps(dict(gens=w, n=n, T=a.T(), need=need, cred=cred, B=B, beta=beta, x=x, sigma=sigma)) + '\n')
    for k_, v in sorted(stats.items(), key=str):
        print(v, k_)

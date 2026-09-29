"""Coverage of a generator's band by capture-recapture over independent chains.

Each input file is one chain = one capture occasion. Samples are reduced to canonical classes up to the 4n
end-circle symmetries plus the global sign flip (vectorized). Per T band:
  * S_obs: distinct classes seen; per chain n_i;
  * Lincoln-Petersen for every chain pair: n_i n_j / m_ij (m_ij = classes seen by both);
  * Chao1 on incidence (Q1 = classes seen by exactly 1 chain, Q2 = by exactly 2): S_obs + (c-1)/c * Q1^2/(2 Q2).
Heterogeneous catchability biases both downward, so the estimates are lower bounds on the reachable class count
and the coverage S_obs/N_hat is an upper bound.

    python search/coverage.py --band 82 <chain1.jsonl> <chain2.jsonl> [...]   (rows: n, T, k, bridges, gens or chi)
"""
import argparse
import collections
import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.insert(1, str(ROOT / "work/lns/push"))
from symmetry import actions  # noqa: E402
from run_lns import chi_from_word  # noqa: E402

_CACHE = {}


def tables(n):
    if n not in _CACHE:
        trip = list(combinations(range(n), 3))
        pos = {t: i for i, t in enumerate(trip)}
        perms, facs = [], []
        for g in actions(n):
            m = g.signed_map(n)
            perms.append([pos[m[t][0]] for t in trip])
            facs.append([m[t][1] for t in trip])
        P, F = np.array(perms), np.array(facs, dtype=np.int8)
        P = np.concatenate([P, P])
        F = np.concatenate([F, -F])  # global sign flip
        _CACHE[n] = (trip, P, F)
    return _CACHE[n]


def canon(chi_vec, n):
    trip, P, F = tables(n)
    M = (F * chi_vec[P]).astype(np.int8)  # all images, one per row
    return min(M[i].tobytes() for i in range(M.shape[0]))  # any fixed total order on rows gives a canonical form


def vec(row):
    n = row["n"]
    trip, _, _ = tables(n)
    chi = chi_from_word(row["gens"], n)  # always from the wiring word (gallery convention)
    return np.array([chi[t] for t in trip], dtype=np.int8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("chains", nargs="+")
    ap.add_argument("--band", type=int, default=82, help="minimum T")
    ap.add_argument("--max-per-chain", type=int, default=10 ** 9)
    a = ap.parse_args()
    per_chain = []
    info = {}
    for f in a.chains:
        s, cnt = set(), 0
        for l in open(f):
            try:
                r = json.loads(l)
            except json.JSONDecodeError:
                continue
            if r.get("T", 0) < a.band:
                continue
            c = canon(vec(r), r["n"])
            s.add(c)
            info.setdefault(c, (r["T"], r.get("k"), r.get("bridges")))
            cnt += 1
            if cnt >= a.max_per_chain:
                break
        per_chain.append(s)
        print(f"{f}: {cnt} samples with T >= {a.band}, {len(s)} distinct classes", flush=True)
    allc = set().union(*per_chain)
    inc = collections.Counter(c for s in per_chain for c in s)
    Q = collections.Counter(inc.values())
    c = len(per_chain)
    print(f"\nband T >= {a.band}: S_obs = {len(allc)} distinct classes over {c} chains; incidence counts {dict(sorted(Q.items()))}")
    for i, j in combinations(range(c), 2):
        m = len(per_chain[i] & per_chain[j])
        lp = len(per_chain[i]) * len(per_chain[j]) / m if m else float("inf")
        print(f"  Lincoln-Petersen chains {i},{j}: n={len(per_chain[i])},{len(per_chain[j])} m={m} -> N_hat = {lp:.0f}")
    if Q.get(2):
        chao = len(allc) + (c - 1) / c * Q.get(1, 0) ** 2 / (2 * Q[2])
    else:
        chao = float("inf")
    print(f"  Chao1 (incidence): N_hat = {chao:.0f}; coverage S_obs/N_hat = {len(allc) / chao:.3f}" if chao != float("inf")
          else "  Chao1: no class seen by exactly 2 chains -> unbounded (coverage ~ 0)")
    byT = collections.Counter(info[x][0] for x in allc)
    print("  distinct classes by T:", dict(sorted(byT.items(), reverse=True)))
    for T in sorted(byT, reverse=True):
        sub = [set(x for x in s if info[x][0] == T) for s in per_chain]
        inc_T = collections.Counter(x for s in sub for x in s)
        QT = collections.Counter(inc_T.values())
        S = len(set().union(*sub))
        chaoT = S + (c - 1) / c * QT.get(1, 0) ** 2 / (2 * QT[2]) if QT.get(2) else float("inf")
        print(f"   T={T}: S_obs={S}, incidence {dict(sorted(QT.items()))}, Chao1 N_hat={chaoT:.0f}")


if __name__ == "__main__":
    main()

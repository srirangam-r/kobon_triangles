"""dpwalk2: bridge- and Z-targeted exact-DP ruin-and-recreate walk (extends search/dpwalk.py; that file is untouched).

State = wiring word.  Move: delete 1 (or 2) lines, re-insert with the exact compiled one-line DP (dp1fast).
Additions over dpwalk.py:
  * --n (any n with a known reference T), --start FILE... (jsonl / json rows with "gens", gallery dirs / globs),
    --exclude-src FILE (drop rows by "src"/file name).
  * Z-targeted deletion: line x is drawn with weight (eps + Zx + dbias*Dx)^gamma, where Zx / Dx are the unused /
    doubly-used bounded segments on x (--zincident also credits the other line at each simple end of an unused
    segment), mixed with uniform deletion at rate 1 - --zprob.
  * Score = T + wk*k + wb*bridges + wd*D - wz*Z.  Note Z - D + 3k = n(n-2) - 3T exactly (an identity, checked in the
    selftest), so wd = wz = w is the same as extra weight on T and k; only wd != wz or a bridge term changes anything.
  * Canonical classes (search/coverage.py canon: 4n end-circle symmetries + sign flip) for the "distinct" bookkeeping
    of every state with T >= --band; chains stay independent, Chao1 over chains is done in `stats`.
  * --pair-rate: exact two-line probe (search/extend2_dp.py pair_search, target = ref+1) on bridge-rich states.
  * `calib` compares the classes found against the held-out bridged n=16 records.

    uv run --no-project --with python-sat python search/dpwalk2.py selftest
    uv run --no-project --with python-sat python search/dpwalk2.py run --n 18 --start work/dpwalk/bridge93.json \
        --secs 3600 --workers 8 --out work/dpwalk2/prod
    uv run --no-project --with python-sat python search/dpwalk2.py stats work/dpwalk2/prod [--heldout FILE]
"""
import argparse
import glob
import hashlib
import json
import math
import os
import random
import sys
import time
from collections import Counter
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.insert(1, str(ROOT / "work" / "lns" / "push"))
sys.path.insert(0, str(ROOT / "search" / "dp1fast"))
sys.path.append(str(ROOT / "work" / "t3"))  # inspect.py there shadows the stdlib: never first
sys.path.insert(0, str(ROOT / "work" / "research2"))
sys.path.insert(0, str(ROOT / "tools/external/kobon-solutions"))
import extend_dp  # noqa: E402
from dp1fast import Dp1  # noqa: E402
from verification.quick_check import count_triangles, replay_word  # noqa: E402

GALLERY = ROOT / "tools/external/kobon-solutions/gallery/data"
N = 18   # set from --n in main()


# ---------------------------------------------------------------- words <-> rows
def tokens_to_gens(toks):
    return " ".join(f"{g}*" if w == 3 else str(g) for g, w in toks)


def rows_from_tokens(toks, n):
    a = list(range(n))
    rows = [[] for _ in range(n)]
    for g, w in toks:
        block = a[g:g + w]
        fs = frozenset(block)
        for x in block:
            rows[x].append(fs - {x})
        a[g:g + w] = block[::-1]
    return tuple(tuple(r) for r in rows)


def sweep(rows, order):
    """Wiring word (list of (g, w)) of the arrangement given by rows with initial bottom-to-top `order`, or None."""
    n = len(order)
    a = list(order)
    ptr = [0] * n
    nxt = [r[0] if r else None for r in rows]
    total = sum(len(r) for r in rows)
    toks = []
    done = 0
    stack = list(range(n - 2, -1, -1))
    while stack:
        g = stack.pop()
        x, y = a[g], a[g + 1]
        ex = nxt[x]
        if ex is None or y not in ex:
            continue
        if len(ex) == 1:
            if nxt[y] != frozenset((x,)):
                continue
            w = 2
        else:
            if g + 2 >= n:
                continue
            z = a[g + 2]
            if ex != frozenset((y, z)) or nxt[y] != frozenset((x, z)) or nxt[z] != frozenset((x, y)):
                continue
            w = 3
        block = a[g:g + w]
        for l in block:
            ptr[l] += 1
            nxt[l] = rows[l][ptr[l]] if ptr[l] < len(rows[l]) else None
        a[g:g + w] = block[::-1]
        toks.append((g, w))
        done += w
        for h in range(max(0, g - 2), min(n - 1, g + w + 1)):
            stack.append(h)
    if done != total:
        return None
    return toks


def rows_to_word(struct_rows, base_n, hl, rev):
    """struct_rows: rows of base_n+1 lines, the new line last (label base_n).  New line has slot hl at the left."""
    rows = struct_rows
    if rev:
        rows = rows[:-1] + (tuple(reversed(rows[-1])),)
    order = list(range(hl)) + [base_n] + list(range(hl, base_n))
    return sweep(rows, order)


# ---------------------------------------------------------------- one-line re-insertion
class Base:
    """A base arrangement (tokens, n lines) with its DP; produces extended words."""

    def __init__(self, toks, n):
        self.toks, self.n = toks, n
        self.dp = Dp1(toks, n)
        self.T0 = self.dp.T0

    def best(self):
        return self.dp.solve()

    def word_of(self, seq, first_fid=None):
        """Wiring word of base + new line along path seq (list of x-elements); first_fid = start face."""
        n = self.n
        rows = self.dp.rows(seq)
        cands = []
        if first_fid is not None:
            f = self.dp.struct[0][first_fid]
            s = len(f["below"])
            right = any(x[0] == "inf" and x[2] == 1 for x in f["cyc"])
            left = any(x[0] == "inf" and x[2] == 0 for x in f["cyc"])
            if left and not right:
                cands.append((s, False))
            elif right and not left:
                cands.append((n - s, True))
        for hl in range(n + 1):
            for rev in (False, True):
                if (hl, rev) not in cands:
                    cands.append((hl, rev))
        for hl, rev in cands:
            t = rows_to_word(rows, n, hl, rev)
            if t is not None:
                return t
        raise RuntimeError("could not rebuild wiring word")

    def paths(self, thr, cap):
        """(count, [(seq, start_fid)]) of paths with T >= thr (canonical starts)."""
        dp = self.dp
        stride = dp.n + 1
        import numpy as np
        from dp1fast import lib, _ptr
        buf = np.zeros(cap * stride, dtype=np.int32)
        sb = np.zeros(cap, dtype=np.int32)
        cnt = lib().dp1_enum(dp.h, 0, 1, thr - dp.T0, cap, stride, _ptr(buf), _ptr(sb))
        buf = buf.reshape(cap, stride)
        out = []
        for i in range(min(cnt, cap)):
            fid0 = dp.elem[int(sb[i])][0]
            out.append((dp._xs(buf[i]), fid0))
        return cnt, out


def delete_lines(toks, n, ds):
    """Delete wires ds (labels), highest first so labels stay valid."""
    for d in sorted(ds, reverse=True):
        toks = extend_dp.delete_wire(toks, n, d)
        n -= 1
    return toks, n


# ---------------------------------------------------------------- state evaluation
REF_T = {14: 55, 15: 65, 16: 72, 17: 85, 18: 93}     # best known T per n (hit = REF_T + 1)


def hash_rows(rows):
    return hash(rows)


def count_T(toks, n):
    return count_triangles(rows_from_tokens(toks, n))


def chi_from_word(gens, n):
    wires = list(range(n))
    slot_of = list(range(n))
    chi = {}
    for tok in gens.split():
        g = int(tok.rstrip("*"))
        w = 3 if tok.endswith("*") else 2
        block = wires[g:g + w]
        for i, k in combinations(sorted(block), 2):
            for j in range(i + 1, k):
                chi[i, j, k] = 0 if j in block else (1 if g > slot_of[j] else -1)
        block.reverse()
        wires[g:g + w] = block
        for s in range(g, g + w):
            slot_of[wires[s]] = s
    return chi


def verify_hit(toks, n):
    """Independent recount with both counters."""
    from kobon_sat import count_general
    gens = tokens_to_gens(toks)
    t1 = len(count_general(n, chi_from_word(gens, n)))
    t2 = count_triangles(replay_word(gens, n).rows)
    return t1, t2


def n_triple(toks):
    return sum(1 for _, w in toks if w == 3)


def info(toks, n):
    """T, k, bridges, Z, D and per-line Z / D / incident-Z counts of the arrangement (one Arr build)."""
    from arr import Arr
    a = Arr(tokens_to_gens(toks), n)
    ev = a.events
    Zl, Dl, Zi = [0] * n, [0] * n, [0.0] * n
    br = set()
    for x in range(n):
        r = a.rows[x]
        for e in range(len(r) - 1):
            s = a.t[x][e]
            if not s:
                Zl[x] += 1
                for p in (r[e], r[e + 1]):
                    if len(ev[p]) == 2:
                        (o,) = ev[p] - {x}
                        Zi[o] += 1
            elif len(s) == 2:
                Dl[x] += 1
                if len(ev[r[e]]) == 3 and len(ev[r[e + 1]]) == 3:
                    br.add(frozenset((r[e], r[e + 1])))
    return dict(T=a.T(), k=len(a.triples), b=len(br), Z=sum(Zl), D=sum(Dl), Zl=Zl, Dl=Dl, Zi=Zi)


def bridge_count(toks, n):
    return info(toks, n)["b"]


def canon_id(gens, n):
    """Hex id of the canonical class (coverage.canon over the 4n end-circle symmetries + sign flip)."""
    import numpy as np
    import coverage
    trip, _, _ = coverage.tables(n)
    chi = coverage.chi_from_word(gens, n)
    v = np.array([chi[t] for t in trip], dtype=np.int8)
    return hashlib.sha1(coverage.canon(v, n)).hexdigest()[:16]


# ---------------------------------------------------------------- the walk
class Walker:
    def __init__(self, rng, out_dir, wid, a):
        self.rng, self.out, self.wid, self.a = rng, out_dir, wid, a
        self.n = a.n
        self.ref = REF_T[a.n]
        self.band = a.band if a.band is not None else self.ref
        self.visited = set()
        self.st = Counter()
        self.hist = Counter()          # (T, k, bridges) over distinct states
        self.best_T = 0
        self.classes = {}              # canon id -> (T, k, b, toks) for T >= band
        self.t_dp = self.t_rest = 0.0
        self.src = "?"

    def score(self, inf):
        a = self.a
        k = min(inf["k"], a.kcap) if a.kcap is not None else inf["k"]
        b = min(inf["b"], a.bcap) if a.bcap is not None else inf["b"]
        return inf["T"] + a.wk * k + a.wb * b + a.wd * inf["D"] - a.wz * inf["Z"]

    def record(self, toks, T, rows, inf, start=False):
        h = hash_rows(rows)
        new = h not in self.visited
        if new:
            self.visited.add(h)
            self.st["distinct"] += 1
            self.hist[(T, inf["k"], inf["b"])] += 1
            if T >= self.band:
                gens = tokens_to_gens(toks)
                cid = canon_id(gens, self.n)
                if cid not in self.classes:
                    self.classes[cid] = (T, inf["k"], inf["b"], toks)
                    with open(self.out / f"cls_w{self.wid}.jsonl", "a") as f:
                        f.write(json.dumps(dict(n=self.n, T=T, k=inf["k"], b=inf["b"], D=inf["D"], Z=inf["Z"],
                                                canon=cid, src=self.src, start=start, gens=gens)) + "\n")
                else:
                    self.st["class_dup"] += 1
            if T > self.best_T:
                self.best_T = T
            if T > self.ref:
                self.hit(toks)
        return new

    def hit(self, toks):
        t1, t2 = verify_hit(toks, self.n)
        rec = dict(T=t2, T_count_general=t1, gens=tokens_to_gens(toks), n=self.n)
        if t1 > self.ref and t2 > self.ref:
            p = self.out.parent / f"HIT_{self.n}_{int(time.time())}_w{self.wid}.json"
            json.dump(rec, open(p, "w"))
            (self.out / "STOP").write_text("hit")
            print("HIT", rec, flush=True)
        else:
            self.st["false_hit"] += 1
            print("FALSE HIT (counters disagree)", rec, flush=True)

    # -- which lines to delete
    def pick_lines(self, inf, two):
        a, rng, n = self.a, self.rng, self.n

        def targeted():
            w = [(a.eps + inf["Zl"][x] + a.zinc * inf["Zi"][x] + a.dbias * inf["Dl"][x]) ** a.gamma for x in range(n)]
            return rng.choices(range(n), weights=w)[0]
        tg = rng.random() < a.zprob
        d1 = targeted() if tg else rng.randrange(n)
        self.st["del_targeted" if tg else "del_uniform"] += 1
        if not two:
            return [d1]
        while True:
            d2 = targeted() if (tg and rng.random() < 0.5) else rng.randrange(n)
            if d2 != d1:
                return [d1, d2]

    def move(self, toks, inf_cur, temp, two):
        """One ruin&recreate.  Returns (new_toks, new_T, new_rows, new_info, Tmax) or None."""
        rng, n = self.rng, self.n
        ds = self.pick_lines(inf_cur, two)
        t0 = time.perf_counter()
        bt, bn = delete_lines(toks, n, ds)
        base = Base(bt, bn)
        r = base.best()
        self.st["dp_solves"] += 1
        Tmax = r["T"]
        if Tmax is None:
            return None
        if two:
            cnt, ps = base.paths(Tmax, 200)
            seq, fid = rng.choice(ps) if ps else (r["path"], None)
            t1 = base.word_of(seq, fid)
            base2 = Base(t1, bn + 1)
            r2 = base2.best()
            self.st["dp_solves"] += 1
            Tmax = r2["T"]
            base = base2
        self.t_dp += time.perf_counter() - t0
        slack = 0 if temp < 0.2 else (1 if temp < 0.5 else 2)
        while True:
            thr = Tmax - slack
            cnt, ps = base.paths(thr, self.a.cap)
            if cnt <= self.a.cap or slack == 0:
                break
            slack -= 1
        if not ps:
            return None
        best = None
        for _ in range(min(self.a.ncand, len(ps))):
            seq, fid = rng.choice(ps)
            nt = base.word_of(seq, fid)
            rows = rows_from_tokens(nt, n)
            Tn = count_triangles(rows)
            fresh = hash_rows(rows) not in self.visited
            if self.a.cand_score and Tn >= Tmax - 1:
                inf = info(nt, n)
                key = (fresh, self.score(inf), rng.random())
            else:
                inf = None
                key = (fresh, Tn, rng.random())
            if best is None or key > best[0]:
                best = (key, nt, Tn, rows, inf)
            if fresh and Tn >= Tmax and not self.a.cand_score:
                break
        self.st["cand"] += 1
        key, nt, Tn, rows, inf = best
        if inf is None:
            inf = info(nt, n)
        return nt, Tn, rows, inf, Tmax

    def pair_probe(self, toks, inf_cur):
        """Exact two-line neighbourhood test for T >= ref+1: delete 2 lines, ask pair_search at every rank pair."""
        import extend2_dp as e2
        n = self.n
        ds = self.pick_lines(inf_cur, True)
        bt, bn = delete_lines(toks, n, ds)
        B = e2.Base(tokens=bt, n=bn)
        t0 = time.time()
        self.st["pair_probes"] += 1
        for r1, r2 in combinations(range(bn + 2), 2):
            if time.time() - t0 > self.a.pair_budget:
                self.st["pair_timeouts"] += 1
                break
            T, best = e2.pair_search(B, r1, r2, target=self.a.pair_target or self.ref + 1)
            self.st["pair_calls"] += 1
            if T is not None:
                rows = e2.witness_rows(B, r1, r2, best)
                k1, _seq = best
                pg = r2 if k1 == 1 else r1
                # rows use base+L1 labels = start slots (the extension graph relabels), second line = label bn + 1
                order = list(range(pg)) + [bn + 1] + list(range(pg, bn + 1))
                nt = e2.rows_to_tokens(tuple(tuple(rows[w]) for w in range(n)), order)
                rowsn = rows_from_tokens(nt, n)
                Tn = count_triangles(rowsn)
                self.st["pair_hits"] += 1
                if Tn != T:
                    self.st["pair_recount_mismatch"] += 1
                    print(f"pair witness recount mismatch: {Tn} vs {T}", flush=True)
                self.record(nt, Tn, rowsn, info(nt, n))
                return (nt, Tn)
        self.st["pair_secs"] += int(time.time() - t0)

    def chain(self, toks, deadline, steps, log):
        rng, a, n = self.rng, self.a, self.n
        T = count_T(toks, n)
        rows = rows_from_tokens(toks, n)
        inf = info(toks, n)
        self.record(toks, T, rows, inf, start=True)
        cur_s = self.score(inf)
        stall = 0
        for it in range(steps):
            if time.time() > deadline or (self.out / "STOP").exists():
                return
            temp = a.tlo + (a.thi - a.tlo) * ((it // 40) % 4) / 3
            if a.pair_rate and inf["b"] >= a.pair_minb and T >= self.ref - 1 and rng.random() < a.pair_rate:
                self.pair_probe(toks, inf)
                continue
            two = rng.random() < a.two_rate
            t0 = time.perf_counter()
            res = self.move(toks, inf, temp, two)
            self.st["moves"] += 1
            if two:
                self.st["moves2"] += 1
            self.t_rest += time.perf_counter() - t0
            if res is None:
                continue
            nt, Tn, rows_n, inf_n, Tmax = res
            new = self.record(nt, Tn, rows_n, inf_n)
            if not new:
                self.st["revisit"] += 1
            sc = self.score(inf_n)
            d = sc - cur_s
            if d >= 0 or rng.random() < math.exp(d / temp):
                self.st["accept"] += 1
                toks, T, cur_s, inf = nt, Tn, sc, inf_n
                stall = 0 if T >= self.best_T - 1 else stall + 1
            else:
                stall += 1
            if stall > a.stall:
                return
            if log and self.st["moves"] % 500 == 0:
                print(f"w{self.wid} moves={self.st['moves']} distinct={self.st['distinct']} best={self.best_T} "
                      f"classes={len(self.classes)} cur=(T{T},k{inf['k']},b{inf['b']})", flush=True)


# ---------------------------------------------------------------- starts
def _expand(p):
    p = str(p)
    if os.path.isdir(p):
        return sorted(glob.glob(os.path.join(p, "*.json")) + glob.glob(os.path.join(p, "*.jsonl")))
    g = sorted(glob.glob(p))
    return g if g else [p]


def load_rows(paths, n, exclude=frozenset()):
    """Wiring words (token lists) with n lines from json/jsonl files, gallery dirs, globs.  Rows with src/name in
    `exclude` (or file name in it) are dropped.  Returns [(toks, src)]."""
    out, seen = [], set()
    for p in paths:
        for f in _expand(p):
            txt = Path(f).read_text()
            try:
                j = json.loads(txt)
                recs = j if isinstance(j, list) else [j]
            except ValueError:
                recs = [json.loads(ln) for ln in txt.splitlines() if ln.strip()]
            for r in recs:
                name = r.get("src") or Path(f).name
                if name in exclude or Path(f).name in exclude:
                    continue
                if r.get("n", n) != n or "gens" not in r:
                    continue
                toks = extend_dp.parse_tokens(r["gens"])
                if not toks or max(g + w for g, w in toks) != n:
                    continue
                key = tokens_to_gens(toks)
                if key in seen:
                    continue
                rows = rows_from_tokens(toks, n)
                if len({q for row in rows for e in row for q in e}) != n:
                    continue
                seen.add(key)
                out.append((toks, name))
    return out


def load_exclude(path):
    names = set()
    if not path:
        return names
    j = json.load(open(path))
    for r in (j if isinstance(j, list) else [j]):
        if "src" in r:
            names.add(r["src"])
        if "name" in r:
            names.add(r["name"])
    return names


def run_worker(wid, a):
    rng = random.Random(a.seed * 1000 + wid)
    out = Path(a.out)
    W = Walker(rng, out, wid, a)
    deadline = time.time() + a.secs
    excl = load_exclude(a.exclude_src)
    pool = load_rows(a.start, a.n, excl)
    first = load_rows(a.start[:1], a.n, excl) if a.first_frac is not None else []
    rng.shuffle(pool)
    print(f"w{wid}: {len(pool)} starts" + (f" ({len(first)} in the first --start file, drawn with p={a.first_frac})"
                                            if first else ""), flush=True)
    t_start = time.time()
    chains = 0
    while time.time() < deadline and not (out / "STOP").exists():
        arch = list(W.classes.values())
        r = rng.random()
        if arch and r < a.p_arch:
            if rng.random() < a.p_bridge_arch and any(c[2] >= 1 for c in arch):
                c = rng.choice([c for c in arch if c[2] >= 1])
            else:
                c = rng.choice(arch)
            toks, src = c[3], "arch"
        else:
            toks, src = rng.choice(first if first and rng.random() < a.first_frac else pool)
        chains += 1
        W.src = src
        W.st["chains_" + ("arch" if src == "arch" else "start")] += 1
        W.chain(toks, deadline, a.chain_steps, log=True)
        dump(W, out, t_start)
    dump(W, out, t_start)


def dump(W, out, t0):
    d = dict(wid=W.wid, secs=time.time() - t0, best_T=W.best_T, classes=len(W.classes), stats=dict(W.st),
             t_dp_and_move_setup=W.t_dp, t_total_moves=W.t_rest, params={k: v for k, v in vars(W.a).items()},
             hist=[[list(k), v] for k, v in sorted(W.hist.items())])
    json.dump(d, open(out / f"stats_w{W.wid}.json", "w"))


# ---------------------------------------------------------------- stats / calibration
def heldout_classes(path, n):
    j = json.load(open(path))
    return {canon_id(r["gens"], n): r for r in j}


def chao1(inc_sets):
    """Bias-corrected Chao1 on incidence (c chains): S + (c-1)/c * Q1^2 / (2 Q2)  (Q2 = 0: (c-1)/c*Q1*(Q1-1)/2)."""
    c = len(inc_sets)
    inc = Counter(x for s in inc_sets for x in s)
    Q = Counter(inc.values())
    S = len(inc)
    q1, q2 = Q.get(1, 0), Q.get(2, 0)
    est = S + (c - 1) / c * (q1 * q1 / (2 * q2) if q2 else q1 * (q1 - 1) / 2)
    return S, dict(sorted(Q.items())), est


def cmd_stats(a):
    d = Path(a.dir)
    tot, hist = Counter(), Counter()
    secs = best = 0
    nw = 0
    for f in sorted(d.glob("stats_w*.json")):
        j = json.load(open(f))
        tot.update(j["stats"])
        for k, v in j["hist"]:
            hist[tuple(k)] += v
        secs, best, nw = max(secs, j["secs"]), max(best, j["best_T"]), nw + 1
    print("workers", nw, "secs", round(secs), "best T", best)
    print("counters", dict(tot))
    print("moves/s/core", round(tot["moves"] / max(secs, 1) / max(1, nw), 2))
    for name, ix in (("T", 0), ("k", 1), ("bridges", 2)):
        c = Counter()
        for key, v in hist.items():
            c[key[ix]] += v
        print(name, "histogram over distinct visited states:", dict(sorted(c.items())))
    per = {}
    info_by = {}
    seeds = set()   # classes that were a chain start somewhere
    for f in sorted(d.glob("cls_w*.jsonl")):
        s = set()
        for ln in open(f):
            r = json.loads(ln)
            s.add(r["canon"])
            info_by[r["canon"]] = r
            if r.get("start"):
                seeds.add(r["canon"])
        per[f.name] = s
    sets = list(per.values())
    print("classes per chain (T >= band):", {k: len(v) for k, v in per.items()})
    ref = REF_T.get(a.n or (next(iter(info_by.values()))["n"] if info_by else 18))
    if sets:
        for label, pred in ((f"T == {ref} (all)", lambda r: r["T"] == ref),
                            (f"T == {ref}, bridges >= 3", lambda r: r["T"] == ref and r["b"] >= 3),
                            (f"T == {ref}, bridges >= 1", lambda r: r["T"] == ref and r["b"] >= 1),
                            ("T > ref", lambda r: r["T"] > ref)):
            sub = [{c for c in s if pred(info_by[c])} for s in sets]
            S, Q, est = chao1(sub)
            print(f"  {label}: S_obs={S}, incidence {Q}, Chao1 N_hat={est:.0f}")
            sub2 = [x - seeds for x in sub]
            S, Q, est = chao1(sub2)
            print(f"      excluding chain-start (seed) classes: S_obs={S}, incidence {Q}, Chao1 N_hat={est:.0f}")
        top = [r for c, r in info_by.items() if r["T"] == ref and c not in seeds]
        print(f"  (histograms below: distinct T=={ref} classes that were never a chain start: {len(top)})")
        print("  (k, bridges) over distinct T==ref classes:",
              dict(sorted(Counter((r["k"], r["b"]) for r in top).items())))
        print("  bridges histogram (classes):", dict(sorted(Counter(r["b"] for r in top).items())))
        print("  k histogram (classes):", dict(sorted(Counter(r["k"] for r in top).items())))
    if a.heldout:
        ho = heldout_classes(a.heldout, a.n)
        found = {c for s in sets for c in s} - seeds
        got = found & set(ho)
        inc = Counter(c for s in sets for c in s if c in ho)
        print(f"held-out bridged classes: {len(ho)} distinct classes in the file, {len(got)} rediscovered"
              f" (chains hitting each: {sorted(inc.values(), reverse=True)})")
        for c in got:
            print("   ", c, {k: ho[c][k] for k in ("T", "k", "bridges")})
        newb = [r for c, r in info_by.items() if r["T"] == ref and r["b"] >= 1 and c not in ho]
        print(f"bridged T=={ref} classes found other than held-out: {len(newb)}",
              [(r['k'], r['b']) for r in newb][:20])
    return info_by


# ---------------------------------------------------------------- selftest
def selftest(a):
    n = a.n
    rng = random.Random(1)
    rows0 = load_rows([str(GALLERY / str(n))], n)
    rng.shuffle(rows0)
    gal = [t for t, _ in rows0[:40]]
    nchk = 0
    t0 = time.time()
    for toks in gal[:15]:
        T = count_T(toks, n)
        assert rows_from_tokens(toks, n) == replay_word(tokens_to_gens(toks), n).rows
        inf = info(toks, n)
        assert inf["T"] == T, (inf["T"], T)
        assert inf["Z"] - inf["D"] + 3 * inf["k"] == n * (n - 2) - 3 * T, inf   # the Lambda identity
        assert sum(inf["Zl"]) == inf["Z"] and sum(inf["Dl"]) == inf["D"]
        rows = rows_from_tokens(toks, n)
        w = sweep(rows, list(range(n)))
        assert w is not None and rows_from_tokens(w, n) == rows
        for d in rng.sample(range(n), 3):
            bt, bn = delete_lines(toks, n, [d])
            base = Base(bt, bn)
            r = base.best()
            assert r["T"] >= T, (r["T"], T)
            nt = base.word_of(r["path"], None)
            assert count_T(nt, n) == r["T"], (count_T(nt, n), r["T"])
            cnt, ps = base.paths(r["T"] - 1, 3000)
            for seq, fid in rng.sample(ps, min(5, len(ps))):
                nt = base.word_of(seq, fid)
                assert count_T(nt, n) >= r["T"] - 1
                nchk += 1
        bt, bn = delete_lines(toks, n, rng.sample(range(n), 2))
        base = Base(bt, bn)
        r = base.best()
        nt = base.word_of(r["path"], None)
        assert count_T(nt, n - 1) == r["T"]
    # exact two-line probe: with target = ref a 93 must be rediscovered and the witness word recounted
    if n in (16, 18):
        a2 = argparse.Namespace(**vars(a))
        a2.pair_target = REF_T[n]
        a2.out, a2.band = "/tmp", 99
        W = Walker(random.Random(3), Path("/tmp"), 99, a2)
        for toks in gal[:3]:
            W.visited.clear()
            res = W.pair_probe(toks, info(toks, n))
            assert res is not None and res[1] == REF_T[n] and W.st["pair_recount_mismatch"] == 0, (res, dict(W.st))
        print("pair probe ok:", dict(W.st))
    # canon invariance: every symmetry image has the same canonical id
    import numpy as np
    import coverage
    trip, P, F = coverage.tables(n)
    for toks in gal[:5]:
        gens = tokens_to_gens(toks)
        chi = coverage.chi_from_word(gens, n)
        v = np.array([chi[t] for t in trip], dtype=np.int8)
        c0 = coverage.canon(v, n)
        for i in rng.sample(range(P.shape[0]), 10):
            img = (F[i] * v[P[i]]).astype(np.int8)
            assert coverage.canon(img, n) == c0
    # bridge counter agrees with the metric stored in the held-out file (n=16)
    if n == 16 and (ROOT / "work/pls/bridge16_heldout.json").exists():
        for r in json.load(open(ROOT / "work/pls/bridge16_heldout.json")):
            i = info(extend_dp.parse_tokens(r["gens"]), 16)
            assert (i["T"], i["k"], i["b"]) == (r["T"], r["k"], r["bridges"]), (i, r)
    print(f"selftest ok (n={n}):", nchk, "sampled paths rebuilt and recounted; Lambda identity, canon invariance,"
          " bridge metric;", round(time.time() - t0, 1), "s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["selftest", "run", "stats"])
    ap.add_argument("dir", nargs="?")
    ap.add_argument("--n", type=int, default=18)
    ap.add_argument("--start", nargs="+", default=None, help="json/jsonl files, gallery dirs or globs")
    ap.add_argument("--first-frac", type=float, default=None, help="probability a start is drawn from the first --start file")
    ap.add_argument("--exclude-src", default=None, help="json rows whose src/name are dropped from --start")
    ap.add_argument("--heldout", default=None)
    ap.add_argument("--secs", type=int, default=3600)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--out", default="work/dpwalk2/run")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--chain-steps", type=int, default=2000)
    ap.add_argument("--stall", type=int, default=150)
    ap.add_argument("--band", type=int, default=None, help="canonical-class bookkeeping for T >= band (default ref T)")
    ap.add_argument("--wk", type=float, default=0.05)
    ap.add_argument("--wb", type=float, default=0.15)
    ap.add_argument("--kcap", type=int, default=None, help="cap on k in the score (bonus saturates)")
    ap.add_argument("--bcap", type=int, default=None, help="cap on bridges in the score")
    ap.add_argument("--wd", type=float, default=0.0)
    ap.add_argument("--wz", type=float, default=0.0)
    ap.add_argument("--zprob", type=float, default=0.5, help="fraction of Z-targeted deletions")
    ap.add_argument("--eps", type=float, default=0.5)
    ap.add_argument("--gamma", type=float, default=1.0)
    ap.add_argument("--zinc", type=float, default=0.0, help="credit to the other line at a simple end of an unused segment")
    ap.add_argument("--dbias", type=float, default=0.0, help="weight of doubly used segments in targeted deletion")
    ap.add_argument("--two-rate", type=float, default=0.15)
    ap.add_argument("--tlo", type=float, default=0.15)
    ap.add_argument("--thi", type=float, default=0.65)
    ap.add_argument("--cap", type=int, default=3000)
    ap.add_argument("--ncand", type=int, default=8)
    ap.add_argument("--cand-score", action="store_true", help="choose among candidates by full score, not T")
    ap.add_argument("--p-arch", type=float, default=0.25, help="chain restart from the walker's own archive")
    ap.add_argument("--p-bridge-arch", type=float, default=0.5)
    ap.add_argument("--pair-rate", type=float, default=0.0)
    ap.add_argument("--pair-minb", type=int, default=3)
    ap.add_argument("--pair-budget", type=float, default=120.0)
    ap.add_argument("--pair-target", type=int, default=None, help="default ref+1 (test only: lower it)")
    a = ap.parse_args()
    global N
    N = a.n
    if a.mode == "selftest":
        selftest(a)
    elif a.mode == "stats":
        a.dir = a.dir or a.out
        cmd_stats(a)
    else:
        if not a.start:
            a.start = [str(GALLERY / str(a.n))]
        from multiprocessing import Process
        Path(a.out).mkdir(parents=True, exist_ok=True)
        ps = [Process(target=run_worker, args=(w, a)) for w in range(a.workers)]
        for p in ps:
            p.start()
        for p in ps:
            p.join()


if __name__ == "__main__":
    main()

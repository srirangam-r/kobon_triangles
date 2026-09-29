"""DP-based large-neighbourhood ("ruin and recreate") walk over 18-line arrangements.

State = wiring word (list of (g, width)).  Move: delete 1 (or 2) lines, then re-insert with the exact compiled
one-line DP (search/dp1fast): best re-insertion or a sample among the top ones (.enum).  Acceptance: annealing
on  score = T + wk*k + wb*bridges  with a visited-state hash set (novelty preferred).  T >= 94 is re-verified
with two independent counters and written to work/dpwalk/HIT_*.json.

    uv run --no-project --with python-sat python search/dpwalk.py selftest
    uv run --no-project --with python-sat python search/dpwalk.py run --secs 3600 --workers 3 --out work/dpwalk/run1
    uv run --no-project --with python-sat python search/dpwalk.py stats work/dpwalk/run1
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
sys.path.insert(0, str(ROOT / "search" / "dp1fast"))
sys.path.append(str(ROOT / "work" / "t3"))  # inspect.py there shadows the stdlib: never first
sys.path.insert(0, str(ROOT / "work" / "research2"))
sys.path.insert(0, str(ROOT / "tools/external/kobon-solutions"))
import extend_dp  # noqa: E402
from dp1fast import Dp1  # noqa: E402
from verification.quick_check import count_triangles, replay_word  # noqa: E402

GALLERY = ROOT / "tools/external/kobon-solutions/gallery/data"
N = 18


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


def bridge_count(toks, n):
    """Doubly used bridges: segments between two triple points carrying triangles on both sides."""
    from arr import Arr
    a = Arr(tokens_to_gens(toks), n)
    ev = a.events
    br = set()
    for x in range(n):
        for e in range(len(a.rows[x]) - 1):
            u, v = a.rows[x][e], a.rows[x][e + 1]
            if len(a.t[x][e]) == 2 and len(ev[u]) == 3 and len(ev[v]) == 3:
                br.add(frozenset((u, v)))
    return len(br)


def n_triple(toks):
    return sum(1 for _, w in toks if w == 3)


# ---------------------------------------------------------------- the walk
class Walker:
    def __init__(self, rng, out_dir, wid, wk=0.05, wb=0.15, cap=3000):
        self.rng, self.out, self.wid = rng, out_dir, wid
        self.wk, self.wb, self.cap = wk, wb, cap
        self.visited = set()
        self.st = Counter()
        self.hist = Counter()          # (T, k, bridges) over distinct states
        self.best_T = 0
        self.d93 = {}                  # rows hash -> tokens (distinct T>=93 states)
        self.brc = {}                  # bridge cache
        self.t_dp = self.t_rest = 0.0

    def score(self, toks, T):
        k = n_triple(toks)
        b = 0
        if T >= 92:
            b = bridge_count(toks, N)
        return T + self.wk * k + self.wb * b, k, b

    def record(self, toks, T, rows):
        h = hash_rows(rows)
        new = h not in self.visited
        if new:
            self.visited.add(h)
            self.st["distinct"] += 1
            if T >= 92:
                k = n_triple(toks)
                b = bridge_count(toks, N)
                self.hist[(T, k, b)] += 1
            else:
                self.hist[(T, n_triple(toks), -1)] += 1
            if T >= 93 and h not in self.d93:
                self.d93[h] = toks
                with open(self.out / f"d93_w{self.wid}.jsonl", "a") as f:
                    f.write(json.dumps(dict(T=T, k=n_triple(toks), gens=tokens_to_gens(toks))) + "\n")
            if T > self.best_T:
                self.best_T = T
            if T >= 94:
                self.hit(toks)
        return new

    def hit(self, toks):
        t1, t2 = verify_hit(toks, N)
        rec = dict(T=t2, T_count_general=t1, gens=tokens_to_gens(toks), n=N)
        if t1 >= 94 and t2 >= 94:
            p = self.out.parent / f"HIT_{int(time.time())}_w{self.wid}.json"
            json.dump(rec, open(p, "w"))
            (self.out / "STOP").write_text("hit")
            print("HIT", rec, flush=True)
        else:
            self.st["false_hit"] += 1
            print("FALSE HIT (counters disagree)", rec, flush=True)

    def move(self, toks, T, temp, two):
        """One ruin&recreate.  Returns (new_toks, new_T, new_rows) or None."""
        rng = self.rng
        ds = rng.sample(range(N), 2 if two else 1)
        t0 = time.perf_counter()
        bt, bn = delete_lines(toks, N, ds)
        base = Base(bt, bn)
        r = base.best()
        self.st["dp_solves"] += 1
        Tmax = r["T"]
        if Tmax is None:
            return None
        if two:
            # greedy first re-insertion: sample among the top, then exact best for the second line
            cnt, ps = base.paths(Tmax, 200)
            seq, fid = rng.choice(ps) if ps else (r["path"], None)
            t1 = base.word_of(seq, fid)
            base2 = Base(t1, bn + 1)
            r2 = base2.best()
            self.st["dp_solves"] += 1
            Tmax = r2["T"]
            base = base2
        self.t_dp += time.perf_counter() - t0
        # choose candidate paths: threshold from temperature
        slack = 0 if temp < 0.2 else (1 if temp < 0.5 else 2)
        while True:
            thr = Tmax - slack
            cnt, ps = base.paths(thr, self.cap)
            if cnt <= self.cap or slack == 0:
                break
            slack -= 1
        if not ps:
            return None
        best = None
        for _ in range(min(8, len(ps))):
            seq, fid = rng.choice(ps)
            nt = base.word_of(seq, fid)
            rows = rows_from_tokens(nt, N)
            Tn = count_triangles(rows)
            h = hash_rows(rows)
            fresh = h not in self.visited
            key = (fresh, Tn, rng.random())
            if best is None or key > best[0]:
                best = (key, nt, Tn, rows)
            if fresh and Tn >= Tmax:
                break
        self.st["cand"] += 1
        return best[1], best[2], best[3], Tmax

    def chain(self, toks, deadline, steps, log):
        """Annealing chain from toks until deadline / steps moves."""
        rng = self.rng
        T = count_T(toks, N)
        rows = rows_from_tokens(toks, N)
        self.record(toks, T, rows)
        cur_s = self.score(toks, T)[0]
        stall = 0
        for it in range(steps):
            if time.time() > deadline or (self.out / "STOP").exists():
                return
            temp = 0.15 + 0.5 * ((it // 40) % 4) / 3          # 0.15..0.65 cycling
            two = rng.random() < 0.15
            t0 = time.perf_counter()
            res = self.move(toks, T, temp, two)
            self.st["moves"] += 1
            if two:
                self.st["moves2"] += 1
            self.t_rest += time.perf_counter() - t0
            if res is None:
                continue
            nt, Tn, rows_n, Tmax = res
            new = self.record(nt, Tn, rows_n)
            if not new:
                self.st["revisit"] += 1
            sc = self.score(nt, Tn)[0] if Tn >= T - 2 else Tn
            d = sc - cur_s
            if d >= 0 or rng.random() < math.exp(d / temp):
                if hash_rows(rows_n) != hash_rows(rows_from_tokens(toks, N)):
                    self.st["accept"] += 1
                toks, T, cur_s = nt, Tn, sc
                stall = 0 if T >= self.best_T - 1 else stall + 1
            else:
                stall += 1
            if stall > 150:
                return
            if log and self.st["moves"] % 200 == 0:
                print(f"w{self.wid} moves={self.st['moves']} distinct={self.st['distinct']} best={self.best_T} "
                      f"d93={len(self.d93)} cur={T}", flush=True)


def load_gallery(rng, nmax=None):
    files = sorted(glob.glob(str(GALLERY / str(N) / "*.json")))
    rng.shuffle(files)
    out = []
    for f in files[:nmax]:
        j = json.load(open(f))
        toks = extend_dp.parse_tokens(j["gens"])
        if len(j["lines"]) == N and max(g + w for g, w in toks) == N:
            rows = rows_from_tokens(toks, N)
            if all(sum(len(e) - 0 for e in r) >= 0 for r in rows) and \
                    len({p for r in rows for e in r for p in e}) == N:
                out.append(toks)
    return out


def random_start(rng):
    """Random restart: random n=18 word by inserting lines with random (non-optimal) DP paths starting from 2 lines."""
    toks = []
    n = 2
    toks = [(0, 2)]
    while n < N:
        base = Base(toks, n)
        r = base.best()
        thr = r["T"] - rng.choice((0, 1, 2, 3, 4))
        cnt, ps = base.paths(thr, 500)
        seq, fid = rng.choice(ps)
        toks = base.word_of(seq, fid)
        n += 1
    return toks


def load_pls17(rng):
    fs = glob.glob(str(ROOT / "work/pls/n17_*_w*.jsonl"))
    f = rng.choice(fs)
    lines = open(f).readlines()
    j = json.loads(rng.choice(lines))
    return extend_dp.parse_tokens(j["gens"])


def extend_to_18(rng, toks, n=17):
    base = Base(toks, n)
    r = base.best()
    cnt, ps = base.paths(r["T"], 200)
    seq, fid = rng.choice(ps)
    return base.word_of(seq, fid)


def run_worker(wid, args):
    rng = random.Random(args.seed * 1000 + wid)
    out = Path(args.out)
    W = Walker(rng, out, wid)
    deadline = time.time() + args.secs
    gal = load_gallery(rng)
    print(f"w{wid}: {len(gal)} gallery starts", flush=True)
    t_start = time.time()
    chains = 0
    while time.time() < deadline and not (out / "STOP").exists():
        c = chains % 4
        if c in (0, 1) or not W.d93:
            toks = rng.choice(gal)
            src = "gallery"
        elif c == 2 and W.d93:
            toks = rng.choice(list(W.d93.values()))
            src = "d93"
        else:
            try:
                if rng.random() < 0.5:
                    toks = extend_to_18(rng, load_pls17(rng))
                    src = "pls17+1"
                else:
                    toks = random_start(rng)
                    src = "random"
            except Exception as e:  # noqa: BLE001
                print("start fail", e, flush=True)
                continue
        chains += 1
        W.st["chains_" + src] += 1
        W.chain(toks, deadline, args.chain_steps, log=True)
        dump(W, out, t_start)
    dump(W, out, t_start)


def dump(W, out, t0):
    d = dict(wid=W.wid, secs=time.time() - t0, best_T=W.best_T, distinct_93=len(W.d93), stats=dict(W.st),
             t_dp_and_move_setup=W.t_dp, t_total_moves=W.t_rest,
             hist=[[list(k), v] for k, v in sorted(W.hist.items())])
    json.dump(d, open(out / f"stats_w{W.wid}.json", "w"))


def cmd_stats(args):
    d = Path(args.dir)
    tot = Counter()
    hist = Counter()
    secs = 0
    best = 0
    for f in sorted(d.glob("stats_w*.json")):
        j = json.load(open(f))
        tot.update(j["stats"])
        for k, v in j["hist"]:
            hist[tuple(k)] += v
        secs = max(secs, j["secs"])
        best = max(best, j["best_T"])
    keys = set()
    byk = Counter()
    for f in d.glob("d93_w*.jsonl"):
        for ln in open(f):
            j = json.loads(ln)
            keys.add(hashlib.sha1(j["gens"].encode()).hexdigest())
    print("workers secs", round(secs), "best T", best)
    print("counters", dict(tot))
    print("moves/s/core", round(tot["moves"] / max(secs, 1) / max(1, len(list(d.glob('stats_w*.json')))), 2))
    print("distinct-word 93s (by word, cross-worker)", len(keys))
    for name, ix in (("T", 0), ("k", 1), ("bridges", 2)):
        c = Counter()
        for key, v in hist.items():
            c[key[ix]] += v
        print(name, "histogram over distinct visited states:", dict(sorted(c.items())))
    c = Counter()
    for key, v in hist.items():
        if key[0] >= 93:
            c[(key[1], key[2])] += v
    print("(k,bridges) for T>=93:", dict(sorted(c.items())))


# ---------------------------------------------------------------- selftest
def selftest():
    rng = random.Random(1)
    gal = load_gallery(rng, 60)
    nchk = 0
    t0 = time.time()
    for toks in gal[:25]:
        T = count_T(toks, N)
        assert rows_from_tokens(toks, N) == replay_word(tokens_to_gens(toks), N).rows
        # rows->word roundtrip
        rows = rows_from_tokens(toks, N)
        w = sweep(rows, list(range(N)))
        assert w is not None and rows_from_tokens(w, N) == rows
        for d in rng.sample(range(N), 3):
            bt, bn = delete_lines(toks, N, [d])
            base = Base(bt, bn)
            r = base.best()
            assert r["T"] >= T, (r["T"], T)
            nt = base.word_of(r["path"], None)
            assert count_T(nt, N) == r["T"], (count_T(nt, N), r["T"])
            cnt, ps = base.paths(r["T"] - 1, 3000)
            for seq, fid in rng.sample(ps, min(5, len(ps))):
                nt = base.word_of(seq, fid)
                Tn = count_T(nt, N)
                assert Tn >= r["T"] - 1, (Tn, r["T"])
                assert base.word_of(seq, None) is not None
                nchk += 1
        # 2-line delete
        bt, bn = delete_lines(toks, N, rng.sample(range(N), 2))
        base = Base(bt, bn)
        r = base.best()
        nt = base.word_of(r["path"], None)
        assert count_T(nt, N - 1) == r["T"]
    print("selftest ok:", nchk, "sampled paths rebuilt and recounted;", round(time.time() - t0, 1), "s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["selftest", "run", "stats"])
    ap.add_argument("dir", nargs="?")
    ap.add_argument("--secs", type=int, default=3600)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--out", default="work/dpwalk/run")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--chain-steps", type=int, default=2000)
    args = ap.parse_args()
    if args.mode == "selftest":
        selftest()
    elif args.mode == "stats":
        cmd_stats(args)
    else:
        from multiprocessing import Process
        Path(args.out).mkdir(parents=True, exist_ok=True)
        ps = [Process(target=run_worker, args=(w, args)) for w in range(args.workers)]
        for p in ps:
            p.start()
        for p in ps:
            p.join()


if __name__ == "__main__":
    main()

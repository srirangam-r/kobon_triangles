"""dpwalk_c: the exact-DP ruin-and-recreate walk of search/dpwalk.py / dpwalk2.py with every per-move hot path in C.

Same walk as dpwalk.py: state = wiring word; move = delete 1 (or 2, greedy) lines and re-insert with the exact
one-line DP (best re-insertion, or a sample among the top ones); annealing acceptance on
T + wk*k + wb*bridges [+ wd*D - wz*Z]; visited-state dedupe; starts = gallery / own archive / n=17+1 / random;
T > ref re-verified with count_general + quick_check -> HIT_*.json + STOP.  The difference is only speed: deleting a
line, the DP graph build + solve + enumeration (dp1fast2's C), rebuilding the wiring word from the DP path, the
exact recount (T, k, bridges, Z, D), the row hash and the canonical-class hash all run in search/walkc.
Options of dpwalk2.py:  --n, --start FILE.. (json/jsonl/gallery dir/glob), --exclude-src, --wk/--wb/--wd/--wz,
--kcap/--bcap, --zprob/--eps/--gamma/--zinc/--dbias (Z-targeted deletion), --two-rate, --tlo/--thi, --cap/--ncand,
--cand-score, --p-arch/--p-bridge-arch, --band (canonical class bookkeeping, cls_w*.jsonl in dpwalk2's format).
Not ported: dpwalk2's --pair-rate exact two-line probe.  Extra: --audit P recounts a fraction P of all visited
states with quick_check.

    uv run --no-project --with python-sat --with numpy python search/dpwalk_c.py selftest
    uv run --no-project --with python-sat --with numpy python search/dpwalk_c.py run --n 18 --secs 300 --workers 3 \
        --out work/eng/T10/run5
    uv run --no-project --with python-sat --with numpy python search/dpwalk_c.py stats work/eng/T10/run5
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
sys.path.insert(1, str(ROOT / "search" / "walkc"))
sys.path.insert(2, str(ROOT / "work" / "lns" / "push"))
sys.path.append(str(ROOT / "work" / "t3"))  # inspect.py there shadows the stdlib: never first
sys.path.insert(3, str(ROOT / "work" / "research2"))
sys.path.insert(4, str(ROOT / "tools/external/kobon-solutions"))
import extend_dp  # noqa: E402
import walkc  # noqa: E402
from walkc import Base  # noqa: E402
from verification.quick_check import count_triangles, replay_word  # noqa: E402

GALLERY = ROOT / "tools/external/kobon-solutions/gallery/data"
REF_T = {14: 55, 15: 65, 16: 72, 17: 85, 18: 93}     # best known T per n (hit = REF_T + 1)


# ---------------------------------------------------------------- helpers
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


def verify_hit(word, n):
    """Independent recount with both reference counters."""
    from kobon_sat import count_general
    gens = walkc.gens(word)
    t1 = len(count_general(n, chi_from_word(gens, n)))
    t2 = count_triangles(replay_word(gens, n).rows)
    return t1, t2


def quick_T(word, n):
    return count_triangles(replay_word(walkc.gens(word), n).rows)


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
        self.classes = {}              # canon hash -> (T, k, b, word) for T >= band
        self.src = "?"
        self.tm = Counter()            # seconds per phase
        self._lines = (None, None)     # (word, count_lines) cache of the current state

    def score(self, st):
        """st = (T, k, bridges, Z, D)"""
        a = self.a
        k = min(st[1], a.kcap) if a.kcap is not None else st[1]
        b = min(st[2], a.bcap) if a.bcap is not None else st[2]
        return st[0] + a.wk * k + a.wb * b + a.wd * st[4] - a.wz * st[3]

    def record(self, word, st, h, start=False):
        new = h not in self.visited
        if new:
            T = st[0]
            self.visited.add(h)
            self.st["distinct"] += 1
            self.hist[(T, st[1], st[2])] += 1
            if self.a.audit and self.rng.random() < self.a.audit:
                self.st["audited"] += 1
                if quick_T(word, self.n) != T:
                    self.st["audit_mismatch"] += 1
                    print("AUDIT MISMATCH", walkc.gens(word), T, flush=True)
            if T >= self.band:
                ch, cb = walkc.canon(word, self.n)
                if ch not in self.classes:
                    self.classes[ch] = (T, st[1], st[2], word)
                    cid = hashlib.sha1(cb).hexdigest()[:16]
                    with open(self.out / f"cls_w{self.wid}.jsonl", "a") as f:
                        f.write(json.dumps(dict(n=self.n, T=T, k=st[1], b=st[2], D=st[4], Z=st[3], canon=cid,
                                                src=self.src, start=start, gens=walkc.gens(word))) + "\n")
                else:
                    self.st["class_dup"] += 1
            if T > self.best_T:
                self.best_T = T
            if T > self.ref:
                self.hit(word)
        return new

    def hit(self, word):
        t1, t2 = verify_hit(word, self.n)
        rec = dict(T=t2, T_count_general=t1, gens=walkc.gens(word), n=self.n)
        if t1 > self.ref and t2 > self.ref:
            p = self.out.parent / f"HIT_{self.n}_{int(time.time())}_w{self.wid}.json"
            json.dump(rec, open(p, "w"))
            (self.out / "STOP").write_text("hit")
            print("HIT", rec, flush=True)
        else:
            self.st["false_hit"] += 1
            print("FALSE HIT (counters disagree)", rec, flush=True)

    # -- which lines to delete
    def lines_info(self, word):
        if self._lines[0] is not word:
            self._lines = (word, walkc.count_lines(word, self.n))
        return self._lines[1]

    def pick_lines(self, word, two):
        a, rng, n = self.a, self.rng, self.n
        tg = rng.random() < a.zprob
        w = None
        if tg:
            inf = self.lines_info(word)
            Zl, Dl, Zi = inf[5], inf[6], inf[7]
            w = [(a.eps + Zl[x] + a.zinc * Zi[x] + a.dbias * Dl[x]) ** a.gamma for x in range(n)]
        d1 = rng.choices(range(n), weights=w)[0] if tg else rng.randrange(n)
        self.st["del_targeted" if tg else "del_uniform"] += 1
        if not two:
            return [d1]
        while True:
            d2 = rng.choices(range(n), weights=w)[0] if (tg and rng.random() < 0.5) else rng.randrange(n)
            if d2 != d1:
                return [d1, d2]

    def move(self, word, temp, two):
        """One ruin&recreate.  Returns (word, stats, rows hash, Tmax) or None."""
        rng, n, a = self.rng, self.n, self.a
        tm = self.tm
        ds = self.pick_lines(word, two)
        t0 = time.perf_counter()
        bw, bn = word, n
        for d in sorted(ds, reverse=True):
            bw = walkc.delete_line(bw, d, bn)
            bn -= 1
        base = Base(bw, bn)
        Tmax = base.solve_max()
        self.st["dp_solves"] += 1
        if Tmax is None:
            return None
        if two:
            cnt = base.enum(Tmax, 200)
            if cnt:
                path, start = base.path(rng.randrange(min(cnt, 200)))
            else:
                _, path, start = base.solve()
            base = Base(base.word_of(path, start), bn + 1)
            Tmax = base.solve_max()
            self.st["dp_solves"] += 1
        t1 = time.perf_counter()
        tm["dp"] += t1 - t0
        slack = 0 if temp < 0.2 else (1 if temp < 0.5 else 2)
        while True:
            cnt = base.enum(Tmax - slack, a.cap)
            if cnt <= a.cap or slack == 0:
                break
            slack -= 1
        t2 = time.perf_counter()
        tm["enum"] += t2 - t1
        if not cnt:
            return None
        m = min(cnt, a.cap)
        best = None
        for _ in range(min(a.ncand, m)):
            i = rng.randrange(m)
            nw, T, k, b, Z, D, h = base.eval(i)
            fresh = h not in self.visited
            st = (T, k, b, Z, D)
            if a.cand_score and T >= Tmax - 1:
                key = (fresh, self.score(st), rng.random())
            else:
                key = (fresh, T, rng.random())
            if best is None or key > best[0]:
                best = (key, nw, st, h)
            if fresh and T >= Tmax and not a.cand_score:
                break
        tm["eval"] += time.perf_counter() - t2
        self.st["cand"] += 1
        return best[1], best[2], best[3], Tmax

    def chain(self, word, deadline, steps, log):
        rng, a, n = self.rng, self.a, self.n
        st = walkc.count(word, n)
        self.record(word, st, walkc.rows_hash(word, n), start=True)
        cur_s = self.score(st)
        stall = 0
        for it in range(steps):
            if time.time() > deadline or (self.out / "STOP").exists():
                return
            temp = a.tlo + (a.thi - a.tlo) * ((it // 40) % 4) / 3
            two = rng.random() < a.two_rate
            t0 = time.perf_counter()
            res = self.move(word, temp, two)
            self.st["moves"] += 1
            if two:
                self.st["moves2"] += 1
            if res is None:
                self.tm["move_total"] += time.perf_counter() - t0
                continue
            nw, st_n, h_n, Tmax = res
            t1 = time.perf_counter()
            new = self.record(nw, st_n, h_n)
            self.tm["record"] += time.perf_counter() - t1
            self.tm["move_total"] += time.perf_counter() - t0
            if not new:
                self.st["revisit"] += 1
            sc = self.score(st_n)
            d = sc - cur_s
            if d >= 0 or rng.random() < math.exp(d / temp):
                self.st["accept"] += 1
                word, st, cur_s = nw, st_n, sc
                stall = 0 if st[0] >= self.best_T - 1 else stall + 1
            else:
                stall += 1
            if stall > a.stall:
                return
            if log and self.st["moves"] % 500 == 0:
                print(f"w{self.wid} moves={self.st['moves']} distinct={self.st['distinct']} best={self.best_T} "
                      f"classes={len(self.classes)} cur=(T{st[0]},k{st[1]},b{st[2]})", flush=True)


# ---------------------------------------------------------------- starts
def _expand(p):
    p = str(p)
    if os.path.isdir(p):
        return sorted(glob.glob(os.path.join(p, "*.json")) + glob.glob(os.path.join(p, "*.jsonl")))
    g = sorted(glob.glob(p))
    return g if g else [p]


def load_rows(paths, n, exclude=frozenset()):
    """Words (bytes) with n lines from json/jsonl files, gallery dirs, globs.  Rows with src/name in `exclude` (or
    file name in it) are dropped.  Returns [(word, src)]."""
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
                w = walkc.to_word(toks)
                if w in seen:
                    continue
                try:
                    walkc.canon(w, n)      # also rejects words with a parallel pair (chi incomplete)
                except ValueError:
                    continue
                rows = replay_word(r["gens"], n).rows
                if len({q for row in rows for e in row for q in e}) != n:
                    continue
                seen.add(w)
                out.append((w, name))
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


def random_start(rng, n):
    """Random n-line word grown from 2 lines by random (not necessarily optimal) DP paths."""
    word, m = walkc.to_word([(0, 2)]), 2
    while m < n:
        base = Base(word, m)
        T = base.solve_max()
        cnt = base.enum(T - rng.choice((0, 1, 2, 3, 4)), 500)
        word = base.word_of(*base.path(rng.randrange(min(cnt, 500))))
        m += 1
    return word


def load_pls17(rng):
    fs = glob.glob(str(ROOT / "work/pls/n17_*_w*.jsonl"))
    if not fs:
        raise FileNotFoundError("no work/pls/n17_*_w*.jsonl")
    j = json.loads(rng.choice(open(rng.choice(fs)).readlines()))
    return walkc.to_word(extend_dp.parse_tokens(j["gens"]))


def extend_by_one(rng, word, n):
    base = Base(word, n)
    T = base.solve_max()
    cnt = base.enum(T, 200)
    return base.word_of(*base.path(rng.randrange(min(cnt, 200))))


def run_worker(wid, a):
    rng = random.Random(a.seed * 1000 + wid)
    out = Path(a.out)
    W = Walker(rng, out, wid, a)
    deadline = time.time() + a.secs
    excl = load_exclude(a.exclude_src)
    legacy = not a.start          # dpwalk.py's start mix: gallery x2, own archive, n-1 + 1 / random
    pool = load_rows(a.start or [str(GALLERY / str(a.n))], a.n, excl)
    first = load_rows(a.start[:1], a.n, excl) if a.first_frac is not None and a.start else []
    rng.shuffle(pool)
    print(f"w{wid}: {len(pool)} starts" + (" (dpwalk.py start mix)" if legacy else ""), flush=True)
    t_start = time.time()
    chains = 0
    while time.time() < deadline and not (out / "STOP").exists():
        arch = list(W.classes.values())
        if legacy:
            c = chains % 4
            if c in (0, 1) or not arch:
                word, src = rng.choice(pool)
            elif c == 2:
                word, src = rng.choice(arch)[3], "arch"
            else:
                try:
                    if a.n == 18 and rng.random() < 0.5:
                        word, src = extend_by_one(rng, load_pls17(rng), 17), "pls17+1"
                    else:
                        word, src = random_start(rng, a.n), "random"
                except Exception as e:  # noqa: BLE001
                    print("start fail", e, flush=True)
                    chains += 1
                    continue
        else:
            if arch and rng.random() < a.p_arch:
                if rng.random() < a.p_bridge_arch and any(c[2] >= 1 for c in arch):
                    c = rng.choice([c for c in arch if c[2] >= 1])
                else:
                    c = rng.choice(arch)
                word, src = c[3], "arch"
            else:
                word, src = rng.choice(first if first and rng.random() < a.first_frac else pool)
        chains += 1
        W.src = src
        W.st["chains_" + (src if src in ("arch", "pls17+1", "random") else "start")] += 1
        W.chain(word, deadline, a.chain_steps, log=True)
        dump(W, out, t_start)
    dump(W, out, t_start)


def dump(W, out, t0):
    d = dict(wid=W.wid, secs=time.time() - t0, best_T=W.best_T, classes=len(W.classes), stats=dict(W.st),
             seconds_by_phase={k: round(v, 3) for k, v in W.tm.items()}, params={k: v for k, v in vars(W.a).items()},
             hist=[[list(k), v] for k, v in sorted(W.hist.items())])
    json.dump(d, open(out / f"stats_w{W.wid}.json", "w"))


# ---------------------------------------------------------------- stats
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
    tot, hist, phase = Counter(), Counter(), Counter()
    secs = best = nw = 0
    for f in sorted(d.glob("stats_w*.json")):
        j = json.load(open(f))
        tot.update(j["stats"])
        phase.update(j.get("seconds_by_phase", {}))
        for k, v in j["hist"]:
            hist[tuple(k)] += v
        secs, best, nw = max(secs, j["secs"]), max(best, j["best_T"]), nw + 1
    print("workers", nw, "secs", round(secs), "best T", best)
    print("counters", dict(tot))
    print("seconds by phase (summed over workers):", {k: round(v, 1) for k, v in phase.items()})
    print("moves/s/core", round(tot["moves"] / max(secs, 1) / max(1, nw), 2))
    for name, ix in (("T", 0), ("k", 1), ("bridges", 2)):
        c = Counter()
        for key, v in hist.items():
            c[key[ix]] += v
        print(name, "histogram over distinct visited states:", dict(sorted(c.items())))
    per, info_by, seeds = {}, {}, set()
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
    ref = REF_T.get(a.n)
    if sets and ref:
        for label, pred in ((f"T == {ref} (all)", lambda r: r["T"] == ref),
                            (f"T == {ref}, bridges >= 3", lambda r: r["T"] == ref and r["b"] >= 3),
                            ("T > ref", lambda r: r["T"] > ref)):
            sub = [{c for c in s if pred(info_by[c])} for s in sets]
            S, Q, est = chao1(sub)
            print(f"  {label}: S_obs={S}, incidence {Q}, Chao1 N_hat={est:.0f}")
        top = [r for c, r in info_by.items() if r["T"] == ref and c not in seeds]
        print(f"  distinct T=={ref} classes that were never a chain start: {len(top)}")
        print("  (k, bridges) over them:", dict(sorted(Counter((r["k"], r["b"]) for r in top).items())))


# ---------------------------------------------------------------- selftest
def selftest(a):
    n = a.n
    rng = random.Random(1)
    words = load_rows([str(GALLERY / str(n))], n)
    rng.shuffle(words)
    t0 = time.time()
    nchk = 0
    sys.path.insert(0, str(ROOT / "search" / "dp1fast2"))
    import dp1fast2
    for word, _ in words[:12]:
        assert walkc.count(word, n)[0] == quick_T(word, n)
        for d in rng.sample(range(n), 3):
            bw = walkc.delete_line(word, d, n)
            base = Base(bw, n - 1)
            Tm = base.solve_max()
            assert Tm == dp1fast2.Dp1(walkc.tokens(bw), n - 1).max_T()
            assert Tm >= walkc.count(word, n)[0]
            cnt = base.enum(Tm - 1, 500)
            for i in rng.sample(range(min(cnt, 500)), min(5, cnt, 500)):
                nw, T, k, b, Z, D, h = base.eval(i)
                assert T == quick_T(nw, n) >= Tm - 1 and (T, k, b, Z, D) == walkc.count(nw, n)
                nchk += 1
    # short walk with audit of every state
    a2 = argparse.Namespace(**vars(a))
    a2.audit = 1.0
    a2.band = 999
    Path("/tmp/dpwalk_c_selftest").mkdir(exist_ok=True)
    W = Walker(random.Random(2), Path("/tmp/dpwalk_c_selftest"), 0, a2)
    W.chain(words[0][0], time.time() + 60, 300, log=False)
    assert W.st["audit_mismatch"] == 0 and W.st["audited"] > 50, dict(W.st)
    print(f"selftest ok (n={n}): {nchk} rebuilt candidates recounted; walk of {W.st['moves']} moves, "
          f"{W.st['audited']} states audited with quick_check; {time.time() - t0:.1f}s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["selftest", "run", "stats"])
    ap.add_argument("dir", nargs="?")
    ap.add_argument("--n", type=int, default=18)
    ap.add_argument("--start", nargs="+", default=None, help="json/jsonl files, gallery dirs or globs")
    ap.add_argument("--first-frac", type=float, default=None, help="probability a start is drawn from the first --start file")
    ap.add_argument("--exclude-src", default=None, help="json rows whose src/name are dropped from --start")
    ap.add_argument("--secs", type=int, default=3600)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--out", default="work/dpwalk_c/run")
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
    ap.add_argument("--zprob", type=float, default=0.0, help="fraction of Z-targeted deletions (dpwalk.py: 0)")
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
    ap.add_argument("--p-arch", type=float, default=0.25, help="chain restart from the walker's own archive (--start mode)")
    ap.add_argument("--p-bridge-arch", type=float, default=0.5)
    ap.add_argument("--audit", type=float, default=0.0, help="fraction of new states recounted with quick_check")
    a = ap.parse_args()
    if a.mode == "selftest":
        selftest(a)
    elif a.mode == "stats":
        a.dir = a.dir or a.out
        cmd_stats(a)
    else:
        from multiprocessing import Process
        Path(a.out).mkdir(parents=True, exist_ok=True)
        ps = [Process(target=run_worker, args=(w, a)) for w in range(a.workers)]
        for p in ps:
            p.start()
        for p in ps:
            p.join()


if __name__ == "__main__":
    main()

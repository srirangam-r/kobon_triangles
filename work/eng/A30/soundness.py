"""A30 item 3: soundness of the FC / FD24 (and FS1-3) certificates on arrangements OUTSIDE the near-optimal corpus.

For each generated n = 18 arrangement (multiplicity <= 3) and each of the 5 initial certificates:
  (a) every real line's enriched-frame window sequence is a path of T25's product graph (NFA simulation on the exported graph),
  (b) DP value of that path (my exact window minima) <= D*(2*final_real + 2), where final_real = v_L + sum w.net comes from the
      independent reference code (real_line_vectors <- bbl_rules2 / rule_ref / bbl_hall),
  (c) final_real >= 0 for every line, and >= 1/24 for clean lines under FD24,
  (d) every rule column (all except a, alpha, wr) is conserved over the lines of the arrangement,
  (e) sum_L final_real <= 3*Lambda - n.
usage: soundness.py MODE COUNT SEED NPROC   (MODE in rand, mut, corpus)"""
import sys, pickle, random, collections, json, time
from fractions import Fraction as F
import numpy as np
ROOT = __import__("pathlib").Path(__file__).resolve().parents[3].as_posix()
sys.path.insert(0, ROOT + "/search"); sys.path.append(ROOT + "/work/t3"); sys.path.insert(0, ROOT + "/work/eng/A30/elim")
import __main__
import rule_lp as RL
__main__.EFrame = RL.EFrame
import line_automaton as LA
LA._imports()
import rule_lp_t25 as T
import dplib as DP
from arr import Arr
from bbl_rules import Charge

NCERT = 5
ST = None
G = None
CERTS = []
CSR = None
WID = None
TERMSET = None


def init():
    global ST, G, CERTS, CSR, WID, TERMSET
    ST = pickle.load(open(ROOT + "/work/eng/T25/elim/state_2.pkl", "rb"))
    G = DP.Graph(ROOT + "/work/eng/A30/elim/g_full.pkl")
    for c in ST["certs"][:NCERT]:
        D = c["D"]
        wcol = G.weights_vec(c["w"])
        wm = G.wmin_array(G.window_values(wcol, D))
        CERTS.append(dict(name=c["name"], D=D, W={k: F(x, D) for k, x in c["w"].items()}, wmin=wm))
    order = np.argsort(G.src, kind="stable")
    indptr = np.zeros(G.N + 1, dtype=np.int64)
    np.add.at(indptr, G.src + 1, 1)
    indptr = np.cumsum(indptr)
    CSR = (indptr, G.ew[order], G.dst[order])
    WID = {r: i for i, r in enumerate(G.win_repr)}
    TERMSET = set(zip(G.tn.tolist(), G.tw.tolist()))


def path_exists(wids):
    """NFA simulation: is the window sequence a path of the graph?"""
    indptr, ew, dst = CSR
    states = set(G.starts.tolist())
    for w in wids[:-1]:
        nxt = set()
        for u in states:
            a, b = indptr[u], indptr[u + 1]
            seg = ew[a:b]
            for j in np.nonzero(seg == w)[0]:
                nxt.add(int(dst[a + j]))
        if not nxt:
            return False
        states = nxt
    last = wids[-1]
    return any((u, last) in TERMSET for u in states)


# ------------------------------------------------------------------------------------------------ generators
def toks_of(word):
    out = []
    for t in word.split():
        out.append((int(t.rstrip("*")), 2 + t.count("*")))
    return out


def word_of(toks):
    return " ".join(str(g) + "*" * (w - 2) for g, w in toks)


def gen_rand(rng, n=18, big=None):
    big = rng.choice([0.0, 0.1, 0.25, 0.5]) if big is None else big
    wires = list(range(n))
    toks = []
    while True:
        moves = []
        for g in range(n - 1):
            if wires[g] < wires[g + 1]:
                moves.append((g, 2))
                if g + 2 < n and wires[g + 1] < wires[g + 2]:
                    moves.append((g, 3))
        if not moves:
            break
        if rng.random() < big:
            cand = [mv for mv in moves if mv[1] == 3] or moves
        else:
            cand = [mv for mv in moves if mv[1] == 2] or moves
        g, w = rng.choice(cand)
        wires[g:g + w] = wires[g:g + w][::-1]
        toks.append((g, w))
    assert wires == sorted(wires, reverse=True)
    return toks


def mutate(toks, rng, steps):
    toks = list(toks)
    for _ in range(steps):
        i = rng.randrange(len(toks))
        mv = rng.random()
        if mv < 0.5 and i + 1 < len(toks):
            (g1, w1), (g2, w2) = toks[i], toks[i + 1]
            if g2 >= g1 + w1 or g1 >= g2 + w2:
                toks[i], toks[i + 1] = toks[i + 1], toks[i]
        elif i + 2 < len(toks):
            a, b, c = toks[i], toks[i + 1], toks[i + 2]
            if a == c and a[1] == 2 and b[1] == 2 and abs(a[0] - b[0]) == 1 and (a[0] + 1 == b[0] or b[0] + 1 == a[0]):
                if rng.random() < 0.6:
                    toks[i:i + 3] = [b, a, b]                        # braid move
                else:
                    g = min(a[0], b[0])
                    toks[i:i + 3] = [(g, 3)]                         # simple triangle -> triple point
            elif a[1] == 3 and rng.random() < 0.5:
                g = a[0]
                pat = rng.choice([[(g, 2), (g + 1, 2), (g, 2)], [(g + 1, 2), (g, 2), (g + 1, 2)]])
                toks[i:i + 1] = pat
        if toks[i % len(toks)][1] == 3 and rng.random() < 0.0:
            pass
    return toks


_REC = {}


def corpus_words(fn, rng, k):
    if fn not in _REC:
        L = []
        for r in LA.records(fn):
            g = r["gens"] if isinstance(r["gens"], str) else " ".join(r["gens"])
            if r.get("n", 18) == 18:
                L.append(g)
        _REC[fn] = L
    lines = _REC[fn]
    return rng.sample(lines, min(k, len(lines)))


# ------------------------------------------------------------------------------------------------ check one arrangement
def check_word(word, c):
    try:
        a = Arr(word, 18)
        ch = Charge(a)
    except Exception as e:
        c["build_fail"] += 1
        return
    a = ch.a
    if a.n != 18 or any(sum(len(a.events[e]) - 1 for e in a.rows[L]) != a.n - 1 for L in range(a.n)):
        c["incomplete"] += 1
        return
    if any(len(ev) > 3 for ev in a.events):
        c["mult4"] += 1
        return
    c["arr"] += 1
    ntr = sum(1 for ev in a.events if len(ev) == 3)
    c["triple_points"] += ntr
    if ntr == 0:
        c["simple_arr"] += 1
    Tn = a.T()
    c[f"T_{Tn // 10 * 10}"] += 1
    n = 18
    lam3 = 3 * (n * (n - 2) - 3 * Tn) - n
    res, unk = T.real_line_vectors(a, None, t1pp=True, extras=True)
    # windows of each line
    wins = {}
    for L in range(n):
        ef, hids = RL.eframes_of_line(ch, L)
        ws = LA.line_windows(ef)
        wins[L] = (ef, ws)
    colsum = [collections.Counter() for _ in CERTS]
    tot = collections.Counter()
    for L in range(n):
        ef, ws = wins[L]
        reprs = [repr(w) for w in ws]
        ids = [WID.get(r) for r in reprs]
        ok_path = None
        if any(i is None for i in ids):
            c["line_window_not_in_graph"] += 1
            ok_path = False
            if c["line_window_not_in_graph"] <= 5:
                print("WINDOW NOT IN GRAPH", word[:80], L, [r for r, i in zip(reprs, ids) if i is None][:1], flush=True)
        else:
            ok_path = path_exists(ids)
            if not ok_path:
                c["line_not_a_path"] += 1
                if c["line_not_a_path"] <= 5:
                    print("LINE NOT A PATH", word[:80], L, flush=True)
        c["lines"] += 1
        v, nt = res[L]
        for k, x in nt.items():
            if k not in (("a",), ("alpha",), ("wr",)) and k[0] != "U":
                tot[k] += x
        clean = all(f.kind == "S" and not (f.bin[0] and f.bout[0]) and not (f.bin[1] and f.bout[1]) for f in ef)
        if clean:
            c["clean_lines"] += 1
        for ci, cert in enumerate(CERTS):
            fin = F(v)
            for k, x in nt.items():
                wk = cert["W"].get(k)
                if wk:
                    fin += wk * x
            colsum[ci][L] = fin
            if fin < 0:
                c[f"neg_final_{cert['name']}"] += 1
                if c[f"neg_final_{cert['name']}"] <= 3:
                    print("NEGATIVE FINAL", cert["name"], word[:80], L, fin, flush=True)
            if fin == 0:
                c[f"tight_{cert['name']}"] += 1
            if cert["name"] == "FD24" and clean and fin < F(1, 24):
                c["clean_below_1_24"] += 1
                if c["clean_below_1_24"] <= 3:
                    print("CLEAN BELOW 1/24", word[:80], L, fin, flush=True)
            if ok_path:
                dpv = sum(int(cert["wmin"][i]) for i in ids)
                bound = cert["D"] * (2 * fin + 2)
                if dpv > bound:
                    c[f"dp_exceeds_real_{cert['name']}"] += 1
                    if c[f"dp_exceeds_real_{cert['name']}"] <= 3:
                        print("DP VALUE EXCEEDS REAL", cert["name"], word[:80], L, dpv, bound, flush=True)
                elif dpv == bound:
                    c[f"dp_equal_real_{cert['name']}"] += 1
    bad = [k for k, x in tot.items() if x != 0]
    if bad:
        c["nonconserved_arr"] += 1
        if c["nonconserved_arr"] <= 3:
            print("NONCONSERVED", word[:80], bad[:3], flush=True)
    for ci, cert in enumerate(CERTS):
        s = sum(colsum[ci].values())
        if s > lam3:
            c[f"identity_violation_{cert['name']}"] += 1
            if c[f"identity_violation_{cert['name']}"] <= 3:
                print("IDENTITY VIOLATION", cert["name"], word[:80], s, lam3, flush=True)
        if s < 0:
            c[f"neg_sum_{cert['name']}"] += 1
        if lam3 == 0:
            c["T94"] += 1


def worker(args):
    mode, count, seed = args
    rng = random.Random(seed)
    c = collections.Counter()
    words = []
    if mode == "rand":
        for _ in range(count):
            words.append(word_of(gen_rand(rng)))
    elif mode == "mut":
        srcs = ["near18.jsonl", "dpwalk2_18.jsonl", "dpwalk93.jsonl", "gallery18.jsonl", "pls18_93.jsonl", "bridge93.jsonl"]
        for _ in range(count):
            if rng.random() < 0.3:
                toks = gen_rand(rng)
            else:
                fn = ROOT + "/work/phi/" + rng.choice(srcs)
                w = corpus_words(fn, rng, 1)
                if not w:
                    continue
                toks = toks_of(w[0])
            words.append(word_of(mutate(toks, rng, rng.choice([5, 20, 60, 200, 600]))))
    elif mode == "corpus":
        srcs = ["near18.jsonl", "dpwalk2_18.jsonl", "dpwalk93.jsonl", "gallery18.jsonl", "pls18_93.jsonl", "bridge93.jsonl"]
        for fn in srcs:
            words += corpus_words(ROOT + "/work/phi/" + fn, rng, count // len(srcs))
    for w in words:
        check_word(w, c)
    return dict(c)


if __name__ == "__main__":
    mode, count, seed, nproc = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    init()
    import multiprocessing as mp
    t0 = time.time()
    tasks = [(mode, count // nproc, seed * 1000 + i) for i in range(nproc)]
    tot = collections.Counter()
    with mp.get_context("fork").Pool(nproc) as pool:
        for r in pool.imap_unordered(worker, tasks):
            tot.update(r)
    print(f"[{mode} seed {seed}] {dict(sorted(tot.items()))} {time.time()-t0:.0f}s")

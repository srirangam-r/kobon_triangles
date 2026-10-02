"""A30 item 4: test the ILP5 identity families on random REAL arrangements (not near-optimal only).
families tested (per arrangement, exactly):
  F0  number of lines = 18 (trivial)
  F4  sum_L tri_L = 3T            tri_L  = sum over frames of (bout0 + bout1)
  F5  sum_L cor_L = 3T            cor_L  = sum_S (bout0+bin0+bin1+bout1)/2 + sum_T (6 sector bits)/3
  F6  sum_L end_L = 0             end_L  = sum_S (ub0+ub1) - #(S frames that are first/last)
  F7  sum_L nT_L = 3 t            (t = number of triple points)
  F8  for every triple point: the 3 lines see the same canonical cfg, and the roles of its three lines are a permutation of cfg_row(cfg)
  F9  simple vertices: the two lines through a simple vertex see the same D4-class of the 4 sector bits (so class counts are 2 x #vertices)
  F3  rule columns (all keys except a, alpha, wr): sum over lines of the net count = 0 (conservation)
usage: ilp_identities.py MODE COUNT SEED     (MODE rand|mut|corpus)"""
import sys, collections, random, time
from fractions import Fraction as F
ROOT = __import__("pathlib").Path(__file__).resolve().parents[4].as_posix()
sys.path.insert(0, ROOT + "/search"); sys.path.append(ROOT + "/work/t3"); sys.path.insert(0, ROOT + "/work/eng/A30"); sys.path.insert(0, ROOT + "/work/eng/T25/elim")
import __main__
import rule_lp as RL
__main__.EFrame = RL.EFrame
import line_automaton as LA
LA._imports()
import rule_lp_t25 as T
from arr import Arr
from bbl_rules import Charge
import soundness as S      # only for generators (gen_rand, mutate, corpus_words); init() is not called

def d4(bits):
    b = tuple(bits)
    imgs = []
    for k in range(4):
        imgs.append(tuple(b[(k + i) % 4] for i in range(4)))
        imgs.append(tuple(b[(k - i) % 4] for i in range(4)))
    return min(imgs)

def chr_of(info):
    return "U" if info is None else ("T" if info[0] == "T" else "S")

def test(word, c):
    try:
        a = Arr(word, 18); ch = Charge(a)
    except Exception:
        c["build_fail"] += 1; return
    a = ch.a
    if any(sum(len(a.events[e]) - 1 for e in a.rows[L]) != a.n - 1 for L in range(a.n)) or any(len(ev) > 3 for ev in a.events):
        c["skipped"] += 1; return
    c["arr"] += 1
    n = 18; Tn = a.T()
    t = sum(1 for ev in a.events if len(ev) == 3)
    tri = cor = end = nT = F(0)
    seen_pt = collections.defaultdict(list)       # triple event -> [(cfg, role) of each line]
    seen_sv = collections.defaultdict(list)       # simple event -> [d4 class]
    for L in range(n):
        ef, hids = RL.eframes_of_line(ch, L)
        wins = LA.line_windows(ef)
        m = len(ef)
        for i, f in enumerate(ef):
            tri += f.bout[0] + f.bout[1]
            V = a.rows[L][i]
            if f.kind == "S":
                cor += F(f.bout[0] + f.bin[0] + f.bin[1] + f.bout[1], 2)
                end += f.ub[0] + f.ub[1] - (1 if i in (0, m - 1) else 0)
                seen_sv[V].append(d4((f.bout[0], f.bin[0], f.bin[1], f.bout[1])))
            else:
                cor += F(f.bout[0] + f.h[0] + f.bin[0] + f.bin[1] + f.h[1] + f.bout[1], 3)
                nT += 1
                prev, cur, nxt = wins[i]
                sig, g = hids[i]
                ring = [chr_of(nxt), "T" if sig[0] else "S", "T" if sig[2] else "S", chr_of(prev), "T" if sig[3] else "S", "T" if sig[1] else "S"]
                sec6 = (cur.bout[0], cur.h[0], cur.bin[0], cur.bin[1], cur.h[1], cur.bout[1])
                cr = T.cfg_role("".join(ring).replace("T", "N"), sec6, 0)
                seen_pt[V].append((cr, "U" in ring))
    if tri != 3 * Tn: c["F4_fail"] += 1
    if cor != 3 * Tn: c["F5_fail"] += 1
    if end != 0: c["F6_fail"] += 1; 
    if nT != 3 * t: c["F7_fail"] += 1
    for V, lst0 in seen_pt.items():
        c["triple_points"] += 1
        if any(u for (_, u) in lst0):
            c["F8_skipped_line_ends_at_point"] += 1      # a line ends here: its ring has the letter U (such windows are not in SURV)
            continue
        lst = [x for (x, _) in lst0]
        if len(lst) != 3 or any(x is None for x in lst): c["F8_none_role"] += 1; continue
        cfgs = {x[0] for x in lst}
        if len(cfgs) != 1: c["F8_cfg_mismatch"] += 1; continue
        cfg = next(iter(cfgs))
        row = T.cfg_row(cfg)
        if collections.Counter(x[1] for x in lst) != collections.Counter(row): c["F8_role_mismatch"] += 1
        c["F8_ok"] += 1
    for V, lst in seen_sv.items():
        c["simple_vertices"] += 1
        if len(lst) != 2 or lst[0] != lst[1]: c["F9_fail"] += 1
    # F3 conservation
    res, unk = T.real_line_vectors(a, None, t1pp=True, extras=True)
    tot = collections.Counter()
    for L, (v, nt) in res.items():
        for k, x in nt.items():
            if k not in (("a",), ("alpha",), ("wr",)) and k[0] != "U":
                tot[k] += x
    if any(x != 0 for x in tot.values()): c["F3_fail"] += 1
    c["F3_columns_seen"] = max(c["F3_columns_seen"], len(tot))

if __name__ == "__main__":
    mode, count, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    rng = random.Random(seed)
    c = collections.Counter()
    srcs = ["near18.jsonl", "dpwalk2_18.jsonl", "dpwalk93.jsonl", "gallery18.jsonl", "pls18_93.jsonl", "bridge93.jsonl"]
    t0 = time.time()
    for _ in range(count):
        if mode == "rand":
            w = S.word_of(S.gen_rand(rng, 18))
        elif mode == "mut":
            if rng.random() < 0.3:
                toks = S.gen_rand(rng)
            else:
                w0 = S.corpus_words(ROOT + "/work/phi/" + rng.choice(srcs), rng, 1)
                toks = S.toks_of(w0[0])
            w = S.word_of(S.mutate(toks, rng, rng.choice([5, 20, 60, 200, 600])))
        else:
            w = S.corpus_words(ROOT + "/work/phi/" + rng.choice(srcs), rng, 1)[0]
        test(w, c)
    print(f"[{mode} seed {seed}] {dict(sorted(c.items()))} {time.time()-t0:.0f}s")

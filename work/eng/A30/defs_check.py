"""A30: direct check of B = C, A = 3/2 C, sum v0 + 3/2 C = 3 Lambda - n per arrangement, with explicit definitions.
A = sum_L nt[a]     = sum_L (3 own_L - 3/2 touch_L)            (own = own unused bounded segments, touch = touch events)
B = sum_L nt[alpha] = sum_L (3 s_L - 1 - v_L),  s_L = (n-2) - tri_L, v_L = value in real_line_vectors before the a=0 shift (portion split a=1/3)
C = sum_L nt[wr]    = sum_L sum_{own unused segments of L} (number of TRIPLE endpoints of the segment)
V0 = sum_L (v_L - own_L + touch_L/2)   (value at a = 0)"""
import sys, random, collections
from fractions import Fraction as F
ROOT = __import__("pathlib").Path(__file__).resolve().parents[3].as_posix()
sys.path.insert(0, ROOT + "/work/eng/A30")
import soundness as S
from arr import Arr
from bbl_rules import Charge
import rule_lp_t25 as T
import line_automaton as LA
rng = random.Random(77)
srcs = ["near18.jsonl", "dpwalk2_18.jsonl", "dpwalk93.jsonl", "gallery18.jsonl", "pls18_93.jsonl", "bridge93.jsonl"]
c = collections.Counter(); rel = collections.Counter()
for mode in ("rand", "mut", "corpus"):
    for _ in range(2500):
        if mode == "rand": w = S.word_of(S.gen_rand(rng))
        elif mode == "mut": w = S.word_of(S.mutate(S.toks_of(S.corpus_words(ROOT + "/work/phi/" + rng.choice(srcs), rng, 1)[0]), rng, rng.choice([20, 200, 600])))
        else: w = S.corpus_words(ROOT + "/work/phi/" + rng.choice(srcs), rng, 1)[0]
        try: a = Arr(w, 18); ch = Charge(a)
        except Exception: continue
        a = ch.a
        if any(sum(len(a.events[e]) - 1 for e in a.rows[L]) != 17 for L in range(18)) or any(len(ev) > 3 for ev in a.events): continue
        res, _ = T.real_line_vectors(a, None, t1pp=True, extras=True)
        # independent recomputation of own/touch/tri/wr from frames
        A = B = C = V0 = F(0); sumS = 0; vbase_sum = F(0)
        Cdirect = 0
        for L in range(18):
            v0, nt = res[L]
            frames, _h = LA.extract(ch, L); frames = LA.normalise(frames); m = len(frames)
            own = sum(1 for i in range(m - 1) if frames[i].bout == LA.NONE)
            touch = sum(1 for f in frames if f.kind == "S" for k in (0, 1) if not f.ub[k] and f.bin[k] + f.bout[k] == 0)
            tri = sum(frames[i].bout[0] + frames[i].bout[1] for i in range(m - 1))
            s_ = 16 - tri; sumS += s_
            Cdirect += sum(int(frames[i].kind == "T") + int(frames[i + 1].kind == "T") for i in range(m - 1) if frames[i].bout == LA.NONE)
            A += F(nt.get(("a",), 0)); B += F(nt.get(("alpha",), 0)); C += F(nt.get(("wr",), 0)); V0 += F(v0)
            vL = F(v0) + own - F(touch, 2)           # back to the a=1/3 value
            vbase_sum += vL
        lam = 18 * 16 - 3 * a.T()
        c["arr"] += 1
        c["B==C"] += B == C; c["A==1.5C"] += A == F(3, 2) * C; c["V0+1.5C==3Lam-n"] += V0 + F(3, 2) * C == 3 * lam - 18
        c["sum s == Lambda"] += sumS == lam; c["C==direct triple-endpoint count"] += C == Cdirect
        c["B==3Lam-n-sum v(1/3)"] += B == 3 * lam - 18 - vbase_sum
        c["C>0"] += C > 0
        rel[(int(B), int(C))] += 0
print(dict(c))

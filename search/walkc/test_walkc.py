"""Validation of walkc against the Python reference implementations.

    uv run --no-project --with python-sat --with numpy python search/walkc/test_walkc.py [--nwords 1200] [--ncases 400]

Parts (all on gallery words with n = 10..18, stratified over the directories, plus bridge-rich n=16/18 records, so
that a large share of the words has triple points):
  A. delete_line == extend_dp.delete_wire (tokens) and == delete_line.delete on rows, every line of every word.
  B. count() == quick_check.count_triangles (T), == work/t3 Arr (T, k, Z, D, per-line Z / D / incident Z) and
     bridges == test_k5L_layer.geometry(Arr)[1]; rows_hash consistent with the arrangement (equal for
     commutation-equivalent words).
  C. canon_bytes == coverage.canon(chi vector) byte for byte, canon_hash == hash of those bytes; the walk's
     symmetry images (canonical form of the image chi vectors) agree.
  D. rows_to_word: mode 0 tokens == dpwalk.sweep, mode 1 gens == audit_planted.rows_to_word, both round-trip to the
     same rows.
  E. insert_path / Base: for deleted-line bases the exact one-line optimum equals dpwalk.Base (dp1fast + Python
     rebuild); the enumerated path counts are equal and the rebuilt words are token-for-token equal to
     dpwalk.Base.word_of (hinted, and unhinted for the argmax path), recount to the DP value; eval() == count().
"""
import argparse
import collections
import glob
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.insert(1, str(ROOT / "search" / "walkc"))
sys.path.insert(2, str(ROOT / "search" / "dp1fast"))
sys.path.append(str(ROOT / "work" / "t3"))          # inspect.py there shadows the stdlib
sys.path.insert(3, str(ROOT / "work" / "research2"))
sys.path.insert(4, str(ROOT / "tools/external/kobon-solutions"))
import numpy as np  # noqa: E402
import walkc  # noqa: E402
import extend_dp  # noqa: E402
import dpwalk  # noqa: E402  (T6 reference: Base.word_of / paths / sweep)
import coverage  # noqa: E402
from arr import Arr  # noqa: E402
from delete_line import delete as row_delete  # noqa: E402
from audit_planted import rows_to_word as audit_rows_to_word  # noqa: E402
from test_k5L_layer import geometry  # noqa: E402
from verification.quick_check import count_triangles, replay_word  # noqa: E402

G = ROOT / "tools/external/kobon-solutions/gallery/data"


def words(nwords, seed=11):
    """[(toks, n, label)]: gallery n = 10..18 (complete arrangements only) + bridge-rich records."""
    rnd = random.Random(seed)
    by = collections.defaultdict(list)
    for d in sorted(G.iterdir()):
        nm = d.name.split("-")[0]
        if d.is_dir() and nm.isdigit() and 10 <= int(nm) <= 18:
            by[d.name] = sorted(d.glob("*.json"))
    out = []
    for name, fs in by.items():
        for f in rnd.sample(fs, min(len(fs), max(20, 4 * nwords // len(by)))):
            j = json.load(open(f))
            toks = extend_dp.parse_tokens(j["gens"])
            n = len(j["lines"])
            out.append((toks, n, f"{name}/{f.name}"))
    extra = []
    for f in (ROOT / "work/dpwalk/bridge93.json", ROOT / "work/pls/bridge16_heldout.json"):
        if f.exists():
            for r in json.load(open(f)):
                toks = extend_dp.parse_tokens(r["gens"])
                extra.append((toks, max(g + w for g, w in toks), f.name))
    rnd.shuffle(extra)
    out += extra[:max(60, nwords // 8)]
    rnd.shuffle(out)
    good = []
    for toks, n, lab in out:
        if max(g + w for g, w in toks) != n or walkc_parallel(toks, n):
            continue
        good.append((toks, n, lab))
    return good[:nwords]


def walkc_parallel(toks, n):
    a = list(range(n))
    seen = set()
    for g, w in toks:
        b = a[g:g + w]
        for i in range(w):
            for j in range(i + 1, w):
                seen.add((min(b[i], b[j]), max(b[i], b[j])))
        a[g:g + w] = b[::-1]
    return len(seen) != n * (n - 1) // 2


def ref_info(toks, n):
    """dpwalk2.info (T, k, b, Z, D, Zl, Dl, Zi) computed from the work/t3 Arr, reimplemented here."""
    a = Arr(dpwalk.tokens_to_gens(toks), n)
    ev = a.events
    Zl, Dl, Zi = [0] * n, [0] * n, [0] * n
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
    return a, (a.T(), len(a.triples), len(br), sum(Zl), sum(Dl), Zl, Dl, Zi)


def rows_of(toks, n):
    return tuple(tuple(frozenset(e) for e in r) for r in dpwalk.rows_from_tokens(toks, n))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nwords", type=int, default=1200)
    ap.add_argument("--ncases", type=int, default=400, help="deleted-line bases for part E")
    ap.add_argument("--parts", default="ABCDE")
    args = ap.parse_args()
    rnd = random.Random(5)
    W = words(args.nwords)
    ntrip = sum(1 for t, n, _ in W if any(w == 3 for _, w in t))
    byn = collections.Counter(n for _, n, _ in W)
    print(f"{len(W)} words, {ntrip} with triple points, by n: {dict(sorted(byn.items()))}", flush=True)
    fails = collections.Counter()
    checks = collections.Counter()

    def ok(name, cond, info=""):
        checks[name] += 1
        if not cond:
            fails[name] += 1
            if fails[name] <= 3:
                print("MISMATCH", name, info, flush=True)

    t0 = time.time()
    # ------------------------------------------------------------------ A. delete
    if "A" in args.parts:
        for toks, n, lab in W:
            rows0 = rows_of(toks, n)
            for d in range(n):
                ref = extend_dp.delete_wire(toks, n, d)
                got = walkc.delete_line(toks, d, n)
                ok("A delete tokens", got == ref, (lab, d))
                ok("A delete bytes", walkc.delete_line(walkc.to_word(toks), d, n) == walkc.to_word(ref))
                ok("A delete rows", rows_of(got, n - 1) == tuple(tuple(r) for r in row_delete(rows0, d)), (lab, d))
        print(f"A done {time.time() - t0:.1f}s", dict(checks), flush=True)

    # ------------------------------------------------------------------ B. count
    if "B" in args.parts:
        for toks, n, lab in W:
            a, ref = ref_info(toks, n)
            T_qc = count_triangles(replay_word(dpwalk.tokens_to_gens(toks), n).rows)
            got = walkc.count_lines(toks, n)
            ok("B T vs quick_check", got[0] == T_qc == ref[0], (lab, got[0], T_qc, ref[0]))
            ok("B (T,k,b,Z,D) vs Arr", tuple(got[:5]) == tuple(ref[:5]), (lab, got[:5], ref[:5]))
            ok("B per-line Zl,Dl,Zi", got[5] == ref[5] and got[6] == ref[6] and got[7] == ref[7], lab)
            ok("B bridges vs geometry()", got[2] == len(geometry(a)[1]), (lab, got[2], len(geometry(a)[1])))
            ok("B count()", walkc.count(toks, n) == tuple(got[:5]))
            ok("B Lambda identity", got[3] - got[4] + 3 * got[1] == n * (n - 2) - 3 * got[0], lab)
            # hash: commutation-equivalent words (mode-1 sweep of the same rows) hash equal; a different arrangement doesn't
            w1 = walkc.rows_to_word(rows_of(toks, n), None, 1)
            ok("B rows_hash commutation-invariant", walkc.rows_hash(w1, n) == walkc.rows_hash(toks, n), lab)
        # different arrangements: distinct hashes
        hs = collections.Counter(walkc.rows_hash(t, n) for t, n, _ in W)
        keys = collections.Counter(dpwalk.hash_rows(dpwalk.rows_from_tokens(t, n)) for t, n, _ in W)
        ok("B rows_hash collisions == python hash(rows) collisions", sorted(hs.values()) == sorted(keys.values()))
        print(f"B done {time.time() - t0:.1f}s", flush=True)

    # ------------------------------------------------------------------ C. canon
    if "C" in args.parts:
        for toks, n, lab in W:
            gens = dpwalk.tokens_to_gens(toks)
            chi = coverage.chi_from_word(gens, n)
            trip, P, F = coverage.tables(n)
            v = np.array([chi[t] for t in trip], dtype=np.int8)
            ref = coverage.canon(v, n)
            h, cb = walkc.canon(toks, n)
            ok("C canon bytes", cb == ref, lab)
            ok("C canon hash", h == walkc.hash_bytes(ref) == walkc.canon_hash(toks, n), lab)
            # symmetry images of the chi vector have the same canonical form (checks the tables as used in C)
            for i in rnd.sample(range(P.shape[0]), 3):
                img = (F[i] * v[P[i]]).astype(np.int8)
                ok("C image canon", coverage.canon(img, n) == cb)
            # independently derived symmetries of the wiring word: vertical flip (g -> n-g-w) and left-right reversal
            # (token order reversed); the canonical hash must not change, while the labelled rows hash does.
            flip = [(n - g - w, w) for g, w in toks]
            rev = toks[::-1]
            for nm, w2 in (("flip", flip), ("reverse", rev), ("flip+reverse", flip[::-1])):
                ok(f"C symmetry invariance ({nm})", walkc.canon_hash(w2, n) == h and walkc.canon_bytes(w2, n) == cb, lab)
                ok(f"C {nm} still a word (same T)", walkc.count(w2, n)[:2] == walkc.count(toks, n)[:2], lab)
        print(f"C done {time.time() - t0:.1f}s", flush=True)

    # ------------------------------------------------------------------ D. rows -> word
    if "D" in args.parts:
        for toks, n, lab in W:
            rows = dpwalk.rows_from_tokens(toks, n)
            order = list(range(n))
            ref0 = dpwalk.sweep(rows, order)
            got0 = walkc.rows_to_word(rows, order, 0)
            ok("D mode0 == dpwalk.sweep", got0 == ref0, lab)
            ok("D mode0 round trip", got0 is not None and dpwalk.rows_from_tokens(got0, n) == rows, lab)
            refa = audit_rows_to_word([tuple(r) for r in rows], n)
            got1 = walkc.rows_to_word(rows, order, 1)
            ok("D mode1 == audit_planted.rows_to_word", got1 is not None and dpwalk.tokens_to_gens(got1) == refa, lab)
            ok("D mode1 round trip", got1 is not None and dpwalk.rows_from_tokens(got1, n) == rows, lab)
            # non-identity start order + failing input: a shifted order must fail identically
            perm = list(range(n))
            rnd.shuffle(perm)
            ok("D bad order agrees", walkc.rows_to_word(rows, perm, 0) == dpwalk.sweep(rows, perm), lab)
        print(f"D done {time.time() - t0:.1f}s", flush=True)

    # ------------------------------------------------------------------ E. insert_path / Base
    if "E" in args.parts:
        cases = 0
        npaths = collections.Counter()
        tp_py = tp_c = 0.0
        pool = [x for x in W if x[1] >= 12]
        while cases < args.ncases:
            toks, n, lab = rnd.choice(pool)
            nd = 2 if rnd.random() < 0.2 else 1
            ds = rnd.sample(range(n), nd)
            # Python reference base, then the same base in walkc (built from the word the C delete produced)
            bt_ref, bn = dpwalk.delete_lines(toks, n, ds)
            bt = toks
            nn = n
            for d in sorted(ds, reverse=True):
                bt = walkc.delete_line(bt, d, nn)
                nn -= 1
            ok("E delete_lines", bt == bt_ref)
            t = time.perf_counter()
            pb = dpwalk.Base(bt_ref, bn)
            r = pb.best()
            tp_py += time.perf_counter() - t
            t = time.perf_counter()
            cb = walkc.Base(bt, bn)
            Tm = cb.solve_max()
            tp_c += time.perf_counter() - t
            ok("E solve_max == python best", Tm == r["T"], (lab, ds, Tm, r["T"]))
            ok("E solve_max == solve_max_ref (dp1_solve_max)", cb.solve_max_ref() == Tm)
            Ts, path, pstart = cb.solve()
            ok("E solve() T", Ts == r["T"])
            # argmax path: unhinted rebuild equals python unhinted, recounts to T
            w_ref = dpwalk.Base.word_of(pb, r["path"], None)
            w_c = walkc.insert_path(bt, path, None, bn)
            ok("E argmax unhinted == python", w_c == w_ref, (lab, ds))
            ok("E argmax recount", walkc.count(w_c, bn + 1)[0] == r["T"] == count_triangles(dpwalk.rows_from_tokens(w_c, bn + 1)),
               (lab, ds))
            wh = cb.word_of(path, pstart)
            ok("E argmax hinted recount", walkc.count(wh, bn + 1)[0] == r["T"])
            for slack in (0, 1, 2):
                thr = r["T"] - slack
                cnt_py, ps = pb.paths(thr, 300)
                cnt_c = cb.enum(thr, 300)
                ok("E enum count", cnt_c == cnt_py, (lab, ds, slack, cnt_c, cnt_py))
                # fused scalar-memo enum == dp1_enum (K-table DP): same count, same paths in the same order
                fbuf, fsb = cb._enum
                fbuf, fsb = fbuf.copy(), fsb.copy()
                cnt_r = cb.enum_ref(thr, 300)
                rb, rsb = cb._enum
                m_ = min(cnt_r, 300)
                ok("E fused enum == dp1_enum", cnt_r == cnt_c and np.array_equal(fbuf[:m_ * cb._stride], rb[:m_ * cb._stride])
                   and np.array_equal(fsb[:m_], rsb[:m_]), (lab, ds, slack, cnt_c, cnt_r))
                cnt_c = cb.enum(thr, 300)
                idx = list(range(min(cnt_py, 300)))
                if len(idx) > 12:
                    idx = rnd.sample(idx, 12)
                for i in idx:
                    seq, fid = ps[i]
                    ref_w = pb.word_of(seq, fid)
                    p, st = cb.path(i)
                    got_w = cb.word_of(p, st)
                    ok("E hinted word == python", walkc.tokens(got_w) == ref_w, (lab, ds, slack, i))
                    ok("E standalone insert_path", walkc.insert_path(bt, p, st, bn) == ref_w)
                    T_ref = count_triangles(dpwalk.rows_from_tokens(ref_w, bn + 1))
                    ok("E recount >= thr", T_ref >= thr - 0, (T_ref, thr))
                    wd, T_, k_, b_, Z_, D_, h_ = cb.eval(i)
                    ok("E eval word", walkc.tokens(wd) == ref_w)
                    ok("E eval stats", (T_, k_, b_, Z_, D_) == walkc.count(wd, bn + 1) and T_ == T_ref)
                    ok("E eval hash", h_ == walkc.rows_hash(wd, bn + 1))
                    npaths[slack] += 1
            cases += 1
        print(f"E: {cases} bases; solve_max {tp_c / cases * 1e3:.2f} ms vs python {tp_py / cases * 1e3:.2f} ms;"
              f" rebuilt paths checked {dict(npaths)}  {time.time() - t0:.1f}s", flush=True)

    print("\nchecks:", json.dumps(dict(checks)))
    print("FAILURES:", dict(fails) if fails else "none")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()

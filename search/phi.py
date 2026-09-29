"""Master-inequality accounting (work/t3/general.md sections 1-3) for a wiring-word arrangement.

  Lambda = n(n-2) - 3T = Z - D + sum_P k_P(k_P-2)
  2Lambda >= n + Phi,  Phi = sigma + x - 2*beta + sum_P h_P + Cred,
  h_P = 2k(k-2) - 2D_P - k - caps_P,   Cred = sum_{non-clean L} kappa(L) + Z_tr
  2Z = sum_L kappa(L) + Z_tr

The slack s = 2*Lambda - n - Phi is decomposed exactly:
  s = clean_excess + capmult,  clean_excess = sum_{clean L}(kappa(L)-1),
  capmult = sum over cap lines C avoiding all multiple points of (#points capped by C - 1).

analyze(gens, n) returns a dict with every term (global, per point, per line) and an 'errors' list that
must be empty (identity / master-inequality failures are bugs).  Wiring words contain triple points only.

CLI:  python search/phi.py selftest <n> <in>...   (cross-check against independent code)
      python search/phi.py <in> <out.jsonl> [--n N] [--limit K] [--workers W]
  <in> is a .json/.jsonl/directory-glob of records with a "gens" field (list or jsonl).
"""
import collections
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT / "work/t3"))     # never first: work/t3/inspect.py shadows the stdlib
from arr import Arr, rays, first_seg, far_end  # noqa: E402


def analyze(gens, n=None):
    a = Arr(gens, n)
    n = a.n
    ev, rows, pos = a.events, a.rows, a.pos
    errors = []
    mult = [eid for eid, e in enumerate(ev) if len(e) > 2]
    if any(len(ev[m]) > 3 for m in mult):
        raise ValueError("4-fold points are not representable in wiring words")
    ismult = lambda eid: len(ev[eid]) > 2
    kP = {m: len(ev[m]) for m in mult}

    # ---- basic counts (all read off the t-sequences, independent of the identities checked below)
    T, Z, D = a.T(), a.Z(), a.D()
    S = sum(len(r) - 1 for r in rows)
    sumk = sum(k * (k - 2) for k in kP.values())
    Lam = n * (n - 2) - 3 * T
    if S != n * (n - 2) - sumk:
        errors.append("S != n(n-2)-sum k(k-2)")
    if 3 * T != S - Z + D:
        errors.append("3T != S-Z+D")
    if Lam != Z - D + sumk:
        errors.append("Lambda != Z-D+sum k(k-2)")

    # ---- multiple lines, sigma
    mult_on = collections.defaultdict(list)          # line -> multiple event ids (in line order)
    for L in range(n):
        for eid in rows[L]:
            if ismult(eid):
                mult_on[L].append(eid)
    sigma = sum(len(v) - 1 for v in mult_on.values() if len(v) >= 2)
    n_multlines = len(mult_on)
    if n_multlines != sum(kP.values()) - sigma:
        errors.append("multiple-line count != sum k - sigma")

    # ---- bridges
    bridges = []
    e_P = collections.Counter()
    for L in range(n):
        for e in range(len(rows[L]) - 1):
            u, v = rows[L][e], rows[L][e + 1]
            if ismult(u) and ismult(v) and len(a.t[L][e]) == 2:
                bridges.append((L, e, u, v))
                e_P[u] += 1
                e_P[v] += 1
    beta = len(bridges)

    # ---- triangles: vertex multiplicity profile, faces per point
    tri_vs = []
    tri_at = collections.Counter()
    tri_mult_profile = collections.Counter()
    allmult_face_at = collections.Counter()
    for f in a.tris:
        vs = set()
        for (x, e, _) in f:
            vs |= {rows[x][e], rows[x][e + 1]}
        if len(vs) != 3:
            errors.append("triangle with %d vertices" % len(vs))
        tri_vs.append(vs)
        nm = sum(ismult(v) for v in vs)
        tri_mult_profile[nm] += 1
        for v in vs:
            if ismult(v):
                tri_at[v] += 1
                if nm == 3:
                    allmult_face_at[v] += 1

    # ---- blocks (doubly used first segments with simple far end), D_P
    blocks = {}          # P -> list of (ray idx, line, direction, X, cap line)
    for P in mult:
        rs = rays(a, P)
        bl = []
        for k, r in enumerate(rs):
            fs = first_seg(a, P, r)
            if fs is None:
                continue
            L, e = fs
            if len(a.t[L][e]) == 2:
                X = far_end(a, P, r)
                if not ismult(X):
                    (c,) = ev[X] - {L}
                    bl.append((k, L, r[1], X, c))
        blocks[P] = bl
    # independent recount of D_P and bridges from segment scan
    Dp_scan = collections.Counter()
    for L in range(n):
        for e in range(len(rows[L]) - 1):
            if len(a.t[L][e]) == 2:
                u, v = rows[L][e], rows[L][e + 1]
                if ismult(u) != ismult(v):
                    Dp_scan[u if ismult(u) else v] += 1
                elif not ismult(u):
                    errors.append("L1 violated: doubly used segment with two simple ends")
    for P in mult:
        if Dp_scan[P] != len(blocks[P]):
            errors.append("D_P mismatch at %d" % P)
    D_P = {P: len(blocks[P]) for P in mult}
    if D != sum(D_P.values()) + beta:
        errors.append("D != sum D_P + beta")

    caps = {P: sorted({b[4] for b in blocks[P]}) for P in mult}
    line_has_mult = set(mult_on)
    x_P = {P: sum(1 for c in caps[P] if c in line_has_mult) for P in mult}
    x = sum(x_P.values())
    h_P = {P: 2 * kP[P] * (kP[P] - 2) - 2 * D_P[P] - kP[P] - len(caps[P]) for P in mult}
    sumh = sum(h_P.values())

    # cap counts
    capped_by = collections.Counter()
    for P in mult:
        for c in caps[P]:
            capped_by[c] += 1
    capline = set(capped_by)
    clean = [L for L in range(n) if L not in line_has_mult and L not in capline]
    capmult = sum(c - 1 for L, c in capped_by.items() if L not in line_has_mult)

    # ---- unused segments, touches
    lemA = set()         # (line, seg idx, X) Lemma-A touches
    lemA_at = collections.Counter()
    mutual_at = collections.Counter()
    unb_at = collections.Counter()
    for P in mult:
        for (k, L, d, X, c) in blocks[P]:
            p = pos[L][P]
            e = p + 1 if d == +1 else p - 2
            if not (0 <= e < len(a.t[L])):
                unb_at[P] += 1
            elif not a.t[L][e]:
                lemA.add((L, e, X))
                lemA_at[P] += 1
            else:
                mutual_at[P] += 1

    kappa = collections.Counter()
    Ztr = 0
    touch_kind = collections.Counter()   # clean / A / capother / multi(-line, non-A)
    zcarrier = collections.Counter()
    zsegs = []
    for L in range(n):
        for e, s in enumerate(a.t[L]):
            if s:
                continue
            u, v = rows[L][e], rows[L][e + 1]
            cls = ("clean" if L not in line_has_mult and L not in capline else
                   "multi+cap" if L in line_has_mult and L in capline else
                   "multi" if L in line_has_mult else "cap")
            ends = "".join(sorted(("m" if ismult(w) else "s") for w in (u, v)))
            zcarrier[(cls, ends)] += 1
            zsegs.append((L, e, cls, ends))
            for X in (u, v):
                if ismult(X):
                    Ztr += 1
                else:
                    (t,) = ev[X] - {L}
                    kappa[t] += 1
                    if t in clean:
                        touch_kind["clean"] += 1
                    elif (L, e, X) in lemA:
                        touch_kind["A"] += 1
                    elif t in line_has_mult:
                        touch_kind["multi"] += 1
                    else:
                        touch_kind["capother"] += 1
    if 2 * Z != sum(kappa.values()) + Ztr:
        errors.append("2Z != sum kappa + Ztr")
    if len(lemA) != sum(1 for _ in lemA):
        errors.append("lemA")
    cred_touch = sum(kappa[L] for L in range(n) if L not in clean)
    Cred = cred_touch + Ztr
    if cred_touch != touch_kind["A"] + touch_kind["multi"] + touch_kind["capother"]:
        errors.append("touch classification mismatch")
    clean_excess = sum(kappa[L] - 1 for L in clean)
    for L in clean:
        if kappa[L] < 1:
            errors.append("L3 violated: clean line %d has kappa 0" % L)

    Phi = sigma + x - 2 * beta + sumh + Cred
    slack = 2 * Lam - n - Phi
    if slack != clean_excess + capmult + 2 * (D - sum(D_P.values()) - beta):
        errors.append("slack decomposition fails (s=%d, clean_excess=%d, capmult=%d)" % (slack, clean_excess, capmult))
    if len(clean) != n - sum(kP.values()) + sigma - (sum(len(c) for c in caps.values()) - x) + capmult:
        errors.append("clean count formula fails")
    if slack < 0:
        errors.append("master inequality violated: s=%d" % slack)

    # ---- point classification
    pts = []
    for P in mult:
        bl = blocks[P]
        b = len(bl)
        ks = sorted(t[0] for t in bl)
        e = e_P[P]
        if b == 3:
            kind = "C"
        elif b == 2:
            kind = "X" if (ks[1] - ks[0]) % 6 == 3 else "V"
            if kind == "X" and e > 0:
                kind = "F"
        elif b == 1:
            rs = rays(a, P)
            k0 = ks[0]
            nb_mult = any(far_end(a, P, rs[(k0 + s) % 6]) is not None and ismult(far_end(a, P, rs[(k0 + s) % 6]))
                          for s in (1, 5))
            kind = "O1b" if nb_mult else "O1a"
        else:
            kind = "O0"
        killed = kind in ("X", "F") and lemA_at[P] == 0
        pts.append(dict(id=P, lines=sorted(ev[P]), k=kP[P], b=b, kind=kind, e=e, D=D_P[P], caps=caps[P],
                        x=x_P[P], h=h_P[P], A=lemA_at[P], mutual=mutual_at[P], unb=unb_at[P], killed=killed,
                        tri=tri_at[P], allmult=allmult_face_at[P],
                        phi_loc=h_P[P] + x_P[P] + lemA_at[P] - e_P[P]))
    lines = []
    for L in range(n):
        cls = ("clean" if L in clean else "multi+cap" if (L in line_has_mult and L in capline) else
               "multi" if L in line_has_mult else "cap")
        lines.append(dict(L=L, cls=cls, j=len(mult_on.get(L, [])), kappa=kappa[L],
                          Z=sum(1 for s in a.t[L] if not s), capof=capped_by[L]))
    kinds = collections.Counter(p["kind"] for p in pts)
    sig = " ".join("%s%d" % (k, kinds[k]) for k in ("X", "F", "V", "C", "O1a", "O1b", "O0") if kinds[k])
    return dict(n=n, T=T, Z=Z, D=D, S=S, Lam=Lam, k=len(mult), sigma=sigma, beta=beta, x=x, sumh=sumh,
                Cred=Cred, Ztr=Ztr, cred_A=touch_kind["A"], cred_multi=touch_kind["multi"],
                cred_capother=touch_kind["capother"], clean_touch=touch_kind["clean"], nclean=len(clean),
                Phi=Phi, slack=slack, clean_excess=clean_excess, capmult=capmult,
                two_lam_minus_n=2 * Lam - n, sig=sig, kinds=dict(kinds),
                tri_mult=dict(tri_mult_profile), nkill=sum(p["killed"] for p in pts),
                zcarrier={"%s/%s" % k: v for k, v in zcarrier.items()},
                points=pts, lines=lines, errors=errors)


# ---------------------------------------------------------------------------------- CLI
def _load(spec):
    """yield (id, n, gens) from a json list / jsonl file / glob of gallery json files"""
    out = []
    for path in sorted(glob.glob(spec)) or [spec]:
        txt = open(path).read()
        try:
            d = json.loads(txt)
            recs = d if isinstance(d, list) else [d]
        except json.JSONDecodeError:
            recs = [json.loads(l) for l in txt.splitlines() if l.strip()]
        for i, r in enumerate(recs):
            out.append((f"{Path(path).name}#{i}", r.get("n"), r["gens"], r))
    return out


SLIM = False


def _work(item):
    rid, n, gens, meta = item
    try:
        r = analyze(gens, n)
    except Exception as ex:  # report, do not hide
        return dict(id=rid, exception=repr(ex))
    r["id"] = rid
    r["src_T"] = meta.get("T")
    if SLIM:
        r.pop("lines")
        if not r["k"]:
            r.pop("points")
        else:
            r["gens"] = gens
    else:
        r["gens"] = gens
    return r


def main(argv):
    import argparse
    import multiprocessing as mp
    ap = argparse.ArgumentParser()
    ap.add_argument("inp")
    ap.add_argument("out")
    ap.add_argument("--n", type=int)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--dedup", action="store_true")
    ap.add_argument("--slim", action="store_true", help="drop gens/lines, and points when k=0")
    ap.add_argument("--minT", type=int)
    ap.add_argument("--maxT", type=int)
    args = ap.parse_args(argv)
    items = []
    for spec in args.inp.split(","):
        items += _load(spec)
    if args.minT is not None:
        items = [it for it in items if (it[3].get("T") or 0) >= args.minT]
    if args.maxT is not None:
        items = [it for it in items if (it[3].get("T") or 0) <= args.maxT]
    global SLIM
    SLIM = args.slim
    if args.n:
        items = [(i, args.n if n is None else n, g, m) for (i, n, g, m) in items]
    if args.dedup:
        seen, keep = set(), []
        for it in items:
            if it[2] not in seen:
                seen.add(it[2])
                keep.append(it)
        items = keep
    if args.limit:
        items = items[:args.limit]
    bad = 0
    with mp.Pool(min(args.workers, 3)) as pool, open(args.out, "w") as f:
        for r in pool.imap(_work, items, chunksize=32):
            if "exception" in r or r["errors"]:
                bad += 1
            f.write(json.dumps(r) + "\n")
    print(f"{len(items)} arrangements, {bad} with errors/exceptions -> {args.out}")


def selftest(paths, n, limit=150):
    """Cross-check T (count_general on chi) and blocks/bridges/all-multiple faces (test_k5L_layer.geometry)."""
    sys.path.append(str(ROOT / "search"))
    from kobon_sat import count_general
    from test_k5L_layer import geometry
    from base2 import chi_from_word
    bad = tested = 0
    for path in paths:
        for rid, nn, gens, meta in _load(path)[:limit]:
            nn = nn or n
            r = analyze(gens, nn)
            a = Arr(gens, nn)
            chi = chi_from_word(gens, nn)
            ok = len(count_general(nn, chi)) == r["T"]
            blocks, bridges, faces = geometry(a)
            ok &= sorted(len(v) for v in blocks.values()) == sorted(p["D"] for p in r["points"])
            ok &= len(bridges) == r["beta"]
            ok &= len(faces) == r["tri_mult"].get(3, 0)
            tested += 1
            if not ok:
                bad += 1
                print("MISMATCH", rid)
    print(f"selftest: {tested} arrangements, {bad} mismatches")


if __name__ == "__main__":
    if sys.argv[1:2] == ["selftest"]:
        selftest(sys.argv[3:], int(sys.argv[2]))
    else:
        main(sys.argv[1:])

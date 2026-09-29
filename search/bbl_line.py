"""Per-line (ray-split) form of the generalized BBL charge.

Each triple point splits 3c_P = (3/2)(N_P - D_P) over its rays: an N ray carries +3/2, a block ray -3/2, a bridge ray 0.
With portions p_L (own unused segments + touches) this gives the exact identity

    3 Lambda = sum_L E_L + waste,   E_L = p_L + (3/2)(N_L - B_L),

where N_L, B_L count the N and block rays along L at the triple points of L. BBL target: E_L >= 1 for every line.

    python search/bbl_line.py <in>... [--limit N] [--show 20]
"""
import argparse
import collections
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search"))
sys.path.append(str(ROOT / "work/t3"))
from arr import Arr, rays  # noqa: E402
from cluster import records  # noqa: E402
from bbl_rules import Charge  # noqa: E402
from bbl_adversary import portions  # noqa: E402

H = F(3, 2)


def line_rays(ch):
    """L -> list of (P, ray index, status) in order along L (two rays per triple point: -dir then +dir)."""
    a = ch.a
    out = {}
    for L in range(a.n):
        seq = []
        for P in ch.onl[L]:
            rs = rays(a, P)
            for d in (-1, +1):
                i = rs.index((L, d))
                seq.append((P, i, ch.st[P][i]))
        out[L] = seq
    return out


def line_values(ch, rec=None):
    rec = portions(ch) if rec is None else rec
    lr = line_rays(ch)
    E = {}
    for L in range(ch.a.n):
        nN = sum(1 for _, _, s in lr[L] if s == "N")
        nB = sum(1 for _, _, s in lr[L] if s == "B")
        E[L] = rec[L] + H * (nN - nB)
    return E, lr, rec


def signature(ch, L, lr, rec):
    """run structure along L: runs separated by '|', ray pair per point, plus caps capped by L and p_L"""
    caps = sum(1 for b in ch.blk if b[5] == L)
    seq = lr[L]
    s = []
    for k in range(0, len(seq), 2):
        s.append(seq[k][2] + seq[k + 1][2])
    return f"{' '.join(s) or '-'} caps={caps} p={rec[L]}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--limit", type=int, default=10 ** 9)
    ap.add_argument("--show", type=int, default=20)
    a = ap.parse_args()
    dist = collections.Counter()
    bad = collections.Counter()
    ex = {}
    cnt = 0
    for inp in a.inputs:
        seen = set()
        for r in records(inp):
            g = r["gens"] if isinstance(r["gens"], str) else " ".join(r["gens"])
            if g in seen:
                continue
            seen.add(g)
            try:
                ch = Charge(Arr(g, r.get("n")))
            except ValueError:
                continue
            cnt += 1
            E, lr, rec = line_values(ch)
            lam = ch.lam
            assert 3 * lam >= sum(E.values()), (g, lam, sum(E.values()))
            for L, v in E.items():
                dist[v] += 1
                if v < 1:
                    sg = signature(ch, L, lr, rec)
                    bad[(str(v), sg)] += 1
                    ex.setdefault((str(v), sg), g)
            if cnt >= a.limit:
                break
    print(f"{cnt} arrangements; E_L distribution:", {str(k): v for k, v in sorted(dist.items())})
    print(f"lines below 1: {sum(bad.values())} in {len(bad)} signatures")
    for k, v in bad.most_common(a.show):
        print(f"  {v:7d}  E={k[0]:>5}  {k[1]}")


if __name__ == "__main__":
    main()

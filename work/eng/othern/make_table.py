"""Builds TABLE.md from log_table_dp_n*.log (+ the earlier n=14,16,20 logs).  Pure arithmetic + log parsing."""
import re, math
from pathlib import Path
from fractions import Fraction as F
H = Path(__file__).resolve().parent
rec = {8: 15, 10: 25, 12: 38, 14: 54, 16: 72, 18: 93, 20: 117}   # records listed in the repo (SUMMARY.md); others unknown to the repo
old = {14: "log_a30dp_FC.log", 16: "log_a30dp_FC.log", 20: "log_a30dp_FC.log"}
rows = []
for n in range(6, 42, 2):
    W = n - 1
    txt = ""
    for f in [H / f"log_table_dp_n{n}.log", H / old.get(n, "none")]:
        if f.exists(): txt += f.read_text()
    m = re.search(rf"W={W} min D\*\(2\*final\+2\) = (\S+)\s+need >= (\S+)\s+final_min = (\S+)\s+(OK|FAIL)", txt)
    wall = re.search(r"wall (\d+) s", txt)
    if not m: rows.append((n, None)); continue
    mn, need, fm, st = m.groups()
    N = n * (n - 2)
    lam = math.ceil(F(n, 3))
    while (lam - N) % 3: lam += 1
    Tb = (N - lam) // 3
    tam, bbl, blanc = N // 3, (n * (3 * n - 7)) // 9, (n * (2 * n - 5)) // 6
    rows.append((n, dict(mn=mn, fm=fm, st=st, lam=lam, T=Tb, tam=tam, bbl=bbl, blanc=blanc, wall=wall.group(1) if wall else "-")))
print("Columns vs Tamura/BBL/Blanc: the bound value and how our T bound compares (BBL and Blanc are for SIMPLE arrangements only).")
print()
print("| n | W=n-1 | DP min D(2f+2) (need 32) | final_min | status | Lambda_min | T <= | record (repo) | vs Tamura | vs BBL | vs Blanc (even n) |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for n, r in rows:
    if r is None: print(f"| {n} | {n-1} | not run | | | | | | | | |"); continue
    ok = r["st"] == "OK"
    T = r["T"] if ok else "n/a (FAIL)"
    rc = rec.get(n, "unknown")
    cmp = lambda b: (f"{b}: ours better by {b - r['T']}" if b > r["T"] else f"{b}: equal" if b == r["T"] else f"{b}: ours weaker by {r['T'] - b}") if ok else "-"
    print(f"| {n} | {n-1} | {r['mn']} | {r['fm']} | {r['st']} | {r['lam']} | {T} | {rc} | {cmp(r['tam'])} | {cmp(r['bbl'])} | {cmp(r['blanc'])} |")

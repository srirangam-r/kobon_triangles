"""Apply point-level discharging rules (from bbl_dischargelp.py --out) and report points with final cost > 6.
    python search/bbl_dcheck.py rules.json <in>...
"""
import collections, json, sys
from fractions import Fraction as F
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "search")); sys.path.append(str(ROOT / "work/t3"))
from arr import Arr
from cluster import records
from bbl_rules import Charge
from bbl_point import costs
from bbl_unit import units
from bbl_charge import point_type
from bbl_dischargelp import graph

rules = {(r["frm"], r["to"], r["edge"]): F(r["w"]).limit_denominator(36) for r in json.load(open(sys.argv[1]))}
bad = collections.Counter(); ex = {}; cnt = pts = 0; unseen = collections.Counter()
known = set(t for t, _, _ in rules) | set(t for _, t, _ in rules)
for inp in sys.argv[2:]:
    seen = set()
    for r in records(inp):
        g = r["gens"] if isinstance(r["gens"], str) else " ".join(r["gens"])
        if g in seen: continue
        seen.add(g)
        try: ch = Charge(Arr(g, r.get("n")))
        except ValueError: continue
        cnt += 1
        cost, sig, st = costs(ch)
        tau = {P: "".join(point_type(ch.st[P])) + ":" + "".join(sorted(sig[P])) for P in ch.a.triples}
        us, _ = units(ch, True)
        exempt = set()
        for K in us:
            if len(K) == 2 and sorted(tau[P].split(":")[1] for P in K) == ["IpMt", "IpMt"]: exempt |= K
        fin = collections.defaultdict(F, cost)
        for p, q, k in graph(ch, st):
            w = rules.get((tau[p], tau[q], k))
            if w: fin[p] -= w; fin[q] += w
        for P in ch.a.triples:
            pts += 1
            if P in exempt: continue
            if fin[P] > 6:
                key = (tau[P], str(cost[P] - 6), str(fin[P] - 6))
                bad[key] += 1; ex.setdefault(key, g)
                if tau[P] not in known: unseen[tau[P]] += 1
print(f"{cnt} arrangements, {pts} points; final cost > 6 at {sum(bad.values())} points; unseen over-budget types {dict(unseen)}")
for k, v in bad.most_common(12): print(f"  {v:6d} {k}")

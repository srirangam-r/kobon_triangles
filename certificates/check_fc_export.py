"""work/eng/T25/rules_FC_full.json (the published per-line LP weights, D = 16) must be exactly the FC certificate that the A30
audit verifies with its own exact DP (certs[1] of work/eng/T25/elim/state_2.pkl).  Re-exports the stored weights with the same
logic as search/rule_lp_t25.export_rules_t25 and compares with the JSON file as sets of rules."""
import sys, json, pickle
from fractions import Fraction as F
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "search")); sys.path.append(str(ROOT / "work/t3"))
import __main__
import rule_lp as RL
__main__.EFrame = RL.EFrame
st = pickle.load(open(ROOT / "work/eng/T25/elim/state_2.pkl", "rb"))
c = st["certs"][1]
assert c["name"] == "FC" and c["D"] == 16, (c["name"], c["D"])
D = c["D"]; rows, special, fam = [], {}, []
for key, x in c["w"].items():
    if not x: continue
    if len(key) == 1:
        special[key[0]] = str(F(int(x), D)); continue
    if key[0] in ("SV", "TRI", "PT", "U"):
        fam.append(dict(family=key[0], key=repr(key[1:]), weight=str(F(int(x), D)))); continue
    pay, rec, cell = key
    ring5, u, pL, pR, tL, tR, oth = cell
    rows.append(dict(payer=pay, receiver=rec, ring5="".join(ring5), u=u, pL=pL, pR=pR, tL=tL, tR=tR, oth=list(oth), weight=str(F(int(x), D))))
d = json.load(open(ROOT / "work/eng/T25/rules_FC_full.json"))
S = lambda L: sorted(json.dumps(r, sort_keys=True) for r in L)
ok = d["denominator"] == D and d["special"] == special and S(d["rules"]) == S(rows) and S(d["families"]) == S(fam)
print(f"FC certificate (D={D}): {len(rows)} block-cell rules + {len(fam)} SV/TRI/PT rules + special {special}")
print("rules_FC_full.json identical to the audited certificate:", ok)
sys.exit(0 if ok else 1)

# Result: the n = 18 FC certificate already proves final >= 0 on every line at n = 14, 16, 20 (multiplicity <= 3)

Runtime and memory: no LP was needed. About 5 min of wall time and under 3 GB of RAM in total.
All commands run from the repo root.

## Outcome per n
| n | W = n - 1 | exact DP min D(2 final + 2), D = 16 | target 2D | final_min | Lambda >= | T <= | Kobon value |
|---|---|---|---|---|---|---|---|
| 14 | 13 | 32 | 32 | 0 | n/3 -> 6 | 54 | K(14) = 54 (the record 54 is attained) |
| 16 | 15 | 32 | 32 | 0 | 8 | 72 | K(16) = 72 |
| 20 | 19 | 32 | 32 | 0 | 9 | 117 | K(20) = 117 |

Certificate found: **yes, for all three n, with the unchanged FC weights** (`weights_FC_D16.pkl`, `weights_FC_D16_rules.json`;
60 block cells, 7 SV/TRI/PT rules, alpha' = 1/2, a = 0, wr = 0, D = 16). Every fact used is class (a) (see FACTS.md);
no (b) or (c) fact is used.
Arithmetic: sum_L final + waste = 3 Lambda - n with waste >= 0 (THEORY §23), so Lambda >= n/3. With Lambda = n(n-2) - 3T,
T <= (n(n-2) - n/3)/3 = 54.44, 72.89, 117.78.

## Exact verification lines
Graph rebuilt with the target W (the alpha' column holds the constant 3(W-1)), flags exactly those of FC:
`uv run --no-project --with numpy --with scipy --with networkx --with python-sat python work/eng/othern/export_graph_n.py full work/eng/othern/g_W$W.pkl --exactw $W`
(= `search/rule_lp_t25.py lp --class full --split --alpha --celldom --wr --sv --tri --pt --eps 0 --exactw $W`; the
export is A30's `export_graph.py` with the repo root hard-coded). Then A30's independent exact-integer layered DP:
`uv run --no-project --with numpy --with scipy --with networkx --with python-sat python work/eng/othern/check_w.py work/eng/othern/g_W$W.pkl $W work/eng/T25/elim/state_2.pkl 1`
```
W=13 min D*(2*final+2) = 32  need >= 32  final_min = 0  OK     (n = 14)
W=15 min D*(2*final+2) = 32  need >= 32  final_min = 0  OK     (n = 16)
W=19 min D*(2*final+2) = 32  need >= 32  final_min = 0  OK     (n = 20)
```
(`log_a30dp_FC.log`). Second implementation (T25's own graph and `RL.min_by_units`, `t25dp_check.py`, logs `log_t25dp_W*.log`):
the top entry is 32 at units 13, 15 and 19, and all lower unit counts are above 32 (these lower entries use the W-specific alpha' constant and are only
indicative).
Planted test: all 68 single-weight decrements (-1/D) are detected at each W (68/68 at W = 13, 15, 19), so the check is sensitive.
Both DPs read the same window graph (topology identical to the n = 18 graph: 116,545 nodes, 3,118,788 edges, 185,583 windows).

## Sensitivity to celldom (why it matters that celldom is class (a))
Without the T23 axis-cell filter (`NOCD=1 ... export_graph_n.py`), FC's weights fail: DP min 16 (W = 13), 0 (W = 15), 0 (W = 19).
So the result rests on celldom. celldom is a pure enumeration over automaton windows filtered by the proved patterns P000-P009,
which hold for all n by the restriction principle and by hand (THEORY §18). If one distrusts P000-P009 at other n, an LP re-solve
without celldom would be required (not done).

## Data check on real arrangements (necessary condition, `data_check.py`, log `data_check.log`)
Exact final per line with the FC weights (T1 + F + T1'' + all columns), real arrangements with n in {14,16,20}, triple points present:
- n = 14: 172 arrangements, 2,408 lines, min final 0, 710 tight lines.
- n = 16: 97,723 arrangements, 1,563,568 lines, min final 0, 877,481 tight lines.
- n = 20: 341 arrangements, 6,820 lines, min final 0, 5,513 tight lines.
- 0 negative lines, 0 non-conserved arrangements (every rule column sums to 0), 0 violations of sum_L final <= 3 Lambda - n.

## Caveats
- The same trust base as the n = 18 result: Python automaton and LP code, the A20/A30 audits (done for the n = 18 graph; the other graphs differ
  only in W), hand proofs of K1*, K2, K2g, K3, F4', F5*, P000-P009 (not machine-checked).
- Only the exact values K(14) = 54, K(16) = 72, K(20) = 117 for multiplicity <= 3 (points of multiplicity >= 4 are not covered).
  For general pseudoline arrangements one still needs the multiplicity >= 4 argument (T22/T27) at those n; not attempted.
- Even n only (M1). Not checked here: a re-derivation of the single-n data (K = 18-specific SAT facts) because none is used.

## Files (work/eng/othern/)
FACTS.md, RESULT.md, weights_FC_D16.pkl, weights_FC_D16_rules.json, export_graph_n.py, run_export.sh, check_w.py, t25dp_check.py,
data_check.py, g_W13.pkl, g_W15.pkl, g_W19.pkl (exported graphs), logs log_*.log, data_check.log.

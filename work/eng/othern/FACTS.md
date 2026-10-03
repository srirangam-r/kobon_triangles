# Validity of the FC certificate ingredients at n = 14, 16, 20

Classes: (a) n-independent (hand proof, or SAT with the restriction principle, valid for every n);
(b) proved only at K = 18; (c) unclear.  Result: **nothing used by FC is class (b)**.  The only n-dependence is the
exact path weight W = n - 1 (and the matching constant 3(W-1) of the alpha' column).

FC = `search/rule_lp_t25.py lp --class full --split --alpha --celldom --wr --sv --tri --pt --eps 0`, weights
`work/eng/T25/rules_FC_full.json` (D = 16; special columns: alpha' = 1/2, a = 0, wr = 0).
Defaults in force: F4', K1*, K2, K2g, K3, T1'', F5*.  NOT in force (the `--facts` and `--pat` flags are absent): P000-P009
as path filters, CEGAR patterns.  Multiplicity <= 3 only (no 4-fold frames).

| # | ingredient | where used | class | basis |
|---|---|---|---|---|
| 1 | Line automaton, frames and local facts F-C, F-S1, F-S3 (= F7, needs n >= 3), F-T1, F1-F8 (F3' forced sig, F5 end compatibility) | graph topology | (a) | THEORY §14 (A20 audit: each re-derived by hand, no soundness bug; exhaustive n = 2..7, sampled to n = 18). The facts are phrased per line, with no n. M1 needs even n >= 4 (14, 16, 20 are even). |
| 2 | F4' (no two adjacent simple vertices cap the same side) | `f4p_edge_allow` | (a) | THEORY §15 "proven", and hand proof P007 in §18 |
| 3 | K1* | FCatalogue k1 | (a) | THEORY §16: hand proof (two crossings of L by line c); restriction principle also gives it as SAT with <= 8 lines (pattern P006/P009) |
| 4 | K2 (kite) | k2 and `k2_violation` | (a) | THEORY §16 hand proof (ring at Y and Y', a and c meet twice); pattern P004 |
| 5 | K2g | k2g | (a) | THEORY §16, derived from K2 by hand |
| 6 | K3 (runs, shared third side) | `k3=True` in WGraph and `install_combined_step` | (a) | THEORY §16 hand proof (a run of s-links shares one third side f). T25 found that K3 is the only fact FC needs |
| 7 | F5* (unbounded-ray flags on opposite sides at different vertices) | `f5` step | (a) | THEORY §19 hand proof (Blanc step 5: the two lines would meet twice on L) |
| 8 | T1'' (and T1, F): transfer rules inside the base value v2 | `enable_t1pp` | (a) | They are rules, not facts. Each moves value between lines, the sum is 0, and conservation of every column is checked on real data (below) |
| 9 | celldom: the axis-cell filter `AXIS_CELLS` (24,714 cell removals) | `cell_ok` | (a) | `work/eng/T23/axis_cells.py`: enumerates the cells produced by every automaton window that survives `sig_domain`, `tau_compatible` and `AF.window_forbidden`. That is a pure enumeration, so it is n-independent given P000-P009. The SAT-derived lists (`sat_removed_*`, `flank_removed`) in cell_domains.json are NOT loaded by `cell_ok`. Unlike the other facts it is load-bearing: **FC fails at W = 13, 15, 19 with `NOCD=1`** (DP minimum 16/0/0 against 32), so it needs the P-facts below |
| 10 | P000-P009 (inside axis_cells only) | `AF.window_forbidden` | (a) | `search/automaton_facts.py` docstring: SAT refutation on the witness lines (<= 11), valid for every n by the restriction principle. Also hand proofs in THEORY §18 (P000, P001, P003 by ring arguments, P002 = F-T3, P004 = K2, P005 and P008 from K3 and K1*, P006 and P009 = K1*, P007 = F4'). These are the "SAT at a given K" objects, but the restriction principle makes them n-free: no arrangement of any size contains the pattern |
| 11 | Special columns, validity: alpha' + wr + 1.5 a <= 3/2 | export | (a) | THEORY §23, base identity proved for general n: 3 Lambda - n = sum v_L + waste, waste >= 0. FC: 1/2 + 0 + 0 |
| 12 | Base identity Lambda = Z + sum c_P, portions, ray split | all rules | (a) | THEORY §23 proof (multiplicity <= 3, general n) |
| 13 | SV / TRI / PT cell columns (transfers whose net over an arrangement is 0) | rules | (a) | Local conservation by construction. Checked on real data, see RESULT.md: 0 non-conserved arrangements at n = 14, 16, 20 |
| 14 | Exact weight W | `--exactw` | n-dependent by design | W = n - 1: a line meets n - 1 other lines, a triple point counts 2. The alpha' column carries 3(W - 1) at the first window (`finish`), so the graph must be rebuilt with the right W. This is done in `work/eng/othern/g_W{13,15,19}.pkl` |
| 15 | Final step: final >= 0 on every line => Lambda >= n/3 => T <= floor((n(n-2) - n/3)/3) | arithmetic | (a) | n = 14: 54.44 -> 54. n = 16: 72.89 -> 72. n = 20: 117.78 -> 117 |

## Not used by FC (so irrelevant here)
- `--facts` P-patterns as path filters, `--pat` CEGAR patterns (n = 18 SAT with the 4-fold points allowed): off.
- Multiplicity >= 4 machinery (T22/T27): off. These certificates cover multiplicity <= 3 only, as requested.
- The strict steps (clean-line delta, no-clean strictness, A30 tightness): n = 18-specific, not needed for the exact Kobon values.

## Residual caveats (all inherited from n = 18, not n-specific)
- The automaton, the LP code and the DP are computer code, not machine-checked. The A30 audit covers the n = 18 graph;
  the n = 14/16/20 graphs are the same graph with different W (identical topology, 116,545 nodes, 3,118,788 edges).
- F5* was audited on data (1.07M lines) and by hand proof, not by SAT.

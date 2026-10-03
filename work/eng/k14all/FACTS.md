# FC-M (multiplicity >= 4 certificate w_FCM25.pkl, D = 16) at n = 14: ingredient validity

Setting. Suppose an arrangement of 14 pseudolines has T >= 55. Take one with T = K(14) and then maximal number of vertices V (lexicographic (T,V)).
All arguments below are local (disk around a point or a pair of points), so they do not depend on n except through the multiplicity range m <= n and the
path weight W = n - 1.  Classes: (a) n-independent, (b) proved only at K = 18 (must be re-proved), (n-dep) depends on W.

| # | ingredient | where | class at n = 14 | basis / action |
|---|---|---|---|---|
| 1 | Perturbation lemma (THEORY 24): only bad 4-fold points (words 11101110, 11111110, 11111111) and triple points survive in a (T,V)-maximal counterexample | M frames restricted to the 3 bad words (`BADONLY`, no M5+ frames) | (a) | Local. m = 4, 5 exhaustive, m = 6 sampled cover of all 4096 patterns, 7 <= m <= 17 explicit lossless W_m, so every m <= 14 (max possible at n = 14) is covered. (m = 18, the pencil, is irrelevant.) T does not decrease, V increases, hence the maximal counterexample has no other multiple points. |
| 2 | Pair lemma PAIRLEM (THEORY 25): a (4-fold, triple) consecutive pair only with the 48 allowed sector patterns (`pair_PQ_all.json`) | `PAIRLEM=1` | (a) | Local window of 6 pseudolines, optimality of (T,V) among n-arrangements; no use of n beyond n >= 6. |
| 3 | Line-automaton facts F-C, F-S, F1-F8 incl. T22 M frames (bin,bout,hE,hW; hW/E independent) | graph topology | (a) | THEORY 14/15: stated per line; M1 needs even n >= 4 (14 is even). Audit evidence includes n = 2..14 exhaustive/sampled, so n = 14 is inside the tested range. |
| 4 | K3 guarded for class-3 apexes | `k3_step_m` | (a) | THEORY 16 hand proof (run of s-links shares one third side), guarded to exactly triple/simple apexes. No n. |
| 5 | F4' guarded (no two adjacent simple vertices cap the same side, only where the capped apex is exactly triple) | `f4p` | (a) | THEORY 15/18 (P007), hand proof. |
| 6 | tau_compatible with apex class 3 | automaton | (a) | local compatibility, no n. |
| 7 | K1*, K2, K2g, F5*, celldom, P000-P009, guarded facts | - | not used | OFF in FC-M (`nok1 nok2 nok2g nof5` defaults, no `--guarded`, no `--celldom`). |
| 8 | CEGAR patterns 0-3 (`cegar/pats.json`, with their 3 symmetric variants each) | `--pats` | (b) -> RE-PROVED at K = 14 | See below: the restricted pattern the DP uses (frames of the stored `preds`) is UNSAT on K = 14 lines, kissat + drat-trim VERIFIED. |
| 9 | CEGAR pattern 4 (three consecutive simple cap vertices sharing a class-3 apex) | `--pats` | (a) hand fact | A class-3 apex has multiplicity exactly 4 in the reduced model (item 1; also true at n = 14), F4' run <= m - 2 = 2. n-free. |
| 10 | Base identity 3 Lambda - n = sum final + waste, waste >= 0, and special columns alpha' + wr + 1.5 a <= 3/2 (here 1/2) | LP columns alpha', a, wr | (a) with caveat | THEORY 23 is proved for general n for multiplicity <= 3. The identities B = C, A = 3C/2 used for the M-model are validated on data (11,117 multiplicity arrangements, 0 failures at n = 18) but NOT proved ("a proof for M outstanding", CERT_FCM25). Same trust gap as n = 18. |
| 11 | Soundness of the M-window chain (hidden star classes, PT4/MB/TRI coupling) | graph | (a) with caveat | validated on real lines (543k, 0 bad, at n = 18); a local, per-line model, no n in it. Data at n = 14 not rerun. |
| 12 | Exact weight W | `--exactw 13` | n-dep, rebuilt | Graph rebuilt with W = 13 (the alpha' constant 3(W-1) enters at the first window). Verified below. |
| 13 | Final arithmetic | - | n-dep, redone | Lambda = n(n-2) - 3T = 168 - 3T = 0 (mod 3). 3 Lambda - 14 >= 14 * (-1/4) = -3.5. T >= 55 would give Lambda <= 3, 3 Lambda - 14 <= -5 < -3.5. Contradiction, so Lambda >= 6, T <= 54. |

Other n-specific items checked: `--mvar / eps0 / 18` rows are only active with `--mvar` (not in the command); `exact` whole-line word patterns do not occur in pats.json
(all entries are window patterns); the `18` literals in `rule_lp_t25m.py` are in the unused --mvar/--eps1 margin rows.  The multiplicity <= 3 case (no 4-fold point)
is closed separately by FC at W = 13 (work/eng/othern/RESULT.md, DP min 32 = 2D, all class (a)).

## Pattern re-proofs at K = 14 (item 8)
The soundness claim of a stored pattern is: the *restricted* pattern (cegar_m.restrict_m of the src path with the stored core: only the frames in `preds`, only the
core elements) has no realization by a pseudoline arrangement with 4-fold points allowed.  `regen_k.py` rebuilds that restricted pattern, asserts that its
frame predicates equal the stored `preds` (so the CNF proves exactly what the DP forbids), builds `patsat_m.build(rp, K)` with every element as a unit clause.
(The older `work/eng/oth/drat_pats/regen.py` instead uses the FULL src path, which needs 18 lines; at K = 14 that would be vacuous and is not the claim.)
Output (all with K = 14 lines, kissat -q with proof, then drat-trim):

| pattern | restricted slots | CNF (vars/clauses) | sha256 of CNF | kissat | drat-trim |
|---|---|---|---|---|---|
| 0 | T T | 37473 / 208859 | b086fe32d8dfa1cb493b8602ef3855fc0d0e89f081d6f818d4aac46886554e9b | UNSAT 10 s | VERIFIED 40 s |
| 1 | T S T | 38270 / 212730 | 1e42737af2e7aa4cd44fbab2f8b51a74b12ea528fe3ba687fe8796ccca181509 | UNSAT 15 s | VERIFIED 60 s |
| 2 | T T | 37473 / 208859 | 18d25b690a94d1fea8105c29d84e51d860e636c20da14f89c6518cf91335c528 | UNSAT 8 s | VERIFIED 37 s |
| 3 | T T T | 39988 / 221287 | 02509b71acf95f6739c4e20cb157cb8d582599d7b21347af3c58a2eff56583af | UNSAT 76 s | VERIFIED 82 s |

CNFs in `cnf_K14/`, hashes in `cnf_K14.sha256`, logs `log_kissat_K14_pat*.log`, `log_dratcheck_K14_pat*.log`, `log_regen_K14.log`.
Note the patterns are used with the 4 symmetric variants (flip sides, reversal), which are images of the same SAT statement under the symmetries of the model.
(The DRAT proofs were deleted after checking; `prove_k.sh 14 i` regenerates.)

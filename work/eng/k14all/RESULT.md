# K(14) = 54 for ALL arrangements: FC-M verifies at exact weight W = 13

Verdict: **the FC-M certificate (w_FCM25.pkl, D = 16, unchanged weights) passes the exact integer DP at n = 14**, every ingredient is n-independent
or was re-proved at K = 14 (FACTS.md). Hence every arrangement of 14 pseudolines has T <= 54, and with the known 54, K(14) = 54 (conditional on the same
trust base as the n = 18 result: Python automaton/LP code, hand-proved local facts, the unproved M identities B = C, A = 3C/2; see FACTS.md rows 10, 11).

## Exact verification (graph rebuilt at W = 13; command in verify_fcm_n.sh, log log_verify_W13.log)
`PAIRLEM=1 .../work/eng/T27/verify_exact_cert.py work/eng/T27/cegar/w_FCM25.pkl 16 lp <flags of certificates/verify_certs.sh fcm25> --exactw 13`
```
graph: 156156 nodes, 9220102 edges (trimmed), 1208966 windows, K=451 rule columns
weights 15 not in the rebuilt catalogue: []
exact DP min D*(2*final+2) = 24.0  target * D = 24.0  OK: True
min per number of units: {2: 528, 3: 504, 4: 432, 5: 408, 6: 336, 7: 312, 8: 240, 9: 216, 10: 144, 11: 120, 12: 48, 13: 24}
```
24/16 = 2 final + 2 = 3/2, i.e. final >= -1/4 on every path (every line). Control at W = 17 (log_verify_W17.log) reproduces the certified n = 18 line:
min 24, per-unit list 720 696 ... 48 24, identical to CERT_FCM25.txt.
Sensitivity (planted_fcm.py, log_planted_W13.log): lowering any one of the 15 nonzero weights by 1/16 drops the DP minimum to 20 < 24 in 15/15 cases.

## Arithmetic at n = 14
3 Lambda - 14 = sum_L final + waste, waste >= 0, Lambda = 168 - 3T (multiple of 3). sum final >= -14/4 = -3.5.
T >= 55 means Lambda <= 3, so 3 Lambda - 14 <= -5 < -3.5. Contradiction: Lambda >= 6, T <= (168 - 6)/3 = 54.
Case split as at n = 18: if the (T,V)-maximal arrangement has a bad 4-fold point the above (FC-M) applies; if all multiple points are triple, FC at W = 13 (DP min 32, work/eng/othern) gives final >= 0, Lambda >= 14/3, so Lambda >= 6.

## Pattern re-proofs at K = 14
Patterns 0-3 re-proved UNSAT with K = 14 lines, kissat and drat-trim VERIFIED (about 1 to 2 min each); pattern 4 is a hand fact (n-free). Table with CNF sha256 in FACTS.md.
Observation: the restricted patterns are tiny (2-3 slots); the old regen.py instead proves the full src path (needs 18 lines), a weaker statement, so `regen_k.py` is the right re-proof.

## Caveats
- Trust base identical to n = 18: unproved M identities (B = C, A = 3C/2), M window soundness validated on n = 18 data only (not rerun at n = 14), hand proofs of K3, F4', perturbation and pair lemmas not machine-checked, code not machine-checked.
- Perturbation lemma at n = 14 relies on its m = 6 sampled cover and explicit W_m for 7 <= m <= 14.
- No real-arrangement data check of FC-M at n = 14 was run.
Files: verify_fcm_n.sh, regen_k.py, prove_k.sh, planted_fcm.py, cnf_K14/, cnf_K14.sha256, log_*.log.

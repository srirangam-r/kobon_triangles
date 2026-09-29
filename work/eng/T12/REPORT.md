# T12 — master-inequality accounting on exactly evaluated arrangements

**Summary (≤200 words).** `search/phi.py` computes every term of 2Λ ≥ n + Φ exactly, per point and per line, from a wiring word. It checks the identities on every input:
- 3T = S − Z + D;
- Λ = Z − D + Σk(k−2);
- 2Z = Σκ + Z_tr;
- D = ΣD_P + β (L1);
- L3 (clean lines have κ ≥ 1);
- the exact decomposition s = clean_excess + capmult.

Across **260,561 arrangements** there were **0 failures**. The sets are gallery-18, DP-walk 93s, bridge-rich 93s, T = 91–92 states, and n = 16 72s and 70–71s.
- **Independent cross-check:** on 293 arrangements, T (from `count_general`) and the blocks, bridges and all-multiple faces (from `test_k5L_layer.geometry`) match with 0 mismatches.
- **Speed:** 56k arrangements in 11 s on 3 cores.
- **Φ is never below −1 at n = 18** (−2 at n = 16). A 94 needs Φ ≤ −6. Every 93 has s = −Φ ∈ {0, 1}, and 99.7% are exactly tight.
- **Structural deficit:** Φ₀ = Φ − Cred reaches −9. It is −9 at the collinear X4 family (σ = 3, x = 0, Σh = −12), which Cred repays.
- **Families where a 94 could hide:** (A) shared-line all-X, β = 0; (B) Z = 0 bridge-rich with all credit zero; (C) wheel W6 (hub of 6 bridges, 6 all-multiple faces), 12 bridges, Z_tr = 0; (D) dense O1b/O0 lattices with k = 15–21. Details below.

Files: `search/phi.py`, `work/phi/*.jsonl`, `work/eng/T12/{REPORT.md,tables.md,report.py,summ.py}`.
`tables.md` is the raw output of `report.py`.

## 1. What `phi.py` does

`analyze(gens, n)` returns:
- the globals: T, Z, D, S, Λ, σ, β, x, Σh, Cred (split into A, multi, capother, Z_tr), Φ, s;
- per point: kind, e (bridges), D_P, caps, x_P, h_P, Lemma-A touches, mutual pairs, killed flag, local φ = h + x + A − e, triangles at the point, all-multiple faces at the point;
- per line: class, j, κ, Z carried, and how many points it caps;
- Z carriers, classed as (clean / cap / multi / multi+cap) × endpoint types (ss / ms / mm).

Point kinds follow C37/C39:
- **b = 3:** C.
- **b = 2:** X (opposite blocks) or V (bent). An X with e > 0 is called F.
- **b = 1:** O1a or O1b, split by whether the two rays next to the block middle have a multiple first vertex.
- **b = 0:** O0.

The slack decomposes **exactly** as s = 2Λ − n − Φ = clean_excess + capmult, where:
- clean_excess = Σ_{clean}(κ − 1);
- capmult = Σ over cap lines avoiding all multiple points of (#points capped − 1).

Φ = σ + Σ_P(h_P + x_P + A_P − e_P) + Cred_rest, where Cred_rest = multi + capother + Z_tr.

CLI:
- `python search/phi.py <in>[,<in2>] <out.jsonl> --n N [--slim --dedup --minT --maxT]`
- `python search/phi.py selftest <n> <in>...`

Wiring words contain triple points only, so 4-fold points are not covered. Odd n is out of scope (L3 needs even n); the checker correctly flags n = 17 words.

## 2. Validation

| check | result |
|---|---|
| identities, L1, L3, s ≥ 0, decomposition (260,561 arrangements) | 0 failures |
| T vs `count_general(chi_from_word)` (293 arrangements) | 0 mismatches |
| blocks, bridges and all-multiple faces vs `test_k5L_layer.geometry` (same 293) | 0 mismatches |
| n = 17 words (out of scope) | flagged, so the checks are live |

**Speed:** `dpwalk93.jsonl` (56,044 arrangements) took 11.4 s wall on 3 cores, about 5,000 per second.

The sets in `work/phi/` are deduplicated within each set only. They overlap each other: the gallery and DP-walk sets share many 93s, and `dpwalk2_18` overlaps `dpwalk93`.

## 3. Distributions

For every 93 (n = 18) and every 72 (n = 16), 2Λ − n = 0, so **s = −Φ**.

| set | N | Φ | s |
|---|---|---|---|
| gallery-18 | 2,376 | −1: 97, 0: 2,279 | 1: 97, 0: 2,279 |
| DP-walk 93 (`dpwalk93`) | 56,044 | −1: 114, 0: 55,930 | same |
| bridge-rich 93 (`bridge93`) | 126 | −1: 1, 0: 125 | |
| DP-walk-2 93 (`dpwalk2_18`) | 32,300 | −1: 442, 0: 31,858 | |
| pls 93 (`pls18_93`) | 550 | −1: 20, 0: 530 | |
| n = 18, T = 91–92 (`near18`) | 30,936 | 0…12 | 0…12 |
| n = 16 bridged 72 (`bridge16`) | 17 | 0: 17 | |
| n = 16 all 72s (`cal16_72`) | 79,117 | **−2: 12**, −1: 487, 0: 78,618 | |
| n = 16, T = 70–71 (`pls16_70_71`) | 59,095 | −1: 3, 0…12 | |

At T = 92 (2Λ − n = 6):
- 7,048 states have s = 0 and Φ = 6;
- 2,968 have Φ = 0 and s = 6.

**Nothing comes near 94.** A 94 needs Φ ≤ −6 (equivalently, T ≤ 93 whenever Φ ≥ −5). The observed minimum is **−1 at n = 18** and −2 at n = 16, so the margin is at least 4 units at n = 18.

## 4. Structural deficit Φ₀ = Φ − Cred (where a proof has to work)

Φ₀ is the value with no credit at all. A 94 needs Φ₀ ≤ −6, and Cred ≥ −Φ₀ − 5 is what a proof must then produce.

Φ₀ over all n = 18 93s (91,396 records, not deduplicated across sets):

| Φ₀ | 0 | −2 | −3 | −4 | −5 | −6 | −7 | −8 | −9 |
|---|---|---|---|---|---|---|---|---|---|
| count | 60,743 | 594 | 20,965 | 848 | 5,108 | 919 | 1,532 | 35 | 650 |

Deficits ≥ 6 occur only in the families below. Every observed arrangement pays them back with Cred ≥ −Φ₀ − 1.

Bridged 93s only (1,730 records): Φ₀ ∈ {0, −2, −3, −4, −5, −6}, and the −6 cases are the 75 `X3 F1 O1b1 O01`, k = 6, β = 3 records.

Φ₁ = Φ minus everything except Lemma-A credits:
- all 93s: Φ₁ ∈ {0 … −4};
- bridged 93s: Φ₁ ∈ {0 … −3};
- the −3 bridged cases are the k = 10, β = 12 family.

So **Lemma A alone leaves a deficit of at most 4 (3 for bridged).** The remaining credits are the multi-line touches and the clean-line claims.

## 5. Tightest configurations, grouped by local structure

**Family A — shared-line all-X, β = 0 (Φ = −1 at n = 18, −2 at n = 16).**
- Structure: k = 3–6 type-X points on a common shared line. σ = k − 1; x = 0 for k = 4 and 8 for k = 6.
- Deepest deficit: X4 has Φ₀ = −9 (σ = 3, x = 0, Σh = −12).
- Cred = 8 (A ≈ 6, multi = 2); nclean = 1.
- **All of s comes from one clean line with κ = 2** (clean_excess = 1). Z ≈ 5 (at k = 4), carried by multi-lines (~4) and the clean line (1); Z_tr = 0; no bridges.
- At n = 16 the Φ = −2 cases have clean_excess = 2 (X3, σ = 2 or 1, 12 states).
- This is the "any k: collinear on one common axis" family that `general.md` §5 lists as closed.
- Counts, n = 18 93s: X4 (Φ = −1) 231, X5 227, X6 179, X3 30. The Φ = 0 versions of the same families have Cred one higher.

**Family B — Z = 0 bridge-rich (Φ = Φ₀ = 0, Cred = 0 exactly, nclean = 0).** The proof has no credit to lean on: σ + x = 2β + |Σh|.
- (k = 8, β = 1, X6 O1b2): 134 records. σ = 8, x = 12, −2β = −2, Σh = −18; six killed X points.
- (8, 0, X7 O1b1): 111 records.
- (9, 2, X6 V1 O1b2) and (9, 2, X6 F1 O1b2): 46 and 44.
- (9, 4, X5 F1 O1b2 O01): 33.
- Large-k versions: (19, 32), (21, 39), (20, 36), (16, 25) …, all with Z = 0 and Cred = 0.
- Overall, 455 of the 1,730 bridged records have Φ₀ = 0.
- The supply is σ and x, from many killed X points capping through multiple points.

**Family C — the wheel W6 (k = 7, β = 12, `O1b6 O01`, 144 records; k = 8, `X1 O1b6 O01`, 39; k = 9, `X2 O1b6 O01`, 27).**
- Structure: one O0 hub with 6 bridges, six O1b rim points with 3 bridges each, and 6 all-multiple faces.
- Terms: σ = 12, x = 6, −2β = −24, Σh = 3 (h = 3 for O0, 0 for each O1b), Cred = 3 (A = 1, multi = 2); Z = 6 with Z_tr = 0.
- The 3 Cred are spread over lines that pass through multiple points; Z is carried by multi/multi+cap lines and one clean segment.
- The single Φ = −1 bridged 93 (bridge93 #108: k = 10, β = 12, `X3 O1b6 O01`, Φ₀ = −5) is this wheel plus 3 extra X points, with one clean line at κ = 2.

**Family D — dense O1b/O0 lattices, k = 15–21, β = 24–39.**
- Examples: `O1b14 O05` (19, 36), `O1b15 O05`, `O1b15 O06` (21, 39).
- σ = 30–45, x = 10–15, Σh = 3–18.
- Z is 0 in most and ≤ 2 in the rest; Φ = 0 throughout.
- Once β ≥ 24, the O0 hubs (h = +3) offset the −2β term.

**Family E — a single bridge (k = 6–9, β = 1–4).**
- Structure: one or few bridges between O1b points plus many X points on shared lines.
- Example: (6, 1, X4 O1b2): 122 records, Φ₀ = −4, A = 4.
- Cred is entirely Lemma-A touches here (multi = 0), and Z ≤ 2. Because Cred_A alone pays, a proof must show A ≥ 2 or 4 in these.

**Zero credits.** Z_tr is nonzero only where a multiple endpoint of an unused segment exists (`ms` carriers, e.g. `X3 F1 O1b1 O01`). Cred_capother (cap-line touches other than Lemma A) is rare in the 93s and 72s (1 gallery-18 record and 26 of the 79,117 n = 16 72s) and common only in the near-optimal states (3,795 of the T = 91–92 / 70–71 records). The clean-line term never adds a tightness beyond nclean ≤ 1 outside the β = 0, k ≤ 2 families.

## 6. Which term families supply the slack in the bridge-rich 93s

Means over `bridge93` (126 records): σ = 15.6, x = 7.8, −2β = −22.6, Σh = −3.7, Cred = 2.9 (A = 2.2, multi = 0.55, Z_tr = 0.15), Φ = −0.008.
- **σ and x supply nearly everything** (23.4 vs 26.3 demanded by −2β and Σh).
- **Cred is small:** ≤ 6, mostly Lemma A.
- **Clean claims** supply essentially none: nclean ≤ 9, and clean_excess = 0 except for the one Φ = −1 arrangement.
- **Z_tr** is ≈ 0.

Per-point local φ = h + x + A − e (bridged 93s):

| kind | typical φ_loc | notes |
|---|---|---|
| X | −2 (1,826), −1 (2,625) | 2,519 killed |
| F | −3 (424, all killed), −2 (85) | |
| V | −3 (132) | |
| O1b | −2 (2,967), −1, 0 (1,377) | x = 1 on average |
| O1a | −1 or 0 | |
| O0 | −3 (780), −1, 0, +1 (346) | |

The tightest local kinds are F and V (−3) and O0 (down to −3); this fits `general.md` §3 (killed −2, bent −1 plus its bridge).

## 7. Short list (where a proof of Φ ≥ −5 must work hard, and where a 94 could hide)

1. **Shared-line all-X, β = 0** (families A): Φ₀ down to −9. The proof's parity and shared-axis arguments must give Cred ≥ 4.
2. **Killed X / F / V points with Cred = 0** (family B, Z = 0). Only σ and x pay, so the argument must be purely about cap lines through multiple points and shared lines.
3. **W6 wheels and dense lattices** (families C and D): the −2β term is offset by O0 hubs (h = +3) and by σ. This is where the per-bridge payment rules (Lemma B, `all-multiple face`) are used.
4. **Single-bridge O1b/X mixtures** (family E): Cred_A alone must be shown to be ≥ 2–4.

## Caveats
- All data are arrangements found by search, and 93 is also the known optimum. Φ ≥ −1 here says these structures are far from 94, not that Φ ≥ −5 holds in general.
- The k = 4 collinear X4 family is the one with the largest deficit (Φ₀ = −9).
- No 4-fold points (not representable in wiring words). Bridged 72s from the cal directories were included in bulk (`cal16_72`, 699 with β > 0), not only the 17 in `bridge16_heldout.json`.
- `id` in the jsonl is `file#index`, where the file name is not unique across directories (`cls_w*.jsonl`). Records with k > 0 carry `gens`; k = 0 records are slim (no gens).

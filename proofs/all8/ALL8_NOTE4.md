# All-8 Note 4 — early trade-off candidates

**Working status: the class trade-off and the exclusion of 94 remain unproved.** This note prioritises the lead's new check-in in `SOL_TASK4.md`; the zero-credit inventory is supporting work, not a solution. The reviewed `ALL8_NOTE3.md` and `note3_check.py` are preserved.

## 1. Exact budget and the required trade-off

Use the accepted identity

\[
\Lambda=\pi+\frac E2,\qquad
E=2U+\sum_P S_P^\circ+2K_3+4K_4+\Delta\ge0,
\quad \pi=18-W.
\]

A 94 has `Lambda=6`, and hence

\[
1\le\pi\le6,\qquad E=12-2\pi.
\]

In particular, positive-credit points such as `(pi,U,Delta)=(1,0,10)` or `(3,3,0)` cannot be discarded. Nothing below assumes that every 94 has `pi=6`.

## 2. First global candidates — UNPROVED in the structural class

### B: baseline trade-off

\[
\boxed{E\ge18-3\pi},\qquad
\boxed{W\le2\Lambda}.
\tag{B}
\]

The two forms are equivalent. Together with `Lambda>=pi`, this gives `Lambda>=6`. More importantly, it would force **every** 94 to have `pi=6` and `E=0`; this reduction has not yet been proved.

**Proved simple-arrangement subcase.** The lead's argument gives `Lambda>=max(pi,18-2pi)`. If `pi<=6`, then `2Lambda+pi>=36-3pi>=18`. If `pi>=6`, then `2Lambda+pi>=3pi>=18`. Thus (B) holds in the simple subcase without the DP.

### A: strict all-8 trade-off

If there is an all-8 point, conjecture

\[
\boxed{E\ge19-3\pi},\qquad
\boxed{W+1\le2\Lambda}.
\tag{A}
\]

For a 94 these require `pi>=7`, contradicting `pi<=6`. This would finish the target, but **no proof is supplied**. It is not an independently established strengthening of (B).

**Testing limitation:** every known 93 has `2Lambda=18`. Consequently (B)'s slack is `pi`, and (A)'s slack, if applicable, is `pi-1`. Both pass such records automatically because `pi>=1`; those passes are not evidence for the missing ownership rule.

## 3. A touch-discount candidate already REFUTED

The early candidate

\[
E-\frac14U\ge18-3\pi
\tag{D4}
\]

is false on the lead's 93 data. Its integer-scaled slack there is `4*pi-U`.

A scan of all 14,376 records in `all8_work/data93/split93.jsonl` gives

```text
records=14376
baseline_min_slack=1
discounted_min_scaled_slack=-2
discounted_failures=202
pi=1 splits (U,Delta):
(0,16):199; (1,14):124; (2,12):121; (3,10):79;
(4,8):178; (5,6):87; (6,4):115
```

Record 107 has

```text
T=93, pi=1, W=17, U=6, Delta=4, Z=5, triples=4
end_counts={'I3':2,'W':34}
```

Here `E=16`, but `E-U/4=14.5<15`. Retain this counterexample; do not use (D4) as a lemma.

A **new test candidate**, not a proved replacement, is

\[
E-\frac16U\ge18-3\pi.
\tag{D6}
\]

On the 93 file this asks `U<=6*pi`. The complete cached scan of all 14,376 records gives **zero failures**, with minimum integer-scaled slack `6*pi-U=0`. The displayed `pi=1,U=6` records make the discount `1/6` the largest uniform touch discount compatible with these samples. This is a calibration observation, **not** a geometric reason to choose that coefficient.

## 4. More discriminating ownership candidates

Let `P0` count lines whose two ends are bad wedges and whose every bounded segment is singly used. No quadruple lies on such a line. Set

\[
I=I_3+I_4,\qquad
\Delta_N=N_{\rm res}-F
=\Delta-(2Z-U-G_Z)\ge0.
\]

Here `F` counts multiple line ends, and `G_Z` counts unused good ends, as in Note 3. The following are **conjectures for early testing**, not derived consequences of the budget:

\[
\boxed{P_0\le I+2U+\Delta_N},
\tag{O1}
\]

and its weaker fallback

\[
\boxed{P_0\le2I+2U+\Delta_N}.
\tag{O2}
\]

**Update: (O1) is REFUTED.** Record 107, independently rebuilt from its valid wiring word, has `P0=15`, `I=2`, `U=6`, and `Delta_N=0`. Its (O1) right-hand side is 14. It passes both the structural-class and triple-optimality checks. That example requires at least `3/2`; the full scan in §6 now forces the coefficient to be at least **2**. O2 passes the full 93 file but remains unproved globally.

These test actual parity-defect ownership rather than a restatement of the triangle count. They do not by themselves control interior lines with double or unused segments, so even a proof of one would only be part of (B).

**Why this is the next local question.** At an eligible perfect interior line, Note 3 gives `t_L+f_L` odd. Under triple optimality, a triple on that line has the two-two-fan four-sector type: its other axis has two opposite double rays. Kite payments on the perfect line pair endpoint tokens on the same single cap edge. A three-fan block at such a triple forces a single central cap edge whose two tokens are unclaimed; these are candidates for `Delta_N` payment. Touch cap steps cost `U`. The difficult remaining source is an **end-block cap step**, which can repair parity without `U` or residual credit; (O1)/(O2) expose that issue through `I` rather than pretending it is already paid.

The preceding observations are a proof route, not a proof of (O1), (O2), or (B). In particular, the good-end resource `I` cannot then be reused without an explicit disjoint allocation.

## 5. Reproducible checks and remaining work

The lead's cached `pi,U,Delta,Z,end_counts` permit immediate scalar tests. Computing `P0` additionally requires rebuilding the wiring arrangement; it must count all perfect interior lines, not silently discard records according to triple optimality.

The scalar scan and reconstruction of record 107 refuted (D4) and (O1). The exact word and rebuilt metrics are preserved in `all8_work/tradeoff_record107.json` (its word matches source record 107 exactly). The final `note4_check.py` also compiles and passes 3,474 deduplicated dataset arrangements; this is a secondary geometry/payment check, **not** a test of the new trade-off conjectures. The new reusable scorer and full 93 scan are reported in §6. Dataset passes are computational checks, never certificates or universal proofs.

Priority remains: prove a disjoint defect-to-resource allocation valid across the entire credit simplex. The earlier opposite-case-B/zero-credit cluster work in `note4_check.py` is secondary and has not been independently reviewed. Neither requested subagent reviewer started; their runtime dependency failure is recorded in `all8_work/note3_delegation_blocker.json`. No runner fallback was used.

## 6. Full reconstructed 93 scan (Codex continuation, 2026-10-02)

`tradeoff_check.py` now implements the reusable scorer. Reconstruction uses
`note3_check.word_valid`, `credit_state`, and `end_data`, and counts **every**
raw perfect interior line before applying any structural/triple-optimality
filter. Every cached `T,pi,W,U,Delta,Z,triples,end_counts` value agrees with
its reconstruction: **14,376 records, zero reconstruction errors**.

| Candidate | Failures, all 14,376 | Minimum scaled slack | Scale |
|---|---:|---:|---:|
| B | 0 | 1 | 1 |
| D4 | 202 | -2 | 4 |
| D6 | 0 | 0 | 6 |
| O1 | 81 | -1 | 1 |
| O3half: `P0 <= 3I/2+2U+Delta_N` | 8 | -1 | 2 |
| O2 | 0 | 0 | 1 |
| O2Q: `Q0 <= 2I+2U+Delta_N` (§9) | 0 | 0 | 1 |

**O3half is REFUTED.** Its first failing record is 375:

```text
T=93, Lambda=9, pi=2, W=16, U=5, Delta=4, Z=6
end_counts={'I3':1,'W':32,'Z':3}; I=1; Delta_N=0; P0=12
word_valid=True; structural_class=True; triple_optimality=True
O3half RHS=11.5; O2 RHS=12
```

The complete word, credits, and per-perfect-line triple/cap inventory are in
`all8_work/tradeoff_rebuilt93/overall_O3half_first_failure.json`. It forces
the coefficient of `I` to be **at least 2** if the coefficients of `U` and
`Delta_N` stay at 2 and 1. Thus O2's coefficient is sample-sharp, not merely
a loose fallback after record 107.

Of the 14,376 records, **13,718** pass both structural-class and triple
optimality checks; 658 fail triple optimality. On that eligible subset O1
still has all 81 failures, O3half all 8, and O2 has none. No record is
silently removed from the overall scores. Raw `P0` is positive on 13,143
records (12,504 eligible). These are dataset results, not a proof of O2.

Reproduce:

```bash
python -m py_compile work/bbl/tradeoff_check.py
python work/bbl/tradeoff_check.py --scalar-only --progress 0 \
  --out work/bbl/all8_work/tradeoff_scalar93 \
  work/bbl/all8_work/data93/split93.jsonl
python work/bbl/tradeoff_check.py --progress 3000 \
  --out work/bbl/all8_work/tradeoff_rebuilt93 \
  work/bbl/all8_work/data93/split93.jsonl
```

Exact summaries are `summary.json` in the two output directories; the full
rebuilt metrics are `tradeoff_rebuilt93/metrics.jsonl`. First failing and
minimum-slack words are retained separately for each candidate and cohort.
The initial full reconstructed run took 58.904 seconds; the final run with
O2Q scored too took 53.951 seconds in this checkout.

The 29 lead binding witnesses in `work/eng/oth/wit3/wit_sat.jsonl` also
reconstruct without error and pass every scored candidate. All 29 satisfy
the structural/triple-optimality checks; 11 contain an all-8 point, and 8
have positive `P0`. Minimum O2 slack is 8; minimum strict-all-8 A slack is
120. These high-slack witnesses do not approach the required 94 exclusion.
Exact output: `all8_work/tradeoff_all8_witnesses/summary.json`.

## 7. A restricted ownership lemma with disjoint labels

**New proved derivation using Note 3; not yet reviewed by the lead.** This
is a local part of the trade-off, not a proof of B or A.

First, a triple lying on a perfect interior line has exactly four triangular
sectors in two opposite runs of two. Number the line's rays 0 and 3. Then
`s5+s0=s2+s3=1`; the two alternating sector sums are at least two. The two
same-side choices are excluded as in Note 3 §7. In either remaining choice
both `s1=s4=1` are forced. The only words are `011011` and `110110`.
Consequently the triple has two opposite double rays on one axis and four
single rays on its other two axes. At most two perfect lines pass through
it. This calculation is also exhaustively checked on all 64 sector masks.

Let `H_UI` be the set of perfect interior lines such that **every** triple
on the line has both those double rays as touch/end blocks (`U` or `I`).
Lines with no triples are included. Then

\[
\boxed{|H_{UI}|\le U_3+I_3+U+I
                  =2(U+I)-U_4-I_4.}
\tag{UI}
\]

**Proof and explicit allocation.** Give each triple-origin U/I block two
distinct labels, called triple and cap. Give each quadruple-origin U/I
block only a cap label. At a triple incident to lines of `H_UI`, its two
opposite blocks are both U/I, and at most two such lines pass through it;
assign their triple incidences injectively to the two triple labels. A
simple same-side step on an `H_UI` line is the unique cap of a U/I block,
and gets that block's cap label. Each block has one centre and one cap
line, so cap labels are also distinct. Triple and cap labels are separate.

Note 3's `t_L+f_L` odd guarantees at least one assigned label on each line
of `H_UI`. Keep one label per line and discard its other labels. This is
an injective assignment, proving (UI). The inventory checker writes the
actual chosen `UI_assignments` and verifies non-reuse. This is label
ownership; an I label does **not** create additional unspent E-credit.
The global end payment for I still has to be reconciled in a proof of B.

## 8. Fresh three-fan residual tokens

**New proved derivation using Note 3; not yet reviewed by the lead.** Let
`h` count three-fan simple centres with at least one of their two block
origins a triple on a perfect interior line. Let `eta0` and `e_mix` have
their Note 3 definitions. Then

\[
\boxed{\Delta_N\ge\eta_0+2e_{\rm mix}+2h,\qquad
       \Delta\ge2\eta_0+2e_{\rm mix}+2h.}
\tag{H}
\]

**Proof.** Such a centre X has two adjacent double block sides XP and XQ,
where P and Q are multiple, and central triangle XPQ. Suppose P is the
perfect-line triple. Its double axis is PX. By the sector calculation in
§7 its ray PQ is single; hence the central cap PQ is singly used. Its two
tokens `(P,PQ)` and `(Q,PQ)` are N tokens on a bounded edge.

They are not old touch/end tokens: those payment triangles have two-fan
centres. Nor are they old three-fan tokens: those use the outer triangles,
whereas XPQ is the central triangle. Kite payments have four-fan centres,
and quadruple touch/end reservations have two-fan centres. A single-edge
token identifies its unique face; here the only simple corner is X, so
none of these payments can use either token. They survive in `N_res-F`.

Different central caps give different tokens, since a single cap identifies
its face and its unique three-fan simple corner. They are disjoint from
the bounded empty-ray tokens, whose edges are unused, and the mixed-kite
single-cap tokens, whose faces have four-fan centres. This proves the
Delta_N bound. Each bounded empty multiple ray also leaves a distinct
unused-edge slot in Delta_Z, giving the Delta bound.

This exposes actual residual credit in the positive-credit cases. It does
not claim that two H tokens can independently pay every triple incidence
in a mutual component.

## 9. Broader ownership candidate and a refuted allocation shortcut

Define `Q0` to count lines with both ends bad wedges and **no bounded unused
segment**; double segments are allowed. Thus `Q0>=P0`. The stronger
candidate

\[
\boxed{Q_0\le2I+2U+\Delta_N}
\tag{O2Q}
\]

is **UNPROVED**. It passes all 14,376 reconstructed 93s, the 29 binding
witnesses, and the 3,445 records of the four earlier datasets, with minimum
slack 0, 8, and 0 respectively. Its 93 coverage is nontrivial: 1,014
records have extra double lines in `Q0-P0`, including 356 eligible records.
On the 29 binding witnesses, 11 have extra double lines. O2 itself is
tight with positive `P0` on 3,170 of the 93 records, all eligible.

**Residual-only shortcut REFUTED.** One cannot pay the UI lines using §7
and then require every remaining perfect line to be paid solely by
Delta_N. The candidate `P0-|H_UI| <= Delta_N` fails on eight eligible 93s.
The first/minimum failure is record 7731:

```text
pi=4, U=3, I=1, Delta=Delta_N=4, P0=6, |H_UI|=1
perfect_lines=[2,4,6,7,9,10]; H_UI=[9]
word_valid=True; structural_class=True; triple_optimality=True
remaining perfect lines=5 > Delta_N=4
```

Line 10 has two triples and one I-cap step; the other four remaining lines
have one triple each. All four triples have a mutual block. This example
requires reassigning some **unused** U/I labels to lines in the mutual
part, rather than reserving all U/I labels for the restricted subset and
discarding their slack. Its complete word and inventories are saved in
`all8_work/tradeoff_inventory93/non_UI_line_payment_minimum.json`.

The even stronger proposal to pay every non-UI triple incidence from
Delta_N also fails: 21 records overall, 17 eligible, minimum slack -2
at record 234 (`non_UI_payment_minimum.json`). Raw incidences can include
five triples on one perfect line; their parity, not their count, must be
transported. These counterexamples concern allocations, not B, A, or O2Q.

The practical next proof obligation is a disjoint allocation that uses
the **remaining** UI labels together with the free N tokens after §7,
then also covers the double lines in `Q0-P0`. There is still no derivation
of B from that allocation, and no strict all-8 surplus proof.

## 10. Inventory verification and exact outputs

The local proofs in §§7–8 were checked with `tradeoff_inventory.py` after
the reconstructed metrics were complete. It verifies the 64-mask local
calculation, actual injective UI labels on eligible arrangements, all H
central-cap tokens against the old claimed tokens, distinctness and
disjointness of the H/empty/mixed tokens, and the residual lower bound.
It counts raw perfect lines before filtering eligibility. The assertion
checks all pass; there are no reconstruction errors in the scorer runs.

| Cohort | Records | Eligible | H caps | Eligible H caps | Residual bound failures |
|---|---:|---:|---:|---:|---:|
| 93 cache | 14,376 | 13,718 | 2,739 | 903 | 0 |
| Four earlier datasets | 3,445 | 2,259 | 675 | 297 | 0 |
| Lead binding witnesses | 29 | 29 | 5 | 5 | 0 |

On the eligible 93 cohort the UI allocation covers 49,574 line occurrences
across 12,498 arrangements. The residual H payment is exercised on 285
eligible 93 arrangements, not solely on high-slack all-8 examples.
Counts are per supplied record; overlapping source datasets are **not**
claimed to be disjoint samples.

```bash
python -m py_compile work/bbl/tradeoff_check.py work/bbl/tradeoff_inventory.py
python work/bbl/tradeoff_check.py --progress 0 \
  --out work/bbl/all8_work/tradeoff_all8_witnesses \
  work/eng/oth/wit3/wit_sat.jsonl
python work/bbl/tradeoff_check.py --progress 1000 \
  --out work/bbl/all8_work/tradeoff_gallery \
  work/eng/lattice/lattice18.jsonl work/eng/lattice/lattice_family.jsonl \
  work/eng/lattice/mixed_all.jsonl work/phi/gallery18.jsonl
python work/bbl/tradeoff_inventory.py \
  --out work/bbl/all8_work/tradeoff_inventory93 \
  work/bbl/all8_work/tradeoff_rebuilt93/metrics.jsonl
python work/bbl/tradeoff_inventory.py \
  --out work/bbl/all8_work/tradeoff_inventory_all8 \
  work/bbl/all8_work/tradeoff_all8_witnesses/metrics.jsonl
python work/bbl/tradeoff_inventory.py \
  --out work/bbl/all8_work/tradeoff_inventory_gallery \
  work/bbl/all8_work/tradeoff_gallery/metrics.jsonl
```

Each inventory directory contains `summary.json`, `inventories.jsonl`,
and the minimum-slack word for every tested bound. Run inventory commands
only **after** the corresponding scorer finishes: metrics are streamed
during reconstruction. One premature concurrent inventory attempt read
an incomplete line and was discarded; the final complete 14,376-record
inventory run above passed.

These are exact sample checks using the accepted arrangement helpers.
No independent arrangement parser, SAT certificate, or universal proof
of B/A/O2/O2Q is claimed. The new local proofs await the lead's review.

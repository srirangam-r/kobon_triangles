# The all-8 case after the 2 October 2026 deadline

These notes were written after the submission (3–30 October 2026). They are hand proofs. **No human has refereed
them.** Where a note says "refereed", the referee was an independent AI agent with fresh context. "Unrefereed" means
not even that. File names refer to earlier notes by their working names:
- `SOL_TASK8.md` Addenda = `../STAGE2_STAR_LEAD_NOTES.md`;
- `STAGE2_TASKn.md` and `ALL8_NOTEn.md` are in `..`;
- `THEORY.md` is in `../../technical_notes/`.

## Setting
A 94 has Λ = 6, where Λ = π + U + H, π = 18 − W (W = number of bad wedges), and the hard credit is
H = ½ΣS° + K₃ + 2K₄ + ½Δ (`../ALL8_NOTE3.md`).

## Results

| Result | Status | Note |
|---|---|---|
| **Stage 2 closed.** The isolated double-case-B star, the last configuration of the zero-credit corner, does not exist (Lemmas R, M, Q, Z). So K(18) = 93 follows from (B) alone | proved; refereed | `STAR_CASES.md` |
| **Theorem 0.** The Stage-2 proofs never use U = 0, so every 94 has H > 0 | proved (audit of the Stage-2 notes) | `W13.md` §0 |
| **H = 1 is impossible** (cases (a)–(e): K₃ = 1, ΣS° = 2, ΣS° = 1 with Δ = 1, Δ = 2). The proofs use only the credit budget, not W | proved; every part refereed | `W13.md`, `W13_caseE.md`, `W13_paths.md`, `W13_caseBCD.md` |
| **Hence every 94 has H ≥ 2 and at least 14 bad wedges** | follows from the above | |
| Lemma UM: every double-B star has a single edge in each of its two edge sextuples, so Δ ≥ 4 at the star. This needs no Δ hypothesis | proved; unrefereed | `W14_stars.md` §1 |
| H = 2, pure Δ (Δ = 4): reduction to seven star configurations C1–C7 | proved; unrefereed | `W14_stars.md` §2 |
| C1, C7 impossible | proved; unrefereed | `W14_stars.md` §4 |
| C2, C5 impossible (Lemma T: payment rules from the exact identity) | proved; unrefereed | `W14_C25.md` |
| C4 impossible at W = 14 (for any W it forces a touch, so W ≥ 15). C6 impossible when GU+ is single | proved; unrefereed | `W14_C346.md` |
| C3, and C6 with GU+ double | **open**, reduced | `W14_C346.md` §4.4 (the C3 reduction section was not finished) |
| H = 2, mixed defects: all K-cases (K₄ = 1, K₃ = 2, K₃ = 1 with anything); ΣS° = 1 with Δ = 3; two or three slack-1 quads | proved; unrefereed | `W14_mixed.md` §§3–5.1 |
| H = 2, slack cases with one or two slack-2/3/4 quads | **open**, explicit mask lists | `W14_mixed.md` §§5.2–5.4 |
| W ≥ 15 (few non-bad ends): partial lemmas and excluded sub-cases at W = 15–17 | partial; unrefereed | `Wbig_ends.md` |

**Open.** H = 2 (the items above), then H = 3, 4, 5, or W ≥ 15 directly. No 94 has been found.

## A negative result
An exhaustive search over 18-line arrangements, pruning on waste ≤ 6 (in the style of Parpalak–Utkin,
[arXiv:2607.29236](https://arxiv.org/abs/2607.29236)), is not feasible.

The obstacle is when the waste settles. On the 14,376 catalogued 93s (final waste 9):
- built from one end, 10% still show almost no settled waste at 90% of the sweep;
- built from both ends, 1% still do.

Most of the waste sits at the line ends and in faces running to infinity, and settles last. So budget pruning cannot
cut the search early.

# The Kobon triangle problem for 18 lines

**Main result.** Every arrangement of 18 lines or pseudolines, of any multiplicity, has **at most 94** bounded
triangular faces. A 94 would have to contain a fourfold point all eight of whose angles are triangles. Whether such
an arrangement exists, i.e. whether K(18) = 93, is the one remaining case.

Paper: [`paper/kobon18.pdf`](paper/kobon18.pdf), with LaTeX source in `paper/`.

## Results

K(18) is the maximum number of bounded triangles formed by 18 lines. Previously known:
- 93 is attained;
- 93 is optimal for **simple** arrangements (Blanc 2008);
- with multiple points allowed, only 96 (Tamura) and an unpublished 95 (Clément–Bader).

| # | Statement | Evidence | Status |
|---|---|---|---|
| 1 | **T ≤ 94** for every arrangement of 18 pseudolines (any multiplicity) | exact per-line LP certificates, checked by an exact DP over a finite line automaton | computer-verified |
| 2 | **T ≤ 93** if no point lies on 4 or more lines | the certificates of 1, joint tightness, elimination, SAT with DRAT proofs | computer-verified, independently audited |
| 3 | A vertex-maximal 94 has only triple points and fourfold points of sector type 11111111, 11111110 or 11101110 | exhaustive enumeration of local redrawings | computer-verified, independently re-derived |
| 4 | In such a 94, consecutive (fourfold, triple) pairs have one of 48 local patterns; every triple has both alternating sector sums ≥ 2 | enumeration; short proof | computer-verified / proved |
| 5 | Such a 94 has no 11101110 point, and needs an **all-8** point (11111111) | exact credit certificates | computer-verified |
| 6 | Exact identity Λ = π + U + ½ΣS° + K₃ + 2K₄ + ½Δ, with every term ≥ 0, where Λ = 288 − 3T. **K(18) = 93 ⟺ Λ ≥ 7** in the all-8 case | hand proofs, each step checked; exact checks on 3,474 arrangements | proved, not refereed |
| 7 | **K(14) = 54, K(16) = 72, K(20) = 117** for arrangements with no point on 4 or more lines | the certificate of result 1, verified exactly at n = 14, 16, 20; all ingredients hold for every n | computer-verified |
| — | **K(18) = 93** | — | **open**: the all-8 case |

Result 7 matches the known records 54, 72 and 117. Those values have so far been proved only for **simple**
arrangements, although the records at n = 14 and 20 use triple points.

**More results, for general n.**
- **Theorem G (every even n):** if no line passes through two multiple points (and no three lines are mutually parallel), T ≤ ⌊(2n² − 5n + 2t)/6⌋ with t triple
  points. This extends Blanc's bound to arrangements with triple points. Proof: `proofs/additional/theorem_G_even_n.md`
  (hand proof, AI-refereed).
- **Line-automaton theorem (every even n):** for arrangements with simple and triple points only, whose triple points
  have restricted local types (three classes), every line has final value ≥ 0, so Λ ≥ n/3. Examples: T ≤ 54 at
  n = 14, T ≤ 72 at n = 16. Exact certificates: `work/eng/T21/certificates.json`.
- **A catalogue of 14,376 distinct 93-triangle 18-line arrangements** (wiring words) with 0 to 21 triple points:
  `data/`.

**Constructions.** Two exact 18-line arrangements with 93 triangles:
- our own, with no multiple points, found by unseeded search;
- one with three triple points, from the Utkin–Parpalak gallery.

93 ties the record; it is not a new record. Both are verified by the competition's exact evaluator and by our
independent checker. The competition's frozen baseline has 16.

**Not yet done.**
- No human refereeing and no formal (Lean) proof; there are no Lean files.
- Some automaton facts used at fourfold points are validated on large data sets but not yet written out by hand.
- The independent audit covers result 2, not the fourfold certificates.
- Details: `paper/kobon18.pdf` §8 and `proofs/STATUS.md`.

## Check it yourself

```sh
python3 checker/kobon_check.py arrangements/n18_T93_anneal_official/solution.json   # 93, two exact methods
python3 checker/test_kobon_check.py                                                   # checker self-tests
python3 tools/build_proof_tools.py                                                    # builds pinned kissat + drat-trim (seconds)
bash certificates/verify_cheap.sh                                                     # fast proof checks (10–20 min)
```

The checker uses only the Python standard library (exact rationals). The exact DP re-verification of the six main certificates (`bash certificates/verify_certs.sh`, about 20 min,
under 10 GB RAM) and everything else are in [`REPRODUCE.md`](REPRODUCE.md) and
[`certificates/README.md`](certificates/README.md).

## Repository map

| Path | Contents |
|---|---|
| `paper/` | paper (PDF and LaTeX source, figures) |
| `arrangements/` | exact line arrangements (`solution.json`), triangle certificates with exact vertices, structure summaries |
| `checker/` | independent exact triangle counter (two methods) and tests |
| `certificates/` | proof certificates, verification commands, expected outputs, logs, manifest |
| `search/`, `work/`, `tools/` | the code and data used by the certificates: automaton, LP/DP, SAT encodings, enumerations, checkers. The layout is kept so that every command runs unchanged. |
| `data/` | the 93 catalogue and the all-8 witness arrangements |
| `proofs/` | statements and proofs: status table, technical notes, notes on the open all-8 case |
| `evaluation/` | the official competition evaluation report |
| `NOVELTY.md` | the contribution and its relation to prior work |
| `DISCLOSURE.md` | authorship, AI systems and compute used |
| `REPRODUCE.md` | every command, with pinned dependencies (`requirements.txt`) |

## Author

Raj Harshit Srirangam. The work was computer-assisted, with AI systems; see [`DISCLOSURE.md`](DISCLOSURE.md).

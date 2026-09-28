# Constructive searches for a 94 at n = 18 (pseudoline model, not a proof)

## Patterns that guided the choices
- In the gallery (3,016 arrangements with T = 93 at n = 18), every 93 has **D − Z = 3k − 9**.
  - The no-bridge family has B = 2k or B = 2k − 1, with Z falling to 0 at k = 8 (B = 15).
- A 94 needs D − Z = 3k − 6. Without bridges this fails for every k (D = B ≤ 2k), so a 94 must be a
  high-k, low-Z cluster **with bridges**. Only 3 of the known 93s have a bridge.
- **Symmetry:** none of the n = 18 records is combinatorially symmetric. Mirror-symmetric records exist at
  n = 13, 17, 19, 21.

## Symmetry classes for 94 (orbit counting on the end circle)
| Group | Status for 94 |
|---|---|
| half-turn C2 (and C6) | impossible: the half-turn fixes every line and reverses all signs, χ = −χ |
| C9 | impossible: T ≡ 0 (mod 9) |
| D3, mirror axes on lines (M0 class) | impossible: the centre is a vertex ⇒ T ≡ 0 (mod 3). SAT: UNSAT in 0.35 s |
| D3, no fixed lines (M1 class) | impossible: a central triangle needs a mirror-fixed line ⇒ T ≡ 0 (mod 3). SAT: UNSAT in 15 s |
| C3 | needs a central triangle, WLOG on lines {0, 6, 12}: `n18_t94_R12_c0612.cnf`, stopped undecided after 35 min (symmetric 94s judged unlikely: no n = 18 record is symmetric) |
| mirror D1 (M0: axis line + perpendicular line; M1: 9 pairs) | open; see calibration below |

## Calibration (search/sym94.py + run.sh, kissat)
- n = 13, mirror M3: 47 SAT in 307 s; 48 UNSAT in 372 s.
- n = 17, mirror M17: both 85 (a known record, so SAT) and 86 hit the 30-minute cap.
- So plain mirror symmetry at n ≥ 17 is not decidable as one call; it needs cube-and-conquer.

## One-line extension of the n = 17 records (search/ext94.py, work/ext/)
- 10 records with T = 85, with a new line at each of 18 slope ranks and in both orientations: 360 calls.
- Every call runs to completion (no conflict budget).
- Control target 93: SAT for several bases, so 93 is reachable by one line from an 85.

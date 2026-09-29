
# Task T15: SAT verifier for the two-hop Hall lemma (new files only: search/hall_sat.py, work/eng/T15/*)

## Background

A new per-line form of the generalized BBL charging reduces "T ≤ 93 at n = 18" to one local statement, the
**two-hop Hall lemma HL(ε)**. `search/bbl_hall.py` is the **specification**: read its docstring first, then
`values()`, `relation()` and `hall_deficit()`. Your SAT model must reproduce those quantities exactly.

Summary of the definitions (the code is authoritative):
- Rays at triple points: N / B (block) / R (bridge); flank rays of a block; flankers; portions p_L. These are the same
  as in T14 (search/unit_sat.py).
- **Line values v_L** (every line):
  - start with p_L − 1 + Σ over triple points P on L of (3/2·#N rays of P along L − 3/2·#B rays of P along L);
  - **T1**: for a block b = [P, X] (axis l, cap c) whose two flankers are triple points, each flanker whose ray along c
    toward X is N makes c give 3/2 to l. b is *served* iff it received > 0.
  - **F**: every unserved block takes 1 from the line of each of its N flank rays.
- **Relations** between lines (1 hop): common triple point; axis ↔ cap of a block; pure cap c of a block at P ↔ each
  line through P. N2(L) = distance 1 or 2.
- **HL(ε)**: with d_L = v_L − ε·[L passes through a triple point], every set S of lines with d < 0 on S satisfies
  Σ_{L∈S} d_L + Σ_{M ∈ N2(S), d_M > 0} d_M ≥ 0.

Useful T14 facts:
- In T14's UnitModel (search/unit_sat.py), blkP[t, l, d, c] is the block at triple t on axis l, direction d, cap c.
- Its flanking triangles are (l, a, c) and (l, b, c), where {a, b} = t \ {l}.
- So the flankers are a∩c and b∩c, and the flank rays are the rays of a and b at t toward those points.
- Reuse UnitModel by importing it. Do not copy or modify search/unit_sat.py.

## Build `search/hall_sat.py`

A SAT or CP-SAT model deciding, for given n, ε and hops:

> ∃ an arrangement of n pseudolines (triple points allowed, no 4-fold point) and a nonempty set S of lines with
> d_L < 0 for all L ∈ S, and Σ_{L∈S} d_L + Σ_{M ∈ N2(S), d_M > 0} d_M < 0.

UNSAT proves HL(ε) at that n. Guidance:
- Scale all values by lcm(2, denominator of ε) so that they are integers.
- Symmetry: the scheme is label-invariant, and the 4n end-circle symmetries (search/symmetry.py) act transitively on
  lines. So WLOG line 0 ∈ S. Add a `symtest` mode that checks label-invariance of v, d and N2 under those symmetries
  on real arrangements.
- Split into cubes further if needed (for example over the status pattern of line 0). Cubes must cover all cases.

## Mandatory validation (before any production claim)

1. **Fixed-χ.** Fix χ to a real arrangement and compare with `search/bbl_hall.py`:
   - per line: v_L, d_L;
   - per block: served;
   - the 1-hop and 2-hop relations;
   - whether HL is violated (hall_deficit > 0), both for ε = 1/6 and for ε = 1.

   Do this on ≥ 500 arrangements with 0 mismatches:
   - gallery n = 10–22;
   - work/phi/bridge93.jsonl, work/phi/cal16_72.jsonl, work/phi/pls16_70_71.jsonl;
   - all of work/bbl/adv/bad.jsonl and work/bbl/lineadv/pilot.jsonl (many triple points).
2. **Planted.**
   - ε = 1 is false on some arrangements of bad.jsonl and pilot.jsonl (see `python search/bbl_hall.py <file> --eps 1`).
     With χ fixed to each of them, the model must be SAT, with the violating S re-checked in Python.
   - Free SAT at n = 10 with ε = 1 must find a violation. Re-check the witness word with bbl_hall.py.
   - Free SAT at n = 11 with ε = 0 must find a violation (odd n; see Production), also re-checked.
3. **Pilot** the production mode ε = 1/6 at n = 10 and 12 first. Report timings before scaling up.

## Production (decisive: every cube SAT or UNSAT, no timeouts; pilot first)

- HL(1/6), hops = 2, at **even** n = 10, 12, 14, 16, 18. n = 18 is the one that matters.
  - HL is false for odd n, already for simple arrangements. BBL's end argument needs n − 2 even, so a clean line of an
    odd arrangement can have no portion. Use odd n only as a quick way to find SAT witnesses when testing.
  - Go as far as the timings allow within your budget, and report the projected cost of the rest.
- Log per cube: result and seconds.
- Write any SAT witness as a wiring word, re-check it with bbl_hall.py, and save it to work/eng/T15/witnesses.jsonl.
  A witness is important news: stop that n and report it.

Output: `work/eng/T15/results.md` (table n × cube → result, time) and `work/eng/T15/REPORT.md`.

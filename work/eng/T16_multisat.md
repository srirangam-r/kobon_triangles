
# Task T16: Hall-lemma SAT verifier for points of ANY multiplicity (new files only: search/multi_sat.py, work/eng/T16/*)

## Background

T15 (`search/hall_sat.py`, on T14's `search/unit_sat.py` UnitModel) verifies the two-hop Hall lemma HL(ε) for
arrangements with simple and triple points only. The proof of T ≤ 93 at n = 18 also needs arrangements with points
of multiplicity m ≥ 4.

**Specification:** `search/bbl_hallm.py`. Read its docstring, then class `Multi`, `values()`, `relation()` and
`hall_deficit()`. It agrees with `search/bbl_hall.py` on triple-only arrangements.

Differences from the triple-only case:
- An m-fold point P (m ≥ 3) has 2m rays. In wiring/χ labelling, with S = sorted lines of P, the counterclockwise
  order is `[(s,-1) for s in S] + [(s,+1) for s in S]` (see `rays()` in work/t3/arr.py).
  - The flank rays of a block on ray i are rays i ± 1 (mod 2m). With the wrap-around this matches the triple case.
- Statuses N / B / R: R means doubly used with a *multiple* far end, B means doubly used with a *simple* far end.
  "Triple" is read as "multiple" everywhere (flankers, pure caps, relation (a)).
- Line values v_L get a **bonus 3(m − 3)** from every m-fold point on L, besides the ray values ±3/2.
- The exact identity 3Λ − n = Σ_L v_L + waste holds for all multiplicities. bbl_hallm.py asserts it on every
  arrangement it tests; waste = number of (unused segment, multiple endpoint) pairs.
- Test data with 4-fold and higher points:
  - wiring words now allow `g**` for a 4-fold point, `g***` for 5-fold, and so on;
  - `work/t3/mutate.push_through(a, P, w)` moves a line w through a multiple point P;
  - `python search/bbl_hallm.py <in> --push K` generates such arrangements. Use it to make your validation set.

## Build `search/multi_sat.py`

- The same question as T15, for arrangements of n pseudolines with points of any multiplicity:

  > ∃ an arrangement and a nonempty set S of lines, line 0 ∈ S, with d < 0 on S and
  > Σ_{L∈S} d_L + Σ_{M∈N2(S), d_M>0} d_M < 0.

- Start from the χ signotope model, but allow any concurrency: drop T14's exclusion of (0,0,0,0) on 4-subsets.
  - A multiple point is a maximal set of ≥ 3 lines that are pairwise concurrent at one point. Represent it however you
    like, for example by (line l, the smallest other line through that crossing).
- Reuse T15's Hall layer (import from search/hall_sat.py; do not modify it) if convenient.
- Bound the multiplicity if needed. At n = 18 you may cap it at m ≤ 6, and must then add a clause forbidding larger
  multiplicities. State clearly what is covered.

## Mandatory validation

1. **Fixed-χ.** Compare with bbl_hallm.py on ≥ 600 arrangements with 0 mismatches:
   - ≥ 300 with a 4-fold point;
   - ≥ 30 with a 5-fold point, if push_through can make them;
   - the rest triple-only, where the values must also agree with T15's model.

   Compare per line v_L and d_L, served flags, relations, and the HL verdict for ε = 1/6 and ε = 1.
2. **Planted.** ε = 1 violators must be SAT with χ fixed. Free SAT at n = 10, ε = 1 must find a violation; re-check it
   with bbl_hallm.py.
3. **Pilot** ε = 1/6 at n = 10, 12 and report timings.

## Production (decisive, no timeouts; pilot first)

- HL(1/6), hops = 2, even n = 10, 12, 14, 16, 18, with multiplicity ≥ 4 allowed.
  - n = 18 is the one that matters.
  - Instead of repeating T15's triple-only search, you may add the clause "some point of multiplicity ≥ 4 exists". This
    is sound together with T15's triple-only result; say so explicitly.
- Log per cube: result and seconds. Save any witness to work/eng/T16/witnesses.jsonl, re-checked with bbl_hallm.py.

Output: `work/eng/T16/results.md` and `work/eng/T16/REPORT.md`.

# Datasets

| File | Contents |
|---|---|
| `kobon18_93_catalogue.jsonl` | 14,376 distinct wiring words of 18-pseudoline arrangements with exactly 93 bounded triangles |
| `all8_binding_witnesses.jsonl` | 29 arrangements of 18 pseudolines in the structural class with an all-8 point (SAT realisations; `paper/` §6) |

`kobon18_93_catalogue.jsonl`, one JSON object per line:
- `gens`: wiring word. Generator `i` swaps tracks i, i+1; `i*` reverses three tracks; `i**` reverses four.
- `T` (= 93) and `triples` (number of triple points: 0 to 21).
- `pi`, `W`, `U`, `Delta`: the terms of the credit identity of the paper (Λ = π + U + ½Δ when there are no fourfold
  points).
- `Z`, `end_counts`.

Notes:
- Distinct words, not reduced up to isomorphism or symmetry.
- These are pseudoline arrangements; straight-line realisability is not checked except for the arrangements taken from
  the Utkin–Parpalak gallery.
- Distribution of triple points:
  - 0: 1,130
  - 1: 9,856
  - 2: 1,718
  - 3: 433
  - 4–9: 1,124
  - 10–21: 115
- Sources: simulated annealing, exact local search and dynamic-programming walks, and the gallery.
- The word format is read by `search`/`work/t3/arr.py` (`Arr(gens, 18)`); `work/bbl/note3_check.py` computes the
  credit terms.

A larger set of near-optimal arrangements (T = 92–93), used to validate the certificates, is under `work/phi/`.

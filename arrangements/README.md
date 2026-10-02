# Published arrangements

Each directory holds `solution.json` (verbatim copy of the submission), `triangles.json` (checker certificate with exact vertices),
`check.txt` (checker stdout) and `structure.json` (n, points with >=3 lines, parallel classes, T).
Both checker methods agree on every entry. The triangle sets equal those listed by the competition's exact evaluator.

| name | n | T | multiplicity profile | source | solution.json sha256 |
|---|---|---|---|---|---|
| n18_T93_anneal_official | 18 | 93 | none (general position) | our annealing; official evaluator score 93 (`evaluation/`) | 969977f8b6a83b6914443d4ab6f5b9ac6793d361ca99ed0f90b529f9de468721 |
| n18_T93_gallery | 18 | 93 | 3 triple points | Utkin–Parpalak gallery | e27af7264b6f856a51af65822d0bcaa7b587dfa8d154b6acde4132677c75aaa5 |
| n15_T65_anneal | 15 | 65 | none | our annealing | 4e3bb690cacd1e76dbb43d45e56d65602790596ff70e58dd63d0477b9d29b82a |
| n15_T65_gallery | 15 | 65 | none | Utkin–Parpalak gallery | c152bd204494b7823cc9e021d24cfb1d9237b365674519b9e774b11488a78eec |
| n18_T16_baseline | 18 | 16 | none | competition baseline 2ix − y − i² = 0 | 6942297ec251888bb88971ed7426c9a7105ca814537d07e7aee719a6e6998986 |
| n15_baseline | 15 | 13 | none | same family, n = 15 | 495cc5efe860c6f1dbe3bf44c15fc0c01beb4fc49aefc23d8a4d5d78a344a1c1 |

`n18_T93_anneal_official/plot.png`: grey lines, shaded counted triangles (frame shows the central part; a few long thin triangles run off it).

Re-check, from the repo root:

    cd arrangements/<name> && sha256sum solution.json && python3 ../../checker/kobon_check.py solution.json

# Competition evaluation

The 93-triangle construction (`arrangements/n18_T93_anneal_official/`) was scored by the official evaluator of the
AutoLab hill `alejandrozu/kobon-triangles` (exact rational arithmetic, n = 18). The full report is
`autolab_official_report_203bd68f.json`; it includes the triangle list, the parameters and the HMAC signature.

| field | value |
|---|---|
| metric `triangles` | **93** |
| params | `{"n": 18}` |
| evaluator tool | `{"version": "0.11.0", "sha256": "970e4a3fcb74c27e0c56b62efd22b4fab82a755229a8aef8f90bbc00a9cfe275"}` |
| `hill` | `kobon-triangles` |
| `tree_hash` | `7d3f1d91dcb8be8d0eef20be763557bd6d876707` |
| `commit` | `17737195485728d244b0d1f30db55db42df60366` |
| `submission_hash` | `sha256:6ddea9807a72cfd128eebf04588d060f75475e40e1b37af4027a09187b920357` |
| `submission_git` | `exp/nail-laptop-24c/203bd68f@479610e` |
| `passed` | `True` |
| `official` | `True` |
| `final` | `False` |
| `timestamp` | `2026-09-27T17:11:21Z` |
| `signature` | `hmac-sha256:422a0174519c71e4df51e0ad19f96403ddb1dc59a0788c1ddb6e8f143359ff1a` |
| `hill_spec_version` | `2` |

Project (climb): `srirangam-r/kobon-triangles-18`; experiment `203bd68f`. The hill's frozen baseline
(`examples/baseline`, 18 parabola tangents) scores 16.

The report's triangle list equals, as a set, the list produced by the independent checker in `checker/`.
The `submission_hash` is the evaluator's hash of the scored submission tree, not the sha256 of `solution.json` alone.

Local re-evaluation with the public evaluator (`hills` 0.11.0). First install the hill as described in its README
(`autolab hills check kobon-triangles`), then:

    uv tool run --from hills==0.11.0 hills eval arrangements/n18_T93_anneal_official -H kobon-triangles
    # -> PASSED triangles=93 (validation mode)

The same count and triangle set are reproduced without the hill by `checker/kobon_check.py`.

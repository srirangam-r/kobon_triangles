# Five-triple-point certificate sample: blocked before solving

This is engineering work, not a construction or a new impossibility proof.
Every `solution.json` remains unchanged. The checker implementation is recovered
from commit `f4be7160`; this branch adds a fixed-sample runner and failed-stage
proof-size reporting.

## Missing prerequisite

The required existing case split is not available in the fetched repositories:

- `work/t3/k5_patterns.jsonl`: the authoritative ordered 192-row pattern family;
- `work/t3/k5_patterns.py`: its generator, referenced by C32_spec;
- `work/referee4/k5_patterns_check.py`: independent regenerator, referenced by
  AUDIT_k5.

`search/k5_cubes.py` converts those patterns to clauses but does not generate the
patterns. Neither the patterns nor the two generators occur in available Git
history. The source repository's only advertised branch is `main` at
`9484ee705c0c40e343cf5a46fb4c356353b711d6`. It was fetched directly from
`https://github.com/srirangam-r/kobon_triangles.git`; origin was also refreshed
and its main remains `f44a9a692f1c9b2103cdc8aced2a34c69a7f45e2`.
The absence was checked with `git ls-tree` and path-specific `git log --all`.
The pinned tool binaries are cached and available; tool availability is not the
blocker. Existing audit and status files are not modified.

**No cases were selected or solved.** There are no 18-line LRAT outcomes, proof
sizes or stage runtimes to report. Planned indices are zero-based **0, 96, 191**
(first, upper middle, last in original order), not a claim to possess those rows.
The machine-readable preflight record is `manifest.json`.

Provide the original ordered pattern file or its documented generator before
running this sample. Do not regenerate a different split from prose or substitute
the small validation instances. Once inputs are restored, the runner uses the
existing base and cube builders without extra assumptions or symmetry breaks.

## Reproduction

Install the already pinned SAT-builder requirements and link the pinned tools:

```sh
uv venv tools/.venv
uv pip sync --python tools/.venv/bin/python tools/requirements-proof.txt
python3 tools/build_proof_tools.py --jobs 2
python3 search/test_k5_lrat_sample.py
```

Preflight (stdlib only, exit 2 until the missing pattern file is supplied):

```sh
python3 search/k5_lrat_sample.py \
  --work-dir "$AUTOLAB_DATA_DIR/k5-lrat-sample" \
  --output work/t3/k5_lrat_sample
```

Actual campaign after recovering the input, with the same options plus `--run`
and the environment's Python:

```sh
tools/.venv/bin/python search/k5_lrat_sample.py \
  --patterns work/t3/k5_patterns.jsonl \
  --work-dir "$AUTOLAB_DATA_DIR/k5-lrat-sample" \
  --output work/t3/k5_lrat_sample \
  --solve-timeout 600 --convert-timeout 600 --check-timeout 600 \
  --build-timeout 600 --heap-mb 2048 --stack-mb 256 --run
```

Run that command in the background with a durable log when using the coding
agent. Builds are cached under a source/input/dependency hash with a file lock;
cache reuse checks all artifact hashes. Cases run sequentially (one at a time).
Before the first solve the manifest records source, pattern, base, IDs and
cube-family hashes, exact selected indices, patterns, and complete cube clauses.
The pipeline logs all attempted outcomes and stage times, retains SAT models,
and removes large temporary CNF/DRAT/LRAT files. Proof sizes are also recorded
for partially written proofs on timeout. `VERIFIED_UNSAT` requires cake_lpr
acceptance, not just a solver or converter exit. Three certificates, if accepted,
would prove only those assembled Boolean formulas unsatisfiable, not case-family
coverage or geometric encoding soundness.

The runner checks family size/schema, not authenticity or mathematical coverage;
restored inputs still need authoritative provenance. Unit tests use synthetic
rows solely to test index selection and refusal behavior, never as proof cases.

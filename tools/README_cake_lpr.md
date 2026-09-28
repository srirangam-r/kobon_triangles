# Verified proof-checking pipeline

This engineering change leaves `submission/solution.json` unchanged. The geometry
evaluator cannot assess these files; preserve this branch for separate review.

## Build

Requirements: Linux x86-64, Python 3, Git, GCC, make, and network access on the first
build. The pipeline itself has no Python package dependencies.

```sh
python3 tools/build_proof_tools.py --jobs 2
```

`proof_tools.lock.json` pins the full upstream commit of Kissat, drat-trim and
cake_lpr. Sources and executables are cached under `$AUTOLAB_DATA_DIR/proof-tools`
(or `tools/.cache/proof-tools` when unset). Use `--cache DIR` to choose another
location. An exclusive `flock` guards population. `tools/kissat`,
`tools/drat-trim`, and `tools/cake_lpr` are generated links into the cache; they
are not committed. Repeated builds verify recorded executable hashes before
skipping compilation. Existing tool directories are not overwritten. The local
`tools/proof_tools.build.json` records revisions and binary SHA-256 hashes.

The build helper invokes `make cake_lpr`, `./configure && make` for Kissat, and
`make drat-trim`. cake_lpr is built by GCC from upstream's distributed verified
assembly and C runtime. This is **not** a local regeneration of the HOL4 proof
or a fresh run of the verified CakeML compiler. The pinned upstream README gives
these sources for its generated assembly:

- HOL4: `0ae7030322cdf2b0d46dc9d5503e2d5eae2fa726`
- CakeML: `fb377b4bb704497c921cde68ccc8da3b4f0e9132`

The upstream checker supports ARMv8 via `make cake_lpr_arm8`; the automated
helper deliberately requires x86-64 instead of silently building the wrong
architecture. Other installations can pass tool paths directly to the pipeline.

## Run

```sh
python3 search/lrat_pipeline.py cubes.jsonl base.cnf results.jsonl \
  --solve-timeout 600 --convert-timeout 600 --check-timeout 600 \
  --heap-mb 1024 --stack-mb 256
```

Rows follow `search/drat_cubes.py`: `tag` or `u`/`S` identifies a cube; `units`,
`clauses`, and `top` specify its additions. Missing lists default to empty.
An empty clause is allowed and makes the assembled CNF contradictory. When
omitted, `top` is inferred from **both units and clauses**, including the base
header; an explicit `top` smaller than any used variable is rejected. Cube
generators must allocate new variables above the base header's variable count.
References to existing variables are legal, so the pipeline cannot detect a
generator that *intended* a fresh variable but reused an existing number.

For each cube the pipeline:

1. Validates DIMACS, preserves clause order, and writes base + cube with a new header.
2. Runs Kissat, writing text DRAT by default (`--binary-drat` also supported).
3. For UNSAT, runs `drat-trim input.cnf proof.drat -L proof.lrat`.
4. Requires converter success, then runs cake_lpr on **that same assembled CNF**
   and the LRAT file. One explicit edge case: drat-trim exits early without LRAT
   if the input already contains an empty clause. After that conversion attempt,
   the pipeline generates a single LRAT step referencing that input clause and
   records `lrat_source=input_empty_clause_reference`. This is untrusted proof
   generation, not a bypass: cake_lpr must still accept the resulting proof.
   `VERIFIED_UNSAT` requires checker exit code zero and the exact line
   `s VERIFIED UNSAT`. Neither a solver UNSAT nor drat-trim success is enough.
5. Appends and fsyncs a JSONL record, then continues. Temporary CNF/DRAT/LRAT and
   stdout/stderr files are automatically deleted, including on failures. Bounded
   output tails and hashes remain in the log; SAT stdout/models are retained
   beside the log. To recheck a deleted proof, rerun with `--rerun`.

All stages have independent timeouts and kill only their own process groups.
Timeout, tool error, conversion error, checker rejection, and SAT are distinct
statuses. SAT is not a proof and is not independently model-checked here. Empty
cube families and malformed inputs are rejected, rather than reported as success.
The CLI returns nonzero for failed/unfinished stages; zero can include SAT and
must **not** be read as a family-wide UNSAT result. Inspect every row's status.

Resume fingerprints include base contents, the entire cube, pipeline source,
tool binary hashes/paths, and runtime options. Only completed SAT or verified
UNSAT rows are skipped. A log lock prevents concurrent append races; damaged
JSONL is rejected. Proof and assembled-CNF hashes support provenance. This is an
operational audit log, not a cryptographically signed formal certificate archive.

cake_lpr's pinned version accepts heap/stack sizes as command-line options
`--CML_HEAP_SIZE=MB` and `--CML_STACK_SIZE=MB`; it no longer reads those settings
from environment variables. The pipeline forwards them explicitly.

## Validation

Only the test generator needs python-sat. Exact Python dependency versions are in
`requirements-proof.txt`; no training, MLflow, or geometry scoring is involved.

```sh
uv venv tools/.venv
uv pip sync --python tools/.venv/bin/python tools/requirements-proof.txt
tools/.venv/bin/python search/test_lrat_pipeline.py --output /tmp/lrat-validation
```

Three small CNFs from the existing simple-arrangement SAT builder are tested:
4 lines requiring 3 triangles, 5 requiring 6, and 6 requiring 8. These are proof
plumbing tests, **not** new mathematical bounds or official triangle scores.
The cases cover empty cubes, fresh unit-only variables, clause extensions and
binary DRAT. Additional controls test SAT model retention, timeout handling,
resume invalidation, malformed inputs, and rejection of empty/fabricated LRAT
proofs. See `work/t3/lrat_validation_summary.json` for the recorded run and
`work/t3/lrat_validation_results.jsonl` for full stage logs, commands and hashes.

The recorded validation passed all three UNSAT cases (14/59/181 base variables,
34/180/578 clauses respectively), one SAT-model control, seven groups of
input/error/resume controls, and the explicit empty-clause fallback. Each
nontrivial UNSAT case passed through drat-trim and cake_lpr, including the binary
DRAT case. A second invocation reused completed fingerprints without duplicate
records, and a second tool-build invocation reused the verified cached binaries.
No large 18-line proof campaign was run in this task.

## What is (and is not) established

cake_lpr supplies the formally verified checking step. Kissat, drat-trim, and
this Python orchestration are not formally verified. The upstream verified
artifact and its C interface, assembler/linker, OS and hardware remain part of
the practical trust assumptions. This work does not re-prove upstream results.

An accepted proof establishes unsatisfiability only of the assembled DIMACS
formula. Soundness of the geometric encoding, necessary-condition lemmas,
auxiliary-variable allocation, and exhaustive coverage by the cube family
remain separate obligations. A solver campaign must discharge those obligations
before claiming a Kobon impossibility result. These tiny tests close no open
18-line proof case.

# Five-triple-point LRAT batch: blocked before solving

Experiment `88079604`. This is an engineering task, not a construction search.
Every `solution.json` is unchanged. **No 18-line cube was solved or certified.**

## What is available

The checkout started at `f44a9a692f1c9b2103cdc8aced2a34c69a7f45e2`, not at the
requested checker commit. The eight checker deliverables from `f4be7160` were
restored unchanged: the pipeline, its tests, pinned build script and tool lock,
Python requirements, build documentation, and two historical small-instance
validation records. Those historical records are not results of this batch.

The unchanged `search/build_k5.py`, `search/k5_cubes.py`,
`work/loop/claims/C32_spec.md`, and `work/loop/verdicts/AUDIT_k5.md` are available.
The audit describes an existing 192-row case family (32 distinct non-wedge sets)
for exactly five triple points, no doubly used bridge, and its remaining
clean-line/exception cases. We do not add assumptions or symmetry breaks.

## Missing originals and recovery checks

The indispensable input `work/t3/k5_patterns.jsonl` is absent. So are its
specified generator `work/t3/k5_patterns.py` and independent check
`work/referee4/k5_patterns_check.py`. The base CNF, IDs, and encoded cube JSONL
are absent too, but those can be rebuilt once the original pattern family is
available. Merely rebuilding the base does not recover the missing patterns.

Checks performed before stopping:

- `git fetch origin --prune` succeeded. Published project refs are `origin/main`
  at `f44a9a6`, restore branch `db39a7ef` at `b355811`, and restore branch
  `f1a1e25b` at `4a7f81c`. None contains the pattern family.
- The source URL `https://github.com/srirangam-r/kobon_triangles.git` publishes
  only branch `main` at `9484ee705c0c40e343cf5a46fb4c356353b711d6` (no tags).
  That commit is already in local history; its tree has none of these inputs.
- `git log --all -- work/t3/k5_patterns.py work/t3/k5_patterns.jsonl
  work/referee4/k5_patterns_check.py` returned no history.
- The checker commit `f4be7160` contains no five-point pattern/cube/CNF data.
- No matching `*k5*` file was found within three levels of this project's
  persistent data cache. Other worktrees and the owner's private working
  directories were not searched or modified.

Retry note: this coding checkout again started at `f44a9a6`. The experiment's
remote branch already held preflight commit `4a9da8a`; after checking its files,
we recovered it by fast-forward rather than overwriting that work. Rechecking
published source refs, local history, commit `40004cc1`, and the project's data
cache still found no pattern family or referenced generator. Both preflight
unit tests passed again, and the refreshed manifest again reports
`BLOCKED_MISSING_PATTERN_FAMILY`. No solver or certificate checker was launched
on this retry. This is an incomplete validation, not three failed proof cases.

**Required action:** publish the original ordered 192-row pattern file, or its
original deterministic generator with any dependencies, in an accessible
project commit. Supplying the independent checker is desirable for confirming
identity/coverage. Do not invent a replacement family to obtain test outcomes.
The order matters because this experiment fixes the rows before solving.

## Delivered preflight

`search/k5_lrat_preflight.py` records hashes and availability of inputs and
encoding sources. Its planned zero-based indices are **0, 96, 191** (first,
`count // 2`, last of 192 rows). These are planned indices, not selected actual
cubes: no complete row is available now. On complete inputs it records each
chosen original pattern and full cube constraints in the manifest, before any
solver is launched. It checks count and required fields, not mathematical
soundness, provenance authenticity, or cube-to-pattern semantic equivalence.

Current record: `work/t3/k5_lrat_preflight.json`. The status is
`BLOCKED_MISSING_PATTERN_FAMILY`, with `solver_launched=false` and no selected
rows. There are no solver runtimes or proof sizes to report. No costly build or
solver campaign was launched and no proof files were produced.

Run the small plumbing tests (temporary synthetic fixtures, never solver inputs):

```sh
python3 search/test_k5_lrat_preflight.py
python3 search/k5_lrat_preflight.py --output work/t3/k5_lrat_preflight.json
# Exit 2 is expected while the original patterns are absent.
```

## Resume only after the original input is supplied

Choose a persistent output directory in configuration, outside a disposable
worktree. The following is a recipe, **not an executed campaign**. Pin the
source revision supplying the recovered patterns and retain its hash. Run
builds under a population lock; retain source hashes with the outputs and do
not reuse outputs built from different sources.

```sh
# BATCH points at a persistent directory selected by the caller.
: "${BATCH:?set a persistent batch directory}"
mkdir -p "$BATCH"
uv venv tools/.venv
uv pip sync --python tools/.venv/bin/python tools/requirements-proof.txt
python3 tools/build_proof_tools.py --jobs 2
# Inside the persistent directory's population lock, if not already built
# from these exact sources:
tools/.venv/bin/python search/build_k5.py "$BATCH/k5.cnf"
tools/.venv/bin/python search/k5_cubes.py "$BATCH/k5.ids.json" \
  work/t3/k5_patterns.jsonl "$BATCH/k5_cubes.jsonl" "$BATCH/k5.cnf"
python3 search/k5_lrat_preflight.py --base "$BATCH/k5.cnf" \
  --ids "$BATCH/k5.ids.json" --cubes "$BATCH/k5_cubes.jsonl" \
  --output "$BATCH/manifest.json"
```

Save the three full cubes from `manifest.json`'s `selected_rows` in order to
`selected_cubes.jsonl`. Retain the manifest before solving. Run **serially**
(one solver at a time, within the requested maximum of two):

```sh
python3 search/lrat_pipeline.py "$BATCH/selected_cubes.jsonl" \
  "$BATCH/k5.cnf" "$BATCH/results.jsonl" \
  --solve-timeout 600 --convert-timeout 600 --check-timeout 600 \
  --work-dir "$BATCH/scratch"
```

Do not replace selected cases after observing their outcomes. Preserve SAT
models and every compact stage log; distinguish timeout, conversion/checker
failure, SAT, and cake_lpr-accepted UNSAT. The pipeline now records sizes
for completed proofs and partial proof files on timeouts before scratch cleanup.
Missing sizes must not be reported as zero. The automated recovery/build/run
entry point is `search/k5_lrat_sample.py`; see `k5_lrat_sample/README.md`.
Only checker acceptance certifies an assembled Boolean formula. Three accepted
certificates would not establish family coverage or geometric encoding
soundness, and would not close a new Kobon case. Claims, ledger entries, and
referee verdicts are unchanged.

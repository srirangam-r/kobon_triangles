# Reproducing the results

Requirements:
- Python ≥ 3.10.
- The checker needs nothing else.
- The proof certificates need the pinned packages in `requirements.txt`, run with `uv`
  (`uv run --no-project --with-requirements requirements.txt python ...`) or a virtualenv.
- SAT proof re-checks need kissat and drat-trim (see `certificates/README.md`).

## 1. Triangle counts (seconds, standard library only)

```sh
python3 checker/test_kobon_check.py                       # self-tests: known small cases, the 16-triangle baseline
for d in arrangements/*/; do python3 checker/kobon_check.py "$d/solution.json" | tail -1; done
python3 checker/kobon_check.py arrangements/n18_T93_anneal_official/solution.json --json /tmp/t.json
```

- Each run prints the count from two independent exact methods and exits nonzero if they disagree.
- `arrangements/*/triangles.json` holds the certificate: line triples with exact vertices.
- The official evaluator's report is in `evaluation/`.

## 2. Proof certificates

See `certificates/README.md` for the full table: claim, files, command, expected output, runtime, RAM.

```sh
python3 tools/build_proof_tools.py       # pinned kissat and drat-trim (needs a C compiler)
bash certificates/verify_cheap.sh        # all fast checks (~10 min)
bash certificates/verify_certs.sh        # exact DP re-verification of FC-M, the credit and adjacency certificates (~20 min, < 10 GB)
```

Each certificate's command, expected output, runtime and memory are listed in `certificates/README.md`, with today's logs in `certificates/logs/`.

## 3. The paper

```sh
cd paper && latexmk -pdf kobon18.tex     # needs a TeX distribution
python3 paper/figures/make_figures.py    # regenerates the figure from arrangements/ (matplotlib)
```

## 4. The 93-triangle construction (search)

`search/anneal.py` is the simulated-annealing search (numpy and numba).

```sh
python3 search/anneal.py 18 300 out_dir --workers 12 --seed 18
```

- It uses a float triangle counter only as a heuristic and writes integer coefficients.
- Every result must be recounted exactly (section 1).
- The official arrangement came from this command. Float arithmetic and process scheduling can make reruns differ,
  so the exact arrangement is the one stored in `arrangements/n18_T93_anneal_official/solution.json`.

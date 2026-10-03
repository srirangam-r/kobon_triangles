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
bash certificates/verify_cheap.sh        # all fast checks (10–20 min)
bash certificates/verify_certs.sh        # exact DP re-verification of FC-M, the credit and adjacency certificates (~20 min, < 10 GB)
```

Each certificate's command, expected output, runtime and memory are listed in `certificates/README.md`, with today's logs in `certificates/logs/`.

## 2b. Other n

Multiplicity ≤ 3, every even n from 6 to 40 (`work/eng/othern/TABLE.md`):

```sh
bash work/eng/othern/run_table_all.sh        # rebuilds the graph and runs the exact DP for each n (1.5–3 min each)
```

K(14) = 54 for all arrangements (`work/eng/k14all/RESULT.md`):

```sh
bash work/eng/k14all/verify_fcm_n.sh 13      # FC-M at n = 14 -> log_verify_W13.log: 'exact DP min D*(2*final+2) = 24.0  target * D = 24.0  OK: True'
uv run --no-project --with-requirements requirements.txt python work/eng/k14all/regen_k.py 14   # rebuilds the 4 pattern CNFs for 14 lines (cadical: UNSAT; sha256 in cnf_K14.sha256)
for i in 0 1 2 3; do bash work/eng/k14all/prove_k.sh 14 $i; done   # kissat + drat-trim (needs tools/ built)
```

K(10) = 25 for all arrangements (`work/eng/fcm_othern/RESULT.md`; about 6 minutes, 1.2 GB):

```sh
bash work/eng/fcm_othern/verify_fcm_n.sh 9    # FC-M at n = 10 -> log_verify_W9.log: '... OK: True'
uv run --no-project --with-requirements requirements.txt python work/eng/fcm_othern/regen_k.py 10
for i in 0 1 2 3; do bash work/eng/fcm_othern/prove_k.sh 10 $i; done
uv run --no-project --with-requirements requirements.txt python work/eng/fcm_othern/pert_cover.py 7 25   # lossless redrawings, 7 <= m <= 25
```

The three values n = 14, 16, 20 individually:

```sh
for W in 13 15 19; do
  bash work/eng/othern/run_export.sh $W          # rebuild the automaton graph for n = W + 1 (~1 min, ~3 GB)
  uv run --no-project --with-requirements requirements.txt python work/eng/othern/check_w.py \
      work/eng/othern/g_W$W.pkl $W work/eng/T25/elim/state_2.pkl 1
done
# expected: "W=13 min D*(2*final+2) = 32  need >= 32  final_min = 0  OK" (and the same for 15, 19)
```

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

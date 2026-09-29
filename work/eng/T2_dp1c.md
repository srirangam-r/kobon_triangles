# Task T2: compiled one-line DP

Port the ONE-line extension DP of work/research2/extend_dp.py to a compiled implementation: C built with gcc
through a small build script plus a ctypes/cffi wrapper, or numba if simpler.

**Features:**
- the exact max T;
- the best T per slope rank of the new line;
- optionally, enumeration of all paths with T >= a threshold (useful for two-line search).

**Validate** identical maxima with the Python DP on a few hundred gallery arrangements (n = 10–18, including ones
with triple points), and against work/ext ground truth (n=17: max 93, never 94).

**Benchmark** the speedup against Python.

**Deliverables:** search/dp1fast/ (sources, build script, wrapper, tests) and work/eng/T2/REPORT.md.

# Task T3: solver engineering for the reduced extension model

**Benchmark set:** build 12 hard UNSAT instances from work/lns/push/ext16_bridges/part_*.jsonl (records with
secs > 30). Reconstruct each with seeds16.json sorted by (-beta, -T0, -k) (seed index = record "seed"), chi0 via
chi_from_word(gens, 16), R = record "R", f = record "sign" (or the orientation with chi0[0,1,2] != -1 when sign is
null), target 94, using fastext.Ext.

**Compare solve time for:**
- pysat cadical153 / cadical195 / glucose4;
- the kissat binary tools/kissat/build/kissat on the dumped CNF, default and with --unsat and other options;
- OR-tools CP-SAT with a native linear count (Ext has card=False and solve_cpsat(); use 1 and 3 workers);
- count encodings: seqcounter / totalizer / sortnetwrk / cardnetwrk / kmtotalizer;
- valid redundant constraints you can justify, e.g. per-line bounds on how many triangles can have a side on one
  new line.

**Deliverables:**
- search/fastsolve.py with solve_best(ext) implementing the fastest configuration, validated to give the same
  answers;
- work/eng/T3/REPORT.md with the timing table.

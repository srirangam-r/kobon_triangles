# Task T5: realizability

Given a pseudoline arrangement on 18 lines (a chi dict, possibly with triple points), find integer lines
[a, b, c] (a x + b y + c = 0) whose arrangement has exactly that chi, including exact concurrency at the triple
points, and verify the triangle count with the hill counter in tools/external/kobon-solutions/verification (quick_check).

**Approach:** numeric optimization (hinge losses on orientation signs, equality for concurrencies), then exact
rational snapping (lines through computed intersection points) and exact verification.

**Validate** on gallery arrangements with triple points: round-trip from word to chi to lines to chi, same T.

**Deliverables:** search/realize.py (CLI `realize <chi.json> <out_solution.json>`) and work/eng/T5/REPORT.md.
This is needed only if a search finds a SAT 94, so it must be dependable.

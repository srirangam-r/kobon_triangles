# Independent Kobon checker

`kobon_check.py` is one file, Python 3 standard library only (`fractions`, `json`, `itertools`). It imports nothing from this project.
It reads `{"lines": [[a,b,c], ...]}` (line a*x+b*y+c=0, integer coefficients), rejects duplicate (proportional) lines,
and counts bounded triangular faces with exact rational arithmetic.

## Face definition
A counted triangle is a bounded face of the arrangement (a region no line crosses) whose boundary has exactly 3 corners,
where a corner is a boundary vertex at which the boundary direction changes. Where several lines meet, a vertex on the
boundary that does not turn is not a corner, so a triangle with an extra arrangement vertex on a side still counts. A big triangle cut by
another line does not count, because its pieces are the faces. Parallel lines and multiple points are allowed.

## Two methods (must agree, otherwise exit code 1)
- A, planar face enumeration: all pairwise intersections as exact Fractions, grouped into points; vertices ordered on each
  line; half-edges sorted by exact angle (integer cross products); faces traced; bounded = positive exact area;
  count faces with exactly 3 turning corners (collinear consecutive edges are not corners).
- B, triple test: for each pairwise non-parallel, non-concurrent triple, the triangle is a face iff no other line has
  vertex values of both signs (a line through a vertex or along a side does not cut the open interior).

## Commands
    python3 checker/kobon_check.py arrangements/n18_T93_anneal_official/solution.json --json cert.json
    python3 checker/test_kobon_check.py     # unit tests (3 lines, hill example, 4 lines, triple point, parallels, baseline 16)

Output: counts from A and B, `methods agree`, `TRIANGLES: N`. `cert.json` holds each triangle's zero-based sorted line
indices and exact vertices, plus structure (multiple points, parallel classes). `--n N` asserts the line count.
Exit codes: 0 agree, 1 disagree, 2 usage, 3 wrong n; duplicates/degenerate lines raise an error.

## Runtime
About 0.05 s per arrangement for n=15..18 (even with 17-digit coefficients); O(n^4) in method B.

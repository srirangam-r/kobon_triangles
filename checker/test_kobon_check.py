#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kobon_check import analyse


def count(lines):
    ta, tb, sa, sb, agree, pts = analyse([tuple(l) for l in lines])
    assert agree, (sorted(sa), sorted(sb))
    return len(sa)


# 3 lines in general position: one triangle
assert count([[1, 0, 0], [0, 1, 0], [1, 1, -1]]) == 1
assert count([[1, 0, 0], [0, 1, 0], [1, 2, -3]]) == 1

# 4 lines in general position: L1:x=0, L2:y=0, L3:x+y=1, L4:2x+y=3.
# Hand count: of the 4 triples, 123 is a face (L4 misses it), 234 is a face (vertices
# (1,0),(1.5,0),(2,-1); L1 is x=0, misses it), 124 is cut by L3, 134 is cut by L2. So 2.
assert count([[1, 0, 0], [0, 1, 0], [1, 1, -1], [2, 1, -3]]) == 2

# triple point: three concurrent lines through origin plus a fourth: no triangle among concurrent ones
assert count([[1, 0, 0], [0, 1, 0], [1, 1, 0]]) == 0
# x=0,y=0,x+y=0 concurrent, x+y=1 parallel to third: triangle (0,0),(1,0),(0,1) is cut by nothing? lines 0,1,3 -> 1 triangle
assert count([[1, 0, 0], [0, 1, 0], [1, 1, 0], [1, 1, -1]]) == 1

# parallel lines: 2 parallel + 2 parallel = one cell, no triangle
assert count([[1, 0, 0], [1, 0, -1], [0, 1, 0], [0, 1, -1]]) == 0
# 2 parallel + 1 transversal = no triangle; plus diagonal gives triangles
assert count([[1, 0, 0], [1, 0, -1], [0, 1, 0]]) == 0
# unit square plus diagonal: 2 triangles
assert count([[1, 0, 0], [1, 0, -1], [0, 1, 0], [0, 1, -1], [1, -1, 0]]) == 2

# a triangle subdivided by a line through a vertex is NOT counted; the two halves are
assert count([[1, 0, 0], [0, 1, 0], [1, 1, -2], [1, -1, 0]]) == 2

# hill baseline: lines 2*i*x - y - i*i = 0, n=18 gives 16
assert count([[2 * i, -1, -i * i] for i in range(18)]) == 16

# duplicates rejected
try:
    count([[1, 0, 0], [2, 0, 0], [0, 1, 0]])
    raise SystemExit("duplicate not rejected")
except ValueError:
    pass
print("all tests passed")

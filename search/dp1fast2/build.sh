#!/bin/sh
# Build libdp1f2.so (graph builder, one-line DP, two-line solver) next to this script.
cd "$(dirname "$0")" && gcc -O2 -shared -fPIC -Wall -o libdp1f2.so graph.c dp1.c ext2.c

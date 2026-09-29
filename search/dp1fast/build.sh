#!/bin/sh
# Build libdp1.so next to this script.
cd "$(dirname "$0")" && gcc -O2 -shared -fPIC -Wall -o libdp1.so dp1.c

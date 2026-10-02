# Validate the TRIOPT frame mapping: for every exactly-triple vertex on every line of real mult<=3 arrangements, the
# frame-bit test (bin0+bout0+h1 >= 2 and h0+bin1+bout1 >= 2) must equal the true test on the 6 cyclic sector bits.
import sys
sys.path[:0] = ["search", "work/t3", "work/eng/comp"]
import line_automaton as LA
LA._imports()
from bad_comp import tri_sectors
from arr import Arr
tot = bad = 0
for g, ch in LA.iter_arrangements(sys.argv[1:], True, 400):
    a = ch.a
    for L in range(a.n):
        fr, _ = LA.extract(ch, L)
        for V, f in zip(a.rows[L], fr):
            if f.kind != "T": continue
            s = tri_sectors(a, V)
            true_ok = (s[0] + s[2] + s[4] >= 2) and (s[1] + s[3] + s[5] >= 2)
            frame_ok = not (f.bin[0] + f.bout[0] + f.h[1] < 2 or f.h[0] + f.bin[1] + f.bout[1] < 2)
            tot += 1; bad += (true_ok != frame_ok); nf = globals().get("nf", 0) + (not true_ok); globals()["nf"] = nf
print("triple incidences", tot, "mismatches", bad, "non-optimal incidences", globals().get("nf", 0))

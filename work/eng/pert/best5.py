from pert import words, faces
import sys
m = int(sys.argv[1])
ws = words(m)
best = {}
for w in ws:
    e, t, mm = faces(m, w)
    sc = t - sum(1 for x in e if x > 0)
    best.setdefault(sc, []).append((w, e, t, mm))
for sc in sorted(best)[-3:]:
    print(sc, len(best[sc]))
    for w, e, t, mm in best[sc][:4]:
        print("   ", w, e, t, mm)

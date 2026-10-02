import sys, json, itertools, time
sys.path.insert(0, "/home/nail/stuff/sundai_math/work/eng/star")
from star_direct import *
g = sys.argv[1]; n = int(sys.argv[2]); maxk = int(sys.argv[3]); sizes = [int(x) for x in sys.argv[4].split(",")]
a = Arr(g, n); T0, V0 = a.T(), len(a.events)
for P, ev in enumerate(a.events):
    if len(ev) != 4 or sum(tri_sectors(a, P)) != 8: continue
    nb = sorted({far_end(a, P, r) for r in rays(a, P) if far_end(a, P, r) is not None})
    for m in sizes:
        for sub in itertools.combinations(nb, m):
            t0 = time.time(); r = try_window(g, n, [P] + list(sub), T0, V0, maxk=maxk)
            if r: print(m, sub, "k", r[0], "events", r[1], "best dT,dV", r[2][:2], "%.1fs" % (time.time() - t0), flush=True)

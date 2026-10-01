# Pilot: window-level cell domains under the CLASS (bad words everywhere, pair lemma, no m>=5), K = 18 only
# (class constraints are global, so smaller K is not a sound restriction). Same groups/candidates as cells_sweep_m.
import sys, time, json, random, pickle
ROOT = "/home/nail/stuff/sundai_math"
sys.path.insert(0, ROOT + "/work/eng/T27")
import cells_sweep_m as CS
import classsat as C
import patsat_m as patsat
from pysat.solvers import Solver

def decide_class(pat, limit):
    B, sel = patsat.build(pat, 18)
    C.add_class(B)
    s = Solver(name="glucose4", bootstrap_with=B.cl)
    asm = [sel[e] for e in pat.elements()]
    deadline = time.time() + limit
    try:
        while True:
            left = deadline - time.time()
            if left <= 0: return None
            try:
                ok = patsat._solve(s, asm, left)
            except patsat.Timeout:
                return None
            if not ok: return False
            Ms = set(x for x in s.get_model() if x > 0)
            vio = C.pair_violations(B, Ms)
            if not vio: return True
            for v in vio:
                s.add_clause(C.violation_clause(B, v))
    finally:
        s.delete()

CS.decide = decide_class

if __name__ == "__main__":
    out, procs, limit, N, seed = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    groups = pickle.load(open(ROOT + "/work/eng/T27/cell_groups_m.pkl", "rb"))
    random.seed(seed)
    sel = random.sample([g for g in groups if len(g[4]) == 2], N)
    items = [(g[0], g[1], g[2], g[3], g[4], g[5], limit) for g in sel]
    from multiprocessing import Pool
    t0 = time.time(); nc = nr = 0; secs = []; unk = 0
    with open(out, "w") as fo, Pool(procs) as pool:
        for i, r in enumerate(pool.imap_unordered(CS.group_task, items, chunksize=1)):
            fo.write(json.dumps(r) + "\n"); fo.flush()
            nc += r["ncand"]; nr += len(r["removed"]); secs.append(r["secs"]); unk += r["unk"]
            print(i, "cand", nc, "removed", nr, "unknown", unk, round(time.time() - t0), flush=True)
    secs.sort(); n = len(secs)
    print("DONE groups", n, "candidates", nc, "removed", nr, f"({100*nr/max(nc,1):.0f}%)", "unknown-calls", unk,
          "secs mean %.0f median %.0f max %.0f" % (sum(secs)/n, secs[n//2], secs[-1]), "wall", round(time.time()-t0))

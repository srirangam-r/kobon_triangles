"""exact n=18 SAT (patsat_m, 4-fold points allowed) of a DP path given in the diag_w frame notation.  usage: sat_path.py 'S[00|11]h00a00/22 M[11|11]h1111 ...'"""
import sys, re, time
ROOT = __import__("pathlib").Path(__file__).resolve().parents[3].as_posix()
sys.path.insert(0, ROOT + "/search"); sys.path.append(ROOT + "/work/t3"); sys.path.append(ROOT + "/work/eng/T27"); sys.path.insert(0, ROOT + "/work/eng/T23")
import line_automaton as LA
LA._imports()
import rule_lp as RL, rule_lp_t25m as M
import patsat_m as P
from line_automaton import NONE
def parse(s):
    frames = []
    for tok in s.split():
        m = re.match(r"([STM]P?)\[(\d)(\d)\|(\d)(\d)\]h(\d+)(?:a(\d)(\d)/(\d)(\d))?(?:u(\d)(\d))?$", tok)
        k, bi0, bi1, bo0, bo1, h, a0, a1, c0, c1, u0, u1 = m.groups()
        bi, bo = (int(bi0), int(bi1)), (int(bo0), int(bo1))
        hh = tuple(int(x) for x in h)
        if k == "M":
            f = M.MF("M", bi, bo, NONE, hh, (0, 0), (0, 0))
            if frames and frames[-1].kind == "M" and frames[-1][:5] == f[:5] and getattr(frames[-1], "_dup", True):
                frames.pop()            # the DP lists the self and the exit window of an M vertex: one vertex
            frames.append(f)
            continue
        ub = (int(u0), int(u1)) if u0 is not None else (0, 0)
        frames.append(RL.EFrame(k, bi, bo, ub, hh if k == "T" else (0, 0), (int(a0), int(a1)), (int(c0), int(c1))))
    # the apex classes of the triangles on a segment M -> S/T are stored in the ain of the next frame: copy them to the aout of the M frame
    # (pattern_exact reads aout); M -> M segments carry no apex information
    for i in range(len(frames) - 1):
        if frames[i].kind == "M" and frames[i + 1].kind != "M":
            f = frames[i]
            frames[i] = M.MF("M", f.bin, f.bout, f.ub, f.h, f.ain, frames[i + 1].ain)
    return frames
if __name__ == "__main__":
    fr = parse(sys.argv[1])
    print(len(fr), "frames; lines =", 1 + sum(1 if f.kind == "S" else 2 if f.kind == "T" else 3 for f in fr))
    pat = P.pattern_exact(fr, None)
    t0 = time.time()
    ok, secs, _ = P.solve_exact(pat, limit=int(sys.argv[2]) if len(sys.argv) > 2 else 600)
    print("SAT" if ok else "UNSAT" if ok is False else "TIMEOUT", f"{time.time()-t0:.1f}s")


def realize_path(frames_str, limit=1200):
    """SAT model -> arrangement (Arr) and its numbers.  returns dict"""
    import realize_chi as rc
    from arr import Arr
    from pysat.solvers import Solver
    fr = parse(frames_str)
    pat = P.pattern_exact(fr, None)
    K = 1 + sum(1 if f.kind == "S" else 2 if f.kind == "T" else 3 for f in fr)
    B, sel = P.build(pat, K)
    s = Solver(name="glucose4", bootstrap_with=B.cl)
    ok = s.solve(assumptions=[sel[e] for e in pat.elements()])
    if not ok:
        return None
    Mset = set(x for x in s.get_model() if x > 0)
    chi = {t: (0 if B.z[t] in Mset else (1 if B.pz[t] in Mset else -1)) for t in B.trip}
    word = rc.realize(K, chi)
    return word, K, chi

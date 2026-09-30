import sys
sys.path.insert(0, '/home/nail/stuff/sundai_math/search'); sys.path.append('/home/nail/stuff/sundai_math/work/t3')
sys.path.insert(0, '/home/nail/.claude/jobs/f347ce4a/tmp')
import line_automaton as LA
import importlib.util
spec = importlib.util.spec_from_file_location("f5", "/home/nail/stuff/sundai_math/work/eng/f5star_check.py")
src = open("/home/nail/stuff/sundai_math/work/eng/f5star_check.py").read().split('if sys.argv[1] == "data":')[0]
exec(src)
def xaxis(f):
    return f.kind == "T" and f.bin == (1, 1) and f.bout == (1, 1) and f.h == (0, 0)
def allow(f):
    if f.kind == "S":
        return LA.clean_frame(f)
    return f.kind == "T" and f.bin == (1, 1) and f.bout == (1, 1) and f.h == (0, 0)
feat = lambda prev, cur, nxt: cur.kind == "T"
for name, G in (("F5 ends", LA.Graph), ("F5*", G5)):
    g = G(allow=allow, feat=feat)
    for par, nm in ((1, "even n"), (0, "odd n")):
        v, path = LA.solve(g, (1, 0, 0, 0, 0), parity=par, need_flag=True)
        print(f"{name}: X-axis lines (only X-axis T frames, no capping), {nm}: min portions = {v}", flush=True)
        if path: print("   ", LA.show(path))

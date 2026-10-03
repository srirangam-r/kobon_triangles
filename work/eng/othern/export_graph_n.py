"""Export T25's window graph (built by T25 code) to plain python structures for an independent exact-integer DP.
usage: export_graph.py full|a0 out.pkl   (a0 = graph restricted to state_0['allowed'])"""
import sys, pickle, argparse, time
ROOT = str(__import__("pathlib").Path(__file__).resolve().parents[3])
sys.path.insert(0, ROOT + "/search"); sys.path.append(ROOT + "/work/t3"); sys.path.insert(0, ROOT + "/work/eng/T25/elim")
import __main__
import numpy as np
import rule_lp as RL, rule_lp_t25 as T
__main__.EFrame = RL.EFrame
which, out = sys.argv[1], sys.argv[2]
ap = T.add_args(argparse.ArgumentParser())
o = ap.parse_args(["lp", "--class", "full", "--split", "--alpha", *(["--celldom"] if not __import__("os").environ.get("NOCD") else []), "--wr", "--sv", "--tri", "--pt", "--eps", "0"] + sys.argv[3:])
allowed = None
if which == "a0":
    st0 = pickle.load(open(ROOT + "/work/eng/T25/elim/state_0.pkl", "rb"))
    allowed = st0["allowed"]
t0 = time.time()
G = T.build_graph(o, allowed=allowed)
print("built", time.time() - t0, G.N, len(G.src), len(G.win_list), flush=True)
# windows -> options
nwin = len(G.win_list)
TO = G.TO.tocsr()
WO = G.WO.tocsr()
term_alts = []   # term id -> list of alternatives, each a list of (col, x)
for t, tm in enumerate(G.term_list):
    term_alts.append([[(int(c), float(x)) for (c, x) in opt] for opt in tm])
# check the term structure against TO rows
opts_by_win = [[] for _ in range(nwin)]
for r in range(len(G.ov2)):
    w = int(G.opt_win[r])
    row = WO.getrow(r)
    opts_by_win[w].append((float(G.ov2[r]), [(int(j), float(v)) for j, v in zip(row.indices, row.data)]))
ku = [2 if G.nodes[i][1].kind == "T" else 1 for i in range(G.N)]
data = dict(N=G.N, ku=ku, starts=[int(x) for x in G.starts], src=G.src.tolist(), dst=G.dst.tolist(), ew=G.ew.tolist(),
            tn=G.tn.tolist(), tw=G.tw.tolist(), win_repr=[repr(w) for w in G.win_list], win_kind=[w[1].kind for w in G.win_list],
            opts=opts_by_win, term_alts=term_alts, keys=list(G.cat.keys), extra_rows=getattr(G.cat, "extra_rows", None),
            win_clean=None)
pickle.dump(data, open(out, "wb"))
print("saved", out, time.time() - t0)

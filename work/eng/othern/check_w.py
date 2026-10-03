"""check given weights (A30 certs format: dict key->int, D) against an exported graph with its exact W. usage: check_w.py graph.pkl W [state_pkl idx]"""
import sys, pickle
from fractions import Fraction as F
R = str(__import__("pathlib").Path(__file__).resolve().parents[3])
sys.path.insert(0,R+"/work/eng/A30/elim"); sys.path.insert(0,R+"/search"); sys.path.append(R+"/work/t3")
import __main__, rule_lp as RL
__main__.EFrame = RL.EFrame
import dplib as DP
g, W = sys.argv[1], int(sys.argv[2])
G = DP.Graph(g)
if len(sys.argv) > 3 and sys.argv[3].endswith('.pkl') and 'state' in sys.argv[3]:
    st = pickle.load(open(sys.argv[3],'rb')); c = st['certs'][int(sys.argv[4])]
else:
    c = pickle.load(open(sys.argv[3],'rb'))
D, w = c['D'], c['w']
wcol = G.weights_vec(w)
print("name", c.get('name'), "D", D, "keys", len(w), "present", len(wcol))
ov = G.window_values(wcol, D)
wm = G.wmin_array(ov)
mn = G.path_min(wm, W=W)
print(f"W={W} min D*(2*final+2) = {mn}  need >= {2*D}  final_min = {F(mn-2*D,2*D)}  {'OK' if mn>=2*D else 'FAIL'}")

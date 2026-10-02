# Independent re-derivation of the pair lemma (THEORY section 25) using faces_indep (half-edge tracing) and a plain
# Python exclusion check; compares the allowed/excluded canonical patterns with pair_PQ_all.json.
import itertools, json
from faces_indep import faces_indep
from window import all_words, crossing_set
k = 6; w0 = [(2, 5), (0, 2)]
req, _ = crossing_set(k, w0)
vec0, t0, nv0 = faces_indep(k, w0)
opts = set()
for w in all_words(k, req):
    if list(w) == w0: continue
    v, t, nv = faces_indep(k, list(w)); opts.add((v, t, nv))
opts = list(opts)
nf = len(vec0)
# sector listings: P = event 0, Q = event 1; derived independently from the face order
# order: [top, bottom, left1..left5, right1..right5] -> indices 0,1, 2..6, 7..11
L = lambda g: 2 + (g - 1); R = lambda g: 7 + (g - 1)
Pcw = [R(3), R(4), R(5), 1, L(5), L(4), L(3), L(2)]
Qcw = [L(2), L(1), 0, R(1), R(2), R(3)]
Pccw = list(reversed(Pcw[:-1])) + [Pcw[-1]]; Pccw = [Pcw[-1]] + list(reversed(Pcw[:-1]))
Qccw = [Qcw[-1]] + list(reversed(Qcw[:-1]))
def bits(tri, idxs): return "".join("1" if tri[f] else "0" for f in idxs)
def canon(tri): return min((bits(tri, Pcw), bits(tri, Qcw)), (bits(tri, Pccw), bits(tri, Qccw)))
status = {}
for tri in itertools.product((0, 1), repeat=nf):
    choices = []
    ok = True
    for f in range(nf):
        if tri[f]:
            o = 3 - vec0[f]
            if o < 0: ok = False; break
            choices.append([o])
        else:
            choices.append([o for o in (0, 1, 2, 3) if (o == 3 or vec0[f] + o >= 3) and vec0[f] + o != 3])
    if not ok: continue
    key = canon(tri); irr = False
    for outs in itertools.product(*choices):
        T0 = sum(1 for f in range(nf) if outs[f] < 3 and vec0[f] + outs[f] == 3) + t0
        good = False
        for (v, t, nv) in opts:
            T1 = sum(1 for f in range(nf) if outs[f] < 3 and v[f] + outs[f] == 3) + t
            if T1 > T0 or (T1 == T0 and nv > nv0): good = True; break
        if not good: irr = True; break
    status[key] = status.get(key, False) or irr
import os
ref = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pair_PQ_all.json")))
ex_ref = set(map(tuple, ref["excluded"])); al_ref = set(map(tuple, ref["allowed"]))
ex = {k_ for k_, v in status.items() if not v}; al = {k_ for k_, v in status.items() if v}
print("independent: patterns", len(status), "excluded", len(ex), "allowed", len(al))
print("agree with pair_PQ_all.json:", ex == ex_ref and al == al_ref, "| diff excluded", len(ex ^ ex_ref), "diff allowed", len(al ^ al_ref))

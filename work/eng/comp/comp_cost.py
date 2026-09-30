# Per-bridge-component cost sum_{P in K} c_P, c_P = m(m-2) - D_P - beta_P/2, on real arrangements.
import sys, json, glob
from collections import Counter, defaultdict
sys.path.insert(0, "work/t3")
from arr import Arr, rays, first_seg, far_end

def analyse(a):
    mult = [e for e, ev in enumerate(a.events) if len(ev) >= 3]
    c = {}; adj = defaultdict(set); ring = {}
    for P in mult:
        m = len(a.events[P]); D = 0; beta = 0; s = []
        for r in rays(a, P):
            fs = first_seg(a, P, r)
            if fs is not None and len(a.t[fs[0]][fs[1]]) == 2:
                X = far_end(a, P, r)
                if len(a.events[X]) >= 3:
                    beta += 1; adj[P].add(X); s.append("R")
                else:
                    D += 1; s.append("B")
            else:
                s.append("N")
        c[P] = m*(m-2) - D - beta/2; ring[P] = "".join(s)
    seen = set(); comps = []
    for P in mult:
        if P in seen: continue
        st = [P]; K = []; seen.add(P)
        while st:
            x = st.pop(); K.append(x)
            for y in adj[x]:
                if y not in seen: seen.add(y); st.append(y)
        comps.append(K)
    Lam = a.n*(a.n-2) - 3*a.T()
    assert abs(Lam - (a.Z() + sum(c.values()))) < 1e-9, (Lam, a.Z(), sum(c.values()))
    return c, ring, comps, Lam

files = sys.argv[1:]
dist = Counter(); worst = []; n_arr = 0; mcomp = Counter()
for f in files:
    for line in open(f):
        d = json.loads(line)
        try:
            a = Arr(d["gens"], d.get("n"))
        except Exception as ex:
            continue
        n_arr += 1
        c, ring, comps, Lam = analyse(a)
        for K in comps:
            s = sum(c[P] for P in K); dist[s] += 1
            has4 = any(len(a.events[P]) >= 4 for P in K)
            if has4: mcomp[s] += 1
            worst.append((s, len(K), a.n, a.T(), sorted(Counter(len(a.events[P]) for P in K).items()), f))
worst.sort()
print("arrangements", n_arr)
print("component cost distribution (low end):", sorted(dist.items())[:15])
print("components with a >=4-fold point, cost dist:", sorted(mcomp.items())[:15])
for w in worst[:10]: print("  ", w)

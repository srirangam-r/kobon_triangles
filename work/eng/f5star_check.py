# F5*: all ub flags along L lie on one side (Blanc step 5 for every pair of vertices, not only the ends).
# Test: (1) data validity; (2) automaton with F5*: min touches on clean lines (Blanc L3) for even / odd n.
import sys
sys.path.insert(0, 'search'); sys.path.append('work/t3')
import line_automaton as LA
orig = LA.exact_vec
def touches_vec(prev, cur, nxt, hid=None):
    p, v2, a, b, t = orig(prev, cur, nxt, hid)
    own = int(nxt is not None and cur.bout == LA.NONE)
    return (p - own, v2, a, b, t, own)

class G5(LA.Graph):
    """cls accumulates the OR of all ub flags seen (S frames, and T frames at the ends); (1,1) is forbidden"""
    def objective_weights(self, obj):
        node_id, nodes = {}, []
        def nid(x):
            if x not in node_id:
                node_id[x] = len(nodes); nodes.append(x)
            return node_id[x]
        def wmin(prev, cur, nxt):
            return min(sum(c * x for c, x in zip(obj, v)) for v in LA.options(prev, cur, nxt))
        starts, edges, terms, stack = [], [], [], []
        for f in self.frames:
            if f.bin == LA.NONE:
                x = (None, f, 1 if f.kind == "S" else 0, f.ub, 0, 0, 0)
                starts.append(nid(x)); stack.append(x)
        seen = set(stack)
        while stack:
            x = stack.pop()
            prev, cur, par, cls, flag, role, cp = x
            u = node_id[x]
            if role == 1:
                fl_t = 1 if (flag or (self.feat and self.feat(prev, cur, None))) else 0
                terms.append((u, wmin(prev, cur, None), fl_t, par, cp)); continue
            for nxt in self.by_bin[cur.bout]:
                if not LA.edge_ok(cur, nxt) or not self.edge_allow(cur, nxt):
                    continue
                for last in (0, 1):
                    if last and nxt.bout != LA.NONE: continue
                    if nxt.kind == "T" and nxt.ub != LA.NONE and not last: continue
                    if (cls[0] and nxt.ub[1]) or (cls[1] and nxt.ub[0]): continue
                    c2 = (cls[0] | nxt.ub[0], cls[1] | nxt.ub[1])
                    ni = nxt.info_next(bool(last))
                    fl2 = 1 if (flag or (self.feat and self.feat(prev, cur, ni))) else 0
                    y = (cur.info_prev(prev is None), nxt, (par + (nxt.kind == "S")) % 2, c2, fl2, last, cp)
                    if y not in seen:
                        seen.add(y); stack.append(y)
                    nid(y)
                    edges.append((u, node_id[y], wmin(prev, cur, ni)))
        return nodes, starts, edges, terms

if sys.argv[1] == "data":
    LA._imports()
    bad = tot = 0
    for g, ch in LA.iter_arrangements(sys.argv[3:], True, 10**9, mod=8, part=int(sys.argv[2])):
        for L in range(ch.a.n):
            fr, _ = LA.extract(ch, L)
            fr = LA.normalise(fr)
            viol = any(fr[i].ub[0] and fr[j].ub[1] for i in range(len(fr)) for j in range(len(fr)) if i != j)
            tot += 1; bad += viol
    print("lines", tot, "F5* violations", bad)
else:
    LA.exact_vec = touches_vec; LA._opt_cache.clear()
    for name, G in (("F5 (ends only)", LA.Graph), ("F5* (all)", G5)):
        g = G(allow=LA.clean_frame)
        for par, nm in ((1, 'even n'), (0, 'odd n')):
            v, path = LA.solve(g, (1, 0, 0, 0, 0, 0), parity=par)
            print(f'{name}: clean lines, {nm}: min touches = {v}', flush=True)
            if path and v is not None and v < 1: print('   witness:', LA.show(path))

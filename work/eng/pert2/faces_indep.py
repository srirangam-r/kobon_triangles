# Independent face computation for a partial wiring diagram (window of k tracks, word of block reversals), by
# explicit planar embedding + half-edge face tracing.  Used to cross-check window.faces (gap counting).
# Output in the same convention as window.faces: vec = window-vertex counts of the boundary faces in the order
# [top, bottom, left_1..left_{k-1}, right_1..right_{k-1}], tloc = number of interior faces with exactly 3 vertices.
import math


def faces_indep(k, w):
    N = len(w)
    pos = {}                       # node -> (x, y)
    adj = {}                       # node -> list of neighbour nodes (with geometry via waypoints)
    seg_pts = {}                   # (u, v) -> first waypoint from u toward v (for angles)

    def add_edge(u, v, wu, wv):
        adj.setdefault(u, []).append(v); adj.setdefault(v, []).append(u)
        seg_pts[(u, v)] = wu; seg_pts[(v, u)] = wv

    # wire paths
    perm = list(range(k))
    cur = {}                       # wire -> (last node, its track)
    for t in range(k):
        n = ("L", t); pos[n] = (-1.0, float(t)); cur[perm[t]] = n
    for e, (i, j) in enumerate(w):
        n = ("E", e); x = float(e); yc = (i + j) / 2.0; pos[n] = (x, yc)
        for t in range(i, j + 1):
            wire = perm[t]; u = cur[wire]
            ux, uy = pos[u]
            # waypoints: leave u horizontally at its outgoing track, arrive at n from track t
            add_edge(u, n, (ux + 0.3, float(t)) if u[0] != "L" else (ux + 0.3, float(t)), (x - 0.3, float(t)))
        perm[i:j + 1] = list(reversed(perm[i:j + 1]))
        for t in range(i, j + 1):
            cur[perm[t]] = n
        # remember outgoing tracks for waypoint of next edge: store per wire
        for t in range(i, j + 1):
            seg_pts[("out", n, perm[t])] = (x + 0.3, float(t))
    for t in range(k):
        n = ("R", t); pos[n] = (float(N), float(t)); wire = perm[t]; u = cur[wire]
        add_edge(u, n, (pos[u][0] + 0.3, float(t)), (float(N) - 0.3, float(t)))
    # fix the outgoing waypoint of edges leaving event nodes: the waypoint must be at the wire's outgoing track
    # (recompute by walking wires again)
    perm = list(range(k)); last = {perm[t]: (("L", t), float(t)) for t in range(k)}
    fixed = {}
    for e, (i, j) in enumerate(w):
        n = ("E", e)
        for t in range(i, j + 1):
            wire = perm[t]; u, ytr = last[wire]
            fixed[(u, n)] = (pos[u][0] + 0.3, ytr); fixed[(n, u)] = (pos[n][0] - 0.3, float(t))
        perm[i:j + 1] = list(reversed(perm[i:j + 1]))
        for t in range(i, j + 1):
            last[perm[t]] = (n, float(t))
    for t in range(k):
        n = ("R", t); wire = perm[t]; u, ytr = last[wire]
        fixed[(u, n)] = (pos[u][0] + 0.3, ytr); fixed[(n, u)] = (float(N) - 0.3, float(t))
    seg_pts = {kk: v for kk, v in fixed.items()}
    # boundary rectangle: corners and side edges
    TL, BL, TR, BR = ("C", "TL"), ("C", "BL"), ("C", "TR"), ("C", "BR")
    pos[TL] = (-1.0, -1.0); pos[BL] = (-1.0, float(k)); pos[TR] = (float(N), -1.0); pos[BR] = (float(N), float(k))
    def bedge(u, v):
        adj.setdefault(u, []).append(v); adj.setdefault(v, []).append(u)
        seg_pts[(u, v)] = pos[v]; seg_pts[(v, u)] = pos[u]
    left = [TL] + [("L", t) for t in range(k)] + [BL]
    right = [TR] + [("R", t) for t in range(k)] + [BR]
    for a, b in zip(left, left[1:]): bedge(a, b)
    for a, b in zip(right, right[1:]): bedge(a, b)
    bedge(TL, TR); bedge(BL, BR)
    # rotation system (y grows downward: track 0 on top); angle in standard math orientation with y flipped
    def ang(u, v):
        px, py = pos[u]; qx, qy = seg_pts[(u, v)]
        return math.atan2(-(qy - py), qx - px)
    rot = {u: sorted(adj[u], key=lambda v: ang(u, v)) for u in adj}
    # face tracing: next half-edge after (u->v) is (v->w) with w = the neighbour of v preceding u in ccw order
    seen = set(); faces = []
    for u in adj:
        for v in adj[u]:
            if (u, v) in seen: continue
            f = []; a, b = u, v
            while (a, b) not in seen:
                seen.add((a, b)); f.append((a, b))
                r = rot[b]; idx = r.index(a)
                c = r[(idx - 1) % len(r)]
                a, b = b, c
            faces.append(f)
    def nodes(f): return {a for a, b in f}
    def has_edge(f, u, v): return any((a == u and b == v) or (a == v and b == u) for a, b in f)
    # outer face: contains all four corners
    outer = [f for f in faces if {TL, TR, BL, BR} <= nodes(f)]
    # the outer face is the one traversing the rectangle boundary only
    outer_f = min(outer, key=len)
    inner = [f for f in faces if f is not outer_f]
    def ev(f): return sum(1 for n in nodes(f) if n[0] == "E")
    def find(u, v):
        c = [f for f in inner if has_edge(f, u, v)]
        assert len(c) == 1, (u, v, len(c))
        return c[0]
    top = find(TL, TR); bot = find(BL, BR)
    lefts = [find(("L", g - 1), ("L", g)) for g in range(1, k)]
    rights = [find(("R", g - 1), ("R", g)) for g in range(1, k)]
    bnd = [top, bot] + lefts + rights
    vec = tuple(ev(f) for f in bnd)
    bids = {id(f) for f in bnd}
    tloc = sum(1 for f in inner if id(f) not in bids and not any(n[0] in ("L", "R", "C") for n in nodes(f)) and ev(f) == 3)
    return vec, tloc, N


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/home/nail/stuff/sundai_math/work/eng/pert2")
    from window import faces, all_words, crossing_set
    bad = 0; tot = 0
    for k, w0 in ((4, [(0, 3)]), (5, [(0, 4)]), (6, [(2, 5), (0, 2)]), (5, [(1, 4), (0, 1)])):
        req, _ = crossing_set(k, w0)
        for w in all_words(k, req):
            a = faces(k, w); b = faces_indep(k, list(w))
            tot += 1
            if (a[0], a[1]) != (b[0], b[1]):
                bad += 1
                if bad <= 5: print("MISMATCH", k, w, a[:2], b[:2])
    print("words compared", tot, "mismatches", bad)

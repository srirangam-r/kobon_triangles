#!/usr/bin/env python3
"""Independent exact checker for Kobon triangles (standard library only).

Usage: python3 kobon_check.py solution.json [--json out.json] [--n N]

Counts bounded triangular faces of a line arrangement with exact rational
arithmetic, by two independent methods, and exits 0 iff they agree.
See checker/README.md for the face definition.
"""
import json
import sys
from fractions import Fraction
from functools import cmp_to_key
from itertools import combinations


def load_lines(path):
    with open(path) as f:
        data = json.load(f)
    lines = data["lines"]
    out = []
    for l in lines:
        if len(l) != 3 or not all(isinstance(v, int) and not isinstance(v, bool) for v in l):
            raise ValueError("each line must be 3 integers: %r" % (l,))
        a, b, c = l
        if a == 0 and b == 0:
            raise ValueError("degenerate line %r" % (l,))
        out.append((a, b, c))
    return out


def check_distinct(lines):
    for i, j in combinations(range(len(lines)), 2):
        a, b, c = lines[i]
        d, e, f = lines[j]
        # proportional iff all 2x2 minors vanish
        if a * e - b * d == 0 and a * f - c * d == 0 and b * f - c * e == 0:
            raise ValueError("lines %d and %d are duplicates" % (i, j))


def intersect(l1, l2):
    a, b, c = l1
    d, e, f = l2
    det = a * e - b * d
    if det == 0:
        return None
    return (Fraction(b * f - c * e, det), Fraction(c * d - a * f, det))


def fstr(p):
    return [str(p[0]), str(p[1])]


# ---------------------------------------------------------------- method A
def method_A(lines):
    n = len(lines)
    pts = {}  # point -> set of line indices
    for i, j in combinations(range(n), 2):
        p = intersect(lines[i], lines[j])
        if p is not None:
            pts.setdefault(p, set()).update((i, j))
    # ordered vertices on each line
    on_line = [[] for _ in range(n)]
    for p, ls in pts.items():
        for i in ls:
            on_line[i].append(p)
    out = {}  # vertex -> list of (direction vector, dest vertex, line)
    for i, (a, b, c) in enumerate(lines):
        d = (-b, a)  # direction vector (integers)
        vs = sorted(on_line[i], key=lambda p: d[0] * p[0] + d[1] * p[1])
        for u, v in zip(vs, vs[1:]):
            out.setdefault(u, []).append((d, v, i))
            out.setdefault(v, []).append(((-d[0], -d[1]), u, i))

    def half(v):
        return 0 if (v[1] > 0 or (v[1] == 0 and v[0] > 0)) else 1

    def cmp(x, y):
        hx, hy = half(x[0]), half(y[0])
        if hx != hy:
            return hx - hy
        cr = x[0][0] * y[0][1] - x[0][1] * y[0][0]
        return -1 if cr > 0 else (1 if cr < 0 else 0)

    for v in out:
        out[v].sort(key=cmp_to_key(cmp))  # ccw by angle
    # half-edge id = (u, index in out[u])
    index_of = {}
    for u, lst in out.items():
        for k, (d, v, i) in enumerate(lst):
            index_of[(u, k)] = (d, v, i)
    # twin lookup: edge u->v on line i; twin is v->u on line i
    twin = {}
    for u, lst in out.items():
        for k, (d, v, i) in enumerate(lst):
            for k2, (d2, w, i2) in enumerate(out[v]):
                if w == u and i2 == i:
                    twin[(u, k)] = (v, k2)
    seen = set()
    tris = []
    for start in index_of:
        if start in seen:
            continue
        cyc = []
        e = start
        while e not in seen:
            seen.add(e)
            cyc.append(e)
            tv, tk = twin[e]  # at head vertex, index of reverse edge
            m = len(out[tv])
            e = (tv, (tk - 1) % m)  # next clockwise from reverse => face on the left
        if e != start:
            raise AssertionError("face traversal did not close")
        verts = [c[0] for c in cyc]
        area2 = sum(verts[k][0] * verts[(k + 1) % len(verts)][1]
                    - verts[(k + 1) % len(verts)][0] * verts[k][1]
                    for k in range(len(verts)))
        if area2 <= 0:
            continue  # outer face (or degenerate)
        dirs = [index_of[c][0] for c in cyc]
        corners = []
        for k in range(len(cyc)):
            d0, d1 = dirs[k - 1], dirs[k]
            if d0[0] * d1[1] - d0[1] * d1[0] != 0:
                corners.append(verts[k])
        if len(corners) == 3:
            ls = sorted(set(index_of[c][2] for c in cyc))
            if len(ls) != 3:
                raise AssertionError("triangle face with %d side lines" % len(ls))
            tris.append((tuple(ls), tuple(corners)))
    return tris, pts


# ---------------------------------------------------------------- method B
def method_B(lines):
    n = len(lines)
    P = {}
    for i, j in combinations(range(n), 2):
        P[(i, j)] = intersect(lines[i], lines[j])
    tris = []
    for i, j, k in combinations(range(n), 3):
        pij, pik, pjk = P[(i, j)], P[(i, k)], P[(j, k)]
        if pij is None or pik is None or pjk is None:
            continue
        if pij == pik:  # concurrent (then all three coincide)
            continue
        vs = (pij, pik, pjk)
        ok = True
        for m in range(n):
            if m in (i, j, k):
                continue
            a, b, c = lines[m]
            s = [a * v[0] + b * v[1] + c for v in vs]
            if any(x > 0 for x in s) and any(x < 0 for x in s):
                ok = False
                break
        if ok:
            tris.append(((i, j, k), vs))
    return tris


def analyse(lines):
    check_distinct(lines)
    ta, pts = method_A(lines)
    tb = method_B(lines)
    sa = {t[0] for t in ta}
    sb = {t[0] for t in tb}
    if len(sa) != len(ta):
        raise AssertionError("method A produced duplicate triangles")
    agree = sa == sb
    return ta, tb, sa, sb, agree, pts


def structure(lines, pts):
    n = len(lines)
    mult = {}
    multipoints = []
    for p, ls in sorted(pts.items()):
        if len(ls) >= 3:
            multipoints.append({"point": fstr(p), "lines": sorted(ls), "multiplicity": len(ls)})
    for m in multipoints:
        mult[m["multiplicity"]] = mult.get(m["multiplicity"], 0) + 1
    classes = {}
    for i, (a, b, c) in enumerate(lines):
        # normalise direction (a,b) up to scale
        from math import gcd
        g = gcd(abs(a), abs(b))
        da, db = a // g, b // g
        if da < 0 or (da == 0 and db < 0):
            da, db = -da, -db
        classes.setdefault((da, db), []).append(i)
    par = [v for v in classes.values() if len(v) >= 2]
    return {"n_lines": n, "multiple_points": multipoints,
            "multiplicity_profile": {str(k): v for k, v in sorted(mult.items())},
            "parallel_classes": par}


def main(argv):
    path = None
    out = None
    want_n = None
    it = iter(argv[1:])
    for a in it:
        if a == "--json":
            out = next(it)
        elif a == "--n":
            want_n = int(next(it))
        else:
            path = a
    if path is None:
        print(__doc__)
        return 2
    lines = load_lines(path)
    if want_n is not None and len(lines) != want_n:
        print("ERROR: expected %d lines, got %d" % (want_n, len(lines)))
        return 3
    ta, tb, sa, sb, agree, pts = analyse(lines)
    print("lines: %d" % len(lines))
    print("method A (planar face enumeration, 3 turning corners): %d" % len(sa))
    print("method B (triple test, no line cuts the open interior): %d" % len(sb))
    print("methods agree: %s" % ("YES" if agree else "NO"))
    if agree:
        print("TRIANGLES: %d" % len(sa))
    else:
        print("only in A: %s" % sorted(sa - sb))
        print("only in B: %s" % sorted(sb - sa))
    if out:
        cert = {"n_lines": len(lines), "count": len(sa), "methods_agree": agree,
                "count_A": len(sa), "count_B": len(sb),
                "triangles": [{"lines": list(t), "vertices": [fstr(v) for v in sorted(vs)]}
                              for t, vs in sorted(tb)],
                "structure": structure(lines, pts)}
        with open(out, "w") as f:
            json.dump(cert, f, indent=1)
    return 0 if agree else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

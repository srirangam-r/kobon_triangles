"""Per-graph cubes for the k=5, beta>0 residue (work/t3/k5_exceptions.jsonl, 28 graphs, refereed C37-C50) on the
k5L base (search/build_k5L.py). Every cube is a list of units on label-layer indicators:

  types      X/F: GE2, AX    V: GE2, -AX    O1 (O1a): GE1, -GE2, -TB    O1b: GE1, -GE2, TB
  bridges    BR(i,j) for the graph's edges, -BR(i,j) for the other pairs (the bridge graph is exact)
  faces      FC(i,j,k) for the listed all-multiple faces
  D-count    sum s <= Zmax = B + beta - 9  (-ZR[Zmax+1])
  exceptions a choice of `need` credit sites (need = #sites - slack, C50) and, per chosen site, one alternative:
               C43 face PQR (P, R the F vertices, Q the O1b vertex): E2(P,Q) | E2(R,Q) | E1(P,R,Q,s) for s off the face
               C50 point Q: MUT(Q) (C50 (i)) | CPE(Q) (C50 (ii))
A real 94 in the residue matches some graph under some labelling, has >= need sites with an exception, and
each exception implies one of the listed alternatives, so it satisfies some cube.

    python3 search/k5L_cubes.py work/k5L/k5L.ids.json work/t3/k5_exceptions.jsonl work/k5L/cubes.jsonl
"""
import json
import sys
from itertools import combinations, product

NBLK = {"X": 2, "F": 2, "V": 2, "O1": 1, "O1b": 1, "O0": 0}


def main():
    ids = json.load(open(sys.argv[1]))
    rows = [json.loads(l) for l in open(sys.argv[2])]
    out = open(sys.argv[3], "w")
    I = lambda name, *k: ids[name][",".join(map(str, k))]
    ncubes = 0
    for gi, r in enumerate(rows):
        t = r["types"]
        units = []
        for i, x in enumerate(t):
            if x in ("X", "F"):
                units += [I("GE2", i), I("AX", i)]
            elif x == "V":
                units += [I("GE2", i), -I("AX", i)]
            elif x in ("O1", "O1b"):
                units += [I("GE1", i), -I("GE2", i), I("TB", i) if x == "O1b" else -I("TB", i)]
            else:
                raise ValueError(x)
        edges = {tuple(sorted(e)) for e in r["bridges"]}
        for i, j in combinations(range(5), 2):
            units.append(I("BR", i, j) if (i, j) in edges else -I("BR", i, j))
        for f in r["faces"]:
            units.append(I("FC", *sorted(f)))
        B, beta = sum(NBLK[x] for x in t), len(edges)
        zmax = B + beta - 9
        assert 0 <= zmax <= 5, (gi, zmax)
        units.append(-I("ZR", zmax + 1))
        alts = []
        for s in r["sites"]:
            if s["kind"] == "C43":
                f = sorted(s["face"])
                Fs = [u for u in f if t[u] == "F"]
                Q = [u for u in f if t[u] != "F"]
                assert len(Fs) == 2 and len(Q) == 1 and t[Q[0]] == "O1b", (gi, f)
                (P, R), Q = Fs, Q[0]
                opts = [(f"E2_{P}{Q}", I("E2", P, Q)), (f"E2_{R}{Q}", I("E2", R, Q))]
                opts += [(f"E1_{P}{R}{Q}{u}", I("E1", P, R, Q, u)) for u in range(5) if u not in f]
            else:
                Q = s["point"]
                assert t[Q] in ("O1", "O1b"), (gi, Q)
                opts = [(f"MUT{Q}", I("MUT", Q)), (f"CPE{Q}", I("CPE", Q))]
            alts.append(opts)
        for chosen in combinations(range(len(alts)), r["need"]):
            for pick in product(*(alts[c] for c in chosen)):
                tag = f"g{gi:02d}_" + "_".join(p[0] for p in pick)
                out.write(json.dumps({"tag": tag, "graph": gi, "need": r["need"], "zmax": zmax,
                                      "units": units + [p[1] for p in pick], "clauses": [], "top": ids["top"]}) + "\n")
                ncubes += 1
    print(f"{ncubes} cubes for {len(rows)} graphs -> {sys.argv[3]}")


if __name__ == "__main__":
    main()

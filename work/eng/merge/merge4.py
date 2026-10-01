# Reverse-perturbation search for a 94 with a 4-fold point: in every near-optimal arrangement (T >= 92, multiplicity
# <= 3), try every merge of 4 lines whose 6 crossings form a contiguous local block (after commuting disjoint tokens)
# into one 4-fold point, recompute T exactly, report T >= 94.  By THEORY section 24, a 94 with a 6/7-type bad point
# is a merge of a mult<=3 93 (loss exactly 1), with an all-8 point a merge of a 92.
import sys, json
sys.path.insert(0, "/home/nail/stuff/sundai_math/work/t3")
from arr import Arr
from itertools import combinations

def parse(gens):
    out = []
    for t in gens.split():
        out.append((int(t.rstrip("*")), 2 + t.count("*")))
    return out

def merges(gens, n):
    toks = parse(gens); N = len(toks)
    perm = list(range(n)); states = []
    for g, m in toks:
        states.append(tuple(perm)); perm[g:g+m] = reversed(perm[g:g+m])
    seen = set()
    for i, (g, m) in enumerate(toks):
        for h in range(max(0, g + m - 4), min(g, n - 4) + 1):
            st = states[i]; wires = st[h:h+4]
            need = {frozenset(p) for p in combinations(wires, 2)}
            got = set(); coll = []; cur = list(st)
            ok = False
            for j in range(i, N):
                gj, mj = toks[j]
                lo, hi = gj, gj + mj - 1
                if hi < h or lo > h + 3:
                    if j > i: cur[lo:hi+1] = reversed(cur[lo:hi+1])
                    continue
                if lo < h or hi > h + 3:
                    break
                blk = cur[lo:hi+1]
                pairs = {frozenset(p) for p in combinations(blk, 2)}
                if not pairs <= need or pairs & got: break
                got |= pairs; coll.append(j); cur[lo:hi+1] = reversed(cur[lo:hi+1])
                if got == need: ok = True; break
            if not ok or len(coll) < 2: continue
            key = (h, tuple(coll))
            if key in seen: continue
            seen.add(key)
            cs = set(coll)
            new = []
            for j, (gj, mj) in enumerate(toks):
                if j == coll[0]: new.append(f"{h}**")
                elif j in cs: continue
                else: new.append(str(gj) + "*" * (mj - 2))
            yield " ".join(new)

if __name__ == "__main__":
    files = sys.argv[3:]; mod, part = int(sys.argv[1]), int(sys.argv[2])
    best = {}; cnt = 0; tried = 0; found = []
    seen_g = set()
    idx = -1
    for f in files:
        for line in open(f):
            d = json.loads(line); n = d.get("n", 18)
            if n != 18: continue
            g = d.get("gens")
            if not g: continue
            if g in seen_g: continue
            seen_g.add(g); idx += 1
            if idx % mod != part: continue
            try:
                a = Arr(g, 18); T0 = a.T()
            except Exception:
                continue
            if T0 < 92: continue
            cnt += 1
            for ng in merges(g, 18):
                tried += 1
                try:
                    T1 = Arr(ng, 18).T()
                except Exception:
                    continue
                best[T1 - T0] = best.get(T1 - T0, 0) + 1
                if T1 >= 94:
                    found.append({"gens": ng, "T": T1, "from_T": T0})
                    print("FOUND", T1, ng, flush=True)
    print(f"part {part}: arrangements {cnt}, merges tried {tried}, dT histogram {sorted(best.items())}, found {len(found)}", flush=True)
    with open(f"found_{part}.jsonl", "w") as fh:
        for x in found: fh.write(json.dumps(x) + "\n")

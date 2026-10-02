"""class-constrained path SAT of one DP path (see classsat.py).  usage: class_path.py '<json task>'   task = {"i":.., "s": notation, "outdir": dir, "tag": str}
prints one json line: cls in SAT | UNSAT | EXACT_ONLY | RESTRICT_SAT | (TIMEOUT is set by the caller when the process is killed)
  SAT        positive pattern AND the exact whole line are realisable in the class: "gens" = a clean arrangement (a real exact row)
  UNSAT      positive pattern unrealisable in the class (n = 18): minimal core, "preds" (frame predicates, cegar_m format), CNF of the verifying instance saved
  EXACT_ONLY positive part realisable, exact whole line not: "word" (anchored pattern)"""
import sys, json, time, itertools, os
ROOT = "/home/nail/stuff/sundai_math"
sys.path.insert(0, ROOT + "/search"); sys.path.insert(0, ROOT + "/work/eng/T29"); sys.path.append(ROOT + "/work/t3"); sys.path.append(ROOT + "/work/eng/T27"); sys.path.insert(0, ROOT + "/work/eng/T23")
import sat_path as SP, patsat_m as P, classsat as C, cegar_m
import realize_chi as rc
from pysat.solvers import Solver
K = 18


def cbuild(pat, elements=None):
    B, sel = P.build(pat, K, elements)
    C.add_class(B)
    if os.environ.get("TRIOPT"):
        # sol's triple optimality (ALL8_NOTE2 section 10): both alternating sector sums of every triple point are >= 2
        for t in B.trip:
            ring = C.triple_ring(B, t); z = B.z[t]
            for par in (0, 1):
                e = [ring[par], ring[par + 2], ring[par + 4]]
                for i in range(3):
                    for j in range(i + 1, 3):
                        B.cl.append([-z, e[i], e[j]])
    return B, sel


def decide(pat, elements=None):
    B, sel = cbuild(pat, elements)
    el = pat.elements() if elements is None else elements
    sv = Solver(name="cadical153", bootstrap_with=B.cl)
    ok, Ms = C.lazy_solve(sv, B, [sel[e] for e in el])
    return ok, Ms, B, sel, sv, el


def dump_cnf(B, assumptions, path):
    with open(path, "w") as fo:
        fo.write(f"p cnf {B.nv} {len(B.cl) + len(assumptions)}\n")
        for c in B.cl:
            fo.write(" ".join(map(str, c)) + " 0\n")
        for a in assumptions:
            fo.write(f"{a} 0\n")


def main():
    task = json.loads(sys.argv[1])
    t0 = time.time()
    fr = SP.parse(task["s"])
    if task.get("hids") is not None:
        res = dict(i=task["i"], s=task["s"], hids=task["hids"])
        # A. POSITIVE instance: frame bits / apex flags / hidden sectors + the DP's sig + the POSITIVE flank features (far / unb).  UNSAT => a sound forbidden pattern with labels.
        patP = P.pattern_from_frames(fr, task["hids"])
        for (ek, es, er) in task.get("extras", []):
            patP.extra.append((ek, es, er))
        okP, MsP, BP, selP, svP, elP = decide(patP)
        if not okP:
            cs = set(svP.get_core()); core = [e for e in elP if selP[e] in cs]
            j = 0
            while j < len(core):
                trial = core[:j] + core[j + 1:]
                ok2, _ = C.lazy_solve(svP, BP, [selP[e] for e in trial])
                if ok2:
                    j += 1
                else:
                    cs = set(svP.get_core()); core = [e for e in trial if selP[e] in cs]; j = min(j, len(core))
            # a sig element is encoded through the adjacent triangle of the ORIGINAL pattern (segment triangle, else the hidden sector): keep that triangle in the pattern
            core = list(core)
            _P = patP
            for e in list(core):
                if e[0] != "sig":
                    continue
                s_, ray = e[1], e[2]
                sgd = 0 if ray in ("E+", "W+") else 1
                segi = s_ if ray[0] == "E" else s_ - 1
                if segi in _P.seg and _P.seg[segi][sgd]:
                    if ("tri", segi, sgd) not in core: core.append(("tri", segi, sgd))
                elif _P.slots[s_][1][sgd]:
                    if ("hid", s_, sgd) not in core: core.append(("hid", s_, sgd))
            touched = set()
            for e in core:
                if e[0] in ("tri", "apex"): touched |= {e[1], e[1] + 1}
                elif e[0] in ("far", "unb"): touched |= ({e[1], e[1] + 1} if e[2][0] == "E" else {e[1] - 1, e[1]})
                else: touched.add(e[1])
            lo, hi = max(min(touched), 0), min(max(touched), len(patP.slots) - 1)
            def restricted(lo, hi):
                hs_ = {}
                for e in core:
                    if e[0] in ("hid", "hidm"): hs_.setdefault(e[1], [0, 0, 0, 0])[e[2]] = 1
                slots = []
                for s_ in range(lo, hi + 1):
                    k = patP.slots[s_][0]; h = hs_.get(s_, [0, 0, 0, 0])
                    slots.append((k, tuple(h[:2]) if k == "T" else tuple(h) if k == "M" else (0, 0)))
                seg, apex, sig, extra = {}, {}, {}, []
                for e in core:
                    if e[0] == "tri": seg.setdefault(e[1] - lo, [0, 0])[e[2]] = 1
                    elif e[0] == "apex": apex[(e[1] - lo, e[2])] = e[3]; seg.setdefault(e[1] - lo, [0, 0])[e[2]] = 1
                    elif e[0] == "sig": sig[(e[1] - lo, e[2])] = e[3]
                    elif e[0] in ("far", "unb"): extra.append((e[0], e[1] - lo, e[2]))
                rp = P.Pattern(slots, {s_: tuple(b) for s_, b in seg.items()}, apex, sig, "")
                rp.extra = extra
                return rp
            rp = restricted(lo, hi)
            ok3, _, _, _, _, _ = decide(rp)
            if ok3:
                lo, hi = 0, len(patP.slots) - 1
                rp = restricted(lo, hi)
                ok3, _, _, _, _, _ = decide(rp)
            if ok3:
                res.update(cls="RESTRICT_SAT", secs=round(time.time() - t0, 1), core=[list(e) for e in core]); print(json.dumps(res)); return
            preds = cegar_m.preds_of(rp)
            labs = [[e[1] - lo, e[2], e[0]] for e in core if e[0] in ("far", "unb")]
            sigs = [[e[1] - lo, e[2], e[3]] for e in core if e[0] == "sig"]
            res.update(cls="UNSAT_POS", secs=round(time.time() - t0, 1), core=[list(e) for e in core], preds=preds, labs=labs, sigs=sigs, lo=lo, hi=hi)
            print(json.dumps(res)); return
        # B. positive instance realisable: the EXACT witness with SOFT negative features (absent triangles / hidden sectors / far / unb, ub flags): UNSAT => core over positive + negative elements
        patS = P.pattern_exact(fr, task["hids"])
        for (ek, es, er) in task.get("extras", []):
            patS.extra.append((ek, es, er))
        for (ek, es, er) in task.get("negextras", []):
            patS.neg.append((ek, es, er))
        patS.softneg = True
        BS, selS = cbuild(patS)
        softk = [k for k in selS if k[0] in ("nt", "nh", "nhm", "nfar", "nunb", "ub")]
        elS = patS.elements()
        svS = Solver(name="cadical153", bootstrap_with=BS.cl)
        allk = elS + softk
        okW, MsW = C.lazy_solve(svS, BS, [selS[e] for e in allk])
        if okW:
            chi = C.chi_of(BS, MsW); word = rc.realize(K, chi)
            res.update(cls="WIT_SAT", gens=None if word is None else (word if isinstance(word, str) else " ".join(map(str, word))), secs=round(time.time() - t0, 1))
            print(json.dumps(res)); return
        cs = set(svS.get_core()); core = [e for e in allk if selS[e] in cs]
        deadline = t0 + float(task.get("limit", 900)) * 0.8
        j = 0
        while j < len(core) and time.time() < deadline:
            trial = core[:j] + core[j + 1:]
            ok2, _ = C.lazy_solve(svS, BS, [selS[e] for e in trial], deadline=deadline)
            if ok2 is None:
                break                      # timeout: keep the current (valid) core
            if ok2:
                j += 1
            else:
                cs = set(svS.get_core()); core = [e for e in trial if selS[e] in cs]; j = min(j, len(core))
        # a sig element is encoded through the adjacent triangle of the ORIGINAL pattern: keep that triangle in the pattern
        core = list(core)
        _P = patS
        for e in list(core):
            if e[0] != "sig":
                continue
            s_, ray = e[1], e[2]
            sgd = 0 if ray in ("E+", "W+") else 1
            segi = s_ if ray[0] == "E" else s_ - 1
            if segi in _P.seg and _P.seg[segi][sgd]:
                if ("tri", segi, sgd) not in core: core.append(("tri", segi, sgd))
            elif _P.slots[s_][1][sgd]:
                if ("hid", s_, sgd) not in core: core.append(("hid", s_, sgd))
        touched = set()
        for e in core:
            if e[0] in ("tri", "apex", "nt"): touched |= {e[1], e[1] + 1}
            elif e[0] in ("far", "unb", "nfar", "nunb"): touched |= ({e[1], e[1] + 1} if e[2][0] == "E" else {e[1] - 1, e[1]})
            else: touched.add(e[1])
        lo, hi = max(min(touched), 0), min(max(touched), len(fr) - 1)
        def restrictedS(lo, hi):
            hs_ = {}
            for e in core:
                if e[0] in ("hid", "hidm"): hs_.setdefault(e[1], [0, 0, 0, 0])[e[2]] = 1
            slots = []
            for s_ in range(lo, hi + 1):
                k = patS.slots[s_][0]; h = hs_.get(s_, [0, 0, 0, 0])
                slots.append((k, tuple(h[:2]) if k == "T" else tuple(h) if k == "M" else (0, 0)))
            seg, apex, sig, extra, neg, ub = {}, {}, {}, [], [], {}
            for e in core:
                if e[0] == "tri": seg.setdefault(e[1] - lo, [0, 0])[e[2]] = 1
                elif e[0] == "apex": apex[(e[1] - lo, e[2])] = e[3]; seg.setdefault(e[1] - lo, [0, 0])[e[2]] = 1
                elif e[0] == "sig": sig[(e[1] - lo, e[2])] = e[3]
                elif e[0] in ("far", "unb"): extra.append((e[0], e[1] - lo, e[2]))
                elif e[0] == "nt": neg.append(("tri", e[1] - lo, e[2])); seg.setdefault(e[1] - lo, [0, 0])
                elif e[0] == "nh": neg.append(("hid", e[1] - lo, e[2]))
                elif e[0] == "nhm": neg.append(("hidm", e[1] - lo, e[2]))
                elif e[0] == "nfar": neg.append(("far", e[1] - lo, e[2]))
                elif e[0] == "nunb": neg.append(("unb", e[1] - lo, e[2]))
                elif e[0] == "ub": ub[(e[1] - lo, e[2])] = 1
            rp = P.Pattern(slots, {s_: tuple(b) for s_, b in seg.items()}, apex, sig, "", neg, ub)
            rp.extra = extra
            return rp
        rp = restrictedS(lo, hi)
        ok3, _, _, _, _, _ = decide(rp)
        if ok3:
            lo, hi = 0, len(fr) - 1
            rp = restrictedS(lo, hi)
            ok3, _, _, _, _, _ = decide(rp)
        if ok3:
            res.update(cls="RESTRICT_SAT", secs=round(time.time() - t0, 1), core=[list(e) for e in core]); print(json.dumps(res)); return
        preds = cegar_m.preds_of(rp)
        labs = [[e[1] - lo, e[2], e[0]] for e in core if e[0] in ("far", "unb", "nfar", "nunb")]
        sigs = [[e[1] - lo, e[2], e[3]] for e in core if e[0] == "sig"]
        zeros = ([[e[1] - lo, "bout", e[2]] for e in core if e[0] == "nt"] + [[e[1] - lo, "h", e[2]] for e in core if e[0] in ("nh", "nhm")]
                 + [[e[1] - lo, "ub", e[2]] for e in core if e[0] == "ub"])
        units = sum(1 if k == "S" else 2 if k == "T" else 3 for k, h in rp.slots)
        anchored = bool(lo == 0 and hi == len(fr) - 1 and units == K - 1)       # all K-1 other lines cross L inside the window: the window is the whole line
        res.update(cls="UNSAT_EXACT", secs=round(time.time() - t0, 1), core=[list(e) for e in core], preds=preds, labs=labs, sigs=sigs, zeros=zeros, lo=lo, hi=hi, anchored=anchored, units=units)
        print(json.dumps(res)); return

    pat = P.pattern_from_frames(fr, None)
    els = pat.elements()
    ok, Ms, B, sel, sv, el = decide(pat)
    res = dict(i=task["i"], s=task["s"])
    if ok:
        patE = P.pattern_exact(fr, None)
        okE, MsE, BE, selE, svE, elE = decide(patE)
        if okE:
            chi = C.chi_of(BE, MsE)
            word = rc.realize(K, chi)
            g = None if word is None else (word if isinstance(word, str) else " ".join(map(str, word)))
            res.update(cls="SAT", gens=g, secs=round(time.time() - t0, 1))
            more = []
            ns = int(task.get("nsol", 1))
            deadline = t0 + float(task.get("limit", 600)) * 0.8
            while len(more) < ns - 1 and time.time() < deadline:
                svE.add_clause([-(BE.z[t] if chi[t] == 0 else BE.pz[t] if chi[t] == 1 else BE.ng[t]) for t in BE.trip])
                ok2, Ms2 = C.lazy_solve(svE, BE, [selE[e] for e in elE], deadline=deadline)
                if not ok2:
                    break
                chi = C.chi_of(BE, Ms2)
                w2 = rc.realize(K, chi)
                if w2 is not None:
                    more.append(w2 if isinstance(w2, str) else " ".join(map(str, w2)))
            res["more_gens"] = more
        else:
            res.update(cls="EXACT_ONLY", secs=round(time.time() - t0, 1), word=[[f.kind, list(f.bin), list(f.bout), list(f.ub), list(f.h), list(f.ain), list(f.aout)] for f in fr])
        print(json.dumps(res)); return
    cs = set(sv.get_core())
    core = [e for e in els if sel[e] in cs]
    j = 0
    while j < len(core):
        trial = core[:j] + core[j + 1:]
        ok2, _ = C.lazy_solve(sv, B, [sel[e] for e in trial])
        if ok2:
            j += 1
        else:
            cs = set(sv.get_core())
            core = [e for e in trial if sel[e] in cs]
            j = min(j, len(core))
    rp, lo, hi = cegar_m.restrict_m(pat, core)
    ok3, Ms3, B3, sel3, sv3, el3 = decide(rp)
    if ok3:
        rp, lo, hi = cegar_m.restrict_m(pat, core, full=True)
        ok3, Ms3, B3, sel3, sv3, el3 = decide(rp)
        if ok3:
            res.update(cls="RESTRICT_SAT", secs=round(time.time() - t0, 1), core=[list(e) for e in core]); print(json.dumps(res)); return
    preds = cegar_m.preds_of(rp)
    cnf = None
    if task.get("outdir"):
        os.makedirs(task["outdir"], exist_ok=True)
        cnf = os.path.join(task["outdir"], f"{task.get('tag','p')}_{task['i']}.cnf")
        dump_cnf(B3, [sel3[e] for e in el3], cnf)
    res.update(cls="UNSAT", secs=round(time.time() - t0, 1), core=[list(e) for e in core], preds=preds, lo=lo, hi=hi, cnf=cnf, lemma_clauses=len(B3.cl))
    print(json.dumps(res))


if __name__ == "__main__":
    main()

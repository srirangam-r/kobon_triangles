"""DRAT-certify a set of cubes: for each, write base + units + clauses, solve with Kissat writing a text DRAT
proof, check it with drat-trim, delete both files. Resumes from the log; SAT writes a model file.

Cube jsonl rows: {"tag" | "u"+"S", "units": [...], "clauses": [[...]], "top": N} (clauses/top optional).
New variables in the rows must start above the base CNF's declared nv: the generators read it from the base
header (see work/loop/verdicts/AUDIT_k6z.md for the collision this prevents).

    python3 search/drat_cubes.py <cubes.jsonl> <base.cnf> <log.jsonl> [--workers 12] [--solve-timeout 900]
"""
import argparse
import json
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KISSAT, DRAT = ROOT / "tools/kissat/build/kissat", ROOT / "tools/drat-trim/drat-trim"
_g = {}


def tag(c):
    return c.get("tag") or "u%d_%s" % (c["u"], "_".join(map(str, c["S"])))


def init(base, work):
    head, body = Path(base).read_text().split("\n", 1)
    _g.update(nv=int(head.split()[2]), nc=int(head.split()[3]), body=body, work=Path(work))


def run(args):
    c, solve_timeout = args
    t_ = tag(c)
    units, clauses = c.get("units", []), c.get("clauses", [])
    top = max(_g["nv"], c.get("top", 0), max((abs(x) for cl in clauses for x in cl), default=0))
    cnf, prf = _g["work"] / f"{t_}.cnf", _g["work"] / f"{t_}.drat"
    extra = "".join(f"{l} 0\n" for l in units) + "".join(" ".join(map(str, cl)) + " 0\n" for cl in clauses)
    cnf.write_text(f"p cnf {top} {_g['nc'] + len(units) + len(clauses)}\n" + _g["body"] + extra)
    t = time.time()
    r = subprocess.run(["timeout", str(solve_timeout), str(KISSAT), "-q", "--no-binary", str(cnf), str(prf)], capture_output=True, text=True)
    res = {"tag": t_, "solve": {10: "SAT", 20: "UNSAT"}.get(r.returncode, "timeout"), "solve_s": round(time.time() - t, 1)}
    if r.returncode == 20:
        t = time.time()
        d = subprocess.run(["timeout", "3600", str(DRAT), str(cnf), str(prf), "-t", "3600"], capture_output=True, text=True)
        res.update(drat="VERIFIED" if "s VERIFIED" in d.stdout else "FAILED", check_s=round(time.time() - t, 1),
                   core=next((l for l in d.stdout.splitlines() if "clauses in core" in l), "").strip())
    elif r.returncode == 10:
        (_g["work"] / f"SAT_{t_}.model").write_text(r.stdout)
    cnf.unlink(missing_ok=True)
    prf.unlink(missing_ok=True)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cubes"); ap.add_argument("base"); ap.add_argument("log")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--solve-timeout", type=int, default=900)
    a = ap.parse_args()
    work = Path(a.log).with_suffix(".tmp")
    work.mkdir(exist_ok=True)
    cubes = [json.loads(l) for l in open(a.cubes)]
    done = {json.loads(l)["tag"] for l in open(a.log)} if Path(a.log).exists() else set()
    todo = [c for c in cubes if tag(c) not in done]
    print(f"{len(done)} done, {len(todo)} to do", flush=True)
    with ProcessPoolExecutor(a.workers, initializer=init, initargs=(a.base, str(work))) as ex, open(a.log, "a") as log:
        for f in as_completed([ex.submit(run, (c, a.solve_timeout)) for c in todo]):
            print(json.dumps(f.result()), file=log, flush=True)
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()

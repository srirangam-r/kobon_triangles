"""Cube-and-conquer with checkable proofs.

1. march_cu splits formula.cnf into cubes (partial assignments).
2. Each cube is solved as formula + unit clauses by CaDiCaL, writing a DRAT proof,
   and every UNSAT answer is checked with drat-trim.
3. Coverage: formula + the negation of every cube must be UNSAT too (the cubes cover
   everything march_cu did not already refute); that is also solved with a DRAT proof
   and checked.
If all cube proofs and the coverage proof verify, the formula is UNSAT, checkably.
A SAT cube stops everything and reports the model.

    python3 search/cnc.py <formula.cnf> <workdir> [--depth D | --cubes N] [--workers W] [--timeout S]
"""
import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"
CADICAL = TOOLS / "cadical" / "build" / "cadical"
DRAT = TOOLS / "drat-trim" / "drat-trim"
MARCH = TOOLS / "CnC" / "march_cu" / "march_cu"


def read_cnf(path):
    header, clauses = None, []
    for line in Path(path).read_text().splitlines():
        if line.startswith("p cnf"):
            header = line
        elif line and not line.startswith("c"):
            clauses.append(line)
    nv = int(header.split()[2])
    return nv, clauses


def write_cnf(path, nv, clauses, extra):
    with open(path, "w") as f:
        f.write(f"p cnf {nv} {len(clauses) + len(extra)}\n")
        f.write("\n".join(clauses) + "\n")
        for c in extra:
            f.write(" ".join(map(str, c)) + " 0\n")


def solve_and_check(args):
    tag, cnf_path, proof_path, timeout = args
    t0 = time.time()
    try:
        out = subprocess.run([str(CADICAL), "-q", "--no-binary", "-t", str(timeout), str(cnf_path), str(proof_path)],
                             capture_output=True, text=True)
    except Exception as e:  # noqa: BLE001
        return tag, "error", str(e), time.time() - t0, None
    solve_s = time.time() - t0
    if out.returncode == 10:
        model = [int(x) for line in out.stdout.splitlines() if line.startswith("v") for x in line.split()[1:] if x != "0"]
        return tag, "SAT", solve_s, None, model
    if out.returncode != 20:
        return tag, "unknown", solve_s, None, None
    t1 = time.time()
    chk = subprocess.run([str(DRAT), str(cnf_path), str(proof_path), "-t", str(max(20000, int(timeout) * 4))],
                         capture_output=True, text=True)
    verified = "s VERIFIED" in chk.stdout
    os.remove(proof_path)  # proofs are large; keep only the verdict (re-run to regenerate)
    return tag, "UNSAT-verified" if verified else "UNSAT-unverified", solve_s, time.time() - t1, None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cnf")
    parser.add_argument("workdir")
    parser.add_argument("--depth", type=int, default=0)
    parser.add_argument("--cubes", type=int, default=0, help="stop cubing at this many cubes (march -l)")
    parser.add_argument("--workers", type=int, default=22)
    parser.add_argument("--timeout", type=int, default=3600)
    args = parser.parse_args()
    work = Path(args.workdir)
    work.mkdir(parents=True, exist_ok=True)
    icnf = work / "cubes.icnf"
    cmd = [str(MARCH), args.cnf, "-o", str(icnf)]
    if args.depth:
        cmd += ["-d", str(args.depth)]
    if args.cubes:
        cmd += ["-l", str(args.cubes)]
    t0 = time.time()
    march = subprocess.run(cmd, capture_output=True, text=True)
    cubes = [[int(x) for x in line.split()[1:-1]] for line in icnf.read_text().splitlines() if line.startswith("a ")] \
        if icnf.exists() else []
    print(f"march_cu: {len(cubes)} cubes in {time.time() - t0:.1f}s", flush=True)
    if "UNSATISFIABLE" in march.stdout and not cubes:
        print("march_cu refuted the formula outright (re-check with cadical for a proof)")
    nv, clauses = read_cnf(args.cnf)
    jobs = []
    for idx, cube in enumerate(cubes):
        path = work / f"cube{idx:05d}.cnf"
        write_cnf(path, nv, clauses, [[l] for l in cube])
        jobs.append((f"cube{idx:05d}", path, work / f"cube{idx:05d}.drat", args.timeout))
    cover = work / "coverage.cnf"
    write_cnf(cover, nv, clauses, [[-l for l in cube] for cube in cubes])
    jobs.append(("coverage", cover, work / "coverage.drat", args.timeout))
    results = {}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(solve_and_check, j) for j in jobs]
        for fut in as_completed(futures):
            tag, verdict, solve_s, check_s, model = fut.result()
            results[tag] = {"verdict": verdict, "solve_s": round(solve_s, 1) if isinstance(solve_s, float) else solve_s,
                            "check_s": round(check_s, 1) if check_s else None}
            done = len(results)
            if verdict == "SAT":
                (work / f"{tag}.model").write_text(" ".join(map(str, model)) + "\n")
                print(f"{tag}: SAT after {solve_s:.1f}s -- model saved; stopping", flush=True)
                for f in futures:
                    f.cancel()
                break
            if done % 10 == 0 or verdict != "UNSAT-verified":
                print(f"[{done}/{len(jobs)}] {tag}: {verdict} solve {results[tag]['solve_s']}s check {results[tag]['check_s']}s", flush=True)
    (work / "results.json").write_text(json.dumps(results, indent=1) + "\n")
    verdicts = [r["verdict"] for r in results.values()]
    summary = {v: verdicts.count(v) for v in set(verdicts)}
    all_ok = len(results) == len(jobs) and set(verdicts) == {"UNSAT-verified"}
    print("summary:", summary, "| formula UNSAT with every proof verified:" if all_ok else "| NOT fully verified", flush=True)


if __name__ == "__main__":
    main()

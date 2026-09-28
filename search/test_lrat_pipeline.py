#!/usr/bin/env python3
"""Integration tests of proof plumbing, not geometric scoring or a parameter search."""
import argparse
import json
from pathlib import Path
import sys
import tempfile

from kobon_sat import build
import lrat_pipeline as lp

ROOT = Path(__file__).resolve().parent.parent


def require(value, message):
    if not value:
        raise AssertionError(message)


def run_case(out, name, n, target, cube_kind, binary=False, expected="VERIFIED_UNSAT"):
    directory = out / name
    directory.mkdir(parents=True, exist_ok=True)
    cnf, chi, _ = build(n, target)
    base = directory / "base.cnf"
    cnf.to_file(str(base))
    cube = {"tag": name, "units": [], "clauses": [], "top": cnf.nv}
    if cube_kind == "units":
        # Fresh variable occurring ONLY in units must still be in the CNF header.
        cube.update(units=[cnf.nv + 1], top=cnf.nv + 1)
    elif cube_kind == "clauses":
        fresh = cnf.nv + 1
        # Extension equivalent to an existing sign literal, with no extra restriction.
        old = next(iter(chi.values()))
        cube = {"u": 2, "S": [1, 3], "units": [], "clauses": [[-fresh, old], [fresh, -old]], "top": fresh}
    cubes, log = directory / "cubes.jsonl", directory / "results.jsonl"
    cubes.write_text(json.dumps(cube) + "\n")
    args = [str(cubes), str(base), str(log), "--solve-timeout", "30", "--convert-timeout", "30",
            "--check-timeout", "30", "--heap-mb", "256", "--stack-mb", "64"]
    if binary:
        args.append("--binary-drat")
    require(lp.main(args) == 0, f"{name}: pipeline failed")
    rows = [json.loads(line) for line in log.read_text().splitlines()]
    result = next(r for r in reversed(rows) if r["cube"] == cube
                  and r["pipeline_sha256"] == lp.digest(lp.__file__)
                  and r["options"]["binary_drat"] == binary)
    require(result["status"] == expected, f"{name}: {result['status']}, expected {expected}")
    count = len(log.read_text().splitlines())
    require(lp.main(args) == 0, f"{name}: resume failed")
    require(len(log.read_text().splitlines()) == count, "resume reran a completed fingerprint")
    require(not list(directory.glob("lrat-*-*")), "temporary proof files were not deleted")
    if expected == "SAT":
        require(Path(result["model"]).exists(), "SAT model was not retained")
        require("s SATISFIABLE" in Path(result["model"]).read_text(), "SAT model output missing")
    return {"name": name, "n": n, "target": target, "variables": cnf.nv, "clauses": len(cnf.clauses),
            "status": result["status"], "key": result["key"], "binary_drat": binary,
            "stages": {k: {x: v[x] for x in ("returncode", "seconds")} for k, v in result["stages"].items()},
            "proof_bytes": {k: result[k] for k in ("drat_bytes", "lrat_bytes") if k in result}}


def negative_tests(out):
    checks = []
    with tempfile.TemporaryDirectory(dir=out, prefix="negative-") as tmp:
        d = Path(tmp)
        body = d / "body"
        # Comments and multiple clauses per line are accepted; order is preserved.
        good = d / "good.cnf"
        good.write_text("c before header\np cnf 2 2\nc middle\n1\n2 0 -1 0\n")
        require(lp.normalize_base(good, body) == (2, 2), "DIMACS multiline parse failed")
        require(body.read_text() == "1 2 0\n-1 0\n", "clause ordering changed")
        checks.append("DIMACS comments and multiline clauses")
        for text in ("p cnf 1 2\n1 0\n", "p cnf 1 1\n2 0\n", "p cnf 1 1\n1\n",
                     "1 0\np cnf 1 1\n", "p cnf 1 0\np cnf 1 0\n"):
            bad = d / "bad.cnf"
            bad.write_text(text)
            try:
                lp.normalize_base(bad, body)
            except ValueError:
                pass
            else:
                raise AssertionError("malformed DIMACS accepted")
        checks.append("five malformed DIMACS inputs rejected")
        for cube in ({"units": [0]}, {"units": [True]}, {"units": [1.5]},
                     {"units": [3], "top": 2}, {"clauses": [[4]], "top": 3}, {"top": False}):
            try:
                lp.validate_cube(cube, 2)
            except ValueError:
                pass
            else:
                raise AssertionError("invalid cube accepted")
        require(lp.validate_cube({"units": [7]}, 2)[2] == 7, "unit-only top inference failed")
        checks.append("six malformed cubes rejected; fresh unit variable included")
        timeout = lp.stage([sys.executable, "-c", "import time; time.sleep(10)"], 0.05, d, "timeout")
        require(timeout["timeout"], "timeout not detected")
        checks.append("process timeout is not proof success")
        require(not lp.accepted({"timeout": False, "returncode": 1, "stdout_tail": "s VERIFIED UNSAT\n"}, "s VERIFIED UNSAT"), "nonzero checker exit accepted")
        require(not lp.accepted({"timeout": False, "returncode": 0, "stdout_tail": "not verified\n"}, "s VERIFIED UNSAT"), "missing success marker accepted")
        checks.append("both checker exit code and exact success marker required")
        # Check a fabricated empty-clause proof against a satisfiable formula.
        sat = d / "sat.cnf"
        sat.write_text("p cnf 1 1\n1 0\n")
        invalid = d / "invalid.lrat"
        for proof in ("", "2 0 1 0\n"):
            invalid.write_text(proof)
            r = lp.stage([ROOT / "tools/cake_lpr/cake_lpr", "--CML_HEAP_SIZE=128", "--CML_STACK_SIZE=64", sat, invalid], 10, d, "reject")
            require(not lp.accepted(r, "s VERIFIED UNSAT"), "cake_lpr accepted an invalid proof")
            require(not r["timeout"] and r["returncode"] is not None, "checker did not execute")
        checks.append("cake_lpr rejects empty and fabricated proofs of a satisfiable CNF")
    return checks


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    a.output = a.output.resolve()
    a.output.mkdir(parents=True, exist_ok=True)
    summary = {"scope": "proof-pipeline validation only; not a proof of encoding soundness or an official geometry score"}
    summary["negative_tests"] = negative_tests(a.output)
    summary["cases"] = [
        run_case(a.output, "four-lines-three-triangles", 4, 3, "none"),
        run_case(a.output, "five-lines-six-triangles", 5, 6, "units"),
        run_case(a.output, "six-lines-eight-triangles", 6, 8, "clauses", binary=True),
        run_case(a.output, "sat-model-control", 3, 1, "none", expected="SAT"),
    ]
    # A changed cube using the same human-readable tag must not reuse a prior proof.
    d = a.output / "sat-model-control"
    (d / "cubes.jsonl").write_text(json.dumps({"tag": "sat-model-control", "clauses": [[]]}) + "\n")
    args = [str(d / "cubes.jsonl"), str(d / "base.cnf"), str(d / "results.jsonl"),
            "--solve-timeout", "30", "--convert-timeout", "30", "--check-timeout", "30", "--heap-mb", "256", "--stack-mb", "64"]
    require(lp.main(args) == 0, "changed cube failed")
    rows = [json.loads(s) for s in (d / "results.jsonl").read_text().splitlines()]
    require(rows[-1]["status"] == "VERIFIED_UNSAT", "stale SAT result reused after cube changed")
    require(rows[-1]["key"] != summary["cases"][-1]["key"], "changed cube has same fingerprint")
    summary["negative_tests"].append("same-tag changed cube rechecked rather than resumed")
    summary["tool_builds"] = json.loads((ROOT / "tools/proof_tools.build.json").read_text())
    summary["passed"] = True
    (a.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Certify base CNF + JSONL cubes via Kissat -> drat-trim LRAT -> cake_lpr.

Only VERIFIED_UNSAT means cake_lpr accepted a proof of the assembled CNF.
This does not prove the geometric encoding or coverage of the cube family.
The pipeline itself uses only Python's standard library.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = 1


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def literal(x):
    if type(x) is not int or x == 0:
        raise ValueError(f"invalid cube literal: {x!r}")
    return x


def validate_cube(cube, nv):
    if not isinstance(cube, dict):
        raise ValueError("cube must be an object")
    units, clauses = cube.get("units", []), cube.get("clauses", [])
    if not isinstance(units, list) or not isinstance(clauses, list):
        raise ValueError("units and clauses must be lists")
    for x in units:
        literal(x)
    for clause in clauses:
        if not isinstance(clause, list):
            raise ValueError("each clause must be a list")
        for x in clause:
            literal(x)
    used = max([nv] + [abs(x) for x in units] + [abs(x) for c in clauses for x in c])
    top = cube.get("top", used)
    if type(top) is not int or top < used:
        raise ValueError("cube top must cover the base and every added literal")
    return units, clauses, top


def normalize_base(source, body):
    """Validate DIMACS and stream normalized clauses, preserving clause order."""
    header = None
    count = 0
    pending = []
    with open(source) as inp, open(body, "w") as out:
        for line in inp:
            s = line.strip()
            if not s or s.startswith("c"):
                continue
            if s.startswith("p"):
                fields = s.split()
                if header is not None or len(fields) != 4 or fields[:2] != ["p", "cnf"]:
                    raise ValueError("invalid or repeated DIMACS header")
                header = tuple(map(int, fields[2:]))
                if min(header) < 0:
                    raise ValueError("negative DIMACS header")
                continue
            if header is None:
                raise ValueError("clause before DIMACS header")
            for text in s.split():
                x = int(text)
                if abs(x) > header[0]:
                    raise ValueError("literal exceeds base variable count")
                if x:
                    pending.append(x)
                else:
                    out.write(" ".join(map(str, pending)) + (" " if pending else "") + "0\n")
                    pending.clear()
                    count += 1
        if header is None or pending or count != header[1]:
            raise ValueError("missing header, unterminated clause, or incorrect clause count")
    return header


def assemble(body, header, cube, target):
    units, clauses, top = validate_cube(cube, header[0])
    nc = header[1] + len(units) + len(clauses)
    empty = None
    with open(target, "w") as out, open(body) as inp:
        out.write(f"p cnf {top} {nc}\n")
        for index, line in enumerate(inp, 1):
            out.write(line)
            if line.strip() == "0" and empty is None:
                empty = index
        for index, clause in enumerate([[x] for x in units] + clauses, header[1] + 1):
            out.write(" ".join(map(str, clause)) + (" " if clause else "") + "0\n")
            if not clause and empty is None:
                empty = index
    return nc, empty


def tail(path, limit=3000):
    with open(path, "rb") as f:
        f.seek(0, 2)
        f.seek(max(0, f.tell() - limit))
        return f.read().decode("utf-8", errors="replace")


def stage(command, timeout, folder, name):
    """Bound the whole process group; never buffer a large solver model in RAM."""
    stdout, stderr = folder / (name + ".out"), folder / (name + ".err")
    start = time.monotonic()
    info = {"command": list(map(str, command)), "timeout": False}
    with stdout.open("wb") as out, stderr.open("wb") as err:
        try:
            p = subprocess.Popen(info["command"], stdout=out, stderr=err, start_new_session=True)
            try:
                info["returncode"] = p.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid, signal.SIGKILL)
                p.wait()
                info.update(timeout=True, returncode=p.returncode)
        except OSError as e:
            info.update(returncode=None, error=str(e))
    info.update(seconds=round(time.monotonic() - start, 4), stdout_tail=tail(stdout), stderr_tail=tail(stderr))
    return info


def accepted(info, marker):
    return (not info["timeout"] and info["returncode"] == 0
            and marker in info["stdout_tail"].splitlines())


def certify(body, header, cube, tools, options, folder, models, key):
    cnf, drat, lrat = (folder / name for name in ("input.cnf", "proof.drat", "proof.lrat"))
    nc, empty_clause = assemble(body, header, cube, cnf)
    result = {"cnf_sha256": digest(cnf), "stages": {}}
    command = [tools["kissat"], "-q"]
    if not options.binary_drat:
        command.append("--no-binary")
    command += [cnf, drat]
    solve = stage(command, options.solve_timeout, folder, "solve")
    result["stages"]["solve"] = solve
    if solve["timeout"]:
        result["status"] = "SOLVE_TIMEOUT"
    elif solve["returncode"] == 10:
        models.mkdir(parents=True, exist_ok=True)
        saved = models / (key + ".model")
        import shutil
        shutil.copyfile(folder / "solve.out", saved)
        result.update(status="SAT", model=str(saved), model_sha256=digest(saved))
    elif solve["returncode"] != 20:
        result["status"] = "SOLVE_ERROR"
    elif not drat.exists():
        result["status"] = "MISSING_DRAT"
    else:
        result.update(drat_sha256=digest(drat), drat_bytes=drat.stat().st_size)
        convert = stage([tools["drat-trim"], cnf, drat, "-L", lrat], options.convert_timeout, folder, "convert")
        result["stages"]["convert"] = convert
        # drat-trim exits early without LRAT when the input already has an empty
        # clause. Re-add that exact input clause with its index as a RUP hint.
        # This is still untrusted proof generation: cake_lpr must accept it.
        trivial = empty_clause is not None and not convert["timeout"] and convert["returncode"] is not None
        if trivial:
            lrat.write_text(f"{nc + 1} 0 {empty_clause} 0\n")
            result["lrat_source"] = "input_empty_clause_reference"
        else:
            result["lrat_source"] = "drat-trim"
        if convert["timeout"]:
            result["status"] = "CONVERT_TIMEOUT"
        elif not trivial and (not accepted(convert, "s VERIFIED") or not lrat.exists()):
            result["status"] = "CONVERT_ERROR"
        else:
            result.update(lrat_sha256=digest(lrat), lrat_bytes=lrat.stat().st_size)
            check = stage([tools["cake_lpr"], f"--CML_HEAP_SIZE={options.heap_mb}",
                           f"--CML_STACK_SIZE={options.stack_mb}", cnf, lrat],
                          options.check_timeout, folder, "check")
            result["stages"]["check"] = check
            result["status"] = ("CHECK_TIMEOUT" if check["timeout"] else
                                "VERIFIED_UNSAT" if accepted(check, "s VERIFIED UNSAT") else "CHECK_ERROR")
    # Preserve sizes even after a solver/converter timeout or other failed stage;
    # the surrounding temporary directory is removed immediately after return.
    for name, path in (("drat", drat), ("lrat", lrat)):
        if path.is_file():
            result[name + "_bytes"] = path.stat().st_size
    return result


def parser():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cubes", type=Path)
    ap.add_argument("base", type=Path)
    ap.add_argument("log", type=Path)
    ap.add_argument("--kissat", type=Path, default=ROOT / "tools/kissat/build/kissat")
    ap.add_argument("--drat-trim", type=Path, default=ROOT / "tools/drat-trim/drat-trim")
    ap.add_argument("--cake-lpr", type=Path, default=ROOT / "tools/cake_lpr/cake_lpr")
    ap.add_argument("--solve-timeout", type=float, default=600)
    ap.add_argument("--convert-timeout", type=float, default=600)
    ap.add_argument("--check-timeout", type=float, default=600)
    ap.add_argument("--heap-mb", type=int, default=1024)
    ap.add_argument("--stack-mb", type=int, default=256)
    ap.add_argument("--binary-drat", action="store_true")
    ap.add_argument("--work-dir", type=Path, help="scratch parent (defaults beside JSONL log)")
    ap.add_argument("--rerun", action="store_true", help="do not resume previously completed fingerprints")
    return ap


def main(argv=None):
    a = parser().parse_args(argv)
    if min(a.solve_timeout, a.convert_timeout, a.check_timeout, a.heap_mb, a.stack_mb) <= 0:
        raise ValueError("timeouts and memory sizes must be positive")
    a.log = a.log.resolve()
    a.log.parent.mkdir(parents=True, exist_ok=True)
    work = (a.work_dir or a.log.parent).resolve()
    work.mkdir(parents=True, exist_ok=True)
    tools = {"kissat": a.kissat.resolve(), "drat-trim": a.drat_trim.resolve(), "cake_lpr": a.cake_lpr.resolve()}
    for path in tools.values():
        if not os.access(path, os.X_OK) or not path.is_file():
            raise ValueError(f"missing executable: {path}; run tools/build_proof_tools.py")
    provenance = {"schema": SCHEMA, "pipeline_sha256": digest(__file__), "base_sha256": digest(a.base),
                  "tools": {name: {"path": str(p), "sha256": digest(p)} for name, p in tools.items()},
                  "options": {k: getattr(a, k) for k in ("binary_drat", "heap_mb", "stack_mb", "solve_timeout", "convert_timeout", "check_timeout")}}
    cubes = [json.loads(line) for line in a.cubes.read_text().splitlines() if line.strip()]
    if not cubes:
        raise ValueError("empty cube input")
    failures = 0
    with a.log.with_suffix(a.log.suffix + ".lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        done = set()
        if a.log.exists() and not a.rerun:
            for line in a.log.read_text().splitlines():
                if not line.strip():
                    continue
                old = json.loads(line)  # fail closed on a damaged/truncated log
                if old.get("status") in ("VERIFIED_UNSAT", "SAT"):
                    done.add(old.get("key"))
        with tempfile.TemporaryDirectory(prefix="lrat-base-", dir=work) as basework:
            body = Path(basework) / "body.cnf"
            header = normalize_base(a.base, body)
            # Preflight the entire input, not just the first cube.
            for c in cubes:
                validate_cube(c, header[0])
            if digest(a.base) != provenance["base_sha256"]:
                raise ValueError("base changed during input normalization")
            with a.log.open("a") as log:
                for c in cubes:
                    key = hashlib.sha256(canonical({"cube": c, **provenance}).encode()).hexdigest()
                    if key in done:
                        print(f"resume {key}", flush=True)
                        continue
                    tag = c.get("tag", f"u{c.get('u', '')}_{c.get('S', '')}")
                    record = {"key": key, "tag": tag, "cube": c, **provenance}
                    with tempfile.TemporaryDirectory(prefix="lrat-cube-", dir=work) as tmp:
                        try:
                            record.update(certify(body, header, c, tools, a, Path(tmp), a.log.with_suffix(".models"), key))
                        except Exception as e:
                            record.update(status="PIPELINE_ERROR", error=f"{type(e).__name__}: {e}")
                    record["temporary_files_deleted"] = True
                    log.write(canonical(record) + "\n")
                    log.flush()
                    os.fsync(log.fileno())
                    print(f"{tag}: {record['status']}", flush=True)
                    failures += record["status"] not in ("VERIFIED_UNSAT", "SAT")
    return int(failures > 0)


if __name__ == "__main__":
    raise SystemExit(main())

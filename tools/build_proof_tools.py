#!/usr/bin/env python3
"""Build pinned upstream proof tools; publish local tools/ links to a locked cache."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess

ROOT = Path(__file__).resolve().parent


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache", type=Path, default=Path(os.environ.get("AUTOLAB_DATA_DIR", ROOT / ".cache")) / "proof-tools")
    ap.add_argument("--jobs", type=int, default=2)
    a = ap.parse_args()
    if a.jobs < 1:
        ap.error("--jobs must be positive")
    if platform.machine() not in ("x86_64", "AMD64"):
        ap.error("this lock builds cake_lpr's x86-64 target; see README for other architectures")
    a.cache = a.cache.resolve()
    a.cache.mkdir(parents=True, exist_ok=True)
    lock = json.loads((ROOT / "proof_tools.lock.json").read_text())
    built = {}
    with (a.cache / ".build.lock").open("w") as guard:
        fcntl.flock(guard, fcntl.LOCK_EX)
        for name, spec in lock.items():
            dest = a.cache / (name + "-" + spec["revision"])
            executable = dest / spec["executable"]
            stamp = dest / ".autolab-built.json"
            ready = stamp.exists() and executable.exists()
            if ready:
                ready = json.loads(stamp.read_text()).get("sha256") == sha256(executable)
            if not ready:
                if not (dest / ".git").exists():
                    dest.mkdir(exist_ok=True)
                    subprocess.run(["git", "init", str(dest)], check=True)
                subprocess.run(["git", "-C", str(dest), "fetch", "--depth=1", spec["url"], spec["revision"]], check=True)
                subprocess.run(["git", "-C", str(dest), "checkout", "--detach", "FETCH_HEAD"], check=True)
                # Rebuild rather than trusting a leftover executable from an interrupted build.
                if executable.exists():
                    executable.unlink()
                for command in spec["build"]:
                    if command[0] == "make":
                        command = command + [f"-j{a.jobs}"]
                    print(name, command, flush=True)
                    subprocess.run(command, cwd=dest, check=True)
                info = {"revision": spec["revision"], "sha256": sha256(executable)}
                stamp.write_text(json.dumps(info, indent=2) + "\n")
            link = ROOT / name
            if link.is_symlink() and link.resolve() != dest:
                raise RuntimeError(f"refusing to replace existing tool link: {link}")
            if not link.exists():
                link.symlink_to(dest, target_is_directory=True)
            if not link.is_symlink() or link.resolve() != dest:
                raise RuntimeError(f"refusing to replace existing directory: {link}")
            built[name] = json.loads(stamp.read_text())
        (ROOT / "proof_tools.build.json").write_text(json.dumps(built, indent=2) + "\n")
    print(json.dumps(built, indent=2), flush=True)


if __name__ == "__main__":
    main()

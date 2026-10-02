"""Check that every file listed in certificates/MANIFEST.txt exists with the recorded size and sha256 (run from anywhere).
usage: python3 certificates/check_manifest.py            (exit 1 on any mismatch; files of the OPTIONAL section may be absent)"""
import hashlib, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
bad = miss = ok = 0
section = ""
for line in open(ROOT / "certificates/MANIFEST.txt"):
    line = line.rstrip("\n")
    if line.startswith("## "): section = line; continue
    if not line or line.startswith("#"): continue
    sha, size, path = line.split()[:3]
    p = ROOT / path
    if not p.is_file():
        if "OPTIONAL" in section: continue
        print("MISSING", path); miss += 1; continue
    if "volatile" in line: ok += 1; continue
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    if h != sha or p.stat().st_size != int(size): print("MISMATCH", path); bad += 1
    else: ok += 1
print(f"manifest check: {ok} ok, {miss} missing, {bad} mismatched")
sys.exit(1 if bad or miss else 0)

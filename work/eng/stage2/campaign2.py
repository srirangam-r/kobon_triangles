#!/usr/bin/env python3
"""python3 campaign2.py LIST NPROC ROUNDTAG : each LIST line is 'cube mask seconds [--flag ...]' (flags passed to run_cube2.py,
e.g. --qpin). Skips jobs whose result.json exists. Output dir logs/TAG/q<cube>_<mask>."""
import sys, subprocess, os
from concurrent.futures import ThreadPoolExecutor
lst, npr, tag = sys.argv[1], int(sys.argv[2]), sys.argv[3]
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../..'))
jobs = [l.split() for l in open(lst) if l.strip()]
def run(j):
    c, mk, secs, flags = j[0], j[1], j[2], j[3:]
    out = f"work/eng/stage2/logs/{tag}/q{c}_{mk.replace('.', 'd')}"
    if os.path.exists(out + '/result.json'): return
    subprocess.run(['python3', 'work/eng/stage2/run_cube2.py', '--cube', c, '--mask', mk, '--pins', '--seconds', secs, '--chunk', '3000', '--out', out] + flags,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
with ThreadPoolExecutor(npr) as ex: list(ex.map(run, jobs))
open(f'work/eng/stage2/logs/{tag}_done', 'w').write('done')

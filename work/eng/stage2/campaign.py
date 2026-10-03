#!/usr/bin/env python3
"""python3 campaign.py LIST SECONDS NPROC ROUNDTAG : run every 'cube mask' line of LIST with run_cube.py"""
import sys, subprocess, os
from concurrent.futures import ThreadPoolExecutor
lst, secs, npr, tag = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../..'))
jobs = [l.split() for l in open(lst) if l.strip()]
def run(j):
    c, mk = j
    out = f"work/eng/stage2/logs/{tag}/q{c}_{mk.replace('.', 'd')}"
    if os.path.exists(out + '/result.json'): return
    subprocess.run(['python3', 'work/eng/stage2/run_cube.py', '--cube', c, '--mask', mk, '--pins', '--seconds', secs, '--chunk', '3000', '--out', out],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
with ThreadPoolExecutor(npr) as ex: list(ex.map(run, jobs))
open(f'work/eng/stage2/logs/{tag}_done', 'w').write('done')

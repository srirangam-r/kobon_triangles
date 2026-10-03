#!/usr/bin/env python3
"""python3 campaign3.py LIST CAP ROUNDTAG : single scheduler loop; keeps at most CAP run_cube processes alive on the
machine (counting other rounds' jobs too). LIST lines: 'cube mask seconds [--flag ...]'. Skips existing result.json."""
import sys, subprocess, os, time
lst, cap, tag = sys.argv[1], int(sys.argv[2]), sys.argv[3]
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../..'))
def nrunning():
    n = 0
    for p in os.listdir('/proc'):
        if p.isdigit():
            try:
                if b'run_cube' in open(f'/proc/{p}/cmdline', 'rb').read().split(b'\0')[1]: n += 1
            except Exception: pass
    return n
procs = []
for j in [l.split() for l in open(lst) if l.strip()]:
    c, mk, secs, flags = j[0], j[1], j[2], j[3:]
    out = f"work/eng/stage2/logs/{tag}/q{c}_{mk.replace('.', 'd')}"
    if os.path.exists(out + '/result.json'): continue
    while nrunning() >= cap: time.sleep(2)
    procs.append(subprocess.Popen(['python3', 'work/eng/stage2/run_cube2.py', '--cube', c, '--mask', mk, '--pins', '--seconds', secs,
                                   '--chunk', '3000', '--out', out] + flags, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
    time.sleep(1)
for p in procs: p.wait()
open(f'work/eng/stage2/logs/{tag}_done', 'w').write('done')

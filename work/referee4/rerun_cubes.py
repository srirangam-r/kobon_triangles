"""Referee4 audit rerun: run sub-cubes (jsonl: tag, units, clauses, top) on a base CNF with every
sub-cube variable > THRESH renumbered above the base's header nv (fixes the id collision between
wedge_cubes_single.py's IDPool(start_from=max(ids.top, tl, sel)+1) and k6z3's own C16 cardinality
auxiliaries).  Temp CNFs in work/referee4/tmp.  usage:
  python3 rerun_cubes.py cubes.jsonl base.cnf THRESH log [workers] [only_tags_file]"""
import json, subprocess, sys, time, os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
src, base, thresh, logp = sys.argv[1], Path(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
workers = int(sys.argv[5]) if len(sys.argv) > 5 else 4
TMP = Path('/home/nail/stuff/sundai_math/work/referee4/tmp'); TMP.mkdir(exist_ok=True)
KISSAT = '/home/nail/stuff/sundai_math/tools/kissat/build/kissat'
with open(base) as fh:
    head = fh.readline()
nv, nc = int(head.split()[2]), int(head.split()[3])
body_off = len(head)
shift = max(0, nv - thresh)


def run(line):
    c = json.loads(line)
    ren = lambda x: (x + shift if x > 0 else x - shift) if abs(x) > thresh else x
    assert all(abs(u) <= thresh for u in c['units']), 'unit on a sub-cube variable'
    clauses = [[ren(x) for x in cl] for cl in c['clauses']]
    top = max(nv, c['top'] + shift)
    path = TMP / f"sub_{c['tag']}.cnf"
    with open(path, 'w') as out, open(base) as b:
        out.write(f'p cnf {top} {nc + len(c["units"]) + len(clauses)}\n')
        b.seek(body_off)
        while True:
            chunk = b.read(1 << 24)
            if not chunk:
                break
            out.write(chunk)
        out.write(''.join(f'{u} 0\n' for u in c['units']))
        out.write(''.join(' '.join(map(str, cl)) + ' 0\n' for cl in clauses))
    t = time.time()
    r = subprocess.run(['timeout', '1800', KISSAT, '-q', str(path)], capture_output=True, text=True)
    path.unlink()
    v = {10: 'SAT', 20: 'UNSAT'}.get(r.returncode, 'timeout/rc%d' % r.returncode)
    return c['tag'], v, round(time.time() - t, 1)


if __name__ == '__main__':
    done = set()
    if Path(logp).exists():
        done = {l.split(':')[0] for l in open(logp) if 'SAT' in l}
    lines = [l for l in open(src).read().splitlines() if json.loads(l)['tag'] not in done]
    print(f'base {base} nv {nv} thresh {thresh} shift {shift} cubes {len(lines)} (skipping {len(done)} done)', flush=True)
    with ProcessPoolExecutor(workers) as ex, open(logp, 'a') as log:
        print(f'base {base} nv {nv} thresh {thresh} shift {shift}', file=log, flush=True)
        for f in as_completed([ex.submit(run, l) for l in lines]):
            print('%s: %s %ss' % f.result(), file=log, flush=True)
        print('ALL DONE', file=log, flush=True)

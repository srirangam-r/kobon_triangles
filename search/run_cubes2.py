"""Run sub-cubes with extra clauses (jsonl: tag, units, clauses, top) on k6z2. usage: run_cubes2.py cubes.jsonl log timeout [workers]"""
import json, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
W = Path('work/k6z2')
src, logp, limit = sys.argv[1], sys.argv[2], sys.argv[3]
workers = int(sys.argv[4]) if len(sys.argv) > 4 else 16
cubes = [json.loads(l) for l in open(src)]
done = {l.split(':')[0] for l in open(logp)} if Path(logp).exists() else set()
base = Path(sys.argv[5]) if len(sys.argv) > 5 else W / 'k6z2.cnf'
text = base.read_text(); head, body = text.split('\n', 1)
nv, nc = int(head.split()[2]), int(head.split()[3])
def run(c):
    t_ = c['tag']; path = W / f'sub_{t_}.cnf'
    extra = ''.join(f'{l} 0\n' for l in c['units']) + ''.join(' '.join(map(str, cl)) + ' 0\n' for cl in c['clauses'])
    path.write_text(f'p cnf {max(nv, c["top"])} {nc + len(c["units"]) + len(c["clauses"])}\n' + body + extra)
    t = time.time()
    r = subprocess.run(['timeout', limit, 'tools/kissat/build/kissat', '-q', str(path)], capture_output=True, text=True)
    path.unlink()
    v = {10: 'SAT', 20: 'UNSAT'}.get(r.returncode, 'timeout')
    if v == 'SAT': (W / f'SAT_{t_}.model').write_text(r.stdout)
    return t_, v, round(time.time() - t, 1)
with ProcessPoolExecutor(workers) as ex, open(logp, 'a') as log:
    for f in as_completed([ex.submit(run, c) for c in cubes if c['tag'] not in done]):
        print('%s: %s %ss' % f.result(), file=log, flush=True)
    print('ALL DONE', file=log, flush=True)

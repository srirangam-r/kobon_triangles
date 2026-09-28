"""DRAT-certify every k=6, beta=0 solver case: solve with a text DRAT log, check with drat-trim, delete the files.
Cases: (A) 16 C26 sub-cubes + 16 min-S-even plain cubes; (B) 225 singleton-shape sub-cubes (k6z3) + 225 min-S-even plain."""
import json, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
W = Path('work/k6z2'); D = W / 'drat'; D.mkdir(exist_ok=True)
tag = lambda c: c.get('tag') or 'u%d_%s' % (c['u'], '_'.join(map(str, c['S'])))
A_even = [c for c in map(json.loads, open(W / 'wedge_cubes_A_c27.jsonl')) if min(c['S']) % 2 == 0]
jobs = ([('k6z2', c) for c in map(json.loads, open(W / 'A_c26.jsonl'))] + [('k6z2', c) for c in A_even] +
        [('k6z3', c) for c in map(json.loads, open(W / 'B_single.jsonl'))] + [('k6z2', c) for c in map(json.loads, open(W / 'wedge_cubes_B_even.jsonl'))])
logp = W / 'drat_all.jsonl'
done = {json.loads(l)['tag'] for l in open(logp)} if logp.exists() else set()
bodies = {}
def body(base):
    if base not in bodies:
        head, b = Path(f'work/{base}/{base}.cnf').read_text().split('\n', 1)
        bodies[base] = (int(head.split()[2]), int(head.split()[3]), b)
    return bodies[base]
def run(job):
    base, c = job
    nv, nc, b = body(base)
    t_ = tag(c); cnf, prf = D / f'{t_}.cnf', D / f'{t_}.drat'
    units, clauses = c.get('units', []), c.get('clauses', [])
    extra = ''.join(f'{l} 0\n' for l in units) + ''.join(' '.join(map(str, cl)) + ' 0\n' for cl in clauses)
    cnf.write_text(f'p cnf {max(nv, c.get("top", 0))} {nc + len(units) + len(clauses)}\n' + b + extra)
    t = time.time()
    r = subprocess.run(['timeout', '900', 'tools/kissat/build/kissat', '-q', '--no-binary', str(cnf), str(prf)], capture_output=True, text=True)
    ts = round(time.time() - t, 1)
    res = {'tag': t_, 'base': base, 'solve': {10: 'SAT', 20: 'UNSAT'}.get(r.returncode, 'timeout'), 'solve_s': ts}
    if r.returncode == 20:
        t = time.time()
        d = subprocess.run(['timeout', '1800', 'tools/drat-trim/drat-trim', str(cnf), str(prf), '-t', '1800'], capture_output=True, text=True)
        res.update(drat='VERIFIED' if 's VERIFIED' in d.stdout else 'FAILED', check_s=round(time.time() - t, 1),
                   core=next((l for l in d.stdout.splitlines() if 'clauses in core' in l), '').strip())
    elif r.returncode == 10:
        (W / f'SAT_drat_{t_}.model').write_text(r.stdout)
    cnf.unlink(missing_ok=True); prf.unlink(missing_ok=True)
    return res
with ProcessPoolExecutor(12) as ex, open(logp, 'a') as log:
    for f in as_completed([ex.submit(run, j) for j in jobs if tag(j[1]) not in done]):
        print(json.dumps(f.result()), file=log, flush=True)
    print(json.dumps({'tag': 'ALL DONE'}), file=log, flush=True)

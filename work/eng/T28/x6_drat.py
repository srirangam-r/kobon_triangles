"""kissat + drat-trim certificates for the 6-X cubes.
usage: x6_drat.py out.jsonl start stride list.json [keep_dir]      list.json = [[u, idx, S], ...]
Each cube = base CNF (build_X6(anchor=False, flip_break=False), 686,368 vars / 2,091,451 clauses) + the cube clauses."""
import sys, os, json, subprocess, time, tempfile, lzma, shutil
sys.path.insert(0, __import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + '/search'); sys.path.insert(0, __import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + '/work/eng/T28')
import flower_sat as F
import x6_cubes as C
ROOT = __import__("pathlib").Path(__file__).resolve().parents[3].as_posix()
KISSAT, DRAT = f'{ROOT}/tools/kissat/build/kissat', f'{ROOT}/tools/drat-trim/drat-trim'
out, start, stride, lst = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
keep = sys.argv[5] if len(sys.argv) > 5 else None
todo = json.load(open(lst))[start::stride]
M = F.build_X6(anchor=False, flip_break=False)
base = '/tmp/x6_base_%d.cnf' % os.getpid()
M.cnf.to_file(base)
head, body = open(base).read().split('\n', 1)
_, _, nv, nc = head.split()
nv, nc = int(nv), int(nc)
assert nv == M.cnf.nv and nc == len(M.cnf.clauses)
tmp = tempfile.mkdtemp(prefix='x6drat')
for item in todo:
    u, idx, S = item[:3]
    extra = C.cube_clauses(M, tuple(S))
    tag = item[4] if len(item) > 4 else None
    if len(item) > 3:   # optional unit clauses [[kind, L, R], ...] (case split on an existing clause of the cube)
        extra = extra + [[M.ext_var(k, L, R)] for k, L, R in item[3]]
    cnf, prf = f'{tmp}/c.cnf', f'{tmp}/c.drat'
    with open(cnf, 'w') as fh:
        fh.write(f'p cnf {nv} {nc + len(extra)}\n' + body)
        fh.write(''.join(' '.join(map(str, c)) + ' 0\n' for c in extra))
    t0 = time.time()
    r = subprocess.run([KISSAT, '-q', '--no-binary', cnf, prf], capture_output=True, text=True)
    st = time.time() - t0
    row = {'u': u, 'idx': idx, 'S': S, 'split': item[3] if len(item) > 3 else None, 'kissat_rc': r.returncode, 'solve_s': round(st, 1)}
    if r.returncode == 20:
        t1 = time.time()
        d = subprocess.run([DRAT, cnf, prf, '-t', '20000'], capture_output=True, text=True)
        row['verified'] = 's VERIFIED' in d.stdout
        row['check_s'] = round(time.time() - t1, 1)
        if keep and st > 60 and row['verified']:
            os.makedirs(keep, exist_ok=True)
            with open(prf, 'rb') as fi, lzma.open(f'{keep}/u{u}_{idx}' + (('_' + '_'.join(f'{k}{a}{b}' for k, a, b in item[3])) if len(item) > 3 else '') + '.drat.xz', 'wb', preset=6) as fo:
                shutil.copyfileobj(fi, fo)
    elif r.returncode == 10:
        row['verified'] = False; row['SAT'] = True
        print('!!!! SAT cube', u, idx, S, flush=True)
    else:
        row['verified'] = False
    open(out, 'a').write(json.dumps(row) + '\n')
    print(row, flush=True)
os.remove(base)

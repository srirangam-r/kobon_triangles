"""Referee (AUDIT_k5L, Q5): rebuild k5L in-process and check id hygiene.
 - every layer / ZR clause uses only (a) variables above the k5g top or (b) the k5g literals the layer is meant to
   read (z, tri, blk, F, G, s);
 - every CardEnc call inside the layer leaves pool.top >= its largest aux var (no reuse by later pool.id);
 - named layer ids are distinct and all > k5g top;
 - the rebuilt CNF is byte-identical to work/k5L/k5L.cnf and ids.json matches;
 - every cube unit of work/k5L/cubes.jsonl is a layer variable that occurs in some layer clause."""
import hashlib, json, sys
from pathlib import Path
ROOT = Path('/home/nail/stuff/sundai_math')
sys.path.insert(0, str(ROOT / 'search'))
import k5L_layer
from build_k5g import build_g
from build_k5b import n
from pysat.card import CardEnc

cnf, pool, g = build_g(zmax=5)
base_top, nbase = pool.top, len(cnf.clauses)
allowed = set(g['z'].values()) | set(g['tri'].values()) | set(g['blk'].values()) | set(g['F'].values()) | \
    set(g['G'].values()) | set(g['s'].values())
bad_card = []
orig = CardEnc.atmost
def wrapped(*a, **kw):
    r = orig(*a, **kw)
    mx = max((abs(l) for cl in r.clauses for l in cl), default=0)
    if mx > kw['vpool'].top: bad_card.append((mx, kw['vpool'].top))
    return r
k5L_layer.CardEnc.atmost = staticmethod(wrapped)
named_before = set(pool.obj2id.values())
ids = k5L_layer.add_labels(cnf, pool, n, g['z'], g['tri'], g['blk'], g['F'], g['G'], nlab=5)
zr = k5L_layer.upper(cnf, pool, list(g['s'].values()), 6, 'LZr')
ids['ZR'] = {str(j): zr[j] for j in range(1, 7)}
ids['top'] = pool.top; ids['k5g_top'] = base_top
new_named = set(pool.obj2id.values()) - named_before
print('base_top', base_top, 'top', pool.top, 'new named ids', len(new_named), 'min', min(new_named))
tail = cnf.clauses[nbase:]
viol = [cl for cl in tail if any(abs(l) <= base_top and abs(l) not in allowed for l in cl)]
print('layer clauses', len(tail), 'using forbidden base vars:', len(viol), viol[:3])
print('CardEnc top violations:', bad_card)
occ = set(abs(l) for cl in tail for l in cl)
print('named layer ids all > base_top:', min(new_named) > base_top, '| named ids unused in clauses:',
      len([v for v in new_named if v not in occ]))
out = ROOT / 'work/referee4/k5L/tmp/k5L_re.cnf'
cnf.to_file(str(out))
h1 = hashlib.md5(open(out, 'rb').read()).hexdigest(); h2 = hashlib.md5(open(ROOT / 'work/k5L/k5L.cnf', 'rb').read()).hexdigest()
print('md5 rebuilt', h1, 'file', h2, 'SAME' if h1 == h2 else 'DIFFER')
fids = json.load(open(ROOT / 'work/k5L/k5L.ids.json'))
print('ids.json equal:', json.loads(json.dumps(ids)) == fids)
units = set()
for l in open(ROOT / 'work/k5L/cubes.jsonl'):
    c = json.loads(l); units |= {abs(u) for u in c['units']}; assert not c['clauses'] and c['top'] == pool.top
print('cube unit vars', len(units), 'all > base_top:', all(u > base_top for u in units), 'all occur in layer clauses:',
      all(u in occ for u in units), 'max', max(units), '<= nv', cnf.nv)
out.unlink()

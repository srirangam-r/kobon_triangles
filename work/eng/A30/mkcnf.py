import sys
ROOT = __import__("pathlib").Path(__file__).resolve().parents[3].as_posix()
sys.path.insert(0, ROOT + '/work/eng/A30')
import tip_cnf as T
for mirror in (False, True):
    for simple in (False, True):
        e = T.build(0, mirror, True, True, simple)
        e.cnf.to_file(f'{ROOT}/work/eng/A30/drat/own_m{int(mirror)}_s{int(simple)}.cnf')

import glob, sys, collections
sys.path.insert(0, '.')
from arr import *
R = '../../tools/external/kobon-solutions/gallery/data'

def ptype(a, P):
    bl = blocks(a, P)
    rs = rays(a, P)
    others = [Q for Q in a.triples if Q != P]
    shared = {L for L in a.events[P] if any(L in a.events[Q] for Q in others)}
    if len(bl) == 2:
        if (bl[0][0] - bl[1][0]) % 6 == 3:
            ax = rs[bl[0][0]][0]
            return 'ax-' + ('sh' if ax in shared else 'pr')
        return 'bent'
    return 'b%d' % len(bl)

cnt = collections.Counter()
if __name__ == "__main__":
  for series in sys.argv[2:]:
      for f in sorted(glob.glob(f'{R}/{series}/*.json')):
          a = load(f)
          k = len(a.triples)
          if k != int(sys.argv[1]): continue
          # sharing graph
          lines = collections.Counter(L for P in a.triples for L in a.events[P])
          mult = tuple(sorted((v for v in lines.values() if v > 1), reverse=True))
          types = tuple(sorted(ptype(a, P) for P in a.triples))
          # bridges
          br = 0
          for L, v in lines.items():
              if v > 1:
                  ps = sorted(a.pos[L][P] for P in a.triples if L in a.events[P])
                  br += sum(1 for x, y in zip(ps, ps[1:]) if y == x + 1)
          cnt[(mult, br, types, a.Z(), a.D())] += 1
  for k, v in sorted(cnt.items(), key=lambda kv: -kv[1]): print(v, k)

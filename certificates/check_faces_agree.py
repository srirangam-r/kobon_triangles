"""Cross-check window.faces (gap counting, used by the perturbation and pair lemma enumerations) against
faces_indep.faces_indep (explicit planar embedding + half-edge tracing) on every word of the windows used:
  single m-fold point windows m = 4, 5 (k = m, w0 = [(0, m-1)]), the pair window PQ (k = 6) and PS (k = 5).
Prints the number of words compared and mismatches (THEORY section 27 notes: 1,945 words, 0 mismatches)."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "work/eng/pert2"))
from window import crossing_set, all_words, faces
from faces_indep import faces_indep

wins = {"m=4": (4, [(0, 3)]), "m=5": (5, [(0, 4)]), "PQ": (6, [(2, 5), (0, 2)]), "PS": (5, [(1, 4), (0, 1)])}
total = bad = 0
for name, (k, w0) in wins.items():
    req, _ = crossing_set(k, w0)
    ws = all_words(k, req)
    nb = 0
    for w in ws:
        a = faces(k, list(w))[:3]
        b = faces_indep(k, list(w))
        if tuple(a[0]) != tuple(b[0]) or a[1] != b[1] or a[2] != b[2]:
            nb += 1
    print(f"window {name}: {len(ws)} words, mismatches {nb}")
    total += len(ws); bad += nb
print(f"faces agreement: {total} words compared, {bad} mismatches")
sys.exit(1 if bad else 0)

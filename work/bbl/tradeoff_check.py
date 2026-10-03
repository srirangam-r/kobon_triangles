#!/usr/bin/env python3
"""Score Task 4 conjectures; sample checks are not universal proofs.

Reconstruction uses the lead-accepted Note 3 routines, not Note 4's
unreviewed secondary geometry assertions. All slacks use integer scales.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import note3_check as N3
from arr import Arr


def scalar_metrics(d):
    n = d.get('n', 18)
    assert n == 18, 'These conjectures are specific to n=18'
    lam = n * (n - 2) - 3 * d['T']
    ec = d['end_counts']
    assert ec.get('W', 0) == 2 * d['W']
    assert d['pi'] == n - d['W']
    # Scalar mode is only for the supplied multiplicity-at-most-three cache.
    assert '**' not in d['gens']
    assert 2 * lam == 2 * d['pi'] + 2 * d['U'] + d['Delta']
    dn = d['Delta'] - (2 * d['Z'] - d['U'] - ec.get('Z', 0))
    assert dn >= 0
    return dict(n=n, T=d['T'], Lambda=lam, pi=d['pi'], W=d['W'],
                U=d['U'], Delta=d['Delta'], Z=d['Z'], end_counts=ec,
                I=ec.get('I3', 0) + ec.get('I4', 0), Delta_N=dn,
                E=2 * lam - 2 * d['pi'], all8=0)


def rebuilt_metrics(d):
    n = d.get('n', 18)
    assert n == 18, 'These conjectures are specific to n=18'
    N3.word_valid(d['gens'], n)
    a = Arr(d['gens'], n)
    assert max(map(len, a.events)) <= 4
    z = N3.credit_state(a)
    ec = z['end_counts']
    lam = n * (n - 2) - 3 * a.T()
    assert z['C'] == 2 * lam
    dn = z['end_remainder'] - (2 * a.Z() - z['U'] - ec.get('Z', 0))
    assert dn >= 0
    ends = N3.end_data(a)
    wends = Counter(e['L'] for e in ends if e['kind'] == 'W')
    interior = [L for L in range(n) if wends[L] == 2]
    perfect = [L for L in interior if all(len(t) == 1 for t in a.t[L])]
    with_zero = [L for L in interior if any(not t for t in a.t[L])]
    with_double = [L for L in interior if any(len(t) == 2 for t in a.t[L])]
    records = N3.BC.block_partition(a)
    caps = {r['far']: r for r in records if r['kind'] in ('U', 'I')}
    # Each touch/end centre has exactly one incoming block and cap line.
    assert len(caps) == sum(r['kind'] in ('U', 'I') for r in records)
    line_details = []
    perfect_triples = Counter()
    perfect_caps = Counter()
    for L in perfect:
        row = a.rows[L]
        triples = [v for v in row if len(a.events[v]) == 3]
        same_steps = []
        for i, v in enumerate(row[1:-1], 1):
            if len(a.events[v]) == 2 and a.t[L][i - 1] == a.t[L][i]:
                r = caps[v]
                assert r['cap'] == L
                same_steps.append(dict(vertex=v, kind=r['kind'], origin=r['point']))
                perfect_caps[r['kind']] += 1
        perfect_triples.update(triples)
        line_details.append(dict(L=L, triples=triples, caps=same_steps))
    class_ok, _ = N3.GB.class_check(a)
    triple_ok = N3.opt_triples(a)
    # Count P0 without using these eligibility filters.
    all8 = sum(len(ev) == 4 and all(N3.GB.tri_sectors(a, p))
               for p, ev in enumerate(a.events))
    m = dict(n=n, T=a.T(), Lambda=lam, pi=n - z['W'], W=z['W'],
             U=z['U'], Delta=z['end_remainder'], Z=a.Z(), end_counts=ec,
             I=ec.get('I3', 0) + ec.get('I4', 0), Delta_N=dn,
             E=2 * lam - 2 * (n - z['W']), S=z['S'], all8=all8,
             structural_class=class_ok, triple_optimality=triple_ok,
             word_valid=True, P0=len(perfect), interior_lines=interior,
             perfect_lines=perfect, interior_with_zero=with_zero,
             interior_with_double=with_double, perfect_line_details=line_details,
             Q0=len(set(interior) - set(with_zero)),
             perfect_triple_incidence=dict(sorted(perfect_triples.items())),
             perfect_cap_counts=dict(sorted(perfect_caps.items())),
             triples=len(a.triples))
    if class_ok and triple_ok:
        for q in line_details:
            assert (len(q['triples']) + len(q['caps'])) % 2 == 1
    for key in ('T', 'pi', 'W', 'U', 'Delta', 'Z', 'triples', 'end_counts'):
        if key in d:
            assert d[key] == m[key], ('cache mismatch', key, d[key], m[key])
    return m


def scores(m):
    e, pi, u = m['E'], m['pi'], m['U']
    b = e - 18 + 3 * pi
    out = dict(B=(b, 1), D4=(4 * b - u, 4), D6=(6 * b - u, 6))
    if m['all8']:
        out['A_all8'] = (b - 1, 1)
    if 'P0' in m:
        p, i, dn = m['P0'], m['I'], m['Delta_N']
        out.update(O1=(i + 2 * u + dn - p, 1),
                   O3half=(3 * i + 4 * u + 2 * dn - 2 * p, 2),
                   O2=(2 * i + 2 * u + dn - p, 1))
        out['O2Q'] = (2 * i + 2 * u + dn - m['Q0'], 1)
    return out


class Report:
    def __init__(self, out, name):
        self.out, self.name = out, name
        self.counts = Counter()
        self.candidates = {}
        self.splits = Counter()

    def add(self, d, m, source, record):
        self.counts['records'] += 1
        if m.get('structural_class') and m.get('triple_optimality'):
            self.counts['eligible'] += 1
        if m['all8']:
            self.counts['with_all8'] += 1
        if m.get('P0', 0):
            self.counts['with_P0'] += 1
        self.splits[(m['pi'], m['U'], m['Delta'])] += 1
        for name, (slack, scale) in scores(m).items():
            s = self.candidates.setdefault(name, dict(tested=0, failures=0,
                                                      scale=scale, minimum=None))
            s['tested'] += 1
            s['failures'] += int(slack < 0)
            if s['minimum'] is None or slack < s['minimum']:
                s.update(minimum=slack, minimum_source=str(source),
                         minimum_record_1_based=record)
                witness = dict(source=str(source), record_1_based=record,
                               gens=d['gens'], metrics=m,
                               candidate=name, scaled_slack=slack, scale=scale)
                (self.out / f'{self.name}_{name}_minimum.json').write_text(
                    json.dumps(witness, indent=2) + '\n')
            if slack < 0 and not s.get('first_failure_saved'):
                s['first_failure_saved'] = True
                witness = dict(source=str(source), record_1_based=record,
                               gens=d['gens'], metrics=m,
                               candidate=name, scaled_slack=slack, scale=scale)
                (self.out / f'{self.name}_{name}_first_failure.json').write_text(
                    json.dumps(witness, indent=2) + '\n')

    def result(self):
        return dict(counts=dict(sorted(self.counts.items())),
                    candidates=self.candidates,
                    splits=[dict(pi=p, U=u, Delta=d, count=c)
                            for (p, u, d), c in sorted(self.splits.items())])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('inputs', nargs='+', type=Path)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--scalar-only', action='store_true')
    p.add_argument('--limit', type=int)
    p.add_argument('--progress', type=int, default=1000)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    overall = Report(args.out, 'overall')
    eligible = Report(args.out, 'eligible')
    per_input = {}
    start = time.monotonic()
    errors = []
    with (args.out / 'metrics.jsonl').open('w') as mf:
        for source in args.inputs:
            report = Report(args.out, source.stem)
            for idx, line in enumerate(source.open(), 1):
                if args.limit and idx > args.limit:
                    break
                d = json.loads(line)
                if not d.get('gens'):
                    continue
                try:
                    m = scalar_metrics(d) if args.scalar_only else rebuilt_metrics(d)
                except Exception as exc:
                    errors.append(dict(source=str(source), record_1_based=idx,
                                       gens=d['gens'], error=repr(exc)))
                    print(f'ERROR {source}:{idx}: {exc!r}', flush=True)
                    continue
                report.add(d, m, source, idx)
                overall.add(d, m, source, idx)
                if m.get('structural_class') and m.get('triple_optimality'):
                    eligible.add(d, m, source, idx)
                mf.write(json.dumps(dict(source=str(source), record_1_based=idx,
                                         **m), sort_keys=True) + '\n')
                if args.progress and overall.counts['records'] % args.progress == 0:
                    print(json.dumps(dict(progress=overall.counts['records'],
                                          elapsed_seconds=round(time.monotonic()-start, 3),
                                          candidates=overall.candidates)), flush=True)
            per_input[str(source)] = report.result()
    summary = dict(mode='scalar' if args.scalar_only else 'rebuilt',
                   elapsed_seconds=round(time.monotonic() - start, 3),
                   overall=overall.result(), eligible=eligible.result(),
                   inputs=per_input, reconstruction_errors=errors)
    (args.out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(dict(mode=summary['mode'],
                          elapsed_seconds=summary['elapsed_seconds'],
                          counts=summary['overall']['counts'],
                          candidates=summary['overall']['candidates'],
                          eligible_counts=summary['eligible']['counts'],
                          eligible_candidates=summary['eligible']['candidates'],
                          reconstruction_errors=len(errors)), sort_keys=True), flush=True)
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()

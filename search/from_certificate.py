"""Convert a kobon-solutions gallery certificate into a hill submission.

Certificates store exact rational lines a*x + b*y = c; the hill wants integer
triples [a, b, c] for a*x + b*y + c = 0. Each line is scaled by the LCM of its
own denominators, which leaves the line (and every exact concurrency) unchanged.

    python3 search/from_certificate.py <certificate.json> <submission_dir>
"""
import json
import sys
from fractions import Fraction
from math import gcd, lcm
from pathlib import Path

LIMIT = 10**30


def to_integer_line(a, b, c):
    a, b, c = Fraction(a), Fraction(b), Fraction(-Fraction(c))
    scale = lcm(a.denominator, b.denominator, c.denominator)
    row = [int(v * scale) for v in (a, b, c)]
    divisor = gcd(gcd(abs(row[0]), abs(row[1])), abs(row[2]))
    row = [v // divisor for v in row]
    if max(abs(v) for v in row) > LIMIT:
        raise ValueError(f"coefficient exceeds 10^30 after clearing denominators: {row}")
    return row


def main(certificate, out_dir):
    data = json.loads(Path(certificate).read_text())
    assert data["line_equation"] == "a*x + b*y = c", data["line_equation"]
    lines = [to_integer_line(*row) for row in data["lines_frac"]]
    assert len(lines) == data["n"]
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "solution.json").write_text(json.dumps({"lines": lines}) + "\n")
    biggest = max(abs(v) for row in lines for v in row)
    print(f"n={len(lines)} claimed={data['triangle_count']} largest |coef| ~ 10^{len(str(biggest)) - 1}")


if __name__ == "__main__":
    main(*sys.argv[1:])

"""Exact bounded triangular-face counter. Submission code is never executed."""
import json
from fractions import Fraction
from itertools import combinations
from math import gcd
from pathlib import Path

MAX_BYTES = 65536
MAX_COEFFICIENT = 10**30


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def _normalize(values):
    divisor = gcd(gcd(abs(values[0]), abs(values[1])), abs(values[2]))
    result = tuple(value // divisor for value in values)
    first = next(value for value in result if value)
    return tuple(-value for value in result) if first < 0 else result


def _load(submission, n):
    path = Path(submission) / "solution.json"
    if path.is_symlink() or not path.is_file():
        raise ValueError("submission must contain a regular, non-symlink solution.json")
    with path.open("rb") as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("solution.json exceeds the 65536-byte size limit")
    data = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique_object)
    if not isinstance(data, dict) or set(data) != {"lines"}:
        raise ValueError('solution.json must be an object with only a "lines" field')
    rows = data["lines"]
    if not isinstance(rows, list) or len(rows) != n:
        raise ValueError(f'"lines" must contain exactly {n} lines')
    lines = []
    seen = set()
    for index, row in enumerate(rows):
        if not isinstance(row, list) or len(row) != 3:
            raise ValueError(f"lines[{index}] must be [a, b, c]")
        if any(type(value) is not int for value in row):
            raise ValueError(f"lines[{index}] coefficients must be JSON integers")
        if any(abs(value) > MAX_COEFFICIENT for value in row):
            raise ValueError(f"lines[{index}] coefficient magnitude exceeds 10^30")
        if row[0] == row[1] == 0:
            raise ValueError(f"lines[{index}] has a = b = 0 and is not a line")
        line = _normalize(row)
        if line in seen:
            raise ValueError(f"lines[{index}] duplicates another geometric line")
        seen.add(line)
        lines.append(line)
    return lines


def _intersection(first, second):
    a, b, c = first
    d, e, f = second
    w = a * e - b * d
    if w == 0:
        return None
    x, y = b * f - c * e, c * d - a * f
    divisor = gcd(gcd(abs(x), abs(y)), abs(w))
    if w < 0:
        divisor = -divisor
    return x // divisor, y // divisor, w // divisor


def count_triangles(lines):
    """Each side of a triangular face joins consecutive arrangement vertices.

    Intersections on each line are deduplicated before sorting. This handles
    concurrent and parallel lines without assuming general position.
    """
    n = len(lines)
    points = [[None] * n for _ in range(n)]
    vertices = [set() for _ in lines]
    for i, j in combinations(range(n), 2):
        point = _intersection(lines[i], lines[j])
        points[i][j] = points[j][i] = point
        if point is not None:
            vertices[i].add(point)
            vertices[j].add(point)
    ranks = []
    for line, line_vertices in zip(lines, vertices):
        axis = 0 if line[1] else 1  # x for nonvertical lines, otherwise y
        ordered = sorted(line_vertices, key=lambda p: Fraction(p[axis], p[2]))
        ranks.append({point: rank for rank, point in enumerate(ordered)})
    triangles = []
    for i, j, k in combinations(range(n), 3):
        ij, ik, jk = points[i][j], points[i][k], points[j][k]
        if ij is None or ik is None or jk is None or ij == ik:
            continue
        if (
            abs(ranks[i][ij] - ranks[i][ik]) == 1
            and abs(ranks[j][ij] - ranks[j][jk]) == 1
            and abs(ranks[k][ik] - ranks[k][jk]) == 1
        ):
            triangles.append([i, j, k])
    return triangles


def _config(n, final):
    return [
        {"name": "n", "value": n, "primary": True},
        {"name": "geometry", "value": "bounded-triangular-faces", "primary": True},
        {"name": "arithmetic", "value": "exact-rational", "primary": True},
        {"name": "mode", "value": "test" if final else "validation", "primary": False},
    ]


def eval(submission: Path, *, final: bool = False, n: int = 18) -> dict:
    config = _config(n, final)
    try:
        if type(n) is not int or not 3 <= n <= 100:
            raise ValueError("n must be an integer between 3 and 100")
        lines = _load(submission, n)
    except (ValueError, OSError, RecursionError) as error:
        return {
            "passed": False, "metrics": [], "config": config,
            "details": {"error": str(error)[:300]},
        }
    triangles = count_triangles(lines)
    return {
        "passed": True,
        "metrics": [{"name": "triangles", "value": len(triangles), "direction": "max"}],
        "config": config,
        "details": {
            "line_count": n,
            "triangle_line_indices": triangles,
            "index_base": 0,
        },
    }



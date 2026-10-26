"""
Placement of the points of a diagram for drawing.

The x coordinates are fixed: vertex k is at x = k + 1 (its position in the product of operators), outgoing external
points at x = 0 and incoming ones at x = n_vertices + 1. Only the heights are chosen, by minimising a cost that
penalises, from most to least important:
- lines that cross,
- points lying on (or very close to) a line they do not belong to,
- external points on the same side that are too close together,
- tall diagrams and steep lines.
The minimisation tries every height of a grid for one point at a time, until nothing improves, from a few starting
shapes. Diagrams have few points, so this is fast and gives the same result every time.

Distances and angles are measured as drawn: one step in x is drawn about twice as long as one unit in y, both in
the TikZ output and in the notebooks.
"""
from itertools import combinations
from math import atan2, degrees

X_ASPECT = 2.0
CROSSING = 100.0
TOO_CLOSE_TO_LINE = 60.0
NEAR_DISTANCE = 0.5
SMALL_ANGLE = 40.0
MIN_ANGLE = 15.0
CLOSE_LINES = 30.0
EXTERNAL_SPACING = 40.0
STEEPNESS = 0.05
HEIGHT = 0.03


def _orientation(p, q, r):
    value = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return 0 if abs(value) < 1e-9 else (1 if value > 0 else -1)


def _cross(p1, p2, p3, p4):
    """True if the segments p1-p2 and p3-p4 cross at a point inside both (or overlap)."""
    o1, o2 = _orientation(p1, p2, p3), _orientation(p1, p2, p4)
    o3, o4 = _orientation(p3, p4, p1), _orientation(p3, p4, p2)
    if o1 != o2 and o3 != o4 and 0 not in (o1, o2, o3, o4):
        return True
    # Collinear segments that overlap
    if o1 == o2 == o3 == o4 == 0:
        lo1, hi1 = sorted((p1[0], p2[0]))
        lo2, hi2 = sorted((p3[0], p4[0]))
        return min(hi1, hi2) - max(lo1, lo2) > 1e-9
    return False


def _distance(point, a, b):
    """Distance from a point to the segment a-b."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    length2 = dx * dx + dy * dy
    s = 0.0 if length2 == 0 else max(0.0, min(1.0, ((point[0] - a[0]) * dx + (point[1] - a[1]) * dy) / length2))
    x, y = a[0] + s * dx - point[0], a[1] + s * dy - point[1]
    return (x * x + y * y) ** 0.5


def _angle(a, b, c):
    """Angle in degrees at a between the segments a-b and a-c."""
    difference = abs(atan2(b[1] - a[1], b[0] - a[0]) - atan2(c[1] - a[1], c[0] - a[0]))
    return degrees(min(difference, 2 * 3.141592653589793 - difference))


def place(n_vertices, lines, external):
    """
    Heights of the vertices and external points of a diagram.

    Args:
        n_vertices: number of vertices
        lines: (vertex a, vertex b) of every line between vertices (several lines between the same vertices are
            drawn bent, so they count once)
        external: (vertex, "out" or "in") of every external line, in the order of their labels
    Returns:
        (vertex heights, external heights)
    """
    n_out = sum(1 for _, io in external if io == "out")
    n_in = len(external) - n_out
    top = 2.0 * max(n_out, n_in, 2) + 2.0
    grid = [k * 0.5 for k in range(int(2 * top) + 1)]

    # Points: vertices first, then external points
    x = [k + 1.0 for k in range(n_vertices)] + [0.0 if io == "out" else n_vertices + 1.0 for _, io in external]
    y = [0.0] * len(x)
    placed = {"out": 0, "in": 0}
    for e, (v, io) in enumerate(external):
        side_total = n_out if io == "out" else n_in
        y[n_vertices + e] = top / 2 + 2.0 * placed[io] - (side_total - 1)
        placed[io] += 1
    for v in range(n_vertices):
        heights = [y[n_vertices + e] for e, (w, _) in enumerate(external) if w == v]
        y[v] = sum(heights) / len(heights) if heights else top / 2

    segments = sorted({tuple(sorted((a, b))) for a, b in lines if a != b})
    segments += [(v, n_vertices + e) for e, (v, _) in enumerate(external)]
    sides = {io: [n_vertices + e for e, (_, side) in enumerate(external) if side == io] for io in ("out", "in")}

    n_points = len(x)
    visual = [[X_ASPECT * px, py] for px, py in zip(x, y)]
    incident = [[i for i, (a, b) in enumerate(segments) if p in (a, b)] for p in range(n_points)]
    side_of = {p: side for side in sides.values() for p in side}

    def set_height(p, value):
        y[p] = value
        visual[p][1] = value

    def pair_term(i, j):
        (a, b), (c, d) = segments[i], segments[j]
        shared = {a, b} & {c, d}
        if not shared:
            if _cross(visual[a], visual[b], visual[c], visual[d]):
                return CROSSING
            # Lines that do not cross but run close to each other
            gap = min(_distance(visual[a], visual[c], visual[d]), _distance(visual[b], visual[c], visual[d]),
                      _distance(visual[c], visual[a], visual[b]), _distance(visual[d], visual[a], visual[b]))
            return CLOSE_LINES if gap < NEAR_DISTANCE else 0.0
        if len(shared) == 1:
            # Lines leaving the same point in almost the same direction look like one line
            (common,) = shared
            angle = _angle(visual[common], visual[b if a == common else a], visual[d if c == common else c])
            if angle < MIN_ANGLE:
                return SMALL_ANGLE * (1 + (MIN_ANGLE - angle) / MIN_ANGLE)
        return 0.0

    def near_term(q, i):
        a, b = segments[i]
        distance = _distance(visual[q], visual[a], visual[b])
        return TOO_CLOSE_TO_LINE * (1 + (NEAR_DISTANCE - distance) / NEAR_DISTANCE) if distance < NEAR_DISTANCE else 0.0

    def steep_term(i):
        a, b = segments[i]
        return STEEPNESS * (y[a] - y[b]) ** 2

    def spacing_term(p, q):
        return EXTERNAL_SPACING if abs(y[p] - y[q]) < 1.0 else 0.0

    def height_term():
        return HEIGHT * (max(y) - min(y)) ** 2

    def cost():
        total = sum(pair_term(i, j) for i, j in combinations(range(len(segments)), 2))
        total += sum(near_term(q, i) for i, (a, b) in enumerate(segments) for q in range(n_points) if q not in (a, b))
        total += sum(steep_term(i) for i in range(len(segments)))
        total += sum(spacing_term(p, q) for side in sides.values() for p, q in combinations(side, 2))
        return total + height_term()

    def local_cost(p):
        """The terms of cost that depend on the height of point p (the others do not change when p moves)."""
        mine = incident[p]
        mine_set = set(mine)
        total = 0.0
        for i in mine:
            for j in range(len(segments)):
                if j != i and (j not in mine_set or j > i):
                    total += pair_term(i, j)
            a, b = segments[i]
            for q in range(n_points):
                if q != a and q != b:
                    total += near_term(q, i)
            total += steep_term(i)
        for i, (a, b) in enumerate(segments):
            if p != a and p != b:
                total += near_term(p, i)
        for q in side_of.get(p, ()):
            if q != p:
                total += spacing_term(p, q)
        return total + height_term()

    # Large drawings (many points) get a shorter search, which still removes most problems
    large = n_points > 20

    def descend():
        for _ in range(3 if large else 10):
            improved = False
            for p in range(n_points):
                current = y[p]
                best = local_cost(p)
                for candidate in grid:
                    if candidate == current:
                        continue
                    set_height(p, candidate)
                    value = local_cost(p)
                    if value < best - 1e-9:
                        best, current, improved = value, candidate, True
                set_height(p, current)
            if not improved:
                break
        return cost()

    # The search can stop in a local minimum, so it starts from a few shapes and keeps the best result: vertices at
    # the height of their external points, and vertices alternately above and below it (both ways), or all above.
    start = list(y)
    shapes = [[0.0] * n_vertices,
              [2.0 * (-1) ** k for k in range(n_vertices)],
              [-2.0 * (-1) ** k for k in range(n_vertices)],
              [2.0] * n_vertices]
    best_value, best_y = None, None
    for shape in shapes[:1] if large else shapes:
        for p in range(n_points):
            set_height(p, start[p])
        for v in range(n_vertices):
            set_height(v, min(max(round(2 * (start[v] + shape[v])) / 2, 0.0), top))
        value = descend()
        if best_value is None or value < best_value - 1e-9:
            best_value, best_y = value, list(y)
    y[:] = best_y

    # Start the drawing at height 1, as in the canonical diagram files
    shift = 1.0 - min(y)
    return [h + shift for h in y[:n_vertices]], [h + shift for h in y[n_vertices:]]

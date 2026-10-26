# Legacy engine

This folder holds the original diagram generation code, kept for reference and comparison. It is not part of the `rgpep_dgt` package and is not installed with it.

- `pipeline.py`: the original `calculate_diagrams`, with the same arguments and return values as `rgpep_dgt.calculate_diagrams` (without counterterms, workers or cache).
- `transforms/` and `search/`: the original modules for joining, simplifying and grouping diagrams.
- `tests/`: the regression tests of the bugs fixed in it, the literature checks run with it, and a comparison with the new engine.

## Status

The bugs listed in [docs/assessment.md](../docs/assessment.md) were fixed here before the new engine was written (see [docs/roadmap.md](../docs/roadmap.md), step 1). One known limitation remains: from third order on, it counts a contraction once for every way of building the product from products of two factors. Głazek's Eq. (31) has one operator with summed coefficients, so these counts are too large. The tests that show this are marked as expected failures.

Otherwise it finds the same diagrams as `rgpep_dgt.engine`. It is much slower (12 s for φ⁴ at fourth order, against 0.01 s), and its framework mode leaves out the instantaneous terms.

## Use

Run from the repository root:

```python
from legacy.pipeline import calculate_diagrams

points, connections, count, _ = calculate_diagrams("phi4", 1, 1, 3)
```

To run its tests:

```bash
python -m pytest legacy/tests
```

They also run on GitHub Actions.

The canonical diagrams (`rgpep_dgt/can_diagrams`) and the array helpers (`rgpep_dgt/core/array_format.py`) are shared with the main package.

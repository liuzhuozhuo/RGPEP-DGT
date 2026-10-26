# RGPEP Diagram Generation Tool

RGPEP-DGT is a Python based framework for generating and visualizing diagrams that occur in the perturbative expansion to solve the RGPEP equation.

## Motivation

This project was developed to

## Theoretical background

See [docs/literature.md](docs/literature.md) for the rules used to generate the diagrams and the references they come from.

## Installation

```bash
pip install -e .            # computing diagrams
pip install -e ".[drawing]" # also drawing them with the feynman package
```

## Usage

```python
from rgpep_dgt import calculate_diagrams, represent_order_diagram

# Diagrams of order 3 for one incoming and one outgoing particle in phi^4 theory
points, connections, count, diagrams = calculate_diagrams("phi4", 1, 1, 3)
represent_order_diagram(points, connections, count, process=[1, 1])
```

The available theories are `"phi4"`, `"qcd_gluons"` and `"qcd"`. For theories with several types of particles, the numbers of incoming and outgoing particles are given as lists (e.g. `[1, 0, 0, 0]` for one gluon in QCD). The notebooks `example.ipynb` and `phi4_test.ipynb` show more examples, including the `"framework"` mode, which lists the products of Hamiltonian terms that contribute.

## Project structure

- `rgpep_dgt/engine/` generates the diagrams.
  - `theory.py`: theories as lists of Hamiltonian terms.
  - `generate.py`: products of terms and their Wick contractions.
  - `arrays.py`: conversion to the arrays used for drawing.
- `rgpep_dgt/can_diagrams/` holds the canonical (initial) Hamiltonian terms of each theory.
- `rgpep_dgt/core/pipeline.py` contains `calculate_diagrams`, the main entry point.
- `rgpep_dgt/rendering/` draws the diagrams.
- `rgpep_dgt/transforms/` and `rgpep_dgt/search/` hold the legacy engine (`engine="legacy"`), kept for comparison.
- `tests/` contains the tests, including a brute-force reference in `tests/wick_reference.py`.
- `docs/` contains the assessment, the roadmap and the literature notes.

## Dependencies

- Python ≥ 3.10, numpy, matplotlib
- [feynman](https://pypi.org/project/feynman/) for `represent_order_diagram` (optional)
- pytest to run the tests

## Tests

```bash
python -m pytest
```

## Roadmap

See [docs/roadmap.md](docs/roadmap.md).

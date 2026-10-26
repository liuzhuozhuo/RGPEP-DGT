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

The available theories are `"phi4"`, `"qcd_gluons"` and `"qcd"`. For theories with several types of particles, the numbers of incoming and outgoing particles are given as lists (e.g. `[1, 0, 0, 0]` for one gluon in QCD). The notebook `example.ipynb` walks through everything the package does. It covers:
- theories and their terms;
- the diagrams of a process, with their counts and symmetry factors;
- diagrams as Hamiltonian terms with their RGPEP coefficients;
- the products of terms before contraction (the `"framework"` mode);
- QCD;
- counterterms;
- the contents of a diagram object;
- LaTeX output;
- large orders.

It writes its files to `output/`.

### Counterterms, expressions and LaTeX

```python
from rgpep_dgt import get_theory, generate_diagrams, term_products, products_table, expression_table, write_latex

theory = get_theory("qcd_gluons", counterterms=True, max_order=3)
diagrams = generate_diagrams(theory, 3, [1, 0], [2, 0])

print(products_table(theory, term_products(theory, 3, [1, 0], [2, 0])))  # products of terms before contraction
print(expression_table(theory, diagrams))                                  # every diagram as a Hamiltonian term
write_latex("three_gluon_vertex.tex", theory, diagrams)                    # TikZ-Feynman drawings + expressions
```

Each diagram is written as `f_t [sum of RGPEP coefficients B] (weight) (product of terms) -> external operators`. The coefficients B are given as labels. Their closed formulas are planned next, in [docs/plan_coefficients.md](docs/plan_coefficients.md). The coefficient labels follow Głazek, Acta Phys. Pol. B 43, 1843 (2012), App. B. The LaTeX file needs the `tikz-feynman` package and compiles with `pdflatex`.

- **Counterterms.** `counterterms=True` adds mass and coupling-constant counterterms at every order where the theory has a loop correction to them.
- **Weight.** The weight includes the normalisation of the terms. In φ⁴ that is 1/(k! l!) from φ⁴/4!, so weights reproduce the usual symmetry factors.

### Drawings

The points of a diagram are placed automatically. The x positions follow the order of the operators in the product: outgoing particles are on the left, incoming ones on the right, numbered as in the expressions. The heights are chosen so that lines do not cross and no point lies on a line it does not belong to.

Counterterm vertices are marked: a crossed dot in LaTeX, a star in the notebooks. In LaTeX, gluons are drawn as springs, instantaneous interactions dotted, and quarks with arrows.

Some diagrams cannot avoid crossings with the vertex order fixed, e.g. four vertices all joined to each other.

### Large orders

`generate_diagrams`, `term_products` and `calculate_diagrams` accept two options:
- `workers=n` uses several processes, and `workers=None` uses one per CPU.
- `cache=True` keeps the results in `~/.cache/rgpep_dgt` and reuses them. They are recomputed automatically when the theory, the process or the code changes.

For example, φ⁴ 2→2 at seventh order (121,419 diagrams) takes about 11 s in one process and 6 s with 8.

## Project structure

- `rgpep_dgt/engine/` generates the diagrams.
  - `theory.py`: theories as lists of Hamiltonian terms, and their counterterms.
  - `generate.py`: products of terms and their Wick contractions.
  - `cache.py`: disk cache of generated diagrams.
  - `expressions.py`: diagrams as Hamiltonian terms, with RGPEP coefficients.
  - `layout.py`: placement of the points for drawing.
  - `arrays.py`: conversion to the arrays used for drawing.
- `rgpep_dgt/can_diagrams/` holds the canonical (initial) Hamiltonian terms of each theory.
- `rgpep_dgt/core/` contains `calculate_diagrams` (`pipeline.py`), the main entry point, and helpers for the array format (`array_format.py`).
- `rgpep_dgt/rendering/` draws the diagrams: `matplotlib_backend.py` in notebooks, and `tikz.py` for LaTeX.
- `tests/` contains the tests, including a brute-force reference in `tests/wick_reference.py`.
- `legacy/` holds the original engine, kept for comparison only, with its own tests. It is not installed with the package; see [legacy/README.md](legacy/README.md).
- `docs/` contains the assessment, the roadmap, the literature notes and the plan for evaluating the RGPEP coefficients.

## Dependencies

- Python ≥ 3.10, numpy, matplotlib
- [feynman](https://pypi.org/project/feynman/) for `represent_order_diagram` (optional)
- pytest to run the tests
- pdflatex with `tikz-feynman` to compile the LaTeX output (optional)

## Tests

```bash
python -m pytest
```

The tests compare the diagrams with hand-derived counts, an independent brute-force enumeration and published results; see [docs/literature.md](docs/literature.md). The tests of the legacy engine run separately with `python -m pytest legacy/tests`. Both run on GitHub Actions on every push.

## Citation

See [CITATION.cff](CITATION.cff).

## Roadmap

See [docs/roadmap.md](docs/roadmap.md).

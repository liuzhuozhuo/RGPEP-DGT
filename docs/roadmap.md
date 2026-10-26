# RGPEP-DGT — roadmap

See [assessment.md](assessment.md) for the reasoning behind each item.

## Steps (in priority order)
1. **Safety net first.** ✅ *Done (2026-10-26), see "Status" below.* Add `pytest` tests that pin down known results, such as diagram counts for φ⁴ 1→1, 2→2 and 1→3 at orders 2–3, and Głazek's known O(g²) QCD terms. Fix bugs 1, 6, 7 and 8. Remove the committed `.pyc` files (`git rm --cached`), and strip notebook outputs (`nbstripout`).
2. **Packaging.** ✅ *Done (2026-10-26), see "Status" below.* Rename `src/` to `rgpep_dgt/` (or use the `src/rgpep_dgt/` layout), complete `pyproject.toml` with a build system and dependencies, and add `__init__` exports.
3. **New core, in parallel with the old one.** ✅ *Done (2026-10-26), see "Status" below.* Add the theory DSL, the graph-based `Diagram`, a generator for contractions, and isomorphism dedup. Validate it against `tests/wick_reference.py` and the literature tests, then switch over. The generator must enumerate each ordered product of initial terms once, with every Wick contraction allowed by the bracketing rule of [docs/literature.md](literature.md). That is the only way to fix the remaining overcounting at order ≥ 3.
4. **Physics features from `changes.txt`:** ✅ *Done (2026-10-26), see "Status" below.* kinetic-term / counterterm insertion (the commented-out blocks), a list of terms before contraction, correct counting and symmetry factors, and labelled in/out particles.
5. **Higher orders and performance.** ✅ *Done (2026-10-26), see "Status" below.* Prune unreachable branches, cache order-n results to disk (pickle or JSON), and optionally use multiprocessing across (A, B) pairs.
6. **Output and docs.** ✅ *Done (2026-10-26), see "Status" below.* Add TikZ export and an algebraic expression per diagram (operator string plus form-factor / energy-denominator structure). This is the step that makes the tool useful for actual RGPEP calculations. Also fill in the README (theory background, usage), CITATION.cff and docs, and add CI (GitHub Actions running pytest).

## Verification
- `pytest` passes with count tests for φ⁴ and the gluon theory at orders 1–3.
- The new and old engines agree on those cases, and any disagreements trace to the bugs listed above.
- The notebooks run top to bottom from a clean kernel (`jupyter nbconvert --execute`).
- Order-4/5 φ⁴ runs within a few hundred MB of memory (measure with `/usr/bin/time -v`).

## Status

### Step 1 (2026-10-26)
Fixed:
- **Bug 1:** `simplify.py`, wrong index when a point is the same end of two lines.
- **Bug 2:** the preallocated buffers with a wrong size estimate were replaced by lists. Peak memory for the test cases dropped from 118 MB to 76 MB, and `scipy` is no longer needed.
- **Bug 3:** `matches_process` checks every particle type with the same convention as the renderer. The final-order filter now actually runs: `max_order` was off by one.
- **Bug 4:** `make_connection` builds every combination of per-type pairings, so any number of types can be contracted at once.
- **Bug 5:** `diagram_signature` no longer depends on how points are numbered. Framework mode dedupes on points *and* lines.
- **Bugs 6–8:** `till_order == 1` works; `pipeline.py` has its own imports; `example.ipynb` unpacks 4 values; `represent_order_diagram` has defaults; `feynman` is only imported when drawing.
- **New:** every second-order product H₁·H₁ was generated twice, so all second-order counts were doubled. Products of a first-order term with a higher-order diagram on the left were missing for φ⁴ from third order on.
- **New:** framework mode contracted the same number of lines of every particle type, and dropped a type unless all four of its in/out numbers were non-zero. This was wrong for QCD: it missed the quark loop in the gluon self-energy and gave 8 instead of 0 for quark 1→1 at third order. φ⁴ output is unchanged.
- **Hygiene:** `.pyc` files untracked, notebook outputs stripped, `tests/` added (`python -m pytest`).

Still open:
- From third order on, counts are too large when a contraction pattern can be built through more than one bracketing. The diagram set is correct: it matches the reference and [GR15] Fig. 7. Tracked by `xfail` tests; fixed in step 3.
- Framework mode only uses first-order canonical terms, so products with G₀₂ (instantaneous terms) are missing in QCD. Fixed in step 3.
- No counterterms (mass, vertex) yet, cf. [GR15] Fig. 7 (f), (i), (j).

### Step 3 (2026-10-26)
New engine in `rgpep_dgt/engine/`, used by default (`calculate_diagrams(..., engine="new")`; `engine="legacy"` keeps the old code).
- **`theory.py`:** a theory is a list of `Term`s (vertices in order, legs per particle type, internal lines such as the instantaneous line). Terms are read automatically from the existing `rgpep_dgt/can_diagrams` files, so nothing was retyped.
- **`generate.py`:** every ordered product of terms is considered once. Contractions are enumerated as numbers of lines between pairs of vertices, and `wick_count` gives the number of Wick contractions for each. Patterns are kept only if they have an RGPEP bracketing. Products that cannot give the process are skipped early (leg-number balance, first/last factor legs, running totals).
- **`arrays.py`:** conversion to and from the array format, so the existing renderer and notebooks work unchanged.
- **Isomorphism:** no graph-isomorphism library was needed. Vertices are totally ordered by their position in the product, so labelling them by position gives a canonical form. The only remaining symmetry is relabelling external legs, which the count accounts for.
- **Results:** counts now agree with the brute-force reference (φ⁴ up to fourth order). Framework mode includes the instantaneous terms. The new engine is much faster: φ⁴ at sixth order takes 0.1 s with 47 MB peak, and QCD 1→1 at fourth order takes 0.2 s. Legacy needed 12 s for φ⁴ at fourth order and could not reach sixth.
- **Bracketings:** each diagram records its `bracketings`, needed later for the RGPEP coefficients (step 6).

Still open:
- No counterterms yet (mass, vertex), cf. [GR15] Fig. 7 (f), (i), (j). Adding them is now just adding `Term`s.
- The automatic drawing layout is basic: lines can overlap for some diagrams (step 6).
- Framework mode at seventh order still enumerates every contraction (~20 s for φ⁴ 2→2); it could stop at the first valid one (step 5).
- The legacy engine can be removed once the notebooks have been checked with the new one.

### Step 2 (2026-10-26)
- **Rename:** `src/` became `rgpep_dgt/` (history kept with `git mv`), and all imports, notebooks and docs were updated. `__init__.py` was added to `can_diagrams/` and `can_diagrams/qcd/`, which had none, so the theory files are included when installed.
- **`pyproject.toml`:** has a setuptools build system, dependencies (numpy, matplotlib), and optional extras `drawing` (feynman) and `test` (pytest). Installs with `pip install -e .`.
- **Exports:** `rgpep_dgt/__init__.py` exports `calculate_diagrams`, `represent_order_diagram`, `get_theory`, `generate_diagrams`, `term_products`, `Theory`, `Term` and `Diagram`. The notebooks import from the package.
- **README:** installation, usage, project structure, dependencies and tests are filled in. Motivation and theoretical background are still to be written.
- **Checked:** the wheel contains every subpackage, and the installed package runs from outside the repository. All tests pass and both notebooks run.

### Step 4 (2026-10-26)
- **Counterterms:** `get_theory(name, counterterms=True, max_order=n)` and `calculate_diagrams(..., counterterms=True)` add mass and coupling-constant counterterms where the theory has loop corrections (see [literature.md](literature.md)). With them, the gluon vertex at third order has all 10 diagrams of [GR15] Fig. 7. Counterterm vertices are part of the diagram key and are drawn as marked vertices.
- **Kinetic term:** read as the mass counterterm. H_f is not a vertex in RGPEP.
- **Counting and symmetry factors:** every diagram has an exact `weight`. φ⁴ terms carry 1/(k! l!), which reproduces the textbook symmetry factors.
- **List of terms before contraction:** `term_products` with `products_table` (step 6).
- **Labelled in/out particles:** `external_legs` numbers the external particles, outgoing first. The labels are used in expressions and drawings (step 6).

### Step 6 (2026-10-26)
- **`rgpep_dgt/engine/expressions.py`:** writes each diagram as a Hamiltonian term, `f_t [Σ B^(...)] weight (product of terms) -> a†1 a†2 a3`, with [G12]'s coefficient labels, in text or LaTeX. It also has the products table.
- **`rgpep_dgt/rendering/tikz.py`:**
  - TikZ-Feynman code for each diagram, with gluon, quark and instantaneous line styles, labelled external particles, crossed dots for counterterms and bent parallel lines;
  - `write_latex` writes a document with drawings and expressions, which compiles with pdflatex.
- **Project files:** README (counterterms, expressions, LaTeX), `CITATION.cff`, a GitHub Actions workflow that runs pytest, and a demo cell at the end of `example.ipynb`.

Still open:
- The automatic layout can cross lines in multi-type diagrams. A layered layout that orders vertices in y by their connections would help.
- Motivation and theoretical background in the README are yours to write.
- The coefficients B are given as labels. Evaluating them (the integrals of A over t) for given momenta would be the next step towards numbers.
- Step 5 (performance) and removing the legacy engine.

### Step 5 (2026-10-26)
Benchmarks on 16 cores; the results are identical to before these changes in every case:

| Case | Diagrams | Before step 5 | Now, 1 process | Now, 8 processes |
|---|---|---|---|---|
| φ⁴ 2→2, order 7 | 121,419 | 24.8 s | 11.3 s | 6.3 s |
| φ⁴ 1→1, order 8 | 58,701 | 23.4 s | 11.7 s | 5.1 s |
| φ⁴ 2→2, order 6 | 7,433 | 1.3 s | 0.6 s | |
| QCD quark → quark + gluon, order 5 | 953 | 2.6 s | 2.3 s | 1.3 s |

For comparison, the legacy engine needed 12 s for φ⁴ at fourth order.

- **Pruning:** the enumeration keeps running totals of free and "locked" outgoing legs, and stops a branch as soon as the remaining incoming legs cannot bring the external lines to the process. Infeasible products of terms are skipped before any work.
- **Cheaper bookkeeping:**
  - plain recursion with a callback instead of nested generators;
  - the Wick-count numerator is computed once per product;
  - weights are computed once per diagram instead of per contraction;
  - bracketing existence is a small table instead of memoised closures.
- **Memory:** `Diagram` uses slots, and identical tuples are shared between diagrams. φ⁴ 2→2 at order 7 went from 514 MB to 373 MB.
- **Parallel:** `generate_diagrams(..., workers=n)` (also in `term_products` and `calculate_diagrams`) splits the products of terms among processes; `workers=None` uses every CPU. Gains stop at about 2× around 8 processes, because the main process has to receive and merge every result. It only pays off for large orders.
- **Disk cache:** `cache=True` (or a directory) stores results in `~/.cache/rgpep_dgt`. The key includes the theory, the process and the engine source, so changing any of them recomputes. Unreadable files are recomputed.

Still open:
- In parallel runs, transferring results between processes is the bottleneck. Returning compact arrays instead of tuples would help if larger orders are needed.
- The legacy engine is still there for comparison and could be removed.

### Clean-up and drawings (2026-10-26)
- **Legacy engine:** moved to `legacy/` (outside the package, history kept), with its tests in `legacy/tests` (CI runs them separately). `rgpep_dgt` no longer contains or references it: `calculate_diagrams` has no `engine` option. The array helpers the package still needs are in `rgpep_dgt/core/array_format.py`, copied unchanged.
- **Drawings:** `rgpep_dgt/engine/layout.py` places the points so that lines do not cross and no point lies on a foreign line or too close to it. It measures distances and angles in the proportions actually drawn, and tries a few starting shapes. It is used by the notebook renderer and the LaTeX output; the old fix-ups (`rearrange_in_out_points`, `find_loops`) are no longer needed. Long expressions are broken into lines in the LaTeX document. `tests/test_layout.py` checks that there are no crossings in the main cases.
- **Drawings of products of terms (framework mode):** every term keeps its own short legs, as in the original code, so no optimisation is needed. Large diagrams get a shorter layout search, and only the cost terms that change are evaluated. A seventh-order diagram takes about 0.4 s to lay out, a typical one about 30 ms.
- **Notebooks:** `example.ipynb` was rewritten as a walk-through of the package: theories, diagrams, expressions, products of terms, QCD, counterterms, diagram objects, LaTeX and large orders. `phi4_test.ipynb` was removed: it only showed the framework mode for φ⁴ at seventh order, which drew 163 products and is now covered by a smaller example.
- **README:** updated for the new structure, the drawings and the notebook.

## Next: step 7, evaluating the RGPEP coefficients
See [plan_coefficients.md](plan_coefficients.md).
- **Decided:** closed formulas first. Each B^(...) is written in terms of the invariant-mass differences ℳ_ij and + momenta p_ij of the groups of factors, using Głazek's generator [H_f, H_Pt].
- **Sign convention:** checked on paper against the gluon self-energy of [GR15] Eq. (C7). That case is the first test.
- **Recommended:** numbers for given momenta come afterwards. Vertex functions and loop integrals are not in scope for now.

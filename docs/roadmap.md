# RGPEP-DGT — roadmap

See [assessment.md](assessment.md) for the reasoning behind each item.

## Steps (in priority order)
1. **Safety net first.** ✅ *Done (2026-10-26), see "Status" below.* Add `pytest` tests that pin down known results, such as diagram counts for φ⁴ 1→1, 2→2 and 1→3 at orders 2–3, and Głazek's known O(g²) QCD terms. Fix bugs 1, 6, 7 and 8. Remove the committed `.pyc` files (`git rm --cached`), and strip notebook outputs (`nbstripout`).
2. **Packaging.** ✅ *Done (2026-10-26), see "Status" below.* Rename `src/` to `rgpep_dgt/` (or use the `src/rgpep_dgt/` layout), complete `pyproject.toml` with a build system and dependencies, and add `__init__` exports.
3. **New core, in parallel with the old one.** ✅ *Done (2026-10-26), see "Status" below.* Add the theory DSL, the graph-based `Diagram`, a generator for contractions, and isomorphism dedup. Validate it against `tests/wick_reference.py` and the literature tests, then switch over. The generator must enumerate each ordered product of initial terms once, with every Wick contraction allowed by the bracketing rule of [docs/literature.md](literature.md). That is the only way to fix the remaining overcounting at order ≥ 3.
4. **Physics features from `changes.txt`:** kinetic-term / counterterm insertion (the commented-out blocks), a list of terms before contraction, correct counting and symmetry factors, and labelled in/out particles.
5. **Higher orders and performance.** Prune unreachable branches, cache order-n results to disk (pickle or JSON), and optionally use multiprocessing across (A, B) pairs.
6. **Output and docs.** Add TikZ export and an algebraic expression per diagram (operator string plus form-factor / energy-denominator structure). This is the step that makes the tool useful for actual RGPEP calculations. Also fill in the README (theory background, usage), CITATION.cff and docs, and add CI (GitHub Actions running pytest).

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

# RGPEP-DGT — roadmap

See [assessment.md](assessment.md) for the reasoning behind each item.

## Steps (in priority order)
1. **Safety net first.** ✅ *Done (2026-10-26), see "Status" below.* Add `pytest` tests that pin down known results, such as diagram counts for φ⁴ 1→1, 2→2 and 1→3 at orders 2–3, and Głazek's known O(g²) QCD terms. Fix bugs 1, 6, 7 and 8. Remove the committed `.pyc` files (`git rm --cached`), and strip notebook outputs (`nbstripout`).
2. **Packaging.** Rename `src/` to `rgpep_dgt/` (or use the `src/rgpep_dgt/` layout), complete `pyproject.toml` with a build system and dependencies, and add `__init__` exports.
3. **New core, in parallel with the old one.** Add the theory DSL, the graph-based `Diagram`, a generator for contractions, and isomorphism dedup. Validate it against `tests/wick_reference.py` and the literature tests, then switch over. The generator must enumerate each ordered product of initial terms once, with every Wick contraction allowed by the bracketing rule of [docs/literature.md](literature.md). That is the only way to fix the remaining overcounting at order ≥ 3.
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
- From third order on, counts are too large when a contraction pattern can be built through more than one bracketing. The diagram set is correct: it matches the reference and [GR15] Fig. 7. Tracked by `xfail` tests and fixed in step 3.
- Framework mode only uses first-order canonical terms, so products with G₀₂ (instantaneous terms) are missing in QCD.
- No counterterms (mass, vertex) yet, cf. [GR15] Fig. 7 (f), (i), (j).

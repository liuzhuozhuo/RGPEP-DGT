# RGPEP-DGT — code assessment

_Written 2026-10-26 against commit `ffdc97d`. Line numbers refer to that commit._

## What the repo does
It enumerates the operator-product "diagrams" that appear order by order in the perturbative solution of the RGPEP equation (Głazek's Renormalization Group Procedure for Effective Particles) and draws them.
- **Theories are hand-entered** as "canonical diagrams" (the interaction-Hamiltonian terms): `src/can_diagrams/{phi4, qcd/gluons, qcd/full_theory}/canonical_diagrams.py`. Each diagram is a `points` array (2D drawing coordinates) plus a `connections` array of shape `(n_particle_types, n_lines, 2)` holding 1-based vertex indices, padded with zeros.
- **Order-n diagrams** come from contracting the outgoing legs of one lower-order diagram with the incoming legs of another (`make_connection`, `combine_diagrams_order` in `src/transforms/concatenation.py`). The result is then simplified by collapsing pass-through vertices (`src/transforms/simplify.py`) and grouped, with multiplicities summed (`group_diagrams`, `src/search/comparison.py`).
- **Two modes** in `calculate_diagrams` (`src/core/pipeline.py`): `"complete"` produces explicit contracted diagrams, and `"framework"` produces only which canonical blocks combine, tracked through in/out leg counts.
- **Rendering** uses matplotlib plus the `feynman` package (`src/rendering/matplotlib_backend.py`).

## Concrete problems found
**Correctness bugs (worth fixing first)**
1. `src/transforms/simplify.py:38`: `elif pos[1, 1] == 1` should be `pos[1, 2] == 1`. As written, `prov` can be undefined, or left over from an earlier iteration, so the wrong lines get merged.
2. `src/transforms/concatenation.py:261-279`: in the size estimate, the inner loop uses `k` where it means `i`. It also shadows the outer `i`, and `binom(n1[j], i+1)` uses the diagram index. The estimate is then masked by a `4*…` fudge factor, so the buffers are preallocated far too large. This is the likely cause of the "not enough RAM" note in `changes.txt`.
3. `src/transforms/concatenation.py:287,302 vs 321,337`: the process filter compares `typeofproc[0][1]` against the in-legs in one branch and `typeofproc[0][0]` in another. It also only checks particle type 0, so multi-species processes are filtered incorrectly.
4. `src/transforms/concatenation.py:186-196` (mixing of particle types): the "triangular matrix" step only builds certain pairwise type mixtures. Contractions that use 3 or more species at once, such as gluon+quark+antiquark between the same two blocks, appear to be missed.
5. Deduplication is label-dependent. `diagram_signature` sorts edges but does not canonicalise vertex numbering, so isomorphic diagrams are counted separately. In framework mode, `is_array_in_list` dedupes on **drawing coordinates only** and ignores connectivity.
6. `pipeline.py` "complete" mode crashes with `UnboundLocalError` when `till_order == 1`. It also passes `max_order=till_order+1`, so the final-order process filter (`curr_order+1 == max_order`) probably never fires. That should be checked.
7. `pipeline.py` uses `np` and `in_out_connections` without importing them. They only resolve through `from src.rendering.matplotlib_backend import *`.
8. `example.ipynb` is stale. It unpacks 3 return values, but `calculate_diagrams` now returns 4, and `represent_order_diagram` now needs `all_in_out, mode, order`.

**Structural / hygiene issues**
- The package is named `src` (`from src.x import …`), so it can't be installed or imported from elsewhere. `pyproject.toml` has no `[build-system]` and no dependencies (numpy, scipy, matplotlib, feynman).
- `__pycache__/*.pyc` files are committed even though `.gitignore` excludes them, because they were added before the ignore rule.
- The notebooks (2.5 MB) are committed with their outputs.
- There are no tests. Correctness is checked only by looking at plots.
- Drawing coordinates are part of a diagram's identity. Layout and topology should be separate.
- Theory dispatch (`if theory == "phi4" … elif …`) is duplicated in `pipeline.py` and `concatenation.py`.
- About 500 lines of hand-typed QCD arrays (`full_theory/canonical_diagrams.py`) are easy to get wrong and hard to review.
- Large commented-out blocks (counterterms) remain, the README, CITATION.cff and docs are empty, and `changes.txt` is a Spanish TODO list.
- The fixed-size zero-padded ndarrays force preallocation, `trim_zeros` everywhere, and deep nested loops. That is the source of most of the complexity and the memory blow-up.

## Is there a better way? (recommended approach)
Yes. Keep the physics algorithm (contract out-legs of A with in-legs of B, then simplify and merge), but change the **data model**:

1. **Declarative theory definition.** A theory is a list of field types plus the H₁ (and higher, if needed) vertices, each given as (incoming legs by type, outgoing legs by type). For example, φ⁴ is `{(1→3), (3→1), (2→2)}` (plus 4→0 and 0→4 if needed), and QCD is the A³, A⁴, ψ̄Aψ and instantaneous terms. Canonical diagrams are generated from this, not typed in, and adding a theory becomes ~20 lines of data.
2. **Diagram = typed, ordered multigraph.** Vertices carry their position in the operator product, which matters because RGPEP products are ordered. Edges carry a field type, and external legs are explicit. Use `networkx.MultiDiGraph`, or a small `@dataclass`.
3. **Contraction as a generator.** For each species, enumerate partial bipartite matchings between A's out-legs and B's in-legs, then take `itertools.product` across species. This handles any number of species correctly, fixing bug 4, and uses no preallocation, fixing the RAM issue. Filter by the target process as early as possible, and prune branches whose external-leg count can no longer reach it.
4. **Canonical form for dedup and counting.** Use a WL hash (`networkx.weisfeiler_lehman_graph_hash` with node and edge attributes) as a bucket key, then confirm with `nx.is_isomorphic(node_match, edge_match)`. Vertex order stays a node attribute, so only physically equivalent relabelings merge. If symmetry factors are needed, take them from the automorphism group size (pynauty or networkx `GraphMatcher`), not from counting duplicates.
5. **Layout only at render time.** Compute x from vertex order and y from a simple layering. Also add a TikZ-Feynman export, which suits papers better than matplotlib PNGs.

Existing tools such as QGRAF, FeynArts and feyngen generate covariant Feynman diagrams, not ordered light-front Hamiltonian products, so they can't replace this tool. Their algorithms (canonical labelling, symmetry factors from automorphisms) carry over directly, though.

Reusable pieces to keep: `get_all_pairings` (`concatenation.py:73`) for the matching enumeration, `find_loops` / `equalize_x_spacing` / `rearrange_in_out_points` for layout, and the `feynman`-based renderer.


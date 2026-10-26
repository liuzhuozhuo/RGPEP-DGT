# Literature behind the tests

This page lists the results from the literature that the tests in `tests/` rely on, and how the expected numbers were derived.

## References

- **[G12]** S. D. Głazek, *Perturbative formulae for relativistic interactions of effective particles*, Acta Phys. Pol. B 43, 1843 (2012), [arXiv:1204.4760](https://arxiv.org/abs/1204.4760).
- **[GGS]** S. D. Głazek, M. Gómez-Rocha, K. Serafin, *RGPEP equation and its perturbative solution up to 4th order* (unpublished notes, 2016/2023).
- **[GR15]** M. Gómez-Rocha, S. D. Głazek, *Asymptotic freedom in the front-form Hamiltonian for quantum chromodynamics of gluons*, Phys. Rev. D 92, 065005 (2015), [arXiv:1505.06688](https://arxiv.org/abs/1505.06688).
- Wick's theorem for normal-ordered products: any QFT textbook, e.g. Peskin & Schroeder, Sec. 4.3.

## Rules used to generate diagrams

1. **Each ordered product of initial terms appears once.** The order-n operator structures are ordered products of the initial (t = 0) terms G₀₁, G₀₂, …, and each ordered product appears once ([G12] Eqs. (B.6)–(B.11); [GGS] Eqs. (10)–(12)). For example,
   - third order: G₀₁G₀₁G₀₁, plus G₀₁G₀₂ and G₀₂G₀₁, plus G₀₃
   - fourth order: G₀₁⁴, plus the three orderings of two G₀₁ and one G₀₂, plus G₀₂G₀₂, G₀₁G₀₃ and G₀₃G₀₁, plus G₀₄

   G₀₂ includes the instantaneous interactions and second-order counterterms. G₀₃ and G₀₄ are counterterms.
2. **Contractions follow Wick's theorem.** The terms are normal ordered, so in a product an annihilation operator of a factor is contracted only with a creation operator of a factor further to the right. The number of ways to contract k of n₁ annihilation operators with k of n₂ creation operators of the same species is C(n₁,k)·C(n₂,k)·k!. This is what `get_all_pairings` enumerates.
3. **At least one contraction between the factors of every product.** [G12], text below Eq. (18): "There are no disconnected terms in H_t, since the second term in Eq. (18) results from a commutator. The commutator also implies that one keeps only the terms that result from commuting at least one annihilation operator with one creation operator in the product H_It ax H_It xb."

   Together with the recursion G′ₙ = Σₖ A Gₖ Gₙ₋ₖ ([G12] Eq. (24)), a contraction pattern of an ordered product is kept if the factors can be split recursively into two contiguous groups with at least one contraction across every split. At third order this is the same as "connected". From fourth order on it is stricter: for example, contractions 1–3, 1–4 and 2–4 only are connected but are not produced.
4. **Different bracketings give one operator with summed coefficients.** A pattern reachable through several bracketings is one operator structure with a summed coefficient, e.g. [B⁽¹²⁴⁾ + B⁽¹³⁴⁾] G₀₃axyb in [G12] Eq. (31). It must be counted once.
5. **The front form has no vacuum terms.** Terms with only creation or only annihilation operators vanish because p⁺ > 0. So φ⁴ has only a†a†aa, a†a†a†a and a†aaa, and the gluon 3-vertex has only a†a†a and a†aa. This matches `src/can_diagrams`.

The **count** of a diagram is the number of Wick contractions, summed over ordered products, that give that diagram.

## Hand-derived values (second order)

Notation: a vertex is (out, in) = (creation, annihilation) operators, with A = a†a†a†a = (3,1), B = a†aaa = (1,3) and C = a†a†aa = (2,2). For an ordered pair (L, R) with k contractions: external in = L.in − k + R.in and external out = L.out + R.out − k.

| Process | Contributing products | Count |
|---|---|---|
| φ⁴ 1→1 | (B, A), k = 3 | 3! = **6** |
| φ⁴ 2→2 | (C, C), k = 2; (B, A), k = 2 | 2! = **2**; 3·3·2! = **18** |
| φ⁴ 1→3 | (C, A), k = 2 | 1·3·2! = **6** |
| gluon 1→1 (pure glue) | (a†aa)(a†a†a), k = 2 | **2** |
| gluon 2→2 (pure glue) | (a†a†a)(a†aa), k = 1; (a†aa)(a†a†a), k = 1; plus the canonical instantaneous terms as drawn in the repo | **1**, **4**, plus 1 and 4 |
| QCD gluon 1→1 | quark loop (a†db)(b†d†a); gluon loop | **1**, **2** |
| QCD quark 1→1 | (b†ab)(b†a†b) with the gluon and the quark contracted | **1** |

Third order, φ⁴ 1→1: only (B, C, A) contributes, with 2 lines B–C, 1 line B–A and 2 lines C–A. Count: 3·2 (B–C) · 3 (B–A) · 2 (C–A) = **36**.

Everything else is computed by the brute-force reference in `tests/wick_reference.py`, which implements rules 1–4 directly and agrees with all the values above.

## Published diagram set: third-order three-gluon vertex

[GR15] Fig. 7 shows the contributions (a)–(j) to the third-order a†a†a term. (f), (i) and (j) are counterterms. The other seven are:
- (a) the gluon triangle
- (b), (c) the triangle with one instantaneous side
- (d), (g) a gluon bubble on an external leg
- (e), (h) the same joined through an instantaneous line

`qcd_gluons`, 1→2, order 3 produces exactly these 7 topologies (`test_three_gluon_vertex_third_order_matches_gomez_rocha_glazek`). [GR15] Sec. II.A also explains why quartic gluon terms are drawn as two 3-vertices joined by an instantaneous line: they are regulated "as if built solely from vertices in which one quantum is changed to two or vice versa".

## Known disagreement

At third order and above the code finds the right set of diagrams, but counts some of them more than once (rule 4). Order 3 is a factor of 2; order 4 is a factor of up to 4. The test `test_phi4_counts_match_reference` is marked `xfail(strict=True)` until the generator is rewritten (see [roadmap.md](roadmap.md), step 3).

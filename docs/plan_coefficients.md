# Plan: evaluating the RGPEP coefficients

*Status: plan, not implemented yet (2026-10-26). This is step 7 of [roadmap.md](roadmap.md). The decisions are at the end: the first was made by the author, the others are recommendations.*

## Goal

Today every diagram is written as

```
f_t [Σ over bracketings of B_t^(...)] × weight × (product of initial terms) → external operators
```

with the coefficients B only as **labels** (see [literature.md](literature.md)). The goal is to replace the labels by their **closed formulas**: functions of t, of the + momenta and of the invariant-mass differences of the groups of particles involved. Numbers for given momenta come afterwards.

## The formulas

The references are those of [literature.md](literature.md): [G12] = Głazek 2012, [GGS] = the fourth-order note, [GR15] = Gómez-Rocha & Głazek 2015.

**Configurations.** In a product of n factors, the configurations 1, …, n+1 are numbered from left to right ([G12] App. B.1).

**Groups.** A group of consecutive factors spanning configurations i … j changes configuration j into i.
- **Outgoing legs:** its external outgoing lines and its lines to factors on its left.
- **Incoming legs:** its external incoming lines and its lines to factors on its right.
- **p_ij:** the total + momentum of its outgoing legs (equal to that of its incoming legs).
- **ℳ_ij = M²(outgoing legs) − M²(incoming legs):** the difference of the free invariant masses squared ([G12] Sec. 3; spectators do not count). With i < j, ℳ_ji = −ℳ_ij and p_ji = p_ij.

**Form factor.** f_t ab = exp(−t ℳ_ab²) ([G12] Eq. (20)), for the whole product (configurations 1 and n+1).

**Derivative factor.** For a split of configurations i … k at j:

  A_t ijk = (p_ij ℳ_ij + p_kj ℳ_kj) exp[−t (ℳ_ij² + ℳ_jk² − ℳ_ik²)] = (p_ij ℳ_ij − p_jk ℳ_jk) exp[−t (ℳ_ij² + ℳ_jk² − ℳ_ik²)]

([G12] Eq. (22), [GGS] Eq. (13)).

**Coefficients.** Integrals of A times the coefficients of the two groups ([G12] Eqs. (B.12)–(B.19)):
- B^(ijk, …) = ∫₀ᵗ dτ A_τ ijk B_τ(left group) B_τ(right group);
- B = 1 for a single factor;
- the labels are those the code already prints.

**Sign convention, checked against [GR15] Eq. (C7).** For the second-order gluon self-energy (Y₁₂ then Y₂₁, configurations 1 = one gluon, 2 = two gluons, 3 = one gluon):
- ℳ_12 = 0 − ℳ₂², ℳ_23 = ℳ₂² − 0 and ℳ_13 = 0, with ℳ₂² the invariant mass of the two gluons, and p_12 = p_23 = p⁺;
- so A = −2 p⁺ ℳ₂² e^(−2τℳ₂⁴), and

  B^(123,0) = −2 p⁺ ℳ₂² (1 − e^(−2tℳ₂⁴)) / (2ℳ₂⁴) = −p⁺ (1 − f_t²)/ℳ₂², with f_t = e^(−tℳ₂⁴).

This is exactly the coefficient of [Y₁₂₀ Y₂₁₀] in [GR15] Eq. (C7), so the convention above is the right one. It will be the first test.

## Design

1. **Group symbols** (`rgpep_dgt/engine/coefficients.py`)
   - For each node of each bracketing of a diagram: the configurations (i, j, k) and the legs of each group.
   - Symbols ℳ_ij and p_ij, written as in the papers.
   - Structural zeros: ℳ = 0 for a group with one incoming and one outgoing particle of the same type, as in a self-energy, since the masses are equal and momentum is conserved. Groups with the same legs share one symbol.
2. **Exponential polynomials** (same module)
   - Sums Σ c τᵏ e^(−λτ) with symbolic coefficients c and rates λ.
   - Exact products and integration from 0 to t. A vanishing rate gives powers of τ.
   - Rates that are not structurally zero are treated as different from each other and from 0. The formulas say so, as the papers do.
   - Written for this purpose rather than calling a general symbolic integrator, which returns case distinctions (Piecewise) for symbolic rates.
3. **Formulas**
   - `coefficient_formula(theory, diagram)` returns f_t Σ_trees B^(tree) × weight as a sympy expression.
   - `diagram_expression(..., formulas=True)` and `write_latex(..., formulas=True)` print it next to the labels.
   - sympy becomes an optional extra (`pip install -e ".[formulas]"`), like feynman for drawing.
4. **Numbers** (after the formulas)
   - Kinematics: masses and front-form momenta of the external lines, loop momenta, and momentum routing through the lines.
   - Invariant masses: M² = P⁺ Σᵢ (kᵢ⊥² + mᵢ²)/kᵢ⁺ − P⊥².
   - The formulas evaluated with them, with series expansions where rates nearly coincide.

## Checks against the literature

| Check | Expected | Source |
|---|---|---|
| Second-order gluon self-energy | B^(123,0) = −p⁺ (1 − f_t²)/ℳ₂² | [GR15] Eq. (C7) |
| Derivatives | dB/dt = A × B(left) × B(right) for every node, symbolically, for all orders up to 4 | [G12] (B.12)–(B.19) |
| t → 0 | Every B → 0, so H_t → H_0 (the initial condition) | [G12] Eqs. (29)–(32) |
| Third order | The coefficients B^(124,(234,0)) + B^(134,(123,0)) of G₀₃axyb, and B^(123,0) of the products with a second-order term | [G12] Eq. (31) |
| Hermiticity | A diagram and its mirror (reversed product, incoming ↔ outgoing) have the same formula after renaming configurations | H_t is hermitian |
| Numbers (step 4) | The formulas agree with nested numerical integration for random momenta | |

## Phases

1. **Closed formulas**
   - Design items 1–3.
   - Tests: the first five rows of the table.
   - The largest part of the work, self-contained.
2. **Numbers**
   - Design item 4.
   - Tests: the last row, and the two-body invariant mass M² = (k⊥² + m²)/(x(1 − x)) for equal masses.
3. **Vertex functions and loop integrals**
   - Not now; see decision 4.

## Decisions

1. **Closed formulas first** — *decided by the author.* Phase 1 above, numbers in phase 2.
2. **Generator** — *recommended:* only Głazek's generator G_t = [H_f, H_Pt].
   - It is [G12] Eq. (6), [GGS] and [GR15] Eq. (A5), and the code already uses its coefficient labels.
   - The other one, [GR15] Eq. (A4) from Głazek 2001, depends on the derivative of the Hamiltonian and is harder to use.
   - [GR15] shows that both give the same third-order coupling, so a second generator would add work without new information.
3. **First check** — *recommended:* the gluon self-energy of [GR15] Eq. (C7).
   - It is a closed formula already printed in the paper, and the code already produces the diagram.
   - The derivation above shows it fixes the sign convention.
   - Next: the third-order structure of [G12] Eq. (31), and the gluon-vertex products of [GR15] Eq. (C8).
4. **Vertex functions and loop integrals** — *recommended:* not now.
   - They depend on the theory (spin and colour sums such as Y₁₂₃, small-x regularisation), and are where the papers spend most of their effort.
   - Phases 1–2 already give the complete RGPEP coefficient of every operator structure. They also give a clean place to plug vertex functions in later.
   - A cheap step towards them: print each term's vertex function as a symbol (e.g. Y₁₂₀ for the gluon vertex) in the formulas, so the output reads like [GR15] Eq. (C7).
   - Decide after phase 1 whether to go further. The natural target would then be the gluon mass of [GR15] Eqs. (41)–(43).

## Risks

- **Symbolic size.** At fourth order a diagram has up to 5 bracketings with nested exponentials, so formulas can get long. Shared group symbols and collecting terms by exponential keep them readable. The LaTeX output already breaks long expressions.
- **Coinciding rates.** In special kinematics, rates that are generically different can coincide. The formulas then need limits, which only matters for numbers (phase 2), where series expansions handle it.
- **Loop momenta.** Choosing them consistently matters only for phase 3.

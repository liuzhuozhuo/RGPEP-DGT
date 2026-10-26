# Plan: evaluating the RGPEP coefficients

*Status: plan only, nothing implemented yet (2026-10-26). This is item 5 of the list of remaining work; in [roadmap.md](roadmap.md) it is step 7.*

## Goal

Today every diagram is written as

```
f_t [Σ over bracketings of B_t^(...)] × weight × (product of initial terms) → external operators
```

with the coefficients B only as **labels** (see [literature.md](literature.md)). The goal is to **evaluate** them as functions of t and of the momenta of the particles. This turns "which terms appear" into actual numbers and formulas that can be compared with published results.

The products of vertex functions (spin, colour, Y₁₂₃, …) and the loop integrals stay outside this step. They depend on the theory, and are the optional last phase.

## The formulas

The references are those of [literature.md](literature.md): [G12] = Głazek 2012, [GGS] = the fourth-order note, [GR15] = Gómez-Rocha & Głazek 2015.

**Form factor.** f_t ab = exp(−t ℳ_ab²) ([G12] Eq. (20)). ℳ_ab = M²_ab − M²_ba is the difference between the free invariant masses squared of the particles a term creates and the particles it annihilates. Spectators do not count.

**Derivative factor.** A_t axb = (p_ax ℳ_ax + p_bx ℳ_bx) exp[−t (ℳ_ax² + ℳ_xb² − ℳ_ab²)] ([G12] Eq. (22)). Here p_ax is the total + momentum of the particles active in the term that changes x into a. [GGS] Eq. (13) writes the same thing as [ℳ_ax p_ax + ℳ_bx p_bx] f_t⁻¹ab f_t ax f_t bx.

**Coefficients.** Nested integrals over τ from 0 to t, e.g.
- B^(123,0) = ∫ A_axb;
- B^(124,(234,0)) = ∫ A_axb B^(123,0)_xyb;
- B^(134,(123,0)) = ∫ A_ayb B^(123,0)_axy;

and so on up to (B.19) ([G12] Eqs. (B.12)–(B.19)).

**In terms of the code.** A bracketing tree node splits a group of factors [lo, hi) into L = [lo, m) and R = [m, hi), so it is a product L·R:
- **Legs of a group.** A group's outgoing legs are its external outgoing lines and its lines to factors on its left. Its incoming legs are its external incoming lines and its lines to factors on its right.
- **For each group G:** p_G is the + momentum of its outgoing legs (equal to that of its incoming legs), and ℳ_G = M²(outgoing legs) − M²(incoming legs).
- **The integrand at the node:** A = (p_L ℳ_L − p_R ℳ_R) exp[−τ (ℳ_L² + ℳ_R² − ℳ_{L∪R}²)]. The minus sign comes from ℳ_bx = −ℳ_xb and has to be checked against [G12] Eq. (18).
- **The coefficient at the node:** B_node(t) = ∫₀ᵗ A(τ) B_L(τ) B_R(τ) dτ, with B = 1 for a single factor.

Every B is a sum of terms c · τᵏ · e^(−λτ), so all the integrals have a closed form. Equal or vanishing rates λ, as in self-energies where ℳ_ab = 0, give powers of τ.

## Design

1. **Kinematics** (`rgpep_dgt/engine/kinematics.py`)
   - Masses for the particle types.
   - Front-form momenta (p⁺, p⊥) for the external lines, and loop momenta for the independent cycles of the diagram.
   - Momentum routing: every line's momentum as a linear combination of external and loop momenta, solved from momentum conservation at the vertices.
   - Free invariant mass of a set of on-shell particles: M² = P⁺ Σᵢ (kᵢ⊥² + mᵢ²)/kᵢ⁺ − P⊥².
2. **Groups** (in the same module)
   - For each node of each bracketing: the legs of L, R and L∪R, and from them p and ℳ.
3. **Exponential polynomials** (`rgpep_dgt/engine/exponential.py`)
   - A small exact class for Σ c τᵏ e^(−λτ): products and integration from 0 to t, with care for λ → 0 (expm1, series), since there can be cancellations.
4. **Coefficients** (`rgpep_dgt/engine/coefficients.py`)
   - `coefficient(theory, diagram, kinematics, t)` returns f_t ab Σ_trees B^(tree) × weight as a number.
   - `coefficient_function(...)` returns the exponential polynomial in t.
5. **Formulas**
   - Optional: the same computation with sympy symbols for the ℳ's and p's, giving the coefficients in closed form as LaTeX for the document of `write_latex`. sympy would be an optional extra, like feynman.
6. **Vertex functions and loop integrals** (optional, theory-specific)
   - The product of vertex functions and the integration over loop momenta.
   - Scalar theories first (φ³, φ⁴), then gluons with colour and polarisation.

## Checks against the literature

| Check | Expected | Source |
|---|---|---|
| B^(123,0) closed form | Agrees with numerical quadrature of A for random momenta | [G12] (B.12) |
| Second-order gluon self-energy | B^(123,0) = −p⁺ (1 − f_t²)/ℳ₂², with ℳ₂² the invariant mass of the two-gluon state | [GR15] Eq. (C7) |
| Nested coefficients | Closed forms of (B.13)–(B.19) agree with nested numerical quadrature | [G12] App. B |
| t → 0 | Every B → 0, so H_t → H_0 (the initial condition) | [G12] Eq. (29)–(32) |
| Hermiticity | A diagram and its mirror (reversed product, incoming ↔ outgoing) have equal coefficients for real momenta | H_t is hermitian |
| Second-order gluon mass, after phase 6 | Eq. (42) with the splitting function P_GG(x) of Eq. (43) | [GR15] Eqs. (41)–(43) |
| Running coupling, long term | The third-order vertex functions γ(a) … γ(i) of App. C.3 and the asymptotic-freedom coefficient | [GR15] App. C.3, D |

## Phases

1. **Kinematics and groups.** Momentum routing; invariant masses of groups.
   - Tests: momentum conservation, and the two-body formula M² = (k⊥² + m²)/(x(1 − x)) for equal masses.
2. **Numerical coefficients.** Exponential polynomials, `coefficient`.
   - Tests: the first five rows of the table.
3. **Formulas.** Symbolic coefficients and LaTeX output, with sympy optional.
4. **Vertex functions and loops.** Scalar theory first, then the gluon mass of [GR15] Eq. (42).
   - Larger and theory-specific. Worth deciding after phases 1–3.

Phases 1 and 2 are the core and are self-contained. Phase 3 is mostly output work. Phase 4 is a project of its own.

## Questions to settle before starting

1. **Numbers or formulas first?** Phase 2 (numbers for given momenta) or phase 3 (closed formulas in terms of ℳ and p)?
2. **Which generator?** [G12] Eq. (22) and [GR15] Eqs. (A4)/(A5) differ in the factors A. [GR15] states that both give the same third-order coupling. The code should probably support both, with [G12] as the default.
3. **Which first physics target?** The gluon mass term (closest to the existing tests), or a scalar theory (simpler, no spin or colour)?
4. **Is phase 4 in scope at all**, or does the tool stop at the operator structure with its coefficient functions?

## Risks

- **Sign conventions.** ℳ_ax = −ℳ_xa, and which group counts as "left". These have to be pinned down with the [GR15] (C7) check before going further.
- **Numerical cancellations.** When rates nearly coincide, differences of exponentials need series expansions.
- **Loop momenta.** Choosing them consistently for diagrams with several loops matters only for phase 4. Phases 1–3 work with the momentum routing as given.

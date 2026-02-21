---
phase: 2
plan: 2
wave: 1
---

# Plan 2.2: Taylor Expansion of Time Evolution Operator

## Objective
Compute the truncated Taylor series $e^{-iHt} \approx \sum_{k=0}^K \frac{(-itH)^k}{k!}$ using Qiskit's `SparsePauliOp` algebra, returning the classical coefficients $\alpha_j$ and the individual Pauli unitaries.

## Context
- `.gsd/SPEC.md`
- `.gsd/ROADMAP.md`
- `src/pauli_decomposition.py` (from Plan 2.1)

## Tasks

<task type="auto">
  <name>Taylor Series Classical Expansion</name>
  <files>
    - `src/taylor_expansion.py`
    - `tests/test_taylor_expansion.py`
  </files>
  <action>
    - Create `src/taylor_expansion.py`.
    - Implement a function `compute_time_evolution_taylor(H_pauli: SparsePauliOp, t: float, K: int) -> SparsePauliOp` that takes the `SparsePauliOp` representation of the Hamiltonian.
    - Calculate the matrix exponential using the truncated Taylor series up to order $K$:
      $U = I + (-it)H + \frac{(-it)^2}{2!}H^2 + \dots + \frac{(-it)^K}{K!}H^K$
    - Leverage Qiskit's overloaded `+` and `@` (or `dot`) operators for `SparsePauliOp` to perform the matrix algebra and group combinations automatically.
    - Since terms can accumulate negligible weights, apply a `.simplify()` or custom truncation to drop terms with absolute coefficients `< 1e-10`.
    - Note that LCU requires positive real coefficients $\alpha_j$ for the PREPARE block, and the complex phases $e^{i\theta_j}$ must be handled. For this phase, just extract the magnitude `abs(c)` as $\alpha_j$ and keep the complex phase associated for later (or return them as tuples). For now, returning the correctly calculated `SparsePauliOp` of the Taylor approximation is sufficient.
    - Create `tests/test_taylor_expansion.py` to verify the logic.
    - In the test, create a 1-qubit dummy Hamiltonian (e.g., $H = X + Z$), expand it, convert the resulting `SparsePauliOp` back to a dense matrix, and compare it against `scipy.linalg.expm(-1j * t * H.to_matrix())` to ensure the Taylor approximation converges.
  </action>
  <verify>source .venv/bin/activate && python -m unittest tests/test_taylor_expansion.py</verify>
  <done>The script correctly constructs the truncated series, and the test proves convergence towards the exact matrix exponential.</done>
</task>

## Success Criteria
- [ ] `src/taylor_expansion.py` successfully computes the Taylor series using Pauli algebra.
- [ ] The theoretical dense matrix of the truncated series approaches the exact `expm` result.
- [ ] Unit tests pass.

---
phase: 2
plan: 1
wave: 1
---

# Plan 2.1: Hamiltonian Pauli Decomposition

## Objective
Convert the discretized 1D Harmonic Oscillator Hamiltonian matrix into a sum of Pauli strings using Qiskit. This prepares the mathematical representation required for the LCU algorithm.

## Context
- `.gsd/SPEC.md`
- `.gsd/ROADMAP.md`
- `src/hamiltonian.py`

## Tasks

<task type="auto">
  <name>Pauli Decomposition Implementation</name>
  <files>
    - `src/pauli_decomposition.py`
    - `tests/test_pauli_decomposition.py`
  </files>
  <action>
    - Create `src/pauli_decomposition.py`.
    - Implement a function `decompose_hamiltonian_to_paulis(H_matrix: np.ndarray) -> SparsePauliOp` that takes the Hermitian Hamiltonian matrix and uses Qiskit's `SparsePauliOp.from_operator` (or equivalent method) to decompose it into Pauli strings.
    - Since matrices might have negligible near-zero coefficients, apply a truncation/filter to remove Pauli terms with coefficient magnitudes below `1e-10` to keep the decomposition sparse and efficient.
    - Create `tests/test_pauli_decomposition.py` to test this function.
    - The test should generate a small Harmonic Oscillator Hamiltonian (e.g., $q=2$), decompose it, reconstruct the matrix explicitly from the Pauli strings, and assert it matches the original matrix using `np.testing.assert_allclose`.
  </action>
  <verify>source .venv/bin/activate && python -m unittest tests/test_pauli_decomposition.py</verify>
  <done>The script runs without error and the reconstructed matrix exactly matches the generated discrete Hamiltonian.</done>
</task>

## Success Criteria
- [ ] `src/pauli_decomposition.py` successfully converts an $N \times N$ matrix to a Qiskit `SparsePauliOp`.
- [ ] Negligible terms are filtered out.
- [ ] Unit tests pass, proving the sum of the returned Pauli strings equals the original matrix.

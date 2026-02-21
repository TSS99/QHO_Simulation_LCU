---
phase: 3
plan: 1
wave: 1
---

# Plan 3.1: LCU PREPARE Block (Ancilla Initialization)

## Objective
Build the Qiskit quantum circuit subroutine that initializes the ancilla register. This block (often called PREPARE or $V$) encodes the normalized coefficients $\sqrt{\alpha_j / \sum \alpha_i}$ of the Taylor expansion into the probability amplitudes of the ancilla states.

## Context
- `.gsd/SPEC.md`
- `.gsd/ROADMAP.md`
- Needs output from `src/taylor_expansion.py` (Phase 2).

## Tasks

<task type="auto">
  <name>PREPARE Circuit Generation</name>
  <files>
    - `src/lcu_circuits.py`
    - `tests/test_lcu_circuits.py`
  </files>
  <action>
    - Create `src/lcu_circuits.py`.
    - Implement `build_prepare_circuit(coefficients: np.ndarray) -> QuantumCircuit`.
    - `coefficients` refers to the absolute values of the Taylor series terms (the $\alpha_j$).
    - Calculate the number of ancilla qubits required: $n_a = \lceil \log_2(M) \rceil$, where $M$ is the number of coefficients.
    - Pad the `coefficients` array with zeros up to $2^{n_a}$ if $M$ is not a power of 2.
    - Normalize the padded coefficients array so that the sum of the *values* squares equals 1 (i.e. amplitudes mathematically represent $\sqrt{\alpha_j / ||\alpha||_1}$).
    - Create a Qiskit `QuantumCircuit` with $n_a$ qubits.
    - Use Qiskit's built-in state preparation instruction (e.g. `circuit.initialize(amplitudes, qubits)` or `circuit.prepare_state`) to load these amplitudes.
    - Export this as a gate or instruction for later composition.
    - Create `tests/test_lcu_circuits.py`.
    - Write a test `test_build_prepare_circuit` that provides dummy coefficients (e.g., `[1.0, 2.0, 1.0]`), builds the circuit, simulates it using Qiskit's `Statevector`, and asserts the resulting probabilities match the normalized coefficients $\alpha_j / \sum \alpha_i$.
  </action>
  <verify>source .venv/bin/activate && python -m unittest tests/test_lcu_circuits.py</verify>
  <done>The script correctly initializes the ancilla register matching the theoretical coefficient distribution.</done>
</task>

## Success Criteria
- [ ] `src/lcu_circuits.py` successfully returns a valid Qiskit `QuantumCircuit` for the PREPARE block.
- [ ] Extraneous states are appropriately zero-padded.
- [ ] Unit tests pass, proving amplitude encoding correctness.

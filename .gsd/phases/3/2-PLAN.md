---
phase: 3
plan: 2
wave: 1
---

# Plan 3.2: LCU SELECT Block (Multiplexing)

## Objective
Construct the multiplexed target unitaries (the SELECT or $U$ block). This block applies each Pauli string $U_j$ from the Taylor expansion to the target state, conditioned on the ancilla register being in the computational basis state $|j\rangle$.

## Context
- `.gsd/SPEC.md`
- `.gsd/ROADMAP.md`
- `src/taylor_expansion.py`

## Tasks

<task type="auto">
  <name>SELECT Circuit Generation</name>
  <files>
    - `src/lcu_circuits.py`
    - `tests/test_lcu_circuits.py`
  </files>
  <action>
    - Open `src/lcu_circuits.py`.
    - Implement `build_select_circuit(paulis: list[str], complex_phases: list[complex]) -> QuantumCircuit`.
    - The `paulis` argument is a list of Pauli string descriptors (e.g. `['IX', 'ZI']`) corresponding to the Taylor series terms.
    - `complex_phases` represents the complex angle $\theta_j$ from each coefficient $c = |c| e^{i\theta_j}$, which we must apply as a global phase modifier.
    - Calculate the number of ancillas needed: $n_a = \lceil \log_2(len(paulis)) \rceil$.
    - The target register size $n_t$ is the length of a Pauli string.
    - Create a Qiskit `QuantumCircuit` with `ancilla_reg` ($n_a$ qubits) and `target_reg` ($n_t$ qubits).
    - Loop through each Pauli string:
        - For string index $j$, apply anti-controls (X gates on the ancillas where the bit in $j$'s binary representation is 0) to "activate" the state $|j\rangle$.
        - Apply the multi-controlled Pauli string to the target register. E.g., if the string has an 'X' on target 0, apply a multi-controlled X with all ancillas as controls pointing to target 0.
        - Apply a multi-controlled phase gate to apply the complex phase $e^{i\theta_j}$. (This might involve decomposing into basic instructions or building a custom diagonal unitary, but for small system statevector simulation, a multi-controlled `Rz` or `U1/P` structure can handle this).
        - Revert the anti-controls (X gates on 0-bits) to restore the ancilla basis state.
    - Export this circuit.
    - Add test `test_build_select_circuit` to `tests/test_lcu_circuits.py` verifying that applying the SELECT block on ancilla state $|j\rangle$ correctly applies the equivalent $U_j$ isolated transformation to a dummy target state.
  </action>
  <verify>source .venv/bin/activate && python -m unittest tests/test_lcu_circuits.py</verify>
  <done>The test executes correctly, validating that the SELECT operation properly multiplexes the given Pauli unitaries governed by the ancilla state.</done>
</task>

## Success Criteria
- [ ] `src/lcu_circuits.py` successfully generates the SELECT quantum circuit.
- [ ] Ancilla multiplexing operates exactly.
- [ ] Multi-controlled operations compile effectively in Qiskit.
- [ ] Unit tests pass, proving correctness of the conditional logic.

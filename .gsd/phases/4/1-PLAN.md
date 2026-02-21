---
phase: 4
plan: 1
wave: 1
---

# Plan 4.1: Full LCU Simulation Pipeline and Sandbox

## Objective
Assemble the components from Phases 1-3 into an executable pipeline. The simulation will build the target Hamiltonian, construct the PREPARE and SELECT LCU subroutines based on a Taylor expansion of $e^{-iHt}$, execute the composed circuit on Qiskit's local statevector simulator, and verify the physical measurement statistics against the theoretically exact state evolution.

## Context
- `.gsd/SPEC.md`
- `.gsd/ROADMAP.md`
- `src/hamiltonian.py`
- `src/pauli_decomposition.py`
- `src/taylor_expansion.py`
- `src/lcu_circuits.py`

## Tasks

<task type="auto">
  <name>End-to-End Simulation Script</name>
  <files>
    - `src/simulate_lcu.py`
    - `tests/test_simulation.py`
  </files>
  <action>
    - Create `src/simulate_lcu.py`.
    - Implement a `run_lcu_simulation(q: int, mass: float, omega: float, max_x: float, t: float, K: int)` orchestration function.
    - Inside the orchestrator:
        1. Generate the dense Hamiltonian `H` for $N=2^q$.
        2. Execute `decompose_hamiltonian_to_paulis` to get the `SparsePauliOp`.
        3. Execute `compute_time_evolution_taylor` up to order $K$ to get the Taylor approximated unitary strings.
        4. Extract the absolute magnitudes $\alpha_j$ and complex phases $e^{i\theta_j}$ from the Taylor output.
        5. Build the PREPARE circuit ($V$) using $\alpha_j$.
        6. Build the SELECT circuit ($U$) using the Pauli strings and complex phases.
        7. Construct the full LCU circuit: 
            - Apply PREPARE ($V$) on the ancillas initialized to $|0\rangle^{\otimes n_a}$.
            - Apply SELECT ($U$) controlled by ancillas acting on the target register.
            - Apply $V^\dagger$ (the inverse of the PREPARE circuit) to the ancillas.
        8. Given an initial state on the targets (e.g., $|0\rangle^{\otimes q}$, or a discretized Gaussian representing the physical ground state, but for simplicity we can use the computational zero state or an explicit generated state from the theoretical `H`), simulate the whole circuit using `Statevector(circuit)`.
        9. Post-select the result: The LCU algorithm isolates the successful time evolution on the branch where the ancillas are measured in the $|0\rangle^{\otimes n_a}$ state. Programmatically trace out or filter the statevector to find the probability of success (chance of measuring all 0s in ancilla) and the normalized target state if successful.
    - Create `tests/test_simulation.py` that runs a small end-to-end sandbox test (e.g., $q=2$, $t=0.5$, $K=5$). 
    - The test must compare the post-selected, normalized simulated target statevector mathematically against the exact statevector derived from `scipy.linalg.expm(-1j * t * H) @ initial_state`.
  </action>
  <verify>source .venv/bin/activate && python -m unittest tests/test_simulation.py</verify>
  <done>The end-to-end sandbox runs cleanly, and the post-selected states closely match theoretical predictions, validating the entire LCU approach.</done>
</task>

## Success Criteria
- [ ] Fully connected LCU circuitry consisting of $V$, $U$, and $V^\dagger$ is generated.
- [ ] Final post-selected simulation state mathematically aligns with classical $e^{-iHt}$ numerical approximations.
- [ ] End-to-end sandbox behaves optimally without framework errors.

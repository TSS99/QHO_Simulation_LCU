# REQUIREMENTS.md

## Format
| ID | Requirement | Source | Status |
|----|-------------|--------|--------|
| REQ-01 | **Automated Environment Setup:** Create and activate a Python `venv` to isolate the project environment and install required dependencies like `qiskit` and `numpy`. | Constraints | Pending |
| REQ-02 | **Spatial Discretization:** The system can construct a discrete version of the 1D Harmonic Oscillator Hamiltonian (Position, Momentum, Kinetic, and Potential components) given the number of qubits ($q$, such that dimension $N=2^q$). | SEC Goal 1 | Pending |
| REQ-03 | **Pauli Decomposition:** The discrete Hamiltonian matrix is correctly decomposed into a sum of Pauli strings (coefficients and matrices) capable of being inputted to the LCU expansion. | SEC Goal 2 | Pending |
| REQ-04 | **Taylor Expansion of Time Evolution:** The time evolution operator $e^{-iHt}$ is approximated by a generic truncated Taylor expansion to a user-specified order $K$, and terms are rewritten back into sums of unitary operators. | SEC Goal 3 | Pending |
| REQ-05 | **Qiskit LCU Circuit Generation:** A Qiskit parameterised circuit must be explicitly constructed to encode the coefficients as probability amplitudes on an ancilla register, and multiplex the component unitary operators effectively onto the target register. | SEC Goal 3 | Pending |
| REQ-06 | **Statevector Simulation:** The entire circuit executes successfully on a Qiskit statevector local simulator. | SEC Goal 4 | Pending |
| REQ-07 | **Validation Sandbox:** Users are able to invoke an end-to-end script providing $q$, $t$, and $K$, which builds the Hamiltonian, creates the LCU time-evolution, runs it, and generates results inside the local environment. | SEC Goal 4 | Pending |

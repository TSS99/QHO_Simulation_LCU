# ROADMAP.md

> **Current Phase**: Not started
> **Milestone**: v1.0

## Must-Haves (from SPEC)
- [ ] Calculate discretized position, momentum, kinetic, and potential operators for the 1D Harmonic Oscillator given an arbitrary parameter $q$ (qubits) using Numpy.
- [ ] Convert arbitrary $2^q \times 2^q$ Hamiltonian matrices into sums of standard Pauli Operators ($I,X,Y,Z$) with coefficients.
- [ ] Extend the decomposed Hamiltonian into a truncated Taylor series of order $K$, yielding an aggregate sum of unitary operators representing $e^{-iHt}$.
- [ ] Programmatically map these generated coefficients to initialize the state of an ancilla register of size $\lceil \log_2(\text{number of unitaries}) \rceil$.
- [ ] Design the SELECT subroutine (multiplexed Pauli strings) for applying the component terms of the Taylor series to the target register.
- [ ] Generate the statevector measurement protocol isolating the correct ancilla outcomes.

## Phases

### Phase 1: Environment and Discretization
**Status**: ✅ Complete
**Objective**: Set up a local Python virtual environment, pull Qiskit/Numpy, and build robust functions that discretize the 1D Harmonic Oscillator (position and momentum spaces) and return the resulting Hamiltonian matrix for $N=2^q$.
**Requirements**: REQ-01, REQ-02

### Phase 2: Pauli Translation and Taylor Expansion
**Status**: ⬜ Not Started
**Objective**: Expand the discrete Hamiltonian into the Pauli basis, and implement a purely mathematical (classical) truncation of the $e^{-iHt}$ Taylor series to obtain classical variables representing a large list of coefficients $\alpha_j$ and individual Pauli strings $U_j$.
**Requirements**: REQ-03, REQ-04

### Phase 3: LCU Qiskit Implementation (Ancilla + Multiplexing)
**Status**: ⬜ Not Started
**Objective**: Build a Qiskit quantum circuit that accepts the $\alpha_j$ and $U_j$ lists from Phase 2. Implement the PREPARE block (mapping $\alpha_j$ to ancilla amplitudes) and the SELECT block (multiplexing target Pauli unitaries conditioned on the ancilla register).
**Requirements**: REQ-05

### Phase 4: Full Statevector Simulation and Verification Sandbox
**Status**: ⬜ Not Started
**Objective**: Combine the components from prior phases into an executable monolithic simulation script that takes inputs ($q, t, K$). Run the circuit on the Qiskit local statevector simulator, analyze the density/probabilities, and visually report execution results against theoretically predicted statevectors.
**Requirements**: REQ-06, REQ-07

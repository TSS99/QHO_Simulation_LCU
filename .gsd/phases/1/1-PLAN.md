---
phase: 1
plan: 1
wave: 1
---

# Plan 1.1: Project Environment and Core Discretization Setup

## Objective
Set up the Python virtual environment, install necessary dependencies (Qiskit, Numpy, Scipy), and create the core matrix representations for the position ($X$) and momentum ($P$) operators for the discretised 1D space according to the number of qubits ($q$).

## Context
- `.gsd/SPEC.md`
- `.gsd/REQUIREMENTS.md`
- No existing source code.
- We require isolated dependencies acting within a local `venv`.

## Tasks

<task type="auto">
  <name>Environment Setup</name>
  <files>
    - `requirements.txt`
    - `setup_env.sh`
  </files>
  <action>
    - Create a `requirements.txt` file specifying `qiskit`, `numpy`, `scipy`.
    - Create a bash script `setup_env.sh` that initializes a python `venv` in the local directory (named `.venv`), activates it, and installs the requirements.
    - Make the script executable.
  </action>
  <verify>bash setup_env.sh && source .venv/bin/activate && python -c "import qiskit, numpy, scipy; print('Environment Ready')"</verify>
  <done>The script runs without error, the `.venv` directory exists, and test import succeeds.</done>
</task>

<task type="auto">
  <name>Discretized Operator Generation</name>
  <files>
    - `src/hamiltonian.py`
    - `tests/test_hamiltonian.py`
  </files>
  <action>
    - Create `src/hamiltonian.py` to contain logic for 1D spatial discretization.
    - Implement a class or functions that take the number of qubits $q$ (dimension $N=2^q$) and maximum spatial extent $L/2$.
    - Build generating functions for the position operator matrix $X$ (diagonal in position basis).
    - Build generating functions for the momentum operator matrix $P$ (using Fourier transforms or finite difference methods over the discretized space).
    - Create `tests/test_hamiltonian.py` using `unittest` to verify matrix dimensions are $2^q \times 2^q$ and matrices are Hermitian.
  </action>
  <verify>source .venv/bin/activate && python -m unittest tests/test_hamiltonian.py</verify>
  <done>The tests pass, verifying $X$ and $P$ matrix construction.</done>
</task>

## Success Criteria
- [ ] `setup_env.sh` successfully provisions the isolated environment.
- [ ] `src/hamiltonian.py` correctly generates $X$ and $P$ matrices.
- [ ] `tests/test_hamiltonian.py` executes successfully.

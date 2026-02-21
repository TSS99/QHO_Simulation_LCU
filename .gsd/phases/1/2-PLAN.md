---
phase: 1
plan: 2
wave: 1
---

# Plan 1.2: Kinetic and Potential Energy Operator Generation

## Objective
Use the basic position ($X$) and momentum ($P$) discretized matrices to construct the full 1D Harmonic Oscillator Hamiltonian ($H = \frac{P^2}{2m} + \frac{1}{2}m\omega^2 X^2$).

## Context
- `.gsd/SPEC.md`
- `.gsd/REQUIREMENTS.md`
- Depends on `src/hamiltonian.py` from Plan 1.1

## Tasks

<task type="auto">
  <name>Hamiltonian Matrix Generation</name>
  <files>
    - `src/hamiltonian.py`
    - `tests/test_hamiltonian.py`
  </files>
  <action>
    - Add a function `generate_harmonic_oscillator_hamiltonian(q, mass, omega, max_x)` to `src/hamiltonian.py`.
    - This function will call the internal $X$ and $P$ generating functions.
    - Implement the logic: $H = \frac{P^2}{2 \times mass} + 0.5 \times mass \times omega^2 \times X^2$.
    - Add tests to `tests/test_hamiltonian.py` to assert that $H$ is a valid size, is Hermitian, and has expected non-negative eigenvalues (ground state $> 0$).
  </action>
  <verify>source .venv/bin/activate && python -m unittest tests/test_hamiltonian.py</verify>
  <done>The tests pass successfully.</done>
</task>

## Success Criteria
- [ ] Matrix representations for $H$ are correctly generated.
- [ ] The full state `hamiltonian.py` is tested and verified.

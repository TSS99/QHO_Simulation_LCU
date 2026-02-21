# Simulating the 1D Quantum Harmonic Oscillator using LCU (Qiskit)

This repository simulates real-time evolution of a particle in a 1D harmonic potential using a Linear Combination of Unitaries (LCU) construction in Qiskit.


---

## Table of Contents

1. [Introduction](#introduction)
2. [Physics. The 1D Quantum Harmonic Oscillator](#physics-the-1d-quantum-harmonic-oscillator)
3. [Discretization and Hamiltonian Construction](#discretization-and-hamiltonian-construction)
4. [Mathematics. Linear Combination of Unitaries (LCU)](#mathematics-linear-combination-of-unitaries-lcu)
5. [Algorithmic Optimizations](#algorithmic-optimizations)
6. [Repository Structure](#repository-structure)
7. [Installation and Setup](#installation-and-setup)
8. [How to Run](#how-to-run)
9. [Outputs and Validation](#outputs-and-validation)

---

## Introduction

For a time-independent Hamiltonian $H$, Schrödinger time evolution is:

$$
|\psi(t)\rangle = e^{-iHt}\,|\psi(0)\rangle.
$$

Directly computing $e^{-iHt}$ is expensive on classical hardware as the dimension grows. This project builds a quantum-circuit approximation of $e^{-iHt}$ using an LCU construction derived from a truncated Taylor series.

---

## Physics. The 1D Quantum Harmonic Oscillator

The 1D quantum harmonic oscillator Hamiltonian is:

$$
H = \frac{p^2}{2m} + \frac{1}{2}m\omega^2 x^2.
$$

- $m$ is the particle mass
- $\omega$ is the oscillator frequency
- $x$ and $p$ are the position and momentum operators

---

## Discretization and Hamiltonian Construction

### Spatial grid

We choose bounds $[-x_{\max}, x_{\max}]$ and discretize into $N = 2^q$ points, where $q$ is the number of target qubits. The discretized position basis has dimension $N$.

Let the grid spacing be $\Delta x$ and grid points be $x_j$ for $j=0,1,\dots,N-1$.

### Potential energy

The potential is diagonal in the position basis:

$$
V(x) = \frac{1}{2}m\omega^2 x^2,
\qquad
V_{jj} = \frac{1}{2}m\omega^2 x_j^2.
$$

### Kinetic energy (finite difference Laplacian)

Using the standard second-order central finite difference:

$$
\frac{d^2\psi}{dx^2}(x_j) \approx \frac{\psi(x_{j+1}) - 2\psi(x_j) + \psi(x_{j-1})}{\Delta x^2},
$$

the kinetic operator (with $\hbar=1$ unless kept explicit) is:

$$
T = -\frac{1}{2m}\frac{d^2}{dx^2}.
$$

So the discretized Hamiltonian is:

$$
H = T + V.
$$

Implementation note:
- `src/hamiltonian.py` builds $T$, $V$, and $H$.

### Initial state

A convenient starting point is a displaced Gaussian wavepacket:

$$
\psi(x) \propto \exp\!\left(-\frac{\alpha}{2}(x-x_0)^2\right).
$$

This produces a clean oscillation in the position-space probability distribution under time evolution.

---

## Mathematics. Linear Combination of Unitaries (LCU)

We want to approximate the evolution operator:

$$
U(t) = e^{-iHt}.
$$

### Step 1. Pauli decomposition

On $q$ qubits, we expand the discretized Hamiltonian in the Pauli basis:

$$
H = \sum_{\ell} c_{\ell} P_{\ell},
\qquad
P_{\ell} \in \{I, X, Y, Z\}^{\otimes q}.
$$

Implementation note:
- `src/pauli_decomposition.py` produces the list of $(c_{\ell}, P_{\ell})$ terms.

### Step 2. Truncated Taylor series

We use a Taylor expansion truncated at order $K$:

$$
e^{-iHt} \approx \sum_{k=0}^{K}\frac{(-it)^k}{k!}H^k.
$$

After expanding products and collecting terms, we rewrite the approximation as an LCU:

$$
e^{-iHt} \approx \sum_{j=0}^{M-1}\alpha_j U_j,
$$

where each $U_j$ is unitary (often a Pauli string up to a phase) and $\alpha_j$ are complex coefficients.

Implementation note:
- `src/taylor_expansion.py` constructs the truncated expansion and returns $(\alpha_j, U_j)$.

### Step 3. The LCU circuit

Let $M$ be the number of terms and let the ancilla size be:

$$
n_a = \left\lceil \log_2 M \right\rceil.
$$

Define the 1-norm weight:

$$
\lambda = \sum_{j=0}^{M-1} |\alpha_j|.
$$

The standard LCU construction uses three blocks.

**PREPARE.** Prepare the ancilla superposition weighted by $|\alpha_j|$:

$$
V|0\rangle^{\otimes n_a} = \sum_{j=0}^{M-1}\sqrt{\frac{|\alpha_j|}{\lambda}}\,|j\rangle.
$$

**SELECT.** Apply the correct unitary controlled on the ancilla index:

$$
\mathrm{SELECT} = \sum_{j=0}^{M-1} |j\rangle\langle j| \otimes U_j.
$$

Any complex phase in $\alpha_j$ is implemented as a phase factor inside $U_j$.

**UNCOMPUTE.** Apply $V^\dagger$ to uncompute the ancilla.

The full block is:

$$
W = (V^\dagger \otimes I)\,\mathrm{SELECT}\,(V \otimes I).
$$

### Post-selection

Measuring the ancilla in the state $|0\rangle^{\otimes n_a}$ projects the target register onto the desired approximation (up to normalization). The success probability can decrease as $t$ increases or as the truncation parameters change.

Implementation notes:
- `src/lcu_circuits.py` builds PREPARE and SELECT
- `src/simulate_lcu.py` orchestrates the full workflow

---

## Algorithmic Optimizations

1. Sparse finite-difference structure  
   The finite-difference kinetic operator is banded. Exploiting sparsity helps control term growth and circuit depth.

2. Time slicing

Instead of approximating $e^{-iHt}$ for the full $t$ at once, use slices with

$$
dt = \frac{t}{s},
$$

where $s$ is the number of time steps, then compose the evolution across slices.

3. Identity shifting  
   If $H$ contains an identity component $c_I I$, shift it out:
   $H' = H - c_I I$.
   Then:
   $e^{-iHt} = e^{-ic_I t}\,e^{-iH't}$.
   The global phase $e^{-ic_I t}$ does not affect measurement probabilities.

4. Gray-code ordering for SELECT (optional)  
   Gray-code ordering reduces control-state bit flips in practical SELECT constructions.

5. Oblivious amplitude amplification (optional)  
   To amplify post-selection success, wrap the LCU block with an OAA iterator such as:

$$
\mathcal{Q} = -W S_0 W^\dagger S_0,
$$

where $S_0$ reflects about the ancilla-all-zero subspace.

---

## Repository Structure

```text
├── main.py
├── requirements.txt
├── src/
│   ├── hamiltonian.py
│   ├── pauli_decomposition.py
│   ├── taylor_expansion.py
│   ├── lcu_circuits.py
│   └── simulate_lcu.py
└── tests/

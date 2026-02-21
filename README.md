# Simulating the 1D Quantum Harmonic Oscillator using LCU (Qiskit)

This repository is an end-to-end framework to simulate real-time evolution of a particle in a 1D harmonic potential using a Linear Combination of Unitaries (LCU) construction in Qiskit.

Math in this README is written using GitHub’s native LaTeX support. Inline math uses `$...$` and display math uses `$$...$$`.

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

Quantum dynamics is governed by Schrödinger time evolution. For a time-independent Hamiltonian $H$, the state evolves as:

$$
\lvert \psi(t)\rangle = e^{-iHt}\,\lvert \psi(0)\rangle.
$$

On a classical computer, evaluating $e^{-iHt}$ becomes expensive as the Hilbert space dimension grows. This project builds a quantum circuit that approximates $e^{-iHt}$ using an LCU construction derived from a truncated Taylor series, so the evolution can be executed on a quantum processor (or simulated via Qiskit backends).

---

## Physics. The 1D Quantum Harmonic Oscillator

The 1D quantum harmonic oscillator (QHO) Hamiltonian is:

$$
H = \frac{p^2}{2m} + \frac{1}{2}m\omega^2 x^2.
$$

- $m$ is the particle mass.
- $\omega$ is the oscillator frequency.
- $x$ and $p$ are the position and momentum operators.

---

## Discretization and Hamiltonian Construction

### Spatial grid

We choose bounds $[-x_{\max}, x_{\max}]$ and discretize into $N = 2^q$ points, where $q$ is the number of target qubits and $N$ is the Hilbert-space dimension of the discretized position basis.

Let the grid spacing be $\Delta x$ and grid points be $x_j$ for $j = 0,1,\dots,N-1$.

### Potential energy operator

The potential is diagonal in the position basis:

$$
V(x) = \frac{1}{2}m\omega^2 x^2,
\qquad
V_{jj} = \frac{1}{2}m\omega^2 x_j^2.
$$

### Kinetic energy operator (finite difference)

Using the standard second-order central finite difference for the second derivative:

$$
\frac{d^2 \psi}{dx^2}(x_j) \approx
\frac{\psi(x_{j+1}) - 2\psi(x_j) + \psi(x_{j-1})}{\Delta x^2},
$$

the kinetic operator (with $\hbar = 1$ by default unless you keep it explicit) becomes a sparse banded matrix:

$$
T = -\frac{1}{2m}\frac{d^2}{dx^2}.
$$

So the full discretized Hamiltonian is:

$$
H = T + V.
$$

Implementation detail:
- `src/hamiltonian.py` generates $T$, $V$, and $H$ from $(q, x_{\max}, m, \omega)$.

### Initial state

A convenient starting point is a displaced Gaussian wavepacket, close to the ground state shape but shifted by $x_0$:

$$
\psi(x) \propto \exp\!\left(-\frac{\alpha}{2}(x-x_0)^2\right).
$$

This produces clear bounded oscillations in position-space probability under time evolution.

---

## Mathematics. Linear Combination of Unitaries (LCU)

We want to implement (or approximate) $U(t) = e^{-iHt}$.

### Step 1. Pauli decomposition

On $q$ qubits, any $N \times N$ operator can be expanded in the Pauli basis:

$$
H = \sum_{\ell} c_{\ell} P_{\ell},
\qquad
P_{\ell} \in \{I,X,Y,Z\}^{\otimes q}.
$$

Implementation detail:
- `src/pauli_decomposition.py` produces a list of $(c_{\ell}, P_{\ell})$ terms.

### Step 2. Truncated Taylor series

We approximate the exponential using a Taylor expansion truncated at order $K$:

$$
e^{-iHt} \approx \sum_{k=0}^{K}\frac{(-it)^k}{k!}H^k.
$$

After expanding the products $H^k$ (symbolically as products of Pauli strings, or numerically with controlled truncation rules), the approximation can be expressed as an LCU form:

$$
e^{-iHt} \approx \sum_{j=0}^{M-1}\alpha_j U_j,
$$

where each $U_j$ is unitary (typically a Pauli string up to a phase) and $\alpha_j$ are complex coefficients.

Implementation detail:
- `src/taylor_expansion.py` constructs the truncated series and returns the $(\alpha_j, U_j)$ list.

### Step 3. LCU circuit structure

Let $M$ be the number of unitaries in the final list, and let $n_a = \lceil \log_2 M \rceil$ be the number of ancilla qubits needed to index them.

Define:

$$
\lambda = \sum_{j=0}^{M-1} \lvert \alpha_j \rvert.
$$

The standard LCU pattern uses three blocks.

1) PREPARE. Create an ancilla superposition weighted by $\lvert \alpha_j \rvert$:

$$
V\lvert 0\rangle^{\otimes n_a}
=
\sum_{j=0}^{M-1}\sqrt{\frac{\lvert \alpha_j \rvert}{\lambda}}\,\lvert j\rangle.
$$

2) SELECT. Apply the right unitary controlled on the ancilla state:

$$
\operatorname{SELECT}
=
\sum_{j=0}^{M-1}\lvert j\rangle\langle j\rvert \otimes U_j.
$$

(Any complex phase in $\alpha_j$ is implemented inside $U_j$ as a phase factor.)

3) Uncompute. Apply $V^\dagger$ to return ancillas to $\lvert 0\rangle^{\otimes n_a}$ when the post-selection succeeds.

Overall block:

$$
W = (V^\dagger \otimes I)\,\operatorname{SELECT}\,(V \otimes I).
$$

### Post-selection

Measuring ancillas as $\lvert 0\rangle^{\otimes n_a}$ projects the target register onto a state proportional to the desired approximation. The success probability is related to $\lambda$ and the norm of the target-state component, so it can decrease as $t$ grows or as $K$ changes.

Implementation detail:
- `src/lcu_circuits.py` builds PREPARE and SELECT.
- `src/simulate_lcu.py` orchestrates the full routine and measurement post-processing.

---

## Algorithmic Optimizations

This project is structured to keep circuit depth and term growth under control.

1. Sparse finite-difference Hamiltonian  
   The central finite-difference kinetic operator produces a banded (sparse) matrix. Sparsity is exploited during decomposition and truncation so the term list does not blow up as quickly as it would for dense constructions.

2. Time slicing (segmented evolution)  
   Instead of approximating $e^{-iHt}$ for a large $t$ directly, the simulation uses steps of size $dt = t/\text{time\_steps}$ and composes the evolution across slices. This helps keep the Taylor truncation stable and reduces per-slice circuit depth.

3. Identity shifting  
   If the decomposition includes an identity component $c_I I$, you can shift it out:
   $H' = H - c_I I$.
   Then:
   $e^{-iHt} = e^{-ic_I t}\,e^{-iH't}$.
   The global phase factor $e^{-ic_I t}$ is physically irrelevant for probabilities, and removing it can reduce unnecessary bookkeeping.

4. Gray-code ordering for SELECT  
   Ordering the index states in Gray-code order reduces the number of basis-state bit flips needed when implementing multiplexed controls, which can reduce depth in practical SELECT constructions.

5. Oblivious amplitude amplification (optional)  
   To boost post-selection success, the code supports an OAA loop around $W$. One common form is:

$$
\mathcal{Q} = -W\,S_0\,W^\dagger\,S_0,
$$

where $S_0$ reflects about the ancilla-all-zero subspace.

---

## Repository Structure

```text
├── main.py                    # Entry point. Configuration and execution
├── requirements.txt           # Dependencies (Qiskit, NumPy, etc.)
├── src/
│   ├── hamiltonian.py         # Finite-difference QHO Hamiltonian builder
│   ├── pauli_decomposition.py # Pauli basis expansion utilities
│   ├── taylor_expansion.py    # Truncated Taylor expansion logic
│   ├── lcu_circuits.py        # PREPARE/SELECT construction (incl. Gray-code helpers)
│   └── simulate_lcu.py        # High-level LCU simulation orchestration
└── tests/                     # Unit tests for operators and circuit sanity checks

# Simulating the 1D Quantum Harmonic Oscillator using LCU

Welcome to the 1D Quantum Harmonic Oscillator LCU Simulation project. This repository contains a complete, end-to-end Python framework using Qiskit to simulate the time evolution of a particle in a 1D Harmonic potential using the Linear Combination of Unitaries (LCU) algorithm.

This project is designed to be highly modular, mathematically rigorous, and fully optimized for deeper exploration into quantum simulation algorithms.

---

## Table of Contents
1. [Introduction](#introduction)
2. [The Physics: 1D Quantum Harmonic Oscillator](#the-physics-1d-quantum-harmonic-oscillator)
3. [The Mathematics: Linear Combination of Unitaries (LCU)](#the-mathematics-linear-combination-of-unitaries-lcu)
4. [Advanced Algorithmic Optimizations](#advanced-algorithmic-optimizations)
5. [Repository Structure](#repository-structure)
6. [Installation & Setup](#installation--setup)
7. [How to Run](#how-to-run)

---

## Introduction
Simulating quantum mechanics is one of the most promising applications of quantum computers. The Schrödinger Equation dictates how a quantum state evolves over time:
$$ |\psi(t)\rangle = e^{-iHt} |\psi(0)\rangle $$
Where $H$ is the Hamiltonian matrix of the system. For large systems, calculating the matrix exponential $e^{-iHt}$ on a classical computer is incredibly difficult because the matrix size grows exponentially. 

This project tackles this by translating the classical Hamiltonian into a Quantum Circuit using the Linear Combination of Unitaries scheme, allowing the time evolution to be simulated on quantum processors.

---

## The Physics: 1D Quantum Harmonic Oscillator
The Harmonic Oscillator describes a particle trapped in a parabolic potential well (like a mass on a spring).

Its Hamiltonian is given by:
$$ H = \frac{p^2}{2m} + \frac{1}{2}m\omega^2x^2 $$

### Spatial Discretization
To simulate this on a computer, space must be discretized. We define physical bounds from $-x_{max}$ to $x_{max}$ and divide space into $N = 2^q$ discrete points, where $q$ is the number of target qubits. 

- The **Potential Energy** $\frac{1}{2}m\omega^2x^2$ becomes a diagonal matrix.
- The **Kinetic Energy** $\frac{p^2}{2m}$ is approximated using a centralized finite-difference discretised Laplacian over the discrete spatial grid to preserve operator sparsity natively.

*(See `src/hamiltonian.py` for the finite-difference matrix generation).*

Furthermore, the simulation calculates distributions dynamically. It initializes from an offset analytical Gaussian ground state $e^{-\alpha(x - x_0)^2/2}$ to elegantly display bounded oscillation over time limits.

---

## The Mathematics: Linear Combination of Unitaries (LCU)

To simulate the exact time-evolution operator $U(t) = e^{-iHt}$, we break the problem down into several structured mathematical steps.

### Step 1: Pauli Decomposition
Quantum computers can only natively execute operations representing Pauli Matrices ($I, X, Y, Z$). Therefore, our first step is to decompose the $N \times N$ discrete Hamiltonian matrix into a sum of Pauli strings:
$$ H = \sum_{j} c_j P_j $$
Where $P_j \in \{I, X, Y, Z\}^{\otimes q}$.

### Step 2: Taylor Series Expansion
We approximate the continuous time-evolution exponential using a truncated Taylor series of order $K$:
$$ e^{-iHt} \approx \sum_{k=0}^{K} \frac{(-it)^k}{k!} H^k $$

By substituting our Pauli expansion of $H$ into the Taylor series and multiplying out the matrices, we acquire a massive list of new, complex coefficients $\alpha_j$ corresponding to unitary Pauli operations $U_j$:
$$ e^{-iHt} \approx \sum_{j=0}^{M-1} \alpha_j U_j $$

*(See `src/taylor_expansion.py`)*

### Step 3: The LCU Circuit
The LCU algorithm allows us to apply a "sum" of unitaries. It does this by using Ancilla (helper) Qubits.

Let $n_a = \lceil \log_2(M) \rceil$ be the number of ancilla qubits needed to index $M$ terms.

1. **PREPARE ($V$)**: Create a circuit on the ancilla register that prepares the amplitudes based on the coefficients.
   $$ V |0\rangle^{\otimes n_a} = \frac{1}{\sqrt{||\alpha||_1}} \sum_{j=0}^{M-1} \sqrt{\alpha_j} |j\rangle $$
2. **SELECT ($U$)**: Apply the corresponding Pauli unitary $U_j$ to the target register, *controlled* by the state $|j\rangle$ in the ancilla register.
   $$ \text{SELECT} = \sum_{j=0}^{M-1} |j\rangle\langle j| \otimes U_j $$
3. **Inverse PREPARE ($V^\dagger$)**: Uncompute the ancilla register.

**Post-Selection:**
The final target state is successfully simulated *if and only if* measuring the ancilla register yields the $|0...0\rangle$ state.

---

## Advanced Algorithmic Optimizations
This repository implements several high-end optimizations designed to keep quantum circuits scalable, narrow, and structurally immune to numerical error scaling.

1. **Tridiagonal Finite-Difference Spatial Constraints:**
   Instead of using dense Discrete Fourier Transforms to evaluate Kinematics (which causes Pauli strings to branch outwards exponentially $O(4^q)$), space is evaluated using a Central Finite-Difference formula yielding a Tridiagonal constraint. This collapses the resultant Pauli decomposition scale to $O(poly(q))$, allowing arbitrary scaling of the qubit boundary arrays without catastrophic circuit depth bloat.

2. **Iterative Time Slicing (Trotterization-like):**
   Instead of calculating the Taylor sequence for the full time $t$, we divide the simulation into segments $dt = t / \text{steps}$. The LCU loop is applied iteratively, preventing Taylor Series blow-ups and dramatically bounding the depth requirements per module.
   
3. **Hamiltonian Identity Shifting:**
   Instead of natively evolving the dense $H$, we analytically strip the Identity matrix scalar out of the Hamiltonian before calculation ($H' = H - c_I I$). This exponentially trims the Taylor series Pauli permutations mapping logic branches prior to execution, massively decreasing complexity.
   
4. **Gray-Coded SELECT Matrices:**
   A naive `SELECT` multiplexer requires $O(M \log M)$ bit-flip (`X`) gates to isolate classical control states. By ordering coefficients into a native **Gray Code** sequence $(j \oplus (j \gg 1))$, adjacent states only ever differ by a single bit. This explicitly reduces required $X$ gates down to $O(M)$, vastly truncating execution depths.

5. **Oblivious Amplitude Amplification (OAA):**
   Because LCU relies on post-selection, the success probability drops for long evolution times. This repository dynamically supports a full state Grover Iterator Loop: 
   $$ G = -W S_0 W^\dagger S_0 $$
   Which safely amplifies probability mappings without relying on observable endpoints.

---

## Repository Structure

```text
├── main.py                    # Master Execution & Config Hub
├── requirements.txt           # Python dependencies (Qiskit, Numpy, etc.)
├── src/
│   ├── hamiltonian.py         # Physics QHO Finite-Difference matrix generator
│   ├── pauli_decomposition.py # Translates matrices into Pauli parameters
│   ├── taylor_expansion.py    # Math framework mapping truncated Taylor approximations
│   ├── lcu_circuits.py        # Qiskit subroutines mapping Gray sequences
│   └── simulate_lcu.py        # Sub-layer algorithm orchestrator 
└── tests/                     # Unit testing suites for physics and unitary validation
```

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd 1D_Systems_LCU
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Requirements:**
   ```bash
   pip install -r requirements.txt
   ```

---

## How to Run

1. Open `main.py` in your development environment.
2. Edit the physics properties under `Simulation Input Parameters`:
   ```python
   q = 4                 # Number of qubits (Target Resolution)
   mass = 1.0            # Particle mass
   omega = 5.0           # Oscillator frequency
   t = 0.5               # Evolution time
   time_steps = 10       # Iteration slices
   num_amplification_steps = 2  # Grover Amplitude Boosts
   ```
3. Execute the script from the command line:
   ```bash
   python main.py
   ```

### Output Validation
The simulation dynamically charts results across two primary output artifacts:
1. `lcu_circuit_diagram.png` - Plots the modularized fault-tolerant block algorithms mapping your specific Taylor parameter constraints.
2. `probability_distribution.png` - Maps the mathematical probability arrays $|\psi|^2$ displaying continuous visual confirmation that the custom quantum LCU outputs mathematically overlay the standard matrix exact density equations tracking particle bounds symmetrically spanning space bounds over $t$ iterations.

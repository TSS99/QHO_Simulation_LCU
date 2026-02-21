# Simulating the 1D Quantum Harmonic Oscillator using LCU

Welcome to the **1D Quantum Harmonic Oscillator LCU Simulation** project! This repository contains a complete, end-to-end Python framework using **Qiskit** to simulate the time evolution of a particle in a 1D Harmonic potential using the **Linear Combination of Unitaries (LCU)** algorithm.

This project is designed to be highly modular, mathematically rigorous, and fully optimized for deeper exploration into quantum simulation algorithms.

---

## 📖 Table of Contents
1. [Introduction](#introduction)
2. [The Physics: 1D Quantum Harmonic Oscillator](#the-physics-1d-quantum-harmonic-oscillator)
3. [The Mathematics: Linear Combination of Unitaries (LCU)](#the-mathematics-linear-combination-of-unitaries-lcu)
4. [Advanced Algorithmic Optimizations](#advanced-algorithmic-optimizations)
5. [Repository Structure](#repository-structure)
6. [Installation & Setup](#installation--setup)
7. [How to Run](#how-to-run)

---

## 🌟 Introduction
Simulating quantum mechanics is one of the most promising applications of quantum computers. The **Schrödinger Equation** dictates how a quantum state evolves over time:
$$ |\psi(t)\rangle = e^{-iHt} |\psi(0)\rangle $$
Where $H$ is the Hamiltonian matrix of the system. For large systems, calculating the matrix exponential $e^{-iHt}$ on a classical computer is incredibly difficult because the matrix size grows exponentially. 

This project tackles this by translating the classical Hamiltonian into a **Quantum Circuit** using the Linear Combination of Unitaries scheme, allowing the time evolution to be simulated on quantum processors!

---

## ⚛️ The Physics: 1D Quantum Harmonic Oscillator
The Harmonic Oscillator is the "hello world" of quantum physics—describing a particle trapped in a parabolic potential well (like a mass on a spring).

Its Hamiltonian is given by:
$$ H = \frac{p^2}{2m} + \frac{1}{2}m\omega^2x^2 $$

### Spatial Discretization
To simulate this on a computer, space must be discretized. We define physical bounds from $-x_{max}$ to $x_{max}$ and divide space into $N = 2^q$ discrete points, where $q$ is the number of target **qubits**. 

- The **Potential Energy** $\frac{1}{2}m\omega^2x^2$ becomes a diagonal matrix.
- The **Kinetic Energy** $\frac{p^2}{2m}$ is approximated using a centralized finite-difference method over the discrete spatial grid.

*(See `src/hamiltonian.py` for the finite-difference matrix generation!)*

---

## 🧮 The Mathematics: Linear Combination of Unitaries (LCU)

To simulate the exact time-evolution operator $U(t) = e^{-iHt}$, we break the problem down into several structured mathematical steps.

### Step 1: Pauli Decomposition
Quantum computers can only natively execute operations representing **Pauli Matrices** ($I, X, Y, Z$). Therefore, our first step is to decompose the $N \times N$ discrete Hamiltonian matrix into a sum of Pauli strings:
$$ H = \sum_{j} c_j P_j $$
Where $P_j \in \{I, X, Y, Z\}^{\otimes q}$.

### Step 2: Taylor Series Expansion
We approximate the continuous time-evolution exponential using a truncated Taylor series of order $K$:
$$ e^{-iHt} \approx \sum_{k=0}^{K} \frac{(-it)^k}{k!} H^k $$

By substituting our Pauli expansion of $H$ into the Taylor series and multiplying out the matrices, we acquire a massive list of new, complex coefficients $\alpha_j$ corresponding to unitary Pauli operations $U_j$:
$$ e^{-iHt} \approx \sum_{j=0}^{M-1} \alpha_j U_j $$

*(See `src/taylor_expansion.py`)*

### Step 3: The LCU Circuit
The LCU algorithm allows us to apply a "sum" of unitaries (which is normally not allowed in quantum mechanics since sums of unitaries are not strictly unitary themselves). It does this by using **Ancilla (helper) Qubits**.

Let $n_a = \lceil \log_2(M) \rceil$ be the number of ancilla qubits needed to index $M$ terms.

1. **PREPARE ($V$)**: Create a circuit on the ancilla register that prepares the amplitudes based on the coefficients.
   $$ V |0\rangle^{\otimes n_a} = \frac{1}{\sqrt{||\alpha||_1}} \sum_{j=0}^{M-1} \sqrt{\alpha_j} |j\rangle $$
2. **SELECT ($U$)**: Apply the corresponding Pauli unitary $U_j$ to the target register, *controlled* by the state $|j\rangle$ in the ancilla register.
   $$ \text{SELECT} = \sum_{j=0}^{M-1} |j\rangle\langle j| \otimes U_j $$
3. **Inverse PREPARE ($V^\dagger$)**: Uncompute the ancilla register.

**Post-Selection:**
The final target state is successfully simulated *if and only if* measuring the ancilla register yields the $|0...0\rangle$ state!

---

## 🚀 Advanced Algorithmic Optimizations
This repository implements several high-end optimizations designed to keep quantum circuits scalable, narrow, and less prone to numerical error drift.

1. **Iterative Time Slicing (Trotterization-like):**
   Instead of calculating the Taylor sequence for the full time $t$, we divide the simulation into tiny segments $dt = t / \text{steps}$. The LCU loop is applied iteratively, preventing Taylor Series blow-ups and dramatically reducing required qubit depths.
   
2. **Hamiltonian Identity Shifting:**
   Instead of evolving the full $H$, we analytically strip the large Identity matrix scalar out of the Hamiltonian before calculation ($H' = H - c_I I$). This exponentially reduces the Taylor Series $L_1$ norm constraint, bounding the system to yield $1.000$ perfect physical fidelities!
   
3. **Gray-Coded SELECT Matrices:**
   A naive `SELECT` multiplexer requires $O(M \log M)$ bit-flip (`X`) gates to isolate classical states. By ordering our mathematical coefficients into a native **Gray Code** sequence ($j \oplus (j \gg 1)$), our adjacent states only ever differ by a single bit. This explicitly reduces required $X$ gates down to $O(M)$, vastly reducing compiler times and time complexity!

4. **Oblivious Amplitude Amplification (OAA):**
   Because LCU relies on post-selection (measuring $|0\rangle$), the success probability drops for long evolution times. This repository supports an optional full state **Grover Iterator Loop**: 
   $$ G = -W S_0 W^\dagger S_0 $$
   Which deterministically amplifies the success probability without needing to know the target state!

---

## 📂 Repository Structure

```text
├── main.py                    # ⚡️ Master Execution & Config Hub
├── requirements.txt           # Python dependencies (Qiskit, Numpy, etc.)
├── src/
│   ├── hamiltonian.py         # Physics QHO Matrix discretization
│   ├── pauli_decomposition.py # Translates H -> Pauli strings
│   ├── taylor_expansion.py    # Math engine to calculate truncated e^{-iHt}
│   ├── lcu_circuits.py        # Qiskit PREPARE, SELECT, and Gray-code logic
│   └── simulate_lcu.py        # Central orchestrator integrating all LCU blocks
└── tests/                     # Unit testing suites for verified execution
```

---

## 💻 Installation & Setup

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

## ▶️ How to Run

1. Open `main.py` in your favorite editor.
2. Edit the physics properties under `--- Simulation Input Parameters ---`:
   ```python
   q = 2                 # Number of qubits (Target Resolution)
   mass = 1.0            # Particle mass
   omega = 1.0           # Oscillator frequency
   t = 0.5               # Evolution time
   time_steps = 10       # Iteration slices
   num_amplification_steps = 10  # Grover Amplitude Boosts
   ```
3. Execute the script!
   ```bash
   python main.py
   ```

### Output Example:
The script natively compares the LCU Qiskit simulation against Scipy's exact dense algorithmic solver to prove success!
```text
Success probability of state projection: 0.8718
State Fidelity: 0.999973

--- Circuit Metrics ---
Unrolled Circuit Depth: 27895
Total Number of Operations: 35360
Gate Counts breakdown:
 - RZ: 16687
 - CX: 13676
...
```
*(The diagram of the block circuit will be automatically saved to your folder as `lcu_circuit_diagram.png`!)*

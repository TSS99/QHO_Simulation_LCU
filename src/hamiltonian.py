import numpy as np

def generate_position_operator(q: int, max_x: float) -> np.ndarray:
    """
    Generates the position operator X in the discretized position basis.
    
    Args:
        q: Number of qubits (dimension N = 2**q).
        max_x: The spatial extent L/2, meaning the space goes from -max_x to max_x.
        
    Returns:
        Diagonal NumPy array (N x N) representing the position operator.
    """
    N = 2**q
    L = 2 * max_x
    dx = L / N
    
    # Position grid from -L/2 to L/2 (exclusive of the very last point to match periodic/DFT bounds)
    x_grid = -max_x + np.arange(N) * dx
    
    # Position operator is diagonal in position basis
    X = np.diag(x_grid)
    return X


def generate_momentum_operator(q: int, max_x: float) -> np.ndarray:
    """
    Generates the momentum operator P in the discretized position basis using DFT.
    
    Args:
        q: Number of qubits (dimension N = 2**q).
        max_x: The spatial extent L/2, meaning the space goes from -max_x to max_x.
        
    Returns:
        Hermitian NumPy array (N x N) representing the momentum operator.
    """
    N = 2**q
    L = 2 * max_x
    
    # Momentum grid. In standard FFT order, the frequencies are [0, 1, ..., N/2-1, -N/2, ..., -1]
    # Corresponding momenta are p = (2 * pi / L) * k
    dp = 2 * np.pi / L
    p_grid = dp * np.fft.fftfreq(N, d=1/N)
    
    # To construct P entirely in position space, we can evaluate its action element-wise 
    # or build the explicit matrix F^+ D_p F. 
    # However, standard DFT uses 0 to N-1 for indices. The unitary discrete Fourier matrix:
    # F_{j, k} = (1 / sqrt(N)) * exp(-2 * pi * i * j * k / N)
    
    F = np.zeros((N, N), dtype=complex)
    for j in range(N):
        for k in range(N):
            F[j, k] = np.exp(-2j * np.pi * j * k / N) / np.sqrt(N)
            
    # D_p is diagonal momentum operator in momentum basis. We must map fftfreq correctly.
    D_p = np.diag(p_grid)
    
    # P in position basis is F^dagger * D_p * F
    F_dagger = F.conj().T
    P = F_dagger @ D_p @ F
    
    return P


def generate_harmonic_oscillator_hamiltonian(q: int, mass: float, omega: float, max_x: float) -> np.ndarray:
    """
    Generates the discrete Hamiltonian matrix for the 1D Quantum Harmonic Oscillator.
    H = P^2 / (2 * mass) + 0.5 * mass * omega^2 * X^2
    
    Args:
        q: Number of qubits (dimension N = 2**q).
        mass: Mass of the particle.
        omega: Angular frequency of the oscillator.
        max_x: The spatial extent L/2.
        
    Returns:
        Hermitian NumPy array (N x N) representing the Hamiltonian.
    """
    X = generate_position_operator(q, max_x)
    P = generate_momentum_operator(q, max_x)
    
    # Kinetic energy: T = P^2 / (2m)
    T = (P @ P) / (2 * mass)
    
    # Potential energy: V = 0.5 * m * w^2 * X^2
    V = 0.5 * mass * (omega ** 2) * (X @ X)
    
    # Total Hamiltonian
    H = T + V
    
    return H

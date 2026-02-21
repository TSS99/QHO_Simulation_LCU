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
    (Deprecated) Direct generation of the continuous Momentum operator.
    Because DFT relies on dense Fourier grids, generating P directly scales O(N^2) Paulis!
    Instead, the Tridiagonal Finite Difference method natively computes P^2 in O(N) Paulis.
    """
    pass


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
    N = 2**q
    L = 2 * max_x
    dx = L / N
    x_grid = -max_x + np.arange(N) * dx
    
    # Central Finite Difference for second derivative (Laplacian)
    # T = P^2 / 2m = - (\hbar^2 / 2m) d^2/dx^2
    # This generates a beautifully sparse Tridiagonal matrix, shrinking Pauli scales!
    diag_T = 1.0 / (mass * dx**2) * np.ones(N)
    off_diag_T = -1.0 / (2 * mass * dx**2) * np.ones(N - 1)
    
    T = np.diag(diag_T) + np.diag(off_diag_T, k=1) + np.diag(off_diag_T, k=-1)
    
    # Enforce Periodic boundary conditions
    T[0, -1] = -1.0 / (2 * mass * dx**2)
    T[-1, 0] = -1.0 / (2 * mass * dx**2)
    
    # Potential energy: V = 0.5 * m * w^2 * X^2
    V = np.diag(0.5 * mass * (omega ** 2) * (x_grid ** 2))
    
    # Total Hamiltonian
    H = T + V
    
    return H

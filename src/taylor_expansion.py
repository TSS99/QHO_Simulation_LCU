import numpy as np
import math
from qiskit.quantum_info import SparsePauliOp

def compute_time_evolution_taylor(H_pauli: SparsePauliOp, t: float, K: int, threshold: float = 1e-10) -> SparsePauliOp:
    """
    Computes the truncated Taylor series approximation of the time evolution operator e^{-iHt}.
    e^{-iHt} ≈ sum_{k=0}^K ( (-it)^k / k! ) * H^k
    
    Args:
        H_pauli: The Hamiltonian represented as a SparsePauliOp.
        t: The evolution time.
        K: The order of the Taylor expansion truncation.
        threshold: The coefficient magnitude threshold for filtering terms.
        
    Returns:
        SparsePauliOp representing the approximated time evolution operator.
    """
    num_qubits = H_pauli.num_qubits
    
    # Initialize the series with the Identity operator for k=0
    # U = I
    I_pauli = SparsePauliOp.from_list([('I' * num_qubits, 1.0)])
    U_approx = I_pauli
    
    # H_pow keeps track of H^k
    H_pow = I_pauli
    
    for k in range(1, K + 1):
        # Accumulate H^k = H^(k-1) @ H
        H_pow = H_pow.dot(H_pauli)
        
        # We simplify H_pow to prevent an exponential blowup of terms during power calculation
        H_pow = H_pow.simplify(atol=threshold)
        
        # Calculate coefficient: (-it)^k / k!
        coeff = ((-1j * t) ** k) / math.factorial(k)
        
        # Add to the Taylor series
        term = H_pow * coeff
        U_approx = U_approx + term
        
        # Simplify the running sum
        U_approx = U_approx.simplify(atol=threshold)
        
    # Final explicit filtering just in case simplify leaves small terms
    valid_indices = np.where(np.abs(U_approx.coeffs) >= threshold)[0]
    if len(valid_indices) == 0:
        return SparsePauliOp.from_list([('I' * num_qubits, 0.0)])
        
    return U_approx[valid_indices]

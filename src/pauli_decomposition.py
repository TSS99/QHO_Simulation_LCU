import numpy as np
from qiskit.quantum_info import SparsePauliOp, Operator

def decompose_hamiltonian_to_paulis(H_matrix: np.ndarray, threshold: float = 1e-10) -> SparsePauliOp:
    """
    Decomposes a dense Hermitian Hamiltonian matrix into a sum of Pauli strings.
    Filters out any Pauli strings whose coefficient magnitude is below the threshold.
    
    Args:
        H_matrix: The Hermitian dense matrix representing the Hamiltonian.
        threshold: The magnitude below which Pauli coefficients are discarded.
        
    Returns:
        SparsePauliOp representing the decomposed Hamiltonian.
    """
    # Verify input is square
    if H_matrix.shape[0] != H_matrix.shape[1]:
        raise ValueError("Hamiltonian matrix must be square.")
        
    # Check if dimension is a power of 2
    N = H_matrix.shape[0]
    if (N & (N - 1)) != 0 or N == 0:
        raise ValueError("Hamiltonian matrix dimension must be a power of 2.")

    # Convert the dense matrix to a Qiskit Operator
    op = Operator(H_matrix)
    
    # Qiskit's SparsePauliOp can be constructed directly from an Operator, 
    # which automatically performs the Pauli decomposition Frobnius inner products.
    pauli_op = SparsePauliOp.from_operator(op)
    
    # Simplify to combine identical terms (if any) and prune zeros inherently
    pauli_op = pauli_op.simplify(atol=threshold)
    
    # Furthermore, we can explicitly filter the terms based on the desired threshold
    # if simplify's atol behaviour is insufficient for complex coefficients.
    valid_indices = np.where(np.abs(pauli_op.coeffs) >= threshold)[0]
    filtered_paulis = pauli_op[valid_indices]
    
    return filtered_paulis

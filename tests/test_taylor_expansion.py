import unittest
import numpy as np
import scipy.linalg
from qiskit.quantum_info import SparsePauliOp

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.taylor_expansion import compute_time_evolution_taylor

class TestTaylorExpansion(unittest.TestCase):
    def test_compute_time_evolution_taylor(self):
        # Create a simple 1-qubit Hamiltonian: H = 0.5 * X + 0.5 * Z
        H_pauli = SparsePauliOp.from_list([('X', 0.5), ('Z', 0.5)])
        H_dense = H_pauli.to_matrix()
        
        t = 1.0
        K = 15  # Choose a high enough K for the Taylor series to converge well
        
        # Exact theoretical calculation using scipy's matrix exponential
        U_exact = scipy.linalg.expm(-1j * t * H_dense)
        
        # Calculated Taylor expansion approximation
        U_approx_pauli = compute_time_evolution_taylor(H_pauli, t, K, threshold=1e-12)
        U_approx_dense = U_approx_pauli.to_matrix()
        
        # The approximation should be extremely close to the exact matrix
        np.testing.assert_allclose(
            U_approx_dense, 
            U_exact, 
            atol=1e-8, 
            err_msg="Taylor approximation does not match the exact matrix exponential."
        )

if __name__ == '__main__':
    unittest.main()

import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.hamiltonian import generate_harmonic_oscillator_hamiltonian
from src.pauli_decomposition import decompose_hamiltonian_to_paulis

class TestPauliDecomposition(unittest.TestCase):
    def test_decompose_hamiltonian_to_paulis(self):
        # Generate a small 2-qubit (N=4) Harmonic Oscillator Hamiltonian
        q = 2
        mass = 1.0
        omega = 1.0
        max_x = 2.0
        
        H = generate_harmonic_oscillator_hamiltonian(q, mass, omega, max_x)
        
        # Decompose into Paulis
        threshold = 1e-10
        pauli_op = decompose_hamiltonian_to_paulis(H, threshold)
        
        # Reconstruct the dense matrix from Pauli strings
        H_reconstructed = pauli_op.to_matrix()
        
        # Compare reconstructed matrix to original Hamiltonian
        # Note: the reconstruct matches the size of H (4x4)
        np.testing.assert_allclose(
            H_reconstructed, 
            H, 
            atol=threshold * 10, # Give some tolerance slightly above threshold
            err_msg="Reconstructed Hamiltonian does not match the original."
        )

        # Check that we actually filtered terms out or didn't blow up size
        num_paulis = len(pauli_op)
        max_possible_paulis = 4**q
        self.assertLessEqual(num_paulis, max_possible_paulis, "Pauli terms exceed dense space basis size.")
        
        # Check coefficients are predominantly real since H is Hermitian
        coeffs = pauli_op.coeffs
        imag_parts = np.abs(np.imag(coeffs))
        self.assertTrue(np.all(imag_parts < threshold), "Found significant imaginary coefficients for Hermitian matrix.")

if __name__ == '__main__':
    unittest.main()

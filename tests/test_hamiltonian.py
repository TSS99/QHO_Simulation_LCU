import unittest
import numpy as np

# We adjust path so we can import src.hamiltonian if not running as a module.
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.hamiltonian import generate_position_operator, generate_momentum_operator, generate_harmonic_oscillator_hamiltonian

class TestHamiltonianOperators(unittest.TestCase):
    def setUp(self):
        self.q = 4  # 16 dimensions
        self.max_x = 5.0
        self.N = 2**self.q

    def test_position_operator(self):
        X = generate_position_operator(self.q, self.max_x)
        
        # Check dimensions
        self.assertEqual(X.shape, (self.N, self.N))
        
        # Check Hermiticity
        np.testing.assert_allclose(X, X.conj().T, err_msg="X is not Hermitian")
        
        # Check reality (diagonal should be real)
        self.assertTrue(np.all(np.isreal(X)))
        
        # Check values
        dx = (2 * self.max_x) / self.N
        self.assertAlmostEqual(X[0, 0], -self.max_x)
        self.assertAlmostEqual(X[-1, -1], self.max_x - dx)

    def test_harmonic_oscillator_hamiltonian(self):
        mass = 1.0
        omega = 1.0
        H = generate_harmonic_oscillator_hamiltonian(self.q, mass, omega, self.max_x)
        
        # Check dimensions
        self.assertEqual(H.shape, (self.N, self.N))
        
        # Check Hermiticity
        np.testing.assert_allclose(H, H.conj().T, atol=1e-10, err_msg="H is not Hermitian")
        
        # Check eigenvalues (ground state should be > 0, approximately omega/2 = 0.5)
        eigenvalues = np.linalg.eigvalsh(H)
        
        # Eigenvalues must be real (since H is Hermitian) and bounded below (positive for HO)
        self.assertTrue(np.all(eigenvalues > 0), "Eigenvalues should be strictly positive")
        
        # The ground state energy should be roughly ~0.5 for m=1, w=1
        ground_state_energy = eigenvalues[0]
        self.assertTrue(0.4 < ground_state_energy < 0.6, f"Ground state energy is {ground_state_energy}, expected ~0.5")

if __name__ == '__main__':
    unittest.main()

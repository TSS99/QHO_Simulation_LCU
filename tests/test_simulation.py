import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.simulate_lcu import run_lcu_simulation

class TestLCUSimulation(unittest.TestCase):
    def test_full_lcu_pipeline(self):
        # Parameters for a small QHO system
        q = 2 # 4 basis states
        t = 0.1
        K = 4 # Modest taylor expansion
        
        res = run_lcu_simulation(q=q, mass=1.0, omega=1.0, max_x=2.0, t=t, K=K)
        
        simulated_state = res['normalized_state']
        exact_unitary = res['exact_unitary']
        
        # In our simulation pipeline, we tested the action assuming target was started in |0>
        # because Qiskit's Statevector implicitly starts all qubits in |0>.
        # So we must compare to exact_unitary applied to |0...0>
        
        initial_state = np.zeros(2**q)
        initial_state[0] = 1.0
        
        expected_state = exact_unitary @ initial_state
        
        # Since Taylor expansion has some truncation error, we don't expect 1e-15 accuracy.
        # But for t=0.1, K=4, it should be reasonably accurate (~1e-4).
        
        # Note: LCU outputs the state |psi> \propto e^{-iHt} |0>, however global phase might shift depending on
        # exact norm sum mappings, but density matrix or pure vector distance should be valid.
        
        fidelity = np.abs(np.vdot(simulated_state, expected_state))**2
        
        self.assertGreater(fidelity, 0.99, "Simulated state fidelity against exact is too low.")
        
        # Also check probability bounds
        self.assertGreater(res['success_prob'], 0, "Success probability should be positive.")
        self.assertLessEqual(res['success_prob'], 1.0 + 1e-10, "Success probability bounded by 1.")

if __name__ == '__main__':
    unittest.main()

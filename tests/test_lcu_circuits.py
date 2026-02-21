import unittest
import numpy as np
from qiskit.quantum_info import Statevector

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.lcu_circuits import build_prepare_circuit, build_select_circuit

class TestLCUCircuits(unittest.TestCase):
    def test_build_prepare_circuit(self):
        # Dummy alphas
        alpha = np.array([1.0, 2.0, 1.0])
        M = len(alpha)
        
        # Expected amplitudes
        l1_norm = np.sum(alpha)
        expected_amplitudes = np.sqrt(alpha / l1_norm)
        
        # The number of ancilla qubits should be ceil(log2(3)) = 2.
        # Padded length is 4.
        padded_expected = np.zeros(4)
        padded_expected[:M] = expected_amplitudes
        
        qc = build_prepare_circuit(alpha)
        self.assertEqual(qc.num_qubits, 2)
        
        # Get the statevector from the circuit
        sv = Statevector(qc)
        
        # Verify the statevector matches expected amplitudes
        np.testing.assert_allclose(
            sv.data, 
            padded_expected, 
            atol=1e-10, 
            err_msg="PREPARE circuit statevector does not match expected amplitudes."
        )

    def test_build_select_circuit(self):
        paulis = ['IX', 'ZI']
        complex_phases = [1.0, 1j] # e^{i*0}, e^{i*pi/2}
        
        qc = build_select_circuit(paulis, complex_phases)
        
        # 2 pauli terms -> 1 ancilla qubit.
        # Length of Pauli string is 2 -> 2 target qubits.
        # Total = 3 qubits
        self.assertEqual(qc.num_qubits, 3)
        
        # Test case 1: Ancilla is |0>. Action should be 1.0 * (I on q2, X on q1).
        # We start with state |0>|00>.
        qc0 = qc.copy()
        
        # Test case 2: Ancilla is |1>. Action should be 1j * (Z on q2, I on q1).
        qc1 = qc.copy()
        # Initialize ancilla to |1> (qubit 2 since q0,q1 are targets, q2 is ancilla based on Qiskit ordering)
        # Note: QC created as ancilla(1), target(2). Qiskit registers are concatenated.
        # q0 = ancilla 0
        # q1 = target 0
        # q2 = target 1
        # Therefore, ancilla is |0> by default. Let's create a full circuit prep.
        from qiskit import QuantumCircuit
        
        # Test state where target is |+>|+> and ancilla is |0>
        test_qc_0 = QuantumCircuit(3)
        test_qc_0.h([1,2]) # target |+>|+>
        test_qc_0.append(qc, [0, 1, 2])
        
        sv_0 = Statevector(test_qc_0)
        
        # Manual apply of 'IX' to |+>|+>
        # IX on target (q1, q2) means X on q1, I on q2.
        # |+> is invariant under X, so state is still |+>|+> on targets.
        manual_qc_0 = QuantumCircuit(3)
        manual_qc_0.h([1,2])
        manual_qc_0.x(1) # because Qiskit Pauli 'IX' applies X to target 0 (which is q1 total)
        sv_manual_0 = Statevector(manual_qc_0)
        
        np.testing.assert_allclose(sv_0.data, sv_manual_0.data, atol=1e-10)

        # Test state where target is |+>|+> and ancilla is |1>
        test_qc_1 = QuantumCircuit(3)
        test_qc_1.h([1,2])
        test_qc_1.x(0) # set ancilla to |1>
        test_qc_1.append(qc, [0, 1, 2])
        
        sv_1 = Statevector(test_qc_1)
        
        # Manual apply of 1j * 'ZI' to |+>|+>
        manual_qc_1 = QuantumCircuit(3)
        manual_qc_1.x(0)
        manual_qc_1.h([1,2])
        manual_qc_1.z(2) # 'ZI' means I on target 0 (q1 entirely), Z on target 1 (q2 entirely)
        # Global phase 1j (pi/2)
        manual_qc_1.global_phase = np.pi/2
        sv_manual_1 = Statevector(manual_qc_1)
        
        np.testing.assert_allclose(sv_1.data, sv_manual_1.data, atol=1e-10)

if __name__ == '__main__':
    unittest.main()

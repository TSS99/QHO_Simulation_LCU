import numpy as np
import math
import sys
import os

# Ensure the root directory of the project is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Statevector

from src.hamiltonian import generate_harmonic_oscillator_hamiltonian
from src.pauli_decomposition import decompose_hamiltonian_to_paulis
from src.taylor_expansion import compute_time_evolution_taylor
from src.lcu_circuits import build_prepare_circuit, build_select_circuit

def run_lcu_simulation(q: int, mass: float, omega: float, max_x: float, t: float, K: int, threshold: float=1e-10):
    """
    Orchestrates the full LCU simulation for the 1D QHO time evolution.
    
    Args:
        q: Number of qubits for the target space (N = 2^q).
        mass: Particle mass.
        omega: Oscillator angular frequency.
        max_x: Spatial bounds (-max_x to max_x).
        t: Time of evolution.
        K: Taylor series truncation order.
        threshold: Precision cutoff.
        
    Returns:
        dict containing:
            'circuit': The full Qiskit QuantumCircuit
            'success_prob': The theoretical probability of successful post-selection
            'normalized_state': The output Statevector of the target register upon success
            'exact_unitary': The exact dense matrix of expm(-iHt) for comparison
            'H_matrix': The generated Hamiltonian matrix
    """
    # 1. Generate Hamiltonian matrix
    H_matrix = generate_harmonic_oscillator_hamiltonian(q, mass, omega, max_x)
    
    # 2. Decompose into Paulis
    H_pauli = decompose_hamiltonian_to_paulis(H_matrix, threshold)
    
    # 3. Compute Taylor expansion
    U_taylor_pauli = compute_time_evolution_taylor(H_pauli, t, K, threshold)
    
    # Extract coefficients and paulis
    complex_coeffs = U_taylor_pauli.coeffs
    paulis = [p.to_label() for p in U_taylor_pauli.paulis]
    
    alpha_j = np.abs(complex_coeffs)
    complex_phases = complex_coeffs / np.where(alpha_j == 0, 1, alpha_j)
    
    # 4. Determine qubit requirements
    M = len(paulis)
    n_a = math.ceil(math.log2(M)) if M > 1 else 1
    n_t = q
    
    # 5. Build subroutines
    qc_prepare = build_prepare_circuit(alpha_j)
    qc_select = build_select_circuit(paulis, complex_phases)
    qc_unprepare = qc_prepare.inverse()
    
    # 6. Compose full circuit
    ancilla = QuantumRegister(n_a, 'ancilla')
    target = QuantumRegister(n_t, 'target')
    full_qc = QuantumCircuit(ancilla, target, name="LCU_Full")
    
    # Target initially |0> state; apply PREPARE on ancilla
    full_qc.append(qc_prepare, ancilla)
    
    # Apply SELECT
    full_qc.append(qc_select, list(ancilla) + list(target))
    
    # Apply PREPARE_dagger on ancilla
    full_qc.append(qc_unprepare, ancilla)
    
    # 7. Post-selection simulation
    sv = Statevector(full_qc).data
    
    # Qiskit registers: target is qubits [n_a, n_a + 1, ...], ancilla is [0, 1, ..., n_a - 1].
    # So the state integer is composed of target bits and ancilla bits.
    # Success means ancilla is |0>...|0>, which corresponds to indices where the lowest n_a bits are exactly 0.
    target_dim = 2**n_t
    ancilla_dim = 2**n_a
    
    # Pre-allocate success state
    success_state = np.zeros(target_dim, dtype=complex)
    
    # The computational basis states are |target>|ancilla>
    # success is when |ancilla> = |0>.
    # So index = target_idx * (2**n_a) + 0
    for target_idx in range(target_dim):
        sv_idx = target_idx * ancilla_dim
        success_state[target_idx] = sv[sv_idx]
        
    p_success_val = np.sum(np.abs(success_state)**2)
    
    # Factor from the LCU protocol calculation
    # ||alpha||_1 norm scales the unitaries. If sum(alpha) != 1, success probability scales by 1/||alpha||_1^2
    # In time evolution by Taylor series, ||alpha||_1 can be roughly e^(||H|| t), 
    # making exact calculation of success_prob mathematically necessary from amplitude weights
    # Note: State is unnormalized here.
    
    if p_success_val > 1e-15:
        normalized_target_state = success_state / np.sqrt(p_success_val)
    else:
        normalized_target_state = success_state
        p_success_val = 0.0
        
    import scipy.linalg
    exact_unitary = scipy.linalg.expm(-1j * t * H_matrix)
    
    return {
        'circuit': full_qc,
        'success_prob': p_success_val,
        'normalized_state': normalized_target_state,
        'exact_unitary': exact_unitary,
        'H_matrix': H_matrix
    }

if __name__ == '__main__':
    # A quick sandbox execution
    print("Running Sandbox LCU...")
    res = run_lcu_simulation(q=2, mass=1.0, omega=1.0, max_x=2.0, t=0.5, K=5)
    print(f"Success probability: {res['success_prob']:.4f}")
    
    exact_state = res['exact_unitary'] @ np.zeros(4)
    exact_state[0] = 1.0 # applying to |0>
    exact_state = res['exact_unitary'] @ exact_state
    
    print("\nSimulated State (target):")
    print(np.round(res['normalized_state'], 4))
    print("\nExact Target State    :")
    print(np.round(exact_state, 4))

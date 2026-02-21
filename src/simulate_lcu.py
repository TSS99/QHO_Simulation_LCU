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

def run_lcu_simulation(q: int, mass: float, omega: float, max_x: float, t: float, K: int, threshold: float=1e-10, time_steps: int=1):
    """
    Orchestrates the full LCU simulation for the 1D QHO time evolution.
    
    Args:
        q: Number of qubits for the target space (N = 2^q).
        mass: Particle mass.
        omega: Oscillator angular frequency.
        max_x: Spatial bounds (-max_x to max_x).
        t: Time of evolution.
        K: Taylor series truncation order per time step.
        threshold: Precision cutoff.
        time_steps: Number of trotters/slices to segment the full time `t` into. This prevents Taylor expansion blow-ups and scales easily to high qubits.
        
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
    
    # Time segment
    dt = t / time_steps
    
    # 3. Compute Taylor expansion for Delta t
    U_taylor_pauli = compute_time_evolution_taylor(H_pauli, dt, K, threshold)
    
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
    
    # 6. Compose full single step circuit
    ancilla = QuantumRegister(n_a, 'ancilla')
    target = QuantumRegister(n_t, 'target')
    step_qc = QuantumCircuit(ancilla, target, name="LCU_Step")
    
    # Apply PREPARE on ancilla
    step_qc.append(qc_prepare, ancilla)
    
    # Apply SELECT
    step_qc.append(qc_select, list(ancilla) + list(target))
    
    # Apply PREPARE_dagger on ancilla
    step_qc.append(qc_unprepare, ancilla)
    
    # Initialize the target state
    current_target_state = np.zeros(2**n_t, dtype=complex)
    current_target_state[0] = 1.0  # Ground-ish computational start
    
    total_success_prob = 1.0
    target_dim = 2**n_t
    ancilla_dim = 2**n_a
    
    # Iterate across time steps, feeding the post-selected statevector back in
    for step in range(time_steps):
        # We tensor the target state with the |0> ancilla state. 
        # In Qiskit's little-endian ordering, the ancilla are the least significant bits (qubits 0 to n_a-1)
        # So we want |target> (X) |0...0_ancilla>.
        # We manually construct this to initialize the Statevector correctly.
        full_state_init = np.zeros(target_dim * ancilla_dim, dtype=complex)
        for target_idx in range(target_dim):
            # The indices corresponding to ancilla = |0>
            sv_idx = target_idx * ancilla_dim
            full_state_init[sv_idx] = current_target_state[target_idx]
            
        sv = Statevector(full_state_init)
        
        # Evolve the statevector using the LCU timestep block
        sv_out = sv.evolve(step_qc).data
        
        # Post-selection: extract indices where ancilla is |0>
        success_state = np.zeros(target_dim, dtype=complex)
        for target_idx in range(target_dim):
            sv_idx = target_idx * ancilla_dim
            success_state[target_idx] = sv_out[sv_idx]
            
        p_success_val = np.sum(np.abs(success_state)**2)
        total_success_prob *= p_success_val
        
        if p_success_val > 1e-15:
            current_target_state = success_state / np.sqrt(p_success_val)
        else:
            current_target_state = success_state
            total_success_prob = 0.0
            break
        
    import scipy.linalg
    exact_unitary = scipy.linalg.expm(-1j * t * H_matrix)
    
    return {
        'circuit': step_qc,
        'success_prob': total_success_prob,
        'normalized_state': current_target_state,
        'exact_unitary': exact_unitary,
        'H_matrix': H_matrix
    }



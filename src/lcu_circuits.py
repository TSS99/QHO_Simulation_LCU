import numpy as np
import math
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import StatePreparation, PhaseGate, MCXGate, MCMT

def build_prepare_circuit(coefficients: np.ndarray) -> QuantumCircuit:
    M = len(coefficients)
    n_a = math.ceil(math.log2(M))
    if n_a == 0:
        n_a = 1
        
    N_padded = 2**n_a
    padded_coeffs = np.zeros(N_padded)
    for j in range(M):
        # Map indices to Gray code ordering to optimize sequential activation in SELECT
        g_j = j ^ (j >> 1)
        padded_coeffs[g_j] = coefficients[j]
    
    l1_norm = np.sum(np.abs(padded_coeffs))
    
    if l1_norm < 1e-15:
        amplitudes = np.zeros(N_padded)
        amplitudes[0] = 1.0
    else:
        amplitudes = np.sqrt(padded_coeffs / l1_norm)
        
    qc = QuantumCircuit(n_a, name="PREPARE")
    qc.prepare_state(amplitudes, qc.qubits)
    
    return qc

def build_select_circuit(paulis: list[str], complex_phases: list[complex]) -> QuantumCircuit:
    if not paulis:
        raise ValueError("Pauli list is empty.")
    
    M = len(paulis)
    n_t = len(paulis[0])
    n_a = math.ceil(math.log2(M)) if M > 1 else 1

    ancilla = QuantumRegister(n_a, 'ancilla')
    target = QuantumRegister(n_t, 'target')
    qc = QuantumCircuit(ancilla, target, name="SELECT")

    # Initialize X-gates natively to logic 0 -> flip all for |0..0>
    current_g = 0
    qc.x(ancilla)

    for j, (pauli_str, phase) in enumerate(zip(paulis, complex_phases)):
        # Calculate Gray code progression
        g_j = j ^ (j >> 1)
        diff = current_g ^ g_j
        current_g = g_j
        
        # Apply X only to the bit that changed state 
        # (reduces O(M*n_a) X-gates to O(M))
        changed_indices = [i for i in range(n_a) if (diff & (1 << i))]
        if changed_indices:
            qc.x([ancilla[i] for i in changed_indices])
        
        angle = np.angle(phase)
        if abs(angle) > 1e-10:
            if n_a > 1:
                mc_p = PhaseGate(angle).control(n_a - 1)
                ctrl_qubits = list(ancilla[1:])
                tgt_qubit = ancilla[0]
                qc.append(mc_p, ctrl_qubits + [tgt_qubit])
            else:
                qc.p(angle, ancilla[0])

        for t_idx, p_op in enumerate(reversed(pauli_str)):
            if p_op == 'I':
                continue
            
            controls = list(ancilla)
            tgt = target[t_idx]
            
            if p_op == 'X':
                mcx = MCXGate(n_a)
                qc.append(mcx, controls + [tgt])
            elif p_op == 'Y':
                # Build an abstract controlled Y gate and append it
                from qiskit.circuit.library import YGate
                mcy = YGate().control(n_a)
                qc.append(mcy, controls + [tgt])
            elif p_op == 'Z':
                from qiskit.circuit.library import ZGate
                mcz = ZGate().control(n_a)
                qc.append(mcz, controls + [tgt])

    # Revert final X-configuration back to pure basis
    final_anti = [ancilla[i] for i in range(n_a) if not (current_g & (1 << i))]
    if final_anti:
        qc.x(final_anti)
            
    return qc

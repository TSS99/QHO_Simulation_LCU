import numpy as np
import matplotlib.pyplot as plt
from src.simulate_lcu import run_lcu_simulation

# ==========================================
# --- Simulation Input Parameters ---
# ==========================================
q = 2                 # Number of qubits for the target space (N = 2^q)
mass = 1.0            # Particle mass
omega = 1.0           # Oscillator angular frequency
max_x = 2.0           # Spatial bounds (-max_x to max_x)
t = 0.5               # Time of evolution
time_steps = 5        # Number of segments to divide the time evolution into
K = 3                 # Taylor series truncation order per step
threshold = 1e-10     # Precision cutoff
num_amplification_steps = 1 # Steps of Oblivious Amplitude Amplification (OAA)
# ==========================================

def run():
    print("--------------------------------------------------")
    print("        1D Quantum Harmonic Oscillator LCU        ")
    print("--------------------------------------------------")
    print(f"Parameters:\n - Qubits (q): {q}\n - Mass: {mass}\n - Omega: {omega}\n - Max X: {max_x}\n - Time (t): {t}\n - Segments (time_steps): {time_steps}\n - Taylor Order (K): {K}\n - OAA Steps: {num_amplification_steps}\n")
    
    # Run the orchestrator
    res = run_lcu_simulation(q=q, mass=mass, omega=omega, max_x=max_x, t=t, K=K, threshold=threshold, time_steps=time_steps, num_amplification_steps=num_amplification_steps)
    
    print(f"Success probability of state projection: {res['success_prob']:.4f}")
    
    # Exact unitary comparison for the standard initial ground-ish state |0>
    exact_state = res['exact_unitary'] @ np.zeros(2**q)
    exact_state[0] = 1.0
    exact_state = res['exact_unitary'] @ exact_state
    
    # Show output vectors
    print("\nSimulated Target Statevector:")
    print(np.round(res['normalized_state'], 4))
    print("\nExact Target Statevector:")
    print(np.round(exact_state, 4))
    
    # Calculate and print fidelity
    # Fidelity for pure states is |<psi|phi>|^2
    fidelity = np.abs(np.vdot(res['normalized_state'], exact_state))**2
    print(f"\nState Fidelity: {fidelity:.6f}")
    
    # Generate the circuit metrics and block plot
    print("\n--- Circuit Metrics ---")
    qc = res['circuit']
    
    # Transpile the abstract blocks (PREPARE, SELECT, etc.) into primitive standard basis gates
    print("Decomposing the abstract blocks into 1- and 2-qubit gates... (This may take a moment)")
    from qiskit import transpile
    basis_gates = ['cx', 'rx', 'ry', 'rz', 'h', 'x', 'y', 'z'] # standard fault-tolerant-like minimal basis
    qc_unrolled = transpile(qc, basis_gates=basis_gates)
    
    print(f"\nUnrolled Circuit Depth: {qc_unrolled.depth()}")
    ops = qc_unrolled.count_ops()
    print(f"Total Number of Operations: {sum(ops.values())}")
    print("Gate Counts breakdown:")
    for gate, count in ops.items():
        print(f" - {gate.upper()}: {count}")
    
    print("\nGenerating and saving block diagram using matplotlib...")
    # Using 'mpl' on the original nested circuit to keep memory low and visually clean
    fig = qc.draw(output='mpl', style='clifford')
    
    # Save the circuit to a file
    filepath = 'lcu_circuit_diagram.png'
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"Saved block circuit to '{filepath}'.")
    
    # Display the circuit interactively if running in a windowed environment
    try:
        print("Attempting to display the circuit window. Close the window to exit the script.")
        plt.show()
    except Exception as e:
        print("Could not display the interactive visualization window.")

if __name__ == "__main__":
    run()

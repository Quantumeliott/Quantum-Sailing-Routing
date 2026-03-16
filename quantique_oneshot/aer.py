import sys
import os
import numpy as np
from scipy.optimize import minimize

class MPSOptimizationResult:
    """Classe 'déguisement' pour tromper next_point.py"""
    def __init__(self, variables_dict):
        self.variables_dict = variables_dict

# --- GESTION DU CHEMIN ---
current_dir = os.path.dirname(os.path.abspath(__file__))
build_path = os.path.join(current_dir, "mps_engine", "build")
if build_path not in sys.path:
    sys.path.insert(0, build_path)

try:
    import mps_engine
except ImportError:
    print(f"❌ Erreur critique : Impossible de charger le moteur C++ depuis {build_path}")
    sys.exit(1)

# --- LE SOLVEUR QAOA ---
def solve_with_mps(qubo_problem, reps=5, maxiter=1000, max_bond_dim=128):
    hamiltonian, offset = qubo_problem.to_ising()
    num_qubits = qubo_problem.get_num_vars()

    def build_circuit(gammas, betas):
        # CORRECTION 1 : On utilise la vraie classe MPS de notre C++
        sim = mps_engine.MPS(num_qubits, max_bond_dim)
        
        for i in range(num_qubits):
            sim.apply_gate("H", i)
            
        for p in range(len(gammas)):
            # --- TRADUCTEUR DE HAMILTONIEN DE COÛT ---
            for pauli_str, coeff in hamiltonian.to_list():
                # Qiskit lit de droite à gauche (le caractère le plus à droite est le qubit 0)
                z_indices = [i for i, char in enumerate(reversed(pauli_str)) if char == 'Z']
                angle = 2.0* gammas[p] * coeff
                
                if len(z_indices) == 1:
                    # Terme linéaire (Zi) -> Une simple rotation RZ
                    sim.apply_gate("RZ", z_indices[0], angle)
                elif len(z_indices) == 2:
                    # Terme quadratique (Zi Zj) -> Le sandwich CNOT-RZ-CNOT
                    q1, q2 = z_indices[0], z_indices[1]
                    sim.apply_cnot(q1, q2)
                    sim.apply_gate("RZ", q2, angle)
                    sim.apply_cnot(q1, q2)
            
            # --- HAMILTONIEN DE MÉLANGE ---
            for i in range(num_qubits):
                sim.apply_gate("RX", i, 2 * betas[p])
        return sim

    def objective_function(params):
        gammas = params[:reps]
        betas = params[reps:]
        sim = build_circuit(gammas, betas)
        
        energy = 0.0
        for pauli_str, coeff in hamiltonian.to_list():
            z_indices = [i for i, char in enumerate(reversed(pauli_str)) if char == 'Z']
            
            # --- CORRECTION ICI : On extrait la partie réelle du coefficient Qiskit ---
            c = float(np.real(coeff))
            
            if len(z_indices) == 1:
                energy += c * sim.expectation_z(z_indices[0])
            elif len(z_indices) == 2:
                # Approximation Mean-Field
                energy += c * sim.expectation_zz(z_indices[0], z_indices[1])
                
        # --- CORRECTION ICI : On s'assure que le retour est un pur float (réel) ---
        return energy + float(np.real(offset))

    # Lancement de l'optimisation
    init_params = np.random.uniform(0, np.pi, 2 * reps)
    res = minimize(objective_function, init_params, method='COBYLA', options={'maxiter': maxiter})

    # Reconstruction finale
    best_sim = build_circuit(res.x[:reps], res.x[reps:])
  
    # On récupère les valeurs binaires du C++
    result_array = [1 if best_sim.expectation_z(i) < 0 else 0 for i in range(num_qubits)]
    
    # On recrée le dictionnaire attendu par le reste de ton projet
    var_dict = {}
    for i, var in enumerate(qubo_problem.variables):
        var_dict[var.name] = result_array[i]
        
    # On renvoie notre faux objet Qiskit
    return MPSOptimizationResult(var_dict)
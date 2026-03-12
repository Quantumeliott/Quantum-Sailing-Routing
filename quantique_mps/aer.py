import numpy as np
from scipy.optimize import minimize
# C'est ici qu'on importe ton bébé compilé en C++
import mps_engine 

def resoudre_sur_aer(qubo_problem, reps=1, maxiter=40, max_bond_dim=64):
    # 1. Extraction des coefficients du Hamiltonien (QUBO)
    # On récupère les poids des arêtes du graphe pour le QAOA
    hamiltonian = qubo_problem.to_ising()
    observable, offset = hamiltonian[0], hamiltonian[1]
    num_qubits = qubo_problem.get_num_vars()

    # 2. Définition de la fonction de coût pour l'optimiseur classique
    def objective_function(params):
        # On sépare les angles gamma (cost) et beta (mixer)
        gammas = params[:reps]
        betas = params[reps:]

        # --- APPEL AU MOTEUR C++ ---
        # On initialise ton simulateur C++
        sim = mps_engine.Simulator(num_qubits, max_bond_dim)
        
        # On construit le circuit QAOA directement dans le moteur C++
        # (On évite de créer des objets Qiskit lourds ici)
        for p in range(reps):
            # Phase de coût (Problem Hamiltonian)
            for pauli_str, coeff in observable.to_list():
                # On applique les rotations basées sur les poids du graphe
                sim.apply_pauli_rotation(pauli_str, gammas[p] * coeff)
            
            # Phase de mélange (Mixer Hamiltonian)
            for i in range(num_qubits):
                sim.apply_gate("RX", i, 2 * betas[p])

        # On demande au C++ de calculer l'énergie (Espérance mathématique)
        # C'est ici que la SVD et le MPS font le gros du travail
        energy = sim.compute_expectation(observable)
        return energy

    # 3. Optimisation classique (Scipy est très robuste ici)
    init_params = np.random.uniform(0, np.pi, 2 * reps)
    res = minimize(objective_function, init_params, method='COBYLA', options={'maxiter': maxiter})

    # 4. Échantillonnage final avec les meilleurs paramètres
    best_sim = mps_engine.Simulator(num_qubits, max_bond_dim)
    # ... (Reconstruction du circuit avec res.x) ...
    
    # On récupère le meilleur chemin (bitstring) depuis le C++
    resultat_binaire = best_sim.get_most_probable_outcome()
    
    return resultat_binaire
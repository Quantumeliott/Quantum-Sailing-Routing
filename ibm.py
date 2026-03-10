from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_optimization.algorithms import MinimumEigenOptimizer

# --- NOUVEAUX IMPORTS POUR LE VRAI MATÉRIEL ---
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

def resoudre_sur_ibm(qubo_problem, reps=1, maxiter=30):
    print("   [IBM] Connexion aux serveurs IBM Cloud...")
    
    # 1. AUTHENTIFICATION CLOUD
    API_KEY = ""
    CRN = ""
    try:
        service = QiskitRuntimeService(
            channel="ibm_cloud", 
            token=API_KEY, 
            instance=CRN
        )
    except Exception as e:
        print(f"Erreur de connexion : {e}")
        return None
        
    # 2. SÉLECTION DE LA PUCE
    print("   [IBM] Recherche du processeur disponible...")
    # Sur IBM Cloud gratuit, tu n'as généralement accès qu'aux simulateurs ou à une puce spécifique
    # On enlève le least_busy trop restrictif pour éviter les crashs sur le Cloud Open Plan
    backend = service.least_busy(simulator=False, min_num_qubits=20)
    print(f"   [IBM] Succès ! Processeur alloué : {backend.name}")
    
    # 3. CONFIGURATION DU MATÉRIEL (La fameuse Mitigation !)
    # On utilise le SamplerV2 moderne
    sampler_ibm = Sampler(mode=backend)
    
    # 4. CONFIGURATION QAOA
    optimiseur = COBYLA(maxiter=maxiter)
    qaoa = QAOA(sampler=sampler_ibm, optimizer=optimiseur, reps=reps)
    qaoa_optimizer = MinimumEigenOptimizer(qaoa)
    
    # 5. EXÉCUTION (L'envoi dans le Cloud)
    print(f"   [IBM] Envoi du Job hybride sur {backend.name} (Attention, ça peut prendre du temps avec la file d'attente)...")
    resultat = qaoa_optimizer.solve(qubo_problem)
    
    print(f"   [IBM] Job terminé ! Temps estimé du trajet choisi : {resultat.fval}")
    
    return resultat

# ==========================================
# ZONE DE TEST INDÉPENDANTE
# ==========================================
if __name__ == "__main__":
    import networkx as nx
    from ising import build_routing_ising
    
    print("Création du problème de test pour la vraie puce IBM...")
    G = nx.DiGraph()
    G.add_edge(0, 1, weight=8.0)
    G.add_edge(0, 2, weight=2.0)
    G.add_edge(1, 3, weight=2.0)
    G.add_edge(2, 3, weight=3.0)
    
    _, _, qp = build_routing_ising(G, source=0, target=3)
    
    # N'oublie pas de mettre ton Token plus haut avant de lancer !
    resultat_test = resoudre_sur_ibm(qp, reps=1, maxiter=20)
    
    print("\nVariables choisies physiquement par la machine :")
    for var, val in resultat_test.variables_dict.items():
        if val > 0.5:
            print(f" -> L'arête {var} est sélectionnée.")
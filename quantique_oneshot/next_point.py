import networkx as nx
from quantique_oneshot.ising import build_routing_ising
from quantique_oneshot.aer import solve_with_mps
from quantique_oneshot.create_graphes import generer_macro_graphe

def get_full_quantum_path(env, pos_bateau, cible_finale=(83.7, 96), t=0.0):
    # 1. On génère ton énorme graphe de 109 qubits
    Gw, Gt, coords, target_id = generer_macro_graphe(env, pos_bateau, cible_finale, t)
    # On met un penalty_factor énorme (ex: 500 ou 1000) pour interdire les chemins brisés
    qp = build_routing_ising(Gw, source=0, target=target_id, penalty_factor=150.0)

    # 2. On solve avec le MPS
    resultat_binaire = solve_with_mps(qp)

    # 3. On récupère toutes les arêtes activées
    chemin_edges = []
    for var_name, val in resultat_binaire.variables_dict.items():
        if val > 0.5:
            parts = var_name.split('_') # qp génère des noms type "x_0_4"
            u, v = int(parts[1]), int(parts[2])
            chemin_edges.append((u, v))
            
    # 4. On reconstruit le chemin complet de 0 jusqu'à target_id
    current_node = 0
    path_nodes = [0]
    
    # Boucle de sécurité pour remonter la chaîne
    max_steps = 30
    step = 0
    while current_node != target_id and step < max_steps:
        next_node = None
        for u, v in chemin_edges:
            if u == current_node:
                next_node = v
                break
        
        if next_node is None:
            print(f"⚠️ Chemin brisé au noeud {current_node}. Le QUBO n'a pas fermé la chaîne.")
            break
            
        path_nodes.append(next_node)
        current_node = next_node
        step += 1

    # 5. On traduit les Noeuds en Coordonnées et on calcule le temps cumulé
    chemin_coords = [coords[n] for n in path_nodes]
    time_register = [t]
    
    current_t = t
    for i in range(len(path_nodes) - 1):
        u = path_nodes[i]
        v = path_nodes[i+1]
        # On additionne le temps de trajet du segment
        segment_time = Gt[u][v]['weight']
        current_t += segment_time
        time_register.append(current_t)

    return chemin_coords, time_register
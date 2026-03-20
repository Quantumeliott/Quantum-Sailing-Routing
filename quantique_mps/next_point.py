import networkx as nx   #type: ignore
from quantique_mps.ising import build_routing_ising
from quantique_mps.aer import solve_with_mps
from quantique_mps.create_graphes import generer_macro_graphe

def get_next_quantum_waypoint(env, pos_bateau, cible_finale=(83.7, 96), t=0.0):

    Gw, Gt, coords, target_id = generer_macro_graphe(env, pos_bateau, cible_finale, t)
    qp = build_routing_ising(Gw, source=0, target=target_id)

    resultat_binaire = solve_with_mps(qp)

    chemin_edges = []
    
    for var_name, val in resultat_binaire.variables_dict.items():
        if val > 0.5:
            parts = var_name.split('_')
            u, v = int(parts[1]), int(parts[2])
            chemin_edges.append((u, v))
            
    prochain_noeud_id = 0
    for u, v in chemin_edges:
        if u == 0:
            prochain_noeud_id = v
            break

    if prochain_noeud_id == 0:
        prochain_noeud_id = min(Gw.successors(0), key=lambda v: Gw[0][v]['weight'])

    prochain_waypoint_coords = coords[prochain_noeud_id]
    duree_segment= Gt[0][prochain_noeud_id]['weight']
    return prochain_waypoint_coords, t+duree_segment
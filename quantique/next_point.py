import networkx as nx   #type: ignore
from quantique.ising import build_routing_ising
from quantique.aer import resoudre_sur_aer
from quantique.create_graphes import generer_macro_graphe

def get_next_quantum_waypoint(env, pos_bateau, cible_finale=(83.7, 96), t=0.0):

    G, coords, target_id = generer_macro_graphe(env, pos_bateau, cible_finale, t)
    G[0][2]['weight'] = 95*G[0][2]['weight']/100
    qp = build_routing_ising(G, source=0, target=target_id)

    resultat_binaire = resoudre_sur_aer(qp)

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
        prochain_noeud_id = 2

    prochain_waypoint_coords = coords[prochain_noeud_id]
    if prochain_noeud_id ==2:
        duree_segment = 100*G[0][prochain_noeud_id]['weight']/95
    else:
        duree_segment= G[0][prochain_noeud_id]['weight']

    return prochain_waypoint_coords, t+duree_segment

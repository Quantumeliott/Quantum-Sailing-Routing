import math
import networkx as nx   #type: ignore
from ising import build_routing_ising
from aer import resoudre_sur_aer
from ibm import resoudre_sur_ibm

def generer_macro_graphe(env, pos_bateau, cible_finale=(83.7, 96), t=0.0):
    G = nx.DiGraph()
    coords = {}
    eta = {0: t}
    
    x0, y0 = pos_bateau
    xt, yt = cible_finale

    # Distance restante jusqu'à l'arrivée
    dist_totale = math.hypot(xt - x0, yt - y0)
    angle = math.atan2(yt - y0, xt - x0)
    
    coords[0] = pos_bateau
    
    # Fonction de calcul des temps de trajet (inchangée, mais encapsulée)
    def get_weight(u, v):
        x1, y1 = coords[u]
        x2, y2 = coords[v]
        t_start = eta.get(u, t) 
        total_time = 0.0
        dist_directe = math.hypot(x2-x1, y2-y1)
        nb_pas = math.ceil(dist_directe) 
        if nb_pas == 0: return 0.1 # Sécurité anti-division par zéro
        
        dx = (x2 - x1) / nb_pas
        dy = (y2 - y1) / nb_pas
        
        for i in range(nb_pas):
            step_time = env.get_travel_time(x1 + i*dx, y1 + i*dy,
                                            x1 + (i+1)*dx, y1 + (i+1)*dy,
                                            t_start + total_time)
            
            if step_time > 1000.0: 
                step_time = 1000.0
            total_time += step_time
        return total_time

    # =========================================================
    # 🎯 MODE APPROCHE FINALE (Moins de 20 unités de distance)
    # =========================================================
    if dist_totale < 20.0:
        # On ne génère que 3 points (gauche, centre, droite)
        dist_h = dist_totale * 0.5
        c1_nodes = [1, 2, 3]
        for i, n in enumerate(c1_nodes):
            d_lat = (i - 1) * (dist_h * 0.4) # Écartement latéral réduit
            coords[n] = (x0 + dist_h*math.cos(angle) - d_lat*math.sin(angle),
                         y0 + dist_h*math.sin(angle) + d_lat*math.cos(angle))
        
        cible_noeud = 4
        coords[cible_noeud] = cible_finale # On connecte directement à la fin

        for n in c1_nodes:
            w1 = get_weight(0, n)
            G.add_edge(0, n, weight=w1)
            eta[n] = t + w1 

            w2 = get_weight(n, cible_noeud)
            G.add_edge(n, cible_noeud, weight=w2)

        return G, coords, cible_noeud

    # =========================================================
    # 🌊 MODE CROISIÈRE (Le grand graphe habituel à 13 qubits)
    # =========================================================
    dist_h = min(dist_totale * 0.2, 40.0)
    c1_nodes = [1, 2, 3]
    for i, n in enumerate(c1_nodes):
        d_fwd = dist_h * 0.5
        d_lat = (i - 1) * (dist_h * 0.3)
        coords[n] = (x0 + d_fwd*math.cos(angle) - d_lat*math.sin(angle),
                     y0 + d_fwd*math.sin(angle) + d_lat*math.cos(angle))

    c2_nodes = [4, 5, 6]
    for i, n in enumerate(c2_nodes):
        d_fwd = dist_h
        d_lat = (i - 1) * (dist_h * 0.15)
        coords[n] = (x0 + d_fwd*math.cos(angle) - d_lat*math.sin(angle),
                     y0 + d_fwd*math.sin(angle) + d_lat*math.cos(angle))
        
    cible_noeud = 7
    coords[cible_noeud] = (x0 + dist_h * 1.2 * math.cos(angle),
                           y0 + dist_h * 1.2 * math.sin(angle))
    
    for n in c1_nodes:
        w = get_weight(0, n)
        G.add_edge(0, n, weight=w)
        eta[n] = t + w 

    edges_c1_c2 = [(1,4), (1,5), (2,4), (2,5), (2,6), (3,5), (3,6)]
    for u, v in edges_c1_c2:
        w = get_weight(u, v)
        G.add_edge(u, v, weight=w)
        eta[v] = eta[u] + w

    for n in c2_nodes:
        G.add_edge(n, cible_noeud, weight=get_weight(n, cible_noeud))
    
    return G, coords, cible_noeud

def get_next_quantum_waypoint(env, pos_bateau, cible_finale=(83.7, 96), backend='aer', t=0.0):

    G, coords, target_id = generer_macro_graphe(env, pos_bateau, cible_finale, t)
    weights = [G.edges[e]['weight'] for e in G.edges()]
    operator, offset, qp = build_routing_ising(G, source=0, target=target_id)

    if backend == 'aer':
        resultat_binaire = resoudre_sur_aer(qp)
    elif backend == 'ibm':
        resultat_binaire = resoudre_sur_ibm(qp)
    else:
        raise ValueError("Backend inconnu.")
    
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
        print("⚠️ Attention : Le solveur n'a pas trouvé de chemin. Direction par défaut vers le noeud 2.")
        prochain_noeud_id = 2

    prochain_waypoint_coords = coords[prochain_noeud_id]
    
    duree_segment = G[0][prochain_noeud_id]['weight']

    return prochain_waypoint_coords, t+duree_segment

import math
import networkx as nx   #type: ignore

def generer_macro_graphe(env, pos_bateau, cible_finale=(83.7, 96), t=0.0):
    Gw = nx.DiGraph(); Gt = nx.DiGraph() 
    coords = {}; eta = {0: t}
    
    x0, y0 = pos_bateau
    xt, yt = cible_finale
    dist_totale = math.hypot(xt - x0, yt - y0)
    angle_dir = math.atan2(yt - y0, xt - x0)
    coords[0] = pos_bateau
    
    def clamp(val): return max(0.5, min(val, 99.5))

    # --- LOGIQUE DYNAMIQUE DE L'ÉVENTAIL ---
    if dist_totale > 40.0:
        # CAS 1 : LOIN (Exploration large)
        # On ouvre l'angle pour chercher le vent au loin
        width = 30.0  # Très large éventail (30km de large)
        horizon = min(dist_totale, 70.0)
    else:
        # CAS 2 : PROCHE (Précision chirurgicale)
        # On resserre tout vers la cible
        width = 10.0  # Éventail étroit (10km de large)
        horizon = dist_totale

    layer_sizes = [4, 5, 5, 4] # ~50 arêtes au total
    layers_nodes = []
    current_id = 1
    step_dist = horizon / (len(layer_sizes) + 1)

    # Génération des couches avec largeur dynamique
    for i, size in enumerate(layer_sizes):
        layer_dist = step_dist * (i + 1)
        nodes_in_layer = []
        for j in range(size):
            # L'offset latéral dépend de la variable 'width' définie plus haut
            offset = (j - (size - 1) / 2) * (width / max(1, size - 1))
            
            nx_val = x0 + layer_dist * math.cos(angle_dir) - offset * math.sin(angle_dir)
            ny_val = y0 + layer_dist * math.sin(angle_dir) + offset * math.cos(angle_dir)
            
            coords[current_id] = (clamp(nx_val), clamp(ny_val))
            nodes_in_layer.append(current_id)
            current_id += 1
        layers_nodes.append(nodes_in_layer)

    target_id = current_id
    coords[target_id] = (xt, yt) if dist_totale <= horizon else (
        clamp(x0 + horizon * 1.05 * math.cos(angle_dir)), 
        clamp(y0 + horizon * 1.05 * math.sin(angle_dir))
    )

    # --- CALCUL DES POIDS ET CONNEXIONS ---
    def get_weight(u, v):
        x1, y1 = coords[u]; x2, y2 = coords[v]
        t_start = eta.get(u, t); total_time = 0.0
        dist_directe = math.hypot(x2-x1, y2-y1)
        if dist_directe < 0.1: return 0.1, 0.1
        
        # On affine le calcul météo : plus on est proche, plus le pas de calcul est petit
        pas_météo = 1.0 if dist_totale > 40 else 0.5
        nb_pas = max(1, math.ceil(dist_directe / pas_météo))
        dx = (x2 - x1) / nb_pas; dy = (y2 - y1) / nb_pas
        
        for i in range(nb_pas):
            total_time += min(env.get_travel_time(x1+i*dx, y1+i*dy, x1+(i+1)*dx, y1+(i+1)*dy, t_start+total_time), 50.0)

        progression = math.hypot(xt-x1, yt-y1) - math.hypot(xt-x2, yt-y2)
        weight = total_time * (1.0 - 0.1 * (progression / dist_directe))
        return total_time, max(0.1, weight)

    # Maillage (Départ -> Couches -> Cible)
    for n in layers_nodes[0]:
        t_r, w_q = get_weight(0, n)
        Gw.add_edge(0, n, weight=w_q); Gt.add_edge(0, n, weight=t_r)
        eta[n] = t + t_r

    for i in range(len(layers_nodes) - 1):
        for u in layers_nodes[i]:
            for v in layers_nodes[i+1]:
                if abs(layers_nodes[i].index(u) - layers_nodes[i+1].index(v)) <= 1:
                    t_r, w_q = get_weight(u, v)
                    Gw.add_edge(u, v, weight=w_q); Gt.add_edge(u, v, weight=t_r)
                    if v not in eta or eta[u] + t_r < eta[v]: eta[v] = eta[u] + t_r

    for n in layers_nodes[-1]:
        t_r, w_q = get_weight(n, target_id)
        Gw.add_edge(n, target_id, weight=w_q); Gt.add_edge(n, target_id, weight=t_r)
    return Gw, Gt, coords, target_id
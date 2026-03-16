import math
import networkx as nx

def generer_macro_graphe(env, pos_bateau, cible_finale, t=0.0):
    Gw, Gt = nx.DiGraph(), nx.DiGraph()
    x0, y0 = pos_bateau
    xt, yt = cible_finale
    
    angle_global = math.atan2(yt - y0, xt - x0)
    coords = {0: pos_bateau}
    eta = {0: t}
    
    def clamp(val): return max(0.5, min(val, 99.5))

    def get_weight(u, v):
        x1, y1 = coords[u]; x2, y2 = coords[v]
        t_start = eta.get(u, t) 
        d_edge = math.hypot(x2 - x1, y2 - y1)
        if d_edge < 0.1: return 0.1, 0.1
        
        nb_pas = max(2, math.ceil(d_edge / 2.0))
        dist_pas = d_edge / nb_pas
        total_time, penalty = 0.0, 0.0  
        
        for i in range(nb_pas):
            cx = x1 + (i/nb_pas)*(x2-x1); cy = y1 + (i/nb_pas)*(y2-y1)
            nx_p = x1 + ((i+1)/nb_pas)*(x2-x1); ny_p = y1 + ((i+1)/nb_pas)*(y2-y1)
            step_t = env.get_travel_time(cx, cy, nx_p, ny_p, t_start + total_time)
            vitesse = dist_pas / step_t if step_t > 0 else 0
            if vitesse < 3.0:
                penalty += (3.0 / (vitesse + 0.1))**2 * 20.0
            total_time += step_t

        efficacite = (math.hypot(xt-x1, yt-y1) - math.hypot(xt-x2, yt-y2)) / d_edge
        weight = (total_time + penalty) * (1.1 - 0.3 * efficacite)
        return total_time, max(0.01, weight / 10.0)

    # --- LA GRILLE DE 40 POINTS ---
    nb_cols = 8
    nb_rows = 5 
    pas = 15.0

    u_x, u_y = math.cos(angle_global), math.sin(angle_global)
    v_x, v_y = -math.sin(angle_global), math.cos(angle_global)

    for c in range(nb_cols):
        for r in range(nb_rows):
            node_id = c * nb_rows + r + 1
            dist_face = (c + 1) * pas 
            dist_cote = (r - 2) * pas 
            nx_pos = x0 + dist_face * u_x + dist_cote * v_x
            ny_pos = y0 + dist_face * u_y + dist_cote * v_y
            coords[node_id] = (clamp(nx_pos), clamp(ny_pos))

    cible_noeud = 41
    coords[cible_noeud] = cible_finale

    # Fonction utilitaire pour éviter le crash visuel de NetworkX
    def points_superposes(n1, n2):
        return math.hypot(coords[n2][0] - coords[n1][0], coords[n2][1] - coords[n1][1]) < 0.1

    # Bateau -> Première Colonne
    for r_cible in [1, 2, 3]:
        node_id = 0 * nb_rows + r_cible + 1
        if points_superposes(0, node_id): continue # Sécurité
        
        tr, w = get_weight(0, node_id)
        Gw.add_edge(0, node_id, weight=w); Gt.add_edge(0, node_id, weight=tr)
        eta[node_id] = t + tr

    # Connexions internes
    for c in range(nb_cols - 1):
        for r in range(nb_rows):
            u = c * nb_rows + r + 1
            if u not in eta: continue
            
            voisins = []
            voisins.append((c + 1) * nb_rows + r + 1)
            if r < nb_rows - 1:
                voisins.append((c + 1) * nb_rows + (r + 1) + 1)
            if r > 0:
                voisins.append((c + 1) * nb_rows + (r - 1) + 1)
                
            for v in voisins:
                if points_superposes(u, v): continue # Sécurité anti-crash
                
                tr, w = get_weight(u, v)
                Gw.add_edge(u, v, weight=w); Gt.add_edge(u, v, weight=tr)
                if v not in eta or eta[u] + tr < eta[v]: 
                    eta[v] = eta[u] + tr

    # Dernière Colonne -> Cible
    for r in range(nb_rows):
        u = (nb_cols - 1) * nb_rows + r + 1
        if u not in eta: continue
        if points_superposes(u, cible_noeud): continue # Sécurité
        
        Gw.add_edge(u, cible_noeud, weight=0.0)
        Gt.add_edge(u, cible_noeud, weight=0.1)

    # =========================================================
    # AJOUT MANUEL : VOIES DE CONTOURNEMENT EXTÉRIEURES
    # =========================================================
    
    # --- POINT 42 : Contournement par le bas (11 -> 42 -> 21) ---
    node_42 = 42
    # Position : Colonne 4 (c=3), Ligne en-dessous de 16 (r=-1)
    dist_face_42 = (3 + 1) * pas 
    dist_cote_42 = (-1 - 2) * pas 
    coords[node_42] = (clamp(x0 + dist_face_42 * u_x + dist_cote_42 * v_x), 
                       clamp(y0 + dist_face_42 * u_y + dist_cote_42 * v_y))

    # Connexion : 11 -> 42 (-45°)
    if not points_superposes(11, node_42) and 11 in eta:
        tr, w = get_weight(11, node_42)
        Gw.add_edge(11, node_42, weight=w); Gt.add_edge(11, node_42, weight=tr)
        if node_42 not in eta or eta[11] + tr < eta[node_42]: eta[node_42] = eta[11] + tr

    # Connexion : 42 -> 21 (+45°)
    if not points_superposes(node_42, 21) and node_42 in eta:
        tr, w = get_weight(node_42, 21)
        Gw.add_edge(node_42, 21, weight=w); Gt.add_edge(node_42, 21, weight=tr)
        if 21 not in eta or eta[node_42] + tr < eta[21]: eta[21] = eta[node_42] + tr


    # --- POINT 43 : Contournement par le haut (15 -> 43 -> 25) ---
    node_43 = 43
    # Position : Colonne 4 (c=3), Ligne au-dessus de 20 (r=5)
    dist_face_43 = (3 + 1) * pas 
    dist_cote_43 = (5 - 2) * pas 
    coords[node_43] = (clamp(x0 + dist_face_43 * u_x + dist_cote_43 * v_x), 
                       clamp(y0 + dist_face_43 * u_y + dist_cote_43 * v_y))

    # Connexion : 15 -> 43 (+45°)
    if not points_superposes(15, node_43) and 15 in eta:
        tr, w = get_weight(15, node_43)
        Gw.add_edge(15, node_43, weight=w); Gt.add_edge(15, node_43, weight=tr)
        if node_43 not in eta or eta[15] + tr < eta[node_43]: eta[node_43] = eta[15] + tr

    # Connexion : 43 -> 25 (-45°)
    if not points_superposes(node_43, 25) and node_43 in eta:
        tr, w = get_weight(node_43, 25)
        Gw.add_edge(node_43, 25, weight=w); Gt.add_edge(node_43, 25, weight=tr)
        if 25 not in eta or eta[node_43] + tr < eta[25]: eta[25] = eta[node_43] + tr

    # =========================================================
    # EXTENSION DU VENTRE : POINTS 44 ET 45
    # =========================================================

    # --- POINT 44 : Extension en bas (c=4, r=-1) ---
    node_44 = 44
    dist_face_44 = (4 + 1) * pas
    dist_cote_44 = (-1 - 2) * pas
    coords[node_44] = (clamp(x0 + dist_face_44 * u_x + dist_cote_44 * v_x), 
                       clamp(y0 + dist_face_44 * u_y + dist_cote_44 * v_y))

    # Connexions IN : 16 -> 44 (-45°) et 42 -> 44 (0°)
    for u in [16, 42]:
        if not points_superposes(u, node_44) and u in eta:
            tr, w = get_weight(u, node_44)
            Gw.add_edge(u, node_44, weight=w); Gt.add_edge(u, node_44, weight=tr)
            if node_44 not in eta or eta[u] + tr < eta[node_44]: eta[node_44] = eta[u] + tr

    # Connexion OUT : 44 -> 26 (+45°)
    if not points_superposes(node_44, 26) and node_44 in eta:
        tr, w = get_weight(node_44, 26)
        Gw.add_edge(node_44, 26, weight=w); Gt.add_edge(node_44, 26, weight=tr)
        if 26 not in eta or eta[node_44] + tr < eta[26]: eta[26] = eta[node_44] + tr


    # --- POINT 45 : Extension en haut (c=4, r=5) ---
    node_45 = 45
    dist_face_45 = (4 + 1) * pas
    dist_cote_45 = (5 - 2) * pas
    coords[node_45] = (clamp(x0 + dist_face_45 * u_x + dist_cote_45 * v_x), 
                       clamp(y0 + dist_face_45 * u_y + dist_cote_45 * v_y))

    # Connexions IN : 20 -> 45 (+45°) et 43 -> 45 (0°)
    for u in [20, 43]:
        if not points_superposes(u, node_45) and u in eta:
            tr, w = get_weight(u, node_45)
            Gw.add_edge(u, node_45, weight=w); Gt.add_edge(u, node_45, weight=tr)
            if node_45 not in eta or eta[u] + tr < eta[node_45]: eta[node_45] = eta[u] + tr

    # Connexion OUT : 45 -> 30 (-45°)
    if not points_superposes(node_45, 30) and node_45 in eta:
        tr, w = get_weight(node_45, 30)
        Gw.add_edge(node_45, 30, weight=w); Gt.add_edge(node_45, 30, weight=tr)
        if 30 not in eta or eta[node_45] + tr < eta[30]: eta[30] = eta[node_45] + tr

        
    return Gw, Gt, coords, cible_noeud
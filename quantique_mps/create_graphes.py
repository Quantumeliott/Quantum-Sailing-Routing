import math
import networkx as nx

def generer_macro_graphe(env, pos_bateau, cible_finale=(83.7, 96), t=0.0):
    Gw = nx.DiGraph() 
    Gt = nx.DiGraph() 
    coords = {}
    eta = {0: t}
    
    x0, y0 = pos_bateau
    xt, yt = cible_finale

    dist_totale = math.hypot(xt - x0, yt - y0)
    angle = math.atan2(yt - y0, xt - x0)
    
    coords[0] = pos_bateau
    
    def clamp(val):
        return max(0.5, min(val, 99.5))

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
            
            # --- PÉNALITÉ DE PUISSANCE ---
            # Si vitesse < 3 nds, on applique une pénalité qui croît très vite.
            # On utilise la formule : Penalty = (Seuil / Vitesse)^2
            if vitesse < 3.0:
                min((3.0 / (vitesse + 0.1))**2 * 20.0, 50.0)
                
            total_time += step_t

        efficacite = (math.hypot(xt-x1, yt-y1) - math.hypot(xt-x2, yt-y2)) / d_edge
        
        # Le poids final combine le temps réel et la pénalité de lenteur
        # On multiplie par (1.1 - efficacite) pour garder l'aspect directionnel
        weight = (total_time + penalty) * (1.1 - 0.7 * efficacite)
            
        return total_time, max(0.01, weight / 4.0)
    
    # --- GRAPHE DE PROXIMITÉ (15 Qubits - Approche fine 4x4) ---
    if dist_totale < 8.0:
        dist_1 = dist_totale * 0.40  # 1ère couche à 40% de la distance
        dist_2 = dist_totale * 0.75  # 2ème couche à 75% de la distance
        
        # Couche 1 (4 noeuds en arc de cercle)
        ecart_1 = math.pi / 4  
        c1_nodes = [1, 2, 3, 4]
        for i, n in enumerate(c1_nodes):
            angle_n = angle + (i - 1.5) * ecart_1
            coords[n] = (clamp(x0 + dist_1 * math.cos(angle_n)),
                         clamp(y0 + dist_1 * math.sin(angle_n)))
                         
        # Couche 2 (4 noeuds en arc de cercle)
        ecart_2 = math.pi / 4
        c2_nodes = [5, 6, 7, 8]
        for i, n in enumerate(c2_nodes):
            angle_n = angle + (i - 1.5) * ecart_2
            coords[n] = (clamp(x0 + dist_2 * math.cos(angle_n)),
                         clamp(y0 + dist_2 * math.sin(angle_n)))
        
        cible_noeud = 9
        coords[cible_noeud] = cible_finale 

        # Bateau -> Couche 1 (4 arêtes)
        for n in c1_nodes:
            t_reel, w_qaoa = get_weight(0, n)
            Gw.add_edge(0, n, weight=w_qaoa)
            Gt.add_edge(0, n, weight=t_reel)
            eta[n] = t + t_reel 
            
        # Couche 1 -> Couche 2 (7 arêtes en "peigne", ZÉRO croisement)
        edges_c1_c2 = [(1,5), (1,6), (2,6), (2,7), (3,7), (3,8), (4,8)]
        for u, v in edges_c1_c2:
            t_reel, w_qaoa = get_weight(u, v)
            Gw.add_edge(u, v, weight=w_qaoa); Gt.add_edge(u, v, weight=t_reel)
            if v not in eta or eta[u] + t_reel < eta[v]: eta[v] = eta[u] + t_reel

        # Couche 2 -> Cible finale (4 arêtes)
        for n in c2_nodes:
            t_reel, w_qaoa = get_weight(n, cible_noeud)
            Gw.add_edge(n, cible_noeud, weight=w_qaoa)
            Gt.add_edge(n, cible_noeud, weight=t_reel)

        return Gw, Gt, coords, cible_noeud

    # --- LE LOSANGE TACTIQUE DENSE (Grand Large) ---
    else:
        # 1. ON BRIDE LA DISTANCE : Le graphe ne va jamais plus loin que 40 unités
        dist_limite = min(dist_totale, 40.0)
        
        dist_1 = dist_limite * 0.25
        dist_2 = dist_limite * 0.65
        
        # 2. ON OUVRE LES ANGLES : pi/3 (60°) pour que le bateau puisse s'écarter de l'axe
        ecart_1 = math.pi / 4.5
        ecart_2 = math.pi / 3.5
        
        c1_nodes, c2_nodes = [1,2,3,4], [5,6,7,8,9,10]
        cible_noeud = 11

        # Placement des couches
        for i, n in enumerate(c1_nodes):
            a = angle + (i - 1.5) * ecart_1
            coords[n] = (clamp(x0 + dist_1 * math.cos(a)), clamp(y0 + dist_1 * math.sin(a)))
        for i, n in enumerate(c2_nodes):
            a = angle + (i - 2.5) * (ecart_2/2.5)
            coords[n] = (clamp(x0 + dist_2 * math.cos(a)), clamp(y0 + dist_2 * math.sin(a)))

        # 3. LA CIBLE DEVIENT UN "PUITS" : On lui donne la position de la cible réelle 
        # pour l'affichage, mais on va rendre le trajet vers elle GRATUIT.
        coords[cible_noeud] = cible_finale
        
        # Connexions standard (Bateau -> C1 -> C2 -> C3)
        for n in c1_nodes:
            t_reel, w_qaoa = get_weight(0, n)
            Gw.add_edge(0, n, weight=w_qaoa); Gt.add_edge(0, n, weight=t_reel); eta[n] = t + t_reel

        edges_c1_c2 = [(1,5), (1,6), (1,7), (2,5), (2,6), (2,7), (2,8), (3,7), (3,8), (3,9), (3,10), (4,8), (4,9), (4,10)]
        for u, v in edges_c1_c2:
            t_reel, w_qaoa = get_weight(u, v)
            Gw.add_edge(u, v, weight=w_qaoa); Gt.add_edge(u, v, weight=t_reel)
            if v not in eta or eta[u] + t_reel < eta[v]: eta[v] = eta[u] + t_reel
            
        # 4. LE FINAL GRATUIT (C3 -> Cible)
        # On met le poids à 0. Le QAOA choisira le noeud de C3 (11, 12, 13, 14) 
        # qui a été le plus rapide et efficace jusqu'ici.
        for n in c2_nodes:
            Gw.add_edge(n, cible_noeud, weight=0.0) 
            Gt.add_edge(n, cible_noeud, weight=0.1) # Temps symbolique pour la simu
            
        return Gw, Gt, coords, cible_noeud
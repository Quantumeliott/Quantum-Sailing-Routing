import math
import networkx as nx   #type: ignore


def generer_macro_graphe(env, pos_bateau, cible_finale=(83.7, 96), t=0.0):
    # init graph
    G = nx.DiGraph()
    coords = {}
    eta = {0: t}
    
    x0, y0 = pos_bateau
    xt, yt = cible_finale

    dist_totale = math.hypot(xt - x0, yt - y0)
    angle = math.atan2(yt - y0, xt - x0)
    
    coords[0] = pos_bateau
    
    # limite de la map
    def clamp(val):
        return max(0.5, min(val, 99.5))

    # fonction poids à minimiser
    def get_weight(u, v):
            x1, y1 = coords[u]
            x2, y2 = coords[v]
            t_start = eta.get(u, t) 
            total_time = 0.0
            dist_directe = math.hypot(x2-x1, y2-y1)
            nb_pas = math.ceil(dist_directe) 
            if nb_pas == 0: return 0.1 
            
            dx = (x2 - x1) / nb_pas
            dy = (y2 - y1) / nb_pas
            
            for i in range(nb_pas):
                step_time = env.get_travel_time(x1 + i*dx, y1 + i*dy,
                                                x1 + (i+1)*dx, y1 + (i+1)*dy,
                                                t_start + total_time)
                if step_time > 50.0: 
                    step_time = 50.0
                    
                total_time += step_time
                
            return total_time

    # trois graphes selon la distance (visualiser sur fichier graphes.py)
 
    # 1 (6 qubits)
    if dist_totale < 15.0:
        dist_1 = dist_totale * 0.5
        ecart = math.pi / 6  
        
        c1_nodes = [1, 2, 3]
        for i, n in enumerate(c1_nodes):
            angle_n = angle + (i - 1) * ecart
            coords[n] = (clamp(x0 + dist_1 * math.cos(angle_n)),
                         clamp(y0 + dist_1 * math.sin(angle_n)))
        
        cible_noeud = 4
        coords[cible_noeud] = cible_finale 

        for n in c1_nodes:
            w1 = get_weight(0, n)
            G.add_edge(0, n, weight=w1)
            eta[n] = t + w1 
            w2 = get_weight(n, cible_noeud)
            G.add_edge(n, cible_noeud, weight=w2)

        return G, coords, cible_noeud

    # 2 (13 qubits)
    elif dist_totale < 90.0:
        if dist_totale < 40.0:
            dist_1 = dist_totale * 0.25
            dist_2 = dist_totale * 0.5
            dist_3 = dist_totale * 0.8
        else:
            dist_1 = 15.0
            dist_2 = 30.0  
            dist_3 = 45.0
        
        ecart_1 = math.pi / 3.5
        
        c1_nodes = [1, 2, 3]
        for i, n in enumerate(c1_nodes):
            angle_n = angle + (i - 1) * ecart_1
            coords[n] = (clamp(x0 + dist_1 * math.cos(angle_n)),
                         clamp(y0 + dist_1 * math.sin(angle_n)))

        ecart_2 = math.pi / 3.5  
        
        c2_nodes = [4, 5, 6]
        for i, n in enumerate(c2_nodes):
            angle_n = angle + (i - 1) * ecart_2
            coords[n] = (clamp(x0 + dist_2 * math.cos(angle_n)),
                         clamp(y0 + dist_2 * math.sin(angle_n)))
            
        cible_noeud = 7
        coords[cible_noeud] = (clamp(x0 + dist_3 * math.cos(angle)),
                               clamp(y0 + dist_3 * math.sin(angle)))
        
        for n in c1_nodes:
            w = get_weight(0, n)
            G.add_edge(0, n, weight=w)
            eta[n] = t + w 

        edges_c1_c2 = [(1,4), (1,5), (2,4), (2,5), (2,6), (3,5), (3,6)]
        for u, v in edges_c1_c2:
            w = get_weight(u, v)
            G.add_edge(u, v, weight=w)
            if v not in eta or eta[u] + w < eta[v]:
                eta[v] = eta[u] + w

        for n in c2_nodes:
            dist_restante = math.hypot(xt - coords[n][0], yt - coords[n][1])
            temps_theorique = dist_restante / 15.0 
            
            G.add_edge(n, cible_noeud, weight=temps_theorique)
        
        return G, coords, cible_noeud

    # 3 (15 qubits)
    else:
        dist_1 = 15.0
        ecart_1 = math.pi / 6  
        
        c1_nodes = [1, 2, 3, 4] 
        for i, n in enumerate(c1_nodes):
            angle_n = angle + (i - 1.5) * ecart_1
            coords[n] = (clamp(x0 + dist_1 * math.cos(angle_n)), clamp(y0 + dist_1 * math.sin(angle_n)))

        dist_2 = 30.0
        ecart_2 = math.pi / 4  
        
        c2_nodes = [5, 6, 7] 
        for i, n in enumerate(c2_nodes):
            angle_n = angle + (i - 1) * ecart_2
            coords[n] = (clamp(x0 + dist_2 * math.cos(angle_n)), clamp(y0 + dist_2 * math.sin(angle_n)))
            
        dist_3 = 45.0 
        cible_noeud = 8 
        coords[cible_noeud] = (clamp(x0 + dist_3 * math.cos(angle)), clamp(y0 + dist_3 * math.sin(angle)))
        
        for n in c1_nodes:
            G.add_edge(0, n, weight=get_weight(0, n))

        edges_c1_c2 = [(1,5), (1,6), (2,5), (2,6), (3,6), (3,7), (4,6), (4,7)]
        for u, v in edges_c1_c2:
            G.add_edge(u, v, weight=get_weight(u, v))
            
        for n in c2_nodes:
            dist_restante = math.hypot(coords[cible_noeud][0] - coords[n][0], coords[cible_noeud][1] - coords[n][1])
            G.add_edge(n, cible_noeud, weight=get_weight(n, cible_noeud))
            
        return G, coords, cible_noeud
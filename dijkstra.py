import heapq
import numpy as np
import time

def heuristic(env, node_idx, goal_idx, vmax=15.0):
    x1, y1 = env.points[node_idx]
    x2, y2 = env.points[goal_idx]
    distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance / vmax

def dijkstra(env, start_time=0.0):
    start_idx= env.get_node_index(5,5)
    goal_idx= env.get_node_index(83.7,96)
    ti = time.time()
    # La file de priorité stocke : (temps_cumulé, index_noeud_actuel)
    start_h = heuristic(env, start_idx, goal_idx)
    pq = [(start_time + start_h, start_time, start_idx)]
    
    # Dictionnaires pour garder une trace des meilleurs temps et du chemin
    temps_min = {start_idx: start_time}
    came_from = {start_idx: None}
    
    nodes_explored = 0

    while pq:
        # On prend le noeud avec le temps de trajet le plus court actuel
        score_f, temps_actuel, noeud_actuel = heapq.heappop(pq)
        nodes_explored += 1
        
        # Condition de victoire : on a atteint l'arrivée !
        if noeud_actuel == goal_idx:
            break
            
        # Si on a déjà trouvé un meilleur chemin pour ce noeud entre-temps, on ignore
        if temps_actuel > temps_min.get(noeud_actuel, float('inf')):
            continue
            
        # Coordonnées réelles (x, y) du noeud actuel
        x1, y1 = env.points[noeud_actuel]
        
        # On regarde tous les noeuds adjacents
        for voisin_idx in env.get_neighbors(noeud_actuel):
            x2, y2 = env.points[voisin_idx]
            
            # --- LE COEUR DE LA PHYSIQUE ---
            # On demande à ton environnement combien de temps ça prend
            temps_trajet = env.get_travel_time(x1, y1, x2, y2, temps_actuel)
            # -------------------------------
            
            temps_total_voisin = temps_actuel + temps_trajet
            
            # Si ce nouveau chemin est plus rapide que ce qu'on connaissait (ou inédit)
            if temps_total_voisin < temps_min.get(voisin_idx, float('inf')):
                temps_min[voisin_idx] = temps_total_voisin
                came_from[voisin_idx] = noeud_actuel
                
                # On ajoute ce voisin à la liste des points à explorer
                h = heuristic(env, voisin_idx, goal_idx)
                nouveau_score_f = temps_total_voisin + h
                heapq.heappush(pq, (nouveau_score_f, temps_total_voisin, voisin_idx))
                
    # --- Reconstruction du chemin ---
    chemin = []
    chemin_temps = []
    noeud_courant = goal_idx
    
    if noeud_courant not in came_from:
        print("Aucun chemin possible trouvé (peut-être bloqué par le vent ?)")
        return [],[], float('inf')
        
    while noeud_courant is not None:
        chemin.append(noeud_courant)
        chemin_temps.append(temps_min[noeud_courant])
        noeud_courant = came_from[noeud_courant]
        
    chemin.reverse()
    chemin_temps.reverse()

    temps_final = temps_min[goal_idx]
    tf = time.time() - ti

    print(f"Simulation terminée en {tf:.2f} secondes.")

    return chemin, chemin_temps, temps_final
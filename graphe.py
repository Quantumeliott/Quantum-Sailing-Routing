import matplotlib.pyplot as plt
import networkx as nx #type: ignore
from quantique_mps.next_point import generer_macro_graphe
import math 

#class test
class MockEnv:
    def get_travel_time(self, x1, y1, x2, y2, t):
        dist = math.hypot(x2-x1, y2-y1)
        return dist / 10.0
    
def visualiser_graphe(ax, G, coords, cible_noeud, titre):
    couleurs_noeuds = []
    tailles_noeuds = []
    
    for noeud in G.nodes():
        if noeud == 0:
            couleurs_noeuds.append('limegreen')
            tailles_noeuds.append(600)
        elif noeud == cible_noeud:
            couleurs_noeuds.append('crimson')
            tailles_noeuds.append(600)
        else:
            couleurs_noeuds.append('skyblue')
            tailles_noeuds.append(300)

    nx.draw(G, pos=coords, ax=ax, with_labels=True, node_color=couleurs_noeuds, 
            node_size=tailles_noeuds, font_weight='bold', font_color='black', 
            edge_color='gray', arrows=True, arrowsize=15)

    poids_aretes = {(u, v): f"{d['weight']:.1f}h" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos=coords, edge_labels=poids_aretes, font_size=8, font_color='red', ax=ax)

    ax.set_title(titre, fontsize=14, fontweight='bold')
    ax.grid(True, linestyle=':', alpha=0.7)
    ax.set_aspect('equal')
    
    ax.set_axis_on()
    ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
    
    #zoom
    tous_les_x = [pos[0] for pos in coords.values()]
    tous_les_y = [pos[1] for pos in coords.values()]
    marge = 5.0
    ax.set_xlim(min(tous_les_x) - marge, max(tous_les_x) + marge)
    ax.set_ylim(min(tous_les_y) - marge, max(tous_les_y) + marge)


if __name__ == "__main__":
    env_test = MockEnv()    
    
    pos1_depart = (85.0, 85.0) 
    pos2_depart = (75.0, 65.0) 
    pos4_depart = (40.0, 35.0)
    pos3_depart = (5.0, 5.0) 

    pos_arrivee = (83.7, 96.0)
    G4,d, coords4, cible4 = generer_macro_graphe(env_test, pos3_depart, pos_arrivee)
    G3,c, coords3, cible3 = generer_macro_graphe(env_test, pos2_depart, pos_arrivee)
    G1,b, coords1, cible1 = generer_macro_graphe(env_test, pos1_depart, pos_arrivee)
    G2,a, coords2, cible2 = generer_macro_graphe(env_test, pos4_depart, pos_arrivee)
    fig, axes = plt.subplots(1, 4, figsize=(18, 6))
    
    visualiser_graphe(axes[0], G4, coords4, cible4, " Départ Loin")
    visualiser_graphe(axes[2], G3, coords3, cible3, "Départ au Milieu")
    visualiser_graphe(axes[1], G2, coords2, cible2, "Départ au Milieu loin")
    visualiser_graphe(axes[3], G1, coords1, cible1, "Départ Proche ")

    plt.tight_layout()
    plt.show()
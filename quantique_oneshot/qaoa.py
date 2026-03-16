from quantique_oneshot.next_point import get_full_quantum_path
import time 

def simulation_mps(env):
    start_pos = (5, 5)
    cible = (83.7, 96)
    
    print("🧠 Lancement du calcul quantique One-Shot (109 qubits)...")
    time_i = time.time()
    
    # Un seul appel pour générer tout le trajet
    chemin_complet, temps_complets = get_full_quantum_path(env, start_pos, cible_finale=cible, t=0.0)
        
    time_f = time.time() - time_i
    print(f"✅ Simulation terminée en {time_f:.2f} secondes.")
    print(f"📍 Nombre de waypoints trouvés : {len(chemin_complet)}")

    return chemin_complet, temps_complets, temps_complets[-1]
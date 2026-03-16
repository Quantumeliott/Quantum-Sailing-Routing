from quantique_mps.next_point import get_next_quantum_waypoint
import math
import time 

def simulation_mps(env):
    chemin = [(5,5)]
    time_register = [0.0]
    i= 0
    time_i = time.time()
    while math.hypot(83.7 - chemin[-1][0], 96 - chemin[-1][1]) > 2.0:
        prochain_waypoint, t_next = get_next_quantum_waypoint(env, chemin[-1], cible_finale=(83.7, 96), t=time_register[-1])
        chemin.append(prochain_waypoint)
        time_register.append(t_next)
        i += 1
        
    time_f = time.time() - time_i
    print(f"Simulation terminée en {time_f:.2f} secondes.")

    return chemin, time_register, time_register[-1]

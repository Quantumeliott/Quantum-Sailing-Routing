import pandas as pd # type: ignore
import numpy as np
import math
from weather import get_wind_at_time

class MarineEnvironment:
    def __init__(self, length=100, width=100, res_x=75, res_y=75, seed=None):
        x = np.linspace(0, length, res_x)
        y = np.linspace(0, width, res_y)
        xv, yv = np.meshgrid(x, y)
        self.points = np.vstack([xv.ravel(), yv.ravel()]).T

        self.freq = 0.04
        self.res_x = res_x
        self.res_y = res_y

        if seed is not None:
            np.random.seed(seed)
        self.base_phase1 = np.random.uniform(0, 50, 2)
        self.base_phase2 = np.random.uniform(0, 50, 2)
        
        # --- NOUVEAUTÉ : Direction du vent de base aléatoire (entre 0 et 360°) ---
        self.base_wind_dir = np.random.uniform(0, 360)
    

    def boat_speed(self, angle_diff, wind_speed):
        # 1. Normalisation de l'angle (toujours entre 0° de face et 180° de dos)
        angle_abs = np.abs(angle_diff) % 360
        if angle_abs > 180:
            angle_abs = 360 - angle_abs
            
        vmax = 15.0
        if wind_speed < 15.0:
            vitesse_potentielle = wind_speed * 0.6
        else:
            vitesse_potentielle = wind_speed * 0.3
        vitesse_potentielle = min(vitesse_potentielle, vmax)
        if angle_abs >= 30.0:
            boat_s = vitesse_potentielle
        else:
            facteur_chute = (angle_abs / 30.0)**10
            boat_s = vitesse_potentielle * facteur_chute
        return boat_s

    def get_travel_time(self, x1, y1, x2, y2, current_time):

        dx, dy = x2 - x1, y2 - y1
        distance = np.sqrt(dx**2 + dy**2)
        boat_angle_math = np.degrees(np.arctan2(dy, dx))
        boat_angle = (90 - boat_angle_math) % 360

        df_t = get_wind_at_time(self, time=current_time)

        distances_to_point = np.sqrt((df_t['x'] - x1)**2 + (df_t['y'] - y1)**2)
        closest_node = df_t.iloc[distances_to_point.idxmin()]
        
        wind_speed = closest_node['wind_speed']
        wind_angle = closest_node['wind_dir']
        
        angle_diff = wind_angle - boat_angle
        speed = self.boat_speed(angle_diff, wind_speed)
        if speed == 0:
            return float('inf')
        return distance / speed
    
    def get_neighbors(self, index):
        neighbors = []
        
        # On utilise les dimensions de l'objet (100x100) !
        y = index // self.res_x
        x = index % self.res_x

        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.res_x and 0 <= ny < self.res_y:
                neighbor_index = ny * self.res_x + nx
                neighbors.append(neighbor_index)
                
        return neighbors
    
    def get_node_index(self, x, y):
    
        distances_sq = (self.points[:, 0] - x)**2 + (self.points[:, 1] - y)**2
        index_noeud = np.argmin(distances_sq)
        
        return index_noeud
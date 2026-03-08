import pandas as pd # type: ignore
import numpy as np
import math

class MarineEnvironment:
    def __init__(self, length=100, width=100, res_x=75, res_y=75, seed=None):
        x = np.linspace(0, length, res_x)
        y = np.linspace(-width/2, width/2, res_y)
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

    def get_wind_at_time(self, time=0):
        temporal_freq_1 = 0.016
        temporal_freq_2 = 0.1  

        ph1 = self.base_phase1 + np.array([
            10 * np.sin(time * temporal_freq_1),
            8 * np.cos(time * temporal_freq_1 * 0.7)
        ])
        ph2 = self.base_phase2 + np.array([
            6 * np.cos(time * temporal_freq_2),
            5 * np.sin(time * temporal_freq_2 * 1.3)
        ])

        def get_noise_layer(points, f, amplitude, phase_shift):
            p1 = points[:, 0] * f + phase_shift[0]
            p2 = points[:, 1] * f + phase_shift[1]
            return amplitude * (np.sin(p1) * np.cos(p2) + 0.5 * np.sin(p2*2) * np.cos(p1*2))

        # 1. Champ de Vitesse de base (Tes ondes)
        speed = 15 + get_noise_layer(self.points, self.freq, 8, ph1) + \
                     get_noise_layer(self.points, self.freq*2.1, 3, ph2)

       # --- MÉTÉO SYNOPTIQUE DYNAMIQUE ---
        
        # 1. L'ANTICYCLONE (Zone de pétole / vent faible)
        # Trajectoire chaotique et plus rapide (Fréquences augmentées)
        cx_anti = 50.0 + 35.0 * np.sin(time * 0.04) * np.cos(time * 0.015)
        cy_anti = 0.0 + 25.0 * np.cos(time * 0.05)
        
        # Rayon qui "respire" de façon agressive (entre 10 et 30 de rayon)
        r_anti = 20.0 + 10.0 * np.sin(time * 0.06)
        
        # Calcul de la zone de l'anticyclone
        dist_sq_anti = (self.points[:, 0] - cx_anti)**2 + (self.points[:, 1] - cy_anti)**2
        effet_anti = 1.0 - 0.9 * np.exp(-dist_sq_anti / (2 * r_anti**2))


        # 2. LA DÉPRESSION (Zone de tempête / vent fort)
        # Elle tourne autour de la carte à une vitesse différente
        cx_dep = 50.0 + 30.0 * np.cos(time * 0.035 + 2.0)
        cy_dep = 0.0 + 30.0 * np.sin(time * 0.045 + 1.0)
        
        r_dep = 18.0 + 6.0 * np.cos(time * 0.07)
        
        # Calcul de la zone de la dépression (Note le "+" ici, ça ajoute du vent !)
        dist_sq_dep = (self.points[:, 0] - cx_dep)**2 + (self.points[:, 1] - cy_dep)**2
        # Augmente le vent jusqu'à +80% au centre de la dépression
        effet_dep = 1.0 + 0.8 * np.exp(-dist_sq_dep / (2 * r_dep**2)) 


        # --- APPLICATION AU CHAMP DE VITESSE ---
        # On applique la pétole ET la tempête.
        speed = speed * effet_anti * effet_dep
        # Sécurité : le vent ne descend jamais en dessous de 2 noeuds (pour ne pas crasher A*) 
        # et on le plafonne à 35 noeuds (pour éviter de dépasser la vitesse max du bateau de façon absurde).
        speed = np.clip(speed, 2.0, 35.0)
        # -------------------------------------------

        # Champ de Direction
        direction = self.base_wind_dir + get_noise_layer(self.points, self.freq, 40, ph1) + \
                          get_noise_layer(self.points, self.freq*1.9, 15, ph2)

        return pd.DataFrame({
            'x': self.points[:, 0], 'y': self.points[:, 1],
            'wind_speed': speed,
            'wind_dir': direction % 360,
            'time': time
        })
    
    def get_boat_position(self, x, y, t):
        print(f"Calculating boat position for time {t} with input coordinates ({x}, {y})")
        df_t = self.get_wind_at_time(t)
        distances = np.sqrt((df_t['x'] - x)**2 + (df_t['y'] - y)**2)
        closest_node = df_t.iloc[distances.idxmin()]
        speed, dir = closest_node['wind_speed'], closest_node['wind_dir']
        x+=speed*np.cos(np.radians((270 - dir) % 360))
        y+=speed*np.sin(np.radians((270 - dir) % 360))
        return x, y

    def boat_speed(self, angle_diff, wind_speed):
        angle_abs = np.abs(angle_diff) % 360
        if angle_abs > 180:
            angle_abs = 360 - angle_abs
        angle_mort = math.radians(30)
        vmax = 15

        boat_s = max(0, wind_speed * np.sin(math.radians(angle_abs)-angle_mort)/5)
        boat_s = min(boat_s, vmax)
        return boat_s

    def get_travel_time(self, x1, y1, x2, y2, current_time):

        # 1. Calcul de la direction du bateau
        dx, dy = x2 - x1, y2 - y1
        distance = np.sqrt(dx**2 + dy**2)
        # 1. Calcul de la direction mathématique
        boat_angle_math = np.degrees(np.arctan2(dy, dx))
        # 2. Conversion en angle Météo/Boussole (Nord=0, Est=90)
        boat_angle = (90 - boat_angle_math) % 360
        
        # 2. Vecteur vent au point de départ (utilise ta fonction interpolée)
        df_t = self.get_wind_at_time(current_time)

        distances_to_point = np.sqrt((df_t['x'] - x1)**2 + (df_t['y'] - y1)**2)
        closest_node = df_t.iloc[distances_to_point.idxmin()]
        
        wind_speed = closest_node['wind_speed']
        wind_angle = closest_node['wind_dir']
        
        # 3. Projection du vent sur l'axe du bateau (cosinus de la différence)
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
        
        # 2. np.argmin retourne l'index où la distance est la plus petite
        index_noeud = np.argmin(distances_sq)
        
        return index_noeud
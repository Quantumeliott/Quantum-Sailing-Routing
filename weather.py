import numpy as np # type: ignore
import pandas as pd # type: ignore

def get_wind_at_time(self, time=0):
    temporal_freq_1 = 0.1
    temporal_freq_2 = 0.3  

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

    # 1. Champ de Vitesse de base (Vent moyen constant de 15 noeuds)
    speed = 15 + get_noise_layer(self.points, self.freq, 5, ph1) + \
                    get_noise_layer(self.points, self.freq*2.1, 2, ph2)

    # =========================================================
    # 🌪️ LA TEMPÊTE À RETARDEMENT (Obstacle d'anticipation)
    # =========================================================
    
    # Centre de l'obstacle : Pile au milieu du trajet diagonal
    cx_obs = 45.0
    cy_obs = 50.0
    
    # Taille de la tempête (Assez large pour bloquer le passage direct)
    r_obs = 22.0 
    
    # ⏱️ LA MAGIE EST ICI : Le facteur d'activation temporelle
    # Si time < 3.0 -> activation = 0 (La tempête n'existe pas)
    # Si 3.0 < time < 6.0 -> activation monte doucement de 0 à 1
    # Si time > 6.0 -> activation = 1 (La tempête est maximale)
    activation = np.clip((time - 3.0) / 3.0, 0.0, 1.0)
    
    dist_sq_obs = (self.points[:, 0] - cx_obs)**2 + (self.points[:, 1] - cy_obs)**2
    
    # On applique l'effet : une chute de vent massive multipliée par l'activation
    effet_obs = 1.0 - (0.95 * activation) * np.exp(-dist_sq_obs / (2 * r_obs**2))

    # --- APPLICATION AU CHAMP DE VITESSE ---
    speed = speed * effet_obs
    
    # Plafond à 35 nœuds, et sécurité plancher à 2 nœuds (le mur infranchissable)
    speed = np.clip(speed, 2.0, 35.0)
    # =========================================================

    # Champ de Direction
    direction = self.base_wind_dir + get_noise_layer(self.points, self.freq, 40, ph1) + \
                        get_noise_layer(self.points, self.freq*1.9, 15, ph2)

    return pd.DataFrame({
        'x': self.points[:, 0], 'y': self.points[:, 1],
        'wind_speed': speed,
        'wind_dir': direction % 360,
        'time': time
    })
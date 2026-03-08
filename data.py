import pandas as pd # type: ignore
import numpy as np

class MarineEnvironment:
    def __init__(self, length=100, width=100, res_x=50, res_y=50, seed=None):
        """Initialise la grille cartésienne (le couloir de jeu)."""

        x = np.linspace(0, length, res_x)
        y = np.linspace(-width/2, width/2, res_y)
        xv, yv = np.meshgrid(x, y)
        self.points = np.vstack([xv.ravel(), yv.ravel()]).T

        # Fréquence spatiale (plus petit = variations plus douces)
        self.freq = 0.04

        # Initialiser les phases de base avec un seed
        if seed is not None:
            np.random.seed(seed)
        self.base_phase1 = np.random.uniform(0, 50, 2)
        self.base_phase2 = np.random.uniform(0, 50, 2)

    def get_wind_at_time(self, time=0):
        temporal_freq_1 = 0.008  # Fréquence lente (période ~125 unités de temps)
        temporal_freq_2 = 0.056  # Fréquence plus lente (période ~210 unités de temps)

        # Phases évoluent continuellement dans le temps
        ph1 = self.base_phase1 + np.array([
            10 * np.sin(time * temporal_freq_1),
            8 * np.cos(time * temporal_freq_1 * 0.7)
        ])
        ph2 = self.base_phase2 + np.array([
            6 * np.cos(time * temporal_freq_2),
            5 * np.sin(time * temporal_freq_2 * 1.3)
        ])

        # Fonction interne pour générer une harmonique de bruit
        def get_noise_layer(points, f, amplitude, phase_shift):
            p1 = points[:, 0] * f + phase_shift[0]
            p2 = points[:, 1] * f + phase_shift[1]
            return amplitude * (np.sin(p1) * np.cos(p2) + 0.5 * np.sin(p2*2) * np.cos(p1*2))

        # Champ de Vitesse (Moyenne 15kts, amplitude +/- 10kts)
        speed = 15 + get_noise_layer(self.points, self.freq, 8, ph1) + \
                     get_noise_layer(self.points, self.freq*2.1, 3, ph2)

        # Champ de Direction (Moyenne 315°/NW, amplitude +/- 45°)
        direction = 315 + get_noise_layer(self.points, self.freq, 40, ph1) + \
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

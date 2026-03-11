import numpy as np # type: ignore
import pandas as pd # type: ignore
import random

def get_wind_at_time(self, time=0):
    # init 
    if not hasattr(self, 'event_init'):
        self.event_type = random.choice(['TEMPÊTE', 'PÉTOLE'])
        
        # Pile ou face pour choisir le côté de la carte (Nord-Ouest vs Sud-Est)
        if self.event_type == 'TEMPÊTE':
            if random.random() > 0.5:
                # Zone Nord-Ouest (En haut à gauche de la diagonale)
                self.event_x = random.uniform(15.0, 40.0)
                self.event_y = random.uniform(60.0, 85.0)
            else: 
                # Zone Sud-Est (En bas à droite de la diagonale)
                self.event_x = random.uniform(60.0, 85.0)
                self.event_y = random.uniform(15.0, 40.0)
            self.event_radius = random.uniform(12.0, 15.0)
        else : 
            self.event_x = random.uniform(45.0, 60.0)
            self.event_y = random.uniform(45.0, 60.0)
            self.event_radius = random.uniform(17.0, 20.0)

        self.event_t_start = random.uniform(3.0, 6.0)
        self.event_t_full = self.event_t_start + 4.0 
         
        self.event_init = True
        
   # weather evolution

    temporal_freq_1 = 0.01
    temporal_freq_2 = 0.03 

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

    speed = 15.0 + get_noise_layer(self.points, self.freq, 10, ph1) + \
                   get_noise_layer(self.points, self.freq * 2.1, 5, ph2)

    direction = self.base_wind_dir + (time * 10.0) + get_noise_layer(self.points, self.freq, 25, ph1)

    # event (storm or petole) evolution

    if time < self.event_t_start:
        activation = 0.0
    elif time > self.event_t_full:
        activation = 1.0
    else:
        activation = (time - self.event_t_start) / (self.event_t_full - self.event_t_start)

    dist_sq = (self.points[:, 0] - self.event_x)**2 + (self.points[:, 1] - self.event_y)**2
    effet_spatial = np.exp(-dist_sq / (2 * self.event_radius**2))
    
    if self.event_type == 'TEMPÊTE': 
       speed += (30.0 * activation * effet_spatial)
    else:
        speed *= (1.0 - (0.95 * activation * effet_spatial))

    speed = np.clip(speed, 2.0, 40.0)

    return pd.DataFrame({
        'x': self.points[:, 0], 'y': self.points[:, 1],
        'wind_speed': speed,
        'wind_dir': direction % 360,
        'time': time
    })